#!/usr/bin/python3

from firebase import Firebase #https://pypi.org/project/firebase/ : sudo pip3 install firebase python_jwt gcloud sseclient requests_toolbelt
from imutils.video import VideoStream
from threading import Thread, Lock
from random import uniform
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import numpy as np
import traceback
import argparse
import imutils
import curses
import base64
import socket
import cv2
import time
import random
import sys
import os
import json
import tracemalloc
from queue import Queue
from flask import request as FlaskRequest
from flask import Response as FlaskResponse
from flask import Flask, render_template, jsonify
from flask_cors import CORS as FlaskCORS
import logging
log = logging.getLogger('werkzeug')
log.disabled = True
LOCK = Lock()

TEST_MODE = True

# check os type
RASPBIAN = 'raspbian'
LINUX = 'linux'
MACOS = 'macos'
WINDOWS = 'windows'
OS_TYPE = ''
# DHT
DHT_LIB = None
DHT_SENSOR = None
if sys.platform == LINUX or sys.platform == "linux2":
    try:
        import RPi.GPIO as GPIO
        import Adafruit_DHT

        OS_TYPE = RASPBIAN
        GPIO.setwarnings(False)
        DHT_LIB = Adafruit_DHT
        DHT_SENSOR = Adafruit_DHT.DHT22
    except (ImportError, RuntimeError):
        OS_TYPE = LINUX
elif sys.platform == "darwin":
    OS_TYPE = MACOS
elif sys.platform == "win32":
    OS_TYPE = WINDOWS
    from GPIOEmulator.EmulatorGUI import GPIO
    GPIO.setwarnings(False)


def millis(): return int(round(time.time() * 1000)) & 0xffffffff

def seconds(): return int(round(time.time())) & 0xffffffff


def process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss


