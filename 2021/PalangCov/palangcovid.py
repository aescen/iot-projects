#!/usr/bin/python3

from threading import Thread, Lock
from imutils.video import FileVideoStream
from imutils.video import VideoStream
import sys
import os
from time import gmtime, strftime, sleep, time
import imutils
import argparse
import datetime
import traceback
import cv2
from math import exp
from math import log
import numpy as np
from flask import Response
from flask import Flask
from flask import render_template
import logging
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)
# log.disabled = True

os.nice(20)

# Const
LOWER_TEMP = 35.0
UPPER_TEMP = 36.7
RASPBIAN = 'raspbian'
LINUX = 'linux'
MACOS = 'macos'
WINDOWS = 'windows'
OS_TYPE = ''
CC = None

if sys.platform == LINUX or sys.platform == "linux2":
    try:
        import RPi.GPIO as IO
        # sudo apt install libgpiod2 -y && sudo pip3 install adafruit-circuitpython-lis3dh adafruit-circuitpython-dht
        import adafruit_dht as dht
        import board
        from smbus2 import SMBus
        from mlx90614 import MLX90614
        import pymysql
        OS_TYPE = RASPBIAN

        # Database setup..
        # Create connection to MySQL server
        print("Connecting ...")
        try:
            connection = pymysql.connect(host='localhost',
                                         user='pi',
                                         password='raspberry',
                                         db='pi',
                                         charset='utf8',
                                         cursorclass=pymysql.cursors.DictCursor)
        except pymysql.err.Error as msg:
            print("Connection error: ", msg)
            exit()
        # Create cursor
        CC = connection.cursor()
    except (ImportError, RuntimeError):
        OS_TYPE = LINUX
elif sys.platform == "darwin":
    OS_TYPE = MACOS
elif sys.platform == "win32":
    OS_TYPE = WINDOWS


# Global functions
def millis(): return int(round(time() * 1000)) & 0xffffffff


def seconds(): return int(round(time())) & 0xffffffff


def setBuzzer(state, pinBuzzer=12):
    def pinOff(pin):
        IO.setup(pin, IO.IN)

    def pinOn(pin):
        IO.setup(pin, IO.OUT, initial=IO.HIGH)

    IO.setup(pinBuzzer, IO.OUT)

    if state is True:
        pinOn(pinBuzzer)
    else:
        pinOff(pinBuzzer)


