## This function takes an image from the channel and finds the contour
## The inputs are as follows:
## im: an image from the channel
## aver_im: An "average image" which is supposed to be the noise
## from the camera and the various lenses etc.
## thresh: the threshhold values used by the edge detection agorithm
## printing output (should be changed!!!)

	
from numpy import array
import cv2
from PIL import Image
from utilities import removeAverage, save_image_as

def GetContours(im, aver_im, thresh,printing_output, iteration):
	
	## Here we convert im from the "Image object" type to the array type
	## and then remove static noise from the image
	pix     = array(im)
	pix_pre = pix.copy()
	pix = removeAverage(pix, aver_im) ## NOTE TO SELF 1: Rename this function?

	## Here we apply a gaussian blur to the image and afterwards use
	## canny edge detection. 
	sigma = 1 						## NOTE TO SELF 2: Constants for the canny edge detection are defined here but they should not be
	blur_im = cv2.GaussianBlur(pix, (7,7), sigma)
	edges   = cv2.Canny(blur_im, thresh/2.5,thresh)

	
	## If desired we save the image before and after removing the noise
	if printing_output:
#		Image.fromarray(pix).save("Images/Averaging/" + str(iteration) + "post_average.jpg")
#		Image.fromarray(pix_pre).save("Images/Averaging/" + str(iteration) + "pre_average.jpg")

		## This saves all the contours. We should add o the image queue here. 
		save_image_as(array(edges), array([array([array([])])]), "contours" + str(iteration))
		
	
	## We use the cv2 function findContours to find contiguous particle
	## candidates among the edges detected by the canny algorithm.
	contours, waste = cv2.findContours(edges,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	return contours, pix



### Histogram equalized values for the Canny Edge detection. Currently not used, maybe in the future

#	im_eq  = ImageOps.equalize(Image.fromarray(pix))
#	pix_eq = array(im_eq)
#	pix_mean = pix.mean()
#	edges_eq= Canny(pix_eq, pix_mean*0.66, pix_mean*1.33)
#	save_image_as(array(edges_eq), array([array([array([])])]), "contours" + str(i) + "canny_const"+str(pix_mean))
