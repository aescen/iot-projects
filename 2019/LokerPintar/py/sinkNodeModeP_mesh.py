#!/usr/bin/env python

from __future__ import print_function
import time, sys
from struct import unpack
from struct import Struct
from RF24 import *
from RF24Network import *
from RF24Mesh import *
from array import array

# radio setup
radio = RF24(22,0)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)

mesh.setNodeID(00)
mesh.begin()
radio.setPALevel(RF24_PA_HIGH) # Power Amplifier
radio.setDataRate(RF24_2MBPS)
radio.printDetails()
print('Running ...')

while True:
    try:
        mesh.update()
        mesh.DHCP()

        while network.available():
            try:
                header, payload = network.read(32)
                s = Struct('f f f f f f f f')
                fields = s.unpack(bytes(payload))
                if chr(header.type) == 'P':
                    data0, data1, data2, data3, data4, data5, data6, data7 = fields[:8]
                    data = str(int(data0))+str(int(data1))+str(int(data2))+str(int(data3))+str(int(data4))+str(int(data5))+str(int(data6))+str(int(data7))
                    print('Received payload:', data, ';From node ', header.from_node)
                else:
                    print('Not a P type found...')
            except Exception as e:
                print(e)

    except KeyboardInterrupt:
        radio.powerDown()
        sys.exit()
