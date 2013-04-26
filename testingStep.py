## A program for testing around with the step engine. 
from StepControl import *
from StepControlAux import *
#from Calibrate import * 
import numpy as np
import ImageGrab, Image, ImageDraw, time, ImageOps
from time import clock
from numpy.linalg import norm
from ModifyVelocity import *
from DetectParticleUtils import *

def find_delay(move_len, step_vel, nr_of_pauses, wait_time = 1, direct_time=-1):
	ConnectSimple(1, "COM5", 9600, 0)
	SetJoystickOff() 
	if direct_time==-1:
		SetVelocity(max(5,step_vel), 1, 0, 0,max_vel=max(5,step_vel))
		MoveToAbsolutePosition(0,0,0,0,1)
		SetVelocity(step_vel, 1, 0, 0,max_vel=max(3,step_vel))
		sleep(wait_time)
		t0 = clock()
		MoveToAbsolutePosition(move_len,0,0,0,1)
		t1 = clock()
		direct_time = (t1-t0)
		print "the direct route took", direct_time*1000
	if nr_of_pauses==0:
		return direct_time

	SetVelocity(max(5,step_vel), 1, 0, 0,max_vel=max(5,step_vel))
	MoveToAbsolutePosition(0,0,0,0,1)
	SetVelocity(step_vel, 1, 0, 0,max_vel=max(5,step_vel))
	sleep(wait_time)
	StopAxes() # This shouldn't be needed at all.
	pause_time = (move_len/(step_vel+1))/(nr_of_pauses+1)
	t0 = clock()
	for i in range(0,nr_of_pauses):
		MoveToAbsolutePosition(move_len,0,0,0,0)		
		sleep(pause_time)
		StopAxes()
		print "pause ", i
	MoveToAbsolutePosition(move_len,0,0,0,0)		
	MoveToAbsolutePosition(move_len,0,0,0,1)
	t1 = clock()
	stop_time = t1 - t0
	print "the direct route took", direct_time*1000, " ms and the pause time took ", stop_time*1000, " ms"
	print "The approximate stop time is ", (stop_time - direct_time)*1000/nr_of_pauses, " ms"
	return (stop_time - direct_time)*1000/nr_of_pauses


def test_step_time_correction():
	x,y = 1490, 205 					  # The x,y coordinates of the top left corner of what we want to crop
	#width, height = 1170, 780             # The size of the image we want to crop
	width, height  = 365, 275
	step_2_pixel   = 940.
	pixel_2_step   = 1./step_2_pixel
	size = (width, height)            	  # The resultant size of our image after resizing
	middle = [size[0]/2, size[1]/2]       # We want our particle to be close to the middle.
	box = (x,y,x+width,y+height)		  # The bounding box for our cropping
	ConnectSimple(1, "COM5", 9600, 0)
	SetVelocityToFactor(0.1,0.1,0,0)
	speed_error = CalcSpeedError(0.2)
	SetSpeed(30,30,0,0, max_speed=30)
	StopAxes()
	SetJoystickOn()
	nothing = raw_input("Press enter when particle is located")
	SetJoystickOff()
	vel_approx = CalcVelocity(0.1)
	step_vel = np.array([vel_approx[0],vel_approx[1]])
	best_position = middle
	SetSpeed(0.2,0,0,0)	
	for i in range(0,4):
		start_time = clock()
		im = ImageGrab.grab(box)
		if i>0:
			old_im_time = im_time
		im_time =  clock()
		pix     = array(im)
		sigma = 1
		blur_im = cv2.GaussianBlur(pix, (7,7), sigma)
		edges   = cv2.Canny(blur_im, 230/2.5,230)
		contours, waste = cv2.findContours(edges,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) 
		best_contour, best_distance = 10000000,10000000
		old_position = best_position
		for j in range(0,len(contours)): 
			tmp_pos = np.sum(contours[j], axis=0)          # Calculate position
			position = tmp_pos[0]/len(contours[j])      # Normalize, the pos[0] is because of an extra layer of nothing
			distance = norm(position - old_position)
			if distance < best_distance:
				best_contour = j
		tmp_pos = np.sum(contours[best_contour], axis=0)
		best_position = tmp_pos[0]/len(contours[best_contour])
		best_position = np.array(best_position)*1.0
		middle = np.array(middle)*1.0
		print "best position is ", best_position, " and best particle is ", best_contour, " and the middle is ", middle
		rod_vel = old_position - best_position
		print "the brute force rod_vel is ", rod_vel, " and pos is ", old_position
		if i==0:
			corr_vec_1 = (middle - best_position)
			corr_vec = corr_vec_1*2/(step_2_pixel)
			print " our corr_vec is ", corr_vec_1, " 2 is ", corr_vec, type(corr_vec_1), corr_vec_1/940
			ModifyStepVelocity(step_vel, True, corr_vec, True, speed_error)
			step_vel += corr_vec
			corr_time = clock()
		elif i==1:
			t1 = corr_time - old_im_time
			## This is the time after step correction took effect
			rod_vel = (best_position - old_position) + (corr_vec*t1*step_2_pixel*4)
			print "we assume that the time after our correction will be ", rod_vel, 
			print " our corr vec contribution is ", (corr_vec*t1*step_2_pixel*4), " with t1 being ", t1
		sleep(0.5)
