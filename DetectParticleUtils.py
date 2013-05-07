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
from PIL import Image, ImageColor
vertical_penalty = 2 # We know that movement is far less common in the vertical direction, so vertical movement is more bad.

## If we call the velocity before correction (but after taking the last image) v_1 , the velocity afterwards v_2 and the meassure velocity v_3
## we have the simple relationship:
## v_1 * t_1 + v_2*t_2 = v_3 * t_3
## where v_2 = v_1 + c and t_3 = t_1 + t_2
## solving for v_1 gives us
## v_1 * (t_1 + t_2) + c*t_2 = v_3*  (t_1 + t_2)
## => v_1 = v_3*(t_1+t_2)/(t_1 + t_2) - c*t_2/(t_1 + t_2)
## => v_1 = v_3 - c * t_2/(t_1 + t_2)
## v_3 = /p_2 - p_1)/t_3

def CalculateMomentBadness(particle_position, old_pos, timedata , state, momentum):
	correction_vec 	= state.corr_vec
	old_vel 		= state.rod_vel

	corr_time = (timedata.detection_start - timedata.step_control_end)
	curr_fps  = 1/(timedata.image_start - timedata.image_old)
	vel_vec = (particle_position - old_pos)*curr_fps # *fps_max ~== /dt
	## The above only works iff: The process is not "lagging" and that the execution time up to the measure point is the same. 
	## The first should always be true, but the second only vaguelly.

	t1 = timedata.step_control_end - timedata.image_old
	t2 = timedata.image_start      - timedata.step_control_end
	#~ print "old vel is ", old_vel, " and correction_vec is ", correction_vec
	#~ print  "old pos is ", old_pos, " and  (old_vel/curr_fps) is ", (old_vel/curr_fps), " and (correction_vec*t2) is ", (correction_vec*t2)
	expected_pos = old_pos + (old_vel/curr_fps)# + (correction_vec*t2)  # They only have 1/fps_max seconds to move!
	#~ print "the correction vector contribution is ",  (correction_vec*t2), " and t2 is ", t2
	# print "expected position is ", expected_pos, " but our real pos is ", particle_position
	real_vec = vel_vec - (correction_vec*(corr_time/curr_fps))
	accel = (real_vec - old_vel)*curr_fps
	accel[1] = accel[1]*vertical_penalty
	moment_badness = momentum*np.square(norm(accel))
#	print "moment badness is ", moment_badness, " and expected_pos is ", expected_pos
	return moment_badness, expected_pos

def CalcThinness(contour_j, thin_weight):
	try:
		pair_distance = max(spatial.distance.pdist(np.sum(contour_j, axis=1)))
		thinness = np.square(thin_weight*len(contour_j)/(pair_distance*pair_distance))
	except:
		# For some reason we have an empty countour that made it this far? 
		print "\n \n \n ERROR WITH THINNESS ", np.sum(contour_j, axis=1), contour_j, "\n \n \n" 
		thinness =  10000000000
	# This is a candidate particle. If it is already bigger it will never be the best.
	return thinness
	print_stats, j, position, state

def print_stats(state, j, position,  rank, badness, weights, acc, timedata, options, parameters):

	old_vel 		= state.rod_vel
	#			(j, position, old_pos, timedata, badness_file, state, rank, badness, weights, acc, ,parameters)
	curr_fps  = 1/(timedata.image_start - timedata.image_old + 0.0001)
	corr_time = (timedata.detection_start - timedata.step_control_end)
	momentum, dist_weight, move_weight, thinness, acc = weights
	dist_from_center = sqrt((position[0]-parameters.middle[0])**2+(position[1]-parameters.middle[1])**2 )
	vel_vec = (position - state.old_pos)*curr_fps						# Relative velocity
	speed = norm(vel_vec)										# The size of the velocity
	vel_abs = vel_vec - (state.corr_vec*(corr_time/curr_fps))			# Absolute velocity
	accel = norm(vel_abs - old_vel)*curr_fps			   		# Acceleration
	moment_bad = momentum*np.square(accel)/100
#	manual_sum = (dist_from_center*dist_weight) + (np.square(speed)*move_weight) + moment_bad + thinness
	options.badness_file.write(str(rank)+"\t"+str(j)+"\t\t"+to_str(dist_from_center*dist_weight)+"\t"+to_str(np.square(speed)*move_weight))
	options.badness_file.write("\t"+to_str(moment_bad )+"\t"+to_str(thinness)+"\t"+to_str(acc)+"\t"+to_str(badness[j])+"\t")	
	options.badness_file.write(to_str(position) + "\t"+to_str(state.expected_pos - position))
	options.badness_file.write("\t" + to_str(norm(state.expected_pos - position))+"\n")

