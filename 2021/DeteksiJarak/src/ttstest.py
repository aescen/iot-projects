#!/usr/bin/python3

from threading import Thread
import pyttsx3
from time import sleep

class TextToSpeech:
    def __init__(self, rate=125, volume=1.0):
        self.isSpeaking = False
        self.rate = rate
        self.volume = volume
        self.engine = pyttsx3.init('espeak')
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        voices = self.engine.getProperty('voices')
        for v in voices:
            if(v.id == 'indonesian'):
                print(f'set voice: {v.id}')
                self.engine.setProperty('voice', v.id)
        self.text = 'Text To Speach'

    def getVoice(self):
        return self.engine.getProperty('voice')

    def say(self, text):
        self.text = text
        if not self.isSpeaking:
            saythread = Thread(target=self.sayThread,
                                  name='SayThread', args=())
            saythread.start()

    def sayThread(self):
        print(f'say: {self.text} with voice: {self.getVoice()}')
        self.isSpeaking = True
        self.engine.say(self.text)
        self.engine.runAndWait()
        self.isSpeaking = False

STR_MSG = 'Mohon Perhatian! Untuk menggunakan masker dan jaga jarak minimal 1 meter'
def main():
    try:
        tts = TextToSpeech()
        tts.say(STR_MSG)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
else:
    print('run from other than __main__')
