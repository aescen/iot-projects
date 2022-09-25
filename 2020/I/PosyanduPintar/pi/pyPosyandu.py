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

octlit = lambda val:int(val, 8)

# radio setup
radio = RF24(22,0)
network = RF24Network(radio)
this_node = octlit("00")

radio.begin()
radio.setPALevel(RF24_PA_MAX) # Power Amplifier
radio.setDataRate(RF24_2MBPS)
network.begin(90, this_node)
time.sleep(1);
radio.printDetails()
print('Running ...')

while True:
    try:
        network.update()
        while network.available():
            try:
                header, payload = network.read(28)
                noNode = int(header.from_node)
                s = Struct('f f f f f f f')
                fields = s.unpack(bytes(payload))
                if noNode == 1:
                    cID1, cID2, cID3, cID4, cID5, TB, BB = fields[:14]
                    noSeri = str(int(cID1)) + " " + str(int(cID2)) + " " + str(int(cID3)) + " " + str(int(cID4)) + " " + str(int(cID5))
                    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print('|Received payload from:',noNode)
                    print('|_T\t\t:', ts)
                    print('|_ID\t\t:', noSeri)
                    print('|_Tinggi Badan\t:', TB)
                    print('|_Berat Badan\t:', BB, '\v')
                    try:
                        cc.execute("UPDATE `posyandu` SET `tb` = '%s', `bb` = '%s' WHERE `posyandu`.`id` = '%s'" % (TB, BB, noSeri))
                        connection.commit()
                    except pymysql.err.InternalError as msg:
                        print("Command skipped: ", msg)

                else:
                    cID1, cID2, cID3, cID4, cID5, TD, SB = fields[:14]
                    noSeri = str(int(cID1)) + " " + str(int(cID2)) + " " + str(int(cID3)) + " " + str(int(cID4)) + " " + str(int(cID5))
                    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print('|Received payload from:',noNode)
                    print('|_T\t\t:', ts)
                    print('|_ID\t\t:', noSeri)
                    print('|_Tensi darah\t:', TD)
                    print('|_Suhu badan\t:', SB, '\v')
                    try:
                        cc.execute("UPDATE `posyandu` SET `td` = '%s', `sb` = '%s' WHERE `posyandu`.`id` = '%s'" % (TD, SB, noSeri))
                        connection.commit()
                    except pymysql.err.InternalError as msg:
                        print("Command skipped: ", msg)
            except Exception as e:
                print(e)

    except KeyboardInterrupt:
        radio.powerDown()
        connection.close()
        sys.exit()