from utilities import *
from numpy import array, zeros
from StepControl import *
from PumpControl import *
from DetectParticleUtils import *
import time


from FindCorrectionVector import *
from ModifyVelocity import *


class DetectorOptions:
	def __init__(self,):
		self.printing_output 	= True
		self.starting_left   	= False
		self.needs_average 		= False
		self.needs_calibrate 	= False
		self.testing_disconnected= False
		self.extra_file          = -1 # we don't want an extra file to save atm
		self.saving_directory    = "E:/staffana/Feb 26/"
		self.badness_file  = open("Metadata/badnesses.txt", 'w')
		self.badness_file.write("Rank \tParticle nr \tcenter_dist \tmoving_badness \tmomentum \tthinness \tacc \ttotal_badness \t error \t abs_error \n")
		



class DetectorParameters:
	def __init__(self):

		## IDEAS: Lower the flow rate quite a bit: What we are studying should be invariant of speed (do better in slow flows?) and now it is so fast that the very short lag of the step engine causes some troubles.
		## Arguments for a high flow rate though could be that it will normally not reach quite so high speedS?

		self.fps_max 			= 10.
		self.correction_interval= 1*self.fps_max	 		# How often we correct the speed. 
		self.max_misses			= 5
		self.fast_speed 		= 55 # This is some number I have decreed!
		self.vel_fac 			= 1/10.

		#~ self.x,self.y			= 1490, 205 				# The x,y coordinates of the top left corner of what we want to crop
				#~ self.width, self.height = 365, 275

		self.x,self.y			= 1295, 105 				# The x,y coordinates of the top left corner of what we want to crop
		self.width, self.height = 540, 340
		self.size 				= (self.width, self.height)         # The resultant size of our image after resizing
		self.middle 			= [self.size[0]/2, self.size[1]/2]  # We want our particle to be close to the middle.
		self.box 				= (self.x,self.y,self.x+self.width,self.y+self.height)    # The bounding box for our cropping

		self.step_2_pixel		= 1300.
#		self.step_2_pixel   	= 940.								# The step engine distance to pixel ratio of the 20x microscope.
		self.pixel_2_step   	= 1./self.step_2_pixel				

		# these are the settings we used for full screen higher setting images, but really we don't need em...
		#x,y  				= 1155, 215
		#width, height 		= 685, 530
		#width, height 		= 1170, 780             	# The size of the image we want to crop
		#step_2_pixel   		= 1680
	
	def change_microscope_objective():
		pass
		# step_2_pixel = XXX
		
		
		## So the first thing to do is to change the pixel to step ratio, but the second question is if there are any static variables defined from these parameters 
		## will need to be updated?




	
class DetectorState:
	def __init__(self,parameters, options):
## I	NITIALIZATIONS									# Some ugly initializations
		self.old_pos 		= parameters.middle      					
		self.average_y 		= parameters.middle[1]		# The first frame it makes sense that conceptually we were previously "in the middle"
		self.last_y			= [0]*5						# We look at the five last values
		self.allsizes 		= array([])             	# Not used currently, could be nice in the future?	
		self.going_right 	= options.starting_left		# We assume that we start at the left inlet.
		self.flowing_right	= options.starting_left		# Presumably, the direction of the flow is the same as the particle...
		self.reversed_flow	= False						# We have not recently reversed the flow.
		self.particle_size 	= 0.							
		self.currentPosition= [0,0]
		self.rod_vel 		= 0
		self.corr_vec 		= zeros(2)
		self.reverse_cooldown= 100000
		self.break_force	= 0
		self.fail_counter	= 0
		self.expected_pos	= parameters.middle
#		self.extra_saving_file = open(get_filename(saving_directory + "position_tracking.txt"), 'w')
		self.pos_approx		= 0
		self.pump 		 	= PumpController()
		self.step_vel 		= 0
		
	def update(self, best_contour_nr, contours,  positions, parameters, frame_nr, timedata, options):
		if best_contour_nr == -1 or best_contour_nr == -2:   # DetectParticle will return -1 if no particle larger than -10 was found
			print "We have been too picky, or the edges etc were bad",  "the number of contours is " ,len(contours)
			self.pos_approx = self.old_pos + (self.rod_vel + self.corr_vec)
			#average_y = ((average_y*(i-1)) + pos_approx[1])/i
			self.last_y.insert(0,self.pos_approx[1])
			self.last_y.pop()
			self.average_y = sum(self.last_y)/len(self.last_y)

			if self.pos_approx[0] < 0:
#				print " we are reducing our x coordinate from ", pos_approx[0], " to 0"
				self.pos_approx[0] = 0
			elif self.pos_approx[0] > parameters.width:
				self.pos_approx[0] = parameters.width

			self.old_pos = self.pos_approx
	#		old_pos = [pos_approx[0], average_y]
			self.counter += 1
			if self.counter > parameters.max_misses:
				StopAxes()
				print "Contour not found in ", parameters.max_misses, " frames, program exiting"
				self.shut_down(options)
				exit()
			timedata.iteration_end = time.clock()
			return 
			# tell outer program to continue
		self.counter = 0

		self.pos_approx = positions[best_contour_nr]
		self.last_y.insert(0,self.pos_approx[1])
		self.last_y.pop()
		self.average_y = sum(self.last_y)/min(len(self.last_y),frame_nr)
		length = len(contours[best_contour_nr])
		self.particle_size = ((self.particle_size*(frame_nr-1)*1.0) + length)/frame_nr

