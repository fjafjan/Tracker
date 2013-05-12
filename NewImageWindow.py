from Tkinter import *
import tkFileDialog
from PIL import ImageTk, Image
from time import sleep
import os, sys
import Queue


from MainThread import MainThread
from Options import *

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
		self.options = DetectorOptions()


# NOTE TO SELF: Change this. Most likely give it one of the "gtinker string".
# BELOW HERE ONLY GUI STUFF
		self.title = Label(text="Tracker v 0.9")
		self.title.pack()
		self.size = im.size
		self.tkimage = ImageTk.PhotoImage(im) # cut out , palette=256, see if it still works/works better.
		self.lbl = Label(master, image=self.tkimage)
		self.lbl.pack(side='top')
		
		main_fr = Frame(master)
		main_fr.pack(side='top', expand=1,fill='x')		
		
		## OKay so I think the things I am packing are frames. SO I should make one frame for the different parts or whatnot
		# One fram for parameters, one for what to show, one for stopping starting etc.
		
		# The button frame to start finding a particle
		findb = Button(main_fr, text="Find particle", command = lambda: self.find_particle())
		findb.grid(row=0, column=0, sticky="w", pady=4)
		
		# The button frame for starting tracking
		stopb = Button(main_fr, text="Start tracking", command = lambda: self.start_tracking())
		stopb.grid(row=0, column=1, sticky="w", pady=4)

		# The button frame for stopping tracking
		stopb = Button(main_fr, text="Done tracking", command = lambda: self.end_tracking())
		stopb.grid(row=0, column=2, sticky="w", pady=4)

#w = Label(master, text=longtext, anchor=W, justify=LEFT)
		start_label = Label(main_fr, text="Starting position:", anchor=E, justify=RIGHT, width=40)
		start_label.grid(row=0, column=3, sticky="e")
	
		self.v0 = StringVar()
		self.v0.set("left")
		for text, value, col in [("left", True, 4), ("right", False, 5)]:
			b = Radiobutton(main_fr, text=text, variable=self.v0, value=text, command=lambda: self.set_starting_pos(self.v0.get()))
			b.grid(row=0, column = col, sticky="w", pady=4)
		

		small_fr_1 = Frame(master)
		small_fr_1.pack(side='top', expand=1,fill='x')

		# The label for the showing contour frame
		show_label = Label(small_fr_1, text="Select what image to show:")
		show_label.grid(row=0, column=0, stick="w", pady=0)

		
		show_fr = Frame(master)
		show_fr.pack(side='top', expand=1,fill='x')

		## NOTE TO SELF: Add show no image option!
		show_modes = [("Show main contour", "main_contour"), 
						("Show all contours", "all_contours"),
						("Showing nothing", "nothing"),
						("Show original", "original")]
		
		self.v1 = StringVar()
		self.v1.set("main_contour")
		col = 0
		
		for text, value in show_modes:
			b = Radiobutton(show_fr, text=text, variable=self.v1, value=value, command=lambda: self.show_queue(value))
			b.grid(row=0, column=col, sticky="w", pady=4)
			col+=1
						
		
		#~ ilabel = Label(show_fr, text="Currently showing:")
		#~ ilabel.grid(row=2, column=0, sticky="w", pady=4)
		#~ ## evar is the number in the windows
		#~ ## entry is the "frame" that holds evar.
		#~ entry = Entry(show_fr, textvariable=self.v1, width=19)
		#~ entry.grid(row=2, column=1, sticky="w", pady=4)
		
		option_fr = Frame(master)
		option_fr.pack(side='top', expand=1,fill='x')
		
		olabel = Label(option_fr, text="Options:")
		olabel.grid(row=0, column=0, sticky="w", pady=4)

		# The button frame for stopping tracking

		calb   = Button(option_fr, text="Run calibration", command = lambda: self.options_queue("calibrate"))
		calb.grid(row=1, column=0, sticky="w", pady=4)
		
		averb  = Button(option_fr, text="Generate average image", command = lambda: self.options_queue("average"))
		averb.grid(row=1, column=1, sticky="w", pady=4) 
		
		file_button = Button(option_fr, text = "Select saving directory", command = lambda: self.set_save_directory())
		file_button.grid(row=2, column=0, sticky="w", pady=4)
		
		file_label = Label(option_fr, text="Savig directory:")
		file_label.grid(row=2, column=1, sticky="w", pady=4)
		## evar is the number in the windows
		## entry is the "frame" that holds evar.
		self.direct_var = StringVar()
		self.direct_var.set(self.options.saving_directory)
		entry = Entry(option_fr, textvariable=self.direct_var, width=40)
		entry.grid(row=2, column=2, sticky="w", pady=4)
		## Save images

	def find_particle(self):
		im_list 	= self.image_queue
		order_list 	= self.order_queue
		queues		= im_list, order_list
		self.tracker = MainThread(queues, self.options)
		self.tracker.start()
		self.update_image()		
	
	def start_tracking(self):
		self.order_queue.put("start_tracking")
		## I think this is all it needs to do?

	def end_tracking(self):
		self.order_queue.put("stop")
		self.end_image_update = True
		self.tracker.join()
		print "The state of the thread is ", self.tracker.isAlive()
		print "WE ARE ENDING NOW I HOPE!!!"
		
	def set_starting_pos(self, text):
		## Ideally this should also move the actual step engine. But currently this is not supported
		if text == "left":
			self.options.starting_left == True
		elif text == "right":
			self.options.starting_left == False
		else:
			print text
			print "ERROR TRYING TO SET STARTING POSITION TO SOMETHINGOTHER THAN LEFT OR RIGHT!!!"


	
	def update_image(self):
		if self.image_queue.empty():
			#print "\n there were no images :( \n"
			pass
		else: 
			im = self.image_queue.get()
#			print "image should be updated", im, type(im)
			self.tkimage.paste(im)
		if self.end_image_update:
			print "IT SHOULD EXIT NOW!!!"
			self.end_image_update = False
			return
		self.top.after(100, self.update_image)

	def show_queue(self, command):
		valid_commands = ["nothing", "main_contour", "original", "all_contours"]
		if command in valid_commands:
			if command == "nothing":
				self.show_black()			
			elif self.paused:
				self.update_image()
				self.paused = False
			self.order_queue.put(command)

	def options_queue(self, command):
		valid_commands = ["calibrate", "average", "starting_left", "starting_right"]
		if command in valid_commands:
			if command == "calibrate":
				from Calibrate import Calibrate
				Calibrate(new_calibration=True)
			elif command == "average":
				from GetAverageImage import GetAverageImage
				GetAverageImage(self.options)
				## This might be trouble as we are using a variable from another thread directly instead of from a queue
			else:
				self.order_queue.put(command)

	def show_black(self):
		im = Image.open("no_image.jpg")
		self.tkimage.paste(im)
		self.end_image_update = True
		self.paused = True
	

	def set_save_directory(self):
		 folder = tkFileDialog.askdirectory()
		 self.direct_var.set(folder)
		 self.options.saving_directory = folder
		 print "folder is ", folder
		 filename = get_filename(folder + "/position_tracking.txt")
		 self.options.extra_file = open(filename, 'w')




def test_this():
	#filelist = ["C:/test.jpg", "C:/testingnew.jpg", "C:/hej.jpg"]
	im1 = Image.open("C:/test.jpg")
	im_queue = Queue.Queue()
	im_queue.put(im1)

	root = Tk()
	app = Viewer(root, im_queue)
	root.mainloop()
	im = Image.open("C:/test.jpg")
	
test_this()
