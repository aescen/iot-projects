from threading import Thread
from pydub import AudioSegment
import pyaudio
import wave
import time
import sys


class RecordAudio:
    def __init__(self, device_id,
                 seconds=None,
                 maxlength=60,
                 filename='output',
                 chunk=8192,
                 sample_format=pyaudio.paInt16,
                 sample_rate=44100):
        self.seconds = seconds
        self.filename = filename
        self.chunk = chunk
        self.maxlength = maxlength
        self.sample_format = sample_format
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.stopped = True
        self.isrecording = False
        self.channels = 1
        if self.seconds != None:
            self.maxlength = None

    def recorder(self):
        def wav2ogg(filename):
            print('Converting wav to ogg...')
            audio = AudioSegment.from_wav(filename + '.wav')
            audio.export(filename + '.ogg', format='ogg')
            return audio

        p = pyaudio.PyAudio()  # Create an interface to PortAudio
        devinfo = p.get_device_info_by_index(self.device_id)
        if p.is_format_supported(self.sample_rate,  # Sample rate
                                 input_device=devinfo["index"],
                                 input_channels=devinfo['maxInputChannels'],
                                 input_format=self.sample_format):
            self.channels = devinfo['maxInputChannels']
            # print('Microphone supported! with id', devinfo["index"],
            #      ', rate', self.sample_rate,
            #      ', channels', devinfo['maxInputChannels'],
            #      ', format', self.sample_format)
        else:
            p.terminate()
            print('No input device supported. Exit.')
            sys.exit()
        stream = p.open(format=self.sample_format,
                        input_device_index=devinfo["index"],
                        channels=devinfo['maxInputChannels'],
                        rate=self.sample_rate,
                        frames_per_buffer=self.chunk,
                        input=True)
        frames = []  # Initialize array to store frames
        # Store data in chunks for X seconds
        t = time.time()
        print('Recording', end='')
        self.isrecording = True
        if self.maxlength == None:
            for i in range(0, int(self.sample_rate / self.chunk * (self.seconds))):
                if self.stopped:
                    break
                if time.time() - t >= 1:
                    print(".", end='', flush=True)
                    t = time.time()
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
            self.stopped = True
            return
        else:
            while True:
                if self.stopped:
                    break
                else:
                    if time.time() - t >= 1:
                        print(".", end='', flush=True)
                        t = time.time()
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    frames.append(data)
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()
        # Save the recorded data as a WAV file
        wf = wave.open(self.filename + ".wav", 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.sample_format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        wav2ogg(self.filename)
        print('Finished recording, file save as', self.filename + '.ogg')
        self.isrecording = False

    def record(self, filename=None):
        if filename != None:
            self.filename = filename
        self.stopped = False
        if not self.isrecording:
            nT = Thread(target=self.recorder, name='recordAudio')
            nT.start()

    def getFilename(self):
        return self.filename

    def isRecordDone(self):
        return not self.isrecording

    def stop(self):
        self.stopped = True