def save_contour_image(j, contours, pix, rank, run_nr):
	pix_copy = pix.copy()
	cv2.drawContours(pix_copy,[contours[j]],-1,(0,255,0),1)
	im = Image.fromarray(pix_copy)
	im.save("Images/Contours/Frame" + str(run_nr)+  "_rank" + str(rank)+" particle_nr "+str(j)+ ".jpg")

def save_position_images(best_pos,old_pos, old_vel, curr_fps, expected_pos, pix, frame_nr, particle_nr, parameters):
	pix_copy = pix.copy()
	
	## Add legend to picture
	colors = ("Red", "Green", "Darkblue", "Teal")
	text   = ["Actual position", "Old position", "Expected position", "Constant motion"]
	im = Image.fromarray(pix_copy)
	add_legend(im, text, colors)
	pix_copy = array(im)
	particle_size = 3

	## Adds the relevant points to the image and checks that they are not overlapping
	const_vel_pos = old_pos+(old_vel/curr_fps) + array([5,0])
	if tuple(const_vel_pos) in (tuple(pos) for pos in (expected_pos, old_pos, best_pos)):
#		print "const vel pos overlaps"
		particle_size += 2 
	pix_point = add_point_to_image(const_vel_pos,  pix_copy, parameters.middle,  color=colors[3], size=particle_size)

	if tuple(expected_pos) in (tuple(pos) for pos in (old_pos, best_pos)):
#		print "expected pos overlap"
		particle_size += 1
	pix_point = add_point_to_image(expected_pos,  pix_point, parameters.middle, color=colors[2], size=particle_size)

	if tuple(old_pos) == tuple(best_pos):
#		print "old pos and best pos overlap"
		particle_size += 1
	pix_point = add_point_to_image(old_pos,		pix_point, parameters.middle, color=colors[1], size=particle_size)

	pix_point = add_point_to_image(best_pos, 	pix_point, parameters.middle, color=colors[0], size=particle_size)
	im = Image.fromarray(pix_point)

	name  = "particle_"+str(particle_nr)
#	print "name is ", name, str(name)
	im.save("Images/Positions/Frame" + str(frame_nr)+name+"position"+ ".jpg")
	#pix_point = save_point_image(very_old_pos, pix_point, "very_old_pos", (255, 140,105), run_nr)
	

def add_point_to_image(position_in, pix, middle, run_nr=-1, flip=True, color=(0,255,0), size=2):
	pix_copy = pix.copy()
	if type(color) == str:
		color = ImageColor.getrgb(color)
	position_c = list(position_in)
	position = array([int(position_c[0]), int(position_c[1])])
	if flip: # If we need to flip the y position to get it to align with the image
		position[1] = (2*middle[1]) - position_c[1]
	if position[0] < 1:  #I am not sure if the 0 point is OK, probably but better safe than sorry
		position[0] = 1
#		print "we have particle ", run_nr, " to the corner from ", position_in
	if position[1] < 1:
		position[1] = 1
#		print "we have particle ", run_nr, " to the corner from ", position_in
	cv2.drawContours(pix_copy,[array([position])],-1,color,size)
	return pix_copy

def isNearEdge(state, parameters):
	if state.pos_approx[0] < 0.1*parameters.height or state.pos_approx[0] > 0.9*parameters.height:
		return True
	elif state.pos_approx[1] < 0.1*parameters.width or state.pos_approx[1] > 0.9*parameters.width:
		return True
	else:
		return False

def isGoingFast(state, parameters):
	return abs(state.rod_vel[0]) > parameters.fast_speed or abs(state.rod_vel[1]) > parameters.fast_speed
	
def GetTargetPos(state, parameters):
	if state.currentPosition[0] < -20 and state.flowing_right:
		target_pos = [parameters.middle[0] + parameters.middle[0]/2, parameters.middle[1]]
	elif state.currentPosition[0] > -15 and not state.flowing_right:
		target_pos = [parameters.middle[0] - parameters.middle[0]/2, parameters.middle[1]]
	else:
		target_pos = parameters.middle
	return target_pos
#def add_legend(img):
#	text		= "Red is actual position, green is old position, dark blue is expected position and teal is constant motion"
#	text_pos 	= (10,10)
#	text_color  = (0,0,0)
#	font_path 	= "C:\WINDOWS\Fonts\Arial.ttf"
#	font 		= ImageFont.truetype(font_path, 14, encoding='unic')
#	
#	img 		= ImageDraw.Draw(img)
#	draw.text(text_pod, text, fill=text_color, font=font)
#	del draw
#	img.save(C:/test.jpg)
