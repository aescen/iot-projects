#!/usr/bin/env python3

from __future__ import print_function

import time, pymysql
import traceback
from struct import unpack
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

octlit = lambda val:int(val, 8)
millis = lambda: int(round(time.time() * 1000)) & 0xffffffff

# radio setup
radio = RF24(22, 0)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)

mesh.setNodeID(0)
mesh.begin(97, RF24_1MBPS, 5000)
radio.setRetries(2, 2);
radio.setAutoAck(True);
radio.setPALevel(RF24_PA_MIN);
radio.setDataRate(RF24_1MBPS);
radio.setCRCLength(RF24_CRC_8);
radio.printPrettyDetails()
print('Running ...')
time.sleep(1)

def main():
    while True:
        try:
            mesh.update()
            mesh.DHCP()

            while network.available():
                try:
                    # arrange variable position from byte->char->int->float (lowest to highest w/o precision)
                    header, payload = network.read(24)
                    nodeId = unpack( 'H', bytes( payload[0:2] ) ) [0] # data is uint16_t from uno which use 2 bytes
                    rtcTime = unpack( 'L', bytes( payload[2:6] ) ) [0] # data is uint32_t from uno which use 4 bytes
                    fields = unpack('f f f f', bytes(payload[6:])) # the rest of float datas
                    # go to https://docs.python.org/3/library/struct.html for more format/type
                    if chr(header.type) == 'M':
                        # parse
                        acVoltage, dcVoltage, acCurrent, dcCurrent = fields[:4]
                        acVoltage = round(float(acVoltage), 4)
                        dcVoltage = round(float(dcVoltage), 4)
                        acCurrent = round(float(acCurrent), 4)
                        dcCurrent = round(float(dcCurrent), 4)
                        #timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(rtcTime))) # time in localtime, automatically +timezone (+7 hour in WIB)
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(rtcTime))) # time in UTC
                        nodeId = int(nodeId)
                        print(datetime.now().strftime('%H:%M:%S'),
                            'Received payload:')
                        print('\t AC voltage:', acVoltage,
                            'DC voltage:', dcVoltage,
                            'AC current:', acCurrent),
                            'DC current:', dcCurrent)
                        print('\t Timestamp:', timestamp,
                            'node ID:', nodeId,
                            'from node:', header.from_node)
                        
                        # save to db
                        try:
                            result = """
                                      UPDATE `nrf24lampu`
                                        SET `acVoltage` = '{0}', 
                                            `dcVoltage` = '{1}',
                                            `acCurrent` = '{2}',
                                            `dcCurrent` = '{2}',
                                            `timeStamp` = '{3}',
                                            `meshId` = '{4}'
                                        WHERE `nrf24lampu`.`id` = {5}
                                     """.format(acVoltage,
                                            dcVoltage,
                                            acCurrent,
                                            dcCurrent,
                                            timestamp,
                                            header.from_node,
                                            nodeId)

                            cc.execute(result)
                            connection.commit()
                        except pymysql.err.InternalError as msg:
                            print("Command skipped: ", msg)
                    else:
                        print('Unknown type.')
                except Exception:
                    print(traceback.format_exc())

            time.sleep(0.01)
        except KeyboardInterrupt:
            try:
                radio.stopListening()
                radio.powerDown()
                time.sleep(.5)
                print('End.')
                exit()
            except (Exception, KeyboardInterrupt):
                print('Forced exit.')
                exit()

if __name__ == '__main__':
    main()
