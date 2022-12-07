
import smbus
import spidev
import RPi.GPIO as GPIO
import time
import math

DEBUG = 1

class motor_command():
	def __init__(self, motor_L, motor_R):
		
		self.addr = 0x40 # Master address
		Channel_6 = [0x1E, 0x20]
		Channel_7 = [0x22, 0x24]
		self.Motors_I2C = {"Left": Channel_6 , "Right": Channel_7}
		self.Motor_L = motor_L # [15, 13]
		self.Motor_R = motor_R #[18, 16]
		self.Motor_GPIO =  {"Left": self.Motor_L, "Right": self.Motor_R}
		self.MaxMotor = 3685 # Equivalent to 4.5 volts 4095/5
			

	def setup_pin(self):
	
		# GPIO setup for direction
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.Motor_GPIO.get("Left")[0], GPIO.OUT)
		GPIO.setup(self.Motor_GPIO.get("Left")[1], GPIO.OUT)
		GPIO.setup(self.Motor_GPIO.get("Right")[0], GPIO.OUT)
		GPIO.setup(self.Motor_GPIO.get("Right")[1], GPIO.OUT)

		# I2C bus enabled
		bus = smbus.SMBus(1)
		bus.write_byte_data(self.addr, 0, 0x10) # enable Prescale change as noted in the datasheet
		time.sleep(.25) # delay for reset
		bus.write_byte_data(self.addr, 0xfe, 0x88) #changes the Prescale register value for 50 Hz, using 			the equation in the datasheet (I later adjusted the value to fine tune the signal with an 			oscilloscope. The original value was 0x79.)
		time.sleep(.25)
		bus.write_byte_data(self.addr, 0, 0x20) # enable the chip
		time.sleep(.25)

		# SPI interface for sensors A/D readings
		spi0 = spidev.SpiDev()
		spi0.open(0,0)
		spi1 = spidev.SpiDev()
		spi1.open(1,0)

		spi0.max_speed_hz = 100000
		spi1.max_speed_hz = 100000
		spi0.mode = 0b10 # Place data falling edge, reading rising edge
		spi1.mode = 0b10

		return(bus, spi0, spi1)
	
	def power2command(self,bus, motor, power):

		# Sign change the polarity of the motor
		if power > 0 : # Forward mode
			GPIO.output(self.Motor_GPIO.get(motor)[1], GPIO.HIGH)
			GPIO.output(self.Motor_GPIO.get(motor)[0], GPIO.LOW)
		elif power < 0 : # Backwards mode
			GPIO.output(self.Motor_GPIO.get(motor)[0], GPIO.HIGH)
			GPIO.output(self.Motor_GPIO.get(motor)[1], GPIO.LOW)
		# power in % from 0 to 100 mapped in I2C from 0 to 4095 -> period
		value = int(round(max(min(abs(power)*self.MaxMotor/100, self.MaxMotor),0)))
		if DEBUG: 
			print(motor +" " +str(value))
		bus.write_word_data(self.addr, self.Motors_I2C.get(motor)[0], 0)
		bus.write_word_data(self.addr, self.Motors_I2C.get(motor)[1], value)


	def driveMotors(self,bus,powerL,powerR):
		self.power2command(bus, "Left", powerL)
		self.power2command(bus, "Right", powerR)
		#time.sleep(1)
		#self.power2command(bus, "Left", -powerL)
		#self.power2command(bus, "Right", -powerR)
		#time.sleep(1)
		#self.power2command(bus, "Left", 0)
		#self.power2command(bus, "Right", 0)
		#time.sleep(1)

"""

def main():
	motor = motor_command([15, 13],[18, 16])
	powerL = 30.5
	powerR = 30.5
	(bus, spi0, spi1) = motor.setup_pin()
	motor.driveMotors(powerL,powerR)
	bus.close()

if __name__ == "__main__":
	main()
	
"""







