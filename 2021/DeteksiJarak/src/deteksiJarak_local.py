#!/usr/bin/python3

# pre-trained model src:
# mask: https://github.com/lp6m/tiny_yolov3_face_mask_detect
# person: https://github.com/ufukguler/tinyYOLOv3-person-detection
# distance src:
# distance: https://github.com/Subikshaa/Social-Distance-Detection-using-OpenCV

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from threading import Thread, Lock
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from scipy.spatial import distance
from math import sqrt
import pymysql
import sys
import time
import base64
import socket
import imutils
import argparse
import traceback
import cv2
import numpy as np
import os
import json
from datetime import timedelta, datetime as dt
from queue import Queue
from flask import request as FlaskRequest
from flask import Response as FlaskResponse
from flask import Flask, render_template, jsonify
from flask_cors import CORS as FlaskCORS
# from dotenv import load_dotenv
# dotenv_path = join(dirname(__file__), '.env')  # Path to .env file
# load_dotenv(dotenv_path)
# flask will find .env files in the project directory by itself.
import logging
log = logging.getLogger('werkzeug')
# error only log
# log.setLevel(logging.ERROR)
# disable log
log.disabled = True
LOCK = Lock()


RASPBIAN = 'raspbian'
LINUX = 'linux'
MACOS = 'macos'
WINDOWS = 'windows'
OS_TYPE = ''

if sys.platform == LINUX or sys.platform == "linux2":
    try:
        import RPi.GPIO as IO
        OS_TYPE = RASPBIAN
    except (ImportError, RuntimeError):
        OS_TYPE = LINUX
elif sys.platform == "darwin":
    OS_TYPE = MACOS
elif sys.platform == "win32":
    OS_TYPE = WINDOWS


def millis(): return int(round(time.time() * 1000)) & 0xffffffff


def seconds(): return int(round(time.time())) & 0xffffffff

def timestampMillisec64():
    return int((dt.utcnow() - dt(1970, 1, 1)).total_seconds() * 1000) 


