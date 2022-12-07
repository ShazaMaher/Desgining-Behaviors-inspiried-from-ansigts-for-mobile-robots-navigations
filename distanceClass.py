
import time
import RPi.GPIO as GPIO

class distance():
	def __init__(self,GPIO_TRIGGER,GPIO_ECHO):
		print("this is init")
		GPIO.setwarnings(False)

		# Use BCM GPIO references
		# instead of physical pin numbers
		GPIO.setmode(GPIO.BOARD)
		
		# Define GPIO to use on Pi
		self.GPIO_TRIGGER = GPIO_TRIGGER
		self.GPIO_ECHO    = GPIO_ECHO

	def setupGPIO(self):
		
		print('Ultrasonic Measurement')
		
		# Set pins as output and input
		GPIO.setup(self.GPIO_TRIGGER,GPIO.OUT)  # Trigger
		GPIO.setup(self.GPIO_ECHO,GPIO.IN)      # Echo

		# Set trigger to False (Low)
		GPIO.output(self.GPIO_TRIGGER, False)


	def measure_distance(self):
		# This function measures a distance
		GPIO.output(self.GPIO_TRIGGER, True)
		time.sleep(0.00001)
		GPIO.output(self.GPIO_TRIGGER, False)
		start = time.time()
		stop = time.time()

		while GPIO.input(self.GPIO_ECHO)==0:
			#print(0)
			start = time.time()

		while GPIO.input(self.GPIO_ECHO)==1:
			#print(1)
			stop = time.time()
                

		elapsed = stop - start
		distance = (elapsed * 34300)/2

		return distance


	def measure_average(self):

		# This function takes 3 measurements and
		# returns the average.
		distance1=self.measure_distance()
		time.sleep(0.1)
		distance2=self.measure_distance()
		time.sleep(0.1)
		distance3=self.measure_distance()
		distance = distance1 + distance2 + distance3
		distance_avg = distance / 3

		return distance_avg

"""	
def main():
	dist = distance(31,33)
	dist.setupGPIO()
	dist1 = distance(38,40)
	dist1.setupGPIO()
	print("main")
	try:
	
		while True:

			dis = dist.measure_distance()
			print("dis")
			print (dis)
			time.sleep(1)
			
			dis1 = dist1.measure_distance()
			print("dis1")
			print (dis1)
			time.sleep(1)

	except KeyboardInterrupt:
		# User pressed CTRL-C
		# Reset GPIO settings
		GPIO.cleanup()

if __name__ == "__main__":
	main()
"""

