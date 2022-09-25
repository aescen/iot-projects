#!/usr/bin/env python

from __future__ import print_function
import time, sys
from struct import *
from RF24 import *
from RF24Network import *
from array import array
from datetime import datetime

octlit = lambda n:int(n, 8)

# radio setup
radio = RF24(22,0)
network = RF24Network(radio)
this_node = octlit("00")

radio.begin()
time.sleep(1);
network.begin(90, this_node)
radio.setPALevel(RF24_PA_MAX) # Power Amplifier
radio.setDataRate(RF24_1MBPS)
radio.printDetails()
print('Running ...')

while True:
    try:
        network.update()
        while network.available():
            try:
                header, payload = network.read(24)
                s = Struct('f f f f f f')
                noNode = int(header.from_node)
                fields = s.unpack(bytes(payload))
                humid, temp, uvLevel, lux, fan, lamp = fields[:12]
                humid, temp, uvLevel, lux, fan, lamp = float(humid), float(temp), int(uvLevel), float(lux), int(fan), int(lamp)
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                noNode = int(header.from_node)
                uvIntensity = (uvLevel * 0.025);
                uvLambda = 100 + (uvLevel * 25);
                if uvLevel == 0:
                    uvLambda = 0
                print('|Received payload from:',noNode)
                print('|_T\t\t:', ts)
                print('|_Humidity\t:', humid)
                print('|_Temperature\t:', temp)
                print('|_UV Level\t:', uvLevel)
                print('|_UV Intensity\t:', uvIntensity)
                print('|_UV Lambda\t:', uvLambda)
                print('|_Lux\t\t:', lux)
                print('|_Fan\t\t:', fan)
                print('|_Lamp\t\t:', lamp, '\v')
            except Exception as e:
                print(e)

    except KeyboardInterrupt:
        radio.powerDown()
        sys.exit()
