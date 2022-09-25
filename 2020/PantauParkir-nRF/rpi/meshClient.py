#!/usr/bin/env python

from __future__ import print_function
from struct import *
from RF24 import *
from RF24Network import *
from RF24Mesh import *
from datetime import datetime
import RPi.GPIO as GPIO
import time, sys
import pymysql

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

print('Connecting ...')
try:
    connection = pymysql.connect(host='localhost',
                                 user='pi',
                                 password='raspberry',
                                 db='pi',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.Error as msg:
    print('Connection error: ', msg)
    exit()
## Create cursor
cc = connection.cursor()

#----------------------------------------------------------------------------------------->

octlit = lambda val:int(val, 8)
last_sent = 0
irDetectIn = -1
irDetectOut = -1
MAX_CAP = 40
jumlahKendaraan = 0
tmpJumlahKendaraan = 0

pinIrIn = 23 #in
pinIrOut = 24 #out

GPIO.setmode (GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pinIrIn,GPIO.IN)
GPIO.setup(pinIrOut,GPIO.IN)

# radio setup
nodeId = 1
renewId = 0
RENEW_COUNT = 2
retry = 0
RETRY_COUNT = 2

radio = RF24(22, 0, 8000000)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)

mesh.setNodeID(octlit('01'))
mesh.begin(97, RF24_1MBPS, 15000)
radio.setPALevel(RF24_PA_MAX)
radio.printDetails()
print('Start client node:', nodeId);
time.sleep(1)
meshConn = mesh.checkConnection()
if not meshConn:
    print(' |renewing address...')
    mesh.renewAddress()
    meshConn = mesh.checkConnection()
    if not meshConn:
        print('Master node(server) not running or DHCP fail! Exiting...')
        sys.exit()
'''
while renewId < RENEW_COUNT and not meshConn:
    meshConn = mesh.checkConnection()
    if not meshConn and renewId < RENEW_COUNT:
        print(' |renewing address...')
        mesh.renewAddress()
        renewId += 1
        time.sleep(1)
    elif not meshConn and renewId == RENEW_COUNT:
        print('Master node(server) not running or DHCP fail! Exiting...')
        sys.exit()
'''

print('Connected with meshId:', mesh.getNodeID())
renewId = 0
cnt = 0
while cnt < 5:
    print(" . ", end='', flush=True)
    time.sleep(1);
    cnt += 1
print('')
print('Client running ...')


if __name__ == '__main__':
    try:
        while True:
            mesh.update()
            
            if renewId == 0 and retry == 0:
                radio.powerDown()
                irDetectIn = irCheck(pinIrIn)
                irDetectOut = irCheck(pinIrOut)
                radio.powerUp()
            
            if tmpJumlahKendaraan == jumlahKendaraan and irDetectIn is 1:
                #print('kendaraan +1')
                tmpJumlahKendaraan = tmpJumlahKendaraan + 1
                irDetectIn = -1
                time.sleep(1)
            elif tmpJumlahKendaraan == jumlahKendaraan and tmpJumlahKendaraan != 0 and irDetectOut is 1:
                #print('kendaraan -1')
                tmpJumlahKendaraan = tmpJumlahKendaraan - 1
                irDetectOut = -1
                time.sleep(1)
            
            if tmpJumlahKendaraan != jumlahKendaraan:
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if tmpJumlahKendaraan == 0:
                    parkirStatus = 'Kosong'
                elif tmpJumlahKendaraan >= 0 and tmpJumlahKendaraan < 35:
                    parkirStatus = 'Tersedia'
                elif tmpJumlahKendaraan >= 35 and tmpJumlahKendaraan < 40:
                    parkirStatus = 'Hampir penuh'
                elif tmpJumlahKendaraan >= 40:
                    parkirStatus = 'Penuh'
                else:
                    parkirStatus = 'null'
                
                sisaSlot = MAX_CAP - tmpJumlahKendaraan
                
                if tmpJumlahKendaraan <= 40:
                    print(ts, '|NodeId:', nodeId, 'meshId:', mesh.getNodeID(), 'total:', tmpJumlahKendaraan, 'sisa:', sisaSlot, 'status:', parkirStatus, end='')
                    
                    if mesh.getNodeID() == 0:
                        meshConn = mesh.checkConnection()
                        mesh.renewAddress()
                        while renewId < RENEW_COUNT and not meshConn:
                            meshConn = mesh.checkConnection()
                            if not meshConn and renewId < RENEW_COUNT and mesh.getNodeID() == 0:
                                print(' |Renewing address...')
                                mesh.renewAddress()
                                renewId += 1
                                time.sleep(1)
                            elif not meshConn and renewId == RENEW_COUNT and mesh.getNodeID() == 0:
                                print(' |Master node(server) not running or DHCP fail! Exiting...')
                                sys.exit()
                            elif mesh.getNodeID() != 0:
                                print(' |Connected with new meshId:', mesh.getNodeID())
                                renewId = 0
                                break
                    
                    print(' |Sending ...', end='')
                    payload = pack('LL', nodeId, tmpJumlahKendaraan)
                    ok = mesh.write(payload, ord('M'))
                    if ok:
                        print(' Ok.')
                        jumlahKendaraan = tmpJumlahKendaraan
                    else:
                        meshConn = mesh.checkConnection()
                        if not meshConn and renewId <= RENEW_COUNT:
                            print(' renewing address')
                            mesh.renewAddress()
                            renewId += 1
                            time.sleep(1)
                        elif not meshConn and renewId == RENEW_COUNT:
                            print(' master node(server) not running or DHCP fail! Skipping update...')
                            jumlahKendaraan = tmpJumlahKendaraan
                            renewId = 0
                        elif retry == RETRY_COUNT:
                            print(' failed multiple time, test Ok. Skipping update...')
                            jumlahKendaraan = tmpJumlahKendaraan
                            retry = 0
                        else:
                            retry += 1
                            print(' failed, test Ok, retrying...')
                            time.sleep(1)
                elif tmpJumlahKendaraan > 40:
                    print('Jumlah kendaraan melebihi kapasitas({}):'.format(MAX_CAP), tmpJumlahKendaraan)
                    jumlahKendaraan = tmpJumlahKendaraan
                
                if renewId == 0 and retry == 0:
                    #print('Updating database... ', jumlahKendaraan, tmpJumlahKendaraan)
                    try:
                        result = '''
                                  UPDATE `parkirpolinema_node`
                                   SET
                                    `meshNodeId` = '{1}',
                                    `jumlahKendaraan`='{2}',
                                    `parkirStatus`='{3}',
                                    `timeStamp`='{4}'
                                   WHERE
                                    `parkirpolinema_node`.`nodeId` = {0};
                                 '''.format(nodeId, mesh.getNodeID(), jumlahKendaraan, parkirStatus, ts)
                        cc.execute(result)
                        connection.commit()
                    except pymysql.err.InternalError as msg:
                        print('Command skipped: ', msg)
    except KeyboardInterrupt:
        radio.powerDown()
        sys.exit()
