#!/usr/bin/python3

import time
import Jetson.GPIO as GPIO

# Define the pin for controlling the fan
FAN_PIN = 15
# Define the pin for reading the fan speed
FAN_SPEED_PIN = 13

# Set up GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(FAN_SPEED_PIN, GPIO.IN)

def fan_on():
    GPIO.output(FAN_PIN, GPIO.HIGH)  # Turn the fan on
    print("Fan turned on")

def fan_off():
    GPIO.output(FAN_PIN, GPIO.LOW)   # Turn the fan off
    print("Fan turned off")

def read_fan_speed():
    fan_speed = GPIO.input(FAN_SPEED_PIN)
    return fan_speed

try:
    while True:
        fan_on()   # Turn the fan on
        time.sleep(5)  # Run the fan for 5 seconds
        fan_off()  # Turn the fan off
        time.sleep(5)  # Wait for 5 seconds before turning on again
        speed = read_fan_speed()
        print("Fan speed:", speed)

except KeyboardInterrupt:
    print("\nExiting program")
    GPIO.cleanup()  # Clean up GPIO on program exit
