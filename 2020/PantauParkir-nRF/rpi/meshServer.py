#!/usr/bin/env python

from __future__ import print_function
from struct import *
from RF24 import *
from RF24Network import *
from RF24Mesh import *
from array import array
from datetime import datetime
import time, sys, re
import pymysql

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
millis = lambda: int(round(time.time() * 1000)) & 0xffffffff
interval = 2000
last_sent = 0
MAX_CAP = 40
jumlahKendaraan = 0
pirDetect = -1
tmp = 0
BUFFER_SIZE = 8

# radio setup
radio = RF24(22, 0, 8000000)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)
mesh.setNodeID(octlit('00'))
mesh.begin(97, RF24_1MBPS, 10000)
radio.setPALevel(RF24_PA_MAX)
radio.printDetails()
print('Start server node:', mesh.getNodeID());
cnt = 0
while cnt < 5:
    print(" . ", end='', flush=True)
    time.sleep(1);
    cnt += 1
print('')
print('Server running ...')

if __name__ == '__main__':
    try:
        while True:
            mesh.update()
            mesh.DHCP()
            if network.available():
                header, payload = network.read(BUFFER_SIZE)
                try:
                    if chr(header.type) == 'M':
                        nodeId, jumlahKendaraan = unpack('LL', bytes(payload))
                        meshId = header.from_node
                        if jumlahKendaraan == 0:
                            parkirStatus = 'Kosong'
                        elif jumlahKendaraan >= 0 and jumlahKendaraan < 35:
                            parkirStatus = 'Tersedia'
                        elif jumlahKendaraan >= 35 and jumlahKendaraan < 40:
                            parkirStatus = 'Hampir penuh'
                        elif jumlahKendaraan >= 40:
                            parkirStatus = 'Penuh'
                        else:
                            parkirStatus = 'null'
                        
                        if jumlahKendaraan <= 40:
                            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            print(ts, '|Received from node:', nodeId, 'meshId', meshId, 'total:', jumlahKendaraan, 'status:', parkirStatus)
                            
                            try:
                                result = '''
                                          UPDATE `parkirpolinema`
                                           SET
                                            `meshNodeId` = '{1}',
                                            `jumlahKendaraan`='{2}',
                                            `parkirStatus`='{3}',
                                            `timeStamp`='{4}'
                                           WHERE
                                            `parkirpolinema`.`nodeId` = {0};
                                         '''.format(nodeId, meshId, jumlahKendaraan, parkirStatus, ts)
                                cc.execute(result)
                                connection.commit()
                            except pymysql.err.InternalError as msg:
                                print('Command skipped: ', msg)
                            
                        else:
                            print(ts, '|Received from:', meshId, 'nodeId', nodeId, 'Jumlah kendaraan melebihi kapasitas({}):'.format(MAX_CAP), jumlahKendaraan)    
                            
                    else:
                        print('Rcv bad type {} from 0{:o}'.format(header.type, header.from_node));
                except Exception as e:
                    print('Error', e, ', payload length', len(payload))
                    try:
                        BUFFER_SIZE = int(re.findall(r'\b\d+\b', str(e))[0]) #regexp
                        print('Will try with BUFFER_SIZE:', BUFFER_SIZE, ' instead...')
                    except Exception as t:
                        print('Error:', t, '- cannot change buffer size.')
    except KeyboardInterrupt:
        radio.powerDown()
        sys.exit()