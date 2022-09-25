#!/usr/bin/python3

from threading import Thread, Lock
import traceback
import argparse
import datetime
import imutils
import pymysql
import numpy as np
import cv2
import pickle
import sys
import time
from flask import Response
from flask import Flask
from flask import render_template
import logging
log = logging.getLogger('werkzeug')
# error only log
#log.setLevel(logging.ERROR)
# disable log
log.disabled = True


RASPBIAN = 'raspbian'
LINUX = 'linux'
MACOS = 'macos'
WINDOWS = 'windows'
OS_TYPE = ''
WIN_NAME = 'Cam'
MAX_WIDTH = 480
MAX_HEIGHT = 360
CANNY_THRES1 = 300
CANNY_THRES2 = 300
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
            try:
                while True:
                    with LOCK:
                        (flag, encodedImage) = cv2.imencode(".jpg", vcp.getFrameDetection())
                        if not flag:
                            continue
                    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                          bytearray(encodedImage) + b'\r\n')
                    time.sleep(.005)
            except:
                return

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
            print("[INFO] exiting...")
            try:
                result = """
                            UPDATE `pantausungai` SET `objectStatus` = '{0}' WHERE `pantausungai`.`id` = {1}
                        """.format(-1,  0)
                CC.execute(result)
                CONN.commit()
            except pymysql.err.InternalError as msg:
                print("Command skipped: ", msg)
            cv2.destroyAllWindows()
            CONN.close()
            vcp.stop()
            exit()
        except Exception as e:
            print('[INFO] forced exit! Exception:', e)
            exit()

    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--roifile", default='./pantauSungai.txt',
                    help="ROI file default: pantauSungai.txt")
    ap.add_argument("-t", "--template", default='./pantauSungai.jpg',
                    help="path to template image default: pantauSungai.jpg")
    ap.add_argument("-v", "--video", default='stream',
                    help="video src, file/stream/url, default: file")
    ap.add_argument("-d", "--threshold", default=15,
                    help="threshold in percent, default: 15")
    ap.add_argument("-f", "--frameskip", default=5,
                    help="frames to skip, default: 5")
    ap.add_argument("-a", "--abc", default="no",
                    help="auto brightness and contrast clip histogram, ex. -a 0.5")
    args = vars(ap.parse_args())


    VIDEO_SRC = './pantauSungai.mp4'
    if args['video'] != 'stream':
        VIDEO_SRC = args['video']
    roiPath = args['roifile']
    templateImg = cv2.imread(args['template'])
    threshPercent = args['threshold']
    frameskip = args['frameskip']

    vcp = VideoCannyProcessing(roiPath, templateImg, videoSrc=VIDEO_SRC, maxWidth=MAX_WIDTH, maxHeight=MAX_HEIGHT,
            cannyTresh1=CANNY_THRES1, cannyTresh2=CANNY_THRES2, frameskip=frameskip, threshPercent=threshPercent)

    # main loop
    infoTimer = millis()
    infoDelay = 500
    dbUpdateTimer = millis()
    dbUpdateDelay = 500
    try:
        vcp.start()
        while not vcp.isOutputReady():
            time.sleep(1)
        runServer()

        if OS_TYPE == WINDOWS:
            cv2.imshow('template_bersih', vcp.getFrame(True))
            cv2.imshow('template_bersih_canny', vcp.getFrameCanny(True))
            if ord('q') == cv2.waitKey(10):
                stop()

        spotsStatus = [{'spot': None,
                       'status': None,
                       'cannysum': None,
                       'threshold': None}]
        while True:
            spotsStatusTmp = vcp.getSpotsStatus()
            if millis() > infoTimer + infoDelay:
                for i in range(len(spotsStatusTmp)):
                    valRoi = spotsStatusTmp[i]['spot']
                    valStatus = spotsStatusTmp[i]['status']
                    valCannySum = spotsStatusTmp[i]['cannysum']
                    valThreshold = spotsStatusTmp[i]['threshold']
                    print("\r[INFO]", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "| roi:", valRoi,
                            "| status:", vcp.getStatusStr(valStatus),
                            "| canny:", valCannySum,
                            "| tresh:", valThreshold,
                            "| fps:", vcp.getFps(), end='\t\r')
                infoTimer = millis()

            if OS_TYPE == WINDOWS:
                cv2.imshow('stack_hasil', vcp.getFrameStack())
                if ord('q') == cv2.waitKey(10):
                    stop()

            if (millis() - dbUpdateTimer) >= dbUpdateDelay:
                for i in range(len(spotsStatusTmp)):
                    valRoi = spotsStatusTmp[i]['spot']
                    valStatus = spotsStatusTmp[i]['status']
                    valCannySum = spotsStatusTmp[i]['cannysum']
                    valThreshold = spotsStatusTmp[i]['threshold']

                    if valStatus != spotsStatus[i]['status']:
                        try:
                            result = """
                                        UPDATE `pantausungai` SET `objectStatus` = '{0}' WHERE `pantausungai`.`id` = {1}
                                    """.format(valStatus,  valRoi)
                            CC.execute(result)
                            CONN.commit()
                        except pymysql.err.InternalError as msg:
                            print("Command skipped: ", msg)

                        spotsStatus[i].update({'spot': valRoi,
                                 'status': valStatus,
                                 'cannysum': valCannySum,
                                 'threshold': valThreshold})

                dbUpdateTimer = millis()

            time.sleep(.1)
    except KeyboardInterrupt:
        stop()
        exit()
    except Exception as e:
        print("[ERROR] exception:", e)
        stop()
        exit()

