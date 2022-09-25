#!/usr/bin/env python

from __future__ import print_function
from struct import *
from RF24 import *
from RF24Network import *
from datetime import datetime
import RPi.GPIO as GPIO
import time, sys
#import pymysql

def irCheck(pin):
    GPIO.setmode (GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pin, GPIO.IN) #IR sensor as input
    if GPIO.input(pin) == False:
        return 1
    elif GPIO.input(pin) == True:
        return 0

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
last_sent = 0
irDetectIn = -1
irDetectOut = -1
jumlahKendaraan = -1
tmpJumlahKendaraan = 0

pinIrIn = 23 #in
pinIrOut = 24 #out

GPIO.setmode (GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pinIrIn,GPIO.IN)
GPIO.setup(pinIrOut,GPIO.IN)

# radio setup
radio = RF24(22, 0, 10000000)
network = RF24Network(radio)
this_node = octlit("01")
server_node = octlit("00")

radio.begin()
radio.setPALevel(RF24_PA_MAX) # Power Amplifier
radio.setDataRate(RF24_1MBPS)
network.begin(97, this_node)
time.sleep(1);
radio.printDetails()
print('Client running ...')


if __name__ == '__main__':
    try:
        while True:
            network.update()
            
            radio.powerDown()
            irDetectIn = irCheck(pinIrIn)
            irDetectOut = irCheck(pinIrOut)
            radio.powerUp()
            
            if irDetectIn is 1:
                tmpJumlahKendaraan = tmpJumlahKendaraan + 1
                irDetectIn = -1
                time.sleep(1)
            elif tmpJumlahKendaraan != 0 and irDetectOut is 1:
                tmpJumlahKendaraan = tmpJumlahKendaraan - 1
                irDetectOut = -1
                time.sleep(1)
            
            if tmpJumlahKendaraan != jumlahKendaraan:
                jumlahKendaraan = tmpJumlahKendaraan
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if jumlahKendaraan == 0:
                    parkirStatus = 'Kosong'
                elif jumlahKendaraan >= 0 and jumlahKendaraan < 35:
                    parkirStatus = 'Tersedia'
                elif jumlahKendaraan >= 35 and jumlahKendaraan < 40:
                    parkirStatus = 'Hampir penuh'
                elif jumlahKendaraan >= 40:
                    parkirStatus = 'Penuh'
                print(ts, '|Node:', this_node, 'total:', jumlahKendaraan, 'status:', parkirStatus)
                
                if jumlahKendaraan <= 40:
                    print('Sending ..', end="")
                    payload = pack('l', jumlahKendaraan)
                    ok = network.write(RF24NetworkHeader(server_node), payload)
                    if ok:
                        print(' Ok.')
                    else:
                        print(' Failed.')
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
    except KeyboardInterrupt:
        radio.powerDown()
        sys.exit()
