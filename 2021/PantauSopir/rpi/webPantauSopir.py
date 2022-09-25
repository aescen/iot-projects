#!/usr/bin/python3

from json import dumps as encodeJson
from threading import Thread, Lock
import numpy as np
import traceback
import argparse
import datetime
import imutils
import pymysql
import time
import cv2
import sys
import pyttsx3
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
WIN_NAME = 'TapoCam_C310'
VIDEO_SRC = 'rtsp://tapocam:t.p.c.m@192.168.0.10:554/stream1'
#VIDEO_SRC = 'rtsp://tapocam:t.p.c.m@192.168.43.178:554/stream1'
MAX_WIDTH = 640
MAX_HEIGHT = 360
LOCK = Lock()

#stdoutOrigin=sys.stdout 
#sys.stdout = open("log.txt", "w")

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
CONN = None
CC = None
try:
    u,p = '', ''
    if OS_TYPE == RASPBIAN:
        u = 'pi'
        p = 'raspberry'
    else:
        u = 'root'
        p = ''

    CONN = pymysql.connect(host='localhost',
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

def millis(): return int(round(time.time() * 1000)) & 0xffffffff

def seconds(): return int(round(time.time())) & 0xffffffff

def main():
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

    def stop():
        try:
            print('[INFO] Exiting...')
            try:
                result = """
                            UPDATE `zonabuta`
                                SET `objectCount` = '0',
                                    `objectType` = '{\"mobil\": 0, \"sepeda_motor\": 0, \"orang\": 0}',
                                    `totalDetection` = '0'
                            WHERE `zonabuta`.`id` = 0
                        """
                CC.execute(result)
                CONN.commit()
            except pymysql.err.InternalError as msg:
                print("Reset command skipped: ", msg)
            cv2.destroyAllWindows()
            CONN.close()
            od.stop()
            exit()
        except Exception as e:
            print('[INFO] Forced exit! Exception:', e)
            exit()

    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--confidence", type=float, default=.6,
                    help="minimum probability to filter weak detections, default: 0.6 (60%)")
    ap.add_argument("-t", "--videotype", default='stream',
                    help="path/url to video file/streams/url")
    ap.add_argument("-v", "--video", default='stream',
                    help="type of video file/streams/url")
    ap.add_argument("-f", "--frameskip", default=5,
                    help="frames to skip, default: 5")
    ap.add_argument("-a", "--abc", default="no",
                    help="auto brightness and contrast clip histogram, ex. -a 0.5")
    args = vars(ap.parse_args())

    try:
        runServer()
        #if OS_TYPE == WINDOWS:
        #    VIDEO_SRC = 1
        od = ObjectDetection(videoSrc=VIDEO_SRC, args=args,
                         maxWidth=MAX_WIDTH, maxHeight=MAX_HEIGHT)
        od.start()
        t2s = Text2Speech()
        
        time.sleep(1)
        infoTimer = millis()
        infoDelay = 500
        dbUpdateTimer = millis()
        dbUpdateDelay = 500
        
        objectCount = 0
        objectCountTmp = 0
        
        while(True):
            fps = od.getFps()
            objectCount = od.getFrameDetectionCount()
            objectType = od.getObjectType()
            totalDetection = od.getTotalObject()

            if millis() > infoTimer + infoDelay:
                print("FPS:", fps,
                    "| Detection:", objectCount,
                    "| Object type:", objectType,
                    "| Total:", totalDetection,
                    end="\t\r")
                infoTimer = millis()

            if objectCountTmp != objectCount:
                if objectCount >= 1:
                    t2s.say("Object detected:" + str(objectCount))
                    objectCountTmp = objectCount

            if OS_TYPE == WINDOWS:
                cv2.imshow(WIN_NAME, od.getFrameStack())
                if ord('q') == cv2.waitKey(10):
                    #sys.stdout.close()
                    #sys.stdout=stdoutOrigin
                    stop()

            if (millis() - dbUpdateTimer) >= dbUpdateDelay:
                try:
                    result = """
                                UPDATE `zonabuta` SET `objectCount` = '{0}', `objectType` = '{1}', `totalDetection` = '{2}' WHERE `zonabuta`.`id` = {3}
                            """.format(objectCount, encodeJson(objectType), totalDetection, 0)
                    CC.execute(result)
                    CONN.commit()
                except pymysql.err.InternalError as msg:
                    print("Command skipped: ", msg)

                dbUpdateTimer = millis()

            time.sleep(.1)
    except KeyboardInterrupt:
        stop()
    except Exception as e:
        print('[ERROR] Exception!', e)
        exit()

