## External downloadable free packages.
import ImageGrab, Image, ImageDraw, time, ImageOps
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import cv2
from numpy import array, zeros
from cv2 import Canny, findContours



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
from ImageWindow import Viewer

## Standard Library packages
import os
import win32api
from sys import exit
setpriority()

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

## CURRENT EDITING NOTES
## I commented the "extra saving file", this might cause some issues and I want to put it back pretty soon


# parameters holding object
parameters  	= DetectorParameters() 

# option holding object
options 		= DetectorOptions()
options.printing_output 	= True
options.starting_left   	= False
options.needs_average 		= False
options.saving_directory    = "E:/staffana/Feb 26/"

# state holding object. Could be replaced if we implement a Kalman filter
state			= DetectorState(parameters, options)

# Object stores the times taken for various computations in this class.
timedata		= TimeData()					# The "class" that handles all the times we meassure

stepfile  = open("MetaData/step_data.txt", 'w')
stepfile.write("i \t re_rod_pos  \t rod vel  \t step vel \t\t correction_vel \t\t new velocity \n") 



#### CONNECT TO THE STEP MOTOR AND LET THE USER FIND A PARTICLE
if not options.testing_disconnected:
	outputs = InitializeStepEngine(parameters.box, options)
	state.step_vel, aver_im, speed_error, state.vel_fac, state.going_right = outputs
	
	## Since right means minus on the step engine, we simply check if our velocity is negative or not
	state.going_right = step_vel < 0
	
	### TRY TO OPEN A SEPARATE WINDOW WHERE THE USER CAN PRESS STOP MAYBE BUT FIRST JUST SHOW IT


### NOW WE START THE (POSSIBLY) NEVER ENDING THE LOOP OF TRACKING THE PARTICLE
for j in range(1,20000):
	timedata.iteration_start = time.clock()
	timedata.pos_save_total = 0
	print "before running SaveStep pos our timedata pos save total was ", timedata.pos_save_total
	ignorePosition, pos_save_time = SaveStepPos(options, timedata)
	print "After running SaveStep pos our timedata pos save total is ", timedata.pos_save_total
	if j%2 == 0:
		i = j/2
	else:
		continue
	
	
	print "\n our current frame is ", i , "\n"
	#### ACQUIRE AND CROP THE IMAGE
	timedata.image_old   = timedata.image_start
	timedata.image_start = time.clock()
	im = ImageGrab.grab(box)
	if options.printing_output:
		im.save("Images/cropped image" + str(i) + ".jpg")
	timedata.image_end = time.clock()
	
	
	#### PERFORM EDGE DETECTION AND CONTOUR DETECTION 
	timedata.contour_start 	= time.clock()
	contours, pix  			= GetContours(im, aver_im, 210, printing_output, i)
	timedata.contour_end	= time.clock()

	#### FIND THE RIGHT CONTOUR
	best_contour_nr, positions = DetectParticle(state,contours,i, timedata,pix, options) # i is the current nr of runs
	# To save space we could possibly merge contours with state? It seems a bit weird either way...
	## Updates the state based on the particle we have, or have not, found.
	state.update(best_contour_nr, positions, parameters, i)

	## If we are printing output we save a picture of the chosen contour
	if options.printing_output:
		cv2.drawContours(pix,[contours[best_contour_nr]],-1,(0,255,0),3)
		im = Image.fromarray(pix)
		im.save("Images/main_contour" + str(i)+ ".jpg")
	
	## Saves the time now that we are done with detecting the particl	e 
	timedata.detection_end


#### 	MEASURE THE POSITION AND VELOCITY OF THE STEP ENGINE
	if not options.testing_disconnected:
		currentPosition = SaveStepPos(options, timedata)
## I HAVE CHAGED SAVE STEP POS NEED TO CHANGE THE DEFINITION		
		state.update_correction_vector(state, parameters, options, current_frame)
		# this should probably also be a state operation.. it would really finish cutting down on the main loop!
####	AND THEN DO THE REQUIRED CORRECTIONS		
		timedata.step_control_start = time.clock()
		timedata.step_control_end = time.clock()


	### IF WE ARE TOO CLOSE TO EITHER INLET WE WANT TO REVERSE THE PUMP
	state.check_pump()
	
#### SLEEP ANY TIME THAT IS LEFT 
	timedata.iteration_end = time.clock()
	dt = timedata.iteration_end - timedata.iteration_start
	time_to_sleep = max(0,(1/fps_max) - dt)
	timedata.write_times() ## Think of a better name for this function...
#	print "dt = ", dt, "time to sleep is ", time_to_sleep
#	print "we are taking approximately ", (dt*fps_max)*100 ,"% of the CPU"
	time.sleep(time_to_sleep)
	print " \n" # just to separate the iterations more.

if not testing_disconnected:
	TerminateStepConnection(starting_left)

#print "all sizes are ", allsizes
#plt.hist(allsizes, bins=150, range=(0,150))
#plt.show()

