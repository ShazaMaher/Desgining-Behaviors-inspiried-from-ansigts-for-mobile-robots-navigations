#import libs
import cv2
import numpy as np
import time
import imutils
import math


lower_light = np.array([0,0,240], dtype = "uint8" )
upper_light = np.array([255,15,255], dtype = "uint8")

kernel = np.ones((7,7), np.uint8)

K = 1

path = "/home/shaza/Documents/masterthesis/masterThesis/img/"

def sigmoid(x):
	y = 1 /(1 + np.exp(- K * x))
	return y  

def findSigmoidOfImageParts(averageImageLeft, averageImageRight):
	sigmoidLeft = sigmoid(averageImageRight)
	sigmoidRight = sigmoid(averageImageLeft)

	return (sigmoidLeft, sigmoidRight)

def findSigmoidofDistanceSensor(distanceSensorValue):
	distanceSensorValueSigmoid = sigmoid(distanceSensorValue)
	return 	distanceSensorValueSigmoid

def ImageCropping(img):
	height, width = img.shape
	cropped_height = height
	cropped_width = int(math.floor(width / 2))
	croppedLeft = img[0:height, 0:cropped_width]
	cv2.imwrite(path+"croppedLeft.jpg", croppedLeft)
	croppedRight = img[0:height, cropped_width + 1 : width]
	cv2.imwrite(path+"croppedRight.jpg", croppedRight)
	averageImageRight = np.mean(croppedRight)
	averageImageLeft = np.mean(croppedLeft)
	print(averageImageRight,averageImageLeft)
	return (averageImageRight,averageImageLeft)



def findContours(image, path):
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        cv2.imwrite(path+"gray.jpg", gray)
	thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)[1]
        cv2.imwrite(path+"thresh.jpg", thresh)

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

		if M["m00"] != 0 and area > 1200:
			cX = int(M["m10"] / M["m00"])
			cY = int(M["m01"] / M["m00"])
			# draw the contour and center of the shape on the image
			cv2.drawContours(frame, [c], -1, (0, 255, 0), 1)
			cv2.circle(frame, (cX, cY), 2, (255, 255, 255), -1)
			#print(cX,cY)

		else:
    			# set values as what you need in the situation
    			cX, cY = 0, 0

	cv2.imwrite(path+"Fres.jpg", frame)
        grayF = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	threshFinial = cv2.threshold(grayF, 240, 255, cv2.THRESH_BINARY)[1]
	(averageImageRight, averageImageLeft) = ImageCropping(threshFinial)
	print(averageImageRight, averageImageLeft)
	(sigmoidLeft, sigmoidRight) = findSigmoidOfImageParts(averageImageLeft, averageImageRight)
	print(sigmoidLeft, sigmoidRight)
	return (sigmoidLeft, sigmoidRight)


#begin streaming
#cap = cv2.VideoCapture(0)

count = 1 

while count < 2:
	distanceSensorValue = 4
	#_, frame = cap.read()

	frame =cv2.imread(path+"1.jpg")
	(sigmoidLeft, sigmoidRight) = findContours(frame, path)

	distanceSensorValueSigmoid = findSigmoidofDistanceSensor(distanceSensorValue)

	vilocityLeft = (sigmoidLeft + distanceSensorValueSigmoid)/2
	vilocityRight = (sigmoidRight + distanceSensorValueSigmoid)/2
	
	print(vilocityLeft)
	print(vilocityRight)

	count = count + 1



