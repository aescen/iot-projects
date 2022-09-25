#!/usr/bin/python3

from threading import Thread, Lock
from imutils.video import FileVideoStream
from imutils.video import VideoStream
import sys
from time import sleep
import imutils
import argparse
import datetime
import traceback
import cv2
import numpy as np
from flask import Response
from flask import Flask
from flask import render_template
import logging
log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)
log.disabled = True


OS_TYPE = ''
if sys.platform == "linux" or sys.platform == "linux2":
    try:
        import RPi.GPIO as IO
        OS_TYPE = 'raspbianlinux'
    except (ImportError, RuntimeError):
        OS_TYPE = 'linux'
elif sys.platform == "darwin":
    OS_TYPE = 'macos'
elif sys.platform == "win32":
    OS_TYPE = 'windows'


def main():

    def runServer(host="0.0.0.0", port="8080", debug=False):

        def appRun():
            app.run(host=host, port=port, debug=debug,
                    threaded=True, use_reloader=False)

        def encodeImage():
            flag = None
            encodedImage = None
            while True:
                with lock:
                    if imageDetect is None:
                        continue
                    (flag, encodedImage) = cv2.imencode(".jpg", imageDetect)
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

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", default='stream',
                    help="path/url to video file/streams")
    ap.add_argument("-f", "--frameskip", default=3,
                    help="frames to skip(default: 3)")
    ap.add_argument("-a", "--abc", default="no",
                    help="auto brightness and contrast clip histogram, ex. -a 0.5")
    args = vars(ap.parse_args())
    minFaceSize = (54, 72)
    timeout = 5
    maxHeight = 480
    maxWidth = 640
    camera_src = 1

    oc = ObjectClassifier(src=camera_src, args=args, minFaceSize=minFaceSize,
                          timeout=timeout, maxWidth=maxWidth, maxHeight=maxHeight)
    oc.start()
    imageDetect = None

    lock = Lock()

    try:
        runServer()
        sleep(1)
        while True:
            imageDetect = oc.getFrameDetection()
            objectCount = oc.getFrameDetectionCount()
            sys.stdout.flush()
            sys.stdout.write("\rDetection: %d, fps: %.2f" %
                             (objectCount, oc.fps()))
            cv2.imshow('Detection: ', imageDetect)
            if ord('q') == cv2.waitKey(10):
                oc.stop()
                cv2.destroyAllWindows()
                sleep(.5)
                print('\nEnd.')
                sys.exit(0)
            sleep(.01)
    except KeyboardInterrupt:
        oc.stop()
        sleep(.5)
        print('\nEnd.')
        sys.exit(0)


class ObjectClassifier:
    def __init__(self, src, args, timeout=10, minFaceSize=(14, 28), maxWidth=640, maxHeight=480, forceResize=False, abcClip=.75):
        self.timeout = timeout
        self.src = src
        self.minFaceSize = minFaceSize
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
            self.frames += 1
            self.it += 1
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
                    if OS_TYPE == 'windows':
                        raw = self.vs.read()[1]
                    else:
                        raw = self.vs.read()

                    if isinstance(raw, (list, tuple, np.ndarray)):
                        (h, w) = raw.shape[:2]
                        if h > self.maxHeight or w > self.maxWidth or self.forceResize:
                            raw = imutils.resize(
                                raw, width=self.maxWidth, height=self.maxHeight)
                        if int(self.args["frameskip"]) > 0:
                            if self.it % int(self.frameskip) == 0:
                                self.frame = raw
                                self.frames += 1
                                processImage()
                            else:
                                self.it += 1
                                self.frames += 1
                        else:
                            self.frame = raw
                            processImage()
        except Exception:
            print(traceback.format_exc())
            self.frameStack = drawText(self.frameStack, traceback.format_exc(),
                                       (384 * .025), (680 * .025), (96, 64, 255), .3)

    def objectClassifier(self, frame):
        self.objectDetectedTmp = 0
        objectPath = 'haarcascade\\haarcascade_frontalface_default.xml'
        objectCascade = cv2.CascadeClassifier(objectPath)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        classifications = objectCascade.detectMultiScale(
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
            while True:
                sleep(.01)
                if self.isProcessing == True:
                    processingState = True
                    continue
                elif processingState == True and self.isProcessing == False:
                    self.stop()
                    return self.objectDetected
        else:
            self.getDetectionOnce(started=True)

    def start(self):
        if self.args["video"] != 'stream':
            self.vs = FileVideoStream(self.args["video"]).start()
            sleep(.5)
        else:
            if OS_TYPE == 'windows':
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
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
