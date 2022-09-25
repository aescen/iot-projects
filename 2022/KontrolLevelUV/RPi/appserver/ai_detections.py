from utils import *
from urllib.request import *
from urllib.error import URLError, HTTPError
from threading import Thread
from imutils.video import FileVideoStream
from imutils.video import VideoStream
import cv2
import numpy as np
import os
import sys
import time
import base64
import socket
import imutils
import traceback

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
        self.personDetected = 0
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
                    self.frameDetect = self.personDetection(raw)
                    # cv2.putText(self.frameDetect, "Total person: %d" % (self.personDetected[0]),
                    #cv2.putText(self.frameDetect, "Total person: %d" % (self.personDetected),
                    #            (int(self.maxWidth * .025),
                    #             int(self.maxHeight * .05)),
                    #            cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255),  1, cv2.LINE_AA)
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

    def personDetection(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(
            frame, (416, 416)), 1 / 255.0, (416, 416),
            swapRB=True, crop=False)
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
        colors = ((255, 0, 0),)
        persons = []
        labels = []
        for i in range(len(boxes)):
            if i in indexes:
                x, y, wx, hx = boxes[i]
                if self.classes4person[classIDs[i]] == self.classes4person[0]:
                    persons.append([x, y, x + wx, y + hx])
                    label = str(f'{self.classes4person[classIDs[i]]}: {confidences[i]:.2f}').replace('0.', '.')
                    labels.append(label)
                    color = colors[classIDs[i]]
                    cv2.rectangle(frame, (x, y), (x + wx, y + hx), color, 2)
                    cv2.putText(frame, label, (x, y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, .5, color, 1)

        self.personDetected = len(persons)

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

    def getPersonDetection(self):
        # return self.personDetected[0]
        return self.personDetected
        
    def isPersonDetected(self):
        return True if self.personDetected >= 1 else False

    def isStopped(self):
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

        videoOutputName = f"{os.path.splitext(os.path.basename(self.args['video']))[0]}_yolov3_output.mp4"
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
