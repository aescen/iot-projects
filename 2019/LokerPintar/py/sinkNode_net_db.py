#!/usr/bin/env python

from __future__ import print_function
import time, sys, pymysql
from struct import unpack
from struct import Struct
from RF24 import *
from RF24Network import *
from array import array
from datetime import datetime

# Database setup..
## Create connection to MySQL server
print("Connecting ...")
try:
    connection = pymysql.connect(host='localhost',
                                 user='wsn',
                                 password='QWEASDZXC',
                                 db='wsn',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.Error as msg:
    print("Connection error: ", msg)
    exit()
## Create cursor
cc = connection.cursor()
#----------------------------------------------------------------------------------------->

# NRF setup
octlit = lambda n:int(n, 8)
## radio setup
radio = RF24(22,0)
network = RF24Network(radio)
this_node = octlit("00")
radio.begin()
time.sleep(0.1);
network.begin(90, this_node)
radio.setPALevel(RF24_PA_MAX) # Power Amplifier
radio.setDataRate(RF24_2MBPS)
radio.printDetails()
print('Running ...')
#----------------------------------------------------------------------------------------->

# Main loop
while True:
    try:
        network.update()
        while network.available():
            try:
                header, payload = network.read(48)
                s = Struct('f f f f f f f f f f f f')
                fields = s.unpack(bytes(payload))
                ldr, cIDa, cIDb, cIDc, cIDd, cIDe, cIDf, cIDg, cIDh, cIDi, cIDj, statusCode = fields[:12]
                stempelWaktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                noSeri = str(int(cIDa)) +  str(int(cIDb)) + str(int(cIDc)) + str(int(cIDd)) + str(int(cIDe))
                noSeriBaca = str(int(cIDf)) + str(int(cIDg)) + str(int(cIDh)) + str(int(cIDi)) + str(int(cIDj))
                statusAlat = int(statusCode)
                noNode = int(header.from_node)
                sensorLdr = int(ldr)
                print('|Received payload:')
                print('|_T\t\t:', stempelWaktu)
                print('|_Ldr\t\t:', sensorLdr)
                print('|_ID\t\t:', noSeri)
                print('|_IDRead\t:', noSeriBaca)
                print('|_Status\t:', statusAlat)
                print('|_Node\t\t:', noNode, '\v')
                try:
                    result = """
                             UPDATE `lokerStatus`
                              SET
                               `stempelWaktu`='{0}',
                               `noSeriBaca` = '{1}',
                               `statusAlat`='{2}',
                               `noNode`='{3}',
                               `sensorLdr`='{4}'
                              WHERE
                               `lokerStatus`.`noSeri` = {5};
                             """.format(stempelWaktu, noSeriBaca, statusAlat, noNode, sensorLdr, noSeri)
                    cc.execute(result)
                    connection.commit()
                except pymysql.err.InternalError as msg:
                    print("Command skipped: ", msg)
            except Exception as e:
                print(e)
    except KeyboardInterrupt:
        radio.powerDown()
        connection.close()
        sys.exit()