#test_step_time_correction()
#StopAxes()
#~ ConnectSimple(1, "COM5", 9600, 0)
#~ pos = GetPosition()
#~ for i in range(0,50):
	#~ x_speed = (i*0.01)
	#~ SetSpeed(x_speed,0,0,0)
	#~ sleep(0.1)
	#~ if GetPosition()[0] != pos[0]:
		#~ print "the minimal speed is ", x_speed
		#~ sleep(2)
		#~ print CalcVelocity(0.5)
		#~ SetVelocityToFactor(0.1,0,0,0)
		#~ break	
#~ sleep(2)
ConnectSimple(1, "COM5", 9600, 0)
SetJoystickOn()
for i in range(1,10000):
	t0 = clock()
	SaveStepPos()
	print i, 1/(clock() - t0)
Disconnect()
#print CalcSpeedError(0.5)
#~ im = Image.open("Images/cropped image112.jpg")
#~ pix     = array(im)
#~ sigma = 1
#~ x,y = 1490, 205 					  # The x,y coordinates of the top left corner of what we want to crop
#~ #width, height = 1170, 780             # The size of the image we want to crop
#~ width, height  = 365, 275
#~ step_2_pixel   = 940.
#~ pixel_2_step   = 1./step_2_pixel
#~ size = (width, height)            	  # The resultant size of our image after resizing
#~ middle = [size[0]/2, size[1]/2]       # We want our particle to be close to the middle.
#~ box = (x,y,x+width,y+height)		  # The bounding box for our cropping
#~ 
#~ blur_im = cv2.GaussianBlur(pix, (7,7), sigma)
#~ edges   = cv2.Canny(blur_im, 230/2.5,230)
#~ contours, waste = cv2.findContours(edges,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
#~ print len(contours)
#~ for i in range(0,len(contours)):
	#~ tmp_pos = np.sum(contours[i], axis=0)          # Calculate position
	#~ position= tmp_pos[0]/len(contours[i])      # Normalize, the pos[0] is because of an extra layer of nothing
	#~ position[1] = (middle[1]*2)-position[1]  # Makes the y-axis positive, ie bottom up and not the opposite
	#~ pix_point = save_point_image(position, pix, "expected", (255,0,0), 0, save=False)
	#~ save_contour_image(i, contours, pix_point, i+10, 0)

#print CalcVelocity(0.5)
#~ StopAxes()
#~ pos_pre = GetPosition()
#~ for i in range(0,51):
	#~ x_speed = (i*0.1) -  2.5
	#~ sleep(0.1)
	#~ SetSpeed(x_speed,0,0,0)
#~ pos_pre = GetPosition()
#~ sleep(0.1)
#~ SetSpeed(1,0,0,0)
#~ sleep(0.5)
#~ StopAxes()
#~ SetJoystickOn()
#print CalcSpeedError(0.5)
#SetSpeed(-1,-1,0,0)
#print "speed is ", GetSpeed()
#sleep(1)
#pos_post= GetPosition()
#topAxes()
#print pos_pre-pos_post

#print CalcSpeedError(0.2)
#print CalcSpeedError(1)
#print CalcSpeedError(10)
#inputs = (1,1,0,0, True)
#MoveToAbsolutePosition(inputs)
#~ StopAxes()
#~ SetJoystickOn()
#~ useless = raw_input("Press enter when you want")
#~ speeds = GetSpeed()
#~ speeds = CalcVelocity(0.1)
#~ print speeds
#~ SetJoystickOff()
#~ SetSpeed(speeds[0], speeds[1], 0, 0)
#~ sleep(2)
#~ StopAxes()

#testfile = open("step_pause_times.txt", 'w')
#for i in range(1,80):
#	for j in range(0,20):
#		if j==0:
#			zero_time = find_delay(move_len=4, step_vel=i*0.05, nr_of_pauses=j, wait_time=0.5)
#		else:
#			stop_time = find_delay(move_len=4, step_vel=i*0.2, nr_of_pauses=j, wait_time=0.5, direct_time=zero_time)
#			testfile.write(str(stop_time) + "\t")
#	testfile.write("\n")
#testfile.close()
#find_delay(move_len=2, step_vel=0.5, nr_of_pauses=1, )
#~ 
#~ for i in range(1,20):
	#~ speed = 0.2*i
	#~ SetSpeed(speed,0,0,0)
	#~ t1 = clock()
	#~ pos_pre = GetPosition()
	#~ sleep(1)
	#~ t2 = clock()
	#~ pos_post = GetPosition()
	#~ StopAxes()
	#~ MoveToAbsolutePosition(pos_pre[0], pos_pre[1], 0,0, True)
	#~ error = (pos_post[0] - pos_pre[0])/(speed*(t2-t1))
	#~ print speed, error

#print CalcSpeedError(1)
