#!/usr/bin/python3

from os import name, system
from imutils.video import FileVideoStream
from imutils.video import FPS
from urllib.request import *
from urllib.error import URLError, HTTPError
#from pydub.utils import make_chunks
from pydub import AudioSegment
from threading import Thread
import pyttsx3
import shutil
import base64
import socket
import numpy as np
import traceback
import argparse
import requests
import imutils
#import logging
import telebot
import pyaudio
#import wave
import time
import cv2
import sys
#import vlc

# local import
from playaudio import PlayAudio
from recordaudio import RecordAudio

TTSengine = pyttsx3.init()

print("[INFO] Telegram init ...")
# Telegram bot API documentation : https://core.telegram.org/bots/api
TOKEN = '**:**'
CHAT_ID = '*'  # Grup chat KameraIndekos
bot = telebot.TeleBot(TOKEN)
commands = {  # command description used in the "help" command
    'start': 'Mulai bot',
    'help': 'Informasi perintah yang tersedia',
    'cuaca': 'Infomasi cuaca'
}
#strStop = 'Hentikan deteksi 2m.'
strSendVC = 'Kirim suara.'
strSendText = 'Kirim text.'
#strPass = 'Biarkan.'
#logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.

def removeFile(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))

def remap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def millis(): return int(round(time.time() * 1000)) & 0xffffffff


def seconds(): return int(round(time.time())) & 0xffffffff


def manual_count(handler):
    frames = 0
    while True:
        frame = handler.read()
        frames += 1
    return frames


@bot.message_handler(commands=['start'])
def command_start(message):
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    if message.chat.type == 'group':
        bot.reply_to(message, "Bot Kamera Indekos", reply_markup=markup)
    else:
        bot.reply_to(message, "Hai " + str(message.chat.first_name) +
                     "! Sayangnya bot ini hanya untuk percakapan group.", reply_markup=markup)


@bot.message_handler(commands=['help'])
def command_help(message):
    help_text = "Perintah yang tersedia: \n"
    for key in commands:
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['cuaca'])
def handle_message(message):
    def getWt():
        cuaca = requests.get('https://www.wttr.in/?format=3')
        bot.reply_to(message, "Hai @" + message.chat.username +
                     "! Cuaca hari ini:" + cuaca.text)
    nt = Thread(target=getWt, name='getWeather')
    nt.start()


# @bot.message_handler(func=lambda message: str(message.text) == strStop)
# def handle_message(message):
#    stopDeteksi(2)
#    markup = telebot.types.ReplyKeyboardRemove(selective=False)
#    bot.reply_to(message, "Deteksi dihentikan oleh @" +
#                 message.chat.username, reply_markup=markup)


@bot.message_handler(func=lambda message: str(message.text) == strSendVC)
def handle_message(message):
    markup = telebot.types.ForceReply(selective=False)
    bot.reply_to(message, '@' + str(message.chat.username) + " silakan kirim suara sekarang...",
                 reply_markup=markup)
    bot.register_next_step_handler(message, processVoice)

@bot.message_handler(func=lambda message: str(message.text) == strSendText)
def handle_message(message):
    markup = telebot.types.ForceReply(selective=False)
    bot.reply_to(message, '@' + str(message.chat.username) + " silakan kirim text sekarang...",
                 reply_markup=markup)
    bot.register_next_step_handler(message, processText2Voice)


# @bot.message_handler(func=lambda message: str(message.text) == strPass)
# def handle_message(message):
#    markup = telebot.types.ReplyKeyboardRemove(selective=False)
#    bot.reply_to(message, "Diacuhkan oleh @" +
#                 message.chat.username, reply_markup=markup)


# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(message, message.text)

def processText2Voice(message):
    def sayText():
        global output_device_id
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        try:
            cid = message.chat.id
            if message.text != None:
                bot.send_message(cid, 'Memutar voice...')
                TTSengine.say(str(message.text))
                TTSengine.runAndWait()
                bot.send_message(cid, 'Selesai...', reply_markup=markup)
            else:
                markup = telebot.types.ForceReply(selective=False)
                bot.reply_to(message, 'Tolong kirimkan text.',
                             reply_markup=markup)
                bot.register_next_step_handler(message, processText2Voice)

        except Exception:
            bot.reply_to(message, 'Oops, something went wrong!',
                         reply_markup=markup)

    nT = Thread(target=pV, name='procesVoice')
    nT.start()

