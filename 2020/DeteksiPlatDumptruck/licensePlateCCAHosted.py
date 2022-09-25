from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_local
from time import gmtime, strftime, sleep, time
from datetime import datetime
from imutils import contours
from skimage import measure
from pprint import pprint
from PIL import Image
from sys import exit
from math import exp
from math import log
import RPi.GPIO as IO
import numpy as np
import pytesseract
import argparse
import requests
import pymysql
import imutils
import json
import cv2

hostUrl = "https://..."
hostUrlLocalIn = "http://in.dumptruck.local/..."
hostUrlLocalOut = "http://out.dumptruck.local/..."
checkData = "/checkdata"
updateData = "/updatedata"
insertData = "/insertdata"
checkHistory = "/checkhistory"
insertHistory = "/inserthistory"

def pinOff(pin):
    IO.setup(pin, IO.IN)

def pinOn(pin):
    IO.setup(pin, IO.OUT, initial = IO.HIGH)

def frange(start, stop, numelements):
    if start == 0:
        start = 1
    if stop == 0:
        stop = 1
    if numelements == 0:
        numelements = 0.001
    incr = (stop - start) / numelements
    return (start + x * incr for x in range(numelements))

def exprange(start, stop, numelements):
    if start == 0:
        start = 1
    if stop == 0:
        stop = 1
    if numelements == 0:
        numelements = 0.001
    return (exp(x) for x in frange(log(start), log(stop), numelements))

def upward(gateA = 0, gateB = 0):
    global upSteps
    global pwmA
    global pwmB
    global pinIn1
    global pinIn2
    global pinIn3
    global pinIn4
    global delayTime
    dcMax = 95
    dcMin = 0
    dc = dcMax
    steps = (dcMax - dcMin) / upSteps
    if gateA is 1 and gateB is 0:
        pwmA.ChangeDutyCycle(dcMax)
    elif gateB is 1 and gateA is 0:
        pwmB.ChangeDutyCycle(dcMax)
    elif gateA is 1 and gateB is 1:
        pwmA.ChangeDutyCycle(dcMax)
        pwmB.ChangeDutyCycle(dcMax)
    for i in exprange(dcMax, dcMin, upSteps):
        if gateA is 1 and gateB is 0:
            pinOff(pinIn1)
            pinOn(pinIn2)
            sleep(delayTime)
            stop()
            if dc <= 0 :
                dc = 0
            pwmA.ChangeDutyCycle(i)
            print("Gate A", i)
        elif gateB is 1 and gateA is 0:
            pinOff(pinIn3)
            pinOn(pinIn4)
            sleep(delayTime)
            stop()
            if dc <= 0 :
                dc = 0
            pwmB.ChangeDutyCycle(i)
            print("Gate B", i)
        elif gateA is 1 and gateB is 1:
            pinOff(pinIn1)
            pinOn(pinIn2)
            pinOff(pinIn3)
            pinOn(pinIn4)
            sleep(delayTime)
            stop()
            if dc <= 0 :
                dc = 0
            pwmA.ChangeDutyCycle(i)
            pwmB.ChangeDutyCycle(i)
            print("Gate A & Gate B", i)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)

def downward(gateA = 0, gateB = 0):
    global downSteps
    global pwmA
    global pwmB
    global pinIn1
    global pinIn2
    global pinIn3
    global pinIn4
    global delayTime
    dcMax = 45
    dcMin = 0
    dc = dcMax
    if gateA is 1 and gateB is 0:
        pwmA.ChangeDutyCycle(dcMax)
    elif gateB is 1 and gateA is 0:
        pwmB.ChangeDutyCycle(dcMax)
    elif gateA is 1 and gateB is 1:
        pwmA.ChangeDutyCycle(dcMax)
        pwmB.ChangeDutyCycle(dcMax)
    for i in range(1, downSteps + 1):
        if gateA is 1 and gateB is 0:
            pinOn(pinIn1)
            pinOff(pinIn2)
            sleep(delayTime)
            stop()
            steps = ((dc - dcMin) / (downSteps))
            dc = dc - steps * 2
            if dc <= 0 :
                dc = 0
            pwmA.ChangeDutyCycle(dc)
            print("Gate A", dc, abs(steps))
        elif gateB is 1 and gateA is 0:
            pinOn(pinIn3)
            pinOff(pinIn4)
            sleep(delayTime)
            stop()
            steps = ((dc - dcMin) / (downSteps))
            dc = dc - steps * 2
            if dc <= 0 :
                dc = 0
            pwmB.ChangeDutyCycle(dc)
            print("Gate B", dc, abs(steps))
        elif gateA is 1 and gateB is 1:
            pinOn(pinIn1)
            pinOff(pinIn2)
            pinOn(pinIn3)
            pinOff(pinIn4)
            sleep(delayTime)
            stop()
            steps = ((dc - dcMin) / (downSteps))
            dc = dc - steps * 2
            if dc <= 0 :
                dc = 0
            pwmA.ChangeDutyCycle(dc)
            pwmB.ChangeDutyCycle(dc)
            print("Gate A & Gate B", dc, abs(steps))
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)

