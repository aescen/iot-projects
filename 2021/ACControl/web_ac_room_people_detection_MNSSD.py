#!/usr/bin/python3
from urllib.request import *
from urllib.error import URLError, HTTPError
from threading import Thread, Lock
from imutils.video import FileVideoStream
from imutils.video import VideoStream
import sys
import time
import base64
import curses
import socket
import imutils
import argparse
import datetime
import traceback
import cv2
import numpy as np
import os
import tracemalloc
import pymysql
from flask import Response
from flask import Flask
from flask import render_template
import logging
log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)
log.disabled = True

RASPBIAN = 'raspbian'
LINUX = 'linux'
MACOS = 'macos'
WINDOWS = 'windows'
OS_TYPE = ''
LOCK = Lock()

if sys.platform == LINUX or sys.platform == "linux2":
    try:
        import RPi.GPIO as IO
        import adafruit_dht as dht # sudo apt install libgpiod2 -y && sudo pip3 install adafruit-circuitpython-lis3dh adafruit-circuitpython-dht
        import board
        OS_TYPE = RASPBIAN
    except (ImportError, RuntimeError):
        OS_TYPE = LINUX
elif sys.platform == "darwin":
    OS_TYPE = MACOS
elif sys.platform == "win32":
    OS_TYPE = WINDOWS