def processVoice(message):
    def ogg2ogg(filename):
        audio = AudioSegment.from_file(filename, 'ogg')
        audio.export(filename, format='ogg')
        return audio

    def pV():
        global output_device_id
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        try:
            cid = message.chat.id
            if message.audio != None or message.voice != None:
                sound = None
                id = None
                if message.audio != None:
                    sound = bot.get_file(message.audio.file_id)
                    id = sound.file_id
                    fn = id + '.mp3'
                    sound = bot.download_file(sound.file_path)
                    with open(fn, 'wb') as new_audio:
                        new_audio.write(sound)
                    time.sleep(.5)
                    bot.send_message(cid, 'Memutar audio...')
                    #if OS_TYPE == 'raspbianlinux':
                    #    system('mpg123 ' + fn)
                    #else:
                    #    system('tskill vlc')
                    #    system('vlc -I cli --no-repeat --no-loop ' + fn)
                    pA = PlayAudio(fn, output_device_id, False)
                    pA.play()
                    bot.send_message(cid, 'Selesai...', reply_markup=markup)
                else:
                    sound = bot.get_file(message.voice.file_id)
                    id = sound.file_id
                    fn = id + '.ogg'
                    sound = bot.download_file(sound.file_path)
                    with open(fn, 'wb') as new_audio:
                        new_audio.write(sound)
                    time.sleep(.5)
                    # seg = ogg2ogg(fn)
                    bot.send_message(cid, 'Memutar voice...')
                    try:
                        if OS_TYPE == 'raspbianlinux':
                            system('ogg123 ' + fn)
                            removeFile(fn)
                        else:
                            system('tskill vlc')
                            system('vlc -I cli --no-repeat --no-loop ' + fn)
                    except:
                        pass
                    # print(fn)
                    #pA = PlayAudio(fn, output_device_id, False)
                    #pA.play()
                    bot.send_message(cid, 'Selesai...', reply_markup=markup)

            else:
                markup = telebot.types.ForceReply(selective=False)
                bot.reply_to(message, 'Tolong kirimkan voice/audio.',
                             reply_markup=markup)
                bot.register_next_step_handler(message, processVoice)

        except Exception:
            bot.reply_to(message, 'Oops, something went wrong!',
                         reply_markup=markup)

    nT = Thread(target=pV, name='procesVoice')
    nT.start()


def sendMessage(msg, chat_id):
    nT = Thread(target=bot.send_message, args=(
        chat_id, msg, ), name='sendMessage')
    nT.start()


def sendPhoto(path, chat_id):
    def newPhoto(path):
        newPhoto = open(path, 'rb')
        bot.send_photo(chat_id, newPhoto)

        markup = telebot.types.ReplyKeyboardMarkup(
            row_width=2, one_time_keyboard=True, resize_keyboard=True)
        #item1 = telebot.types.KeyboardButton(strStop)
        item2 = telebot.types.KeyboardButton(strSendVC)
        #item3 = telebot.types.KeyboardButton(strSendText)
        #item4 = telebot.types.KeyboardButton(strPass)
        # markup.row(item1)
        markup.row(item2)
        #markup.row(item3)
        # markup.row(item4)
        bot.send_message(
            chat_id, "Pilih tindakan:", reply_markup=markup)

    nT = Thread(target=newPhoto, args=(path, ), name='sendPhoto')
    nT.start()


def sendAudio(path, chat_id):
    def newAudio(path):
        newAudio = open(path, 'rb')
        bot.send_audio(chat_id, newAudio)

    nT = Thread(target=newAudio, args=(path, ), name='sendAudio')
    nT.start()


def botPolling(interval=0, none_stop=False):
    try:
        print('[INFO] BotPolling process running ...')
        bot.polling(none_stop=none_stop, interval=interval)
    except KeyboardInterrupt:
        bot.stop_polling
        return


def buzzUp(interval=60):
    global buzzerState
    global buzzerPin
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(buzzerPin, gpio.OUT)

    def turnOn():
        timerBuzzer = interval
        try:
            while True:
                if seconds() - timerBuzzer >= interval:
                    buzzerState = False
                else:
                    buzzerState = True

                if buzzerState == True:
                    gpio.output(buzzerPin, True)
                elif buzzerState == False:
                    gpio.output(buzzerPin, False)
                    break
                time.sleep(.05)
        except KeyboardInterrupt:
            gpio.output(buzzerPin, False)
            return

    nT = Thread(target=turnOn, name='BuzzupOn')
    nT.start()