class main:
    def __init__(self):
        self.ap = argparse.ArgumentParser()
        self.ap.add_argument("-v", "--video", default='stream',
                             help="path/url to video file/streams")
        self.ap.add_argument("-f", "--frameskip", default=0,
                             help="frames to skip(default: 0)")
        self.ap.add_argument("-a", "--abc", default="no",
                             help="auto brightness and contrast clip histogram, ex. -a 0.5")
        self.args = vars(self.ap.parse_args())
        self.minFaceSize = (54, 72)
        self.maxHeight = 480
        self.maxWidth = 640
        self.camera_src = 0
        self.dbUpdateTimer = seconds()
        self.dbUpdateDelay = 1

        self.oc = ObjectClassifier(src=self.camera_src, args=self.args, minFaceSize=self.minFaceSize,
                                   maxWidth=self.maxWidth, maxHeight=self.maxHeight)
        self.oc.start()

        self.pc = PalangControl(pinEnableA=26, pinEnableB=16, pinIn1=13, pinIn2=19,
                                pinIn3=21, pinIn4=20, delayTime=.25, upSteps=9, downSteps=9)

        self.ud = UltrasonicDetection(
            triggerPin=17, echoPin=27, detectionDistance=500)
        self.ud.start()
        self.bus = SMBus(1)
        self.mlx = MLX90614(self.bus, address=0x5A)
        self.ambTemp = 0
        self.objTemp = 0

        self.dht11 = dht.DHT11(board.D23)
        self.dhtHumid = 0
        self.dhtTemp = 0

        self.objectImage = None
        self.objectCount = 0
        self.totalCount = 0

        self.lock = Lock()

        self.infoDelay = 1
        self.infoTimer = seconds()

    def runServer(self, host="0.0.0.0", port="8080", debug=False):
        def appRun():
            app.run(host=host, port=port, debug=debug,
                    threaded=True, use_reloader=False)

        def encodeImage():
            while True:
                with self.lock:
                    if self.objectImage is None:
                        continue
                    (flag, encodedImage) = cv2.imencode(
                        ".jpg", self.objectImage)
                    if not flag:
                        continue
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                      bytearray(encodedImage) + b'\r\n')
                sleep(0.01)

        app = Flask(__name__)

        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/image")
        def image():
            return Response(encodeImage(), mimetype="multipart/x-mixed-replace; boundary=frame")

        imagefeedthread = Thread(target=appRun,
                                 name='Feed Image', args=())
        imagefeedthread.daemon = True
        imagefeedthread.start()

    def start(self):
        try:
            self.runServer()
            self.pc.downward(1)
            sleep(1)

            while True:
                self.getInfo()
                self.showInfo()

                if OS_TYPE == RASPBIAN:
                    # detected: ok
                    if self.objectCount > 0 and (self.objTemp >= LOWER_TEMP and self.objTemp <= UPPER_TEMP):
                        setBuzzer(False)
                        self.pc.upward(1)
                        # wait object to pass
                        while not self.ud.getDetection():
                            self.getInfo()
                            self.showInfo()
                            sleep(.01)
                        # total +1
                        self.pc.downward(1)
                    # detected: not ok
                    elif self.objectCount > 0 and self.objTemp > UPPER_TEMP:
                        setBuzzer(True)
                        while self.objectCount > 0 or self.objTemp > UPPER_TEMP:
                            self.getInfo()
                            self.showInfo()
                            sleep(.01)
                        # object gone
                        setBuzzer(False)

                sleep(.01)
        except KeyboardInterrupt:
            self.cleanup()
            sys.exit(0)

    def getInfo(self):
        with self.lock:
            self.objectImage = self.oc.getFrameDetection()
        self.objectCount = self.oc.getFrameDetectionCount()
        if OS_TYPE == RASPBIAN:
            try:
                self.dhtTemp = self.dht11.temperature
                self.dhtHumid = self.dht11.humidity
                if self.dhtHumid is None:
                    self.dhtHumid = -1

                if self.dhtTemp is None:
                    self.dhtTemp = -1
            except:
                self.dhtHumid = -1
                self.dhtTemp = -1

            try:
                self.ambTemp = self.mlx.get_amb_temp()
                self.objTemp = self.mlx.get_obj_temp()
            except Exception:
                self.ambTemp = -1
                self.objTemp = -1

            self.totalCount = self.ud.getTotalDetection()
            if self.totalCount is None:
                self.totalCount = -1

    def showInfo(self):
        if seconds() - self.infoTimer >= self.infoDelay:
            # print(self.ambTemp, self.objTemp, self.dhtTemp, self.dhtHumid,
            #       self.objectCount, self.oc.fps(), self.ud.getDetection(), self.totalCount)
            sys.stdout.flush()
            sys.stdout.write("\r Amb_T: %.2f | Obj_T: %.2f | Dht_T: %.2f | Dht_H: %.2f Face: %d | Vid_fps: %.2f | USonic: %r | Total: %d               \r" % (
                self.ambTemp, self.objTemp, self.dhtTemp, self.dhtHumid, self.objectCount, self.oc.fps(), self.ud.getDetection(), self.totalCount))

            if OS_TYPE == RASPBIAN:
                if (seconds() - self.dbUpdateTimer) >= self.dbUpdateDelay:
                    try:
                        result = """
                                    UPDATE `palangcov` SET `ambTemp` = '{0}', `objTemp` = '{1}', `humidDHT` = '{2}', `tempDHT` = '{3}', `totalVisitor` = '{4}' WHERE `palangcov`.`id` = {5};
                                    """.format(self.ambTemp, self.objTemp, self.dhtHumid, self.dhtTemp, self.totalCount, 1)
                        CC.execute(result)
                        connection.commit()
                    except pymysql.err.InternalError as msg:
                        print("Command skipped: ", msg)

                    self.dbUpdateTimer = seconds()

            if OS_TYPE != RASPBIAN:
                cv2.imshow('Image: In/Out', self.oc.getFrameStack())
                if ord('q') == cv2.waitKey(10):
                    self.cleanup()
                    sys.exit(0)
            self.infoTimer = seconds()

    def cleanup(self):
        self.oc.stop()
        self.ud.stop()
        self.pc.stop()
        self.bus.close()
        sleep(1)
        print('\nEnd.')


