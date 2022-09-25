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
mesh.begin(97, RF24_2MBPS, 15000);
radio.setPALevel(RF24_PA_MAX) # Power Amplifier
radio.printDetails()
print('Running ...')

while True:
    try:
        mesh.update()
        mesh.DHCP()

        while network.available():
            try:
                header, payload = network.read(32)
                s = Struct('f f f f f f f')
                fields = s.unpack(bytes(payload))
                if chr(header.type) == 'M':
                    lux, cIDa, cIDb, cIDc, cIDd, cIDe, statusCode = fields[:7]
                    cID = str(int(cIDa)) +  str(int(cIDb)) + str(int(cIDc)) + str(int(cIDd)) + str(int(cIDe))
                    #cIDar = array('i',[int(cIDa), int(cIDb), int(cIDc), int(cIDd), int(cIDe)])
                    #cID = ''.join([str(x) for x in cIDar])
                    statusCode = int(statusCode)
                    print('Received payload:', 'Lux:', lux, ';CardID:', cID, ';Status code:', statusCode, ';From node ', header.from_node)
                else:
                    print('Not a M type found...')
            except Exception as e:
                print(e)

    except KeyboardInterrupt:
        radio.powerDown()
        sys.exit()
