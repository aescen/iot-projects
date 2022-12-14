#!/usr/bin/env python3

from RF24 import *
from RF24Network import *
from RF24Mesh import *

from struct import unpack

radio = RF24(22,0);
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)

mesh.setNodeID(0)
mesh.begin()
radio.setPALevel(RF24_PA_LOW) # Power Amplifier
radio.printDetails()

try:
    while True:
        mesh.update()
        mesh.DHCP()

        while network.available():
            header, payload = network.read(10)
            if chr(header.type) == 'M':
                print("Rcv {} from 0{:o}".format(unpack("L", int(payload)[0]), header.from_node))
            else:
                print("Rcv bad type {} from 0{:o}".format(header.type,header.from_node))
except KeyboardInterrupt:
    exit()