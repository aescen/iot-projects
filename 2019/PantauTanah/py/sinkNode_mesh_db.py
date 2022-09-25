#!/usr/bin/env python

from __future__ import print_function
import time, sys, pymysql
from struct import unpack
from struct import Struct
from RF24 import *
from RF24Network import *
from RF24Mesh import *
from array import array
from datetime import datetime

# Database setup..
## Create connection to MySQL server
print("Connecting ...")
try:
    connection = pymysql.connect(host='localhost',
                                 user='pi',
                                 password='raspberry',
                                 db='pi',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.Error as msg:
    print("Connection error: ", msg)
    exit()
## Create cursor
cc = connection.cursor()
#----------------------------------------------------------------------------------------->


# radio setup
radio = RF24(22,0)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)

mesh.setNodeID(00)
mesh.begin(97, RF24_1MBPS, 15000)
radio.setPALevel(RF24_PA_MAX) # Power Amplifier
radio.printDetails()
print('Running ...')

while True:
    try:
        mesh.update()
        mesh.DHCP()

        while network.available():
            try:
                header, payload = network.read(18)
                s = Struct('f f')
                fields = s.unpack(bytes(payload))
                if chr(header.type) == 'M':
                    soilRead, nodeID = fields[:2]
                    soilRead = int(soilRead)
                    nodeID = int(nodeID)
                    meshNodeID = header.from_node
                    timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #xxxx-xx-xx xx:xx:xx
                    if soilRead == 0:
                        soilStatus = 'Sensor hubung singkat!'
                    elif soilRead >= 0 and soilRead < 370:
                        soilStatus = 'Sensor di dalam air!'
                    elif soilRead >= 370 and soilRead < 600:
                        soilStatus = 'Tanah lembab!'
                    elif soilRead >= 600 and soilRead < 1000:
                        soilStatus = 'Tanah kering!'
                    elif soilRead >= 1000 and soilRead < 1024:
                        soilStatus = 'Sensor terputus/di udara!'
                    try:
                        result = """
                                  UPDATE `mhSensor`
                                   SET
                                    `timeStamp`='{0}',
                                    `nodeID` = '{1}',
                                    `meshNodeID`='{2}',
                                    `soilRead`='{3}',
                                    `soilStatus`='{4}'
                                   WHERE
                                    `mhSensor`.`nodeID` = {1};
                                 """.format(timeStamp, nodeID, meshNodeID, soilRead, soilStatus)
                        cc.execute(result)
                        connection.commit()
                    except pymysql.err.InternalError as msg:
                        print("Command skipped: ", msg)
                    print(timeStamp,'Received payload:', 'moist sensor:', soilRead, 'node ID', nodeID, 'from node:', meshNodeID)
                else:
                    print('Not a M type found...')
            except Exception as e:
                print(e)

    except KeyboardInterrupt:
        radio.powerDown()
        connection.close()
        sys.exit()
