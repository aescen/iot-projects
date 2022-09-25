from pydub.utils import make_chunks
from pydub import AudioSegment
from time import time
import pyaudio
import wave
import sys

__SOURCE__ = 'https://realpython.com/playing-and-recording-sound-python/'

if sys.platform == "linux" or sys.platform == "linux2":
    try:
        import RPi.GPIO as gpio
        OS_TYPE = 'raspbianlinux'
    except (ImportError, RuntimeError):
        OS_TYPE = 'linux'
elif sys.platform == "darwin":
    OS_TYPE = 'macos'
elif sys.platform == "win32":
    OS_TYPE = 'windows'

# pyaudio recording section
chunks = 8192
input_sample_format = pyaudio.paInt16
channels = 1
fs = 44100
seconds = 5
filename = "output"

input_device_id = 1
output_device_id = 3
if OS_TYPE == 'raspbianlinux':
    input_device_id = 1
    output_device_id = 0


def checkDevice():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    # for each audio device, determine if is an input or an output and add it to the appropriate list and dictionary
    for i in range(0, numdevices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            print("Input Device id ", i, " - ",
                  p.get_device_info_by_host_api_device_index(0, i).get('name'))

        if p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0:
            print("Output Device id ", i, " - ",
                  p.get_device_info_by_host_api_device_index(0, i).get('name'))

    devinfo = p.get_device_info_by_index(input_device_id)
    print("Selected input device is ", devinfo.get('name'))
    if p.is_format_supported(fs,  # Sample rate
                             input_device=devinfo["index"],
                             input_channels=devinfo['maxInputChannels'],
                             input_format=pyaudio.paInt16):
        print('Microphone supported!')
    devinfo = p.get_device_info_by_index(output_device_id)
    print("Selected input device is ", devinfo.get('name'))
    if p.is_format_supported(fs,  # Sample rate
                             output_device=devinfo["index"],
                             output_channels=devinfo['maxOutputChannels'],
                             output_format=pyaudio.paInt24):
        print('Speaker supported!')

    p.terminate()


def record(seconds,
           filename,
           chunk=chunks,
           sample_format=pyaudio.paInt16,
           device_id=None,
           channels=channels,
           sample_rate=fs):
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    if p.is_format_supported(sample_rate,
                             input_device=device_id,
                             input_channels=channels,
                             input_format=sample_format):
        print('Input id', device_id, 'with channels', channels, 'supported.')
    else:
        p.terminate()
        print('No input device supported. Exit.')
        sys.exit()
    stream = p.open(format=sample_format,
                    input_device_index=device_id,
                    channels=channels,
                    rate=sample_rate,
                    frames_per_buffer=chunks,
                    input=True)
    frames = []  # Initialize array to store frames
    # Store data in chunks for X seconds
    t = time()
    print('Recording', end='')
    for i in range(0, int(fs / chunks * seconds)):
        if time() - t >= 1:
            print(".", end='', flush=True)
            t = time()
        data = stream.read(chunks)
        frames.append(data)
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()
    # Save the recorded data as a WAV file
    wf = wave.open(filename + ".wav", 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    print('\nFinished recording, file save as', filename + '.wav')


def play(filename=None, seg=None, device_id=None):
    seg = seg
    if seg == None:
        if filename == None:
            raise Exception('You must provide filename.')
        else:
            seg = AudioSegment.from_file(filename)
    p = pyaudio.PyAudio()
    if p.is_format_supported(seg.frame_rate,
                             output_device=device_id,
                             output_channels=seg.channels,
                             output_format=p.get_format_from_width(seg.sample_width)):
        print('Output id', device_id, 'with channels', channels, 'supported.')
    else:
        p.terminate()
        print('No output device supported. Exit.')
        sys.exit()
    stream = p.open(rate=seg.frame_rate,
                    format=p.get_format_from_width(seg.sample_width),
                    channels=seg.channels,
                    output=True,
                    output_device_index=device_id)
    # Just in case there were any exceptions/interrupts, we release the resource
    # So as not to raise OSError: Device Unavailable should play() be used again
    try:
        print('Playing sound', end='')
        # break audio into quarter-second chunks (to allows keyboard interrupts)
        t = time()
        for chunk in make_chunks(seg, 250):
            if time() - t >= 1:
                print(".", end='', flush=True)
                t = time()
            stream.write(chunk._data)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print('\nDone.')


def wav2ogg(filename):
    print('Converting...')
    audio = AudioSegment.from_wav(filename + '.wav')
    audio.export(filename + '.ogg', format='ogg')
    return audio


checkDevice()
record(seconds, filename, chunks, input_sample_format,
       input_device_id, channels, fs)  # realtek input
seg = wav2ogg(filename)
play(seg=seg, device_id=output_device_id)  # realtek output
