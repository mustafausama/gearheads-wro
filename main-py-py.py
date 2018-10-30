import RPi.GPIO as GPIO
import time
import threading

from Modules import control
from Modules import sensors

USsList = [[19, 21], [23, 24]]
Ultrasonic = sensors.Ultrasonic(USsList)

try:
    print("Hello")
    while True:
        print("US 0:-")
        time.sleep(0.5)
        print(Ultrasonic.usData(0))
        time.sleep(1)

        print("US 1:-")
        time.sleep(0.5)
        print(Ultrasonic.usData(1))
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