def main():
    def delay(fps, x=2):
        if fps < 1:
            return 1
        return 1 / (fps * x)

    def imageStream(host="localhost", port="5000", debug=False, secure=False):
        app = Flask(__name__, template_folder=os.path.abspath(
            os.path.dirname(os.path.abspath(__file__)) + '/web/templates'))
        certPath = os.path.abspath(
                     os.path.dirname(os.path.abspath(__file__)) + '/web/aesce.local/local.crt')
        keyPath = os.path.abspath(
                os.path.dirname(os.path.abspath(__file__)) + '/web/aesce.local/local.key')
        FlaskCORS(app, send_wildcard=True)
        streamQueue = Queue()
        serveQueue = Queue()
        # webroot = os.path.join(os.path.dirname(
        #     os.path.abspath(__file__)), "web")
        
        # Database setup..
        CONN = None
        CC = None
        try:
            u, p  = '', ''
            if OS_TYPE == RASPBIAN:
                u = 'pi'
                p = 'raspberry'
            else:
                u = 'root'
                p = ''

            CONN = pymysql.connect(
                host='localhost',
                user=u,
                password=p,
                db='pi',
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)
            # Create cursor
            CC = CONN.cursor()
        except pymysql.err.Error as e:
            print("Database connection error: ", e)
            sys.exit(2)

        def getDate(ts):
            baseDatetime = dt( 1970, 1, 1 )
            delta = timedelta( 0, 0, 0, ts )
            targetDate = baseDatetime + delta
            t = dt(targetDate.date().year, targetDate.date().month, targetDate.date().day)
            targetDateTrunc = dt.utcfromtimestamp(t + 25200.0)
            return {
                'date': targetDate.strftime('%d-%m-%Y'),
                'clock': targetDate.strftime('%H:%M:%S'),
                'seconds': targetDateTrunc.timestamp(),
                'millis': targetDateTrunc.timestamp() * 1000,
                'dt': targetDate,
                'dtt': targetDateTrunc,
            }

        def saveToDb(log):
            try:
                result = '''
                            INSERT INTO `sideteksilog` (
                                `id`, `person`, `mask`, `no_mask`, `incorrect_mask`, `risky_distance`)
                            VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')
                        '''.format(
                            log['id'], log['person'], log['mask'], log['no_mask'], log['incorrect_mask'] , log['risky_distance'])
                CC.execute(result)
                CONN.commit()
            except pymysql.err.InternalError as msg:
                print("Command skipped: ", msg)

        def getLogs(start, end=False):
            try:
                start = int(start)
                end = int(end)
                result = ''
                if end == False:
                    end = start + 86400000
                sql = '''
                            SELECT * FROM `sideteksilog` WHERE `id` >= {0} AND `id` <= {1};
                        '''.format(start, end)
                CC.execute(sql)
                res = CC.fetchall()
                if isinstance(res, (list, tuple, np.ndarray)):
                    return res
                return []
            except pymysql.err.InternalError as msg:
                print("Command skipped: ", msg)
                return []

        def event_stream():
            try:
                while True:
                    msg = json.dumps(streamQueue.get(True)['event'])
                    # print("Sending {}".format(msg))
                    yield('data: {}\n\n'.format(msg))
                    time.sleep(delay(od.getFps()))
            except Exception as e:
                print(e)
                return

        def encodeImageStream():
            flag = None
            encodedImage = None
            try:
                while True:
                    with LOCK:
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 37]
                        (flag, encodedImage) = cv2.imencode(
                            ".jpg", od.getFrameDetection(resize=True, w=320, h=240), encode_param)
                        # (flag, encodedImage) = cv2.imencode(
                        #    ".png", od.getFrameDetection())
                        if not flag:
                            continue
                    yield(b'--frame\r\n' b'Content-Type: image/jpg\r\n\r\n' +
                          bytearray(encodedImage) + b'\r\n')
                    # yield(b'--frame\r\n' b'Content-Type: image/png\r\n\r\n' +
                    #      bytearray(encodedImage) + b'\r\n')
                    time.sleep(delay(od.getFps()))
            except Exception as e:
                print(e)
                return

        def encodeImage():
            try:
                with LOCK:
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 37]
                    (flag, encodedImage) = cv2.imencode(
                        ".jpg", od.getFrameDetection(resize=True, w=320, h=240), encode_param)
                    # (flag, encodedImage) = cv2.imencode(
                    #    ".png", od.getFrameDetection())
                    if not flag:
                        return
                    return encodedImage
            except Exception as e:
                print(e)
                return

        @app.route('/api/logs', methods=['POST'])
        def apiLogs():
            #_r = request.args.get('logsrange')
            #logsRange = ({'start': _r[_r.find('S')+len('S'):_r.rfind('T')],
            #              'end':} _r[_r.find('T')+len('T'):_r.rfind('E')])
            form = FlaskRequest.get_json()
            #print(form['logsrange'])
            start = form['logsrange']['start']
            end = form['logsrange']['end']
            logs = getLogs(start, end)
            
            return jsonify(logs)
        
        @app.route('/api/post', methods=['POST'])
        def apiParseSentence():
            streamQueue.put({
                'event': {
                    'id': timestampMillisec64(),
                    'person': FlaskRequest.args.get('person'),
                    'mask': FlaskRequest.args.get('mask'),
                    'no_mask': FlaskRequest.args.get('no_mask'),
                    'incorrect_mask': FlaskRequest.args.get('incorrect_mask'),
                    'risky_distance': FlaskRequest.args.get('risky_distance')
                },
                'image': FlaskRequest.args.get('image')
            })
            return "OK"

        @app.route('/api/stream')
        def apiStream():
            resp = FlaskResponse(event_stream(), mimetype="text/event-stream", content_type="text/event-stream")
            resp.headers['Bypass-Tunnel-Reminder'] = True
            return resp

        @app.route("/api/teststream")
        def apiTestStream():
            return render_template("test_stream.html")

        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/imagestream")
        def imagestream():
            resp = FlaskResponse(encodeImageStream(), mimetype="multipart/x-mixed-replace; boundary=frame")
            resp.headers['Bypass-Tunnel-Reminder'] = True
            return resp

        @app.route("/image")
        def image():
            resp = FlaskResponse(streamQueue.get(True)['image'], mimetype="image/jpg", content_type="image/jpg")
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

        def processDataForDb():
            totalPerson = -1
            totalMask = -1
            totalNoMask = -1
            totalIncorrectMask = -1
            totalRiskyDistance = -1
            try:
                while True:
                    totalPersonTmp = od.getPersonDetection()
                    totalMaskTmp = od.getMaskDetection()
                    totalNoMaskTmp = od.getNoMaskDetection()
                    totalIncorrectMaskTmp = od.getIncorrectMaskDetection()
                    totalRiskyDistanceTmp = od.getRiskyDetection()
                    snapshotTime = timestampMillisec64()

                    if (totalPerson != totalPersonTmp) or (
                            totalMask != totalMaskTmp) or (
                            totalNoMask != totalNoMaskTmp) or (
                            totalIncorrectMask != totalIncorrectMaskTmp) or (
                            totalRiskyDistance != totalRiskyDistanceTmp):
                        streamQueue.put({
                            'event': {
                                'id': snapshotTime,
                                'person': totalPersonTmp,
                                'mask': totalMaskTmp,
                                'no_mask': totalNoMaskTmp,
                                'incorrect_mask': totalIncorrectMaskTmp,
                                'risky_distance': totalRiskyDistanceTmp
                            },
                            'image': encodeImage().tobytes(),
                        })
                        totalPerson = totalPersonTmp
                        totalMask = totalMaskTmp
                        totalIncorrectMask = totalIncorrectMaskTmp
                        totalNoMask = totalNoMaskTmp
                        totalRiskyDistance = totalRiskyDistanceTmp
                        log = {
                            'id': snapshotTime,
                            'person': totalPersonTmp,
                            'mask': totalMaskTmp,
                            'no_mask': totalNoMaskTmp,
                            'incorrect_mask': totalIncorrectMaskTmp,
                            'risky_distance': totalRiskyDistanceTmp
                        }
                        checkZeroes = totalPerson + totalMask + totalNoMask + totalIncorrectMask + totalRiskyDistance
                        if (checkZeroes != 0):
                            saveToDb(log)
                    time.sleep(delay(od.getFps()))
            except Exception as e:
                print(e)
                return

        imagefeedthread = Thread(target=appRun,
                                 name='feed_image', args=())
        imagefeedthread.daemon = True
        imagefeedthread.start()
        riskthread = Thread(target=processDataForDb,
                            name='process_data_for_db', args=())
        riskthread.daemon = True
        riskthread.start()

    def stop():
        try:
            print("[INFO] exiting...")
            if not od.getStopped():
                od.stop()
            sys.exit(0)
        except Exception as e:
            print('[INFO] forced exit! Exception:', e)
            sys.exit(2)

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
    ap.add_argument("-A", "--host", default='localhost',
                    help="host/address name for flask")
    ap.add_argument("-P", "--port", default="5000",
                    help="port number for flask")
    ap.add_argument("-u", "--use-gpu", type=int, default=0,
                    help="GPU mode")
    ap.add_argument("-n", "--netmode", type=int, default=0,
                    help="ai network mode, 0: person+mask, 1:mask, 2:person")
    ap.add_argument("-c", "--confidence", type=float, default=.51,
                    help="minimum probability to filter weak detections")
    # triangle similarity length unit in cm, euclidean length unit in pixel
    ap.add_argument("-D", "--distance", type=float, default=100,
                    help="distance for risky detection")
    # assuming that average human height is 165cm
    ap.add_argument("-T", "--objectHeight", type=float, default=165,
                    help="average object height")
    # equation 1:
    # Focal Lenght = (Object Height in pixel * Object Distance from camera) / Object Real Height
    # default is 615 ref: https://github.com/Subikshaa/Social-Distance-Detection-using-OpenCV
    # assuming distance from camera is ±250cm set to 385
    ap.add_argument("-F", "--focalLength", type=float, default=385,
                    help="focal length.")
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

    odParams = {
        'args': args,
        'classes4mask': ["mask", "incorrect", "no_mask"],
        'classes4person': ["person", "_1_", "_2_", "_3_", "_4_"],
        'url': None,
        'username': None,
        'password': None,
        'timeout': 10,
        'forceResize': True,
        'abcClip': .5
    }
    od = ObjectDetection(odParams)

    # View camera online in Barrigada, Guam, Barrigada Mayor'S Office http://www.insecam.org/en/view/882308/
    #url = "http://121.55.235.78/oneshotimage1"
    #username = "user"
    #password = "user"
    #url = "http://192.168.0.20/image.jpg"
    #od = ObjectDetection(classes=classes,args=args, url=url, maxWidth=maxWidth, maxHeight=maxHeight)
    # od = ObjectDetection(classes=classes, args=args, url=url, username=username,
    #                     password=password, timeout=timeout, maxWidth=maxWidth, maxHeight=maxHeight)

    od.start()

    try:
        imageStream(host=args['host'], port=args['port'], secure=False)
        time.sleep(1)

        while True:
            
            if OS_TYPE == WINDOWS:
                cv2.imshow('Image: In/Out', od.getFrameStack())
                #cv2.imshow('Image: In', od.getFrame())
                #cv2.imshow('Image: Out', od.getFrameDetection())
                if ord('q') == cv2.waitKey(10):
                    od.stop()
                    cv2.destroyAllWindows()
                    sys.exit(0)
            
            if not od.getStopped():
                sys.stdout.flush()
                if od.getNetMode() == 0:
                    sys.stdout.write("\r Detections => person: %d | risky: %d | mask: %d | incorrect_mask: %d | no_mask: %d | FPS: %.2f        \r" %
                                     (od.getPersonDetection(), od.getRiskyDetection(), od.getMaskDetection(), od.getIncorrectMaskDetection(), od.getNoMaskDetection(), od.getFps()))
                elif od.getNetMode() == 1:
                    sys.stdout.write("\r Detections => mask: %d | incorrect_mask: %d | no_mask: %d | FPS: %.2f        \r" %
                                     (od.getMaskDetection(), od.getIncorrectMaskDetection(), od.getNoMaskDetection(), od.getFps()))
                elif od.getNetMode() == 2:
                    sys.stdout.write("\r Detections => person: %d | risky: %d | FPS: %.2f       \r" % (
                        od.getPersonDetection(), od.getRiskyDetection(), od.getFps()))
            if od.getStopped():
                raise KeyboardInterrupt
            time.sleep(delay(od.getFps()))
    except KeyboardInterrupt:
        stop()