def ledUp(pin, state):
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(pin, gpio.OUT)
    gpio.output(pin, state)


class BellButtonState:
    def __init__(self, bellButtonPin):
        self.bellButtonPin = bellButtonPin
        self.pinState = False
        self.stopped = False
        self.captureState = False

    def setState(self, state):
        self.captureState = state

    def getState(self):
        return self.captureState

    def poll(self):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(self.bellButtonPin, gpio.IN)
        try:
            while True:
                if self.stopped:
                    break
                if gpio.input(self.bellButtonPin) == True:
                    self.pinState = True
                    self.captureState = True
                elif gpio.input(self.bellButtonPin) == False:
                    self.pinState = False
                time.sleep(.05)
        except KeyboardInterrupt:
            return

    def stop(self):
        self.stopped = True

    def start(self):
        nT = Thread(target=self.poll, name='Poll bell btn')
        nT.start()


class RecordButtonState:
    def __init__(self, recordButtonPin):
        self.recordButtonPin = recordButtonPin
        self.pinState = False
        self.stopped = False

    def getState(self):
        return self.pinState

    def poll(self):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(self.recordButtonPin, gpio.IN)
        global recordTimer
        try:
            while True:
                if self.stopped:
                    break
                if gpio.input(self.recordButtonPin) == True:
                    self.pinState = True
                    recordTimer = seconds()
                elif gpio.input(self.recordButtonPin) == False:
                    self.pinState = False
                time.sleep(.05)
        except KeyboardInterrupt:
            return

    def stop(self):
        self.stopped = True

    def start(self):
        nT = Thread(target=self.poll, name='Poll bell btn')
        nT.start()


def stopDeteksi(interval=2):
    s = seconds() * 60

    def tick():
        while True:
            if seconds() - s >= interval:
                STOP_DETEKSI = False
                break
            else:
                STOP_DETEKSI = True
    Thread(target=tick, name='stopDeteksiTick').start


def startDeteksi():
    STOP_DETEKSI = False


def getTs(strDate, strSep, strTime):
    # xxxx-xx-xx_xx.xx.xx
    strFormat = "%Y{0}%m{0}%d{1}%H{2}%M{2}%S".format(strDate, strSep, strTime)
    return time.strftime(strFormat, time.localtime())


def getAbc(image, clip_hist_percent=0.5):
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


