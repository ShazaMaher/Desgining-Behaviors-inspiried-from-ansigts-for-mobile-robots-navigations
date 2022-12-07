import smbus
import spidev
import RPi.GPIO as GPIO
import time
import math


DEBUG = 1

Points = 1000
SleepNose = .1
SleepServo = .05

# I2C mapping addresses
addr = 0x40 # Master address
Channel_6 = [0x1E, 0x20]
Channel_7 = [0x22, 0x24]
Motors_I2C = {"Left": Channel_6 , "Right": Channel_7}
    # Wheel motors
Motor_L = [15, 13]
Motor_R = [18, 16]
Motor_GPIO =  {"Left": Motor_L, "Right": Motor_R}
MaxMotor = 3685 # Equivalent to 4.5 volts 4095/5
    # Servo motors
Channel_0 = [0x06, 0x08]
Channel_1 = [0x0A, 0x0C]
Servo_I2C= {"Left": Channel_0 , "Right": Channel_1}

def setup_pin():

    # GPIO setup for direction
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(Motor_GPIO.get("Left")[0], GPIO.OUT)
    GPIO.setup(Motor_GPIO.get("Left")[1], GPIO.OUT)
    GPIO.setup(Motor_GPIO.get("Right")[0], GPIO.OUT)
    GPIO.setup(Motor_GPIO.get("Right")[1], GPIO.OUT)
    #GPIO.setup(38, GPIO.OUT)
    #GPIO.setup(40, GPIO.IN)

    # I2C bus enabled
    bus = smbus.SMBus(1)
    bus.write_byte_data(addr, 0, 0x10) # enable Prescale change as noted in the datasheet
    time.sleep(.25) # delay for reset
    bus.write_byte_data(addr, 0xfe, 0x88) #changes the Prescale register value for 50 Hz, using the equation in the datasheet (I later adjusted the value to fine tune the signal with an oscilloscope. The original value was 0x79.)
    time.sleep(.25)
    bus.write_byte_data(addr, 0, 0x20) # enable the chip
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


################################################################
# Convert power to a motor command                             #
#   required by the I2C protocol and GPIO Polarization         #
################################################################
def power2command(bus, motor, power):
    # Sign change the polarity of the motor
    if power > 0 : # Forward mode
        GPIO.output(Motor_GPIO.get(motor)[1], GPIO.HIGH)
        GPIO.output(Motor_GPIO.get(motor)[0], GPIO.LOW)
    elif power < 0 : # Backwards mode
        GPIO.output(Motor_GPIO.get(motor)[0], GPIO.HIGH)
        GPIO.output(Motor_GPIO.get(motor)[1], GPIO.LOW)
    # power in % from 0 to 100 mapped in I2C from 0 to 4095 -> period
    value = int(round(max(min(abs(power)*MaxMotor/100, MaxMotor),0)))
    if DEBUG: 
        print(motor +" " +str(value))
    bus.write_word_data(addr, Motors_I2C.get(motor)[0], 0)
    bus.write_word_data(addr, Motors_I2C.get(motor)[1], value)


##################################################################
# Convert angle to a servo command required by the I2C protocol  #
##################################################################
def angle2command(bus, servo, angle):
    # angle from 0 to 120 degrees mapped in I2C between 430 and 190 
    if servo == "Left":
        value = int( min( max( 430 - angle * 2 , 190 ), 430 ) ) 
    elif servo == "Right":
        value = int( min( max( angle * 2 + 190, 190 ), 430 ) ) 
    if DEBUG: 
        print(servo +" " +str(value))
    bus.write_word_data(addr, Servo_I2C.get(servo)[0], 0)
    bus.write_word_data(addr, Servo_I2C.get(servo)[1], value)


# Motor testing
def testMotors(bus):
    power2command(bus, "Left", 30.5)
    power2command(bus, "Right", 30.5)
    time.sleep(1)
    power2command(bus, "Left", -30.5)
    power2command(bus, "Right", -30.5)
    time.sleep(1)
    power2command(bus, "Left", 0)
    power2command(bus, "Right", 0)
    time.sleep(1)


# Servo range testing
def testServos(bus, offset):
    mid = 60 
    amplitude = 60
    period = 2*amplitude
    for i in range(2*period):
        valueL = int(round(mid + amplitude * math.sin(2*math.pi*i/period )))
        angle2command(bus, "Left", valueL)
        valueR = int(round(mid + amplitude * math.sin(2*math.pi*i/period + offset)))
        angle2command(bus, "Right", valueR)
        time.sleep(SleepServo)
    #angle2command(bus, "Left", 0) # between 0 and 120 degrees 
    #angle2command(bus, "Right", 0) # between 0 and 120 degrees 
    return


def testNoses(spiL, spiR):
    for i in range(Points):
        rL = spiL.readbytes(2)
        rR = spiR.readbytes(2)

        respL = 256*rL[0] + rL[1]
        respR = 256*rR[0] + rR[1]
    
        stL = str(i) + "\t" + "L" + "\t" + str(respL) + "\n"
        stR = str(i) + "\t" + "R" + "\t" + str(respR) + "\n"

        print(stL)
        print(stR)
        print("")
        if DEBUG:
            print(rL)
            print(rR)
            print("")
        time.sleep(SleepNose)



# test ultrasonic sensor:
def distance(measure='cm'):
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(38, GPIO.OUT)
        GPIO.setup(40, GPIO.IN)
        
        GPIO.output(38, False)
        while GPIO.input(40) == 0:
            nosig = time.time()
	   # print(0)

        while GPIO.input(40) == 1:
            sig = time.time()
	    #print(1)

        tl = sig - nosig

        if measure == 'cm':
            distance = tl / 0.000058
        elif measure == 'in':
            distance = tl / 0.000148
        else:
            print('improper choice of measurement: in or cm')
            distance = None

        GPIO.cleanup()
        return distance
    except:
        distance = 100
        GPIO.cleanup()
        return distance

def main():
    (bus, spi0, spi1) = setup_pin()
#    print("Test Motors: Have you connected the power cable?")
#   testMotors(bus)
    print(distance('cm'))

    bus.close()



if __name__ == "__main__":
    main()

