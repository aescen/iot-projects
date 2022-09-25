# import required packages
import numpy as np
import argparse
import imutils
import cv2
import time
import sys

#================================================== functions
# Automatic brightness and contrast optimization with optional histogram clipping
def abc(image, clip_hist_percent=0.1):
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

def detect():
    global args
    global boundaries
    # load the image
    if args["image"] == "camera":
        webcam = cv2.VideoCapture(2)
        if webcam.isOpened():
            _, image = webcam.read()
        else:
            ret=False
    else:
        image = cv2.imread(args["image"])
    
    image = imutils.resize(image, height = 384, width = 683)
    if args["abc"] != "no":
        image, _, _= abc(image, clip_hist_percent=float(args["abc"]))
    label = "none"
    imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imsize = np.size(image)
    label = "none"
    detected= False
    # loop over the boundaries
    for (lower, upper, label, treshhold) in boundaries:
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
        cv2.imshow(label, np.hstack([image, output]))'''
        cv2.imwrite('imgs/1. imagegray.png', imageGray)
        #cv2.imwrite('imgs/2. imagehsv.png', v1)
        cv2.imwrite('imgs/2. imagemask.png', mask)
        cv2.imwrite('imgs/3. imageoutput.png', output)
        cv2.imwrite('imgs/4. imageoutputgray.png', outputGray)
        #cv2.imwrite('imgs/5. imageoutputhsv.png', v2)
        cv2.imwrite('imgs/5. imagestack.png', np.hstack([image, output]))
        
        if int(imnz) >=  int(t):
            detected = True
            cv2.imshow(label, np.hstack([ \
                imutils.resize(image, height = 192, width = 341), \
                imutils.resize(output, height = 192, width = 341)]))
            print("Detected: ", label)
            if cv2.waitKey(0):
                exit()
            break
        else:
            detected = False
    if label == "none":
        print("Not detected")
    if args["image"] == "camera":
        webcam.release()
    return label

#================================================== variables
#contruct argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", default="camera", help="path to input image")
ap.add_argument("-a", "--abc", default="no", help = "auto brightness and contrast clip histogram, ex. -a 0.1")
args = vars(ap.parse_args())

e1 = "Etching 1x"
e2 = "Etching 2x"
e3 = "Etching 3x"
e4 = "Etching 4x"
e5 = "Purple"
e6 = "Blue"
e7 = "Orange"
e8 = "Darkwood"
e9 = "Lake"

# define the list of color range boundaries
boundaries = [
    # B G R lower  B G R upper
    ([10, 15, 101], [20, 30, 120], e1, 0.04),
    ([13, 29, 82], [18, 39, 94], e4, 0.02),
    ([250, 20, 165], [255, 80, 191], e5, 0.05),
    ([190, 120, 60], [195, 128, 68], e6, 0.05),
    ([80, 91, 249], [84, 96, 254], e7, 0.05),
    ([15, 20, 34], [22, 32, 54], e8, 0.05),
    ([44, 49, 86], [142, 164, 223], e9, 0.05)
]

try:
    while True:
        status = detect()
except KeyboardInterrupt:
    exit()