# Classes
class UltrasonicDetection:
    def __init__(self, triggerPin=17, echoPin=27, detectionDistance=50, detectionTimeout=3, sampleSize=11, sampleWait=0.1, celsius=25):
        from hcsr04sensor import sensor as us  # sudo pip3 install hcsr04sensor

        self.totalDetection = 0
        self.distance = 0
        self.triggerPin = triggerPin
        self.echoPin = echoPin
        self.usMeasure = us.Measurement
        IO.setmode(IO.BCM)
        IO.setwarnings(False)
        IO.setup(triggerPin, IO.OUT)
        IO.setup(echoPin, IO.IN)
        self.detectionDistance = detectionDistance
        self.detectionTimeout = detectionTimeout
        self.detected = False
        self.detectTimer = seconds()
        self.celsius = celsius
        self.sampleSize = sampleSize
        self.sampleWait = sampleWait

    def start(self):
        self.stopped = False
        ultrasonicthread = Thread(target=self.distancePoll,
                                  name='UltrasonicDetectionThread', args=())
        ultrasonicthread.daemon = True
        ultrasonicthread.start()
        return self

    def stop(self):
        self.stopped = True
        IO.cleanup((self.triggerPin, self.echoPin))

    def getDetectionDistance(self):
        return self.detectionDistance

    def getDetectionTimeout(self):
        return self.detectionTimeout

    def getDetection(self, detectionDistance=None):
        if detectionDistance != None:
            self.detectionDistance = detectionDistance

        if self.distance <= self.detectionDistance and not self.detected:
            self.detectTimer = seconds()
            self.detected = True
            self.totalDetection += 1
            return True
        elif self.detected:
            if self.distance <= self.detectionDistance:
                self.detectTimer = seconds()
            elif seconds() - self.detectTimer <= self.detectionTimeout and self.distance > self.detectionDistance:
                self.detected = False
                return False

            return True
        else:
            return False

    def getTotalDetection(self):
        return self.totalDetection

    def getDistance(self):
        return self.distance

    def distancePoll(self):
        try:
            while True:
                if self.stopped is True:
                    break
                else:
                    self.distance = self.usMeasure.basic_distance(
                        self.triggerPin, self.echoPin, celsius=self.celsius)
                    sleep(.01)
        except RuntimeError:
            pass
        except KeyboardInterrupt:
            self.stop()
        except Exception:
            print(traceback.format_exc())


