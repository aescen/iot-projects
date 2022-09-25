#!/usr/bin/env python3

# system imports
from queue import Queue
from flask import request as FlaskRequest
from flask import Response as FlaskResponse
from flask import Flask, render_template, jsonify
from flask_cors import CORS as FlaskCORS
from threading import Thread, Lock
from datetime import datetime
import os
import re
import sys
import time
import argparse
import logging
import cv2
import pymysql

# project imports
from ai_detections import ObjectDetection
from utils import *


# const vars
NODE_LAMP = '01'
HEADER_SERVER = 'S'
HEADER_OUTDOOR = 'O'
HEADER_INDOOR = 'I'

# global vars
logging.getLogger('werkzeug').disabled = True
threadLock = Lock()

def main():
    def delayFPS(fps, x=2):
        if fps < 1:
            return 1
        return 1 / (fps * x)

    def sendPayload(toNodeId, led, uv, uvo, luxo, p):
        sentStatus = False
        payload = pack( "fffff", float(luxo), float(uvo), float(led), float(uv), float(p) )
        if not mesh.write( payload, ord(HEADER_SERVER), octlit(toNodeId) ):
            print("Send fail!")
        else:
            #print( "Send ok:", toNodeId, "->", { int(uv), int(led), int(p), uvo, luxo, }, "\t" )
            sentStatus = True

        return sentStatus

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
            result = """
                       UPDATE
                         `kontroluv`
                       SET 
                         `lux_led` = '{0}',
                         `temp` = '{1}',
                         `humid` = '{2}',
                         `uv_outdoor` = '{3}',
                         `uv_indoor` = '{4}',
                         `power_usage` = '{5}',
                         `total_visitor` = '{6}'
                       WHERE
                         `kontroluv`.`id` = {7}
                     """.format(
                          valLuxIndoor,
                          valTempIndoor,
                          valHumidIndoor,
                          valUVOutdoor,
                          valUVIndoor,
                          valPowerUsage,
                          valPersonCount,
                          0)
            dbCursor.execute(result)
            dbConnection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)

    def imageStream(host="0.0.0.0", port="5000", debug=False, secure=False):
        app = Flask(__name__)
        certPath = os.path.abspath(
                     os.path.dirname(os.path.abspath(__file__)) + '/web/aesce.local/local.crt')
        keyPath = os.path.abspath(
                os.path.dirname(os.path.abspath(__file__)) + '/web/aesce.local/local.key')
        FlaskCORS(app, send_wildcard=True)
        streamQueue = Queue()
        serveQueue = Queue()

        def encodeImageStream():
            flag = None
            encodedImage = None
            try:
                while True:
                    with threadLock:
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 37]
                        (flag, encodedImage) = cv2.imencode(
                            ".jpeg", od.getFrameDetection(resize=True, w=320, h=240), encode_param)
                        # (flag, encodedImage) = cv2.imencode(
                        #    ".png", od.getFrameDetection())
                        if not flag:
                            continue
                    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                          bytearray(encodedImage) + b'\r\n')
                    # yield(b'--frame\r\n' b'Content-Type: image/png\r\n\r\n' +
                    #      bytearray(encodedImage) + b'\r\n')
                    time.sleep(delayFPS(od.getFps()))
            except Exception as e:
                print(e)
                return

        def encodeImage():
            try:
                with threadLock:
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 37]
                    (flag, encodedImage) = cv2.imencode(
                        ".jpeg", od.getFrameDetection(resize=True, w=320, h=240), encode_param)
                    # (flag, encodedImage) = cv2.imencode(
                    #    ".png", od.getFrameDetection())
                    if not flag:
                        return
                    return encodedImage
            except Exception as e:
                print(e)
                return

        @app.route("/imagestream")
        def stream():
            resp = FlaskResponse(encodeImageStream(), mimetype="multipart/x-mixed-replace; boundary=frame")
            resp.headers['Bypass-Tunnel-Reminder'] = True
            return resp

        @app.route("/image")
        def image():
            resp = FlaskResponse(streamQueue.get(True)['image'], mimetype="image/jpeg", content_type="image/jpeg")
            resp.headers['Bypass-Tunnel-Reminder'] = True
            return resp

        def appRun():
            print('[INFO] Server running on: %s:%s' % (host, port))
            #certificate and key files
            if secure:
                context = (certPath, keyPath)
                app.run(host=host, port=port, debug=debug, ssl_context=context,
                        threaded=True, use_reloader=False)
            else:
                app.run(host=host, port=port, debug=debug,
                        threaded=True, use_reloader=False)

        imagefeedthread = Thread(target=appRun,
                             name='feed_image', args=())
        imagefeedthread.daemon = True
        imagefeedthread.start()

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

    # args
    ap = argparse.ArgumentParser()
    ap.add_argument("-y", "--yolo",
                    default=os.path.abspath(os.path.dirname(
                        os.path.abspath(__file__)) + '/YOLO'),
                    help="path to yolo directory")
    ap.add_argument("-t", "--videotype", default='stream',
                    help="path/url to video file/streams/url")
    ap.add_argument("-v", "--video", default='stream',
                    help="type of video filepath/streams/url")
    ap.add_argument("-C", "--camera", type=int, default=0,
                    help="camera source")
    ap.add_argument("-W", "--maxWidth", type=int, default=640,
                    help="Video max width")
    ap.add_argument("-H", "--maxHeight", type=int, default=480,
                    help="Video max height")
    ap.add_argument("-s", "--saveVideo", default="no",
                    help="Save video?")
    ap.add_argument("-A", "--host", default='0.0.0.0',
                    help="host/address name for flask")
    ap.add_argument("-P", "--port", default="5000",
                    help="port number for flask")
    ap.add_argument("-u", "--use-gpu", type=int, default=0,
                    help="GPU mode")
    ap.add_argument("-c", "--confidence", type=float, default=.51,
                    help="minimum probability to filter weak detections")
    ap.add_argument("-f", "--frameskip", type=int, default=3,
                    help="frames to skip(default: 3)")
    ap.add_argument("-V", "--videofps", type=float, default=30.0,
                    help="Frame per second")
    ap.add_argument("-a", "--abc", default="no",
                    help="auto brightness and contrast clip histogram, ex. -a 0.5")
    args = vars(ap.parse_args())

    if args['video'] != 'stream':
        args['video'] = os.path.sep.join(
            [os.path.abspath(os.curdir), os.path.relpath(args['video'])])
    args['videotype'] = 'file' if (
        args['video'] != 'stream' and args['videotype'] == 'stream') else args['videotype']

    #-
    odParams = {
        'args': args,
        'classes4person': ["person", "_1_", "_2_", "_3_", "_4_"],
        'url': None,
        'username': None,
        'password': None,
        'timeout': 10,
        'forceResize': True,
        'abcClip': .51
    }

    od = ObjectDetection(odParams)

    # sensor vars
    valUVIndoor = 0
    valLuxIndoor = 0
    valPowerUsage = 0
    newValUVIndoor = 0
    newValLuxIndoor = 0
    newValPowerUsage = 0

    valHumidIndoor = 0
    valTempIndoor = 0
    valUVOutdoor = 0
    valLuxOutdoor = 0
    newValHumidIndoor = 0
    newValTempIndoor = 0
    newValUVOutdoor = 0
    newValLuxOutdoor = 0

    # object detection vars
    valPersonCount = 0
    isPersonDetected = False

    # control vars
    valUVLampRelay = 0
    valLEDLampRelay = 0
    isConnectionProblem = False
    failCount = 0

    # timer vars
    sensorUpdateInterval = 2000
    sensorUpdateTimer = millis()

    controlInterval = 2000
    controlTimer = millis()

    # mesh vars
    headerProperties = {
        HEADER_INDOOR: 'fffff',
        HEADER_OUTDOOR: 'ff',
        HEADER_SERVER: 'f',
        'type': [HEADER_INDOOR, HEADER_OUTDOOR, HEADER_SERVER]
    }

    ##------------------------------------------------------------------------------
    print('[INFO] Start object detection ...')
    od.start()

    print('[INFO] Start image streaming ...')
    imageStream(host=args['host'], port=args['port'], secure=False)

    time.sleep(1)
    print('[INFO] Running ...')

    while True:
        try:
            # object detection
            if not od.isStopped():
                sys.stdout.write("\r Detections => person: %d  | FPS: %.2f \t\t\r"
                    % (od.getPersonDetection(), od.getFps()) )
            else:
                raise KeyboardInterrupt
            valPersonCount = od.getPersonDetection()
            isPersonDetected = od.isPersonDetected()

            # mesh
            meshUpdate()
            meshData = readMeshNetwork(headerProperties)

            if meshData['data'] != None:
                if meshData['type'] == HEADER_INDOOR:
                    h, t, uvi, luxi, pu = meshData['data']
                    newValHumidIndoor = float(h)
                    newValTempIndoor = float(t)
                    newValUVIndoor = float(uvi)
                    newValLuxIndoor = float(luxi)
                    newValPowerUsage = float(pu)
                    print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y'),
                        f"Indoor -> UV: {uvi:.2f} - Lux: {luxi:.2f} - Humid: {h:.2f} - Temp: {t:.2f} - Power: {pu:.2f}")
                if meshData['type'] == HEADER_OUTDOOR:
                    uvo, luxo = meshData['data']
                    newValUVOutdoor = float(uvo)
                    newValLuxOutdoor = float(luxo)
                    print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y'),
                        f"Outdoor -> UV: {uvo:.2f} - Lux: {luxo:.2f}")

            # sensor data
            if millis() - sensorUpdateTimer > sensorUpdateInterval:
                if ( valLuxIndoor != newValLuxIndoor
                  or valHumidIndoor != newValHumidIndoor
                  or valTempIndoor != newValTempIndoor
                  or valUVIndoor != newValUVIndoor
                  or valUVOutdoor != newValUVOutdoor
                  or valLuxIndoor != newValLuxIndoor
                  or valLuxOutdoor != newValLuxOutdoor
                  or valPowerUsage != newValPowerUsage ):
                    valLuxIndoor = newValLuxIndoor
                    valHumidIndoor = newValHumidIndoor
                    valTempIndoor = newValTempIndoor
                    valUVIndoor = newValUVIndoor
                    valUVOutdoor = newValUVOutdoor
                    valLuxIndoor = newValLuxIndoor
                    valLuxOutdoor = newValLuxOutdoor
                    valPowerUsage = newValPowerUsage
                    saveCurrentDataToDb()
                    

                sensorUpdateTimer = millis()

            # control
            if millis() - controlTimer > controlInterval:
                sent = False
                if isPersonDetected:
                    valUVLampRelay = 0
                    valLEDLampRelay = 1
                else:
                    valUVLampRelay = 1
                    valLEDLampRelay = 0
                
                sent = sendPayload(NODE_LAMP, valLEDLampRelay, valUVLampRelay, valUVOutdoor, valLuxOutdoor, valPersonCount)
                print(datetime.now().strftime( '%H:%M:%S-%d/%m/%Y'),
                    f"To {NODE_LAMP} -> uv: {int(valUVLampRelay)} led: {int(valLEDLampRelay)} person: {valPersonCount} {sent}")

                controlTimer = millis()

        except KeyboardInterrupt:
            print("[INFO] exiting...")
            if not od.isStopped():
                od.stop()

            radio.powerDown()
            sys.exit()

if __name__ == '__main__':
    main()
