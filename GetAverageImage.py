import numpy as np
import Image , ImageGrab

from StepControl import *

def GetAverageImage(averages, start_x, iter_step, box):
	aver_ims = []
	averages  = 40
	nothing = raw_input("Press enter when you are ready to remove static noise")
	for i in range(0,averages):
		MoveToAbsolutePosition(start_x+(iter_step*i),0,0,0,1) ## We assume that we are at the left inlet
		aver_ims.append(ImageGrab.grab(box))
	dirt_im = np.array(aver_ims[0])
	print "aver_ims0 is ", aver_ims[0]
	dirt_im = dirt_im.astype(np.float32)*0
	for im in aver_ims:
		dirt_im += (np.array(im)).astype(np.float32)
	dirt_im = dirt_im /averages
	dirt_im = (abs(dirt_im -np.mean(dirt_im))).astype(np.uint8)
	dirt_im = Image.fromarray(dirt_im)
	dirt_im.save("Images/Averaging/average_image.jpg")
	dirt_arr= np.array(dirt_im) 
	dirt_arr= dirt_arr.astype(np.float32)
	MoveToAbsolutePosition(start_x,0,0,0,1)
	return dirt_arr
