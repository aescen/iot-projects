#!/usr/bin/python3

from imutils.video import VideoStream
from threading import Thread
import numpy as np
import traceback
import argparse
import imutils
import curses
import cv2
import time
import sys
import os

def main():
    try:
        #contruct argument parser
        ap = argparse.ArgumentParser()
        ap.add_argument("-i1", "--image1", default="camera", help="path to input image 1")
        ap.add_argument("-i2", "--image2", default="camera", help="path to input image 2")
        ap.add_argument("-a", "--abc", default="no", help = "auto brightness and contrast clip histogram, ex. -a 0.5")
        args = vars(ap.parse_args())

        e1 = "Telur segar"
        e2 = "Telur umur 1 bulan"

        # define the list of color range boundaries
        boundaries = [
            # B G R lower  B G R upper
            ([4, 75, 238], [120, 220, 255], e1, 0.1),
            ([0, 0, 30], [186, 240, 250], e2, 0.05),
        ]
        # source for camera. Unused when using image as source
        src1 = {'src':2,'path':args['image1']}
        src2 = {'src':3,'path':args['image2']}
        
        newDetect1 = Detect(src1, boundaries, args)
        newDetect1.start()
        newDetect2 = Detect(src2, boundaries, args)
        newDetect2.start()
        windowLabel1 = 'Loading...'
        windowLabel2 = 'Loading...'
        labelWidth1 = 0
        labelWidth2 = 0
        
        screen = curses.initscr()
        screen.refresh()
        
        while True:
            label1, frame1 = newDetect1.getStatus()
            label2, frame2 = newDetect2.getStatus()
            if label1 != None:
                if windowLabel1 != label1:
                    windowLabel1 = label1
                    if len(label1) > labelWidth1:
                        labelWidth1 = len(label1)
                    screen.addstr(0, 0, "\rSource 1; Port %s; Detected %s" % (src1['src'], windowLabel1.ljust(labelWidth1)))
            else:
                label1 = windowLabel1
            if label2 != None:
                if windowLabel2 != label2:
                    windowLabel2 = label2
                    if len(label2) > labelWidth2:
                        labelWidth2 = len(label2)
                    screen.addstr(1, 0, "\rSource 2; Port %s; Detected %s" % (src2['src'], windowLabel2.ljust(labelWidth2)))
            else:
                label2 = windowLabel2
            screen.refresh()
            '''sys.stdout.write("\rSource 1; Port %s; Detected %s" % (str(src1), label1.ljust(labelWidth1)))
            sys.stdout.write("\rSource 2; Port %s; Detected %s" % (str(src2), label2.ljust(labelWidth2)))
            sys.stdout.flush()'''
            cv2.imshow("Input / Output Source 1", frame1)
            cv2.imshow("Input / Output Source 2", frame2)
            if ord('q') == cv2.waitKey(10):
                newDetect1.stop()
                newDetect2.stop()
                cv2.destroyAllWindows()
                curses.endwin()
                sys.exit(0)
    except Exception:
        print(traceback.format_exc())
        newDetect1.stop()
        newDetect2.stop()
        cv2.destroyAllWindows()
        curses.endwin()
        sys.exit(str(traceback.format_exc()))
    except KeyboardInterrupt:
        newDetect1.stop()
        newDetect2.stop()
        cv2.destroyAllWindows()
        curses.endwin()
        sys.exit(0)

