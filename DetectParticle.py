# Tries to detect the right particle. We use three conditions:
# 1) The particle will be of some size. This is true for almost all times and
#    orientations, only when the particle is alligned in the Z-X plane will it for
#    short periods be tiny, but since in that plane it rotates very quickly once it
#    turns, it should not matter much. 
#     Particles that are "too small" (currently less than 10 pixels) are disgarded
# 2) The particle will be thin. We compare the maximum distance between two points
#    in every detected contour with the total size of that contour. So a long thin
#    contour will do better than a big blob or circle. 
#    This is the first meassure of a candidate particle
# 3) The particle will not move. We thus assume that we have previously detected
#    the particle at a position. We then check to see how much the particle has moved
#    the more it has moved the worse it is
#    This is the second meassure of a candidate particle
# 4) Being far from the center. We pick a particle currently in the center of the 
#    screen and the goal is to keep it close to there. This should however be a linear
#    penalty, the real particle can stray while something else shows up in the middle
#    And in that case the penalty for "jumping" over there must dominate (it is square)
#    These two (currently) meassures are combined and the best particle is picked. 

# I should probably also add a penalty for being bigger than we know the particel to be.

# CURRENT PROBLEM:
from time import clock
import numpy as np
import scipy as sp
from scipy import spatial
from numpy import array, argmin, zeros
from numpy.linalg import norm
from bisect import insort
from math import sqrt
from utilities import *
from DetectParticleUtils import *
import cv2
from PIL 	import Image
	
# We can speed this up pretty significantly by changing data structure I bet. 

# HERE WE SPECIFY PARAMETERS
min_size 	  = 10		# The minimum size we consider
max_size      = 200 	# The maximum size we consider
move_weight   = 5 		# The weight we give to the particle not moving relative to the camera
momentum      = 100    	# The weight we give to the particle not changing speed
dist_weight   = 8     	# The weight we give tot he particle not being close to the center
thin_weight   = 300 	# The weight we give to the particle being thin
nr_of_bad     = 5   	# This is the number of particles we will check the roundness of.
max_acc 	  = 50

## I should move this.. let's do it now
## Initializations

## Let's replace fps_max with out time_data knowledge!
## CORRECTION VEC SHOULD BE = (corr_vec-break_force)*step_2_pixel
def DetectParticle(state,contours,run_nr, timedata,pix, parameters, options):
	timedata.detection_start = clock()

	# some ugly initializations
	if run_nr > 0:
		old_pos   = state.old_pos
		old_pos[1]= state.average_y
		curr_fps  = 1/(timedata.image_start - timedata.image_old)
		corr_time = (timedata.detection_start - timedata.step_control_end)
		print "the time for the correction_vec to act is ", corr_time, " and our current fps is approx ", curr_fps, " and our current position is ", old_pos

	least_bad = [100000000]*nr_of_bad
	sizes = array([]) ## We then append this array to the big array
	badness, velocity, position = zeros(len(contours)), zeros((len(contours),2)), zeros((len(contours),2))
	accelerations = zeros(len(contours))
	found_particle = False
	
	t0 = clock()
	for j in range(0,len(contours)):
		# We always remove particles that are too small.
		if len(contours[j]) < min_size or len(contours[j]) > max_size:
			badness[j] = 100000000  # We simply do not want this particle
			continue              # particle to be this small that it won't matter
			
		# After a few iterations we hope to have a pretty good estimation of the particle size
		# Note: It is harder to say something about being much smaller, as it might rotate 
		if run_nr > 10: 
			if len(contours[j]) > 2*state.particle_size:  
				# print "I am too big, I am size ", len(contours[j]), " compared to our particle which we think is about ", state.particle_size, ", I am particle nr ", j 
				badness[j] = 100000000
				continue 
		found_particle = True	# we passed the preceeding checks without "continue"

		## We find the position of this particular particle
		tmp_pos = np.sum(contours[j], axis=0)          # Calculate position
		position[j] = tmp_pos[0]/len(contours[j])      # Normalize, the pos[0] is because of an extra layer of nothing
		position[j][1] = (parameters.middle[1]*2)-position[j][1]  # Makes the y-axis positive, ie bottom up and not the opposite
		## Add badness to particles for their acceleration or if they are too close to the center
		## Note we can't consider the speed/acceleration the first frame, as we have no reference point. 
		## Instead we then consider it's distance from the center as the primary attribute
		if run_nr > 2: 
#			print "1) we added the particle ", j, " with position ", position[j]
			accelerations[j], expected_pos = CalculateMomentBadness(position[j], old_pos, timedata , state, momentum) 
			accelerations[j] /= 10000 ## The badnesses we get can be gigantic even for small numbers...  this is just to compensate. Stupid
			badness[j] += accelerations[j]
			if run_nr>10:
				badness[j] += abs(len(contours[j]) - state.particle_size) 
		elif run_nr == 2:
			badness[j] += 100*norm(old_pos - position[j])
			expected_pos = old_pos
		else:
			distance_from_center = sqrt( (position[j][0] - parameters.middle[0])**2 + (position[j][1] - parameters.middle[1])**2)
			badness[j] += dist_weight*(norm(distance_from_center)**1.3)
			expected_pos = parameters.middle

		## Compare the current particle to the best so far, add to list if among the best
		if badness[j] < least_bad[-1]: # Top N best so far
