# sudo python3 rt_OD_bird.py --prototxt MobileNetSSD.prototxt.txt --model MobileNetSSD.caffemodel --video "Video.mp4" --frameskip 30 --resize yes
# import the necessary packages
from firebase import Firebase #https://pypi.org/project/firebase/ : sudo pip3 install firebase python_jwt gcloud sseclient
from multiprocessing import Process
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import RPi.GPIO as GPIO
import argparse, imutils, cv2, sys, time

def pinOff(pin):
    GPIO.setup(pin, GPIO.IN)

def pinOn(pin):
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

# Default resolutions of the frame are obtained.The default resolutions are system dependent.
def manual_count(handler):
    frames = 0
    while True:
        frame = handler.read()
        frames += 1
    return frames

def pirDetect(pin):
    GPIO.setup(pin,GPIO.IN) #IR sensor as input
    if GPIO.input(pin) == True:
        return True
    elif GPIO.input(pin) == False:
        return False

def pirDetection():
    global pir
    global pirPin1
    global bcolors
    global args
    print(bcolors.OKBLUE + "[INFO] PIR detection start..." + bcolors.ENDC)
    try:
        detection = False
        tmp = False
        time.sleep(2)
        updateTikus(0)
        print(bcolors.WARNING + "[RESET] PIR: 0 | Time:", getTs(), "" + bcolors.ENDC)
        while True:
            tmp = pirDetect(pirPin1)
            if tmp:
                pir = 1
                setSpeaker(1, 'tikus')
                # update firebase
                updateTikus(pir)
                if tmp != detection:
                    detection = tmp
                    print(bcolors.OKGREEN + "[OK] PIR: 1 | Time:", getTs(), "" + bcolors.ENDC)
            else:
                pir = 0
                setSpeaker(0, 'tikus')
                updateTikus(pir)
                if tmp != detection:
                    detection = tmp
                    print(bcolors.OKGREEN + "[OK] PIR: 0 | Time:", getTs(), "" + bcolors.ENDC)
            time.sleep(1)
            
            if args["stdout"] == 'yes':
                sys.stdout.buffer.write(frame.tobytes())
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
    except (Exception) as exc:
        print(bcolors.FAIL + "[67-ERR]", exc, "" + bcolors.ENDC)
        return False
    except KeyboardInterrupt:
        print(bcolors.OKBLUE + '[INFO] Exiting...' + bcolors.ENDC)
        return False
    else:
        return True

def birdDetection():
    global motion
    global it
    global fps
    global bcolors
    global f
    global frame
    global h
    global w
    global vs
    global out
    global args    
    print(bcolors.OKBLUE + "[INFO] Bird detection start..." + bcolors.ENDC)
    try:
        updateBurung(0)
        print(bcolors.WARNING + "[RESET] Motion: 0 | Time:",getTs(), "" + bcolors.ENDC)
        time.sleep(2)
        tmp = -1
        fps = FPS().start()
        while True:
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            if '://' in args["video"] or args["video"] == 'stream':
                try:
                    frame = vs.read()
                except ValueError as e:
                    ret, frame = vs.read()
            else:
                try:
                    ret, frame = vs.read()
                except ValueError as e:
                    frame = vs.read()
            
            #read every [f]th frame
            if it % f == 0:
                motion = 0
                frame = frame[1]
                (h, w) = frame.shape[:2]
                pframe = frame
                if args["resize"] is "y" or args["resize"] is "yes" or args["resize"] is "Y" or args["resize"] is "Yes":
                    pframe = imutils.resize(frame, width=256)
                    blob = cv2.dnn.blobFromImage(cv2.resize(pframe, (256, 256)),
                        0.007843, (256, 256), 127.5)
                else: 
                    # grab the pframe dimensions and convert it to a blob
                    if args["video"] == 'stream':
                        (ph, pw) = pframe[1].shape[:2]
                    else:
                        (ph, pw) = pframe.shape[:2]
                    
                    blob = cv2.dnn.blobFromImage(cv2.resize(pframe, (pw, ph)),
                            0.007843, (pw, ph), 127.5)
                
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
                            motion = 1
                            # compute the (x, y)-coordinates of the bounding box
                            # for the object
                            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                            (startX, startY, endX, endY) = box.astype("int")
                            
                            # draw the bounding box around the detected object on
                            # the frame
                            label = "{}: {:.2f}%".format(CLASSES[idx],
                                confidence * 100)
                            cv2.rectangle(frame, (startX, startY), (endX, endY),
                                COLORS[idx], 1)
                            y = startY - 15 if startY - 15 > 15 else startY + 15
                            cv2.putText(frame, label, (startX, y),
                                cv2.FONT_HERSHEY_DUPLEX, 0.5, COLORS[idx], 1)
                
                # show the output pframe
                #cv2.imshow("pframe", pframe)
                #cv2.imshow("frame", frame)
                if tmp != motion:
                    # update firebase
                    updateBurung(motion)
                    print(bcolors.OKGREEN + "[OK] Motion:", motion, " | Time:",getTs(), "" + bcolors.ENDC)
                    tmp = motion
                if motion is 0:
                    setSpeaker(0, 'burung')
                elif motion is 1:
                    setSpeaker(1, 'burung')
                else:
                    setSpeaker(0, 'burung')
                # write the flipped frame
                out.write(frame)
                cv2.imwrite("frame.jpg", frame)
                cv2.imwrite("pframe.jpg", pframe)
                #cv2.imwrite("/var/www/tambak/video.jpg", frame)
                
                if args["stdout"] == 'yes':
                    sys.stdout.buffer.write(frame.tobytes())
                key = cv2.waitKey(1) & 0xFF
                
                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    print(bcolors.OKBLUE + '[INFO] Exiting...' + bcolors.ENDC)
                    sys.exit(0)
                
                frame = 0
            
            # if there is no more pframe, break from the loop
            if '://' not in args["video"] and '.' in args["video"]:
                if it >= frames:
                    break
            
            it = it + 1
            # update the FPS counter
            fps.update()
        
    except (Exception) as exc:
        print(bcolors.FAIL + "[201-ERR] ", exc, "" + bcolors.ENDC)
        return False
    except KeyboardInterrupt:
        print(bcolors.OKBLUE + '[INFO] Exiting...' + bcolors.ENDC)
        return False
    else:
        return True

