#!/usr/bin/env python3

# system imports
from datetime import datetime
from types import SimpleNamespace as Namespace
from threading import Thread
import cv2
import os
import sys
import time
import json
import argparse
import pymysql

# project imports
from utils import *
from SX127x.LoRa import *
from SX127x.board_config import BOARD

#const vars
APP_NAME = "SERVER APLIKASI PANTAU KUALITAS TANAH - KUD SUBUR"

class LoRaServer(LoRa):
    def __init__(self, localAddress, clientAddress, verbose=False):
        super(LoRaServer, self).__init__(verbose)
        hexlit = lambda n:int(n, 16)
        self.localAddress = localAddress
        self.hexlit = hexlit
        self.received = [ False, 0, 0, 0, 0, 0, 0, 0,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) ]
        self.clientAddress = []
        for i in clientAddress:
            self.clientAddress.append(self.hexlit(i))
        #self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.stoplora = False
        self.status = None
        self.rssi_value = None

    def stop(self):
        self.stoplora = True
    def start(self):
        def loraStart():
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)
            while True:
                if self.stoplora:
                    return
                time.sleep(.05)
                self.rssi_value = self.get_rssi_value()
                self.status = self.get_modem_status()
                #sys.stdout.flush()
        loraThread = Thread(target=loraStart, name='lora_start', args=())
        loraThread.daemon = True
        loraThread.start()

    def getReceivedData(self):
        return self.received

    def resetReceivedData(self):
        self.received[0] = False

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        payload = bytes(payload).decode("utf8",'ignore')
        try:
            packet = json.loads(payload, object_hook=lambda d: Namespace(**d))
            client = self.hexlit( hex(int(packet.c)) )
            server =   self.hexlit( hex(int(packet.s)) )
            data = packet.d
            if server == self.hexlit(self.localAddress) and client in self.clientAddress:
                cid = int(data.i)
                moist = float(data.sm);
                temp = float(data.st);
                ph = float(data.sp);
                npk = float(data.n);
                humidDHT = float(data.dh);
                tempDHT = float(data.dt);
                print("Received from", hex(client).upper().replace("X", "x"),
                    "Soil Moist:", moist,
                    "Soil Temp:", temp,
                    "Soil PH:", ph,
                    "Soil NPK:", npk,
                    "DHT Humid:", humidDHT,
                    "DHT Temp:", tempDHT,
                    "Client ID:", cid)
                ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) #xxxx-xx-xx xx:xx:xx
                self.received = [ True, cid, moist, temp, ph, npk, humidDHT, tempDHT, ts ]
        except Exception as e:
            print("Error parsing JSON data: ", packet)      
        #self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

def main():
    def getDbConnection(host='localhost', user='pi', password='raspberry', db='pi', charset='utf8'):
        try:
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                db=db,
                charset=charset,
                cursorclass=pymysql.cursors.DictCursor)
            return connection
        except pymysql.err.Error as msg:
            print("Connection error: ", msg)
            sys.exit()

    def saveCurrentDataToDb(nodeId):
        # save to db
        try:
            result = f"""
                UPDATE
                    `pupuk_sensor`
                SET
                    `dht_humid` = '{valHumidDHT}',
                    `dht_temp` = '{valTempDHT}',
                    `moist` = '{valMoist}',
                    `npk` = '{valNPK}',
                    `ph` = '{valPh}',
                    `lm35_temp` = '{valTemp}',
                    `voltage` = '{valVoltage}'
                WHERE `pupuk_sensor`.`id` = '{nodeId}'"""
            dbCursor.execute(result)
            dbConnection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)

    # Database setup..
    dbConnection = getDbConnection()
    dbCursor = dbConnection.cursor()

    # radio setup
    BOARD.setup()
    lora = LoRaServer(localAddress='0x01', clientAddress=['0xA0','0xA1'], verbose=False)
    lora.set_pa_config(pa_select=1) #Power Amplifier Boost
    lora.set_bw(7) #125kHz
    lora.set_spreading_factor(7)
    lora.set_coding_rate(CODING_RATE.CR4_5)
    lora.set_rx_crc(False)
    lora.set_freq(467.5) #467.5MHz
    
    # sensor vars
    valMoist = 0
    valTemp = 0
    valPh = 0
    valNPK = 0
    valHumidDHT = 0
    valTempDHT = 0
    
    newValMoist = 0
    newValTemp = 0
    newValPh = 0
    newValNPK = 0
    newValHumidDHT = 0
    newValTempDHT = 0
    
    valVoltage = 0
    newValVoltage = 0

    # timer vars
    sensorUpdateInterval = 1000
    sensorUpdateTimer = millis()

    ##------------------------------------------------------------------------------

    time.sleep(2)

    print('[INFO] Running ...')

    try:
        lora.start()
        while True:
            ret, clientId, newValMoist, newValTemp, newValPh, newValNPK, newValHumidDHT, newValTempDHT, ts = lora.getReceivedData()
            lora.resetReceivedData()
            if ret:
                # sensor data
                if millis() - sensorUpdateTimer >= sensorUpdateInterval:
                    if ( valMoist != newValMoist
                        or valTemp != newValTemp
                        or valPh != newValPh
                        or valNPK != newValNPK
                        or valHumidDHT != newValHumidDHT
                        or valTempDHT != newValTempDHT ):
                        
                        valMoist = newValMoist
                        valTemp = newValTemp
                        valPh = newValPh
                        valNPK = newValNPK
                        valHumidDHT = newValHumidDHT
                        valTempDHT = newValTempDHT

                        saveCurrentDataToDb(clientId)

                    sensorUpdateTimer = millis()

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("[INFO] exiting...")
        BOARD.teardown()
        sys.exit()

if __name__ == '__main__':
    print(APP_NAME)
    main()
