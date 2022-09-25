#!/usr/bin/env python3

from __future__ import print_function
from struct import *
from RF24 import *
from RF24Network import *
from RF24Mesh import *
from array import array
from datetime import datetime
import time, sys, re
import pymysql

def printd(d = 3):
    cnt = 0
    while cnt < d:
        print(" . ", end='', flush=True)
        time.sleep(1);
        cnt += 1
    print('')


octlit = lambda val:int(val, 8)
millis = lambda: int(round(time.time() * 1000)) & 0xffffffff

BUFFER_SIZE = 8

# radio setup
radio = RF24(22, 0, 8000000)
#radio = RF24(22, 0)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)
mesh.setNodeID(0)
mesh.begin(111, RF24_1MBPS, 10000)
radio.setRetries(2, 8)
radio.setPALevel(RF24_PA_LOW)
time.sleep(.5)
radio.printPrettyDetails()
print('Start server node:', mesh.getNodeID());
printd()
print('Server running ...')

if __name__ == '__main__':
    mainInterval = 5000
    mainTimer = millis()
    try:
        while True:
            mesh.update()
            mesh.DHCP()
            
            if network.available():
                header, payload = network.read(BUFFER_SIZE)
                try:
                    if chr(header.type) == 'O':
                        a, b, c, d = unpack('ffff', bytes(payload))
                        meshId = header.from_node
                        print(f"Received: {a:.2f} - {b:.2f} - {c:.2f} - {d:.2f} -- {meshId}")
                    elif chr(header.type) == 'I':
                        a, b, = unpack('ff', bytes(payload))
                        meshId = header.from_node
                        print(f"Received: {a:.2f} - {b:.2f} -- {meshId}")
                    else:
                        print('Rcv bad type {} from 0{:o}'.format(chr(header.type), header.from_node));
                except Exception as e:
                    print('Error', e, ', payload length', len(payload))
                    try:
                        BUFFER_SIZE = int(re.findall(r'\b\d+\b', str(e))[0]) #regexp
                        print('Will try with BUFFER_SIZE:', BUFFER_SIZE, ' instead...')
                    except Exception as t:
                        print('Error:', t, '- cannot change buffer size.')
            
            if millis() - mainTimer > mainInterval:
                payload = pack( "ffff", 1.0, 2.0, 3.3, 4.4 )
                if not mesh.write( payload, ord('S'), octlit('01') ):
                    print("Send to node 1 fail!")
                else:
                    print( "Send ok:", '01', "->", { 1.0, 2.0, 3.3, 4.4 } )
                mainTimer = millis()
    except KeyboardInterrupt:
        radio.powerDown()
        sys.exit()
