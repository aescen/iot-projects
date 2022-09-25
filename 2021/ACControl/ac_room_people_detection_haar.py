#!/usr/bin/python3
from urllib.request import *
from urllib.error import URLError, HTTPError
from threading import Thread
from imutils.video import FileVideoStream
import sys
import time
import base64
import socket
import imutils
import argparse
import datetime
import traceback
import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--prototxt", default='.\\MobileNetSSD\\prototxt',
                    help="path to Caffe 'deploy' prototxt file")
    ap.add_argument("-m", "--model", default='.\\MobileNetSSD\\caffemodel',
                    help="path to Caffe pre-trained model")
    ap.add_argument("-c", "--confidence", type=float, default=.6,
                    help="minimum probability to filter weak detections")
    ap.add_argument("-v", "--video", default='stream',
                    help="path/url to video file/streams")
    ap.add_argument("-f", "--frameskip", default=0,
                    help="frames to skip(default: 0)")
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
    # View camera online in Barrigada, Guam, Barrigada Mayor'S Office http://www.insecam.org/en/view/882308/
    #url = "http://121.55.235.78/oneshotimage1"
    username = "user"
    password = "user"
    url = "http://192.168.0.20/image.jpg"
    #stream = Stream(url=url, maxWidth=maxWidth, maxHeight=maxHeight)
    oc = ObjectClassifier(url=url, classes=classes, args=args,
                         username=username, password=password,
                         timeout=timeout, maxWidth=maxWidth, maxHeight=maxHeight)
    oc.start()
    try:
        while True:
            imageStack = oc.getFrameStack()
            objectCount = oc.getFrameDetectionCount()
            sys.stdout.flush()
            sys.stdout.write("\rfps: %.2f" % (oc.fps()))
            cv2.imshow('Image: In/Out', imageStack)
            if ord('q') == cv2.waitKey(10):
                oc.stop()
                cv2.destroyAllWindows()
                print('')
                sys.exit(0)

    except KeyboardInterrupt:
        oc.stop()
        print('')
        sys.exit(0)


class ObjectClassifier:
    def __init__(self, url, classes, args, username=None, password=None, timeout=10, maxWidth=640, maxHeight=480, forceResize=False, abcClip=.5):
        self.timeout = timeout
        self.url = url
        self.classes = classes
        self.args = args
        self.forceResize = forceResize
        self.username = username
        self.password = password
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        self.abcClip = abcClip
        self.streamthread = Thread()
        self.request = Request(url)
        self.colors = np.random.uniform(0, 255, size=(len(classes), 3))
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
        self.frame = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameDetect = np.zeros(
            shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)
        self.frameStack = np.hstack([imutils.resize(self.frame, height=192, width=340),
                                     imutils.resize(self.frame, height=192, width=340)])
        time.sleep(0.5)

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

        try:
            while True:
                if self.stopped:
                    return
                else:
                    raw = None
                    if self.args["video"] == 'stream':
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
                                self.frame = raw
                                self.frames += 1
                            else:
                                continue
                        else:
                            self.frame = raw
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
                    self.frameDetect = self.objectClassifier(raw)
                    self.frameStack = np.hstack([imutils.resize(self.frame, height=192, width=340),
                        imutils.resize(self.frameDetect, height=192, width=340)])
                    self.avgfps = getAvgFps()
                    if not self.vs.more:
                        self.stop()

        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            self.frameStack = drawText(self.frameStack, e.code, (384 * .025), (680 * .025), (96, 64, 255), .3)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
            self.frameStack = drawText(self.frameStack, e.reason, (384 * .025), (680 * .025), (96, 64, 255), .3)
        except Exception:
            print(traceback.format_exc())
            self.frameStack = drawText(self.frameStack, traceback.format_exc(), (384 * .025), (680 * 0.025), (96, 64, 255), .3)

    def objectClassifier(self, frame):
        self.objectDetectedTmp = 0
        objectPath = 'haarcascade\\official_opencv_haarcascade_fullbody.xml'
        objectCascade = cv2.CascadeClassifier(objectPath)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        classifications = objectCascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=3, minSize=(14, 28))
        
        for (x, y, w, h) in classifications:
            colorBox = (255, 0, 0)
            colorText = (255, 255, 255)
            rw = int(w * 0.01)
            rh = int(h * 0.01)
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

    def start(self):
        if self.args["video"] != 'stream':
            self.vs = FileVideoStream(self.args["video"]).start()
            time.sleep(.5)
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
        print('\nEnd.')

if __name__ == '__main__':
    main()