#		print "Frame ", frame_nr, ", currently the particle size is ", self.particle_size, "and the size this round was ", length
		timedata.detection_end = time.clock()
	
		
			#### CALCULATE THE VELOCITY 
		if frame_nr == 1: 				 # If it is the first iteration
			self.old_pos = [self.pos_approx[0], self.average_y] # The velicty the first frame is 0
		
		curr_fps  = 1/(timedata.image_start - timedata.image_old)
		
		## This is the time before step correction took effect
		t1 = timedata.step_control_end - timedata.image_old

		## This is the time after step correction took effect
		t2 = timedata.image_start      - timedata.step_control_end

		#	print "corr vec is ", corr_vec
		self.simple_vel = (self.pos_approx - self.old_pos)
		if self.reverse_cooldown < 300:
			self.rod_vel = self.simple_vel
		else:
			correction_term = (array([self.corr_vec[0], -self.corr_vec[1]])*t1*parameters.step_2_pixel)
			self.rod_vel = self.simple_vel + correction_term
			#rod_vel = (pos_approx - old_pos) + (corr_vec*t1*step_2_pixel*curr_fps)
#			print "\n Our old approximation is ", self.simple_vel
#			print " and the correction vector contrib is ",correction_term
#			print "our rod_vel is thus ", self.rod_vel, " and ur corr_vec is ", self.corr_vec, "\n"
		self.old_pos = self.pos_approx
	#	old_pos = [pos_approx[0], average_y]


		#v1*t1 + v2*t2 = v3*t3 
		# v2*t2 = (v3*t3 - v1*t1)/t2
		## What do we want to know? We want to know the velocity we have NOW, ie v2. v2 = v1 + c
		## v1 = v3 - c * t2/(t1 + t2)
		## v2 = v3 - c*t2(t1+t2) + c*(t1+t2)/(t1+t2) =>
		## v2 = v3 + c*t1/(t1+t2) 
		## v3 = pos_approx - old_pos, t1+t2 = t3 = 1/curr_fps
	
	def update_correction_vector(self, state, parameters, options, current_frame):
		# Unless it's an even second or we are about to lose the particle do we try to correct:
		if current_frame%parameters.correction_interval == 0 or isNearEdge(self, parameters) or isGoingFast(self,parameters): 
			target_pos = GetTargetPos(self, parameters)
			# Where we want our particle to be depends on if are close to turning or not
			
#			print "the rod vel is ", self.rod_vel , " and our simple vel is ", self.simple_vel
			#~ self.corr_vec, moving = FindCorrectionVector(self, parameters, target_pos)
			## DANGER DANGER THIS WAS CHANGED WITHOUT MUCH THOGUHT
			self.corr_vec, moving = FindCorrectionVector(self.pos_approx, self.rod_vel, target_pos)

			
			if self.reversed_flow:
				print "\n We are adjusting for breaking \n "
				self.reverse_counter += 1
				self.break_force = [self.step_vel[0]*0.01, 0]
#				going_right = ModifyStepVelocity(step_vel, going_right, corr_vec+break_force, moving, speed_error, vel_fac)
				if self.reverse_counter > parameters.fps_max*2.5:
					self.reversed_flow = False
					self.break_force = 0
					print "\n \n We are done breaking \n\n"
#				start_direction = going_right
#				corr_vec[0] -= step_vel[0]*0.1
#				print "we are adding reverse flow bonus to corr vel "
			print "step_vel before correction is ", self.step_vel
			self.going_right = ModifyStepVelocity(self, moving, parameters)
			print "step_vel after correction is ", self.step_vel, " and corr_vec is ", self.corr_vec

#			print "corr_vec afterwards is ", corr_vec
			#self.step_vel += self.corr_vec # This should already be done
		else:
			if current_frame==1:
				oldTime     = time.clock()
				SaveStepPos(parameters.extra_saving_file, parameters.saving_directory, timedata)
			self.corr_vec *= 0 # We have no correction vector to take into consideration
		## replace these three lines with a singular function, it will probably also make you improve readability
		## NOTE TO SELF: ADD STEPFILE AGAIN!!
		
		#stepfile.write(str(i)+"\t"+to_str(self.pos_approx-parameters.middle, 5))
		#stepfile.write("\t"+to_str(self.rod_vel, 4)+"\t"+to_str(self.step_vel - self.corr_vec))
		#stepfile.write("\t" + to_str(self.corr_vec) + "\t" + to_str(self.step_vel) + "\n")
	
	def check_pump(self):
		if (self.currentPosition[0] < -25 and self.flowing_right) or (self.currentPosition[0] > -10 and not self.flowing_right):  #These numbers have to be tweaked obviously
			if self.reverse_cooldown > 100:
				self.reverse_cooldown = 0
				p = PumpThread(self.pump)
				p.setDaemon(False)
				p.start()
				print "\n\n !!!!!!!! WE HAVE REVERSED THE FLOW !!!!!!! \n\n"
				self.reversed_flow = True
				self.reverse_counter = 0
				self.flowing_right = not self.flowing_right # This just flips the value
		self.reverse_cooldown += 1
	
	# Closes all connections and files and shuts down.
	def shut_down(self, options):
		TerminateStepConnection(options.starting_left)
		self.pump.CloseConnection()
		return
		