def faceDetect():
    global faceCascade
    global minFaceSize
    global frame
    global vs
    global itr
    global args
    global out
    global w
    global h
    global fps
    global sendInterval
    global CHAT_ID
    global STOP_DETEKSI
    global bellButtonPin
    global recordButtonPin
    global recordMin
    global username
    global password
    global webcam_url
    global maxWidth
    global maxHeight
    global input_device_id
    global output_device_id
    try:
        print('[INFO] FaceDetection process running ...')
        time.sleep(1)
        fps = FPS().start()
        faceTmp = 0
        timer = seconds()
        recordTimer = seconds()
        isRecording = False
        ra = RecordAudio(device_id=input_device_id)
        bbs = BellButtonState(bellButtonPin)
        bbs.start()
        rbs = RecordButtonState(recordButtonPin)
        rbs.start()
        while True:
            raw = None
            if args["video"] == 'stream':
                try:
                    socket.setdefaulttimeout(timeout)
                    request = Request(webcam_url)
                    if username != None and password != None:
                        base64string = base64.b64encode(
                            bytes('%s:%s' % (username, password), 'ascii'))
                        request.add_header(
                            "Authorization", "Basic %s" % base64string.decode('utf-8'))
                    with urlopen(request) as response:
                        imgArr = np.array(
                            bytearray(response.read()), dtype=np.uint8)
                        raw = cv2.imdecode(imgArr, cv2.IMREAD_COLOR)
                except HTTPError as e:
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
                except URLError as e:
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                except Exception:
                    print(traceback.format_exc())
            else:
                if OS_TYPE == 'windows':
                    raw = vs.read()[1]
                else:
                    raw = vs.read()

            if isinstance(raw, (list, tuple, np.ndarray)):
                (h, w) = raw.shape[:2]
                frame = raw
            else:
                continue

            itr += 1
            fps.update()

            if args["resize"] is "y" or args["resize"] is "yes" or args["resize"] is "Y" or args["resize"] is "Yes":
                pframe = imutils.resize(frame, width=maxWidth)
            else:
                pframe = frame
            if args["abc"] != "no":
                pframe, _, _ = getAbc(
                    pframe, clip_hist_percent=float(args["abc"]))
            try:
                (ph, pw) = pframe.shape[:2]
            except AttributeError:
                sys.stdout.flush()
                sys.stdout.write("\r[INFO] Loading:100%")
                break
            gray = cv2.cvtColor(pframe, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=3, minSize=minFaceSize)
            for (pfx, pfy, pfw, pfh) in faces:
                w_ratio = pw/w
                h_ratio = ph/h
                fx = int(pfx / w_ratio)
                fy = int(pfy / h_ratio)
                fw = int(pfw / w_ratio)
                fh = int(pfh / h_ratio)
                colorBox = (255, 0, 0)
                colorText = (255, 255, 255)
                pframe = cv2.rectangle(
                    pframe, (pfx, pfy), (pfx+pfw, pfy+pfh), color=colorBox, thickness=2)
                pframe = cv2.rectangle(
                    pframe, (pfx, pfy-15), (pfx+pfw, pfy), color=colorBox, thickness=-1)
                frame = cv2.rectangle(
                    frame, (fx, fy), (fx+fw, fy+fh), color=colorBox, thickness=2)
                frame = cv2.rectangle(
                    frame, (fx, fy-30), (fx+fw, fy), color=colorBox, thickness=-1)
                # roi_gray = gray[fy:fy+fh, fx:fx+fw]
                # roi_color = pframe[fy:fy+fh, fx:fx+fw]
                cv2.putText(pframe, 'Face(s):' +
                            str(len(faces)), (pfx+(int(pfw*0.025)), pfy-(int(pfh*0.025))), font, fontScale=0.5,
                            color=colorText, thickness=1, lineType=cv2.LINE_AA)
                cv2.putText(frame, 'Face(s):' +
                            str(len(faces)), (fx+(int(fw*0.025)), fy-(int(fh*0.025))), font, fontScale=0.5,
                            color=colorText, thickness=1, lineType=cv2.LINE_AA)
                newFaceTmp = len(faces)

                if bbs.getState():
                    if newFaceTmp != faceTmp:
                        if seconds() - timer >= sendInterval:
                            timer = seconds()
                            fname = str(getTs('-', '_', '.'))
                            path = "./imgs/" + fname + ".jpg"
                            cv2.imwrite(path, frame)
                            sendMessage('Face detected:' +
                                        str(len(faces)) + '@' +
                                        str(getTs('-', ' ', ':')), CHAT_ID)
                            sendPhoto(path, CHAT_ID)
                            faceTmp = newFaceTmp
                    bbs.setState(False)
                else:
                    faceTmp = -1

            if OS_TYPE != 'raspbianlinux':
                #cv2.imshow("pframe", pframe)
                cv2.imshow("frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

            out.write(frame)

            if rbs.getState():
                if not isRecording:
                    ledUp(recordLedPin, True)
                    ra.record()
                    recordTimer = seconds()
                    isRecording = True
            else:
                if isRecording:
                    if seconds() - recordTimer >= recordMin:
                        recordTimer = seconds()
                        ledUp(recordLedPin, False)
                        ra.stop()
                        if ra.isRecordDone():
                            # pa = PlayAudio(ra.getFilename() + '.ogg',
                            #                device_id=output_device_id)
                            # pa.play()
                            sendAudio(ra.getFilename() + '.ogg', CHAT_ID)
                            isRecording = False

        if args["video"] != 'stream':
            process = remap(itr, 0, frames, 0, 100)
            sys.stdout.flush()
            sys.stdout.write("\r[INFO] Loading:%d" % (process))
            sys.stdout.write("%")
        cleanUp()
        return True
    except Exception:
        print(traceback.format_exc())
        cleanUp()
        return False
    except KeyboardInterrupt:
        cleanUp()
        return False


def cleanUp():
    global fps
    global args
    global vc
    global vs
    global out

    cv2.destroyAllWindows()
    if fps != None:
        fps.stop()
        print("\n[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    print('[INFO] Clean up ...')
    if args["video"] != 'stream':
        if OS_TYPE == 'windows':
            vs.release()
        else:
            vs.stop()
    out.release()
    gpio.cleanup()
    print('[INFO] Exiting ...')


buzzerState = False
buzzerPin = 8
bellButtonState = False
bellButtonPin = 25
recordButtonState = False
recordButtonPin = 23
recordLedPin = 24
recordMin = 3
STOP_DETEKSI = False
IS_SIMULATION = False
OS_TYPE = None

if sys.platform == "linux" or sys.platform == "linux2":
    try:
        import RPi.GPIO as gpio
        OS_TYPE = 'raspbianlinux'
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(bellButtonPin, gpio.IN)
        gpio.setup(recordButtonPin, gpio.IN)
        gpio.setup(recordLedPin, gpio.OUT)
        gpio.setup(buzzerPin, gpio.OUT)
        IS_SIMULATION = False
    except (ImportError, RuntimeError):
        IS_SIMULATION = True
        OS_TYPE = 'linux'
elif sys.platform == "darwin":
    OS_TYPE = 'macos'
    IS_SIMULATION = True
elif sys.platform == "win32":
    from GPIOEmulator.EmulatorGUI import GPIO as gpio
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(bellButtonPin, gpio.IN)
    gpio.setup(recordButtonPin, gpio.IN)
    gpio.setup(recordLedPin, gpio.OUT)
    gpio.setup(buzzerPin, gpio.OUT)
    OS_TYPE = 'windows'
    IS_SIMULATION = True

input_device_id = 1
output_device_id = 3
if OS_TYPE == 'raspbianlinux':
    input_device_id = 1
    output_device_id = 0

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", default='stream',
                help="path/url to video file/streams")
ap.add_argument("-r", "--resize", default='n', help="resize video frame (y/n)")
ap.add_argument("-f", "--frameskip", default=2,
                help="frames to skip(default: 2)")
ap.add_argument("-a", "--abc", default="no",
                help="auto brightness and contrast clip histogram, ex. -a 0.75, to disable use -a no")
args = vars(ap.parse_args())
# https://github.com/opencv/opencv/tree/master/data/haarcascades
facePath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(facePath)
fps = None
sendInterval = 5
minFaceSize = (50, 50)
timeout = 5
maxHeight = 480
maxWidth = 640
# View camera online in Barrigada, Guam, Barrigada Mayor'S Office http://www.insecam.org/en/view/882308/
#webcam_url = "http://121.55.235.78/oneshotimage1"
username = "admin"
password = "admin"
webcam_url = "http://192.168.137.102/image.jpg"
vs = None
vc = None
frame = None
print("[INFO] Starting video stream ...")
if args["video"] == 'stream':
    try:
        socket.setdefaulttimeout(timeout)
        request = Request(webcam_url)
        if username != None and password != None:
            base64string = base64.b64encode(
                bytes('%s:%s' % (username, password), 'ascii'))
            request.add_header(
                "Authorization", "Basic %s" % base64string.decode('utf-8'))
        with urlopen(request) as response:
            imgArr = np.array(
                bytearray(response.read()), dtype=np.uint8)
            frame = cv2.imdecode(imgArr, cv2.IMREAD_COLOR)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    except Exception:
        print(traceback.format_exc())
else:
    vs = FileVideoStream(args["video"]).start()
    vc = cv2.VideoCapture(args["video"])
    print("[INFO] Using video file/url as video stream ...")

time.sleep(1.0)

if int(args["frameskip"]) < 0:
    args["frameskip"] = 0
print("[INFO] Frameskip set to", args["frameskip"], "...")
itr, f = 0, int(args["frameskip"])
frames = 0
fourcc = cv2.VideoWriter_fourcc(*'XVID')
h, w = frame.shape[:2]
out = cv2.VideoWriter('output.avi', fourcc, 15.0, (w, h))
font = cv2.FONT_HERSHEY_SIMPLEX

if args["video"] != 'stream':
    frames = 0
    try:
        frames = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        vc.release()
    except:
        frames = manual_count(vc)
        vc.release()
    print("[INFO] Frame size:", frames, "@", w, "x", h)
else:
    print("[INFO] Frame size:", w, "x", h)
print("[INFO] Init done ...")
time.sleep(1.0)

if __name__ == '__main__':
    botPollingThread = Thread(target=botPolling,
                              args=(0, True), name='BotPolling')
    faceDetectThread = Thread(target=faceDetect, name='FaceDetection')

    botPollingThread.start()
    faceDetectThread.start()
