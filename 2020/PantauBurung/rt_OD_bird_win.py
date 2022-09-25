# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse, imutils, time, cv2, sys

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
    help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
    help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
    help="minimum probability to filter weak detections")
ap.add_argument("-v", "--video", default='stream', help="path/url to video file/streams")
ap.add_argument("-r", "--resize", default='y', help="resize video frame (y/n)")
ap.add_argument("-f", "--frameskip", default=2, help="frames to skip(default: 2)")
ap.add_argument("-s", "--stdout", default='no', help="use stdout to use vlc stream(yes or no, default: no)")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]
#CLASSES = ["background","person"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

print("[INFO] Initializing ...")
# load our serialized model from disk
print("[INFO] Loading model ...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] Starting video stream ...")
if args["video"] == 'stream':
    vs = VideoStream(src=1).start()
    print("[INFO] Using webcam as video stream ...")
else:
    vs = FileVideoStream(args["video"]).start()
    vc = cv2.VideoCapture(args["video"])
    print("[INFO] Using video file/url as video stream ...")

time.sleep(2.0)

# loop over the frames from the video stream
if int(args["frameskip"]) < 0:
    args["frameskip"] = 0
print("[INFO] Frameskip set to", args["frameskip"],"...")
it, f = 0, int(args["frameskip"])

# range converter
def remap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

# Default resolutions of the frame are obtained.The default resolutions are system dependent.
def manual_count(handler):
    frames = 0
    while True:
        frame = handler.read()
        frames += 1
    return frames 

frame = vs.read()
(h, w) = frame.shape[:2]
if args["video"] != 'stream':
    frames = 0
    try:
        # Fast, efficient but inaccurate method
        frames = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        vc.release()
    except:
        # Slow, inefficient but 100% accurate method 
        frames = manual_count(vc)
        vc.release()
    print("[INFO] Frame size:", frames , "@", h, "x", w)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (w,h))
#out = cv2.VideoWriter('output.avi', -1, 20.0, (w,h))
print("[INFO] Init done.")

time.sleep(1.0)
fps = FPS().start()

while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    #frame = imutils.resize(frame, width=800)
    #frame = imutils.resize(frame, width=400) 
    if int(args["frameskip"]) > 0:
        #read every frameskip-th frame
        if it % f == 0:
            pframe = frame
            # grab the pframe dimensions and convert it to a blob
            try:
                (ph, pw) = pframe.shape[:2]
            except AttributeError:
                sys.stdout.flush()
                sys.stdout.write("\r[INFO] Loading:100%")
            
            blob = cv2.dnn.blobFromImage(cv2.resize(pframe, (pw, ph)),
                    0.007843, (pw, ph), 127.5)
            if args["resize"] is "y" or args["resize"] is "yes" or args["resize"] is "Y" or args["resize"] is "Yes":
                pframe = imutils.resize(frame, width=200)
                blob = cv2.dnn.blobFromImage(cv2.resize(pframe, (200, 200)),
                    0.007843, (200, 200), 127.5)
            
            # pass the blob through the network and obtain the detections and
            # predictions
            net.setInput(blob)
            detections = net.forward()
            
            # loop over the detections
            for i in np.arange(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the prediction
                confidence = detections[0, 0, i, 2]
                
                # filter out weak detections by ensuring the `confidence` is
                # greater than the minimum confidence
                if confidence > args["confidence"]:
                    # extract the index of the class label from the
                    # `detections`, then compute the (x, y)-coordinates of
                    # the bounding box for the object
                    idx = int(detections[0, 0, i, 1])
                    #only show person which index is 15
                    if idx == 3:
                        # compute the (x, y)-coordinates of the bounding box
                        # for the object
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")
                        
                        # draw the bounding box around the detected object on
                        # the frame
                        label = "{}: {:.2f}%".format(CLASSES[idx],
                            confidence * 100)
                        cv2.rectangle(frame, (startX, startY), (endX, endY),
                            COLORS[idx], 2)
                        y = startY - 15 if startY - 15 > 15 else startY + 15
                        cv2.putText(frame, label, (startX, y),
                            cv2.FONT_HERSHEY_DUPLEX, 0.5, COLORS[idx], 1)
            
            # show the output pframe
            #cv2.imshow("pframe", pframe)
            cv2.imshow("frame", frame)
            out.write(frame)
            
            if args["stdout"] == 'yes':
                sys.stdout.buffer.write(frame.tobytes())
            
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
    
    elif int(args["frameskip"]) == 0:
        pframe = frame
        # grab the pframe dimensions and convert it to a blob
        try:
            (ph, pw) = pframe.shape[:2]
        except AttributeError:
            sys.stdout.flush()
            sys.stdout.write("\r[INFO] Loading:100%")
        blob = cv2.dnn.blobFromImage(cv2.resize(pframe, (300, 300)),
            0.007843, (300, 300), 127.5)
        
        if args["resize"] is "y" or args["resize"] is "yes" or args["resize"] is "Y" or args["resize"] is "Yes":
            pframe = imutils.resize(frame, width=200)
        
        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()
        
        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]
            
            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > args["confidence"]:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                #only show person which index is 3
                if idx == 3:
                    # compute the (x, y)-coordinates of the bounding box
                    # for the object
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    
                    # draw the bounding box around the detected object on
                    # the frame
                    label = "{}: {:.2f}%".format(CLASSES[idx],
                        confidence * 100)
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                        COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, COLORS[idx], 1)
        
        # show the output pframe
        #cv2.imshow("pframe", pframe)
        cv2.imshow("frame", frame)
        out.write(frame)
        
        if args["stdout"] == 'yes':
            sys.stdout.buffer.write(frame.tobytes())
        
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
    if args["video"] != 'stream':
        process = remap(it, 0, frames, 0, 100)
        sys.stdout.flush()
        sys.stdout.write("\r[INFO] Loading:%d" % (process))
        sys.stdout.write("%")
    it = it + 1
    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("\n[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
out.release()