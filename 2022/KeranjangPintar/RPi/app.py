#!/usr/bin/env python3

# system imports
from datetime import datetime
import cv2
import os
import sys
import time
import argparse
import pymysql

# project imports
from utils import *

#const vars
APP_NAME = "SERVER APLIKASI KERANJANG PINTAR"
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
                header, data = network.read(20)
                #payloadSize = network.peek(header)
                #_, data = network.read(payloadSize)
                if chr(header.type) in headerProp['type']:
                    ststr = headerProp[chr(header.type)]
                    payload['id'] = header.from_node
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

    def saveCurrentDataToDb(nodeId):
        # save to db
        try:
            result = f"""
                INSERT INTO `keranjang_pos` (
                    `id_user`,
                    `id_keranjang`,
                    `id_produk`,
                    `jumlah`)
                VALUES (
                    '1',
                    '{nodeId}',
                    '{valTagId}',
                    '{valJumlah}')"""
            dbCursor.execute(result)
            dbConnection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)

    # Camera setup
    ct = Camera(VIDEO_SRC)

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
    print('Server nodeID:', mesh.getNodeID());

    # sensor vars
    valJumlah = 0
    valTagId = ''

    # timer vars

    # mesh vars
    headerProperties = {
        HEADER_NODE: 'fff',
        HEADER_SERVER: 'f',
        'type': [HEADER_NODE, HEADER_SERVER]
    }
    nodeIds = {
        '1': '1',
        '2': '2'
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
                    cid1, cid2, cid3, cid4, cid5, jumlah, nid = meshData['data']
                    nid = int(nid)
                    newValTagId = f"{int(cid1)}_{int(cid2:d)}_{int(cid3:d)}_{int(cid4:d)}_{int(cid5:d)}"
                    newValJumlah = int(jumlah)
                    print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y'),
                        f"ID: {nid} - Jumlah: {newValJumlah} - TagID: {newValTagId}")

                    valJumlah = newValJumlah
                    valTagId = newValTagId

                    saveCurrentDataToDb(nodeIds['nid'])
                    time.sleep(.37)

        except KeyboardInterrupt:
            print("[INFO] exiting...")

            radio.powerDown()
            sys.exit()

if __name__ == '__main__':
    print(APP_NAME)
    main()
