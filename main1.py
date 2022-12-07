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

cap = cv2.VideoCapture()

K = 1

def sigmoid(x):
	y = 1 /(1 + np.exp(- K * x))
	return y

def main():
	motor = motor_command([15, 13],[18, 16])
	dist = distance(38,40)
        dist1 = distance(31,33)
	(bus, spi0, spi1) = motor.setup_pin()
	
	dist.setupGPIO()
	try:
	
		while True:

			dis = dist.measure_average()
			print(dis)
			_, frame = cap.read()
			cv2.imwrite(path+"frame.jpg", frame)
			ImageProc = ImageProcessing(frame, path)

                	(averageImageRight, averageImageLeft )= ImageProc.findContours(frame)
			speedIR = sigmoid(averageImageLeft)
			speedIL = sigmoid(averageImageRight)
			speedDis = sigmoid(dis)
			powerL =  speedIL + speedDis
			powerR = speedIR + speedDis
		
			while dis > 20:
				motor.driveMotors(powerL,powerR)
			if dis <= 20:
				motor.driveMotors(0,0)

	except KeyboardInterrupt:
		GPIO.cleanup()


if __name__ == "__main__":
	main()
