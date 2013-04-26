from math import floor
import numpy as np
from numpy import array

import cv2
from PIL import Image, ImageFont, ImageDraw
def sum_of(contour):
	pos = np.sum(contour, axis=0)
	pos = pos[0]/len(contour)   # For some reason it is stored with an unnecessary array layer
	pos[0] = pos[0]/len(contour)
	pos[1] = pos[1]/len(contour)
#	print "our end position is ", pos
	return pos


def setpriority(pid=None, priority=1):
	import win32api, win32process, win32con
	priorityclasses = [win32process.BELOW_NORMAL_PRIORITY_CLASS, 
	win32process.NORMAL_PRIORITY_CLASS, 
	win32process.ABOVE_NORMAL_PRIORITY_CLASS, 
	win32process.HIGH_PRIORITY_CLASS, 
	win32process.REALTIME_PRIORITY_CLASS]
	if pid == None:
		pid = win32api.GetCurrentProcessId()
	handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
	win32process.SetPriorityClass(handle, priorityclasses[priority])

def save_image_as(pix, add, name):
	import cv2, time
	from PIL import ImageGrab, Image, ImageDraw, ImageOps
	pix2 = pix.copy()  ## We make a copy of the background image
	cv2.drawContours(pix2,add,-1,(0,255,0),3)
	im = Image.fromarray(pix2)
	im.save("Images/" + name + ".png")

def to_str(n, length=8):
	if type(n)== list or type(n) == np.ndarray:
		final_str = "["
		for item in n:
			final_str += to_str(item, length) + ", "
		return (final_str.strip()).rstrip(',') + "]"
	s = repr(n)
	s = s[0:length]
	if s.find(".") == -1:
		s+="."
	if len(s) < length:
		s+=("0"*(length-len(s)))
	return s

def clear_folder(folder_name):
	import os
	for the_file in os.listdir(folder_name):
		file_path = os.path.join(folder_name,the_file)
		try:
			os.unlink(file_path)
		except Exception, e:
			print e

def remove_old_images():
	folder_name = "Images/"
	import os
	for the_file in os.listdir(folder_name):
		file_path = os.path.join(folder_name,the_file)
		if file_path.find("main_contour") >= 0 or file_path.find("cropped")>=0 or file_path.find("contours")>=0:
			try:
				os.unlink(file_path)
			except Exception, e:
				print e
				
def removeAverage(pix, aver_im):
	pix_tmp = pix.astype(np.float32)
	pix_tmp = abs(pix_tmp + aver_im)
	pix_tmp = pix_tmp*255/np.amax(pix_tmp)
	pix     = pix_tmp.astype('uint8')
	return pix

def edge_detect_levels(im, name):
	sigma = 1
	blur_im = cv2.GaussianBlur(im, (7,7), sigma)
	for i in range(140,240,20):
		edges = cv2.Canny(blur_im, i/3,i)
		save_image_as(array(edges), array([array([array([])])]), "/EdgeTesting/" + name + str(i))

def contour_detect_levels(im, name):
	sigma = 2
	blur_im = cv2.GaussianBlur(im, (7,7), sigma)
#	for i in range(140,240,20):
	i = 200
	print "name is ", name
	blur_copy = blur_im.copy()
	edges = cv2.Canny(blur_im, i/3,i)
	contours, waste = cv2.findContours(edges,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	for j in range(0,len(contours)):
		cv2.drawContours(blur_copy,[contours[j]],-1,(0,255,0),1)
		im = Image.fromarray(blur_copy)
		im.save("Images/ContourTesting/200/Frame" + name + "Level" + str(i)+ "Contour " + str(j) + ".png")
		
def contour_detect_no_smooth(im, name):
	i = 200
	im_copy = im.copy()
	edges = cv2.Canny(im, 85,230)
	contours, waste = cv2.findContours(edges,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	for j in range(0,len(contours)):
		cv2.drawContours(im_copy,[contours[j]],-1,(0,255,0),1)
		im = Image.fromarray(im_copy)
		im.save("Images/ContourTesting/200/Frame" + name + "Level" + str(i)+ "Contour " + str(j) + "no_smooth" + ".png")

def add_legend(img, text, colors, position=-1):
	font_size   = 14
	font_path 	= "C:\WINDOWS\Fonts\ARIAL.TTF"
	font 		= ImageFont.truetype(font_path, font_size, encoding='unic')
#	colors		= ["Red", "green", "Darkblue", "teal"]
	box_size 	= (len(max(text))*font_size*1.2, len(text)*font_size*1.2)
	box_size    = (int(box_size[0]), int(box_size[1]))
	if position == -1:
		box_pos = (img.size[0]-(10+box_size[0]),10)
	else:
		box_pos = position
	text_pos 	= (box_pos[0]+0.1*box_size[0],box_pos[1]+0.1*box_size[1])
	text_pos    = (int(text_pos[0]), int(text_pos[1]))
	text_color  = "Black" #ImageDraw.ImageColor.getrgb("black")
	draw 		= ImageDraw.Draw(img)
	line_width  = 4
	line_pos    = [text_pos[0] - (font_size+4), text_pos[1]+(font_size-line_width)/2,text_pos[0] - 6,text_pos[1]+ (font_size+line_width)/2 ]
	draw.rectangle([box_pos[0], box_pos[1], box_pos[0]+box_size[0], box_pos[1]+box_size[1]], fill="White", outline="Black")

	for line, color in zip(text, colors):
		draw.rectangle(line_pos, fill=color, outline=color)
		draw.text(text_pos, line, fill=text_color, font=font)
		text_pos =  (text_pos[0], text_pos[1] + font_size)
		line_pos[1] += font_size
		line_pos[3] += font_size
	del draw
	#img.save("C:/test.jpg")

def get_filename(old_filename):
	filename = old_filename
	name_is_taken = True
	while name_is_taken:
		try:
			outfile = open(filename, 'r')
			name_is_taken = True
			print "we are currently trying the name ", filename
			if filename[-5].isdigit():
				new_filename = filename[:-5] + str(int(filename[-5]) + 1) + filename[-4:]
			else:
				new_filename = filename[:-4] + "0" + filename[-4:]
			filename = new_filename		
			print old_filename, " already exists, trying to write to file ", new_filename , " instead"
		except IOError as ioe:			
			name_is_taken = False
	return filename
#img = Image.open("C:/testing.png")
#text		= ["Red is actual position", "green is old position", "dark blue is expected position", "teal is constant motion"]
#add_legend(img, text)

## Test many images for many types of edges

#for i in range(1,50):
#	name = "cropped image" + str(i) + ".jpg"
#	im = Image.open("Images/"+name)
#	im_array = array(im)
#	edge_detect_levels(im_array, name)
#
#~ for i in range(1,90):
	#~ name = "cropped image" + str(i) + ".jpg"
	#~ im = Image.open("Images/"+name)
	#~ im_array = array(im)
	#~ contour_detect_no_smooth(im_array, str(i))
		



