
## External downloadable free packages.
from PIL import Image as Img
from PIL import Image, ImageDraw, ImageOps
import numpy as np
import scipy as sp
#import matplotlib.pyplot as plt
import cv2
from numpy import array, zeros
from cv2 import Canny, findContours
# Also requires 



## My own files
from StepControl import *
from PumpControl import *
from GetContours import GetContours
from DetectParticle import *
from InitializeStep import *
from ModifyVelocity import ModifyStepVelocity
from FindCorrectionVector import FindCorrectionVector
from utilities import sum_of, setpriority, save_image_as, to_str
from TimeData import *
from Options import DetectorOptions, DetectorParameters, DetectorState
from Kalman import Kalman
#from ImageWindow import Viewer

## Standard Library packages
import os
import time
#import win32api
import threading
import thread
import Queue
from sys import exit
#setpriority()

class MainThread(threading.Thread):
	def __init__(self, queues, options, parameters):
		threading.Thread.__init__(self)
		im_list, order_list = queues
		self.im_list = im_list
		print "the size of the list is ", im_list.qsize()
		time.sleep(1)
		self.order_list = order_list
		self.image_to_show = "main_contour"	
		self.options = options
		self.parameters = parameters


## THINGS FOR KALMAN FILTER
## EXPERIMENTAL
	#~ dt = 1/fps_max
	#~ A = np.mat([[1,dt,0,0],[0,1,0,0],[0,0,1,dt],[0,0,0,1]])
	#~ B = np.mat([[dt,0,0,0],[0,1,0,0],[0,0,dt,0],[0,0,0,1]])
	#~ H = np.identity(4)#*step_2_pixel # Which should we choose here?...
	#~ P = np.identity(4) # This changes over time so we are not too worried.
	#~ Q = np.identity(4)*0.01 # We are pretty confident it our model.. maybe foolishly so!
	#~ R = np.identity(4)*0.010  # we are a fair bit more uncertain about this...
	#~ I = np.identity(4)

	def run(self):
		## Short explanatory text re parameters, options and state.
		## PARAMETERS
		## Parameters are numbers where there is some optimal or obvious value, they might be tweaked between runs
		## but ultimately we want to stick with one. 
		##
		## OPTIONS
		## Options are typically yes or no questions, but more over it is simple things that you might want to change
		## between runs simply depending on what you want to do. Are you debugging? If so, printing output is nice.
		## 
		## STATE
		## State values are things that change during a run, it's all the stuff like the position of the particle
		## the speed of the step engine, etc etc.


		# parameters holding object
		self.kalman = Kalman(fps_max = 10, going_right = True, middle = self.parameters.middle)

		# option holding object
		options 		= self.options
		options.testing_disconnected= False
		options.printing_output 	= True
#		options.starting_left   	= True
#		options.needs_average 		= False
		options.saving_directory    = "E:/staffana/Feb 26/"
		print "starting left is ", options.starting_left
		# state holding object. Could be replaced if we implement a Kalman filter
		#self.state			= DetectorState(self.parameters, options)
				
		# Object stores the times taken for various computations in this class.
		timedata		= TimeData()					# The "class" that handles all the times we meassure

		stepfile  = open("MetaData/step_data.txt", 'w')
		stepfile.write("i \t re_rod_pos  \t rod vel  \t step vel \t\t correction_vel \t\t new velocity \n") 

		#### CONNECT TO THE STEP MOTOR AND LET THE USER FIND A PARTICLE
		if not options.testing_disconnected:
			aver_im, self.state = InitializeStepEngine(self.order_list, self.im_list, options, self.parameters, timedata)
			#~ state.step_vel, aver_im, state.speed_error, state.vel_fac, state.going_right = outputs

			state = self.state # I think this is safe. 
			### TRY TO OPEN A SEPARATE WINDOW WHERE THE USER CAN PRESS STOP MAYBE BUT FIRST JUST SHOW IT
		else:
