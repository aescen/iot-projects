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

# range converter
def remap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

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
mesh.begin(97, RF24_1MBPS, 10000)
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
                    header, payload = network.read(12)
                    s = Struct('f f f')
                    fields = s.unpack(bytes(payload))
                    if chr(header.type) == 'M':
                        soilRead, tinggi, nodeId = fields[:3]
                        soilRead = float(soilRead)
                        tinggi = int(tinggi)
                        nodeId = int(nodeId)
                        meshNodeId = header.from_node
                        timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #xxxx-xx-xx xx:xx:xx
                        if soilRead is 0:
                            soilStatus = 'Sensor hubung singkat!'
                        elif soilRead >= 0 and soilRead < 370:
                            soilStatus = 'Sensor di dalam air!'
                            soilRead = remap(soilRead, 0, 1023, 100, 0)
                        elif soilRead >= 370 and soilRead < 600:
                            soilStatus = 'Tanah lembab!'
                            soilRead = remap(soilRead, 0, 1023, 100, 0)
                        elif soilRead >= 600 and soilRead < 1000:
                            soilStatus = 'Tanah kering!'
                            soilRead = remap(soilRead, 0, 1023, 100, 0)
                        elif soilRead >= 1000 and soilRead < 1024:
                            soilStatus = 'Sensor terputus/di udara!'
                            soilRead = remap(soilRead, 0, 1023, 100, 0)
                        try:
                            result = """
                                      UPDATE `pantauJati`
                                       SET
                                        `soilMoist`='{1}',
                                        `soilStatus`='{2}',
                                        `ketinggian`='{3}',
                                        `timeStamp`='{4}'
                                       WHERE
                                        `pantauJati`.`nodeId` = {0};
                                     """.format(nodeId, soilRead, soilStatus, tinggi, timeStamp)
                            cc.execute(result)
                            connection.commit()                            
                        except pymysql.err.InternalError as msg:
                            print("Command skipped: ", msg)
                        print(datetime.now().strftime('%H:%M:%S-%d/%m/%Y'), 'Received payload: soil sensor:', soilRead, 'tinggi sensor:', tinggi, 'node Id', nodeId, 'from node:', meshNodeId)
                    else:
                        print('Not a M type found...')
                except Exception as e:
                    print(e)
        
        except KeyboardInterrupt:
            radio.powerDown()
            connection.close()
            sys.exit()
