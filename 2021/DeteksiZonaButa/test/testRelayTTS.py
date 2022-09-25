#!/usr/bin/python3

import pyttsx3
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

print('print off')
pinoff(RELAY_PIN)

engine = pyttsx3.init()
engine.setProperty('rate', 125)
engine.setProperty('voice', 'indonesian')
engine.setProperty('volume', 1.0)

engine.say("Jumlah terdeteksi, 1 orang.")
engine.runAndWait()

print('print on')
pinon(RELAY_PIN)
time.sleep(15)
print('print off')
pinoff(RELAY_PIN)
print('end')
exit()
