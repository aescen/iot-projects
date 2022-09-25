#!/usr/bin/env python3

from __future__ import print_function

import time, sys, pymysql
import traceback
from struct import unpack
from struct import Struct
from RF24 import *
from RF24Network import *
from RF24Mesh import *
from array import array
from datetime import datetime

octlit = lambda val:int(val, 8)
millis = lambda: int(round(time.time() * 1000)) & 0xffffffff

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
radio = RF24(22, 0, 8000000)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)

mesh.setNodeID(0o0)
mesh.begin(97, RF24_1MBPS, 5000)
radio.setRetries(2, 8);
radio.setPALevel(RF24_PA_HIGH);
radio.setDataRate(RF24_1MBPS);
radio.setCRCLength(RF24_CRC_8);
radio.printPrettyDetails()
print('Running ...')
time.sleep(1)

if __name__ == '__main__':
    status = 2
    total = 0

    for i in range(1, 4):
        sqlResult = """
                UPDATE `pengadukmasker`
                    SET `status` = '{0}',
                        `total` = '{1}'
                    WHERE `pengadukmasker`.`id` = {2};
                     """.format(status, total, i)
        cc.execute(sqlResult)
        connection.commit()

    while True:
        try:
            mesh.update()
            mesh.DHCP()

            while network.available():
                try:
                    header, payload = network.read(12)
                    s = Struct('f f f')
                    fields = s.unpack(bytes(payload))
                    newStatus, newTotal, nodeId = fields[:3]
                    newStatus = int(newStatus)
                    newTotal = int(newTotal)
                    nodeId = int(nodeId)

                    if newStatus != status or newTotal != total:
                        try:
                            sqlResult = """
                                        UPDATE `pengadukmasker`
                                            SET `status` = '{0}',
                                                `total` = '{1}'
                                            WHERE `pengadukmasker`.`id` = {2};
                                        """.format(newStatus, newTotal, nodeId)
                            cc.execute(sqlResult)
                            connection.commit()
                            status, total = newStatus, newTotal
                        except pymysql.err.InternalError as msg:
                            print("Command skipped: ", msg)
                        print(datetime.now().strftime('%H:%M:%S-%d/%m/%Y'), 'Received payload: ', 'Status:', status, 'Total:', total, 'Node Id:', nodeId, 'From node:', header.from_node)

                except Exception as e:
                    print(e)

        except KeyboardInterrupt:
            radio.powerDown()
            connection.close()
            sys.exit()
