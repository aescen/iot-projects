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
APP_NAME = "SERVER APLIKASI PANTAU PERKEBUNAN JERUK"
HEADER_NODE = 'N'
HEADER_SERVER = 'S'
NODE_SPRAY = '03'
#VIDEO_SRC = 'rtsp://admintapo:admintapo@192.168.0.100/stream1' #high quality
VIDEO_SRC = 'rtsp://admintapo:admintapo@192.168.0.100/stream2' #low quality
WIN_NAME = 'TapoCam_C310'
IMG_DIR = '/var/www/html/pantaujeruk/imgs/'
THRESH_PH = 6
THRESH_HUMID = 40
TEST_MODE = False

class CameraTapo:
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

    def sendPayload(toNodeId, relaySpray):
        sentStatus = False
        payload = pack( "f", float(relaySpray) )
        if not mesh.write( payload, ord(HEADER_SERVER), octlit(toNodeId) ):
            print("Send fail!")
        else:
            sentStatus = True

        return sentStatus

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
                UPDATE
                    `pantaujeruk`
                SET
                    `ph` = '{valPh}',
                    `moist` = '{valMoist}'
                WHERE
                    `pantaujeruk`.`node_id` = '{nodeId}'"""
            dbCursor.execute(result)
            dbConnection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)

    def saveImagePathToDb(imgName):
        try:
            result = f"""
                        UPDATE
                            `pantaujeruk`
                        SET
                            `imgPath` = '{imgName}'
                        WHERE
                            `pantaujeruk`.`node_id` = {int(NODE_SPRAY)}
                     """
            dbCursor.execute(result)
            dbConnection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)

    def getSoilQuality(ph, moist):
        if int(ph) != THRESH_PH and int(moist) < 40:
            return 'BAD'
        if int(ph) == THRESH_PH and int(moist) < 40:
            return 'DRY'
        if int(ph) == THRESH_PH and int(moist) > 40:
            return 'OK'

    def runTest(ph, moist, nodeId):
        meshUpdate()
        valPh = ph
        valMoist = moist
        saveCurrentDataToDb(nodeId)
        #control node spray
        code = controlCode[getSoilQuality(valPh, valMoist)]
        sendPayload(NODE_SPRAY, code)
        print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y'),
            f"To {NODE_SPRAY} -> relay: {code}")
        #save image
        img = ct.getImage()
        imgName = datetime.now().strftime( '%Y-%m-%d_%H.%M.%S') + '.png'
        ct.saveToDisk(IMG_DIR + imgName, img)
        saveImagePathToDb(imgName)

    # Camera setup
    ct = CameraTapo(VIDEO_SRC)

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
    valPh = 0
    valMoist = 0
    newValPh = 0
    newValMoist = 0

    # timer vars
    controlInterval = 30000
    controlTimer = millis()
    

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
    controlCode = {
        'OK': 0,
        'DRY': 1,
        'BAD': 2
    }
    snapTime = [
        7, 15
    ]

    ##------------------------------------------------------------------------------

    time.sleep(2)

    if TEST_MODE:
        print('[INFO] Running test...')

        print('[INFO] Test: ph=7, moist=33, from node:1')
        runTest(7, 33, 1)
        time.sleep(2)
        print('[INFO] Test: ph=5, moist=33, from node:2')
        runTest(5, 33, 2)
        time.sleep(2)
        print('[INFO] Test: ph=6, moist=33, from node:1')
        runTest(6, 33, 1)
        time.sleep(2)
        print('[INFO] Test: ph=6, moist=55, from node:2')
        runTest(6, 55, 2)
        sys.exit()


    print('[INFO] Running ...')

    while True:
        try:
            # mesh
            meshUpdate()
            meshData = readMeshNetwork(headerProperties)

            if meshData['data'] != None:
                if meshData['type'] == HEADER_NODE:
                    tds, fc, nid = meshData['data']
                    nid = int(nid)
                    newValPh = float(fc)
                    newValMoist = float(tds)
                    print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y'),
                        f"ID: {nid} - TDS: {tds:.2f} - FC: {fc:.2f}")

            # sensor data
            if millis() - sensorUpdateTimer > sensorUpdateInterval:
                if ( valPh != newValPh or valMoist != newValMoist ):
                    valPh = newValPh
                    valMoist = newValMoist
                    saveCurrentDataToDb(nodeIds[nid])

                sensorUpdateTimer = millis()

            # control + save snapshot
            if millis() - controlTimer > controlInterval:
                if int(datetime.now().strftime('%H')) in snapTime:

                    #control node spray
                    code = controlCode[getSoilQuality(valPh, valMoist)]
                    sendPayload(NODE_SPRAY, code)
                    print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y'),
                        f"To {NODE_SPRAY} -> relay: {code}")
                    #save image
                    img = ct.getImage()
                    imgName = datetime.now().strftime( '%Y-%m-%d_%H.%M.%S') + '.png'
                    ct.saveToDisk(IMG_DIR + imgName, img)
                    saveImagePathToDb(imgName)

                controlTimer = millis()

        except KeyboardInterrupt:
            print("[INFO] exiting...")

            radio.powerDown()
            sys.exit()

if __name__ == '__main__':
    print(APP_NAME)
    main()