#			print "2) we added the particle ", j, " with position ", position[j]
			least_bad.pop(-1)
			insort(least_bad, badness[j]) # Hopefully this means the array shoud remain sorted

	## If we have looked at all our contours and they are all too large or small
	if not found_particle:
		return -2, position   # -2 means there just weren't any even remotely good particles

	options.badness_file.write("\n\n" + "Frame " + str(run_nr) + "\n")
	least_bad_added = least_bad[:]

	print "\n"
	## We add badness to particles that are not thin. 
	for j in range(0,len(contours)):
		# index -1 means the last of the array and it should be sorted so the last is largest
		if badness[j] <= least_bad[-1]: 
			try:
				rank = least_bad.index(badness[j])  # It would stand to reason that the least_bad_ array should contain this badness
			except ValueError as e:
				print "!!!!BUG!!!! \n", e
				print "least bad is ", least_bad
				noway = error_bug ## this will crash the program
			#~ else:
				#~ print "our current value is ", badness[j], " with rank ", rank, " and least_bad is ", least_bad
			#print "our vector of least bad is ", least_bad, " and the badness is ", badness[j]
			thinness = CalcThinness(contours[j], thin_weight)
			badness[j] += thinness
			least_bad_added[rank] += thinness
			#~ print "2) we added the particle ", j, " with position ", position[j]
			if options.printing_output:
				pix_point = add_point_to_image(position[j], pix, parameters.middle, color="Red", size=3) 
				save_contour_image(j, contours, pix_point, rank, run_nr)
			#~ print "3) we added the particle ", j, " with position ", position[j]

		else:
			badness[j] +=5000000 # We don't want anyone out of the top N.
	least_bad = least_bad_added
	least_bad.sort()
	print "\n"

	for rank in range(0, nr_of_bad):
		###### MOST LIKELY CULPRIT ######
		ind = np.where(badness == least_bad[rank])[0]
		if len(ind) == 0:
			ind = np.argmin(abs(badness - least_bad[rank]))
			if least_bad[rank] != 100000000:
				pass
#				print "our problem value is ", least_bad[rank], " and our best fit is ", badness[ind]
		else:
			ind = ind[0]
		thinness = CalcThinness(contours[ind], thin_weight)
		acc = sqrt(accelerations[ind]/momentum)
		weights = (momentum, dist_weight, move_weight, thinness, acc)
		print_stats(state, ind, position[ind],  rank, badness, weights, acc, timedata, options, parameters)

	best_particle = argmin(badness)

	if options.printing_output:
		if run_nr > 1:
			save_position_images(position[best_particle],old_pos, state.rod_vel, curr_fps, expected_pos, pix, frame_nr=run_nr, particle_nr=best_particle, parameters=parameters)
#			pix_point = save_point_image(expected_pos, pix, "expected", (0,0,255), run_nr, save=False)
#			pix_point = save_point_image(old_pos + (old_vel/curr_fps), pix_point, "no_correction", (0,220,220), run_nr, save=False)
#			pix_point = save_point_image(old_pos, pix_point, "old_pos", (0,255,0), run_nr, save=False, flip=True)
#			#pix_point = save_point_image(very_old_pos, pix_point, "very_old_pos", (255, 140,105), run_nr)
#			pix_point = save_point_image(, pix_point, "particle_"+str(j), (255,0,0), run_nr, flip=True)
#	print "particle position is ", position[best_particle], " and our old position is ", old_pos, " frame nr ", run_nr
#	print "the best part is ", best_particle, " and acceleration is ", accelerations[best_particle]
	
	if run_nr > 1:
		temp_accel, expected_pos = CalculateMomentBadness(position[best_particle], old_pos, timedata , state, momentum) 
		if accelerations[best_particle] != temp_accel:
			pass
#			print "accelerations[bp] is ", accelerations[best_particle], " but the actual acceleration of that particle is ", temp_accel
	
	if position[best_particle][0] == 0 and position[best_particle][1] == 0:
		print "\n SOMETHING HAS GONE WRONG WE ARE AT POSITION 0 0!!! :(:(:( \n\n"
	pass
#	print "max acc is compared to ", sqrt(accelerations[best_particle])/momentum*100, " instead of using expected_pos which would give us ", norm(expected_pos - position[best_particle])
	if sqrt(accelerations[best_particle])/momentum*100 > max_acc:
		print "we excluded particles for accelerating too much "
		if options.printing_output and run_nr > 1:
			for j in range(0,len(contours)):
				if badness[j] <= least_bad[-1]: # index -1 means the last of the array and it should be sorted so the last is largest
					save_position_images(position[j],old_pos, state	.rod_vel, curr_fps, expected_pos, pix, frame_nr=run_nr, particle_nr=j, parameters=parameters)
#					draw = ImageDraw(pix_point)	
#					draw.text((10,10), "Red is actual position, green is old position, dark blue is expected position and teal is constant motion"
#					pix_point = save_point_image(old_pos + (old_vel/curr_fps), pix_point, "no_correction", (0,220,220), run_nr, save=False)
#					pix_point = save_point_image(expected_pos, pix, "expected", (0,0,255), run_nr, save=False)
#					pix_point = save_point_image(old_pos, pix_point, "old_pos", (0,255,0), run_nr, save=False, flip=True)
#					#pix_point = save_point_image(very_old_pos, pix_point, "very_old_pos", (255, 140,105), run_nr)
#					pix_point = save_point_image(position[j], pix_point, "particle_"+str(j), (255,0,0), run_nr, flip=True)
						
		return -1, position
	return best_particle, position
 
