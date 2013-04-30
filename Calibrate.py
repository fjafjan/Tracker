from StepControl import *
import numpy as np
from PIL import ImageGrab, Image, ImageDraw, ImageOps
import time
from ast import *

## THINK A BIT ABOUT THIS FUNCTION SO THAT IT IS REASONABLE
## As far as I can see it is looking pretty reasonable. 
def Calibrate(new_calibration):
	if new_calibration:
		ConnectSimple(1, "COM4", 9600, 0)
		calibration_file = open("MetaData/calibration.txt", 'w')
		SetJoystickOn()
		SetVelocity(5, 5, 0, 0,max_vel=5)
		nothing = raw_input("Press enter when you are over the left inlet")
		SetPosition(5,0,0,0) # We want to be some distance removed from the inlet
		left_inlet = GetPosition()
		## I should move a bit from there and reset the axis no?
		nothing = raw_input("Press enter when you are over the right inlet")
		right_inlet = GetPosition()
		calibration_file.write(str(left_inlet[0]) +","+ str(left_inlet[1])+"\n")
		print "The y difference is ", left_inlet[1] - right_inlet[1]
		SetJoystickOff()
		print "calibration completed"
	else:
		inlet_file = open("calibration.txt", 'r')
		left_inlet = eval(inlet_file.readline())
		right_inlet= eval(inlet_file.readline()) 
		print "left inlet is ", left_inlet, " and is of type ", type(left_inlet)
		print "right inlet is ", right_inlet, " and is of type ", type(right_inlet)
	return left_inlet, right_inlet
