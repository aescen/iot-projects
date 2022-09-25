#! /usr/bin/python3

import time
import sys
import numpy as np
from KalmanFilter import SimpleKalmanFilter

# SimpleKalmanFilter(e_mea, e_est, q);
#  e_mea: Measurement Uncertainty 
#  e_est: Estimation Uncertainty 
#  q: Process Noise

# skf = SimpleKalmanFilter(1, 1, 0.01)
skf = SimpleKalmanFilter(3, 1, 0.1)

# referenceUnit = 1
referenceUnit = 517

EMULATE_HX711=False



if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711py.hx711 import HX711
else:
    from hx711py.hx711 import HX711

def micros(): return int(round(time.time() * 1000000)) & 0xffffffff

def millis(): return int(round(time.time() * 1000)) & 0xffffffff

def seconds(): return int(round(time.time())) & 0xffffffff

def saveData(arr, filename):
    # use pandas
    #import pandas as pd
    #df = pd.DataFrame (arr)
    #df.to_excel(filename + '.xlsx', index=False)
    
    # use numpy
    np.savetxt(filename + ".csv", arr, delimiter = ",", fmt='%s')

def cleanAndExit():
    global dataArray
    saveData(dataArray, "sample")
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()


hx = HX711(21, 20) # DT, SCK

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")

# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()
dataArray = np.array([['Time', 'Value', 'Filtered'],])
while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
        
        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print(binary_string + " " + np_arr8_string)
        
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        val = max(0, int(hx.get_weight(3) * 1000)) / 1000
        filteredVal = skf.updateEstimate(val)
        #ts = time.time() # epoch
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) #xxxx-xx-xx xx:xx:xx
        dataArray = np.concatenate( (dataArray, [[ts, val, filteredVal]] ) )
        print("Value:", val)
        print("Filtered value:", filteredVal)

        # To get weight from both channels (if you have load cells hooked up 
        # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        #print("A: %s  B: %s" % ( val_A, val_B ))

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)
        
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
