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
                        print(datetime.now().strftime('%H:%M:%S-%d/%m/%Y'),'Received payload:', 'CO 1 sensor:', ppm1, 'dust sensor:', dust, 'jumlah:', jumlah, 'data ID:', nodeId, 'from node:', header.from_node)
                        try:
                            result = """
                                      UPDATE `kualitasudara` SET `ppm1` = '{0}', `dust` = '{1}', `jumlah` = '{2}' WHERE `kualitasudara`.`id` = {3}
                                     """.format(ppm1, dust, jumlah, nodeId)
                            cc.execute(result)
                            connection.commit()                            
                        except pymysql.err.InternalError as msg:
                            print("Command skipped: ", msg)
                    elif(header.type == ord('2')):
                        ppm2, ppm3, _, nodeId = fields[:4]
                        ppm2 = float(ppm2)
                        ppm3 = float(ppm3)
                        nodeId = int(nodeId)
                        try:
                            result = """
                                      UPDATE `kualitasudara` SET `ppm2` = '{0}', `ppm3` = '{1}' WHERE `kualitasudara`.`id` = {2}
                                     """.format(ppm2, ppm3, nodeId)
                            cc.execute(result)
                            connection.commit()                            
                        except pymysql.err.InternalError as msg:
                            print("Command skipped: ", msg)
                        print(datetime.now().strftime('%H:%M:%S-%d/%m/%Y'),'Received payload:', 'CO 2 sensor:', ppm2, 'CO 3 sensor:', ppm3, 'data ID:', nodeId, 'from node:', header.from_node)
                    else:
                        print('Unknown type.')
                    
                except Exception as e:
                    print(e)
        
        except KeyboardInterrupt:
            radio.powerDown()
            connection.close()
            sys.exit()
