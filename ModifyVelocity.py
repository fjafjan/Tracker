import numpy as np
from StepControl import *
from numpy import array
from numpy.linalg import norm
from time import clock
from FindCorrectionVector import * 
from utilities import *


def ModifyStepVelocity(state, moving, parameters):
	# rod vel is the velocity of the particle as relative our camera
	# What we will do is use the positions we meassure anyhow and calculate the speed from these
	state.corr_vec[1] = -state.corr_vec[1]  # Because of some bug? Unknown!
	t0 = clock()
	if moving:
#		print "step_vel is ", step_vel, "correction vec is ", correction_vec
		new_velocity = state.step_vel + state.corr_vec
#		print  "we set a new speed, the correction vector was ", correction_vec
		##### THIS FIXES VERTICAL MOVEMENT. HERE IS THE MATH TO MAKE IT UNDERSTANDABLE
		##    y_v/x_v = y_dir/x_dir => y_v/x_v*x_dir = y_dir 
		## => [x_dir = x_end - x_cur, y_dir = y_end - y_cur] => 
	    ## => y_end = y_cur + (y_v/x_v)*(x_end - x_cur)
		
		
		if state.step_vel[0] > 0 and new_velocity[0] < 0: # We are close to the left inlet
			state.going_right = True
			print "We have hit the left border and are going right"
		elif state.step_vel[0] < 0 and new_velocity[0] > 0:
			state.going_right = False
			print "We have hit the right border and are going left"
#		StopAxes()
#		MoveToAbsolutePosition(going_to_x,going_to_y,0,0,0) ## We assume that we are at the left inlet
	else:
		new_velocity = state.step_vel.copy()
		print "we did not set a new speed"
		return state.going_right
	## The step engine sets the speed to "vel fac" times the speed we tell it to, so we have to companesate for this
	new_velocity *= parameters.vel_fac
	## There is some inherant error in the speed setting which causes the velocity to be different
	new_velocity /= state.speed_error
	state.step_vel = new_velocity
	SetSpeed(new_velocity[0],new_velocity[1], 0, 0, print_error=True)
	move_time = clock() - t0
	return state.going_right
