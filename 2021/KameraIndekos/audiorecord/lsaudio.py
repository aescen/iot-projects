import pyaudio
import sys

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

input_device_id = 1
output_device_id = 3
if OS_TYPE == 'raspbianlinux':
    input_device_id = 1
    output_device_id = 0

fs = 44100

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
    print('Yay!')
devinfo = p.get_device_info_by_index(output_device_id)
print("Selected output device is ", devinfo.get('name'))
if p.is_format_supported(fs,  # Sample rate
                         output_device=devinfo["index"],
                         output_channels=devinfo['maxOutputChannels'],
                         output_format=pyaudio.paInt24):
    print('Yay!')
p.terminate()