class ObjectDetection:
    def __init__(self, params):
        self.timeout = params['timeout']
        self.url = params['url']
        self.args = params['args']
        self.videoSrc = self.args['camera']
        self.forceResize = params['forceResize']
        self.username = params['username']
        self.password = params['password']
        self.maxWidth = self.args['maxWidth']
        self.maxHeight = self.args['maxHeight']
        netMode = 0 if (
            self.args['netmode'] > 2 or self.args['netmode'] < 0) else self.args['netmode']
        self.netMode = netMode
        self.stackSizeW = 510
        self.stackSizeH = 288
        self.abcClip = params['abcClip']
        if self.args["videotype"] == 'url':
            self.request = Request(self.url)
        # mask
        self.colors4mask = ''
        self.classes4mask = ''
        if isinstance(params['classes4mask'], (list, tuple, np.ndarray)):
            self.classes4mask = params['classes4mask']
        if isinstance(params['classes4mask'], (list, tuple, np.ndarray)):
            self.colors4mask = np.random.uniform(
                0, 255, size=(len(params['classes4mask']), 3))
        weights4mask = os.path.sep.join(
            [self.args["yolo"], "yolov3_mask.weights"])
        config4mask = os.path.sep.join([self.args["yolo"], "yolov3_mask.cfg"])
        self.net4mask = cv2.dnn.readNet(weights4mask, config4mask)
        if self.args["use_gpu"]:
            # set CUDA as the preferable backend and target
            print("[INFO] setting preferable backend and target to CUDA...")
            self.net4mask.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net4mask.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.maskLayerNames = self.net4mask.getLayerNames()
        self.maskOutputLayers = [self.maskLayerNames[i - 1] for i in self.net4mask.getUnconnectedOutLayers()]
        # --
        # person
        self.colors4person = ''
        self.classes4person = ''
        if isinstance(params['classes4person'], (list, tuple, np.ndarray)):
            self.classes4person = params['classes4person']
        if isinstance(params['classes4person'], (list, tuple, np.ndarray)):
            self.colors4person = np.random.uniform(
                0, 255, size=(len(params['classes4person']), 3))
        weights4person = os.path.sep.join(
            [self.args["yolo"], "yolov3_person.weights"])
        config4person = os.path.sep.join(
            [self.args["yolo"], "yolov3_person.cfg"])
        self.net4person = cv2.dnn.readNet(weights4person, config4person)
        if self.args["use_gpu"]:
            # set CUDA as the preferable backend and target
            print("[INFO] setting preferable backend and target to CUDA...")
            self.net4person.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net4person.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.personLayerNames = self.net4person.getLayerNames()
        self.personOutputLayers = [self.personLayerNames[i - 1] for i in self.net4person.getUnconnectedOutLayers()]
                                  
        # --
        #self.maskDetected = np.zeros((len(self.classes4mask)), dtype=int)
        #self.personDetected = np.zeros((len(self.classes4person)), dtype=int)
        self.withMaskDetected = 0
        self.noMaskDetected = 0
        self.incorrectMaskDetected = 0
        self.personDetected = 0
        self.riskyDistance = 0
        self.it = 0
        self.objCount = 0
        self.dstCount = 0
        self.frameskip = int(self.args["frameskip"])
        self.avgfps = 0
        self.frames = 0
        self.starttime = seconds()
        self.stopped = False
        self.vs = None
        self.outvideo = None
        self.frame = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameDetect = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameStack = np.hstack([imutils.resize(self.frame, self.stackSizeW),
                                     imutils.resize(self.frameDetect, self.stackSizeW)])
        time.sleep(1)

    def imageProcessing(self):
        def drawText(frame, text, startX=int(self.maxWidth * .025), startY=int(self.maxHeight * .05), textColor=(64, 255, 96),  fontSize=1, thickness=1):
            if thickness < 1:
                thickness = 1
            cv2.putText(frame, str(text), (int(startX), int(startY)),
                        cv2.FONT_HERSHEY_SIMPLEX, fontSize, (textColor), int(thickness))
            return frame

        def getAvgFps():
            fps = .1
            try:
                fps = .1 if self.frames is 0 else self.frames / (seconds() - self.starttime)
                if self.frames >= 128:
                    self.frames = 0
                    self.starttime = seconds()
            except Exception as e:
                return .1
            return fps

        try:
            self.starttime = seconds()
            while True:
                if self.stopped:
                    return
                else:
                    raw = None
                    if self.args["videotype"] == 'url':
                        socket.setdefaulttimeout(self.timeout)
                        request = Request(self.url)
                        if self.username != None and self.password != None:
                            base64string = base64.b64encode(
                                bytes('%s:%s' % (self.username, self.password), 'ascii'))
                            request.add_header(
                                "Authorization", "Basic %s" % base64string.decode('utf-8'))
                        with urlopen(request) as response:
                            imgArr = np.array(
                                bytearray(response.read()), dtype=np.uint8)
                            raw = cv2.imdecode(imgArr, cv2.IMREAD_COLOR)
                    else:
                        if self.args["videotype"] == 'file':
                            raw = self.vs.read()
                            if raw is None:
                                print('[INFO] No more frame present...')
                                self.stop()
                                continue
                        else:
                            if OS_TYPE == WINDOWS:
                                raw = self.vs.read()[1]
                            else:
                                raw = self.vs.read()

                    if isinstance(raw, (list, tuple, np.ndarray)):
                        (h, w) = raw.shape[:2]
                        #raw = cv2.GaussianBlur(raw, (3, 3), 0)
                        #raw = cv2.bilateralFilter(raw, 3, 30, 30)
                        if h > self.maxHeight or w > self.maxWidth or self.forceResize:
                            raw = cv2.resize(
                                raw, (self.maxWidth, self.maxHeight))
                        if int(self.args["frameskip"]) > 0:
                            if self.it % self.frameskip == 0:
                                self.frame = raw.copy()
                                self.frames += 1
                            else:
                                self.it += 1
                                self.frames += 1
                                continue
                        else:
                            self.frame = raw.copy()
                            self.frames += 1
                    else:
                        continue

                    self.it += 1
                    if self.args['abc'] != 'no':
                        try:
                            self.abcClip = float(self.args['abc'])
                        except ValueError:
                            pass
                        raw = self.abc(
                            raw, clip_hist_percent=self.abcClip)[0]
                        self.frame = raw.copy()
                    if self.netMode == 0:
                        maskFrame = self.maskDetection(raw)
                        personFrame = self.personDetection(raw)
                        self.frameDetect = cv2.addWeighted(
                            maskFrame, 0.5, personFrame, 0.5, 0.0)
                        cv2.putText(self.frameDetect, "Total person: %d, mask: %d, no_mask: %d" % (
                            self.personDetected, self.withMaskDetected, self.noMaskDetected),
                            (int(self.maxWidth * .025), int(self.maxHeight * .05)),
                            cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255),  1, cv2.LINE_AA)
                    elif self.netMode == 1:
                        self.frameDetect = self.maskDetection(raw)
                        cv2.putText(self.frameDetect, "Total mask: %d, no_mask: %d" % (
                            self.withMaskDetected, self.noMaskDetected), (
                            int(self.maxWidth * .025), int(self.maxHeight * .05)),
                            cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255),  1, cv2.LINE_AA)
                    elif self.netMode == 2:
                        self.frameDetect = self.personDetection(raw)
                        # cv2.putText(self.frameDetect, "Total person: %d" % (self.personDetected[0]),
                        cv2.putText(self.frameDetect, "Total person: %d" % (self.personDetected),
                                    (int(self.maxWidth * .025),
                                     int(self.maxHeight * .05)),
                                    cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255),  1, cv2.LINE_AA)
                    try:
                        self.frameStack = np.hstack([imutils.resize(self.frame, self.stackSizeW),
                                                     imutils.resize(self.frameDetect, self.stackSizeW)])
                    except:
                        pass
                    self.avgfps = getAvgFps()
                    if self.outvideo != None:
                        self.outvideo.write(self.frameDetect)

                    time.sleep(.008333)

        except HTTPError as e:
            print('[ERROR] The server couldn\'t fulfill the request.')
            print('[ERROR] Error code: ', e.code)
            self.frameStack = drawText(self.frameStack,
                                       e.code, (384 * .025), (680 * .025), (96, 64, 255), .3)
        except URLError as e:
            print('[ERROR] We failed to reach a server.')
            print('[ERROR] Reason: ', e.reason)
            self.frameStack = drawText(self.frameStack,
                                       e.reason, (384 * .025), (680 * .025), (96, 64, 255), .3)
        except Exception:
            print('[ERROR] ', traceback.format_exc())
            self.frameStack = drawText(self.frameStack, traceback.format_exc(),
                                       (384 * .025), (680 * 0.025), (96, 64, 255), .3)

    def maskDetection(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(
            frame, (416, 416)), 1 / 255.0, (416, 416),
            swapRB=True, crop=False)
        # blob = cv2.dnn.blobFromImage(cv2.resize(
        #    frame, 300, 300), 0.007843, (300, 300), 127.5)
        self.net4mask.setInput(blob)
        layerOutputs = self.net4mask.forward(self.maskOutputLayers)
        classIDs = []
        confidences = []
        boxes = []
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > float(self.args["confidence"]):
                    # Object detected
                    center_x = int(detection[0] * w)
                    center_y = int(detection[1] * h)
                    wx = int(detection[2] * w)
                    hx = int(detection[3] * h)

                    # Rectangle coordinates
                    x = int(center_x - wx / 2)
                    y = int(center_y - hx / 2)

                    boxes.append([x, y, wx, hx])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # Non-maximum Suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        #colors = np.random.uniform(0, 255, size=(len(self.classes4mask), 3))
        colors = ((0, 255, 0), (0, 255, 255), (0, 0, 255))
        detections = np.zeros((len(self.classes4mask)), dtype=int)
        for i in range(len(boxes)):
            if i in indexes:
                detections[classIDs[i]] += 1
                x, y, wx, hx = boxes[i]
                #label = str(self.classes4mask[classIDs[i]])
                label = str(f'{self.classes4mask[classIDs[i]]}: {confidences[i]:.2f}').replace('0.', '.')
                color = colors[classIDs[i]]
                cv2.rectangle(frame, (x, y), (x + wx, y + hx), color, 2)
                cv2.putText(frame, label, (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, .5, color, 1)

        #self.maskDetected = detections
        self.withMaskDetected = int(detections[0])
        self.incorrectMaskDetected = int(detections[1])
        self.noMaskDetected = int(detections[2])

        return frame

    def personDetection(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(
            frame, (416, 416)), 1 / 255.0, (416, 416),
            swapRB=True, crop=False)
        # blob = cv2.dnn.blobFromImage(cv2.resize(
        #    frame, 300, 300), 0.007843, (300, 300), 127.5)
        self.net4person.setInput(blob)
        layerOutputs = self.net4person.forward(self.personOutputLayers)
        classIDs = []
        confidences = []
        boxes = []
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > float(self.args["confidence"]):
                    # Object detected
                    center_x = int(detection[0] * w)
                    center_y = int(detection[1] * h)
                    wx = int(detection[2] * w)
                    hx = int(detection[3] * h)

                    # Rectangle coordinates
                    x = int(center_x - wx / 2)
                    y = int(center_y - hx / 2)

                    boxes.append([x, y, wx, hx])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # Non-maximum Suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, .5, .4)
        #colors = np.random.uniform(0, 255, size=(len(self.classes4person), 3))
        colors = ((255, 0, 0),)
        #detections = np.zeros((len(self.classes4person)), dtype=int)
        persons = []
        labels = []
        for i in range(len(boxes)):
            if i in indexes:
                #detections[classIDs[i]] += 1
                x, y, wx, hx = boxes[i]
                if self.classes4person[classIDs[i]] == self.classes4person[0]:
                    persons.append([x, y, x + wx, y + hx])
                    #label = str(self.classes4person[classIDs[i]])
                    label = str(f'{self.classes4person[classIDs[i]]}: {confidences[i]:.2f}').replace('0.', '.')
                    labels.append(label)
                    color = colors[classIDs[i]]
                    cv2.rectangle(frame, (x, y), (x + wx, y + hx), color, 2)
                    cv2.putText(frame, label, (x, y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, .5, color, 1)

        #self.personDetected = detections
        self.personDetected = len(persons)
        midPoints = [self.getMidPoint(frame, persons, i)
                     for i in range(self.personDetected)]
        distances = self.getDistance(midPoints, self.personDetected, frame=frame, frameLog=True)
        #distances = self.getDistance(midPoints, self.personDetected, frame)
        person1, person2, _ = self.getClosest(
            distances, self.personDetected, self.args['distance'])
        frame, self.riskyDistance = self.getRiskyDistance(
            frame, persons, person1, person2, midPoints, labels)

        return frame

    def getMidPoint(self, frame, persons, idx):
        # get the coordinates
        (startX, startY, endX, endY) = persons[idx]
        cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 1)

        # compute bottom center of bbox
        xMid = int((startX + endX) / 2)
        yMid = int((startY + endY) / 2)
        height = int((yMid - startY) * 2)
        midPoint = {
            'idx': idx,
            'point': (xMid, yMid),
            'height': height
        }

        cv2.circle(frame, midPoint['point'], 5, (255, 0, 0), -1)
        cv2.putText(frame, str(idx), midPoint['point'],
                    cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA)

        return midPoint

    # simple distance in pixel unit
    def getDistanceSimple(self, midPoints, totalPerson, frame=None):
        dist = np.zeros((totalPerson, totalPerson))
        for i in range(totalPerson):
            for j in range(i + 1, totalPerson):
                if i != j:
                    # distance using euclidean / pythagorean distance
                    dst = distance.euclidean(midPoints[i]['point'], midPoints[j]['point'])
                    dist[i][j] = dst
                    self.dstCount += 1
                    print(
                        f'frame no: {self.dstCount}',
                        f'dist: {dst:.2f}px'
                    )
                    if not frame is None:
                        cv2.putText(frame, str(f'frame: {self.dstCount} dst: {dst:.2f}cm'),
                            (int(self.maxWidth * .025), int(self.maxHeight * .1)),
                            cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1)
        return dist
    
    def getDistance(self, midPoints, totalPerson, frame=None, log=True, frameLog=False):
        # distance using triangle similarity
        # equation 1:
        # Focal Lenght = (Object Height in pixel * Object Distance from camera) / Object Real Height
        # equation 2:
        # Object Distance from camera = (Object Real Height * Focal Length) / Object Height in pixel
        dist = np.zeros((totalPerson, totalPerson))
        if log:
            tWidth = int(self.maxWidth * .025)
            tHeightDst = int(self.maxHeight * .1)
            hGap = int(self.maxHeight * .05)
            if frameLog:
                tDstColor = (255,0,143)
                tObjColor = (20,150,255)
        for i in range(totalPerson):
            for j in range(i + 1, totalPerson):
                if i != j:
                    # pos 1:i
                    pos1ToCam = (self.args['objectHeight'] * self.args['focalLength']) / midPoints[i]['height']
                    midPoint1_cm = (
                        ( (midPoints[i]['point'][0] * pos1ToCam) / self.args['focalLength'] ), # X
                        ( (midPoints[i]['point'][1] * pos1ToCam) / self.args['focalLength'] ), # Y
                    )

                    # pos 2:j
                    pos2ToCam = (self.args['objectHeight'] * self.args['focalLength']) / midPoints[j]['height']
                    midPoint2_cm = (
                        ( (midPoints[j]['point'][0] * pos2ToCam) / self.args['focalLength'] ),
                        ( (midPoints[j]['point'][1] * pos2ToCam) / self.args['focalLength'] ),
                    )

                    # dst = (a^2 + b^2) ^.5: pythagorean theorem
                    X = midPoint1_cm[0] - midPoint2_cm[0]
                    Y = midPoint1_cm[1] - midPoint2_cm[1]
                    dstA = sqrt(
                        pow( X, 2 ) +
                        pow( Y, 2 )
                    )
                    dstB = pos1ToCam - pos2ToCam
                    dstC = sqrt(
                        pow( dstA, 2 ) +
                        pow( dstB, 2 )
                    )
                    dist[i][j] = dstC
                    
                    self.dstCount += 1
                    
                    if log:
                        print(
                            f"\nobj {midPoints[i]['idx']} to obj {midPoints[j]['idx']}:",
                            f"{midPoints[i]['idx']} to cam: {pos1ToCam:.2f}cm",
                            f"{midPoints[j]['idx']} to cam: {pos2ToCam:.2f}cm",
                            f'dist: {dstC:.2f}cm; '
                        )

                    if not frame is None and frameLog:
                        cv2.putText(frame,
                            f"\nobj {midPoints[i]['idx']} to obj {midPoints[j]['idx']}: {self.dstCount} dst: {dstC:.2f}cm",
                            (tWidth, tHeightDst),
                            cv2.FONT_HERSHEY_DUPLEX, .5, tDstColor, 1)
                        tHeightDst = tHeightDst + hGap

        tHeightObj = tHeightDst + int(hGap * .5)
        for i in range(totalPerson):
            self.objCount += 1
            posObjToCam = (self.args['objectHeight'] * self.args['focalLength']) / midPoints[i]['height']
            if log:
                objText = str(f"\ncnt: {self.objCount} obj: {midPoints[i]['idx']} dst: {posObjToCam:.2f}cm; ")
                print(objText)
            if not frame is None and frameLog:
                cv2.putText(frame, objText,
                    (tWidth, tHeightObj),
                    cv2.FONT_HERSHEY_DUPLEX, .5, tObjColor, 1)
                tHeightObj = tHeightObj + hGap
        return dist
    
    def getClosest(self, distances, totalPerson, thresh):
        person1 = []
        person2 = []
        dist = []
        for i in range(totalPerson):
            for j in range(i, totalPerson):
                if((i != j) & (distances[i][j] <= thresh)):
                    person1.append(i)
                    person2.append(j)
                    dist.append(distances[i][j])
        return person1, person2, dist

    def getRiskyDistance(self, frame, persons, person1, person2, midPoints, labels):
        risky = np.unique(person1 + person2)
        for i in risky:
            (startX, startY, endX, endY) = persons[i]
            cv2.rectangle(frame, (startX, startY),
                          (endX, endY), (0, 0, 255), 2)
            cv2.circle(frame, midPoints[i]['point'], 5, (0, 0, 255), -1)
            cv2.putText(frame, str(i),
                        midPoints[i]['point'], cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, labels[i], (startX, startY - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 1)
        return frame, len(risky)

    def abc(self, image, clip_hist_percent=.5):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Calculate grayscale histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_size = len(hist)

        # Calculate cumulative distribution from the histogram
        accumulator = []
        accumulator.append(float(hist[0]))
        for index in range(1, hist_size):
            accumulator.append(accumulator[index - 1] + float(hist[index]))

        # Locate points to clip
        maximum = accumulator[-1]
        clip_hist_percent *= (maximum/100.0)
        clip_hist_percent /= 2.0

        # Locate left cut
        minimum_gray = 0
        while accumulator[minimum_gray] < clip_hist_percent:
            minimum_gray += 1

        # Locate right cut
        maximum_gray = hist_size - 1
        while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
            maximum_gray -= 1

        # Calculate alpha and beta values
        alpha = 255 / (maximum_gray - minimum_gray)
        beta = -minimum_gray * alpha

        auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return (auto_result, alpha, beta)

    def fixResizeAspectRatio(self, w, h):
        if w > h:
            h = int(h / int(w / self.maxWidth))
            return (self.maxWidth, h)
        if h > w:
            w = int(w / int(h / self.maxHeight))
            return (w, self.maxHeight)
        
        return (self.maxWidth, self.maxHeight)
    
    def getFps(self):
        if self.avgfps == 0:
            return .1
        return self.avgfps

    def getFrameDetection(self, resize=False, w=320, h=128):
        if resize:
            return cv2.resize(self.frameDetect, (w, h))
        return self.frameDetect

    def getFrame(self):
        return self.frame

    def getFrameStack(self):
        return self.frameStack

    def getMaskDetection(self):
        return self.withMaskDetected

    def getNoMaskDetection(self):
        return self.noMaskDetected
    
    def getIncorrectMaskDetection(self):
        return self.incorrectMaskDetected

    def getPersonDetection(self):
        # return self.personDetected[0]
        return self.personDetected

    def getRiskyDetection(self):
        return self.riskyDistance

    def getNetMode(self):
        return self.netMode

    def setNetMode(self, netMode):
        self.netMode = netMode

    def getStopped(self):
        return self.stopped

    def start(self):
        print('[INFO] Starting object detection...:')
        if self.args["video"] == 'stream':
            if OS_TYPE == WINDOWS:
                self.vs = cv2.VideoCapture(self.videoSrc, cv2.CAP_DSHOW)
                try:
                    self.vs.set(cv2.CAP_PROP_FRAME_WIDTH, self.maxWidth)
                    self.vs.set(cv2.CAP_PROP_FRAME_HEIGHT, self.maxHeight)
                except Exception as e:
                    print(e)
            else:
                self.vs = VideoStream(self.videoSrc).start()
            time.sleep(.5)
        elif self.args["videotype"] == 'file':
            self.vs = FileVideoStream(self.args["video"]).start()
            time.sleep(.5)
        if OS_TYPE == WINDOWS and self.args["videotype"] != 'file':
            _img = self.vs.read()[1]
        else:
            _img = self.vs.read()

        if self.args["videotype"] == 'file':
            if not isinstance(_img, (list, tuple, np.ndarray)):
                if _img is None:
                    print('[ERROR] video stream error NoneType.')
                    sys.exit(2)
            if not self.vs.more:
                print('[ERROR] video stream error no frame.')
                sys.exit(2)
        (h, w) = _img.shape[:2]
        (self.maxWidth, self.maxHeight) = self.fixResizeAspectRatio(w, h)
        print('[INFO] Video size set to:', self.maxWidth, self.maxHeight)
        if (h > self.maxHeight or w > self.maxWidth) and self.forceResize:
            _img = cv2.resize(
                _img, (self.maxWidth, self.maxHeight))
            (h, w) = _img.shape[:2]
        _fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        outputPath = os.path.abspath(os.path.dirname(
            os.path.abspath(__file__)) + '/output/videos') + '/'
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        videoOutputName = f"{self.netMode}_{os.path.splitext(os.path.basename(self.args['video']))[0]}_yolov3_output.mp4"
        print(outputPath, videoOutputName)
        if self.args['saveVideo'] != 'no':
            self.outvideo = cv2.VideoWriter(outputPath +  # str(time.strftime('%Y-%m-%d_%H.%M.%S')) +
                                        videoOutputName
                                        , _fourcc, 30.0, (w, h))
        streamthread = Thread(target=self.imageProcessing,
                              name='FetchImageUrl', args=())
        streamthread.daemon = True
        streamthread.start()
        return self

    def stop(self):
        self.stopped = True
        if self.vs != None:
            if self.args["videotype"] != 'file':
                if OS_TYPE == WINDOWS:
                    self.vs.release()
                else:
                    self.vs.stop()
        if self.outvideo != None:
            self.outvideo.release()
        cv2.destroyAllWindows()
        print('[INFO] Object detection stopped.')


if __name__ == '__main__':
    main()
