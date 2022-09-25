import time
import sys

def octlit(val): return int(val, 8)

def millis(): return int(round(time.time() * 1000)) & 0xffffffff

def seconds(): return int(round(time.time())) & 0xffffffff

RASPBIAN = 'raspbian'
LINUX = 'linux'
MACOS = 'macos'
WINDOWS = 'windows'
OS_TYPE = ''

# check os type
if sys.platform == LINUX or sys.platform == "linux2":
    try:
        from struct import unpack, pack, Struct
        from RF24 import *
        from RF24Network import *
        from RF24Mesh import *
        import RPi.GPIO as GPIO

        OS_TYPE = RASPBIAN
    except (ImportError, RuntimeError):
        OS_TYPE = LINUX
elif sys.platform == "darwin":
    OS_TYPE = MACOS
elif sys.platform == "win32":
    OS_TYPE = WINDOWS