class Text2Speech:
    def __init__(self, rate=125, volume=1.0):
        self.rate = rate
        self.volume = volume
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('voice', 'ms')
        self.engine.setProperty('volume', self.volume)

    def say(self, text):
        def process(self, text):
            self.engine.say(text)
            self.engine.runAndWait()
        
        saythread = Thread(target=self.say,
                              name='Text2Speech Say:' + text, args=(str(text)))
        saythread.daemon = True
        saythread.start()

class ObjectDetection:
    def __init__(self, args, videoSrc=0, username=None, password=None, maxWidth=640, maxHeight=480, forceResize=False, abcClip=.5):
        #self.classes = ["background", "aeroplane", "bicycle", "bird", "boat",
        #                "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        #                "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        #                "sofa", "train", "tvmonitor"] # 2, 6, 7, 14, 15 - bicycle, bus, car, motorbike, person
        self.classes = ["latar_belakang", "pesawat", "sepeda", "burung", "perahu",
                        "botol", "bis", "mobil", "kucing", "kursi", "sapi", "meja_makan",
                        "anjing", "kuda", "sepeda_motor", "orang", "bunga", "domba",
                        "sofa", "kereta", "monitor_tv"]
        self.objectType = {self.classes[7]: 0, self.classes[14]: 0, self.classes[15]: 0}
        self.objectTypeTmp = {self.classes[7]: 0, self.classes[14]: 0, self.classes[15]: 0}
        self.stackSizeW = 510
        self.stackSizeH = 288
        self.objectToDetect = [7, 14, 15]
        self.args = args
        self.videoSrc = videoSrc
        self.forceResize = forceResize
        self.username = username
        self.password = password
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        self.abcClip = abcClip
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        self.net = cv2.dnn.readNetFromCaffe('./MobileNetSSD/prototxt', './MobileNetSSD/caffemodel')
        self.objectDetected = 0
        self.objectDetectedTmp = 0
        self.updateObjectType = True
        self.updateObjectTypeTimer = 0
        self.updateObjectTypeDelay = 1
        self.it = 0
        self.frameskip = int(args["frameskip"])
        self.avgfps = 0
        self.frames = 0
        self.starttime = datetime.datetime.now()
        self.stopped = False
        self.vs = None
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
            fps = self.frames / (datetime.datetime.now() -
                                 self.starttime).total_seconds()
            if self.frames >= 128:
                self.frames = 0
                self.starttime = datetime.datetime.now()
            return fps

        try:
            while True:
                if self.stopped:
                    return
                else:
                    raw = None
                    try:
                        grabbed, raw = self.vs.read()
                    except:
                        pass

                    if isinstance(raw, (list, tuple, np.ndarray)):
                        (h, w) = raw.shape[:2]
                        #raw = cv2.GaussianBlur(raw, (3, 3), 0)
                        #raw = cv2.bilateralFilter(raw, 3, 30, 30)
                        if h > self.maxHeight or w > self.maxWidth or self.forceResize:
                            raw = imutils.resize(
                                raw, width=self.maxWidth, height=self.maxHeight)
                        if self.args['abc'] != 'no':
                            try:
                                self.abcClip = float(self.args['abc'])
                            except ValueError:
                                pass
                            raw = self.abc(raw, clip_hist_percent=self.abcClip)[0]
                        if int(self.args["frameskip"]) > 0:
                            if self.it % self.frameskip == 0:
                                self.frame = raw.copy()
                                self.frames += 1
                            else:
                                self.it += 1
                                self.frames += 1
                                # skip
                                continue
                        else:
                            self.frame = raw.copy()
                            self.frames += 1
                    else:
                        # skip
                        continue

                    self.it += 1
                    self.frameDetect = self.objectDetection(raw)
                    self.frameStack = np.hstack([imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW),
                                                 imutils.resize(self.frameDetect, height=self.stackSizeH, width=self.stackSizeW)])
                    self.avgfps = getAvgFps()
                    if self.args["videotype"] == 'file':
                        if not self.vs.more:
                            self.stop()

                    time.sleep(.01)

        except KeyboardInterrupt:
            self.stop()
        except Exception:
            print('[ERROR] ', traceback.format_exc())
            self.frameStack = drawText(self.frameStack, traceback.format_exc(
            ), ( (self.stackSizeH * 2) * .025), ( (self.stackSizeW * 2) * .025), (96, 64, 255), .3)

    def objectDetection(self, frame):
        self.objectDetectedTmp = 0
        for k, v in self.objectTypeTmp.items():
            self.objectTypeTmp.update({k: 0})
        #objectTypeTmp = [-1, False]
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(imutils.resize(
            frame, 300, 300), .007843, (300, 300), 127.5)
        self.net.setInput(blob)

        # detection output blob has the shape of 1x1xNx7 arrays,
        # N is number of object in label/model,
        # 7: 0 is image index(always 0 if using only 1 input image),
        #  : 1 is index of label,
        #  : 2 is confidence,
        #  : 3 to 6 is bounding box (startX, startY, endX, endY)
        detections = self.net.forward()
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > float(self.args["confidence"]):
                idx = int(detections[0, 0, i, 1])
                for o in self.objectToDetect:
                    if idx == o:
                        self.objectDetectedTmp += 1
                        if self.objectDetected < self.objectDetectedTmp:
                            if (seconds() - self.updateObjectTypeTimer) > self.updateObjectTypeDelay:
                                self.updateObjectType = True
                                self.objectTypeTmp[self.classes[idx]] += 1
                                self.updateObjectTypeTimer = seconds()

                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")
                        y = endY + 15 if endY + 15 > 15 else endY - 15

                        if isinstance(self.classes, (list, tuple, np.ndarray)):
                            label = "{}: {:.2f}%".format(self.classes[idx],
                                                         confidence * 100)
                            cv2.rectangle(frame, (startX, startY), (endX, endY),
                                          self.colors[idx], 2)
                            cv2.putText(frame, label, (startX, y),
                                        cv2.FONT_HERSHEY_DUPLEX, .5, self.colors[idx], 1)
                        else:
                            label = "{}: {:.2f}%".format('Detection',
                                                         confidence * 100)
                            cv2.rectangle(frame, (startX, startY), (endX, endY),
                                          (64, 255, 96), 2)
                            cv2.putText(frame, label, (startX, y),
                                        cv2.FONT_HERSHEY_DUPLEX, .5, self.colors[idx], 1)

                if self.updateObjectType:
                    for k, v in self.objectTypeTmp.items():
                        if int(self.objectTypeTmp[k]) > 0:
                            nV = self.objectType[k]
                            nV += v
                            self.objectType.update({k: nV})
                    self.updateObjectType = False
                    self.updateObjectTypeTimer = seconds()

        if self.objectDetected != self.objectDetectedTmp:
            self.objectDetected = self.objectDetectedTmp

        cv2.putText(frame, "Total detected: %d" % self.objectDetected,
                    (int(self.maxWidth * .025), int(self.maxHeight * .05)),
                    cv2.FONT_HERSHEY_DUPLEX, .5, (255, 255, 255), 1)

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
        return (auto_result.copy(), alpha, beta)

    def getFps(self):
        return round(self.avgfps, 2)

    def getObjectType(self):
        return self.objectType

    def getTotalObject(self):
        total = 0
        for k, v in self.objectType.items():
            total += v
        return total

    def getFrameDetection(self):
        return self.frameDetect

    def getFrame(self):
        return self.frame

    def getFrameStack(self):
        return self.frameStack

    def getFrameDetectionCount(self):
        return self.objectDetected

    def start(self):
        if self.args["video"] == 'stream':
            if OS_TYPE == WINDOWS:
                self.vs = cv2.VideoCapture(self.videoSrc, cv2.CAP_DSHOW) #CAP_FFMPEG, CAP_IMAGES, CAP_DSHOW, CAP_MSMF, CAP_V4L2
                r, f = self.vs.read()
                if f == None:
                    self.vs = cv2.VideoCapture(self.videoSrc)
            else:
                self.vs = cv2.VideoCapture(self.videoSrc)
            time.sleep(.5)
        elif self.args["videotype"] == 'file':
            self.vs = FileVideoStream(self.args["video"]).start()
            time.sleep(.5)
        print('[INFO] Starting object detection...')
        streamthread = Thread(target=self.imageProcessing,
                              name='FetchImageUrl', args=())
        streamthread.daemon = True
        streamthread.start()
        return self

    def stop(self):
        self.stopped = True
        self.vs.release()
        self.frame = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameDetect = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameStack = np.hstack([imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW),
                                     imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW)])
        cv2.destroyAllWindows()
        print('[INFO] Object detection stopped.')

if __name__ == '__main__':
    main()