def stop():
    global pinIn1
    global pinIn2
    global pinIn3
    global pinIn4
    
    pinOff(pinIn1)
    pinOff(pinIn2)
    pinOff(pinIn3)
    pinOff(pinIn4)

def req(body, hostUrl, mode):
    try:
        hostUrl = hostUrl + mode
        response = requests.post(hostUrl, json=body)
        if response.status_code is 200:
            try:
                payload = json.loads(response.content.decode('utf-8'))
                return payload
            except ValueError as e:
                payload = str(response.content.decode('utf-8-sig'))
                try:
                    payload = json.loads(payload)
                    return payload
                except ValueError as e:
                    pprint(response.content)
                    pprint(e)
                    return 'Oops! json value error'
        else :
            return 'Oops! ' + response.reason + '/' + str(response.status_code)
    except Exception as e:
        pprint(e)
        return 'Oops! error occured'

def updateDB(plateId):
    global connection
    global cc
    global hostUrl
    # check if data exist
    dateNow = strftime("%Y-%m-%d", gmtime())
    dateNowFull = datetime.now()
    query1 = """SELECT
                *
            FROM
                `platenumbershistory`
            WHERE
                `plateNumbers` LIKE '{0}'
                AND
                    DATE(comeIn) = '{1}'
                AND
                    comeOut IS NULL;""".format(plateId, dateNow)
    cc.execute(query1)
    result1 = cc.fetchall() #if exist = 1 else 0
    body={}
    body["plateNumber"]= str(plateId)
    body["dateNow"]= str(dateNow)
    r = req(body, hostUrl, checkHistory)
    if str(r).find('Oops') is -1 and str(r).find('array') is -1:
        r = r['history']
        if result1 is not () and int(r) is 1:
            query2 = """UPDATE
                            `platenumbershistory`
                        SET
                            `comeOut` = '{0}'
                        WHERE
                            `platenumbershistory`.`plateNumbers` LIKE '{1}' 
                            AND
                                DATE(comeIn) = '{2}'
                            AND 
                                comeOut IS NULL;""".format(dateNowFull, plateId, dateNow)
            cc.execute(query2)
            result2 = cc.fetchall() #if exist = 1 else 0
            connection.commit()
            #for update body = {"plateNumber":"B 457 UTY","comeOut`":"2020-06-09 00:00:00.000000"}
            body={}
            body["plateNumber"]= str(plateId)
            body["dateNow"]= str(dateNow)
            body["comeOut"] = str(dateNowFull)
            r = req(body, hostUrl, updateData)
            if str(r).find('Oops') is -1 and str(r).find('array') is -1:
                r = r['update']
                if int(r) is 1:
                    return 'Update: True'
                elif int(r) is 0:
                    return 'Update: False'
            else:
                return str(r)
        elif result1 is () and int(r) is 0:
            query2 = """INSERT INTO `platenumbershistory`(
                            `ids`,
                            `plateNumbers`,
                            `comeIn`,
                            `comeOut`
                        )
                        VALUES(
                            NULL,
                            '{0}',
                            '{1}',
                            NULL
                        );""".format(plateId, dateNowFull)
            cc.execute(query2)
            result2 = cc.fetchall() #if exist = 1 else 0
            connection.commit()
            #for update body = {"plateNumber":"B 457 UTY","comeIn`":"2020-06-09 00:00:00.000000"}
            body={}
            body["plateNumber"]= str(plateId)
            body["dateNow"]= str(dateNow)
            body["comeIn"] = str(dateNowFull)
            r = req(body, hostUrl, insertData)
            if str(r).find('Oops') is -1 and str(r).find('array') is -1:
                r = r['insert']
                if int(r) is 1:
                    return 'Insert: True'
                elif int(r) is 0:
                    return 'Insert: False'
            else:
                return str(r)
    else:
        return str(r)