def main():
    def delay(fps, x=2):
        if fps < 1:
            return 1
        return 1 / (fps * x)

    def imageStream(host="0.0.0.0", port="5000", debug=False, secure=False):
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

        def encodeImageStream():
            flag = None
            encodedImage = None
            try:
                while True:
                    with LOCK:
                        #encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 37]
                        #_, frame = newDetect.getFrame()
                        #(flag, encodedImage) = cv2.imencode(".jpg", frame, encode_param)
                        # (flag, encodedImage) = cv2.imencode(".png", frame)
                        encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), 37]
                        frame = newDetect.getFrame()
                        (flag, encodedImage) = cv2.imencode(".webp", frame, encode_param)
                        if not flag:
                            continue
                    #yield(b'--frame\r\n' b'Content-Type: image/jpg\r\n\r\n' +
                    #      bytearray(encodedImage) + b'\r\n')
                    # yield(b'--frame\r\n' b'Content-Type: image/png\r\n\r\n' +
                    #      bytearray(encodedImage) + b'\r\n')
                    yield(b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' +
                          bytearray(encodedImage) + b'\r\n')
                    time.sleep(0.1667)
            except Exception as e:
                print(e)
                return

        def encodeImage():
            try:
                with LOCK:
                    #encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 37]
                    #_, frame = newDetect.getFrame()
                    #(flag, encodedImage) = cv2.imencode(".jpg", frame, encode_param)
                    # (flag, encodedImage) = cv2.imencode(".png", frame)
                    encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), 37]
                    frame = newDetect.getFrame()
                    (flag, encodedImage) = cv2.imencode(".webp", frame, encode_param)
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
            encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), 37]
            frame = newDetect.getFrame()
            (flag, encodedImage) = cv2.imencode(".webp", frame, encode_param)
            resp = FlaskResponse(encodedImage, mimetype="image/webp", content_type="image/webp")
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

    def cleanup():
        sys.exit()

    def micros(): return int(round(time.time() * 1000000)) & 0xffffffff

    def millis(): return int(round(time.time() * 1000)) & 0xffffffff

    def seconds(): return int(round(time.time())) & 0xffffffff

    def dbUpdateNotif(notif): #0: kontaminasi, 1: balik, 2: diangkat
        firebaseDb.child("jtd").child("Oncom").update({"notif":notif})

    def dbUpdateColor(b, g, r):
        color = {
            'b': b,
            'g': g,
            'r': r
        }
        firebaseDb.child("jtd").child("Oncom").child("color").push(color)

    def dbUpdateSensor(moist, temp):
        firebaseDb.child("jtd").child("Oncom").update({"moist":moist})
        firebaseDb.child("jtd").child("Oncom").update({"temp":temp})

    def dbSetBlacked(blacked):
        firebaseDb.child("jtd").child("Oncom").update({"isBlacked":blacked})

    def dbSetPaused(pause):
        firebaseDb.child("jtd").child("Oncom").update({"paused":pause})

    def dbSetFlipped(flip):
        firebaseDb.child("jtd").child("Oncom").update({"isFlipped":flip})

    def dbSetReset(reset):
        firebaseDb.child("jtd").child("Oncom").update({"isResetted":reset})

    def dbSetLifted(reset):
        firebaseDb.child("jtd").child("Oncom").update({"isLifted":reset})

    def dbIsResetted():
        isResetted = firebaseDb.child("jtd").child("Oncom").child("resetted").get().val()
        return isResetted

    def dbIsFlipped():
        isFlipped = firebaseDb.child("jtd").child("Oncom").child("isFlipped").get().val()
        return isFlipped

    def dbIsLifted():
        isLifted = firebaseDb.child("jtd").child("Oncom").child("isLifted").get().val()
        return isLifted

    def dbSetSensor(humid, temp):
        firebaseDb.child("jtd").child("Oncom").update({"moist":humid})
        firebaseDb.child("jtd").child("Oncom").update({"temp":temp})

    def dbSaveImage(img, name, path):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 37]
        (flag, encodedImage) = cv2.imencode(name, img, encode_param)
        cv2.imwrite(path + name, encodedImage)
        storage.child(f"images/{name}").put(path + name)

    def resetSystem():
        pauseOncomSystem = False
        dbSetFlipped(False)
        dbSetBlacked(False)
        dbSetPaused(False)
        dbSetReset(False)
        dbSetLifted(False)

    # Vars
    # Lamp relay
    LAMP_PIN = 5
    # DHT
    DHT_LIB = None
    DHT_SENSOR = None
    DHT_PIN = 6
    # L298N
    IN_1_PIN = 13
    IN_2_PIN = 19
    ENABLE_A_PIN = 26
    IN_3_PIN = 16
    IN_4_PIN = 20
    ENABLE_B_PIN = 21

    # contruct argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", default="camera",
                    help="path to input image")
    ap.add_argument("-a", "--abc", default="no",
                    help="auto brightness and contrast clip histogram, ex. -a 0.5")
    args = vars(ap.parse_args())

    config = {
        "apiKey": "AIzaSyDt0MmiHszpy-EkSIDbTXbiVu_OoXIxmDc",
        "authDomain": "ycmlg-sub1.firebaseapp.com",
        "databaseURL": "https://ycmlg-sub1.firebaseio.com/",
        "storageBucket": "ycmlg-sub1.appspot.com"
    }
    firebase = Firebase(config)
    firebaseDb = firebase.database()

    e1 = "Putih"
    e2 = "Hitam"
    e3 = "Oren"

    # define the list of color range boundaries
    boundaries = {
        # B G R lower, B G R upper
        # 'hitam': ([0, 0, 0], [150, 160, 170], e2, 0.002),
        'putih': ([95, 103, 111], [255, 255, 255], e1, 0.1),
        'hitam': ([0, 0, 0], [150, 150, 150], e2, 0.2),
        'oren': ([30, 91, 139], [177, 200, 200], e3, 0.1),
    }

    # source for camera. Unused when using image as source
    src = {'src': 0, 'path': args['image']}
    flipThresh = 50
    newDetect = Detect(src, boundaries, args, flipThresh)
    windowLabel = 'Loading'
    labelWidth1 = 0

    # fan & heater
    DHT_PARAM = {
        'dht': DHT_LIB,
        'dhtSensor': DHT_SENSOR,
        'dhtPin': DHT_PIN,
    }
    FAN_PARAM = {
        'in1': IN_1_PIN,
        'in2': IN_2_PIN,
        'enA': ENABLE_A_PIN,
        'in3': IN_3_PIN,
        'in4': IN_4_PIN,
        'enB': ENABLE_B_PIN,
        'pwm': {
            'off': 0,
            'lo': 50,
            'hi': 100,
        }
    }
    HEATER_PARAM = {
        'off': 0,
        'lo': 50,
        'hi': 100,
    }
    newATC = None
    if OS_TYPE != WINDOWS:
        newATC = AirTempControl(DHT_PARAM, FAN_PARAM, HEATER_PARAM, LAMP_PIN)

    humidLo = (0, 45)
    humidMed = (45, 65)
    humidHi = (65, 100)

    tempLo = (0, 28)
    tempMed = (28, 35)
    tempHi = (35, 100)

    fanOff = (
        (humidMed, tempMed),
    )
    fanLo = (
        (humidLo, tempLo),
        (humidLo, tempMed),
        (humidMed, tempLo),
        (humidHi, tempMed),
    )
    fanHi = (
        (humidLo, tempHi),
        (humidMed, tempHi),
        (humidHi, tempLo),
        (humidHi, tempHi),
    )
    fanRules = {
        'id': ('off', 'lo', 'hi'),
        'rule': (fanOff, fanLo, fanHi)
    }

    heaterOff = (
        (humidMed, tempMed),
        (humidMed, tempHi),
        (humidHi, tempMed),
        (humidHi, tempHi)
    )
    heaterLo = (
        (humidLo, tempHi),
        (humidMed, tempLo),
        (humidHi, tempLo)
    )
    heaterHi = (
        (humidLo, tempLo),
        (humidLo, tempMed)
    )
    heaterRules = {
        'id': ('off', 'lo', 'hi'),
        'rule': (heaterOff, heaterLo, heaterHi)
    }


    pauseOncomSystem = False

    # timer
    dbCheckTimer = seconds()
    dbCheckInterval = 2

    sensorCheckTimer = millis()
    sensorCheckInterval = 250
    detectionRunningTimeInterval = 50 #* 3600   #   50 hours

    try:
        #screen = curses.initscr()
        #screen.refresh()
        imageStream(host='0.0.0.0', port='5000', secure=False)
        newDetect.start()
        traceTime = seconds()
        resetSystem()
        isLamp = False
        isNewLamp = False
        while True:
            #------------------------------------ Oncom Detection ---------------------------------------//
            label, frame1 = newDetect.getStatus()
            detectionRunningTime = newDetect.getDetectionRunTime()
            isLamp = newDetect.getLamp()
            if isNewLamp != isLamp:
                isLamp = isNewLamp
                if OS_TYPE != WINDOWS:
                    newATC.setLamp(isLamp)
            if detectionRunningTime <= detectionRunningTimeInterval:
                # oncom contaminated
                if newDetect.isOncomBlack() or newDetect.isPaused():
                    if seconds() - dbCheckTimer >= dbCheckInterval:
                        print('----------------- Oncom Detection -----------------')
                        dbSetPaused(True)
                        # oncom is resetted
                        isResetted = dbIsResetted()
                        if isResetted:
                            # continue
                            newDetect.hasResetted(True)
                            newDetect.setIsBlack(False)
                            newDetect.setPaused(False)
                            dbSetBlacked(False)
                            dbSetPaused(False)
                            dbSetReset(False)

                        dbCheckTimer = seconds()
                        print('---------------------------------------------------')
                else:
                    if (seconds() - dbCheckTimer >= dbCheckInterval) and (not newDetect.isOncomProcessDone()):
                        print('----------------- Oncom Detection -----------------')
                        # oncom is flipped
                        isFlipped = dbIsFlipped()
                        b, g, r = newDetect.getColor()
                        dbUpdateColor(b, g, r)
                        newDetect.setIsFlipped(isFlipped)
                        #print(isFlipped, seconds(), dbCheckTimer, dbCheckInterval)
                        if not isFlipped:
                            # continue detection
                            newDetect.setIsBlack(False)
                            newDetect.setPaused(False)
                            dbSetBlacked(False)
                            dbSetPaused(False)

                        dbCheckTimer = seconds()
                        print('---------------------------------------------------')
            elif newDetect.isOncomProcessDone():
                pauseOncomSystem = True

            if not pauseOncomSystem:
                #------------------------------------ ATC ---------------------------------------//
                if millis() - sensorCheckTimer >= sensorCheckInterval:
                    if OS_TYPE != WINDOWS:
                        humid = newATC.getHumid()
                        temp = newATC.getTemp()
                        fanSpeed = newATC.getState(humid, temp, fanRules)
                        heaterTemp = newATC.getState(humid, temp, heaterRules)
                        newATC.fanControl(fanSpeed)
                        newATC.heaterControl(heaterTemp)
                        print('----------------------- ATC -----------------------')
                        print('H:', humid, 'T:', temp)
                        print('Fan speed:', fanSpeed)
                        print('Heater temp:', heaterTemp)
                        print('---------------------------------------------------')

                    sensorCheckTimer = millis()

                #------------------------------------ Info ---------------------------------------//
                memCurrent, memPeak = tracemalloc.get_traced_memory()

                if label != None:
                    if windowLabel != label:
                        windowLabel = label
                        if len(label) > labelWidth1:
                            labelWidth1 = len(label)
                        #screen.clrtoeol()
                        #screen.refresh()
                        #screen.addstr(0, 0, "\rSource 1; Port %s; Detected %s" % (
                        #    src['src'], windowLabel.ljust(labelWidth1)))
                        print("\rSource 1; Port %s; Detected %s" % (
                            src['src'], windowLabel.ljust(labelWidth1)))
                else:
                    label = windowLabel

                #screen.clrtoeol()
                #screen.refresh()

                if seconds() - traceTime >= 2:
                    print('----------------------- Info ----------------------')
                    #screen.clrtoeol()
                    #screen.refresh()
                    #screen.addstr(3, 0, "\r[Memory] Current: %fMB - Peak: %fMiB" %
                    #              (memCurrent / 10**6, memPeak / 10**6))
                    print("\r[Memory] Current: %fMB - Peak: %fMiB" %
                                  (memCurrent / 10**6, memPeak / 10**6))
                    traceTime = seconds()
                    print('---------------------------------------------------')

                #------------------------------------//
                if OS_TYPE == 'windows':
                    cv2.imshow("Input / Output Source 1", newDetect.getFrameStack())
                    if ord('q') == cv2.waitKey(10):
                        newDetect.stop()
                        cv2.destroyAllWindows()
                        #curses.endwin()
                        sys.exit(0)

                #if newDetect.isStopped():
                #    sys.exit(0)

            if (millis() - sensorCheckTimer >= sensorCheckInterval) and pauseOncomSystem:
                print('- APP PAUSED -')
                isResetted = dbIsResetted()
                if isResetted:
                    resetSystem()

                sensorCheckTimer = millis()

            time.sleep(0.05)
    except ConnectionError as e:
        print(e)
    except Exception:
        newDetect.stop()
        cv2.destroyAllWindows()
        #curses.endwin()
        print(traceback.format_exc())
        sys.exit(str(traceback.format_exc()))
    except KeyboardInterrupt:
        newDetect.stop()
        cv2.destroyAllWindows()
        #curses.endwin()
        sys.exit(0)


