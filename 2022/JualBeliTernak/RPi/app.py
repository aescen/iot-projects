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
APP_NAME = "SERVER APLIKASI TERNAK"
HEADER_NODE = 'N'
HEADER_SERVER = 'S'
VIDEO_SRC = 0
IMG_DIR = '/var/www/html/pantauternak/imgs/'
HARGA_PER_KILO = 120000

class Camera:
    def __init__(self, urlStream):
        self.vs = None
        self.urlStream = urlStream
        if OS_TYPE == WINDOWS:
            self.vs = cv2.VideoCapture(urlStream, cv2.CAP_DSHOW) #CAP_FFMPEG, CAP_IMAGES, CAP_DSHOW, CAP_MSMF, CAP_V4L2
            r, f = vs.read()
            if f == None:
                self.vs = cv2.VideoCapture(urlStream)
        else:
            self.vs = cv2.VideoCapture(urlStream)
        time.sleep(.5)

    def getImage(self, dec='raw'):
        grabbed, raw = self.vs.read()
        
        if dec == 'raw':
            return raw
        
        (flag, encodedImage) = cv2.imencode(f".{dec}", raw)
        return encodedImage
    
    def saveToDisk(self, path, img):
        #'/path/to/destination/image.png'
        cv2.imwrite(path, img)
        return path

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

    def saveCurrentDataToDb():
        # save to db
        try:
            result = f"""
                INSERT INTO `pantauternak` (
                    `tipe`,
                    `berat`,
                    `Harga`,
                    `suhu`,
                    `keterangan`,
                    `time_stamp`,
                    `img_path`)
                VALUES (
                    'Kambing',
                    '{valBerat}',
                    '{valHarga}',
                    '{valSuhu}',
                    'Sehat',
                    current_timestamp(),
                    '{valImgPath}')"""
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
    valBerat = 0
    valHarga = 0
    valSuhu = 0
    valKeterangan = 'Sehat'
    valImgPath = 'Kambing.png'

    # timer vars
    sensorUpdateInterval = 2000
    sensorUpdateTimer = millis()

    # mesh vars
    headerProperties = {
        HEADER_NODE: 'fff',
        HEADER_SERVER: 'f',
        'type': [HEADER_NODE, HEADER_SERVER]
    }
    nodeIds = {
        1: '1',
        2: '2'
    }

    ##------------------------------------------------------------------------------

    time.sleep(2)

    print('[INFO] Running ...')

    while True:
        try:
            # mesh
            meshUpdate()
            meshData = readMeshNetwork(headerProperties)

            if meshData['data'] != None:
                if meshData['type'] == HEADER_NODE:
                    berat, suhu, nid = meshData['data']
                    nid = int(nid)
                    newValBerat = float(berat)
                    newValSuhu = float(suhu)
                    newValHarga = newValBerat * HARGA_PER_KILO
                    print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y'),
                        f"ID: {nid} - Berat: {berat:.2f} - Suhu: {suhu:.2f}")
                    
                    if ( valBerat != newValBerat or valSuhu != newValSuhu or valHarga != newValHarga):
                        img = ct.getImage()
                        valBerat = newValBerat
                        valSuhu = newValSuhu
                        valHarga = newValHarga
                        valImgPath = datetime.now().strftime( '%Y-%m-%d_%H.%M.%S') + '.webp'

                        ct.saveToDisk(IMG_DIR + valImgPath, img)

                        saveCurrentDataToDb()

        except KeyboardInterrupt:
            print("[INFO] exiting...")

            radio.powerDown()
            sys.exit()

if __name__ == '__main__':
    print(APP_NAME)
    main()