def checkDB(plateNumber):
    global connection
    global cc
    query = "SELECT * FROM `platenumbers` WHERE `plateNumbers` LIKE '%s';" % (plateNumber)
    result = cc.execute(query)
    rows = cc.fetchall()
    rCount = len(rows)
    #body = {"id":"B 457 UTY"}
    body = {}
    body["plateNumber"] = str(plateNumber)
    r = req(body, hostUrl, checkData)
    if str(r).find('Oops') is -1 and str(r).find('array') is -1:
        rCount2 = r['check']        
        if int(rCount) is 1 and int(rCount2) is 1:
            return True
        elif int(rCount) is 0 and int(rCount2) is 1:
            print("Local data not found, found online only.")
            return True
        elif int(rCount) is 0 or int(rCount2) is 0:
            return False
    else:
        return str(r)

def filterChars(str, set = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '):
    result = ''.join([l for l in str if l in set])
    return result

def autoCanny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged

# Automatic brightness and contrast optimization with optional histogram clipping
def abc(image, clip_hist_percent=10):
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
        
def plateDetect():
    # load the example image
    global args
    global temp_folder
    global ncf
    global s
    plateId = ''
    imgPath = temp_folder
    fN = ''
    #imgPath = '/home/pi/tesseract/test.bmp'
    thresh = []
    ncf = True
    bitwise = False
    iter = 1
    if args["image"] == "camera":
        webcam = cv2.VideoCapture(0)
        _, image = webcam.read()
        webcam.release()
    else:
        image = cv2.imread(args["image"])
    while ncf:
        # load the image and compute the ratio of the old height
        # to the new height, clone it, and resize it
        # auto brightness and contrast image
        image, _, _ = abc(image)
        ratio = image.shape[0] / 512.0
        orig = image.copy()
        image_resized = imutils.resize(image, height = 512)
        
        # convert the image to grayscale and blur it
        # in the image
        print("STEP 1: Preprocess image for CCA")
        gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("1.1. Grayscale",gray)
        cv2.imwrite(temp_folder + '1.1. Grayscale.png', gray)
        # dilation to strengthen the edges
        gray = cv2.convertScaleAbs(gray)
        # Creating the kernel for dilation
        kernel = np.ones((3,3), np.uint8)
        gray = cv2.dilate(gray,kernel,iterations=iter)
        #cv2.imshow("1.2. Dilated",gray)
        cv2.imwrite(temp_folder + '1.2. dilated.png', gray)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        #cv2.imshow("1.3. Blurred",blurred)
        cv2.imwrite(temp_folder + '1.3. Blurred.png', blurred)
        
        # threshold the image to reveal light regions in the
        # blurred image
        thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)[1]
        
        # perform a series of erosions and dilations to remove
        # any small blobs of noise from the thresholded image
        thresh = cv2.erode(thresh, None, iterations=1)
        thresh = cv2.dilate(thresh, None, iterations=2)
        if bitwise == True:
            thresh = cv2.bitwise_not(thresh)
        #cv2.imshow("1.4. Threshold",thresh)
        cv2.imwrite(temp_folder + '1.4. Threshold.png', thresh)
        
        # perform a connected component analysis on the thresholded
        # image, then initialize a mask to store only the "large"
        # components
        print("STEP 2: Perform a connected component analysis(CCA)")
        labels = measure.label(thresh, connectivity=1, background=0)
        mask = np.zeros(thresh.shape, dtype="uint8")
        
        # loop over the unique components
        for label in np.unique(labels):
            # if this is the background label, ignore it
            if label == 0:
                continue
            
            # otherwise, construct the label mask and count the
            # number of pixels 
            labelMask = np.zeros(thresh.shape, dtype="uint8")
            labelMask[labels == label] = 255
            numPixels = cv2.countNonZero(labelMask)
            
            # if the number of pixels in the component is sufficiently
            # large, then add it to our mask of "large blobs"
            if numPixels > 500:
                mask = cv2.add(mask, labelMask)
        
        # find the biggest of 4 point contours
        print("STEP 3: Find the biggest of 4 point contours")
        cnts = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
         
        # loop over the contours
        screenCnt = []
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            # if our approximated contour has four points, then we
            # can assume that we have found our screen
            if len(approx) == 4:
                screenCnt = approx
                ncf = False
                break
        if len(screenCnt) != 4:
            print("No contour found! restarting with new image from step 1 after ",  s," seconds!", end=" ", flush=True)
            if bitwise == True:
                iter += 1
            bitwise = True
            for i in range(5):
                sleep(1)
                print(".", end=" ", flush=True)
            print()
            ncf = True
        if ncf is False:
            # show the contour (outline) of the plate
            imageC = cv2.drawContours(image_resized, [screenCnt], -1, (0, 255, 0), 2)
            #cv2.imshow("2. Outlined", imageC)
            cv2.imwrite(temp_folder + '2. Outlined.png', imageC)
            
            # apply the four point transform to obtain a top-down
            # view of the original image_resized
            print("STEP 3: Apply perspective transform")
            warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
            #cv2.imshow("3.1. Warped", warped)
            cv2.imwrite(temp_folder + '3.1. Warped.png', warped)
            
            # crop image
            height, width, c = warped.shape
            height2 = height * 0.72
            #cv2.rectangle(warped,(0,0),(int(width), int(height2)),(0,255,0),3)
            cropped = warped[0:int(height2), 0:int(width)]
            height, width, c = cropped.shape
            lborder = width * 0.02
            tborder = height * 0.02
            rborder = width - (width * 0.02)
            cropped = cropped[int(tborder):height,int(lborder):int(rborder)]
            #cv2.imshow("3.2. Cropped", cropped)
            cv2.imwrite(temp_folder + '3.2. Cropped.png', cropped)
            
            # preprocess cropped image
            print("STEP 4: Preprocess/threshold image")
            # Convert cropped image to grayscale
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            #cv2.imshow("4.1. Grayscale 2", gray)
            cv2.imwrite(temp_folder + '4.1. Grayscale 2.png', gray)
            # Noise removal with iterative bilateral filter(removes noise while preserving edges)
            gray = cv2.bilateralFilter(gray,6,50,50)
            #cv2.imshow("4.2. Noise remove",gray)
            cv2.imwrite(temp_folder + '4.2. Noise remove.png', gray)    
            
            edged_crop = autoCanny(gray)
            #cv2.imshow("4.3. Edged 2", edged_crop)
            cv2.imwrite(temp_folder + '4.3. Edged 2.png', edged_crop)
            
            # Dilation+ to strengthen the edges
            dilated = cv2.convertScaleAbs(gray)
            # Creating the kernel for dilation
            kernel = np.ones((3,3), np.uint8)
            dilated = cv2.dilate(dilated,kernel,iterations=2)
            #cv2.imshow("4.4. Dilation", dilated)
            cv2.imwrite(temp_folder + '4.4. Dilated image.png', dilated)
            
            diff = []
            if args["diff"] == "diff":
                # Finding absolute difference to preserve edges
                diff = 128 - cv2.absdiff(dilated, edged_crop)
                #cv2.imshow("4.5. Absolute difference", diff)
                cv2.imwrite(temp_folder + '4.5. Diff.png', diff)
            elif args["diff"] == "non":
                diff = dilated
            
            # Normalizing between 0 to 255
            norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            #cv2.imshow("4.6. Normalized", norm)
            cv2.imwrite(temp_folder + '4.6. Normalized.png', norm)
            
            # Resize image
            sx = 1
            while int(norm.shape[1] * sx / 100) < 1920:
                sx += 1
            scale_percent = sx # percent of original size
            width = int(norm.shape[1] * scale_percent / 100)
            height = int(norm.shape[0] * scale_percent / 100)
            dim = (width, height)
            gray_resized = cv2.resize(norm, dim, interpolation = cv2.INTER_CUBIC)
            #cv2.imshow("4.7. Resized", gray_resized)
            cv2.imwrite(temp_folder + '4.7. Resized.png', gray_resized)
            
            # Blurring
            # Blurring
            if args["blur"] == "9":
                blur2 = cv2.medianBlur(gray_resized, 9)
            else:
                blur2 = cv2.medianBlur(gray_resized, int(args["blur"]))
            #cv2.imshow("4.8. Blurred", blur2)
            cv2.imwrite(temp_folder + '4.8. Blurred.png', blur2)
            
            # Thresholding
            thresh = cv2.threshold(blur2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            thresh = cv2.erode(thresh, None, iterations=1)
            thresh = cv2.dilate(thresh, None, iterations=1)
            count_white = cv2.countNonZero(thresh)
            count_black = thresh.shape[1] * thresh.shape[0] - count_white
            if bitwise == True or count_black > count_white :
                thresh = cv2.bitwise_not(thresh)
            cv2.imwrite(temp_folder + '4.9. Threshold.png', thresh)
            #cv2.imshow("4.9. Threshold", thresh)
            
            print("STEP 5: Extract text from image with tesseract")
            #plateId = pytesseract.image_to_string(thresh, lang='eng', config='-l eng --oem 3 --psm 7 outputbase nobatch')
            #plateId = pytesseract.image_to_string(thresh, lang='eng', config='-l eng --oem 0 --psm 7')
            custom_oem_psm_config = r'--oem 2 --psm 7 --tessdata-dir "/home/pi/tesseract/tessdata/"'
            plateId = pytesseract.image_to_string(blur2, lang='eng', config=custom_oem_psm_config)
            plateId = filterChars(plateId.upper())
            if plateId and not plateId.isspace():
                print('Plate number:', plateId)
                plateReg = checkDB(plateId)
                if plateReg == False:
                    print("Plate ID not registered! restarting with new image from step 1 after ",  s," seconds!", end=" ", flush=True)
                    for i in range(0, 5): #beep 5x
                        buzzOn(pinBuzzer)
                    for i in range(s):
                        sleep(1)
                        print(".", end=" ", flush=True)
                    print()
                    ncf = True
                else:
                    # Resize image to reduce blob size
                    scale_percent = 5 # percent of original size
                    width = int(thresh.shape[1] * scale_percent / 100)
                    height = int(thresh.shape[0] * scale_percent / 100)
                    dim = (width, height)
                    thresh = cv2.resize(thresh, dim, interpolation = cv2.INTER_CUBIC)
                    iP = filterChars(plateId, set = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
                    #cv2.imshow("4.9. Threshold resized", thresh)
                    fN = iP +'.png'
                    cv2.imwrite(temp_folder + fN, thresh)
                    imgPath += fN
                    break
            else:
                print("No detection! restarting with new image from step 1 after ",  s," seconds!", end=" ", flush=True)
                for i in range(s):
                    sleep(1)
                    print(".", end=" ", flush=True)
                print()
                ncf = True
            #cv2.rectangle(image,(0,0),(int(width),int(height2)),(0,255,0),3)
            #cv2.waitKey(0)
    return plateId, imgPath, fN

def buzzOn(pinBuzzer):
    pinOn(pinBuzzer)
    print ("Beep")
    sleep(1) # Delay in seconds
    pinOff(pinBuzzer)
    print ("No Beep")
    sleep(1)

def pinOff(pin):
    IO.setup(pin, IO.IN)

def pinOn(pin):
    IO.setup(pin, IO.OUT, initial=IO.HIGH)

def distance():
    # set Trigger to HIGH
    IO.output(GPIO_TRIGGER, True)
    
    # set Trigger after 0.01ms to LOW
    sleep(0.00001)
    IO.output(GPIO_TRIGGER, False)
    
    StartTime = time()
    StopTime = time()
    
    # save StartTime
    while IO.input(GPIO_ECHO) == 0:
        StartTime = time()
    
    # save time of arrival
    while IO.input(GPIO_ECHO) == 1:
        StopTime = time()
    
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    
    return distance

def irDetect():
    if IO.input(irPin1) == True and IO.input(irPin2) == True and IO.input(irPin3) == True: #object is far away
        irD = "WEIGHT OK"
    if IO.input(irPin1) == False or IO.input(irPin2) == False or IO.input(irPin3) == False: #object is near
        irD = "OVERWEIGHT"
    return irD

def usDetect():
    global dist
    newDistance = distance()
    if int(newDistance) != int(dist):
        print('Distance to nearest object is', newDistance, 'cm')
        dist = newDistance
    return dist

GPIO_TRIGGER = 17
GPIO_ECHO = 27

irPin1 = 16
irPin2 = 20
irPin3 = 21

pinBuzzer = 18

#L298N
pinIn1 = 13
pinIn2 = 19
pinEnableA = 26
pinIn3 = 23
pinIn4 = 24
pinEnableB = 25
delayTime = 0.25
upSteps = 9
downSteps = 9

IO.setmode (IO.BCM)
IO.setwarnings(False)

#set GPIO direction (IN / OUT)
IO.setup(GPIO_TRIGGER, IO.OUT)
IO.setup(GPIO_ECHO, IO.IN)

IO.setup(irPin1,IO.IN) #IR sensor as input
IO.setup(irPin2,IO.IN) #IR sensor as input
IO.setup(irPin3,IO.IN) #IR sensor as input

IO.setup(pinBuzzer,IO.OUT)

IO.setup(pinIn1, IO.OUT)
IO.setup(pinIn2, IO.OUT)
IO.setup(pinEnableA, IO.OUT)
IO.setup(pinIn3, IO.OUT)
IO.setup(pinIn4, IO.OUT)
IO.setup(pinEnableB, IO.OUT)

pinOff(pinIn1)
pinOff(pinIn2)
pinOff(pinIn3)
pinOff(pinIn4)

pwmA = IO.PWM(pinEnableA, 1000)
pwmA.start(0)
pwmA.ChangeDutyCycle(0)
pwmB = IO.PWM(pinEnableB, 1000)
pwmB.start(0)
pwmB.ChangeDutyCycle(0)

pinOff(pinBuzzer)
dist = distance()
sleep(1)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", default="camera",
    help="path to input image to be OCR'd")
ap.add_argument("-o", "--output", default="temp",
    help="path to output image")
ap.add_argument("-d", "--diff", default="non",
    help="diff image")
ap.add_argument("-b", "--blur", default="9",
    help="blur image")
ap.add_argument("-f", "--offline", default="online",
    help="don't update server (for testing image processing result)")
args = vars(ap.parse_args())

#Setting temp folder for images saving
if args["output"] == "temp":
    temp_folder = '/home/pi/tesseract/temp/'
else:
    temp_folder = args["output"]
#temp_folder = os.getcwd()+'/temp_folder2/'

#No countour found yet
ncf = True

#Delay 5s
s = 5

# Database setup..
## Create connection to MySQL server
print("Connecting ...")
try:
    connection = pymysql.connect(host='localhost',
                                 user='...',
                                 password='...',
                                 db='pi',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.Error as msg:
    print("Connection error: ", msg)
    exit()
## Create cursor
cc = connection.cursor()

gate = 'out' # in / out

if __name__ == '__main__':
    print('Running...')
    while True:
        try:
            if gate == 'out':
                if irDetect() is "OVERWEIGHT":
                    print(irDetect())
                    while irDetect() is "OVERWEIGHT":
                        buzzOn(pinBuzzer)
                        if irDetect() is not "OVERWEIGHT":
                            break
                else:
                    print(irDetect())
                    if int(usDetect()) <= 500:
                        print("Out Gate Plate detection...")
                        plateNumber, _, _ = plateDetect()
                        if args["offline"] == "online":
                            status = updateDB(plateNumber)
                            print(status)
                            sleep(0.5)
                        else:
                            print("Offline mode !")
                            sleep(0.5)
                        upward(1, 0)
                        sleep(10)
                        downward(1,0)
            else:
                if int(usDetect()) <= 500:
                    print("In Gate Plate detection...")
                    plateNumber, _, _ = plateDetect()
                    if args["offline"] == "online":
                        status = updateDB(plateNumber)
                        print(status)
                        sleep(0.5)
                    else:
                        print("Offline mode !")
                        sleep(0.5)
                    upward(1, 0)
                    sleep(10)
                    downward(1,0)
            sleep(0.5)
        except KeyboardInterrupt:
            print("Exiting...")
            connection.close()
            pwmA.stop()
            pwmB.stop()
            IO.cleanup()
            exit()
