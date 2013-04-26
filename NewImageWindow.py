from Tkinter import *
from PIL import ImageTk, Image
from time import sleep
import os, sys
import Queue
from MainThread import MainThread

class Viewer:
	def __init__(self, master, im_queue):
		self.top = master
		self.image_queue = im_queue
		self.order_queue = Queue.Queue()
		self.index = 0
		self.image_to_show = "contour"
		self.end_image_update = False
		self.paused = False
		# Show the first image
		im = im_queue.get()


# NOTE TO SELF: Change this. Most likely give it one of the "gtinker string".
		self.title = Label(text="Running")
		self.title.pack()
		### I have no idea what this _does_, but presumably it's wrong.
		if im.format == "SPIDER":		
			im = im.convert2byte()
		self.size = im.size
		self.tkimage = ImageTk.PhotoImage(im) # cut out , palette=256, see if it still works/works better.
		self.lbl = Label(master, image=self.tkimage)
		self.lbl.pack(side='top')
		
		main_fr = Frame(master)
		main_fr.pack(side='top', expand=1,fill='x')
		

		
		## OKay so I think the things I am packing are frames. SO I should make one frame for the different parts or whatnot
		# One fram for parameters, one for what to show, one for stopping starting etc.
		
		# The button frame for stopping tracking
		stopb = Button(main_fr, text="Start tracking", command = lambda: self.start_tracking())
		stopb.grid(row=0, column=0, sticky="w", pady=4)

		# The button frame for stopping tracking
		stopb = Button(main_fr, text="Done tracking", command = lambda: self.end_tracking())
		stopb.grid(row=0, column=1, sticky="w", pady=4)
		
		small_fr_1 = Frame(master)
		small_fr_1.pack(side='top', expand=1,fill='x')

		# The label for the showing contour frame
		show_label = Label(small_fr_1, text="Select what image to show")
		show_label.grid(row=0, column=0, stick="w", pady=0)

		
		show_fr = Frame(master)
		show_fr.pack(side='top', expand=1,fill='x')

		## NOTE TO SELF: Add show no image option!
		
		# The button frame for showing contours
		contb = Button(show_fr, text="Show main contour", command = lambda: self.show_queue("main_contour"))
		contb.grid(row=1, column=0, sticky="w", pady=4)
		
		# The button frame for showing contours
		contb = Button(show_fr, text="Show all contours", command = lambda: self.show_queue("all_contours"))
		contb.grid(row=1, column=1, sticky="w", pady=4)

		# The button frame for showing contours
		contb = Button(show_fr, text="Show nothing", command = lambda: self.show_queue("nothing"))
		contb.grid(row=1, column=2, sticky="w", pady=4)

		# The button frame for showing contours
		contb = Button(show_fr, text="Show original", command = lambda: self.show_queue("original"))
		contb.grid(row=1, column=3, sticky="w", pady=4)

		
		# The button frame for showing the next image?		
#		back = Button(fr, text="back", command = lambda: self.nextframe(1))
#		back.grid(row=0, column=0, sticky="w", padx=4, pady=4)
		
		ilabel = Label(show_fr, text="Currently showing:")
		ilabel.grid(row=2, column=0, stick="e", pady=4)
		## evar is the number in the windows
		## entry is the "frame" that holds evar.
		entry = Entry(show_fr, textvariable=self.image_to_show, width=19)
		entry.grid(row=2, column=1, sticky="w", pady=4)
	
	def getImage(self, im_queue):
		im = im_queue.get()
#		im = Image.open(filename)
		if im.format == "SPIDER":
			im = im.convert2byte
		if im.size != self.size:
			print "all images must be the same dimensions:"
			self.top.quit()
		return im
	
	def nextframe(self, i=1, imgnum=-1):
		if self.image_queue.empty():
			#print "\n there were no images :( \n"
			return
		im = self.image_queue.get()
#		im.save("C:/Users\Fjafjan/Documents/Exjobb/notprint.jpg")
		print "image should be updated", im, type(im)
		self.tkimage.paste(im)
	
	def getimgnum(self, event=None):
		self.nextframe(imgnum=self.evar.get())
	
	def start_tracking(self):
		im_list 	= self.image_queue
		order_list 	= self.order_queue
		queues		= im_list, order_list
		self.tracker = MainThread(queues)
		self.tracker.start()
		self.update_image()

	def end_tracking(self):
		self.order_queue.put("stop")
		self.end_image_update = True
		print "WE ARE ENDING NOW I HOPE!!!"
	
	def update_image(self):
		self.nextframe()
		if self.end_image_update:
			print "IT SHOULD EXIT NOW!!!"
			self.end_image_update = False
			return
		self.top.after(200, self.update_image)

	def show_queue(self, command):
		valid_commands = ["nothing", "main_contour", "original", "all_contours"]
		if command in valid_commands:
			if command == "nothing":
				self.show_black()			
			elif self.paused:
				self.update_image()
				self.paused = False
			self.order_queue.put(command)

	def show_black(self):
		im = Image.open("no_image.jpg")
		self.tkimage.paste(im)
		self.end_image_update = True
		self.paused = True
		
def test_this():
	#filelist = ["C:/test.jpg", "C:/testingnew.jpg", "C:/hej.jpg"]
	im1 = Image.open("C:/test.jpg")
	im2 = Image.open("C:/testing.jpg")
	im_queue = Queue.Queue()
	im_queue.put(im1)
	im_queue.put(im2)

	root = Tk()
	app = Viewer(root, im_queue)
	root.mainloop()
	im = Image.open("C:/test.jpg")
	
test_this()
