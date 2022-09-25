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
import pymysql
import tracemalloc


def process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss


def main():
    def getAvgColor(c1, c2): # RGB
        cAvg = np.average( np.array([c1, c2]), axis=0 )
        return cAvg.astype(np.uint8)

    def pinoff(pin):
        gpio.setup(pin, gpio.IN)

    def pinon(pin):
        gpio.setup(pin, gpio.OUT)

    def cleanup():
        gpio.cleanup()
        sys.exit()

    def saveDb(result):
        # save to db
        try:
            cc.execute(result)
            connection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)

    def micros(): return int(round(time.time() * 1000000)) & 0xffffffff

    def millis(): return int(round(time.time() * 1000)) & 0xffffffff

    def seconds(): return int(round(time.time())) & 0xffffffff

    # Vars
    OS_TYPE = ''
    relayPin = 16
    referenceUnit = 517
    sample = 5
    DT = 21
    SCK = 20
    weightThresh = 35

    if sys.platform == "linux" or sys.platform == "linux2":
        try:
            import RPi.GPIO as gpio
            OS_TYPE = 'raspbianlinux'
            gpio.setwarnings(False)
            gpio.setmode(gpio.BCM)
            gpio.setup(relayPin, gpio.OUT, initial=gpio.LOW)
        except (ImportError, RuntimeError):
            OS_TYPE = 'linux'
    elif sys.platform == "darwin":
        print("Using Mac is not supported yet! Exiting.")
        sys.exit()
    elif sys.platform == "win32":
        from GPIOEmulator.EmulatorGUI import GPIO as gpio
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(relayPin, gpio.OUT, initial=gpio.LOW)
        OS_TYPE = 'windows'

    # Database setup..
    # Create connection to MySQL server
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
    cc = connection.cursor()

    # contruct argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-i1", "--image1", default="camera",
                    help="path to input image 1")
    ap.add_argument("-i2", "--image2", default="camera",
                    help="path to input image 2")
    ap.add_argument("-a", "--abc", default="no",
                    help="auto brightness and contrast clip histogram, ex. -a 0.5")
    args = vars(ap.parse_args())

    e1 = "Telur segar"
    e2 = "Telur berkembang biak"
    e3 = "Telur busuk"

    # define the list of color range boundaries
    boundaries = [
        # B G R lower  B G R upper
        ([4, 75, 238], [120, 220, 255], e1, 0.1),  # segar
        ([0, 0, 30], [186, 240, 250], e2, 0.05),  # brkbgbiak
        ([71, 66, 98], [122, 113, 139], e3, 0.05),  # busuk
    ]
    # source for camera. Unused when using image as source
    src1 = {'src': 0, 'path': args['image1']}
    src2 = {'src': 2, 'path': args['image2']}

    newDetect1 = Detect(src1, boundaries, args, False)
    newDetect2 = Detect(src2, boundaries, args, False)
    newWeight = Weight(DT, SCK, referenceUnit, sample)

    screen = curses.initscr()
    screen.refresh()

    windowLabel1 = 'Loading...'
    windowLabel2 = 'Loading...'
    labelWidth1 = 0
    labelWidth2 = 0

    traceTime = seconds()
    relayOnTmp = False
    relayOffTmp = False

    saveTotalSegar = False
    saveTotalBerkembangBiak = False
    saveTotalBusuk = False
    totalSegar = 0
    totalBerkembangBiak = 0
    totalBusuk = 0

    testDbTimer = seconds()
    testDbDelay = 8

    try:
        newDetect1.start()
        newDetect2.start()
        newWeight.start()

        # segar
        resultSegar = """
                UPDATE `kualitastelur` SET `r` = '{0}', `g` = '{1}', `b` = '{2}', `beban` = '{3}', `jumlah` = '{4}' WHERE `kualitastelur`.`id` = {5}
            """.format(0, 0, 0, 0, 0, 1)
        saveDb(resultSegar)
        # berkembang biak
        resultBerkembangBiak = """
                UPDATE `kualitastelur` SET `r` = '{0}', `g` = '{1}', `b` = '{2}', `beban` = '{3}', `jumlah` = '{4}' WHERE `kualitastelur`.`id` = {5}
            """.format(0, 0, 0, 0, 0, 2)
        saveDb(resultBerkembangBiak)
        # busuk
        resultBusuk = """
                UPDATE `kualitastelur` SET `r` = '{0}', `g` = '{1}', `b` = '{2}', `beban` = '{3}', `jumlah` = '{4}' WHERE `kualitastelur`.`id` = {5}
            """.format(0, 0, 0, 0, 0, 3)
        saveDb(resultBusuk)

        while True:
            # update sensor/info data
            label1, frame1, color1 = newDetect1.getStatus()
            label2, frame2, color2 = newDetect2.getStatus()
            avgColor = getAvgColor(color1, color2)
            weight = newWeight.getWeight()
            memCurrent, memPeak = tracemalloc.get_traced_memory()

            if label1 != None:
                if windowLabel1 != label1:
                    windowLabel1 = label1
                    if len(label1) > labelWidth1:
                        labelWidth1 = len(label1)
                    screen.clrtoeol()
                    screen.refresh()
                    screen.addstr(0, 0, "\rSource: 1; Port: %s; Detected: %s" % (
                        src1['src'], windowLabel1.ljust(labelWidth1)))
            else:
                label1 = windowLabel1
            if label2 != None:
                if windowLabel2 != label2:
                    windowLabel2 = label2
                    if len(label2) > labelWidth2:
                        labelWidth2 = len(label2)
                    screen.clrtoeol()
                    screen.refresh()
                    screen.addstr(1, 0, "\rSource: 2; Port: %s; Detected: %s" % (
                        src2['src'], windowLabel2.ljust(labelWidth2)))
            else:
                label2 = windowLabel2

            screen.clrtoeol()
            screen.refresh()
            screen.addstr(2, 0, "\rWeight: %fg" % (weight))

            # check weigh, process image, save db
            if weight >= weightThresh:
                if not relayOnTmp:
                    relayOnTmp = True
                    relayOffTmp = False
                    pinon(relayPin)
                    newDetect1.processImage(True)
                    newDetect2.processImage(True)
                    saveTotalSegar = True
                    saveTotalBerkembangBiak = True
                    saveTotalBusuk = True
                    time.sleep(.05)
            else:
                if not relayOffTmp:
                    relayOnTmp = False
                    relayOffTmp = True
                    pinoff(relayPin)
                    newDetect1.processImage(False)
                    newDetect2.processImage(False)

            # save db

            # test
            # if seconds() - testDbTimer >= testDbDelay:
            #     label1 = e1
            #     label2 = label1
            #     testDbTimer = seconds()

            # segar
            if label1 is label2 is e1 and relayOnTmp:
                if saveTotalSegar:
                    totalSegar += 1
                    saveTotalSegar = False
                time.sleep(.05)
                resultSegar = """
                        UPDATE `kualitastelur` SET `r` = '{0}', `g` = '{1}', `b` = '{2}', `beban` = '{3}', `jumlah` = '{4}' WHERE `kualitastelur`.`id` = {5}
                    """.format(avgColor[0], avgColor[1], avgColor[2], weight, totalSegar, 1)
                saveDb(resultSegar)

            # berkembang biak
            elif label1 is label2 is e2 and relayOnTmp:
                if saveTotalBerkembangBiak:
                    totalBerkembangBiak += 1
                    saveTotalBerkembangBiak = False
                time.sleep(.05)
                resultBerkembangBiak = """
                        UPDATE `kualitastelur` SET `r` = '{0}', `g` = '{1}', `b` = '{2}', `beban` = '{3}', `jumlah` = '{4}' WHERE `kualitastelur`.`id` = {5}
                    """.format(avgColor[0], avgColor[1], avgColor[2], weight, totalBerkembangBiak, 2)
                saveDb(resultBerkembangBiak)
            # busuk
            elif label1 is label2 is e3 and relayOnTmp:
                if saveTotalBusuk:
                    totalBusuk += 1
                    saveTotalBusuk = False
                time.sleep(.05)
                resultBusuk = """
                        UPDATE `kualitastelur` SET `r` = '{0}', `g` = '{1}', `b` = '{2}', `beban` = '{3}', `jumlah` = '{4}' WHERE `kualitastelur`.`id` = {5}
                    """.format(avgColor[0], avgColor[1], avgColor[2], weight, totalBusuk, 3)
                saveDb(resultBusuk)

            screen.clrtoeol()
            screen.refresh()
            screen.addstr(3, 0, "\rTotal segar: %d; Total berkembangbiak: %d; Total busuk: %d" % (totalSegar, totalBerkembangBiak, totalBusuk))

            # info
            if seconds() - traceTime >= 2:
                screen.clrtoeol()
                screen.refresh()
                screen.addstr(4, 0, "\r[Memory] Current: %fMB - Peak: %fMiB" %
                              (memCurrent / 10**6, memPeak / 10**6))
                traceTime = seconds()

            if OS_TYPE == 'windows':
                cv2.imshow("Input / Output Source 1", frame1)
                cv2.imshow("Input / Output Source 2", frame2)
                if ord('q') == cv2.waitKey(10):
                    newDetect1.stop()
                    newDetect2.stop()
                    newWeight.stop()
                    cv2.destroyAllWindows()
                    curses.endwin()
                    sys.exit(0)
            time.sleep(.05)
    except Exception:
        newDetect1.stop()
        newDetect2.stop()
        newWeight.stop()
        pinoff(relayPin)
        cv2.destroyAllWindows()
        curses.endwin()
        print(traceback.format_exc())
        sys.exit(str(traceback.format_exc()))
    except KeyboardInterrupt:
        newDetect1.stop()
        newDetect2.stop()
        newWeight.stop()
        pinoff(relayPin)
        cv2.destroyAllWindows()
        curses.endwin()
        sys.exit(0)


