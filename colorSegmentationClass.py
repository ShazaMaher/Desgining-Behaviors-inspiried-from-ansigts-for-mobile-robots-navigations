from picamera.array import PiRGBArray
from picamera import PiCamera
from distanceClass import *
from motorClass import *
from colorSegmentationClass import *

import cv2
import numpy as np
import time
import imutils
import math

path = "/home/pi/master_project/master_project/img/"

class ImageProcessing():
	def __init__(self, image, path):
		self.lower_light = np.array([0,0,240], dtype = "uint8" )
		self.upper_light = np.array([255,15,255], dtype = "uint8")
		self.kernel = np.ones((7,7), np.uint8)
		self.path = path
		self.image = image
	
	def ImageCropping(self,img):
		height, width = img.shape
		cropped_height = height
		cropped_width = int(math.floor(width / 2))
		croppedLeft = img[0:height, 0:cropped_width]
		cv2.imwrite(self.path+"croppedLeft.jpg", croppedLeft)
		croppedRight = img[0:height, cropped_width + 1 : width]
		cv2.imwrite(self.path+"croppedRight.jpg", croppedRight)
		averageImageRight = np.mean(croppedRight)
		averageImageLeft = np.mean(croppedLeft)

		return (averageImageRight,averageImageLeft)


	
	def findContours(self,image):
		gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

		cv2.imwrite(self.path+"gray.jpg", gray)						 			
		thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)[1]
		cv2.imwrite(self.path+"thresh.jpg", thresh)

		# find contours in the thresholded image
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		#print(cnts)	

		# loop over the contours
		for c in cnts:
			# compute the center of the contour
			M = cv2.moments(c)
			area = cv2.contourArea(c)
			#print(area)

			if M["m00"] != 0 : #and area > 1200:
				cX = int(M["m10"] / M["m00"])
				cY = int(M["m01"] / M["m00"])
				# draw the contour and center of the shape on the image
				cv2.drawContours(thresh, [c], -1, (0, 255, 0), 1)
				cv2.circle(thresh, (cX, cY), 1, (255, 255, 255), -1)
				#print(cX,cY)

			else:
    				# set values as what you need in the situation
    				cX, cY = 0, 0

		cv2.imwrite(self.path+"Fres.jpg", thresh)
		#grayF = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY)
		#threshFinial = cv2.threshold(grayF, 100, 255, cv2.THRESH_BINARY)[1]
		(averageImageRight, averageImageLeft) = self.ImageCropping(thresh)
		return (averageImageRight, averageImageLeft)


	def findCircles(self, image):
                output = image.copy()
		gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

		cv2.imwrite(self.path+"gray.jpg", gray)

		thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)[1]
		cv2.imwrite(self.path+"thresh.jpg", thresh)


		# detect circles in the image
		circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, 1, 20,param1=50,param2=30,minRadius=0,maxRadius=0)
		 
		# ensure at least some circles were found
		if circles is not None:
			# convert the (x, y) coordinates and radius of the circles to integers
			circles = np.round(circles[0, :]).astype("int")
		 
			# loop over the (x, y) coordinates and radius of the circles
			for (x, y, r) in circles:
				# draw the circle in the output image, then draw a rectangle
				# corresponding to the center of the circle
				cv2.circle(output, (x, y), r, (0, 255, 0), 1)
   				cv2.circle(output,(x, y), r,(0,0,255),1)

		cv2.imwrite(self.path+"output.jpg", output)
		grayF = cv2.cvtColor(output,cv2.COLOR_BGR2GRAY)
		cv2.imwrite(self.path+"grayF.jpg", grayF)
		# = cv2.threshold(grayF, 240, 255, cv2.THRESH_BINARY)[1]
		#cv2.imwrite(self.path+"threshFinial.jpg", grayF)
		(averageImageRight, averageImageLeft) = self.ImageCropping(grayF)
		return (averageImageRight, averageImageLeft)

#begin streaming
#cap = cv2.VideoCapture(0)

"""
def main():
	
	try:
		cameraAvg = 0
		camera = PiCamera()
		camera.resolution = (1280, 720)
		camera.framerate = 60
		rawCapture = PiRGBArray(camera, size=(1280, 720))

		# allow the camera to warmup
		#time.sleep(0.1)

		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			# grab the raw NumPy array representing the image, then initialize the timestamp
			# and occupied/unoccupied text
			frame.seek(0)
			image = frame.array
			#while cameraAvg < 1000 :	
		        #frame.seek(0)
			#image = frame.array
			cv2.imwrite(path+"frame.jpg", image)
			ImageProc = ImageProcessing(image, path)
			#(cR, cL)= ImageProc.findCircles(image)
			(cR, cL )= ImageProc.findContours(image)
			

			print(cR)
			print(cL)
			cameraAvg = cL + cR
			frame.seek(0)
                        frame.truncate()


			#camera.stop_recording()
			print("cameraAvg:")
			print(cameraAvg)

			

	except KeyboardInterrupt:
		camera.stop_recording()


if __name__ == "__main__":
	main()
"""

