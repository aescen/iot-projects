#!/usr/bin/env python3

# system imports
from datetime import datetime
import os
import sys
import time
import argparse
import pymysql

# project imports
from utils import *

#const vars
APP_NAME = "SERVER APLIKASI OTOBUS"
HEADER_NODE = 'N'
HEADER_SERVER = 'S'

def main():
    def meshUpdate():
        try:
            mesh.DHCP()
            mesh.update()
        except Exception as e:
            print(e)

    def readMeshNetwork(headerProp):
        payload = { 'id': None, 'type': None, 'data': None }
        data = {}
        if network.available():
            try:
                header, data = network.read(16)
                if chr(header.type) in headerProp['type']:
                    ststr = headerProp[chr(header.type)]
                    payload['id'] = int(header.from_node)
                    payload['type'] = chr(header.type)
                    payload['data'] = unpack(ststr, bytes(data))
                    return payload
                else:
                    print('Rcv bad type {} from 0{:o}'.format(chr(header.type), header.from_node));
                    return payload
            except Exception as e:
                print('Error', e, ', payload length', len(data))
                return payload
            except Exception as e:
                print(e)
                return payload
        return payload

    def getDbConnection(host='localhost', user='pi', password='raspberry', db='pi', charset='utf8'):
        try:
            connection = pymysql.connect(host=host,
                                         user=user,
                                         password=password,
                                         db=db,
                                         charset=charset,
                                         cursorclass=pymysql.cursors.DictCursor)
            return connection
        except pymysql.err.Error as msg:
            print("Connection error: ", msg)
            sys.exit()

    def saveCurrentDataToDb(idNode):
        # save to db
        try:
            result = """
                       UPDATE
                         `otobus`
                       SET 
                         `power_usage` = '{0}',
                         `info` = '{1}'
                       WHERE
                         `otobus`.`node_id` = {2}
                     """.format(
                          valDaya,
                          valInfo,
                          idNode)
            dbCursor.execute(result)
            dbConnection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)

    # Database setup..
    dbConnection = getDbConnection()
    dbCursor = dbConnection.cursor()

    # NRF radio setup
    radio = RF24(22, 0, 8000000)
    network = RF24Network(radio)
    mesh = RF24Mesh(radio, network)

    mesh.setNodeID(0)
    if not radio.begin():
        print("Radio hardware not responding!")
        sys.exit()
    mesh.begin(99, RF24_1MBPS, 10000)
    radio.setRetries(2, 8)
    radio.setPALevel(RF24_PA_HIGH) # Power Amplifier
    time.sleep(.1)
    radio.printPrettyDetails()
    print('Server Node');

    # sensor vars
    valDaya = 0
    valInfo = 0
    newValDaya = 0
    newValInfo = 0
    
    valNid = 0

    # timer vars
    sensorUpdateInterval = 2000
    sensorUpdateTimer = millis()

    # mesh vars
    headerProperties = {
        HEADER_NODE: 'fff',
        HEADER_SERVER: 'f',
        'type': [HEADER_NODE, HEADER_SERVER]
    }
    
    infoStatus = {
        0: 'NORMAL',
        1: 'BERLEBIH'
    }

    ##------------------------------------------------------------------------------

    time.sleep(1)
    print('[INFO] Running ...')

    while True:
        try:
            # mesh
            meshUpdate()
            meshData = readMeshNetwork(headerProperties)

            if meshData['data'] != None:
                if meshData['type'] == HEADER_NODE:
                    w, i, nid = meshData['data']
                    newValDaya = float(w)
                    newValInfo = int(i)
                    valNid = int(nid)
                    print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y'),
                        f"Node: {valNid} - Daya: {newValDaya:.2f} - Info: {infoStatus[newValInfo]}")

            # sensor data
            if millis() - sensorUpdateTimer > sensorUpdateInterval:
                if ( valDaya != newValDaya
                  or valInfo != newValInfo ):
                    valDaya = newValDaya
                    valInfo = newValInfo
                    saveCurrentDataToDb(valNid)

                sensorUpdateTimer = millis()

        except KeyboardInterrupt:
            print("[INFO] exiting...")
            radio.powerDown()
            sys.exit()

if __name__ == '__main__':
    print(APP_NAME)
    main()
