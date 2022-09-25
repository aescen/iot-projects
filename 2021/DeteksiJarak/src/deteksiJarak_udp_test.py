#!/usr/bin/python3

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from threading import Thread, Lock
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from scipy.spatial import distance
from firebase import Firebase #https://pypi.org/project/firebase/ : sudo pip3 install firebase python_jwt gcloud sseclient
import websockets
import pymysql
import sys
import time
import base64
import asyncio
import socket
import struct
import math
import imutils
import argparse
import traceback
import cv2
import numpy as np
import os
import json
import pyttsx3
from datetime import timedelta, datetime as dt
from queue import Queue
from flask import request as FlaskRequest
from flask import Response as FlaskResponse
from flask import Flask, render_template, jsonify
from flask_cors import CORS as FlaskCORS
import logging
log = logging.getLogger('werkzeug')
# error only log
# log.setLevel(logging.ERROR)
# disable log
log.disabled = True

LOCK = Lock()

MP3_WARNING = 'rekaman.mp3'
RASPBIAN = 'raspbian'
LINUX = 'linux'
MACOS = 'macos'
WINDOWS = 'windows'
OS_TYPE = ''
STR_MSG = 'Mohon Perhatian! Untuk menggunakan masker dan jaga jarak minimal 1 meter'

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
    def playAudio(fn):
        if OS_TYPE == RASPBIAN:
            os.system('mpg123 ' + fn)
        else:
            os.system('tskill vlc')
            os.system('vlc -I cli --no-repeat --no-loop ' + fn)

    def imageStream(host='0.0.0.0', port='5000', udpPort='9000', debug=False, secure=False):
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
        # Set up websocket
        frameSegment = FrameSegment(host, udpPort)
        
        # Database setup..
        isFirebase = False
        firebasDb = None
        CONN = None
        CC = None
        if isFirebase:
            config = {
                #
            }
            firebase = Firebase(config)
            firebaseDb = firebase.database()
        else:
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
                exit()

        def getDate(ts):
            baseDatetime = dt( 1970, 1, 1 )
            delta = timedelta( 0, 0, 0, ts )
            targetDate = baseDatetime + delta
            t = dt(targetDate.date().year, targetDate.date().month, targetDate.date().day)
            targetDateTrunc = dt.utcfromtimestamp(t.timestamp() + 25200.0)
            return {
                'date': targetDate.strftime('%Y-%m-%d'),
                'clock': targetDate.strftime('%H:%M:%S'),
                'seconds': targetDateTrunc.timestamp(),
                'millis': targetDateTrunc.timestamp() * 1000,
                'dt': targetDate,
                'dtt': targetDateTrunc,
            }
        
        def updateEventDb(event):
            if isFirebase:
                firebaseDb.child("Aisya").child("events").update(event)
        
        def saveToDb(log):
            if isFirebase:
                date = dt.now().strftime('%Y-%m-%d')
                value = {
                    'id': log['id'],
                    'deteksi': log['deteksi'],
                    'riskan': log['riskan']
                }
                firebaseDb.child("Aisya").child("logs").push(value)
            else:
                try:
                    result = '''
                                INSERT INTO `sideteksilog` (`id`, `deteksi`, `riskan`) VALUES ('{0}', '{1}', '{2}')
                            '''.format(log['id'], log['deteksi'], log['riskan'])
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

        def udpStream():
            frameSegment.run()
            print('[INFO] UDP server running on: ws://%s:%s' % (host, udpPort))
            try:
                while True:
                    frameSegment.udpFrame(od.getFrameDetection())
                    time.sleep(delay(od.getFps()))
            except Exception as e:
                print(e)
                return
        
        def eventStream():
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
                    'person': FlaskRequest.args.get('person'),
                    'mask': FlaskRequest.args.get('mask'),
                    'no_mask': FlaskRequest.args.get('no_mask'),
                    'risky': FlaskRequest.args.get('risky')
                },
                'image': FlaskRequest.args.get('image')
            })
            return "OK"

        @app.route('/api/stream')
        def apiStream():
            resp = FlaskResponse(eventStream(), mimetype="text/event-stream", content_type="text/event-stream")
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

        def riskCheck():
            totalPerson = -1
            totalMask = -1
            totalNoMask = -1
            totalRisky = -1
            try:
                while True:
                    totalPersonTmp = od.getPersonDetection()
                    totalMaskTmp = od.getMaskDetection()
                    totalNoMaskTmp = od.getNoMaskDetection()
                    totalRiskyTmp = od.getTotalRisky()

                    if (totalPerson != totalPersonTmp) or (
                            totalMask != totalMaskTmp) or (
                            totalNoMask != totalNoMaskTmp) or (
                            totalRiskyTmp != totalRisky):
                        streamQueue.put({
                            'event': {
                                'person': totalPersonTmp,
                                'mask': totalMaskTmp,
                                'no_mask': totalNoMaskTmp,
                                'risky': totalRiskyTmp
                            },
                            'image': encodeImage().tobytes(),
                        })
                        totalPerson = totalPersonTmp
                        totalMask = totalMaskTmp
                        totalNoMask = totalNoMaskTmp
                        totalRisky = totalRiskyTmp
                        log = {
                            'id': timestampMillisec64(),
                            'deteksi': totalPerson,
                            'riskan': totalRisky
                        }
                        event = {
                            'person': totalPersonTmp,
                            'mask': totalMaskTmp,
                            'no_mask': totalNoMaskTmp,
                            'risky': totalRiskyTmp
                        }
                        updateEventDb(event);
                        saveToDb(log)
                    time.sleep(delay(od.getFps()))
            except Exception as e:
                print(e)
                return

        udpstreamthread = Thread(target=udpStream,
                                 name='udp_stream', args=())
        udpstreamthread.daemon = True
        udpstreamthread.start()
        imagefeedthread = Thread(target=appRun,
                                 name='feed_image', args=())
        imagefeedthread.daemon = True
        imagefeedthread.start()
        riskthread = Thread(target=riskCheck,
                            name='risk_check', args=())
        riskthread.daemon = True
        riskthread.start()
    
    def delay(fps, x=2):
        if fps < 1:
            return 1
        return 1 / (fps * x)

    def stop():
        try:
            print("[INFO] exiting...")
            od.stop()
            cv2.destroyAllWindows()
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
    ap.add_argument("-S", "--saveVideo", default="no",
                    help="Save video?")
    ap.add_argument("-H", "--host", default='localhost',
                    help="host name for flask")
    ap.add_argument("-P", "--port", default="5000",
                    help="port number for flask")
    ap.add_argument("-u", "--use-gpu", type=int, default=0,
                    help="GPU mode")
    ap.add_argument("-N", "--netmode", type=int, default=0,
                    help="ai network mode, 0: person+mask, 1:mask, 2:person")
    ap.add_argument("-c", "--confidence", type=float, default=.51,
                    help="minimum probability to filter weak detections")
    ap.add_argument("-d", "--distance", type=float, default=100,
                    help="distance for risky detection")
    ap.add_argument("-f", "--frameskip", type=int, default=3,
                    help="frames to skip(default: 3)")
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
        'classes4mask': ["mask", "?", "no_mask"],
        'classes4person': ["person", "_1_", "_2_", "_3_", "_4_"],
        'url': None,
        'username': None,
        'password': None,
        'timeout': 10,
        'maxWidth': 640,
        'maxHeight': 480,
        'forceResize': False,
        'abcClip': .5
    }
    od = ObjectDetection(odParams)
    tts = TextToSpeech()

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
            '''
            if OS_TYPE == WINDOWS:
                cv2.imshow('Image: In/Out', od.getFrameStack())
                #cv2.imshow('Image: In', od.getFrame())
                #cv2.imshow('Image: Out', od.getFrameDetection())
                if ord('q') == cv2.waitKey(10):
                    od.stop()
                    cv2.destroyAllWindows()
                    sys.exit(0)
            '''
            
            if od.getTotalRisky() > 0:
                tts.say(STR_MSG)

            sys.stdout.flush()
            if od.getNetMode() == 0:
                sys.stdout.write("\r Detections => person: %d | mask: %d | no_mask: %d | FPS: %.2f       \r" %
                                 (od.getPersonDetection(), od.getMaskDetection(), od.getNoMaskDetection(), od.getFps()))
            elif od.getNetMode() == 1:
                sys.stdout.write("\r Detections => mask: %d | no_mask: %d | FPS: %.2f       \r" %
                                 (od.getMaskDetection(), od.getNoMaskDetection(), od.getFps()))
            elif od.getNetMode() == 2:
                sys.stdout.write("\r Detections => person: %d | FPS: %.2f       \r" % (
                    od.getPersonDetection(), od.getFps()))

            time.sleep(delay(od.getFps()))

    except KeyboardInterrupt:
        stop()    

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 125)
        #self.engine.setProperty('name', voices[0].id)
        self.engine.setProperty('volume', 1.0)
        self.isSpeaking = False
        self.text = 'Text To Speach'

    def say(self, text):
        self.text = text
        if not self.isSpeaking:
            saythread = Thread(target=self.sayThread,
                                  name='SayThread', args=())
            saythread.daemon = True
            saythread.start()
        else:
            #print('[INFO] TTS is still speaking. Try again later.')
            pass

    def sayThread(self):
        self.isSpeaking = True
        self.engine.say(self.text)
        self.engine.runAndWait()
        self.isSpeaking = False

