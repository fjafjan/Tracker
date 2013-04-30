import numpy as np
from numpy import array
from numpy.linalg import norm
from time import clock
from StepControl import NormalizeVector


### So the plan is this: We calculate our position and velocity
### Case 1: If we are "close" to the center of the screen then we want our velocity to be 0.
### 	Case 1-1: Our current velocity is "almost zero"
### 		Action: Do nothing, we are happy
### 	Case 1-2: Our velocity is "something"
###			Action: Add a small correction in the opposite direction of our current velocity
### Case 2: If we are "far" from the center of the screen
### 	Case 2-1: Our velocity is "almost zero"
###			Action: Add a small correction in the direction of the center
###		Case 2-2: Our velocity is noticeable
###         Case 2-2-1: Our velocity is in the direction of the center
### 			Case 2-2-1-1: The velcity is quite large
###					Action: Add a correction in the opposite direction from our current velocity
###				Case 2-2-1-2: Our velocity is quite small
###					Action: do nothing, 
###         Case 2-2-2: Our velocity is away from the center
###				Action: Add small correction in the direction of M - V 
###					where M is the vector towards the middle and V is our velocity

######## NOTE ########
### The rod velocity we get in to this function is not dependent on the FPS. Ie, it's just between this frame and the previous one. 

### I now changed this. I should check the code and see if this messes things up later on. 
close_to_center = 40   # some fairly arbitrary number indicating when a particle is "close" to the center
small_velocity  = 5  # No idea what is reasonable here, this might be huge? tiny? This is tiny. 
large_velocity = 25  # It's better to be conservative here honestly, no reason to not try to slow down
increment_size  = 0.1 # 10% 
almost_equal    = 0.80 # How close the two vector have to be to pointing in the same direction.
step_2_pixel    = 940. # Conversion from our pixel scale to our real length scale.  
#step_2_pixel    = 1680
pixel_2_step     = 1./step_2_pixel


def FindCorrectionVector(rod_pos, rod_vel, middle):
	t0 = clock()
	moving 			= False# If we already have a good velocity there is no need to apply our "no change".
	correction_vec   = array([0,0])
	if np.linalg.norm(rod_pos - middle) < close_to_center:  
		if norm(rod_vel) < small_velocity:
			print "We are standing still near the center"#
#			correction_vec = (middle - rod_pos)*0.001
#			moving = True
			#It sucks when we are floating around not in the middle...
			pass 										# Do nothing
		else:
			print "We are moving near the center"
			correction_vec = (rod_vel)*-0.5 # We slow the speed by half, should be good enough. 
			moving = True
	
	else: 												# Case 2
		middle_vec = middle - rod_pos  					# The vector from our current pos to the middle
		#middle_vec[1] = rod_pos[1] - middle[1]			# Let's see if this fixes things?
		if norm(rod_vel) < small_velocity: 				# If we are "standing still"
			print "We are standing still far away from the center"
			correction_vec = (middle_vec)*increment_size # If vel ~= 0 this will put is near the center in ~10 seconds
			moving = True
		elif np.dot(NormalizeVector(rod_vel), NormalizeVector(middle_vec)) > almost_equal:
			if np.linalg.norm(rod_vel) > large_velocity:  # We are moving too fast towards the center
				correction_vec = (rod_vel)*-0.25			# We are already going in a pretty good direction, so we just try to slow down. 
				moving = True
			print "We are moving towards the center"
			pass 										# We are moving towards the center, do nothing
		else: 											# Else we are not moving towards the center
			#~ correction_vec = -1*rod_vel
			#~ moving = True
			print "We are far away fromt he center and going further"
			desired_vec = (middle_vec/np.linalg.norm(middle_vec))*norm(rod_vel)*0.5
			correction_vec = desired_vec - rod_vel		# (v+c) ~= v' => c ~= v'-v # Note this is too simple
			print "norm of our correction vec is ", np.linalg.norm(correction_vec) , " and the norm of our current rod vel is ", np.linalg.norm(rod_vel)
			moving = True
			print "rod vel is ", rod_vel, " and middle vec is ", middle_vec, " and our new  corr_ vec is ", correction_vec
			#~ #correction_vec = correction_vec*increment_size
	
	print "our found correction vec is ", correction_vec, " and our percieved rod_vel is ", rod_vel
	correction_vec = correction_vec*pixel_2_step*0.8 # We try making it just a little bit smaller so that the velocity changes don't overshoot so much...
	correction_vec[1] = correction_vec[1]*0.5 # Vertical movements should be less extreme and require less extreme corrections
	print "correction vector adjusted for pixel 2 step is ", correction_vec
#	find_corr_time = clock() - t0
	return correction_vec, moving



## The motivation for desired vec and the following calculation is as follows:
## We want our resulting velocity v' to have the following properties
## v' || d
## |v'| = |v|/2
## where d is the vector towards the center and v is our current velocity. 
## Ie we want to be going towards the center, with half of our current velocity. 
## givven these properties we also define v' as being
## v' = d/|d| * |v|/2 
## ie, a normalized d times half the size of v. 