#			dirt_im = Image.open("Images/Averaging/average_image.jpg")
			dirt_im = Img.open("C:/test.jpg")
			dirt_arr = np.array(dirt_im) 
			aver_im= dirt_arr.astype(np.float32)
		
		
		## NOW WE START THE (POSSIBLY) NEVER ENDING THE LOOP OF TRACKING THE PARTICLE
		for j in range(1,30000):
			timedata.iteration_start = time.clock()
			timedata.pos_save_total = 0
			#print "before running SaveStep pos our timedata pos save total was ", timedata.pos_save_total
			ignorePosition = SaveStepPos(options, timedata)
			#print "After running SaveStep pos our timedata pos save total is ", timedata.pos_save_total
			if j%2 == 0:
				i = j/2
			else:
				continue
			
			
			print "\n our current frame is ", i , "\n"
			#### ACQUIRE AND CROP THE IMAGE
			timedata.image_old   = timedata.image_start
			timedata.image_start = time.clock()
			im = ImageGrab.grab(self.parameters.box)
			if options.printing_output:
				im.save("Images/cropped image" + str(i) + ".jpg")
			if self.image_to_show == "original":
				self.im_list.put(im)
			timedata.image_end 	= time.clock()
			
				#### PERFORM EDGE DETECTION AND CONTOUR DETECTION 
			timedata.contour_start 	= time.clock()
			
			contours, pix  			= GetContours(im, aver_im, 190, options.printing_output, i)
			timedata.contour_end	= time.clock()
			
					
			best_contour_nr, positions = DetectParticle(state,contours,i, timedata,pix, self.parameters, options) # i is the current nr of runs
			# To save space we could possibly merge contours with state? It seems a bit weird either way...
			## Updates the state based on the particle we have, or have not, found.
			state.update(best_contour_nr, contours, positions, self.parameters, i, timedata, options)
			self.kalman.predict(state, self.parameters.step_2_pixel)
			self.kalman.update(state)
			print " the found position we think was ", state.pos_approx
			print "Kalman predicted the position to be ", [self.kalman.x_pred.item(0), self.kalman.x_pred.item(2)] 
			print "Kalman thinks our actual position is ", [self.kalman.x_est.item(0), self.kalman.x_est.item(2)], 
			if best_contour_nr < 0:
				continue
			## If we are printing output we save a picture of the chosen contour
			if options.printing_output:
				try:
					cv2.drawContours(pix,[contours[best_contour_nr]],-1,(0,255,0),3)
				except IndexError as ie:
					print "contours is ", contours, " and the best contour number is ", best_contour_nr
					raise
				im = Image.fromarray(pix)
				if self.image_to_show == "main_contour":
					self.im_list.put(im)
					#print "WE ADDED AN IMAGEHOORAY HOORAY \n \n"

				im.save("Images/main_contour" + str(i)+ ".jpg")
			
			## Saves the time now that we are done with detecting the particle 
			timedata.detection_end


		#### 	MEASURE THE POSITION AND VELOCITY OF THE STEP ENGINE
			if not options.testing_disconnected:
				state.currentPosition = SaveStepPos(options, timedata)

		## I HAVE CHAGED SAVE STEP POS NEED TO CHANGE THE DEFINITION		
				state.update_correction_vector(state, self.parameters, options, current_frame=j)
				state.corr_vec *= 0
				# this should probably also be a state operation.. it would really finish cutting down on the main loop!

		####	AND THEN DO THE REQUIRED CORRECTIONS		
				timedata.step_control_start = time.clock()
				timedata.step_control_end = time.clock()


		### IF WE ARE TOO CLOSE TO EITHER INLET WE WANT TO REVERSE THE PUMP
				state.check_pump()
			
		#### Check the image queue and the order queue if we should stop or something
			self.check_queues()
			
		#### SLEEP ANY TIME THAT IS LEFT 
			timedata.iteration_end = time.clock()
			dt = timedata.iteration_end - timedata.iteration_start
			time_to_sleep = max(0,(1/self.parameters.fps_max) - dt)
			timedata.write_times() ## Think of a better name for this function...
		#	print "dt = ", dt, "time to sleep is ", time_to_sleep
		#	print "we are taking approximately ", (dt*fps_max)*100 ,"% of the CPU"
			time.sleep(time_to_sleep)
			print " \n" # just to separate the iterations more.


	def check_queues(self):
		if not self.order_list.empty():
			order = self.order_list.get()
			if order == "stop":
				print "WE HAVE ORDERED TO STOP!!!!"
				## close connection to step engine
				StopAxes()
				Disconnect() 
				## close connection to the pump
				self.state.pump.CloseConnection()
				
				## Should close various files as well? I think opening them next time will solve that.
				thread.exit()
#				import sys
#				sys.exit()				
			image_commands = ["nothing", "main_contour", "original", "all_contours"]
			if order in image_commands:
				self.image_to_show = order
			
			option_commands  = ["calibrate", "average", "starting_left", "starting_right"]
			if order in option_commands:
				pass
				
		else:
			pass
			# print "OUR ORDERS WERE EMPTY WTF WTF WTF WTF"

#im_list 	= Queue.Queue()
#order_list 	= Queue.Queue()
#queues		= im_list, order_list
#t = MainThread(queues)
#t.start()

#w = WindowT
