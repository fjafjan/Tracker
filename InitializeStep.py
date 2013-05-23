import cv2
import numpy as np
import ImageGrab, Image, ImageDraw, time, ImageOps


from StepControl import *
from Calibrate import * 
from GetAverageImage import GetAverageImage
from utilities import *
from GetContours import *
from DetectParticle import *
from Options import *


def InitializeStepEngine(order_list, image_list, options, parameters, timedata):	
	## 		Connect to the step engine and turn off the joystick
	ConnectSimple(1, "COM4", 9600, 0)
	SetJoystickOff() #   
	
	
	## 		We find any potential difference between the speed we set, and the speed we get
	SetVelocityToFactor(0.1,0.1,0,0) # This is noise
	vel_fac = GetVelocityFactor()
	x_vel_fac, y_vel_fac = vel_fac[0], vel_fac[1]
	speed_error = CalcSpeedError(0.3) 
	print "speed error is ", speed_error

	
	## 		We callibrate our positions, so that the inlets are where we wants them to be
	left_inlet, right_inlet = Calibrate(options.needs_calibrate)
	# We don't actually do anything with them atm :D
	
	## 	 	We find the appropriate starting position
	if options.starting_left:
		start_x = 0
	else:
		start_x = -35
	MoveToAbsolutePosition(start_x,0,0,0,1) ## We assume that we are at the left inlet
	
	
	## 	 	If we do not have a good average image, we fix that.
	if options.needs_average:
		dirt_arr = GetAverageImage(options)
	else:
		dirt_im = Image.open("Images/Averaging/average_image.jpg")
		dirt_arr = np.array(dirt_im) 
		dirt_arr= dirt_arr.astype(np.float32)
		
	## Remove old image files if we intend to save new ones
	if options.printing_output:
#		nothing = raw_input("Press enter to remove old image files")
		contour_folder =  "Images/Contours"
		positions_folder = "Images/Positions"
		clear_folder(contour_folder) # Makes sure we only store the images from this particular run. 
		clear_folder(positions_folder)
		remove_old_images()


	##	 	We let the user find a particle
	SetJoystickOn(True, True)
	print "Press the star tracking button to initiate tracking of the particle closes to the middle"
	
	state = DetectorState(parameters, options)
	state.speed_error = speed_error
	state.vel_fac = [x_vel_fac, y_vel_fac]

	
	while True:
		if not order_list.empty():
			if order_list.get() == "start_tracking":
				break
		im = ImageGrab.grab(parameters.box)
		contours, pix  	= GetContours(im, dirt_arr, 210, printing_output=False, iteration=0)
		best_contour_nr, positions = DetectParticle(state,contours,0, timedata,pix, parameters, options, initialize=True) # i is the current nr of runs
		if best_contour_nr < 0:
			continue
		cv2.drawContours(pix,[contours[best_contour_nr]],-1,(0,255,0),3)
		im = Image.fromarray(pix)
		image_list.put(im)
		sleep(1.5/parameters.fps_max)
	
	##	 	We find the velocity we were going at
	vel_approx = CalcVelocity(0.1)
	print "vel approx is ", vel_approx


	state.step_vel = np.array([vel_approx[0],vel_approx[1]])
	state.going_right = vel_approx[0]<0
	state.flowing_right = vel_approx[0]<0
	print " We think we are going right: ", state.going_right
	print " We think we are going right: ", state.flowing_right

	## 		We set the step engine to move at this speed
	SetJoystickOff()
	##### MAYBE WE SHOULD INCLUDE THE SPEED ERROR HERE? I THINK SO BUT LET'S TEST THAT IT'S REASONABLE FIRST
	SetSpeed(vel_approx[0]/x_vel_fac, vel_approx[1]/y_vel_fac, 0, 0, max_speed = 3.0/(min(x_vel_fac, y_vel_fac)))
	
	 
#	return np.array([vel_approx[0],vel_approx[1]]), dirt_arr, speed_error, [x_vel_fac, y_vel_fac], going_right
	return dirt_arr, state



# Some stuff from an age gone by that might come useful one day
	#~ filehandle = open("velocity_measurement.txt", 'w')
	#~ filehandle.write(str(speed0)+"\t"+str(speed1)+"\t"+str(speed2)+"\t"+str(speed3)+"\t"+str(speed4)+"\t"+str(speed5)+"\t"+str(speed6))
	#~ filehandle.close()
	#~ print "the speeds we calculated are ", speed0,speed1,speed2,speed3,speed4, speed5, speed6
