#!/usr/bin/python3

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

        def saveToDb(log):
            try:
                result = '''
                            UPDATE
                              `pantauayam`
                            SET
                              `ayam_mati` = '{0}'
                            WHERE
                              `pantauayam`.`id` = '0';
                        '''.format(
                            log['ayam_mati'])
                CC.execute(result)
                CONN.commit()
            except pymysql.err.InternalError as msg:
                print("Command skipped: ", msg)

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
            totalAyamMati = -1
            try:
                while True:
                    totalAyamMatiTmp = od.getAyamMatiDetection()
                    snapshotTime = timestampMillisec64()

                    if (totalAyamMati != totalAyamMatiTmp):
                        streamQueue.put({
                            'event': {
                                'id': snapshotTime,
                                'ayam_mati': totalAyamMatiTmp
                            },
                            'image': encodeImage().tobytes(),
                        })
                        totalAyamMati = totalAyamMatiTmp
                        log = {
                            'id': snapshotTime,
                            'ayam_mati': totalAyamMatiTmp,
                        }


                        saveToDb(log)
                    time.sleep(delay(od.getFps()))
            except Exception as e:
                print(e)
                return

        imagefeedthread = Thread(target=appRun,
                                 name='feed_image', args=())
        imagefeedthread.daemon = True
        imagefeedthread.start()
        ayammatithread = Thread(target=processDataForDb,
                            name='process_data_for_db', args=())
        ayammatithread.daemon = True
        ayammatithread.start()

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
    ap.add_argument("-c", "--confidence", type=float, default=0.5,
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
        'classesAyamMati': ["ayammati2", "_1_", "_2_", "_3_", "_4_"],
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
            
            if not od.getStopped():
                sys.stdout.flush()
                sys.stdout.write("\r Detections => ayam mati: %d | FPS: %.2f       \r" % (
                    od.getAyamMatiDetection(), od.getFps()))
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
        self.stackSizeW = 510
        self.stackSizeH = 288
        self.abcClip = params['abcClip']
        if self.args["videotype"] == 'url':
            self.request = Request(self.url)
        # AyamMati
        self.colorsAyamMati = ''
        self.classesAyamMati = ''
        if isinstance(params['classesAyamMati'], (list, tuple, np.ndarray)):
            self.classesAyamMati = params['classesAyamMati']
        if isinstance(params['classesAyamMati'], (list, tuple, np.ndarray)):
            self.colorsAyamMati = np.random.uniform(
                0, 255, size=(len(params['classesAyamMati']), 3))
        onnxAyamMati = os.path.sep.join(
            [self.args["yolo"], "ayam_mati.onnx"])
        #self.netOnnxAyamMati = cv2.dnn.readNet(onnxAyamMati)
        self.netOnnxAyamMati = cv2.dnn.readNetFromONNX(onnxAyamMati)
        if self.args["use_gpu"]:
            # set CUDA as the preferable backend and target
            print("[INFO] setting preferable backend and target to CUDA...")
            self.netOnnxAyamMati.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.netOnnxAyamMati.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.ayamMatiLayerNames = self.netOnnxAyamMati.getLayerNames()
        self.ayamMatiOutputLayers = [self.ayamMatiLayerNames[i - 1] for i in self.netOnnxAyamMati.getUnconnectedOutLayers()]
        # --
        self.ayamMatiDetected = 0
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
                    else:
                        self.frameDetect = self.ayamMatiDetection(raw)
                        cv2.putText(self.frameDetect, "Total ayam mati: %d" % (self.ayamMatiDetected),
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


    def ayamMatiDetection(self, frame):
        resizeTo = 640
        (imageHeight, imageWidth) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(
            frame, (resizeTo, resizeTo)), 0.00392156862745098, (resizeTo, resizeTo),
            swapRB=True, crop=False)
        #blob = cv2.dnn.blobFromImage(image=frame, scalefactor=0.01, size=(416, 416), mean=(104, 117, 123))
        self.netOnnxAyamMati.setInput(blob)
        layers = self.netOnnxAyamMati.forward(self.ayamMatiOutputLayers)
        #layers = self.netOnnxAyamMati.forward(self.netOnnxAyamMati.getUnconnectedOutLayersNames())
        outputCount = layers[0].shape[1]

        classIDs = []
        confidences = []
        boxes = []

        for outputBox in range(outputCount):
            # detection: | Center X: Num | Center Y: Num | Width: Num | Height: Num | Confidence: Num | Score of Classes: Arr |
            detection = layers[0][0][outputBox]
            confidence = float(detection[4])
            # filter only >= 51% (default from confidence args) probability that the detection are objects
            if confidence >= float(self.args["confidence"]):
                scores = detection[5:]
                # classID: class with highest score
                classID = np.argmax(scores)
                score = float(scores[classID])
                # filter only object with class score of 51% probability
                if score >= float(self.args["confidence"]):
                    # Get object coordinate for rectangle drawing
                    center_x = int(detection[0])
                    center_y = int(detection[1])
                    wx = int(detection[2])
                    hx = int(detection[3])
###################################################################################################################################################
                    x = int(center_x - (wx / 2))
                    y = int(center_y - (hx / 2)) - 100

                    boxes.append([x, y, wx, hx])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # Non-maximum Suppression
        
        indexes = cv2.dnn.NMSBoxes(
            boxes,
            confidences,
            float(self.args["confidence"]),
            float(self.args["confidence"]) - 0.1)
        nmsClassIDs = []
        nmsConfidences = []
        nmsBoxes = []

        for i in indexes:
            nmsConfidences.append(confidences[i])
            nmsClassIDs.append(classIDs[i])
            nmsBoxes.append(boxes[i])
        
        classIDs = nmsClassIDs
        confidences = nmsConfidences
        boxes = nmsBoxes

        colors = ((0, 0, 255),)
        ayamMati = []
        # Drawing rectangle
        for i in range(len(boxes)):
            x, y, wx, hx = boxes[i]
            if self.classesAyamMati[classIDs[i]] == self.classesAyamMati[0]:
                ayamMati.append([x, y, x + wx, y + hx])
                label = str(f'{self.classesAyamMati[classIDs[i]]}: {confidences[i]:.2f}').replace('0.', '.')
                color = colors[classIDs[i]]
                cv2.rectangle(frame, (x, y), (x + wx, y + hx), color, 2)
                cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, .5, color, 1)

        self.ayamMatiDetected = len(ayamMati)
        return frame

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

    def getAyamMatiDetection(self):
        return self.ayamMatiDetected

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

        videoOutputName = f"{os.path.splitext(os.path.basename(self.args['video']))[0]}_yolov5_output.mp4"
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