class AirTempControl():
    def __init__(self, dhtParam, fanParam, heaterParam, lampPin, dht=True, test=False): #Adafruit_DHT, DHT_SENSOR, DHT_PIN
        self.fanSpeed = 0
        self.fanSpeedPWM = fanParam['pwm']
        self.heaterTemp = 0
        self.heaterTempPWM =  heaterParam
        self.dht = dhtParam['dht']
        self.dhtSensor = dhtParam['dhtSensor']
        self.dhtPin = dhtParam['dhtPin']
        self.in1 = fanParam['in1']
        self.in2 = fanParam['in2']
        self.enA = fanParam['enA']
        self.in3 = fanParam['in3']
        self.in4 = fanParam['in4']
        self.enB = fanParam['enB']
        self.lampPin = lampPin
        self.humid = 0
        self.temp = 0
        self.test = test
        self.stopped = True

        # setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.enA, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)
        GPIO.setup(self.in4, GPIO.OUT)
        GPIO.setup(self.enB, GPIO.OUT)

        # set fan 1 direction
        self.pinOn(self.in1)
        self.pinOff(self.in2)

        # set fan/heater 2 direction
        self.pinOn(self.in3)
        self.pinOff(self.in4)

        # setup Fan PWM
        self.pwmA = GPIO.PWM(self.enA, 1000)
        self.pwmA.start(0)
        self.pwmA.ChangeDutyCycle(0)
        self.pwmB = GPIO.PWM(self.enB, 1000)
        self.pwmB.start(0)
        self.pwmB.ChangeDutyCycle(0)
        
        # DHT
        if dht:
            self.setDHT(True)

    def pinOff(self, pin):
        GPIO.setup(pin, GPIO.IN)

    def pinOn(self, pin):
        GPIO.setup(pin, GPIO.OUT, initial = GPIO.HIGH)

    def setLamp(self, state=False):
        if state:
            self.pinOn(self.lampPin)
        else:
            self.pinOff(self.lampPin)
        

    def setDHT(self, start = True):
        def start():
            if self.stopped:
                return
            humid, temp = dht.read_retry(self.dhtSensor, self.dhtPin)
            if humid is not None and temp is not None:
                self.humid, self.temp = (humid, temp)
            time.sleep(.1)

        if self.stopped and start:
            self.stopped = False
            dhtThread = Thread(target=start,
                                  name='Read DHT', args=())
            dhtThread.daemon = True
            dhtThread.start()
        else:
            self.stopped = True

    def getHumid(self):
        if self.test:
            return int(uniform(0, 100))
        return self.humid

    def getTemp(self):
        if self.test:
            return int(uniform(0, 100))
        return self.temp

    # off, lo, hi
    def fanControl(self, speed='off', raw=None):
        print('fan speed:', speed)
        if raw != None:
            self.pwmA.ChangeDutyCycle(raw)
        else:
            self.pwmA.ChangeDutyCycle(self.fanSpeedPWM[speed])
        self.fanSpeed = speed

    # off, lo, hi
    def heaterControl(self, temp='off', raw=None):
        if raw != None:
            self.pwmB.ChangeDutyCycle(raw)
        else:
            self.pwmB.ChangeDutyCycle(self.fanSpeedPWM[temp])
        self.heaterTemp = temp

    def getState(self, humid, temp, rules):
        def getTruthy(humid, temp, rule):
            return rule[0][0] <= int(humid) < rule[0][1] and rule[1][0] <= int(temp) < rule[1][1]
        rulePos = 0
        ruleWhich = rules['id'][0]
        while rulePos < len(rules['rule']):
            for rule in rules['rule'][rulePos]:
                if getTruthy(humid, temp, rule):
                    ruleWhich = rules['id'][rulePos]
            rulePos += 1
        return (ruleWhich)