class FrameSegment:
    """ 
    Object to break down image frame segment
    if the size of image exceed maximum datagram size 
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 37]
        self.serve_queue = Queue()
        self.stop = True
    
    async def serve(self, websocket, path):
        while True:
            with LOCK:
                q = None
                try:
                    q = self.serve_queue.get(True)
                except Queue.Empty:
                    continue
                data = q['data']
                size = q['size']
                count = q['count']
                pos_start = 0
                while count:
                    pos_end = min(size, pos_start + self.MAX_IMAGE_DGRAM)
                    #payload = struct.pack("B", count) + data[pos_start:pos_end]
                    payload = json.dumps({
                        'count': count,
                        'segment':  base64.standard_b64encode(data[pos_start:pos_end]).decode('utf-8')
                    })
                    await websocket.send(payload)
                    pos_start = pos_end
                    count -= 1

    def run(self):
        def start():
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.start_server = websockets.serve(self.serve, self.addr, self.port, loop=self.loop)
            self.loop.run_until_complete(self.start_server)
            self.loop.run_forever()
        self.stop = False
        framesegmentthread = Thread(target=start, name='frame_segment', args=())
        framesegmentthread.daemon = True
        framesegmentthread.start()
    
    def stop():
        self.stop = True

    def udpFrame(self, img, quality=37):
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        #compress_img = cv2.imencode('.png', img)[1]
        compress_img = cv2.imencode('.jpg', img, self.encode_param)[1]
        data = compress_img.tobytes()
        size = len(data)
        count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
        self.serve_queue.put({
            'data': data,
            'size': size,
            'count': count
        })

class ObjectDetection:
    def __init__(self, params):
        self.timeout = params['timeout']
        self.url = params['url']
        self.args = params['args']
        self.videoSrc = self.args['camera']
        self.forceResize = params['forceResize']
        self.username = params['username']
        self.password = params['password']
        self.maxWidth = params['maxWidth']
        self.maxHeight = params['maxHeight']
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
        self.maskOutputLayers = [self.maskLayerNames[i[0] - 1]
                                 for i in self.net4mask.getUnconnectedOutLayers()]
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
        self.personOutputLayers = [self.personLayerNames[i[0] - 1]
                                   for i in self.net4person.getUnconnectedOutLayers()]
        # --
        #self.maskDetected = np.zeros((len(self.classes4mask)), dtype=int)
        #self.personDetected = np.zeros((len(self.classes4person)), dtype=int)
        self.withMaskDetected = 0
        self.noMaskDetected = 0
        self.personDetected = 0
        self.totalRisky = 0
        self.it = 0
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
        self.frameStack = np.hstack([imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW),
                                     imutils.resize(self.frameDetect, height=self.stackSizeH, width=self.stackSizeW)])
        time.sleep(.5)

    def imageProcessing(self):
        def drawText(frame, text, startX=int(self.maxWidth * .025), startY=int(self.maxHeight * .05), textColor=(64, 255, 96),  fontSize=1, thickness=1):
            if thickness < 1:
                thickness = 1
            cv2.putText(frame, str(text), (int(startX), int(startY)),
                        cv2.FONT_HERSHEY_DUPLEX, fontSize, (textColor), int(thickness))
            return frame

        def getAvgFps():
            fps = .1 if self.frames == 0 else self.frames / (seconds() - self.starttime)
            if self.frames >= 128:
                self.frames = 0
                self.starttime = seconds()
            
            return fps

        try:
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
                            raw = imutils.resize(
                                raw, width=self.maxWidth, height=self.maxHeight)
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
                            cv2.FONT_HERSHEY_DUPLEX, .5, (255, 255, 255),  1)
                    elif self.netMode == 1:
                        self.frameDetect = self.maskDetection(raw)
                        cv2.putText(self.frameDetect, "Total mask: %d, no_mask: %d" % (
                            self.withMaskDetected, self.noMaskDetected), (
                            int(self.maxWidth * .025), int(self.maxHeight * .05)),
                            cv2.FONT_HERSHEY_DUPLEX, .5, (255, 255, 255),  1)
                    elif self.netMode == 2:
                        self.frameDetect = self.personDetection(raw)
                        # cv2.putText(self.frameDetect, "Total person: %d" % (self.personDetected[0]),
                        cv2.putText(self.frameDetect, "Total person: %d" % (self.personDetected),
                                    (int(self.maxWidth * .025),
                                     int(self.maxHeight * .05)),
                                    cv2.FONT_HERSHEY_DUPLEX, .5, (255, 255, 255),  1)
                    try:
                        self.frameStack = np.hstack([imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW),
                                                     imutils.resize(self.frameDetect, height=self.stackSizeH, width=self.stackSizeW)])
                    except:
                        pass
                    self.avgfps = getAvgFps()
                    if self.outvideo != None:
                        self.outvideo.write(self.frameDetect)
                    if self.args["videotype"] == 'file':
                        if not self.vs.more:
                            print('[INFO] No more frame present...')
                            # self.stop()
                            exit()

                    time.sleep(.008333333333333333)

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
        blob = cv2.dnn.blobFromImage(imutils.resize(
            frame, 416, 416), 1 / 255.0, (416, 416),
            swapRB=True, crop=False)
        # blob = cv2.dnn.blobFromImage(imutils.resize(
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
                label = str("%.2f" % confidences[i]).replace('0.', '.')
                color = colors[classIDs[i]]
                cv2.rectangle(frame, (x, y), (x + wx, y + hx), color, 2)
                cv2.putText(frame, label, (x, y - 5),
                            cv2.FONT_HERSHEY_DUPLEX, .5, color, 1)

        #self.maskDetected = detections
        self.withMaskDetected = int(detections[0])
        self.noMaskDetected = int(detections[2])

        return frame

    def personDetection(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(imutils.resize(
            frame, 416, 416), 1 / 255.0, (416, 416),
            swapRB=True, crop=False)
        # blob = cv2.dnn.blobFromImage(imutils.resize(
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
                    label = str("%.2f" % confidences[i]).replace('0.', '.')
                    labels.append(label)
                    color = colors[classIDs[i]]
                    cv2.rectangle(frame, (x, y), (x + wx, y + hx), color, 2)
                    cv2.putText(frame, label, (x, y - 5),
                                cv2.FONT_HERSHEY_DUPLEX, .5, color, 1)

        #self.personDetected = detections
        self.personDetected = len(persons)
        midPoints = [self.getMidPoint(frame, persons, i)
                     for i in range(self.personDetected)]
        distances = self.getDistance(midPoints, self.personDetected)
        person1, person2, _ = self.getClosest(
            distances, self.personDetected, self.args['distance'])
        frame, self.totalRisky = self.getRiskyDistance(
            frame, persons, person1, person2, midPoints, labels)

        return frame

    def getMidPoint(self, frame, persons, idx):
        # get the coordinates
        (startX, startY, endX, endY) = persons[idx]
        cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 1)

        # compute bottom center of bbox
        xMid = int((startX + endX) / 2)
        yMid = int((startY + endY) / 2)
        midPoint = (xMid, yMid)

        cv2.circle(frame, midPoint, 5, (255, 0, 0), -1)
        cv2.putText(frame, str(idx), midPoint,
                    cv2.FONT_HERSHEY_DUPLEX, .5, (255, 255, 255), 1)

        return midPoint

    def getDistance(self, midpoints, totalPerson):
        dist = np.zeros((totalPerson, totalPerson))
        for i in range(totalPerson):
            for j in range(i + 1, totalPerson):
                if i != j:
                    dst = distance.euclidean(midpoints[i], midpoints[j])
                    dist[i][j] = dst
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
            cv2.circle(frame, midPoints[i], 5, (0, 0, 255), -1)
            cv2.putText(frame, str(i),
                        midPoints[i], cv2.FONT_HERSHEY_DUPLEX, .5, (255, 255, 255), 1)
            cv2.putText(frame, labels[i], (startX, startY - 5),
                        cv2.FONT_HERSHEY_DUPLEX, .5, (0, 0, 255), 1)
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

    def getFps(self):
        if self.avgfps == 0:
            return .1
        return self.avgfps

    def getFrameDetection(self, resize=False, w=320, h=128):
        if resize:
            return imutils.resize(self.frameDetect, height=h, width=w)
        return self.frameDetect

    def getFrame(self):
        return self.frame

    def getFrameStack(self):
        return self.frameStack

    def getMaskDetection(self):
        return self.withMaskDetected

    def getNoMaskDetection(self):
        return self.noMaskDetected

    def getPersonDetection(self):
        # return self.personDetected[0]
        return self.personDetected

    def getTotalRisky(self):
        return self.totalRisky

    def getNetMode(self):
        return self.netMode

    def setNetMode(self, netMode):
        self.netMode = netMode

    def start(self):
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
            if _img is None:
                print('[ERROR] video stream error NoneType.')
                exit()
            if not self.vs.more:
                print('[ERROR] video stream error no frame.')
                exit()
        (h, w) = _img.shape[:2]
        if h > self.maxHeight or w > self.maxWidth or self.forceResize:
            _img = imutils.resize(
                _img, width=self.maxWidth, height=self.maxHeight)
            (h, w) = _img.shape[:2]
        _fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        outputPath = os.path.abspath(os.path.dirname(
            os.path.abspath(__file__)) + '/output/videos') + '/'
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        if self.args['saveVideo'] != 'no':
            self.outvideo = cv2.VideoWriter(outputPath +  # str(time.strftime('%Y-%m-%d_%H.%M.%S')) +
                                        str(self.netMode) + '_' + os.path.basename(self.args['video']) + '_yolov3_output.mp4', _fourcc, 30.0, (w, h))  # 30.0 fps
        print('[INFO] Starting object detection...')
        streamthread = Thread(target=self.imageProcessing,
                              name='FetchImageUrl', args=())
        streamthread.daemon = True
        streamthread.start()
        return self

    def stop(self):
        self.stopped = True
        self.frame = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameDetect = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameStack = np.hstack([imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW),
                                     imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW)])
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
