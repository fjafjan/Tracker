from utilities import to_str

class TimeData:
	def __init__(self):
		self.timefile = open("MetaData/benchmarks.txt", 'w')
		self.timefile.write("Image time"+"\t\t"+" Contour/Edge time" + "\t" + "Particle finding time")
		self.timefile.write("\t"+"Moving time"+ "\t\t"+"Position saving time"+"\t"+"Total time"+ "\n")
		self.iteration_start    = -1
		self.iteration_end 		= -1 
		self.image_start 		= -1
		self.image_end			= -1
		self.image_old			= -1
		self.contour_start		= -1
		self.contour_end		= -1
		self.detection_start	= -1
		self.detection_end		= -1
		self.step_control_start	= -1
		self.step_control_end	= -1
		self.pos_save_total 	= 0
	def write_times(self):
		image_time 		= self.image_end - self.image_start
		contour_time 	= self.contour_end - self.contour_start
		detection_time  = self.detection_end - self.detection_start
		move_time 		=  self.step_control_end -  self.step_control_start
		iter_time 		= self.iteration_end - self.iteration_start
		pos_save_time   = self.pos_save_total + 0
		k = 1000
		self.timefile.write(to_str(image_time*k)+"\t\t"+to_str(contour_time*k)+"\t\t"+to_str(detection_time*k)+"\t\t")
		self.timefile.write(to_str(move_time*k)+ "\t\t" + to_str(pos_save_time*k)+"\t\t"+to_str(iter_time*k)+"\n")
#		print "I just wrote ", image_time*k, contour_time*k, detection_time*k, move_time*k, iter_time*k


#t.image_start = 5
#t.image_end = 3
#t.write_times()
