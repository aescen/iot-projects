from datetime import datetime
from firebase import Firebase #https://pypi.org/project/firebase/
from sys import exit
import RPi.GPIO as GPIO
import pymysql, time

config = {
    "apiKey": "...",
    "authDomain": "...",
    "databaseURL": "...",
    "storageBucket": "..."
    }
firebase = Firebase(config)
db = firebase.database()

s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 10

# Database setup..
## Create connection to MySQL server
print("Connecting ...")
try:
    connection = pymysql.connect(host='localhost',
                                 user='pi',
                                 password='raspberry',
                                 db='pi',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.Error as msg:
    print("Connection error: ", msg)
    exit()
## Create cursor
cc = connection.cursor()

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(signal,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s2,GPIO.OUT)
    GPIO.setup(s3,GPIO.OUT)
    print("\n")

def updateDB(jumlah, r, g, b, warna):
    timestamp = datetime.now()
    try:
        query = """
            UPDATE
                `kubis`
            SET
                `jumlah` = '{0}',
                `r` = '{1}',
                `g` = '{2}',
                `b` = '{3}',
                `timestamp` = '{4}'
            WHERE
                `kubis`.`warna` = '{5}'
                 """.format(jumlah, r, g, b, timestamp, warna)
        #print(query)
        cc.execute(query)
        connection.commit()
    except pymysql.err.InternalError as msg:
        print("Command skipped: ", msg)

def loop():
    cntHijau = 0
    cntCokelat = 0
    while(1):  
        GPIO.output(s2,GPIO.LOW)
        GPIO.output(s3,GPIO.LOW)
        time.sleep(0.3)
        start = time.time()
        for impulse_count in range(NUM_CYCLES):
            GPIO.wait_for_edge(signal, GPIO.FALLING)
        duration = time.time() - start 
        red  = NUM_CYCLES / duration
		
        GPIO.output(s2,GPIO.LOW)
        GPIO.output(s3,GPIO.HIGH)
        time.sleep(0.3)
        start = time.time()
        for impulse_count in range(NUM_CYCLES):
            GPIO.wait_for_edge(signal, GPIO.FALLING)
        duration = time.time() - start
        blue = NUM_CYCLES / duration
		
        GPIO.output(s2,GPIO.HIGH)
        GPIO.output(s3,GPIO.HIGH)
        time.sleep(0.3)
        start = time.time()
        for impulse_count in range(NUM_CYCLES):
            GPIO.wait_for_edge(signal, GPIO.FALLING)
        duration = time.time() - start
        green = NUM_CYCLES / duration
		
        rgb = [red, green, blue]
        print(red, green, blue)
        db.child("jtd").child("tcs").child("data").update({"rgb":rgb})
        if red>green and green>8104:
            print("Hijau")
            cntHijau += 1
            updateDB(cntHijau, round(red), round(green), round(blue), 'Hijau')
            db.child("jtd").child("tcs").child("data").update({"color":"Hijau"})
        elif blue>red and green<=8104:
            print("Cokelat")
            cntCokelat +=1
            updateDB(cntCokelat, round(red), round(green), round(blue), 'Cokelat')
            db.child("jtd").child("tcs").child("data").update({"color":"Cokelat"})
        elif red < 10000 and green < 10000 and blue < 10000:
            print("No object...")
        
        
        print("Hijau: ", cntHijau, " - Cokelat:", cntCokelat, sep="")
        time.sleep(10)

def endprogram():
    GPIO.cleanup()
    connection.close()
    exit()

if __name__=='__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        endprogram()