class PalangControl:
    def __init__(self, pinEnableA=26, pinEnableB=21, pinIn1=19, pinIn2=13, pinIn3=20, pinIn4=16, delayTime=.25, upSteps=6, downSteps=6):
        self.pinEnableA = pinEnableA
        self.pinEnableB = pinEnableB
        self.pinIn1 = pinIn1
        self.pinIn2 = pinIn2
        self.pinIn3 = pinIn3
        self.pinIn4 = pinIn4
        self.delayTime = delayTime
        self.upSteps = upSteps
        self.downSteps = downSteps
        IO.setmode(IO.BCM)
        IO.setwarnings(False)
        IO.setup(self.pinIn1, IO.OUT)
        IO.setup(self.pinIn2, IO.OUT)
        IO.setup(self.pinEnableA, IO.OUT)
        IO.setup(self.pinIn3, IO.OUT)
        IO.setup(self.pinIn4, IO.OUT)
        IO.setup(self.pinEnableB, IO.OUT)
        self.pinOff(self.pinIn1)
        self.pinOff(self.pinIn2)
        self.pinOff(self.pinIn3)
        self.pinOff(self.pinIn4)
        self.pwmA = IO.PWM(self.pinEnableA, 1000)
        self.pwmA.start(0)
        self.pwmA.ChangeDutyCycle(0)
        self.pwmB = IO.PWM(self.pinEnableB, 1000)
        self.pwmB.start(0)
        self.pwmB.ChangeDutyCycle(0)
        self.stopped = False

    def pinOff(self, pin):
        IO.setup(pin, IO.IN)

    def pinOn(self, pin):
        IO.setup(pin, IO.OUT, initial=IO.HIGH)

    def frange(self, start, stop, numelements):
        if start == 0:
            start = 1
        if stop == 0:
            stop = 1
        if numelements == 0:
            numelements = 0.001
        incr = (stop - start) / numelements
        return (start + x * incr for x in range(numelements))

    def exprange(self, start, stop, numelements):
        if start == 0:
            start = 1
        if stop == 0:
            stop = 1
        if numelements == 0:
            numelements = 0.001
        return (exp(x) for x in self.frange(log(start), log(stop), numelements))

    def up(self, gateA=0, gateB=0, upSteps=None, dcMax=42, dcMin=36):
        if upSteps != None:
            self.upSteps = upSteps
        try:
            while True:
                if self.stopped:
                    self.pwmA.ChangeDutyCycle(0)
                    self.pwmB.ChangeDutyCycle(0)
                    self.stopMotor()
                    break
                else:
                    if upSteps == None:
                        upSteps = self.upSteps
                    dc = dcMax
                    if gateA is 1 and gateB is 0:
                        self.pwmA.ChangeDutyCycle(dcMax)
                    elif gateB is 1 and gateA is 0:
                        self.pwmB.ChangeDutyCycle(dcMax)
                    elif gateA is 1 and gateB is 1:
                        self.pwmA.ChangeDutyCycle(dcMax)
                        self.pwmB.ChangeDutyCycle(dcMax)
                    for i in self.exprange(dcMax, dcMin, upSteps):
                        if gateA is 1 and gateB is 0:
                            self.pinOff(self.pinIn1)
                            self.pinOn(self.pinIn2)
                            sleep(self.delayTime)
                            self.stopMotor()
                            if dc <= 0:
                                dc = 0
                            self.pwmA.ChangeDutyCycle(i)
                            #print("Gate A", i)
                        elif gateB is 1 and gateA is 0:
                            self.pinOff(self.pinIn3)
                            self.pinOn(self.pinIn4)
                            sleep(self.delayTime)
                            self.stopMotor()
                            if dc <= 0:
                                dc = 0
                            self.pwmB.ChangeDutyCycle(i)
                            #print("Gate B", i)
                        elif gateA is 1 and gateB is 1:
                            self.pinOff(self.pinIn1)
                            self.pinOn(self.pinIn2)
                            self.pinOff(self.pinIn3)
                            self.pinOn(self.pinIn4)
                            sleep(self.delayTime)
                            self.stopMotor()
                            if dc <= 0:
                                dc = 0
                            self.pwmA.ChangeDutyCycle(i)
                            self.pwmB.ChangeDutyCycle(i)
                            #print("Gate A & Gate B", i)
                    self.pwmA.ChangeDutyCycle(0)
                    self.pwmB.ChangeDutyCycle(0)
                    self.stopped = True
                sleep(.01)
        except KeyboardInterrupt:
            self.stop()

    def upward(self, gateA=0, gateB=0):
        self.stopped = False
        upwardthread = Thread(target=self.up,
                              name='UpwardThread', args=(gateA, gateB))
        upwardthread.daemon = True
        upwardthread.start()
        return self

    def down(self, gateA=0, gateB=0, downSteps=None, dcMax=34, dcMin=24):
        if downSteps != None:
            self.downSteps = downSteps
        try:
            while True:
                if self.stopped:
                    self.pwmA.ChangeDutyCycle(0)
                    self.pwmB.ChangeDutyCycle(0)
                    self.stopMotor()
                    break
                else:
                    if downSteps == None:
                        downSteps = self.downSteps
                    dc = dcMax
                    if gateA is 1 and gateB is 0:
                        self.pwmA.ChangeDutyCycle(dcMax)
                    elif gateB is 1 and gateA is 0:
                        self.pwmB.ChangeDutyCycle(dcMax)
                    elif gateA is 1 and gateB is 1:
                        self.pwmA.ChangeDutyCycle(dcMax)
                        self.pwmB.ChangeDutyCycle(dcMax)
                    for _ in range(1, downSteps + 1):
                        if gateA is 1 and gateB is 0:
                            self.pinOn(self.pinIn1)
                            self.pinOff(self.pinIn2)
                            sleep(self.delayTime)
                            self.stop()
                            steps = ((dc - dcMin) / (downSteps))
                            dc = dc - steps * 2
                            if dc <= 0:
                                dc = 0
                            self.pwmA.ChangeDutyCycle(dc)
                            #print("Gate A", dc, abs(steps))
                        elif gateB is 1 and gateA is 0:
                            self.pinOn(self.pinIn3)
                            self.pinOff(self.pinIn4)
                            sleep(self.delayTime)
                            self.stopMotor()
                            steps = ((dc - dcMin) / (downSteps))
                            dc = dc - steps * 2
                            if dc <= 0:
                                dc = 0
                            self.pwmB.ChangeDutyCycle(dc)
                            #print("Gate B", dc, abs(steps))
                        elif gateA is 1 and gateB is 1:
                            self.pinOn(self.pinIn1)
                            self.pinOff(self.pinIn2)
                            self.pinOn(self.pinIn3)
                            self.pinOff(self.pinIn4)
                            sleep(self.delayTime)
                            self.stopMotor()
                            steps = ((dc - dcMin) / (downSteps))
                            dc = dc - steps * 2
                            if dc <= 0:
                                dc = 0
                            self.pwmA.ChangeDutyCycle(dc)
                            self.pwmB.ChangeDutyCycle(dc)
                            #print("Gate A & Gate B", dc, abs(steps))
                    self.pwmA.ChangeDutyCycle(0)
                    self.pwmB.ChangeDutyCycle(0)
                    self.stopped = True
                sleep(.01)
        except KeyboardInterrupt:
            self.stop()

    def downward(self, gateA=0, gateB=0):
        self.stopped = False
        downwardthread = Thread(target=self.down,
                                name='DownwardThread', args=(gateA, gateB))
        downwardthread.daemon = True
        downwardthread.start()
        return self

    def stopMotor(self):
        self.pinOff(self.pinIn1)
        self.pinOff(self.pinIn2)
        self.pinOff(self.pinIn3)
        self.pinOff(self.pinIn4)

    def stop(self):
        self.stopped = True