class VideoCannyProcessing:
    def __init__(self, roiPath, templateImg, videoSrc=0, maxWidth=640, maxHeight=480, cannyTresh1=300, cannyTresh2=300, abcClip=-1, frameskip=3, showTemplate=True, threshPercent=12):
        self.stackSizeW = 510
        self.stackSizeH = 288
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        self.abcClip = abcClip
        self.roiPath = roiPath
        self.videoSrc = videoSrc
        self.cannyTresh1 = cannyTresh1
        self.cannyTresh2 = cannyTresh2
        self.showTemplate = showTemplate
        self.threshPercent = int(threshPercent)
        self.it = 0
        self.frameskip = int(frameskip)
        self.avgfps = 0
        self.frames = 0
        self.stopped = False
        self.vs = None
        self.frame = None
        self.frameDetect = None
        self.frameCanny = None
        self.frameStack = None
        self.origImg = templateImg
        self.origCanny = cv2.Canny(templateImg, cannyTresh1, cannyTresh2)
        self.listROI = self.loadROI(roiPath)
        self.templateEdges = self.loadTemplate()
        self.statusStr = {'-1': 'kode tidak diketahui',
                           '0': 'sungai bersih',
                           '1': 'sungai kotor'}
        self.spotsStatus = [{}] * len(self.listROI)
        self.outvideo = None
        self.outputReady = False
        time.sleep(.5)

    def process(self):
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
            self.starttime = datetime.datetime.now()

            while True:
                if self.stopped:
                    return
                else:
                    raw = None
                    try:
                        grabbed, raw = self.vs.read()
                        if not grabbed:
                            self.stop()
                            continue
                    except:
                        pass

                    if isinstance(raw, (list, tuple, np.ndarray)):
                        (h, w) = raw.shape[:2]
                        #raw = cv2.GaussianBlur(raw, (3, 3), 0)
                        #raw = cv2.bilateralFilter(raw, 3, 30, 30)
                        #if h > self.maxHeight or w > self.maxWidth:
                        #    raw = imutils.resize(
                        #        raw, width=self.maxWidth, height=self.maxHeight)
                        if self.abcClip > 0:
                            raw = self.abc(raw, clip_hist_percent=self.abcClip)[0]
                        if self.frameskip > 0:
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
                    self.frameDetect, self.frameCanny = self.cannyForward(raw)
                    self.frameStack = np.hstack([imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW),
                                                 imutils.resize(self.frameDetect, height=self.stackSizeH, width=self.stackSizeW)])
                    self.avgfps = getAvgFps()
                    if not self.outputReady:
                        self.outputReady = True
                    time.sleep(.005)
        except KeyboardInterrupt:
            self.stop()
        except Exception:
            print('[ERROR] ', traceback.format_exc())
            self.frameStack = drawText(self.frameStack, traceback.format_exc(
            ), ( (self.stackSizeH * 2) * .025), ( (self.stackSizeW * 2) * .025), (96, 64, 255), .3)
            self.stop()

    def cannyForward(self, frame):
        frameCanny = cv2.Canny(frame, self.cannyTresh1, self.cannyTresh2)

        for spot in range(len(self.listROI)):
            (x1, y1, x2, y2) = self.listROI[spot]
            new = frame[y1:y2, x1:x2, :]
            #cv2.imwrite('./output/images/outputcanny/new' + str(i) + '_' + str(spot) + '.jpg', new)

            # extract Canny edges
            newEdges = cv2.Canny(new, self.cannyTresh1, self.cannyTresh2)
            #cv2.imwrite('./output/images/outputcanny/newCanny' + str(i) + '_'  + str(spot) + '.jpg', newEdges)

            # calculate the difference between template and new edges
            sub = cv2.absdiff(self.templateEdges[spot], newEdges)

            # normalize the difference normSub is array of 1's and zeros
            normSub = sub / 255

            threshold = int(normSub.size * self.threshPercent / 100)
            frameCanny = cv2.cvtColor(frameCanny, cv2.COLOR_GRAY2RGB)
            cannySum = int(sum(sum(normSub)))

            if cannySum > threshold:
                # if there is greater than a xx% change between template and new edges
                # declare the river is dirty
                # draw a red rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), [0, 0, 255], 2)
                cv2.rectangle(frameCanny, (x1, y1), (x2, y2), [0, 0, 255], 2)
                self.spotsStatus[spot].update({'spot': spot,
                                              'status': 1,
                                              'cannysum': cannySum,
                                              'threshold': threshold})
            else:
                # draw a green rectangle to indicate a clean ROI spot
                cv2.rectangle(frame, (x1, y1), (x2, y2), [0, 255, 0], 2)
                cv2.rectangle(frameCanny, (x1, y1), (x2, y2), [0, 255, 0], 2)
                self.spotsStatus[spot].update({'spot': spot,
                                              'status': 0,
                                              'cannysum': cannySum,
                                              'threshold': threshold})

            if self.outvideo != None:
                self.outvideo.write(frame)

        return frame.copy(), frameCanny.copy()

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

    def isOutputReady(self):
        return self.outputReady

    def loadROI(self, path):
        roiFile = open(path, 'rb')
        ROI = pickle.load(roiFile)
        roiFile.close()
        return ROI

    def loadTemplate(self):
        templateEdges = []
        # Preload templates and precompute template edges
        for r in self.listROI:  # proses canny
            (x1, y1, x2, y2) = r
            template = self.origImg[y1:y2, x1:x2, :]
            #cv2.imwrite('./output/images/outputcanny/newTemplate' + str(r) + '.jpg', self.template)
            templateEdgesCanny = cv2.Canny(template, self.cannyTresh1, self.cannyTresh2)
            templateEdges.append(templateEdgesCanny)
            #cv2.imwrite('./output/images/outputcanny/newCannyTemplate' + str(r) + '.jpg', templateEdgesCanny)
        return templateEdges

    def getFps(self):
        return round(self.avgfps, 2)

    def getStatusStr(self, code):
        return self.statusStr[str(code)]

    def getSpotsStatus(self):
        return self.spotsStatus

    def getFrameDetection(self, resize=False):
        if resize:
            return imutils.resize(self.frameDetect.copy(), height=self.maxHeight, width=self.maxWidth)
        return self.frameDetect.copy()

    def getFrameCanny(self, resize=False):
        if resize:
            return imutils.resize(self.frameCanny.copy(), height=self.maxHeight, width=self.maxWidth)
        return self.frameCanny.copy()

    def getFrame(self, resize=False):
        if resize:
            return imutils.resize(self.frame.copy(), height=self.maxHeight, width=self.maxWidth)
        return self.frame.copy()

    def getFrameStack(self):
        return self.frameStack.copy()

    def start(self):
        print('[INFO] Starting canny detection...')
        self.frame = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameDetect = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameCanny = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameStack = np.hstack([imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW),
                                     imutils.resize(self.frame, height=self.stackSizeH, width=self.stackSizeW)])
        if OS_TYPE == WINDOWS:
            self.vs = cv2.VideoCapture(self.videoSrc, cv2.CAP_DSHOW) #CAP_FFMPEG, CAP_IMAGES, CAP_DSHOW, CAP_MSMF, CAP_V4L2
            ret, img = self.vs.read()
            if img == None:
                self.vs = cv2.VideoCapture(self.videoSrc, cv2.CAP_FFMPEG) #CAP_FFMPEG, CAP_IMAGES, CAP_DSHOW, CAP_MSMF, CAP_V4L2
        else:
            self.vs = cv2.VideoCapture(self.videoSrc)
        time.sleep(.5)
        ret, img = self.vs.read()
        if not ret:
            print('[ERROR] video stream error.')
            exit()
        (height, width) = img.shape[:2]
        #if img.shape[:2] != self.origImg.shape[:2]:
        #    self.origImg = imutils.resize(self.origImg, height=self.maxHeight, width=self.maxWidth)
        #    self.origCanny = imutils.resize(self.origCanny, height=self.maxHeight, width=self.maxWidth)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.outvideo = cv2.VideoWriter('./output/videos/' + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')) +
                   '_output.avi',fourcc, 30.0, (width, height)) # 30.0 fps
        streamthread = Thread(target=self.process,
                              name='ProcessingVideo', args=())
        streamthread.daemon = True
        streamthread.start()
        time.sleep(.5)
        return self

    def stop(self):
        self.stopped = True
        self.outputReady = False
        if self.vs != None:
            self.vs.release()
        if self.outvideo != None:
            self.outvideo.release()
        print('[INFO] canny detection stopped.')

if __name__ == '__main__':
    main()