# Database setup..
try:
    u,p = '', ''
    if OS_TYPE == RASPBIAN:
        u = 'pi'
        p = 'raspberry'
    else:
        u = 'root'
        p = ''

    connection = pymysql.connect(host='localhost',
                                 user=u,
                                 password=p,
                                 db='pi',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.Error as msg:
    print("Connection error: ", msg)
    exit()
# Create cursor
CC = connection.cursor()

def millis(): return int(round(time.time() * 1000)) & 0xffffffff


def seconds(): return int(round(time.time())) & 0xffffffff


def main():
    mainTracemalloc = tracemalloc
    mainTracemalloc.start()
    def runServer(host="localhost", port="8080", debug=False):
        app = Flask(__name__, template_folder='./web/templates/')

        def encodeImage():
            flag = None
            encodedImage = None
            while True:
                with LOCK:
                    (flag, encodedImage) = cv2.imencode(".jpg", od.getFrameDetection())
                    if not flag:
                        continue
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                      bytearray(encodedImage) + b'\r\n')
                time.sleep(.01)

        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/image")
        def image():
            return Response(encodeImage(), mimetype="multipart/x-mixed-replace; boundary=frame")

        def appRun():
            app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)
        
        imagefeedthread = Thread(target=appRun,
                                 name='Feed Image', args=())
        imagefeedthread.daemon = True
        imagefeedthread.start()


    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--prototxt", default='./MobileNetSSD/prototxt',
                    help="path to Caffe 'deploy' prototxt file")
    ap.add_argument("-m", "--model", default='./MobileNetSSD/caffemodel',
                    help="path to Caffe pre-trained model")
    ap.add_argument("-c", "--confidence", type=float, default=.6,
                    help="minimum probability to filter weak detections")
    ap.add_argument("-t", "--videotype", default='stream',
                    help="type of video file/streams/url")
    ap.add_argument("-v", "--video", default='stream',
                    help="path/url to video file/streams/url")
    ap.add_argument("-f", "--frameskip", default=3,
                    help="frames to skip(default: 3)")
    ap.add_argument("-a", "--abc", default="no",
                    help="auto brightness and contrast clip histogram, ex. -a 0.5")
    args = vars(ap.parse_args())
    classes = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    timeout = 5
    maxHeight = 480
    maxWidth = 640
    #screen = curses.initscr()
    # screen.refresh()
    # View camera online in Barrigada, Guam, Barrigada Mayor'S Office http://www.insecam.org/en/view/882308/
    #url = "http://121.55.235.78/oneshotimage1"
    #username = "user"
    #password = "user"
    #url = "http://192.168.0.20/image.jpg"
    #od = ObjectDetection(classes=classes,args=args, url=url, maxWidth=maxWidth, maxHeight=maxHeight)
    # od = ObjectDetection(classes=classes, args=args, url=url, username=username,
    #                     password=password, timeout=timeout, maxWidth=maxWidth, maxHeight=maxHeight)
    
    VIDEO_SRC = 1 if args["video"] == 'stream' else args["video"]
    od = ObjectDetection(classes=classes, videoSrc=VIDEO_SRC, args=args,
                         maxWidth=maxWidth, maxHeight=maxHeight)
    od.start()
    ac = ACControl('LG_AC')
    objectCount = -1
    
    dht11 = None
    dhtHumid = 0
    dhtTemp = 0
    acTemp = 0
    acSpeed = 0
    totalVisitor = 0
    totalVisitorTmp = 0

    if OS_TYPE == RASPBIAN:
        dht11 = dht.DHT11(board.D23)

    visitorUpdateTimer = seconds()
    visitorUpdateDelay = 1
    dbUpdateTimer = millis()
    dbUpdateDelay = 1000

    try:
        runServer()
        time.sleep(1)

        while True:
            mainMemCurrent, mainMemPeak = mainTracemalloc.get_traced_memory()
            odMemCurrent, odMemPeak = od.getMem()
            memCurrent = mainMemCurrent + odMemCurrent
            memPeak = mainMemPeak + odMemPeak

            if objectCount != od.getFrameDetectionCount():
                objectCount = od.getFrameDetectionCount()

                if OS_TYPE == RASPBIAN:
                    ac.setObjectCount(od.getFrameDetectionCount())
                    acTemp = ac.getTemp()
                    acSpeed = ac.getSpeed()

            if totalVisitorTmp != objectCount and (seconds() - visitorUpdateTimer) > visitorUpdateDelay:
                totalVisitorTmp = objectCount
                totalVisitor += totalVisitorTmp
                visitorUpdateTimer = seconds()

            if OS_TYPE == RASPBIAN:
                try:
                    dhtTemp = dht11.temperature
                    dhtHumid = dht11.humidity
                except:
                    dhtHumid = -1
                    dhtTemp = -1

            if OS_TYPE == WINDOWS:
                #screen.addstr(0, 0, "\rTotal detected: %d" % (objectCount))
                #screen.addstr(1, 0, "\rfps: %.2f" % (fps))
                #screen.refresh()
                cv2.imshow('Image: In/Out', od.getFrameStack())
                #cv2.imshow('Image: In', od.getFrame())
                #cv2.imshow('Image: Out', od.getFrameDetection())
                if ord('q') == cv2.waitKey(10):
                    od.stop()
                    cv2.destroyAllWindows()
                    # curses.endwin()
                    sys.exit(0)
            sys.stdout.flush()
            sys.stdout.write( "\r Detection: %d | FPS: %.2f | Temp: %.2f | Humid: %.2f | AC Temp: %d | AC Speed: %s | Mem: %dM       \r" % ( objectCount, od.getFps(), dhtTemp, dhtHumid, acTemp, acSpeed, int(memCurrent / 10**5) ) )

            if (millis() - dbUpdateTimer) >= dbUpdateDelay:
                try:
                    result = """
                                UPDATE `accontrol` SET `objectCount` = '{0}', `roomTemp` = '{1}', `humidity` = '{2}', `acTemp` = '{3}', `acSpeed` = '{4}', `totalVisitor` = '{5}' WHERE `accontrol`.`id` = {6}
                            """.format(objectCount, dhtTemp, dhtHumid, acTemp, acSpeed, totalVisitor, 1)
                    CC.execute(result)
                    connection.commit()
                except pymysql.err.InternalError as msg:
                    print("Command skipped: ", msg)

                dbUpdateTimer = millis()

            time.sleep(.1)

    except KeyboardInterrupt:
        od.stop()
        # curses.endwin()
        mainTracemalloc.stop()
        sys.exit(0)