class ObjectClassifier:
    def __init__(self, src, args, minFaceSize=(14, 28), maxWidth=640, maxHeight=480, forceResize=False, abcClip=.75):
        self.src = src
        self.minFaceSize = minFaceSize
        self.objectPath = 'haarcascade_frontalface_default.xml'
        self.objectCascade = cv2.CascadeClassifier(self.objectPath)
        self.args = args
        self.forceResize = forceResize
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        self.abcClip = abcClip
        self.streamthread = Thread()
        self.isProcessing = False
        self.objectDetected = 0
        self.objectDetectedTmp = 0
        self.it = 0
        self.frameskip = int(args["frameskip"])
        self.avgfps = 0
        self.frames = 0
        self.starttime = 0
        self.stopped = False
        self.vs = None
        self.frame = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameDetect = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameStack = np.hstack([imutils.resize(self.frame, height=192, width=340),
                                     imutils.resize(self.frame, height=192, width=340)])
        sleep(.5)

    def imageProcessing(self):
        def drawText(frame, text, startX=int(self.maxWidth * .025), startY=int(self.maxHeight * .05), textColor=(64, 255, 96),  fontSize=1, thickness=1):
            if thickness < 1:
                thickness = 1
            cv2.putText(frame, str(text), (int(startX), int(startY)),
                        cv2.FONT_HERSHEY_SIMPLEX, fontSize, (textColor), int(thickness))
            return frame

        def getAvgFps():
            fps = self.frames / (datetime.datetime.now() -
                                 self.starttime).total_seconds()
            if self.frames >= 128:
                self.frames = 0
                self.starttime = datetime.datetime.now()
            return fps

        def processImage():
            self.it += 1
            self.frames += 1
            if self.args['abc'] != 'no':
                try:
                    self.abcClip = float(self.args['abc'])
                except ValueError:
                    pass
                self.frame = self.abc(
                    self.frame, clip_hist_percent=self.abcClip)[0]
            self.frameDetect = self.objectClassifier(raw)
            self.frameStack = np.hstack([imutils.resize(self.frame, height=192, width=340),
                                         imutils.resize(self.frameDetect, height=192, width=340)])
            self.avgfps = getAvgFps()
            if isinstance(self.vs, (list, tuple, np.ndarray)):
                if not self.vs.more:
                    self.stop()
            self.isProcessing = False

        try:
            self.starttime = datetime.datetime.now()
            while True:
                sleep(.01)
                if self.stopped:
                    self.isProcessing = False
                    break
                else:
                    self.isProcessing = True
                    raw = None
                    if OS_TYPE == WINDOWS:
                        raw = self.vs.read()[1]
                    else:
                        raw = self.vs.read()

                    if isinstance(raw, (list, tuple, np.ndarray)):
                        (h, w) = raw.shape[:2]
                        if h > self.maxHeight or w > self.maxWidth or self.forceResize:
                            raw = imutils.resize(
                                raw, width=self.maxWidth, height=self.maxHeight)
                        if int(self.args["frameskip"]) > 0:
                            if self.it % self.frameskip == 0:
                                self.frame = raw
                                self.frames += 1
                                processImage()
                            else:
                                self.it += 1
                                self.frames += 1
                        else:
                            self.frame = raw
                            processImage()
        except KeyboardInterrupt:
            self.stop()
        except Exception:
            print(traceback.format_exc())
            self.frameStack = drawText(self.frameStack, traceback.format_exc(
            ), (384 * .025), (680 * .025), (96, 64, 255), .3)

    def objectClassifier(self, frame):
        self.objectDetectedTmp = 0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        classifications = self.objectCascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=3, minSize=(14, 28))

        for (x, y, w, h) in classifications:
            colorBox = (255, 0, 0)
            colorText = (255, 255, 255)
            rw = int(w * .01)
            rh = int(h * .01)
            y = y - rw if y - rw > rw else y + rw
            frame = cv2.rectangle(
                frame, (x, y), (x + w, y + h), color=colorBox, thickness=2)
            frame = cv2.rectangle(
                frame, (x, y - rw), (x + w, y), color=colorBox, thickness=-1)
            self.objectDetectedTmp = len(classifications)

        if self.objectDetected != self.objectDetectedTmp:
            self.objectDetected = self.objectDetectedTmp

        cv2.putText(frame, "Total detected: %d" % self.objectDetected,
                    (int(self.maxWidth * .025), int(self.maxHeight * .05)),
                    cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)

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

    def fps(self):
        return self.avgfps

    def getFrameDetection(self):
        return self.frameDetect

    def getFrame(self):
        return self.frame

    def getFrameStack(self):
        return self.frameStack

    def getFrameDetectionCount(self):
        return self.objectDetected

    def getDetectionOnce(self, started=False):
        processingState = False
        if started == False:
            self.start()
        if processingState == False:
            try:
                while True:
                    sleep(.01)
                    if self.isProcessing is True:
                        processingState = True
                        continue
                    elif processingState is True and self.isProcessing == False:
                        self.stop()
                        return self.objectDetected
            except KeyboardInterrupt:
                self.stop()
        else:
            self.getDetectionOnce(started=True)

    def start(self):
        if self.args["video"] != 'stream':
            self.vs = FileVideoStream(self.args["video"]).start()
            sleep(.5)
        else:
            if OS_TYPE == WINDOWS:
                self.vs = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
            else:
                self.vs = VideoStream(self.src).start()
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
        if OS_TYPE != RASPBIAN:
            cv2.destroyAllWindows()


# Run main function
if __name__ == '__main__':
    m = main()
    m.start()