class Weight:
    def __init__(self, dt, sck, ref=1, sample=3):
        from hx711py.hx711 import HX711
        self.dt = dt
        self.sck = sck
        self.referenceUnit = ref
        self.sample = sample
        self.stopped = False
        self.value = 0.0
        self.hx = HX711(self.dt, self.sck)
        self.hx.set_reading_format("MSB", "MSB")
        self.hx.set_reference_unit(self.referenceUnit)
        self.hx.reset()
        self.hx.tare()

    def weighting(self):
        while True:
            try:
                if self.stopped:
                    return
                else:
                    self.value = max(
                        0, int(self.hx.get_weight(self.sample) * 1000)) / 1000
                    self.hx.power_down()
                    self.hx.power_up()
                    time.sleep(0.1)
            except KeyboardInterrupt:
                self.stop()
            except Exception:
                print(traceback.format_exc())
                self.stop()

    def getWeight(self):
        return self.value

    def start(self):
        newThread = Thread(target=self.weighting, name='Weighting', args=())
        newThread.start()

    def stop(self):
        self.stopped = True


class Detect():
    def __init__(self, src, boundaries, args, processImg=True):
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
        self.avgColor = np.array([0, 0, 0])
        self.stopped = False
        self.lcnt = 1
        self.processImg = processImg

    def processImage(self, process=True):
        self.processImg = process
        time.sleep(0.5)

    # replace pixels
    def getColored(self, arr, fromColor, toColor):
        arr[np.where((arr==fromColor).all(axis=2))] = toColor
        return arr


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
            self.frame = abc(
                self.frame, clip_hist_percent=float(self.args["abc"]))[0]

        time.sleep(0.5)

        while True:
            try:
                if self.stopped:
                    return
                else:
                    if self.processImg:
                        if isinstance(self.frame, (list, tuple, np.ndarray)):
                            if self.imagepath == "camera":
                                if self.OS_TYPE == 'windows':
                                    self.frame = self.vs.read()[1]
                                else:
                                    self.frame = self.vs.read()
                            else:
                                self.frame = cv2.imread(self.imagepath)

                            if self.args["abc"] != "no":
                                self.frame = self.abc(
                                    self.frame, clip_hist_percent=float(self.args["abc"]))[0]

                            if isinstance(self.frame, (list, tuple, np.ndarray)):
                                imageName = self.imagepath
                                if self.imagepath != "camera":
                                    imageName = str(imageName)[imageName.rfind(
                                        '/')+1:imageName.rfind('.')].replace(' ', '_')
                                else:
                                    imageName = imageName + str(self.src)
                                savePath = os.getcwd() + '/imgs'
                                image = imutils.resize(
                                    self.frame, height=480, width=640)
                                output = []
                                label = "none"
                                imageHSV = cv2.cvtColor(
                                    image, cv2.COLOR_BGR2HSV)
                                imageGray = cv2.cvtColor(
                                    image, cv2.COLOR_BGR2GRAY)
                                imsize = np.size(image)
                                self.label = None
                                self.detected = False
                                # loop over the boundaries
                                for (lower, upper, label, treshhold) in self.boundaries:
                                    # create NumPy arrays from the boundaries
                                    lower = np.array(lower, dtype="uint8")
                                    upper = np.array(upper, dtype="uint8")
                                    # find the colors within the specified boundaries and apply
                                    # the mask
                                    mask = cv2.inRange(image, lower, upper)
                                    output = cv2.bitwise_and(
                                        image, image, mask=mask)
                                    #outputHSV = cv2.cvtColor(output, cv2.COLOR_BGR2HSV)
                                    outputGray = cv2.cvtColor(
                                        output, cv2.COLOR_BGR2GRAY)
                                    #h1, s1, v1 = cv2.split(imageHSV)
                                    #h2, s2, v2 = cv2.split(outputHSV)
                                    imnz = cv2.countNonZero(outputGray)
                                    t = imsize * treshhold
                                    '''print("Image size:", imsize)
                                    print("NonZero size:", imnz)
                                    print("Thresh size:", t)'''
                                    # show the images
                                    '''
                                    if OS_TYPE = 'windows':
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

                                    if int(imnz) >= int(t):
                                        avgBoundary = np.average([lower, upper], axis=0)# column average axis = 0
                                        avgOutput = self.getColored(output, [0,0,0], avgBoundary)
                                        avgColor_perRow = np.average(avgOutput, axis=0)
                                        avgColor = np.average(avgColor_perRow, axis=0)# BGR
                                        self.avgColor = np.array( [ int(avgColor[2]), int(avgColor[1]), int(avgColor[0]) ]) # RGB
                                        self.detected = True
                                        self.label = label
                                        path = self.makedirs(
                                            savePath, imageName)
                                        cv2.imwrite(
                                            path + '1.[Image]_' + imageName + '.png', image)
                                        cv2.imwrite(
                                            path + '2.[Gray]_' + imageName + '.png', imageGray)
                                        cv2.imwrite(
                                            path + '3.[Mask]_' + imageName + '.png', mask)
                                        cv2.imwrite(
                                            path + '4.[Output]_' + imageName + '.png', output)
                                        cv2.imwrite(
                                            path + '5.[OutputGray]_' + imageName + '.png', outputGray)
                                        cv2.imwrite(
                                            path + '6.[Stack]_' + imageName + '.png', np.hstack([image, output]))
                                        break
                                    else:
                                        self.avgColor = np.array([0, 0, 0])
                                        self.detected = False
                                        self.label = "None detected"
                                self.frameStack = np.hstack([imutils.resize(image, height=192, width=340),
                                                             imutils.resize(output, height=192, width=340)])
                            else:
                                self.label = "None detected"
                        else:
                            self.stop()
                            print(
                                'Image is empty! Cannot continue, please check video/image source!')
            except KeyboardInterrupt:
                self.stop()
            except Exception:
                print(traceback.format_exc())
                self.stop()
            time.sleep(0.1)

        if self.imagepath == "camera":
            self.vs.release()
        cv2.destroyAllWindows()

    def getStatus(self):
        if isinstance(self.frameStack, (list, tuple, np.ndarray)):
            return (self.label, self.frameStack, self.avgColor)
        elif self.frameStack == None:
            height = 192
            width = 680
            img = np.zeros(shape=[height, width, 3], dtype=np.uint8)
            label = "Loading" + ("." * self.lcnt)
            cv2.putText(img, label,  (int(height*0.02), int(width*0.02)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            self.lcnt += 1
            return ( "None detected", img, np.array([0,0,0]) )

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
            return path + '/'
        except OSError as e:
            print("Cannot create directory '%s'" % child)
            return 'imgs/'


if __name__ == '__main__':
    tracemalloc.start()
    main()
    tracemalloc.stop()
