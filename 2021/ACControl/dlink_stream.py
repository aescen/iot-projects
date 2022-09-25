#!/usr/bin/python3
from urllib.request import *
from urllib.error import URLError, HTTPError
from threading import Thread
import sys
import base64
import socket
import imutils
import datetime
import traceback
import cv2 as cv
import numpy as np

class Stream:
    def __init__(self, url, username=None, password=None, timeout=10, maxWidth=640, maxHeight=480, forceResize=False, abcClip=0.5):
        self.timeout = timeout
        self.url = url
        self.forceResize = forceResize
        self.username = username
        self.password = password
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        self.abcClip = abcClip
        self.streamthread = Thread()
        self.request = Request(url)
        self.avgfps = 0
        self.frames = 0
        self.starttime = datetime.datetime.now()
        self.stopped = False
        self.frame = np.zeros(shape=[self.maxHeight, self.maxWidth, 3], dtype=np.uint8)

    def fetchImg(self):
        try:
            socket.setdefaulttimeout(self.timeout)
            request = Request(self.url)
            if self.username != None and self.password != None:
                base64string = base64.b64encode(bytes('%s:%s' % (self.username, self.password), 'ascii'))
                request.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))
            while True:
                if self.stopped:
                    return
                with urlopen(request) as response:
                    imgArr = np.array(bytearray(response.read()), dtype=np.uint8)
                    raw = cv.imdecode(imgArr, cv.IMREAD_COLOR)
                    (h, w) = raw.shape[:2]
                    #raw, _, _ = abc(raw, self.abcClip)
                    raw = cv.GaussianBlur(raw, (3, 3), 0)
                    raw = cv.bilateralFilter(raw, 3, 30, 30)
                    if h > self.maxHeight or w > self.maxWidth or self.forceResize:
                        self.frame = imutils.resize(raw, width=self.maxWidth, height=self.maxHeight)
                    else:
                        self.frame = raw
                    self.frames += 1
                    self.avgfps = self.frames / (datetime.datetime.now() - self.starttime).total_seconds()
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        except Exception:
            print(traceback.format_exc())
            pass
    
    def abc(self, image, clip_hist_percent=0.5):
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # Calculate grayscale histogram
        hist = cv.calcHist([gray],[0],None,[256],[0,256])
        hist_size = len(hist)

        # Calculate cumulative distribution from the histogram
        accumulator = []
        accumulator.append(float(hist[0]))
        for index in range(1, hist_size):
            accumulator.append(accumulator[index -1] + float(hist[index]))

        # Locate points to clip
        maximum = accumulator[-1]
        clip_hist_percent *= (maximum/100.0)
        clip_hist_percent /= 2.0

        # Locate left cut
        minimum_gray = 0
        while accumulator[minimum_gray] < clip_hist_percent:
            minimum_gray += 1

        # Locate right cut
        maximum_gray = hist_size -1
        while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
            maximum_gray -= 1

        # Calculate alpha and beta values
        alpha = 255 / (maximum_gray - minimum_gray)
        beta = -minimum_gray * alpha

        auto_result = cv.convertScaleAbs(image, alpha=alpha, beta=beta)
        return (auto_result, alpha, beta)
    
    def fps(self):
        return self.avgfps
    
    def read(self):
        return self.frame
        
    def start(self):
        streamthread = Thread(target=self.fetchImg, name='FetchImageUrl', args=())
        streamthread.daemon = True
        streamthread.start()
        return self
    
    def stop(self):
        self.stopped = True

def main():
    #url = "http://192.168.0.20/image.jpg"
    #View camera online in Barrigada, Barrigada Mayor'S Office http://www.insecam.org/en/view/882308/ 
    url = "http://121.55.235.78/oneshotimage1"
    username = "user"
    password = "user"
    timeout = 5
    maxHeight = 480
    maxWidth = 640
    #stream = Stream(url=url, username=username, password=password, timeout=timeout, maxWidth=maxWidth, maxHeight=maxHeight)
    stream = Stream(url=url, maxWidth=maxWidth, maxHeight=maxHeight)
    stream.start()
    try:
        while True:
            img = stream.read()
            sys.stdout.flush()
            sys.stdout.write("\rfps: %.2f" % (stream.fps()))
            cv.imshow('test', img)
            if ord('q') == cv.waitKey(10):
                stream.stop()
                cv.destroyAllWindows()
                print('')
                sys.exit(0)

    except KeyboardInterrupt:
        stream.stop()
        print('')
        sys.exit(0)

if __name__ == '__main__':
    main()
    