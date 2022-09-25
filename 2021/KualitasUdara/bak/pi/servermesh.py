#!/usr/bin/env python3

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
radio = RF24(22, 0)
network = RF24Network(radio)

radio.begin();
network.begin(2, 0o0);
radio.setRetries(2, 2);
radio.setAutoAck(True);
radio.setPALevel(RF24_PA_MAX);
radio.setDataRate(RF24_1MBPS);
radio.setCRCLength(RF24_CRC_8);
radio.printPrettyDetails()
print('Running ...')
time.sleep(1.0)

if __name__ == '__main__':
    while True:
        try:
            network.update()

            while network.available():
                try:
                    header, payload = network.read(16)
                    print(header.from_node, header.type)
                    s = Struct('f f f f')
                    fields = s.unpack(bytes(payload))
                    if(header.type == ord('1')):
                        ppm1, dust, jumlah, nodeId = fields[:4]
                        ppm1 = float(ppm1)
                        dust = float(dust)
                        jumlah = int(jumlah)
                        nodeId = int(nodeId)
                        print(datetime.now().strftime('%H:%M:%S-%d/%m/%Y'),'Received payload:', 'CO 1 sensor:', ppm1, 'dust sensor:', dust, 'jumlah:', jumlah, 'node ID:', nodeId, 'from node:', header.from_node)
                    elif(header.type == ord('2')):
                        ppm2, ppm3, nodeId, _ = fields[:4]
                        ppm2 = float(ppm2)
                        ppm3 = float(ppm3)
                        nodeId = int(nodeId)
                        print(datetime.now().strftime('%H:%M:%S-%d/%m/%Y'),'Received payload:', 'CO 2 sensor:', ppm2, 'CO 3 sensor:', ppm3, 'node ID:', nodeId, 'from node:', header.from_node)
                    else:
                        print('Unknown type.')
                    
                except Exception as e:
                    print(e)

        except KeyboardInterrupt:
            radio.powerDown()
            sys.exit()
