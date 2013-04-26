from Tkinter import *
from PIL import ImageTk, Image
from time import sleep
import os, sys

class Viewer:
	def __init__(self, master, im_queue):
		self.top = master
		self.image_queue = im_queue
		self.index = 0
		# Show the first image
		im = im_queue.get()
		filename = im.

# there is no way that an image doesn't exist. There are other things though
#		if not os.path.exists(filename):
#			print "Unable to find ", filename
#			self.top.quit()

# Change this		
#		self.title = Label(text=os.path.basename(filename))
		self.title = Label(text="Running")
		self.title.pack()
		
		im = Image.open(filename)
		if im.format == "SPIDER":
			im = im.convert2byte()
		self.size = im.size
		self.tkimage = ImageTk.PhotoImage(im, palette=256)
		self.lbl = Label(master, image=self.tkimage)
		self.lbl.pack(side='top')
		
		# The button frame for showing the next image?
		stopb = Button(fr, text="Done tracking", command = lambda: self.end_tracking())
		stopb.grid(row=1, column=0, sticky="s", pady=4)
		
		fr = Frame(master)
		fr.pack(side='top', expand=1,fill='x')
		back = Button(fr, text="back", command = lambda: self.nextframe(1))
		back.grid(row=0, column=0, sticky="w", padx=4, pady=4)
		
		ilabel = Label(fr, text="image number:")
		ilabel.grid(row=0, column=1, stick="e", pady=4)
		## evar is the number in the windows
		self.evar = IntVar()
		self.evar.set(1)
		## entry is the "frame" that holds evar.
		entry = Entry(fr, textvariable=self.evar)
		entry.grid(row=0, column=2, sticky="w", pady=4)
	
	def getImage(self, im_queue):
		im = im_queue.get()
#		im = Image.open(filename)
		if im.format == "SPIDER":
			im = im.convert2byte
		if im.size != self.size:
			print "all images must be the same dimensions:"
			f1 = os.path.basename(self.files[0])
			f2 = os.path.basename(filename)
			print "%s %s %s : %s " % (f1, str(self.size), f2, str(im.size))
			self.top.quit()
		return im
	
	def nextframe(self, i=1, imgnum=-1):
		# If we are not given an image number we just increase the old one
		if imgnum == -1:
			self.index += 1
		else:
			self.index = imgnum - 1
		# check so that our index is not too large or less than zero
		if self.index >= len(self.files) - 1:
			self.index = 0
		elif self.index < 0:
			self.index = len(self.files) - 1
		filename = self.files[self.index]
		if not os.path.exists(filename):
			print "Unable to find file ", filename
			self.top.quit()
		self.title.configure(text=os.path.basename(filename))
		self.evar.set(self.index+1)
		
		im = self.getImage(filename)
		self.tkimage.paste(im)
	
	def getimgnum(self, event=None):
		self.nextframe(imgnum=self.evar.get())

def test_this():
	filelist = ["C:/test.jpg", "C:/testingnew.jpg", "C:/hej.jpg"]
	root = Tk()
	app = Viewer(root, filelist)
	root.mainloop()
	im = Image.open("C:/test.jpg")