class Detect():
    def __init__(self, src, boundaries, args, flipThresh = 48, captureThresh = 4):
        self.src = src['src']
        self.imagePath = src['path']
        self.boundaries = boundaries
        self.args = args
        self.vs = None
        self.frame = None
        self.frameStack = None
        self.OS_TYPE = "Unknown"
        self.label = "None detected"
        self.imgColor = [255, 255, 255] # BGR
        self.detected = False
        self.stopped = False
        self.paused = False
        self.isWhite = False
        self.isBlack = False
        self.isOrange = False
        self.isFlipped = False
        self.forDbImage = []
        self.forDbImageName = "image.jpg"
        self.forDbImagePath = "./"
        self.lcnt = 1
        self.notifState = ('baru', 'oncom putih')
        self.pausedTime = 0
        self.oncomProcessDone = False
        self.lampWait = 2
        self.setLamp = False
        self.captureTimer = seconds()
        self.systemRunTimer = seconds()
        if TEST_MODE:
            self.flipThresh = self.systemRunTimer + 48
            self.captureInterval = 4
        else:
            self.flipThresh = self.systemRunTimer + (3600 * flipThresh) # hour
            self.captureInterval = 3600 * captureThresh #hour


    def detectQ(self):
        def averageColor(img):
            acRow = np.average(img, axis=0)
            b, g, r = np.average(acRow, axis=0)
            return [b, g, r]

        def checkColor(boundary, image):
            self.label = None
            self.detected = False
            output = []
            label = "none"
            imageGray = cv2.cvtColor(
                image, cv2.COLOR_BGR2GRAY)
            imsize = np.size(image)
            # create NumPy arrays from the boundaries
            lower = np.array(boundary[0], dtype="uint8")
            upper = np.array(boundary[1], dtype="uint8")
            label = boundary[2]
            treshhold = boundary[3]
            # find the colors within the specified boundaries and apply
            # the mask
            mask = cv2.inRange(image, lower, upper)
            output = cv2.bitwise_and(image, image, mask=mask)
            outputGray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
            imnz = cv2.countNonZero(outputGray)
            t = imsize * treshhold
            if int(imnz) >= int(t):
                return (True, label, imsize, imnz, t, imageGray, mask, output, outputGray)
            return (False, label, imsize, imnz, t, imageGray, mask, output, outputGray)

        def printColorInfo(i, l, px, npx, t):
            print(f"For {l}: {i}")
            print("Image size:", px)
            print("NonZero size:", npx, "-", f"{npx/px}%")
            print("Thresh size:", t, "-", f"{t/px}%")
            print("")

        def getImage():
            if isinstance(self.frame, (list, tuple, np.ndarray)):
                if self.imagePath == "camera":
                    if self.OS_TYPE == 'windows':
                        self.frame = self.vs.read()[1]
                    else:
                        self.frame = self.vs.read()
                else:
                    self.frame = cv2.imread(self.imagePath)

                if self.args["abc"] != "no":
                    self.frame = self.abc(
                        self.frame, clip_hist_percent=float(self.args["abc"]))[0]

                if isinstance(self.frame, (list, tuple, np.ndarray)):
                    return imutils.resize(self.frame, height=480, width=640)

            self.stop()
            print('Image is empty! Cannot continue, please check video/image source!')

        def saveImage(image, imageGray, mask, output, outputGray):
            savePath = os.getcwd() + '\\imgs'
            imageName = self.imagePath
            if self.imagePath != "camera":
                imageName = str(imageName)[imageName.rfind(
                    '\\')+1:imageName.rfind('.')].replace(' ', '_')
            else:
                imageName = imageName + str(self.src)

            path = self.makedirs(savePath, imageName)
            cv2.imwrite(
                path + '1.[Gray]_' + imageName + '.png', imageGray)
            cv2.imwrite(
                path + '2.[Mask]_' + imageName + '.png', mask)
            cv2.imwrite(
                path + '3.[Output]_' + imageName + '.png', output)
            cv2.imwrite(
                path + '4.[OutputGray]_' + imageName + '.png', outputGray)
            cv2.imwrite(
                path + '5.[Stack]_' + imageName + '.png', np.hstack([image, output]))

        # process
        self.stopped = False
        if sys.platform == "linux" or sys.platform == "linux2":
            try:
                import RPi.GPIO as GPIO
                self.OS_TYPE = 'raspbianlinux'
            except (ImportError, RuntimeError):
                self.OS_TYPE = 'linux'
        elif sys.platform == "darwin":
            self.OS_TYPE = 'macos'
        elif sys.platform == "win32":
            self.OS_TYPE = 'windows'

        if self.imagePath == "camera":
            if self.OS_TYPE == 'windows':
                self.vs = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
                self.frame = self.vs.read()[1]
            else:
                self.vs = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
                self.frame = self.vs.read()[1]
                #self.vs = VideoStream(self.src).start()
                #self.frame = self.vs.read()
        else:
            self.frame = cv2.imread(self.imagePath)

        if self.args["abc"] != "no":
            self.frame = self.abc(
                self.frame, clip_hist_percent=float(self.args["abc"]))[0]

        time.sleep(0.5)

        while True:
            try:
                self.systemRunTimer = seconds()
                if self.stopped:
                    return
                elif self.paused:
                    time.sleep(0.5)
                else:
                    if self.isCaptureTime():
                        image = getImage()

                        # check for white
                        self.isWhite, labelW, totalPx, nonZeroPx, thres, imageGrayW, maskW, outputW, outputWGray = checkColor(
                            self.boundaries['putih'], image)
                        #printColorInfo(self.isWhite, labelW, totalPx, nonZeroPx, thres)
                        self.detected = self.isWhite

                        # check for black
                        self.isBlack, labelB, totalPx, nonZeroPx, thres, imageGrayB, maskB, outputB, outputBGray = checkColor(
                            self.boundaries['hitam'], image)
                        #printColorInfo(self.isBlack, labelB, totalPx, nonZeroPx, thres)
                        self.detected = self.isBlack

                        # check for orange
                        self.isOrange, labelO, totalPx, nonZeroPx, thres, imageGrayO, maskO, outputO, outputOGray = checkColor(
                            self.boundaries['oren'], image)
                        #printColorInfo(self.isOrange, labelO, totalPx, nonZeroPx, thres)
                        self.detected = self.isOrange

                        imageGraySave = []
                        maskSave = []
                        outputSave = []
                        outputGraySave = []

                        # range hitam
                        if self.isBlack:
                            self.setPaused(True)
                            imageGraySave = imageGrayB
                            maskSave = maskB
                            outputSave = outputB
                            outputGraySave = outputBGray
                            self.label = labelB
                            self.pausedTime = seconds()
                            self.detected = self.isBlack
                            self.notifState = ('busuk', 'Oncom terkontaminasi, tahan/jeda sistem')
                            print(self.notifState[1])
                        # range oren / di atas putih (tidak putih)
                        elif self.isOrange and not self.isBlack:
                            imageGraySave = imageGrayO
                            maskSave = maskO
                            outputSave = outputO
                            outputGraySave = outputOGray
                            self.label = labelO
                            self.detected = self.isOrange
                            if self.notifState[0] == 'baru':
                                self.notifState = ('dibalik', 'oncom berwarna oren, waktunya dibalik')
                            elif self.systemRunTimer >= self.flipThresh:
                                self.notifState = ('selesai', 'proses sudah 48 jam, oncom siap diangkat, matikan sistem')
                                self.oncomProcessDone = True
                            print(self.notifState[1])
                            if self.oncomProcessDone:
                                self.stop()
                        # range putih
                        elif self.isWhite and not self.isBlack:
                            imageGraySave = imageGrayW
                            maskSave = maskW
                            outputSave = outputW
                            outputGraySave = outputWGray
                            self.label = labelW
                            self.detected = self.isWhite
                            self.notifState = ('baru', 'oncom putih')
                            print(self.notifState[1])
                        elif not self.isWhite and not self.isBlack and not self.isOrange:
                            self.detected = False
                            self.label = "None detected"
                            self.stop()

                        if self.detected:
                            self.forDbImage = outputSave
                            self.imgColor = averageColor(image)
                            saveImage(image, imageGraySave, maskSave, outputSave, outputGraySave)
                            self.frameStack = np.hstack([
                                imutils.resize(image, height=192, width=340),
                                imutils.resize(outputSave, height=192, width=340)
                            ])
            except KeyboardInterrupt:
                self.stop()
            except Exception:
                print(traceback.format_exc())
                self.stop()
            time.sleep(0.1)

        if self.imagePath == "camera":
            self.vs.release()
        cv2.destroyAllWindows()

    def hasResetted(self, reset):
        self.paused = reset
        if TEST_MODE:
            self.imagePath = './images/1_tampilan_awal.jpg'
            self.frame = cv2.imread(self.imagePath)
            print(self.imagePath)
        print("continue detection")

    def isStopped(self):
        return self.stopped

    def isPaused(self):
        return self.paused

    def isCaptureTime(self):
        isTime = True if TEST_MODE else False
        if seconds() - self.captureTimer - self.lampWait >= self.captureInterval:
            self.captureTimer = seconds()
            isTime = True
        self.setLamp = True
        return isTime

    def isOncomWhite(self):
        return self.isWhite

    def isOncomBlack(self):
        return self.isBlack

    def isOncomOrange(self):
        return self.isOrange

    def isOncomProcessDone(self):
        return self.oncomProcessDone

    def isStopped(self):
        return self.stopped

    def setIsFlipped(self, flip):
        if flip:
            self.notifState = ('dibaik', 'oncom sudah dibalik')
        self.isFlipped = flip

    def setPaused(self, pause):
        if pause:
            print("Detection paused")
        if self.pausedTime > 0:
            self.flipThresh = self.flipThresh + (self.systemRunTimer - self.pausedTime)
            self.pausedTime = 0
        self.paused = pause

    def setIsBlack(self, black):
        self.isBlack = black

    def getLamp(self):
        lamp = self.setLamp
        self.setLamp = False
        return lamp

    def getStatus(self):
        if isinstance(self.frameStack, (list, tuple, np.ndarray)):
            return (self.label, self.frameStack)
        elif self.frameStack == None:
            height = 192
            width = 680
            img = np.zeros(shape=[height, width, 3], dtype=np.uint8)
            label = "Loading" + ("." * self.lcnt)
            cv2.putText(img, label,  (int(height*0.02), int(width*0.02)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            self.lcnt = 0 if self.lcnt == 52 else self.lcnt + 1
            return (self.label, img)

    def getFrame(self, width=640, height=480):
        if isinstance(self.frame, (list, tuple, np.ndarray)):
            frame = imutils.resize(self.frame, height=height, width=width)
            return frame
        elif self.frame == None:
            return np.zeros(shape=[height, width, 3], dtype=np.uint8)
    def getFrameStack(self, width=680, height=192):
        if isinstance(self.frame, (list, tuple, np.ndarray)):
            frameStack = imutils.resize(self.frameStack, height=height, width=width)
            return frameStack
        elif self.frameStack == None:
            return np.zeros(shape=[height, width, 3], dtype=np.uint8)

    def getDetectionRunTime(self):
        return self.systemRunTimer

    def getColor(self):
        return self.imgColor

    def getImageForDb(self):
        savePath = os.getcwd() + '\\imgs'
        imageName = self.imagePath
        if self.imagePath != "camera":
            imageName = str(imageName)[imageName.rfind(
                '\\')+1:imageName.rfind('.')].replace(' ', '_')
        else:
            imageName = imageName + str(self.src)
        self.forDbImagePath = self.makedirs(savePath, imageName)
        self.forDbImageName = datetime.now().strftime( '%Y-%m-%d_%H.%M.%S') + '.png'
        return (self.forDbImage, self.forDbImageName, self.forDbImagePath)

    def start(self):
        newThread = Thread(target=self.detectQ,
                           name='DetectImageQuality', args=())
        newThread.start()

    def stop(self):
        self.stopped = True

    # automatic brightness and contrast optimization with optional histogram clipping
    def abc(self, image, clip_hist_percent=0.5):
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

    # create directory / sub-directory
    def makedirs(self, parent, child):
        path = os.path.join(parent, child)
        try:
            os.makedirs(path, exist_ok=True)
            return path + '\\'
        except OSError as e:
            print("Cannot create directory '%s'" % child)
            return 'imgs\\'


if __name__ == '__main__':
    tracemalloc.start()
    main()
    tracemalloc.stop()
