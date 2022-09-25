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
                                 password='QWEASDZXC',
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
radio.setDataRate(RF24_1MBPS)
network.begin(90, this_node)
time.sleep(1);
radio.printDetails()
print('Running ...')

while True:
    try:
        network.update()
        while network.available():
            try:
                header, payload = network.read(24)
                s = Struct('f f f f f f')
                noNode = int(header.from_node)
                fields = s.unpack(bytes(payload))
                humid, temp, uvLevel, lux, fan, lamp = fields[:12]
                humid, temp, uvLevel, lux, fan, lamp = round(float(humid), 4), round(float(temp), 4), int(uvLevel), round(float(lux), 4), int(fan), int(lamp)
                humid = 
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                noNode = int(header.from_node)
                uvIntensity = (uvLevel * 0.025);
                uvLambda = 100 + (uvLevel * 25);
                if uvLevel == 0:
                    uvLambda = 0
                print('|Received payload from:',noNode)
                print('|_T\t\t:', ts)
                print('|_Humidity\t:', humid)
                print('|_Temperature\t:', temp)
                print('|_UV Level\t:', uvLevel)
                print('|_UV Intensity\t:', uvIntensity)
                print('|_UV Lambda\t:', uvLambda)
                print('|_Lux\t\t:', lux)
                print('|_Fan\t\t:', fan)
                print('|_Lamp\t\t:', lamp, '\v')
                if noNode == 1:
                    setPath = "1"
                else:
                    setPath = "2"
                try:
                    cc.execute("UPDATE `uv` SET `value` = '%s' WHERE `uv`.`id` = 'fan%s'" % (fan, setPath))
                    cc.execute("UPDATE `uv` SET `value` = '%s' WHERE `uv`.`id` = 'humidity%s'" % (humid, setPath))
                    cc.execute("UPDATE `uv` SET `value` = '%s' WHERE `uv`.`id` = 'lamp%s'" % (lamp, setPath))
                    cc.execute("UPDATE `uv` SET `value` = '%s' WHERE `uv`.`id` = 'temperature%s'" % (temp, setPath))
                    cc.execute("UPDATE `uv` SET `value` = '%s' WHERE `uv`.`id` = 'uvLevel%s'" % (uvLevel, setPath))
                    cc.execute("UPDATE `uv` SET `value` = '%s' WHERE `uv`.`id` = 'uvIntensity%s'" % (uvIntensity, setPath))
                    cc.execute("UPDATE `uv` SET `value` = '%s' WHERE `uv`.`id` = 'uvLambda%s'" % (uvLambda, setPath))
                    cc.execute("UPDATE `uv` SET `value` = '%s' WHERE `uv`.`id` = 'lux%s'" % (lux, setPath))
                    connection.commit()
                except pymysql.err.InternalError as msg:
                    print("Command skipped: ", msg)
            except Exception as e:
                print(e)

    except KeyboardInterrupt:
        radio.powerDown()
        connection.close()
        sys.exit()