def updateBurung(value = 0):
    db.child(path).update({pathBurung:value})

def updateTikus(value = 0):
    db.child(path).update({pathTikus:value})

def setSpeaker(value, mode):
    if mode is 'burung':
        if value is 0:
            pinOff(relayPin1)
        elif value is 1:
            pinOn(relayPin1)
        else:
            pinOff(relayPin1)
    elif mode is 'tikus':
        if value is 0:
            pinOff(relayPin2)
        elif value is 1:
            pinOn(relayPin2)
        else:
            pinOff(relayPin2)
    else:
        pinOff(relayPin1)
        pinOff(relayPin2)

def getTs():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) #xxxx-xx-xx xx:xx:xx

def cleanUp():
    # stop the timer and display FPS information
    fps.stop()
    print(bcolors.OKBLUE + "[INFO] elapsed time: {:.2f}".format(fps.elapsed()), "" + bcolors.ENDC)
    print(bcolors.OKBLUE + "[INFO] approx. FPS: {:.2f}".format(fps.fps()), "" + bcolors.ENDC)
    
    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    out.release()
    GPIO.cleanup()

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
    help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
    help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
    help="minimum probability to filter weak detections")
ap.add_argument("-r", "--resize", default='no', help="resize frame")
ap.add_argument("-v", "--video", default='stream', help="path/url to video file/streams")
ap.add_argument("-f", "--frameskip", default=10, help="frames to skip(default: 10)")
ap.add_argument("-s", "--stdout", default='no', help="use stdout to use vlc stream(yes or no, default: no)")
args = vars(ap.parse_args())

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print(bcolors.OKBLUE + "[INFO] Loading model ..." + bcolors.ENDC)
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print(bcolors.OKBLUE + "[INFO] Starting video stream ..." + bcolors.ENDC)
vs = 0
cap = 0
if args["video"] == 'stream':
    vs = cv2.VideoCapture(0)
    print(bcolors.OKBLUE + "[INFO] Using webcam as video stream ..." + bcolors.ENDC)
else:
    cap = cv2.VideoCapture(args["video"])
    vs = FileVideoStream(args["video"]).start()
    print(bcolors.OKBLUE + "[INFO] Using video file/url as video stream ..." + bcolors.ENDC)

# initialize GPIO
pirPin1 = 18
relayPin1 = 23
relayPin2 = 24
GPIO.setmode (GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pirPin1,GPIO.IN)
GPIO.setup(relayPin1, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(relayPin2, GPIO.OUT, initial=GPIO.HIGH)

pir = 0
motion = 0
path = "Roby"
pathBurung = "JumlahBurung"
pathTikus = "JumlahTikus"
pathSpeaker = "MenyalakanSpeaker"

# Database setup..
config = {
        "apiKey": "...",
        "authDomain": "...",
        "databaseURL": "...",
        "storageBucket": "..."
    }
firebase = Firebase(config)
db = firebase.database()

# loop over the frames from the video stream
if int(args["frameskip"]) == 0:
    args["frameskip"] = 10
print(bcolors.OKBLUE + "[INFO] Frameskip set to", args["frameskip"],"..." + bcolors.ENDC)
it,f = 0, int(args["frameskip"])
fps = 0

# Default resolutions of the frame are obtained.The default resolutions are system dependent.
if '://' in args["video"] or args["video"] == 'stream':
    try:
        frame = vs.read()
    except ValueError as e:
        ret, frame = vs.read()
else:
    try:
        ret, frame = vs.read()
    except ValueError as e:
        frame = vs.read()

if args["video"] == 'stream':
    (h, w) = frame[1].shape[:2]
else:
    (h, w) = frame.shape[:2]

if args["video"] != 'stream':
    try:
        # Fast, efficient but inaccurate method
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap = 0
    except:
        # Slow, inefficient but 100% accurate method 
        frames = manual_count(cap)
        cap = 0
 
# Define the codec and create VideoWriter object.The output is stored in 'output.avi' file.
if args["video"] != 'stream':
    print(bcolors.OKBLUE + "[INFO] Frame size:", frames , "@", h, "x", w, "" + bcolors.ENDC)
else:
    print(bcolors.OKBLUE + "[INFO] Video size:", h, "x", w, "" + bcolors.ENDC)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (w,h))

if __name__ == '__main__':
    time.sleep(1.0)
    print(bcolors.OKBLUE + '[INFO] Running...' + bcolors.ENDC)
    tmp = False
    try:
        p1 = Process(target=birdDetection)
        p2 = Process(target=pirDetection)
        p1.start()
        p2.start()
    except Exception as exc:
        p1.kill()
        p2.kill()
        cleanUp()
        updateBurung(0)
        updateTikus(0)
        if not tmp:
            print(bcolors.FAIL + '[383-ERR] Exiting...', exc, '' + bcolors.ENDC)
            tmp = True
        sys.exit(0)
    except KeyboardInterrupt:
        p1.kill()
        p2.kill()
        cleanUp()
        updateBurung(0)
        updateTikus(0)
        if not tmp:
            print(bcolors.OKBLUE + '[INFO] Exiting...' + bcolors.ENDC)
            tmp = True
        sys.exit(0)