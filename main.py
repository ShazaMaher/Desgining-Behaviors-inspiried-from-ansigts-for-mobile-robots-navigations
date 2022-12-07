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

#cap = cv2.VideoCapture(0, cv2.CAP_V4L)

K = 1



def sigmoid(x):
	y = 4 /(1 + (K * np.exp(- x)))
	return y

def main():
	allowGoing = True
	motor = motor_command([15, 13],[18, 16])
	dist = distance(38,40)
	(bus, spi0, spi1) = motor.setup_pin()
	
	dist.setupGPIO()
	dis = dist.measure_average()
	try:
		camera = PiCamera()
		camera.resolution = (1280, 720)
		camera.framerate = 60
		rawCapture = PiRGBArray(camera, size=(1280, 720))
		# allow the camera to warmup
		time.sleep(0.1)


		dis = dist.measure_average()
		print(dis)
	
		while allowGoing == True:	

			if dis < 10:
				print(dis)
				motor.driveMotors(bus,0,0)
				allowGoing = False
				#camera.stop_recording()
			else:
				print(dis)
				for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	    				# grab the raw NumPy array representing the image, then initialize the timestamp
	  				# and occupied/unoccupied text
					frame.seek(0)
	    				image = frame.array
					cv2.imwrite(path+"frame.jpg", image)
					ImageProc = ImageProcessing(image, path)

			        	(averageImageRight, averageImageLeft )= ImageProc.findContours(image)
					speedIR = sigmoid(averageImageLeft)
					speedIL = sigmoid(averageImageRight)
					speedDis = sigmoid(dis)
					powerL =  speedIL + speedDis
					powerR = speedIR + speedDis

					motor.driveMotors(bus,powerL*20,powerR*20)
					dis = dist.measure_average()
					print(dis)
					if dis <= 20:
						print(dis)
						motor.driveMotors(bus,0,0)
						allowGoing = False
						camera.stop_recording()
						break;
			

	except KeyboardInterrupt:
		GPIO.cleanup()
		camera.stop_recording()


if __name__ == "__main__":
	main()