class ObjectDetection:
    def __init__(self, args, classes=None, videoSrc=0, url=None, username=None, password=None, timeout=10, maxWidth=640, maxHeight=480, forceResize=False, abcClip=.5):
        self.traceMalloc = tracemalloc
        self.memCurrent = 0
        self.memPeak = 0
        self.timeout = timeout
        self.url = url
        self.classes = ''
        if isinstance(classes, (list, tuple, np.ndarray)):
            self.classes = classes
        self.args = args
        self.videoSrc = videoSrc
        self.forceResize = forceResize
        self.username = username
        self.password = password
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        self.abcClip = abcClip
        if self.args["videotype"] == 'url':
            self.request = Request(url)
        self.colors = ''
        if isinstance(classes, (list, tuple, np.ndarray)):
            self.colors = np.random.uniform(0, 255, size=(len(classes), 3))
        self.frameColor = (64, 255, 96)
        self.net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
        self.objectDetected = 0
        self.objectDetectedTmp = 0
        self.it = 0
        self.frameskip = int(args["frameskip"])
        self.avgfps = 0
        self.frames = 0
        self.starttime = datetime.datetime.now()
        self.stopped = False
        self.vs = None
        self.outvideo = None
        self.frame = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameDetect = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameStack = np.hstack([imutils.resize(self.frame, height=192, width=340),
                                     imutils.resize(self.frameDetect, height=192, width=340)])
        time.sleep(0.5)
        self.traceMalloc.start()

    def imageProcessing(self):
        def drawText(frame, text, startX=int(self.maxWidth * .025), startY=int(self.maxHeight * .05), textColor=(64, 255, 96),  fontSize=1, thickness=1):
            if thickness < 1:
                thickness = 1
            cv2.putText(frame, str(text), (int(startX), int(startY)),
                        cv2.FONT_HERSHEY_DUPLEX, fontSize, (textColor), int(thickness))
            return frame

        def getAvgFps():
            fps = self.frames / (datetime.datetime.now() -
                                 self.starttime).total_seconds()
            if self.frames >= 128:
                self.frames = 0
                self.starttime = datetime.datetime.now()
            return fps

        try:
            self.stopped = False
            while True:
                if self.stopped:
                    self.traceMalloc.stop()
                    return
                else:
                    self.memCurrent, self.memPeak = self.traceMalloc.get_traced_memory()
                    time.sleep(.01)
                    self.frame = None
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
                            self.frame = cv2.imdecode(imgArr, cv2.IMREAD_COLOR)
                    else:
                        try:
                            grabbed, self.frame = self.vs.read()
                            if not grabbed:
                                self.stop()
                                continue
                        except:
                            pass

                    if isinstance(self.frame, (list, tuple, np.ndarray)):
                        (h, w) = self.frame.shape[:2]
                        #self.frame = cv2.GaussianBlur(self.frame, (3, 3), 0)
                        #self.frame = cv2.bilateralFilter(self.frame, 3, 30, 30)
                        if h > self.maxHeight or w > self.maxWidth or self.forceResize:
                            self.frame = imutils.resize(
                                self.frame, width=self.maxWidth, height=self.maxHeight)
                        if int(self.args["frameskip"]) > 0:
                            if self.it % self.frameskip == 0:
                                self.frames += 1
                            else:
                                self.it += 1
                                self.frames += 1
                                continue
                        else:
                            self.frames += 1
                    else:
                        continue

                    self.it += 1
                    if self.args['abc'] != 'no':
                        try:
                            self.abcClip = float(self.args['abc'])
                        except ValueError:
                            pass
                        self.frame = self.abc(
                            self.frame, clip_hist_percent=self.abcClip)[0]
                    self.frameDetect = self.objectDetection(self.frame.copy())
                    self.frameStack = np.hstack([imutils.resize(self.frame, height=192, width=340),
                                                 imutils.resize(self.frameDetect, height=192, width=340)])
                    self.avgfps = getAvgFps()
                    if self.args["videotype"] == 'file':
                        if not self.vs.more:
                            self.stop()

        except HTTPError as e:
            print('[ERROR] The server couldn\'t fulfill the request.')
            print('[ERROR] Error code: ', e.code)
            self.frameStack = drawText(
                self.frameStack, e.code, (384 * .025), (680 * .025), (96, 64, 255), .3)
        except URLError as e:
            print('[ERROR] We failed to reach a server.')
            print('[ERROR] Reason: ', e.reason)
            self.frameStack = drawText(
                self.frameStack, e.reason, (384 * .025), (680 * .025), (96, 64, 255), .3)
        except KeyboardInterrupt:
            self.stop()
        except Exception:
            print('[ERROR] ', traceback.format_exc())
            self.frameStack = drawText(self.frameStack, traceback.format_exc(
                ), (384 * .025), (680 * 0.025), (96, 64, 255), .3)

    def objectDetection(self, frame):
        self.objectDetectedTmp = 0
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(imutils.resize(
            frame, 300, 300), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > float(self.args["confidence"]):
                self.objectDetectedTmp += 1
                idx = int(detections[0, 0, i, 1])
                if idx == 15:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    y = startY - 20 if startY - 20 > 20 else startY + 20
                    if isinstance(self.classes, (list, tuple, np.ndarray)):
                        label = "{}: {:.2f}%".format(self.classes[idx],
                                                     confidence * 100)
                        cv2.rectangle(frame, (startX, startY), (endX, endY),
                                      self.frameColor, 2)
                        cv2.rectangle(frame, (startX, y), (endX, startY),
                                      self.frameColor, -1)
                        cv2.putText(frame, label, (startX + 2, y + 15),
                                    cv2.FONT_HERSHEY_DUPLEX, .5, (0, 0, 0), 1)
                    else:
                        label = "{}: {:.2f}%".format('People',
                                                     confidence * 100)
                        cv2.rectangle(frame, (startX, startY), (endX, endY),
                                      self.frameColor, 2)
                        cv2.rectangle(frame, (startX, y), (endX, startY),
                                      self.frameColor, -1)
                        cv2.putText(frame, label, (startX + 2, y + 15),
                                    cv2.FONT_HERSHEY_DUPLEX, .5, self.frameColor, 1)

        if self.objectDetected != self.objectDetectedTmp:
            self.objectDetected = self.objectDetectedTmp

        cv2.putText(frame, "Total detected: %d" % self.objectDetected,
                    (int(self.maxWidth * .025), int(self.maxHeight * .05)),
                    cv2.FONT_HERSHEY_DUPLEX, .5, (255, 255, 255), 1)
        if self.outvideo != None:
            self.outvideo.write(frame)
        return frame.copy()

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
        return self.avgfps

    def getFrameDetection(self):
        return self.frameDetect

    def getFrame(self):
        return self.frame

    def getFrameStack(self):
        return self.frameStack

    def getFrameDetectionCount(self):
        return self.objectDetected

    def getMem(self):
        return (self.memCurrent, self.memPeak)

    def start(self):
        print('[INFO] Starting object detection...')
        if OS_TYPE == WINDOWS:
            self.vs = cv2.VideoCapture(self.videoSrc, cv2.CAP_DSHOW) #CAP_FFMPEG, CAP_IMAGES, CAP_DSHOW, CAP_MSMF, CAP_V4L2
            ret, img = self.vs.read()
            if not isinstance(img, (list, tuple, np.ndarray)):
                self.vs = cv2.VideoCapture(self.videoSrc, cv2.CAP_FFMPEG) #CAP_FFMPEG, CAP_IMAGES, CAP_DSHOW, CAP_MSMF, CAP_V4L2
        else:
            self.vs = cv2.VideoCapture(self.videoSrc)
        time.sleep(.5)
        ret, img = self.vs.read()
        if not ret:
            print('[ERROR] video stream error.')
            exit()
        (height, width) = img.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.outvideo = cv2.VideoWriter('./output/videos/' + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')) +
                   '_output.avi',fourcc, 15.0, (width, height)) # 30.0 fps
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
        self.frameStack = np.hstack([imutils.resize(self.frame, height=192, width=340),
                                     imutils.resize(self.frame, height=192, width=340)])
        if self.vs != None:
            self.vs.release()
        if self.outvideo != None:
            self.outvideo.release()
        cv2.destroyAllWindows()
        print('[INFO] Object detection stopped.')


class ACControl:
    # LG AKB73315611
    AC_ON = ' AC_ON'
    AC_OFF = ' AC_OFF'
    SWING_ON = ' SWING_ON'
    SWING_OFF = ' SWING_OFF'
    AC_LOW_18 = ' AC_LOW_18'
    AC_LOW_20 = ' AC_LOW_20'
    AC_LOW_21 = ' AC_LOW_21'
    AC_LOW_22 = ' AC_LOW_22'
    AC_LOW_23 = ' AC_LOW_23'
    AC_LOW_24 = ' AC_LOW_24'
    AC_LOW_25 = ' AC_LOW_25'
    AC_LOW_26 = ' AC_LOW_26'
    AC_LOW_27 = ' AC_LOW_27'
    AC_LOW_28 = ' AC_LOW_28'
    AC_LOW_29 = ' AC_LOW_29'
    AC_LOW_30 = ' AC_LOW_30'
    AC_MID_18 = ' AC_MID_18'
    AC_MID_20 = ' AC_MID_20'
    AC_MID_21 = ' AC_MID_21'
    AC_MID_22 = ' AC_MID_22'
    AC_MID_23 = ' AC_MID_23'
    AC_MID_24 = ' AC_MID_24'
    AC_MID_25 = ' AC_MID_25'
    AC_MID_26 = ' AC_MID_26'
    AC_MID_27 = ' AC_MID_27'
    AC_MID_28 = ' AC_MID_28'
    AC_MID_29 = ' AC_MID_29'
    AC_MID_30 = ' AC_MID_30'
    AC_HIGH_18 = ' AC_HIGH_18'
    AC_HIGH_20 = ' AC_HIGH_20'
    AC_HIGH_21 = ' AC_HIGH_21'
    AC_HIGH_22 = ' AC_HIGH_22'
    AC_HIGH_23 = ' AC_HIGH_23'
    AC_HIGH_24 = ' AC_HIGH_24'
    AC_HIGH_25 = ' AC_HIGH_25'
    AC_HIGH_26 = ' AC_HIGH_26'
    AC_HIGH_27 = ' AC_HIGH_27'
    AC_HIGH_28 = ' AC_HIGH_28'
    AC_HIGH_29 = ' AC_HIGH_29'
    AC_HIGH_30 = ' AC_HIGH_30'
    AC_CHAOS_18 = ' AC_CHAOS_18'
    AC_CHAOS_20 = ' AC_CHAOS_20'
    AC_CHAOS_21 = ' AC_CHAOS_21'
    AC_CHAOS_22 = ' AC_CHAOS_22'
    AC_CHAOS_23 = ' AC_CHAOS_23'
    AC_CHAOS_24 = ' AC_CHAOS_24'
    AC_CHAOS_25 = ' AC_CHAOS_25'
    AC_CHAOS_26 = ' AC_CHAOS_26'
    AC_CHAOS_27 = ' AC_CHAOS_27'
    AC_CHAOS_28 = ' AC_CHAOS_28'
    AC_CHAOS_29 = ' AC_CHAOS_29'
    AC_CHAOS_30 = ' AC_CHAOS_30'
    AI_LOW_18 = ' AI_LOW_18'
    AI_LOW_20 = ' AI_LOW_20'
    AI_LOW_21 = ' AI_LOW_21'
    AI_LOW_22 = ' AI_LOW_22'
    AI_LOW_23 = ' AI_LOW_23'
    AI_LOW_24 = ' AI_LOW_24'
    AI_LOW_25 = ' AI_LOW_25'
    AI_LOW_26 = ' AI_LOW_26'
    AI_LOW_27 = ' AI_LOW_27'
    AI_LOW_28 = ' AI_LOW_28'
    AI_LOW_29 = ' AI_LOW_29'
    AI_LOW_30 = ' AI_LOW_30'
    AI_MID_18 = ' AI_MID_18'
    AI_MID_20 = ' AI_MID_20'
    AI_MID_21 = ' AI_MID_21'
    AI_MID_22 = ' AI_MID_22'
    AI_MID_23 = ' AI_MID_23'
    AI_MID_24 = ' AI_MID_24'
    AI_MID_25 = ' AI_MID_25'
    AI_MID_26 = ' AI_MID_26'
    AI_MID_27 = ' AI_MID_27'
    AI_MID_28 = ' AI_MID_28'
    AI_MID_29 = ' AI_MID_29'
    AI_MID_30 = ' AI_MID_30'
    AI_HIGH_18 = ' AI_HIGH_18'
    AI_HIGH_20 = ' AI_HIGH_20'
    AI_HIGH_21 = ' AI_HIGH_21'
    AI_HIGH_22 = ' AI_HIGH_22'
    AI_HIGH_23 = ' AI_HIGH_23'
    AI_HIGH_24 = ' AI_HIGH_24'
    AI_HIGH_25 = ' AI_HIGH_25'
    AI_HIGH_26 = ' AI_HIGH_26'
    AI_HIGH_27 = ' AI_HIGH_27'
    AI_HIGH_28 = ' AI_HIGH_28'
    AI_HIGH_29 = ' AI_HIGH_29'
    AI_HIGH_30 = ' AI_HIGH_30'
    AI_CHAOS_18 = ' AI_CHAOS_18'
    AI_CHAOS_20 = ' AI_CHAOS_20'
    AI_CHAOS_21 = ' AI_CHAOS_21'
    AI_CHAOS_22 = ' AI_CHAOS_22'
    AI_CHAOS_23 = ' AI_CHAOS_23'
    AI_CHAOS_24 = ' AI_CHAOS_24'
    AI_CHAOS_25 = ' AI_CHAOS_25'
    AI_CHAOS_26 = ' AI_CHAOS_26'
    AI_CHAOS_27 = ' AI_CHAOS_27'
    AI_CHAOS_28 = ' AI_CHAOS_28'
    AI_CHAOS_29 = ' AI_CHAOS_29'
    AI_CHAOS_30 = ' AI_CHAOS_30'
    DEHUM_LOW = ' DEHUM_LOW'
    DEHUM_MID = ' DEHUM_MID'
    DEHUM_HIGH = ' DEHUM_HIGH'
    DEHUM_CHAOS = ' DEHUM_CHAOS'
    HEAT_LOW_18 = ' HEAT_LOW_18'
    HEAT_LOW_20 = ' HEAT_LOW_20'
    HEAT_LOW_21 = ' HEAT_LOW_21'
    HEAT_LOW_22 = ' HEAT_LOW_22'
    HEAT_LOW_23 = ' HEAT_LOW_23'
    HEAT_LOW_24 = ' HEAT_LOW_24'
    HEAT_LOW_25 = ' HEAT_LOW_25'
    HEAT_LOW_26 = ' HEAT_LOW_26'
    HEAT_LOW_27 = ' HEAT_LOW_27'
    HEAT_LOW_28 = ' HEAT_LOW_28'
    HEAT_LOW_29 = ' HEAT_LOW_29'
    HEAT_LOW_30 = ' HEAT_LOW_30'
    HEAT_MID_18 = ' HEAT_MID_18'
    HEAT_MID_20 = ' HEAT_MID_20'
    HEAT_MID_21 = ' HEAT_MID_21'
    HEAT_MID_22 = ' HEAT_MID_22'
    HEAT_MID_23 = ' HEAT_MID_23'
    HEAT_MID_24 = ' HEAT_MID_24'
    HEAT_MID_25 = ' HEAT_MID_25'
    HEAT_MID_26 = ' HEAT_MID_26'
    HEAT_MID_27 = ' HEAT_MID_27'
    HEAT_MID_28 = ' HEAT_MID_28'
    HEAT_MID_29 = ' HEAT_MID_29'
    HEAT_MID_30 = ' HEAT_MID_30'
    HEAT_HIGH_18 = ' HEAT_HIGH_18'
    HEAT_HIGH_20 = ' HEAT_HIGH_20'
    HEAT_HIGH_21 = ' HEAT_HIGH_21'
    HEAT_HIGH_22 = ' HEAT_HIGH_22'
    HEAT_HIGH_23 = ' HEAT_HIGH_23'
    HEAT_HIGH_24 = ' HEAT_HIGH_24'
    HEAT_HIGH_25 = ' HEAT_HIGH_25'
    HEAT_HIGH_26 = ' HEAT_HIGH_26'
    HEAT_HIGH_27 = ' HEAT_HIGH_27'
    HEAT_HIGH_28 = ' HEAT_HIGH_28'
    HEAT_HIGH_29 = ' HEAT_HIGH_29'
    HEAT_HIGH_30 = ' HEAT_HIGH_30'
    HEAT_CHAOS_18 = ' HEAT_CHAOS_18'
    HEAT_CHAOS_20 = ' HEAT_CHAOS_20'
    HEAT_CHAOS_21 = ' HEAT_CHAOS_21'
    HEAT_CHAOS_22 = ' HEAT_CHAOS_22'
    HEAT_CHAOS_23 = ' HEAT_CHAOS_23'
    HEAT_CHAOS_24 = ' HEAT_CHAOS_24'
    HEAT_CHAOS_25 = ' HEAT_CHAOS_25'
    HEAT_CHAOS_26 = ' HEAT_CHAOS_26'
    HEAT_CHAOS_27 = ' HEAT_CHAOS_27'
    HEAT_CHAOS_28 = ' HEAT_CHAOS_28'
    HEAT_CHAOS_29 = ' HEAT_CHAOS_29'
    HEAT_CHAOS_30 = ' HEAT_CHAOS_30'

    def __init__(self, confName='LG_AC'):
        self.acConfName = confName
        self.countTmp = -1
        self.waitTmp = False
        self.commandTimer = 0
        self.commandInterval = 5
        self.currentTempSet = 24
        self.currentSpeedSet = 'LOW'

    def sendCommand(self, command, repeat=False):
        command = 'irsend SEND_ONCE ' + self.acConfName + command
        os.system(command)

    def getTemp(self):
        return self.currentTempSet

    def getSpeed(self):
        return self.currentSpeedSet

    def setObjectCount(self, objectCount):
        if seconds() - self.commandTimer > self.commandInterval:
            self.commandTimer = seconds()
            if self.countTmp != objectCount:
                self.countTmp = objectCount
                self.waitTmp = True
                if objectCount == 0:
                    self.sendCommand(ACControl.AC_LOW_24)
                    self.currentTempSet = 24
                    self.currentSpeedSet = 'LOW'
                #    print('[INFO] AC command: ' + ACControl.AC_LOW_24)
                elif objectCount > 0 < 2:
                    self.sendCommand(ACControl.AC_LOW_22)
                    self.currentTempSet = 22
                    self.currentSpeedSet = 'LOW'
                #    print('[INFO] AC command: ' + ACControl.AC_LOW_22)
                elif objectCount > 1 < 3:
                    self.sendCommand(ACControl.AC_LOW_20)
                    self.currentTempSet = 20
                    self.currentSpeedSet = 'LOW'
                #    print('[INFO] AC command: ' + ACControl.AC_LOW_20)
                elif objectCount > 2 < 4:
                    self.sendCommand(ACControl.AC_LOW_18)
                    self.currentTempSet = 18
                    self.currentSpeedSet = 'LOW'
                #    print('[INFO] AC command: ' + ACControl.AC_LOW_18)
                elif objectCount > 3 < 5:
                    self.sendCommand(ACControl.AC_MID_24)
                    self.currentTempSet = 24
                    self.currentSpeedSet = 'MID'
                #    print('[INFO] AC command: ' + ACControl.AC_MID_24)
                elif objectCount > 4 < 6:
                    self.sendCommand(ACControl.AC_MID_22)
                    self.currentTempSet = 22
                    self.currentSpeedSet = 'MID'
                #    print('[INFO] AC command: ' + ACControl.AC_MID_22)
                elif objectCount > 5 < 7:
                    self.sendCommand(ACControl.AC_MID_20)
                    self.currentTempSet = 20
                    self.currentSpeedSet = 'MID'
                #    print('[INFO] AC command: ' + ACControl.AC_MID_20)
                elif objectCount > 6 < 8:
                    self.sendCommand(ACControl.AC_MID_18)
                    self.currentTempSet = 18
                    self.currentSpeedSet = 'MID'
                #    print('[INFO] AC command: ' + ACControl.AC_MID_18)
                elif objectCount > 7 < 9:
                    self.sendCommand(ACControl.AC_HIGH_24)
                    self.currentTempSet = 24
                    self.currentSpeedSet = 'HIGH'
                #    print('[INFO] AC command: ' + ACControl.AC_HIGH_24)
                elif objectCount > 8 < 10:
                    self.sendCommand(ACControl.AC_HIGH_22)
                    self.currentTempSet = 22
                    self.currentSpeedSet = 'HIGH'
                #    print('[INFO] AC command: ' + ACControl.AC_HIGH_22)
                elif objectCount > 9 < 11:
                    self.sendCommand(ACControl.AC_HIGH_20)
                    self.currentTempSet = 20
                    self.currentSpeedSet = 'HIGH'
                #    print('[INFO] AC command: ' + ACControl.AC_HIGH_20)
                elif objectCount > 10 < 12:
                    self.sendCommand(ACControl.AC_HIGH_18)
                    self.currentTempSet = 18
                    self.currentSpeedSet = 'HIGH'
                #    print('[INFO] AC command: ' + ACControl.AC_HIGH_18)
        else:
            if self.waitTmp:
                self.waitTmp = False
                #print('[INFO] Wait ' + str(seconds() - self.commandTimer) +
                #      's before sending next command to AC.')


if __name__ == '__main__':
    main()
