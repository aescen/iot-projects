import RPi.GPIO as GPIO
import time
import sys

def pinoff(pin):
    GPIO.setup(pin, GPIO.IN)

def pinon(pin):
    GPIO.setup(pin, GPIO.OUT)

def cleanup():
    GPIO.cleanup()
    sys.exit()


relayPin = 16

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(relayPin, GPIO.OUT, initial=GPIO.LOW)

try:
    for i in range(0, 4):
        pinon(relayPin)
        print("On")
        time.sleep(1)
        pinoff(relayPin)
        print("Off")
        time.sleep(1)
    
    cleanup()
except KeyboardInterrupt:
    cleanup()