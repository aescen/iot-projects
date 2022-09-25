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
APP_NAME = "SERVER APLIKASI PANTAU BIOFLOK"
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
                header, data = network.read(24)
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
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                db=db,
                charset=charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except pymysql.err.Error as msg:
            print("Connection error: ", msg)
            sys.exit()

    def saveCurrentDataToDb(idKolam):
        # save to db
        try:
            result = """
                       UPDATE
                         `pantaubioflok`
                       SET 
                         `cuaca` = '{0}',
                         `airhujan` = '{1}',
                         `kekeruhan` = '{2}',
                         `pakan` = '{3}'
                       WHERE
                         `pantaubioflok`.`kolam` = '{4}'
                     """.format(
                          cuacaId[newValCuaca],
                          valAirHujan,
                          valKekeruhan,
                          valBeratPakan,
                          idKolam)
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
    mesh.begin(111, RF24_1MBPS, 10000)
    radio.setRetries(2, 8)
    radio.setPALevel(RF24_PA_LOW) # Power Amplifier
    time.sleep(.1)
    radio.printPrettyDetails()
    print('Server Node');

    # sensor vars
    valAirHujan = 0
    valKekeruhan = 0
    valBeratPakan = 0
    valCuaca = 1
    nodeId = 0
    newValAirHujan = 0
    newValKekeruhan = 0
    newValBeratPakan = 0
    newValCuaca = 1

    # timer vars
    mainInterval = 2000
    mainTimer = millis()

    sensorUpdateInterval = 2000
    sensorUpdateTimer = millis()

    # mesh vars
    headerProperties = {
        HEADER_NODE: 'fffff',
        HEADER_SERVER: 'f',
        'type': [HEADER_NODE, HEADER_SERVER]
    }
    kolamNodeIds = {
        1: 'A',
        2: 'B'
    }
    
    cuacaId = {
        1: 'HUJAN',
        2: 'CERAH'
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
                    tds, fc, cc, lc, nid = meshData['data']
                    newValKekeruhan = float(tds)
                    newValAirHujan = float(fc)
                    newValBeratPakan = float(lc)
                    newValCuaca = int(cc)
                    nodeId = int(nid)
                    print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y' ), end='')
                    print(f"Node: {nodeId} - Kekeruhan: {tds:.2f} - Air Hujan: {fc:.2f} - ", end='')
                    print(f"Cuaca: {cuacaId[newValCuaca]} - Berat pakan: {lc:.2f}")

            # sensor data
            if millis() - sensorUpdateTimer > sensorUpdateInterval:
                if ( valAirHujan != newValAirHujan
                    or valKekeruhan != newValKekeruhan
                    or valBeratPakan != newValBeratPakan ):
                    valAirHujan = newValAirHujan
                    valKekeruhan = newValKekeruhan
                    valBeratPakan = newValBeratPakan
                    valCuaca = newValCuaca

                    saveCurrentDataToDb(kolamNodeIds[nodeId])

                sensorUpdateTimer = millis()

        except KeyboardInterrupt:
            print("[INFO] exiting...")
            radio.powerDown()
            sys.exit()

if __name__ == '__main__':
    print(APP_NAME)
    main()
