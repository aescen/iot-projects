import threading
from pydub.utils import make_chunks
from pydub import AudioSegment
from threading import Thread
import pyaudio
import shutil
import time
import sys
import os


class PlayAudio:
    def __init__(self, sound_path, device_id=4, keep_file=True):
        self.keep_file = keep_file
        self.sound_path = sound_path
        self.device_id = device_id
        self.stopped = False
        self.isplaying = False

    def removeFile(self, path):
        """ param <path> could either be relative or absolute. """
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)  # remove the file
        elif os.path.isdir(path):
            shutil.rmtree(path)  # remove dir and all contains
        else:
            raise ValueError("file {} is not a file or dir.".format(path))

    '''def play():
        player = vlc.MediaPlayer(sound_path)
        time.sleep(1)
        player.play()'''

    def player(self):
        if self.sound_path == None:
            print('Sound path cannot be None. Exit.')
            threading.main_thread().join()
            sys.exit()
        if self.device_id == None:
            print('Device id cannot be None. Exit.')
            threading.main_thread().join()
            sys.exit()
        seg = AudioSegment.from_file(self.sound_path, 'ogg')
        p = pyaudio.PyAudio()
        devinfo = p.get_device_info_by_index(self.device_id)
        #print("Selected input device is ", devinfo.get('name'))
        if p.is_format_supported(seg.frame_rate,  # Sample rate
                                 output_device=self.device_id,
                                 output_channels=seg.channels,
                                 output_format=p.get_format_from_width(seg.sample_width)):
            # print('Speaker supported! with id', devinfo["index"],
            #      ', rate', seg.frame_rate,
            #      ', channels', devinfo['maxOutputChannels'],
            #      ', format', p.get_format_from_width(seg.sample_width))
            pass
        else:
            p.terminate()
            print('No output device supported. Exit.')
            threading.main_thread().join()
            sys.exit()
        stream = p.open(format=p.get_format_from_width(seg.sample_width),
                        channels=devinfo['maxOutputChannels'],
                        rate=seg.frame_rate,
                        output_device_index=devinfo["index"],
                        output=True)
        # Just in case there were any exceptions/interrupts, we release the resource
        # So as not to raise OSError: Device Unavailable should play() be used again
        try:
            print('Playing sound', end='')
            self.isplaying = True
            # break audio into half-second chunks (to allows keyboard interrupts)
            t = time.time()
            for chunk in make_chunks(seg, 500):
                if self.stopped == True:
                    print('Stopped.')
                    break
                if time.time() - t >= 1:
                    print(".", end='', flush=True)
                    t = time.time()
                stream.write(chunk._data)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.stopped = True
            print('Done.')
            if not self.keep_file:
                self.removeFile(self.sound_path)

    def play(self):
        self.stopped = False
        if not self.isplaying:
            nT = Thread(target=self.player, name='playAudio')
            nT.start()

    def stop(self):
        self.stopped = True
