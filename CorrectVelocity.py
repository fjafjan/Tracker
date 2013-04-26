import ModifyStepVelocity
import FindCorrectionVector

def CorrectVelocity(Options, rod_vel, currentPosition, flowing_right, pos_approx, step_velocity_const, going_right, speed_error, vel_fac):
	if i%correction_interval == 0 or isNearEdge(pos_approx,width, height) or isGoingFast(rod_vel,middle): # Unless it's an even second or we are about to lose the particle do we try to correct:
		if currentPosition[0] < -20 and flowing_right:
			target_pos = [middle[0] + middle[0]/2, middle[1]]
		elif currentPosition[0] > -15 and not flowing_right:
			target_pos = [middle[0] - middle[0]/2, middle[1]]
		else:
			target_pos = middle
		print "the rod vel is ", rod_vel , " and our simple vel is ", simple_vel
		corr_vec, moving = FindCorrectionVector(pos_approx, rod_vel*fps_max, target_pos)
		
#			print "corr_vec first is ", corr_vec
		if reversed_flow:
			print "\n We are adjusting for breaking \n "
			reverse_counter += 1
			break_force = [step_velocity_const[0]*0.01, 0]
#				going_right = ModifyStepVelocity(step_velocity_const, going_right, corr_vec+break_force, moving, speed_error, vel_fac)
			if reverse_counter > fps_max*2.5:
				reversed_flow = False
				break_force = 0
				print "\n \n We are done breaking \n\n"
		going_right = ModifyStepVelocity(step_velocity_const, going_right, corr_vec, moving, speed_error, vel_fac)
#			print "corr_vec afterwards is ", corr_vec
	else:
		if i==1:
			oldPosition = GetPosition()
			oldTime     = time.clock()
			SaveStepPos(extra_saving_file, saving_directory)
			#outfile.write(to_str(oldTime,10) + "\t" + to_str(oldPosition[0],10) + "\t" + to_str(oldPosition[1],10) + "\n")
		corr_vec *= 0 # We have no correction vector to take into consideration
	stepfile.write(str(i)+"\t"+to_str(pos_approx-middle, 5)+"\t"+to_str(rod_vel, 4)+"\t"+to_str(step_velocity_const - corr_vec)+"\t" + to_str(corr_vec) + "\t" + to_str(step_velocity_const) + "\n")
	step_velocity_const += corr_vec
