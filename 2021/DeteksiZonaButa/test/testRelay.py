#!/usr/bin/python3

import time
import RPi.GPIO as IO


RELAY_PIN = 21
IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(RELAY_PIN, IO.OUT, initial=IO.LOW)


def pinoff(pin):
    IO.setup(pin, IO.IN)

def pinon(pin):
    IO.setup(pin, IO.OUT)

print('print on')
pinon(RELAY_PIN)
time.sleep(1)
print('print off')
pinoff(RELAY_PIN)
time.sleep(1)
print('print on')
pinon(RELAY_PIN)
time.sleep(1)
print('print off')
pinoff(RELAY_PIN)
print('end')
exit()