class Detect():
    def __init__(self, src, boundaries, args):
        self.src = src['src']
        self.imagepath = src['path']
        self.boundaries = boundaries
        self.args = args
        self.vs = None
        self.frame = None
        self.frameStack = None
        self.OS_TYPE = "Unknown"
        self.label = "None detected"
        self.detected = False
        self.stopped = False
        self.lcnt = 1
    
    def detectQ(self):
        self.stopped = False
        if sys.platform == "linux" or sys.platform == "linux2":
            try:
                import RPi.GPIO as gpio
                self.OS_TYPE = 'raspbianlinux'
            except (ImportError, RuntimeError):
                self.OS_TYPE = 'linux'
        elif sys.platform == "darwin":
            self.OS_TYPE = 'macos'
        elif sys.platform == "win32":
            self.OS_TYPE = 'windows'
        
        if self.imagepath == "camera":
            if self.OS_TYPE == 'windows':
                self.vs = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
                self.frame = self.vs.read()[1]
            else:
                self.vs = VideoStream(self.src).start()
                self.frame = self.vs.read()
        else:
            self.frame = cv2.imread(self.imagepath)
            
        
        if self.args["abc"] != "no":
            self.frame = abc(self.frame, clip_hist_percent=float(self.args["abc"]))[0]
        
        time.sleep(0.5)
        
        while True:
            try:
                if self.stopped:
                    return
                else:
                    if isinstance(self.frame, (list, tuple, np.ndarray)):
                        if self.imagepath == "camera":
                            if self.OS_TYPE == 'windows':
                                self.frame = self.vs.read()[1]
                            else:
                                self.frame = self.vs.read()
                        else:
                            self.frame = cv2.imread(self.imagepath)
                        
                        if self.args["abc"] != "no":
                            self.frame = self.abc(self.frame, clip_hist_percent=float(self.args["abc"]))[0]
                        
                        if isinstance(self.frame, (list, tuple, np.ndarray)):
                            imageName = self.imagepath
                            if self.imagepath != "camera":
                                imageName = str(imageName)[imageName.rfind('\\')+1:imageName.rfind('.')].replace(' ', '_')
                            else:
                                imageName = imageName + str(self.src)
                            savePath = os.getcwd() + '\\imgs'
                            image = imutils.resize(self.frame, height = 480, width = 640)
                            output = []
                            label = "none"
                            imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                            imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            imsize = np.size(image)
                            self.label = None
                            self.detected= False
                            # loop over the boundaries
                            for (lower, upper, label, treshhold) in self.boundaries:
                                # create NumPy arrays from the boundaries
                                lower = np.array(lower, dtype = "uint8")
                                upper = np.array(upper, dtype = "uint8")
                                # find the colors within the specified boundaries and apply
                                # the mask
                                mask = cv2.inRange(image, lower, upper)
                                output = cv2.bitwise_and(image, image, mask = mask)
                                #outputHSV = cv2.cvtColor(output, cv2.COLOR_BGR2HSV)
                                outputGray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
                                #h1, s1, v1 = cv2.split(imageHSV)
                                #h2, s2, v2 = cv2.split(outputHSV)
                                imnz = cv2.countNonZero(outputGray)
                                t = imsize * treshhold
                                '''print("Image size:", imsize)
                                print("NonZero size:", imnz)
                                print("Thresh size:", t)'''
                                # show the images
                                '''
                                cv2.imshow("Image Gray", imageGray)
                                cv2.imshow("Image HSV", v1)
                                cv2.imshow("Mask", mask)
                                cv2.imshow("Output", output)
                                cv2.imshow("Gray", outputGray)
                                cv2.imshow("HSV", v2)
                                cv2.imshow(label, np.hstack([image, output]))
                                #cv2.imwrite('imgs/2. imagehsv.png', v1)
                                #cv2.imwrite('imgs/5. imageoutputhsv.png', v2)
                                cv2.imwrite('imgs/1. [Gray]' + imageName +'.png', imageGray)
                                cv2.imwrite('imgs/2. [Mask]' + imageName +'.png', mask)
                                cv2.imwrite('imgs/3. [Output]' + imageName +'.png', output)
                                cv2.imwrite('imgs/4. [OutputGray]' + imageName +'.png', outputGray)
                                cv2.imwrite('imgs/5. [Stack]' + imageName +'.png', np.hstack([image, output]))'''
                                
                                if int(imnz) >=  int(t):
                                    self.detected = True
                                    self.label = label
                                    path = self.makedirs(savePath, imageName)
                                    cv2.imwrite(path + '1.[Gray]_' + imageName + '.png', imageGray)
                                    cv2.imwrite(path + '2.[Mask]_' + imageName + '.png', mask)
                                    cv2.imwrite(path + '3.[Output]_' + imageName + '.png', output)
                                    cv2.imwrite(path + '4.[OutputGray]_' + imageName + '.png', outputGray)
                                    cv2.imwrite(path + '5.[Stack]_' + imageName + '.png', np.hstack([image, output]))
                                    break
                                else:
                                    self.detected = False
                                    self.label = "None detected"
                            self.frameStack = np.hstack([imutils.resize(image, height = 192, width = 340),
                                    imutils.resize(output, height = 192, width = 340)])
                        else:
                            self.label = "None detected"
                    else:
                        self.stop()
                        print('Image is empty! Cannot continue, please check video/image source!')
            except Exception:
                print(traceback.format_exc())
                self.stop()
                
        if self.imagepath == "camera":
            self.vs.release()
        cv2.destroyAllWindows()
    
    def getStatus(self):
        if isinstance(self.frameStack, (list, tuple, np.ndarray)):
            return (self.label, self.frameStack)
        elif self.frameStack == None:
            height = 192
            width = 680
            img = np.zeros(shape=[height, width, 3], dtype=np.uint8)
            label = "Loading" + ("." * self.lcnt)
            cv2.putText(img, label,  (int(height*0.02), int(width*0.02)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            self.lcnt += 1
            return (self.label, img)
            
    def start(self):
        newThread = Thread(target=self.detectQ, name='DetectImageQuality', args=())
        newThread.start()
    
    def stop(self):
        self.stopped = True
    
    # automatic brightness and contrast optimization with optional histogram clipping
    def abc(self, image, clip_hist_percent=0.5):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Calculate grayscale histogram
        hist = cv2.calcHist([gray],[0],None,[256],[0,256])
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

        auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return (auto_result, alpha, beta)
    
    # create directory / sub-directory
    def makedirs(self, parent, child):
        path = os.path.join(parent, child)
        try:
            os.makedirs(path, exist_ok = True)
            return path + '\\'
        except OSError as e:
            print("Cannot create directory '%s'" % child)
            return 'imgs\\'

if __name__ == '__main__':
    main()
    