#!/usr/bin/env python

from __future__ import print_function
import time, sys
from struct import unpack
from struct import Struct
from RF24 import *
from RF24Network import *
from RF24Mesh import *
from array import array
from datetime import datetime

# radio setup
radio = RF24(22,0)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)

mesh.setNodeID(00)
mesh.begin(97, RF24_1MBPS, 15000)
radio.setPALevel(RF24_PA_MAX) # Power Amplifier
radio.printDetails()
print('Running ...')

if __name__ == '__main__':
    time.sleep(1.0)
    while True:
        try:
            mesh.update()
            mesh.DHCP()

            while network.available():
                try:
                    header, payload = network.read(22)
                    s = Struct('f f')
                    fields = s.unpack(bytes(payload))
                    if chr(header.type) == 'M':
                        soil, tinggi, nodeID = fields[:3]
                        soil = float(soil)
                        tinggi = int(tinggi)
                        nodeID = int(nodeID)
                        print(datetime.now().strftime('%H:%M:%S-%d/%m/%Y'),'Received payload:', 'soil sensor:', soil, 'tinggi sensor:', tinggi, 'node ID', nodeID, 'from node:', header.from_node)
                    else:
                        print('Not a M type found...')
                    mesh.update()
                    mesh.DHCP()
                except Exception as e:
                    print(e)

        except KeyboardInterrupt:
            radio.powerDown()
            sys.exit()
