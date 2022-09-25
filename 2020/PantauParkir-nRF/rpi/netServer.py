#!/usr/bin/env python

from __future__ import print_function
from struct import *
from RF24 import *
from RF24Network import *
from array import array
from datetime import datetime
import time, sys, time
#import pymysql

# Database setup..
## Create connection to MySQL server
"""
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
"""
#----------------------------------------------------------------------------------------->


octlit = lambda val:int(val, 8)
millis = lambda: int(round(time.time() * 1000)) & 0xffffffff
interval = 2000
last_sent = 0
jumlahKendaraan = 0
pirDetect = -1
tmp = 0

# radio setup
radio = RF24(22, 0, 10000000)
network = RF24Network(radio)
this_node = octlit("00")
client_node = octlit("01")

radio.begin()
radio.setPALevel(RF24_PA_MAX) # Power Amplifier
radio.setDataRate(RF24_1MBPS)
network.begin(97, this_node)
time.sleep(1);
radio.printDetails()
print('Server running ...')

if __name__ == '__main__':
    try:
        while True:
            network.update()
            if network.available():
                try:
                    header, payload = network.read(4)
                    #print("Payload length ", len(payload))
                    jumlahKendaraan = unpack('l', bytes(payload))
                    jumlahKendaraan = jumlahKendaraan[0]
                    noNode = header.from_node
                    #print(jumlahKendaraan, noNode)
                    if jumlahKendaraan == 0:
                        parkirStatus = 'Kosong'
                    elif jumlahKendaraan >= 0 and jumlahKendaraan < 35:
                        parkirStatus = 'Tersedia'
                    elif jumlahKendaraan >= 35 and jumlahKendaraan < 40:
                        parkirStatus = 'Hampir penuh'
                    elif jumlahKendaraan >= 40:
                        parkirStatus = 'Penuh'
                    
                    if jumlahKendaraan <= 40:
                        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(ts, '|Received payload from:', noNode, 'total:', jumlahKendaraan, 'status:', parkirStatus)
                    else:
                        print('Jumlah kendaraan melebihi kapasitas(40):', jumlahKendaraan)
                    '''
                    try:
                        result = """
                                  UPDATE `parkirpolinema`
                                   SET
                                    `timeStamp`='{0}',
                                    `nodeID` = '{1}',
                                    `jumlahKendaraan`='{2}',
                                    `parkirStatus`='{3}',
                                   WHERE
                                    `mhSensor`.`nodeID` = {1};
                                 """.format(timeStamp, nodeID, jumlahKendaraan, parkirStatus)
                        cc.execute(result)
                        connection.commit()
                    except pymysql.err.InternalError as msg:
                        print("Command skipped: ", msg)
                    '''
                except Exception as e:
                    print(e)
    except KeyboardInterrupt:
        radio.powerDown()
        sys.exit()