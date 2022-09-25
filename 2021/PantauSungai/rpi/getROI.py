import numpy
import cv2
import pickle
import os
import sys
import imutils


# mouse callback function
def draw_ROI(event, x, y, flags, param):
    global gx, gy, drawing, ROI, imgBGR, ratioH, ratioW, resized
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        gx, gy = x, y
        if resized:
            cv2.line(imgBGRResized, (gx,gy), (x,y), (0,0,255), 2)
        else:
            cv2.line(imgBGR, (gx,gy), (x,y), (0,0,255), 2)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if resized:
            cv2.rectangle(imgBGRResized,(gx,gy),(x,y),(0,0,255),2)
        else:
            cv2.rectangle(imgBGR,(gx,gy),(x,y),(0,0,255),2)
        
        if resized:
            ROI.append((int(gx*ratioW), int(gy*ratioH), int(x*ratioW), int(y*ratioH)))


if len(sys.argv) < 3:
    print('usage: getROI.py <empty lot image> <output ROI filename>')
    sys.exit(2)

drawing = False
gx,gy = -1,-1
ROI = []
maxWidth = 480
maxHeight = 360

#load image
imgBGR = cv2.imread(sys.argv[1],1)

#create window and point to mouse callback

resized = False
h, w = imgBGR.shape[:2]
ratioH = -1
ratioW = -1
imgBGRResized = ()

if h > maxHeight or w > maxWidth:
    resized = True
    imgBGRResized = imutils.resize(imgBGR, height=maxHeight, width=maxWidth)
    (hr, wr) = imgBGRResized.shape[:2]
    ratioH = h/hr
    ratioW = w/wr


if __name__ == '__main__':
    #main loop
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_ROI)
    while True:
        #show the image
        if resized:
            cv2.imshow('image', imgBGRResized)
        else:
            cv2.imshow('image', imgBGR)
        k = cv2.waitKey(1) & 0xFF
        if k == 13:
            break
    cv2.destroyAllWindows()

    #write data to output file
    f = open(sys.argv[2], 'wb')
    print(ROI)
    pickle.dump(ROI, f)
    f.close()