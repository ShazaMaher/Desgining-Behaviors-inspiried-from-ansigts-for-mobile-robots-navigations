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

#initialization
path = "/home/pi/master_project/master_project/img/"


rate_learning = 0.01

def sigmoid(x, K):
	y = 1 /(1 + np.exp(- K * x))
	return y


def main():
	dist_old_L = 0
	dist_new_L = 0
	dist_old_R = 0
	dist_new_R = 0

	w_L = 0
	w_R = 0
	cR = 0
	cL = 0
	k_L = 0
	k_R = 0

	allowGoing = True
	cameraAvg = 0

	motor = motor_command([15, 13],[18, 16])
        (bus, spi0, spi1) = motor.setup_pin()

	distL = distance(38,40)
        distR = distance(31,33)
	distL.setupGPIO()
	distR.setupGPIO()

	try:
		camera = PiCamera()
		camera.resolution = (1280, 720)
		camera.framerate = 60
		rawCapture = PiRGBArray(camera, size=(1280, 720))
		
		dist_old_L = dist_new_L  
		dist_new_L = distL.measure_distance()

		dist_old_R = dist_new_R 
		dist_new_R = distR.measure_distance()
	
		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			# grab the raw NumPy array representing the image, then initialize the timestamp
			# and occupied/unoccupied text
			frame.seek(0)
			image = frame.array
			cv2.imwrite(path+"frame.jpg", image)
			ImageProc = ImageProcessing(image, path)
			(cR, cL)= ImageProc.findContours(image)
                        cameraAvg = cR + cL
			print("cameraAvg")
                        print(cameraAvg)

			#while cameraAvg < 30 and cameraAvg > 0:
			"""frame.seek(0)
			image = frame.array
			cv2.imwrite(path+"frame.jpg", image)	
			ImageProc = ImageProcessing(image, path)
			(cR, cL)= ImageProc.findContours(image)
                	cameraAvg = cR + cL
			print("cameraAvg")
                	print(cameraAvg)"""

			# calculate kL, kR and yL and yR
			delta_k_L = rate_learning * cL * (dist_new_L - dist_old_L)
			delta_k_R = rate_learning * cR * (dist_new_R - dist_old_R)
			
			k_L = k_L + delta_k_L

			k_R = k_R + delta_k_R

			"""w_L = w_L + delta_w_L
			w_R = w_R + delta_w_R

			k_L = w_L * cL + dist_new
			k_R = w_R * cR + dist_new"""


			# calculate the vilocity of the wheels
			V_C_L = sigmoid(cR, k_L)

			v_C_R = sigmoid(cL, k_R)
			
			# path smoothing
			y_L = rate_learning * dist_new_L * (dist_new_L - dist_old_L)
			y_R = rate_learning * dist_new_R * (dist_new_R - dist_old_R)
			
			

			# calculate VD for path smoothing
			V_D_R = sigmoid(dist_new_R, y_R)

			V_D_L = sigmoid(dist_new_L, y_L)
			
			# calculate obstracle avoidance:
			V_L = sigmoid(dist_new_L, 1)
			V_R = sigmoid(dist_new_R, 1)
			

			difference = abs(dist_new_L - dist_new_R) 


			if dist_new_L < 40:
			# calculate the finial vilocity
				V_Left = V_C_L +  V_R + V_D_R
			else:
				V_Left = V_C_L +  V_R  


			if dist_new_R < 40: 
				V_Right = v_C_R + V_L +  V_D_L
			else:
				V_Right = v_C_R + V_L 

			if difference < 20 and dist_new_R > dist_new_L:
				V_Right = v_C_R + V_R +  V_D_R
				V_Left = V_C_L +  V_L + V_D_L

                        elif difference < 20 and dist_new_R < dist_new_L:
				V_Right = v_C_R + V_R +  V_D_R
				V_Left = V_C_L +  V_L + V_D_L
				


			motor.driveMotors(bus,V_Left*20,V_Right*20)

			dist_old_L = dist_new_L  
			dist_new_L = distL.measure_distance()

			dist_old_R = dist_new_R 
			dist_new_R = distR.measure_distance()
			print(dist_old_L)
			print(dist_new_L)
			print(dist_old_R)
			print(dist_new_R)

			k_Left = k_L
			k_Right = k_R
			print("k_Left",k_Left)
			print("k_Right",k_Right)
			print("cR",cR)
			print("cL",cL)

			if cameraAvg > 30:
				dist_old_L = 0
				dist_old_R = 0

				print(dist_old_L)
				print(dist_new_L)
				print(dist_old_R)
				print(dist_new_R)

				motor.driveMotors(bus,0,0)
				camera.stop_recording()

			

	except KeyboardInterrupt:
		GPIO.cleanup()
		camera.stop_recording()


if __name__ == "__main__":
	main()

		

		
		
		

	

		
		

	

