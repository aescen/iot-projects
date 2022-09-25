#!/usr/bin/env python3
from time import sleep, strftime, localtime, time
from SX127x_mod.LoRa import *
from SX127x_mod.board_config import BOARD
import pymysql

BOARD.setup()

class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.localAddress = '0x00'
        clientsAddress = ['0x01', '0x02'] # right side, left side
        self.pinStopLamp = 12
        self.pinGoLamp = 16
        self.pinRightLamp = 20
        self.pinLeftLamp = 21
        self.time2wait = 1 #in minute
        self.clientsAddress = []
        self.hexlit = lambda n:int(n, 16)
        for i in clientsAddress:
            self.clientsAddress.append(self.hexlit(i))
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        try:
            self.connection = pymysql.connect(host='localhost',
                                         user='pi',
                                         password='raspberry',
                                         db='pi',
                                         charset='utf8',
                                         cursorclass=pymysql.cursors.DictCursor)
        except pymysql.err.Error as msg:
            print("Connection error: ", msg)
            sys.exit()
        self.cc = self.connection.cursor()
        self.trainCount = 0
        self.trainDetect = False
        self.directionLamp = "" # FromLeft, FromRight
        self.stopGoLamp = "-" # Stop, Go
        self.rightSide = 0
        self.leftSide = 0
        self.rightLamp = False
        self.leftLamp = False
        self.ts = strftime('%Y-%m-%d %H:%M:%S', localtime()) #xxxx-xx-xx xx:xx:xx
        self.update = True
        self.go = False
        self.stop = False
        self.wait = time()
        self.about2pass = False
    
    def on_rx_done(self):
        BOARD.led_on()
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        try:
            if len(payload) > 4:
                length = payload[2]
                data = payload[3:]
                try:
                    if len(data) is length:
                        self.ts = strftime('%Y-%m-%d %H:%M:%S', localtime()) #xxxx-xx-xx xx:xx:xx
                        receiver = self.hexlit(hex(int(payload[0])))
                        sender = self.hexlit(hex(int(payload[1])))
                        data = int(bytes(data).decode("utf8",'ignore'))
                        
                        if receiver is self.hexlit(self.localAddress) and sender in self.clientsAddress:
                            rssi_value = self.get_rssi_value()
                            print("")
                            print(self.ts, ":", "sender_id:", hex(sender).upper().replace("X", "x"), "data:", data, "RSSI:", rssi_value, end="", flush=True)
                            
                            if sender is self.clientsAddress[0]:
                                self.rightSide = data
                                self.leftSide = 0
                            elif sender is self.clientsAddress[1]:
                                self.leftSide = data
                                self.rightSide = 0
                            
                            if self.rightSide > 15:
                                self.wait = time()
                                self.stopGoLamp = "Stop"
                                if not self.leftLamp:
                                    BOARD.pinOn(self.pinRightLamp)
                                    if not self.rightLamp:
                                        self.update = True
                                    self.rightLamp = True
                                    print(" right lamp: ON")
                                    self.directionLamp = "FromRight"
                                    #sleep(60 * self.time2wait)
                                else:
                                    BOARD.pinOff(self.pinRightLamp)
                                    BOARD.pinOn(self.pinLeftLamp)
                                    self.rightLamp = False
                                    print(" right lamp: OFF")
                                    self.about2pass = True
                            
                            if self.leftSide > 15:
                                self.wait = time()
                                self.stopGoLamp = "Stop"
                                if not self.rightLamp:
                                    BOARD.pinOn(self.pinLeftLamp)
                                    if not self.leftLamp:
                                        self.update = True
                                    self.leftLamp = True
                                    self.directionLamp = "FromLeft"
                                    print(" left lamp: ON")
                                    #sleep(60 * self.time2wait)
                                else:
                                    BOARD.pinOn(self.pinRightLamp)
                                    BOARD.pinOff(self.pinLeftLamp)
                                    self.leftLamp = False
                                    print(" left lamp: OFF")
                                    self.about2pass = True
                            
                            sleep(1)
                        else:
                            print("\runknown client data, receiver id:%s sender id:%s" % (hex(receiver).upper().replace("X", "x"), hex(sender).upper().replace("X", "x")))
                except Exception as e:
                    print(e)
            elif len(payload) < 4 and len(payload) > 0:
                raise Exception("Payload length not enough!")
        except Exception as e:
            print(e, payload)
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.RXCONT)
    
    def on_tx_done(self):
        print("\nTxDone")
        print(self.get_irq_flags())
    
    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())
    
    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())
    
    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())
    
    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())
    
    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())
    
    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        BOARD.pinOff(self.pinStopLamp)
        BOARD.pinOff(self.pinGoLamp)
        BOARD.pinOff(self.pinRightLamp)
        BOARD.pinOff(self.pinLeftLamp)
        while True:
            #print(int(time() - self.wait), self.leftLamp, self.rightLamp, self.update, self.directionLamp, self.stopGoLamp)
            if self.leftLamp or self.rightLamp:
                if self.stop == False:
                    BOARD.pinOn(self.pinStopLamp)
                    BOARD.pinOff(self.pinGoLamp)
                    self.trainDetect = True
                    self.stopGoLamp = "Stop"
                    self.stop = True
                    self.go = False
                else:
                    if self.about2pass:
                        if ( time() - self.wait) >= 10:
                            self.leftLamp = False
                            self.rightLamp = False
                            self.about2pass = False
                            self.time = time()
                            self.ts = strftime('%Y-%m-%d %H:%M:%S', localtime()) #xxxx-xx-xx xx:xx:xx
                            print(self.ts, ": Train has passed.")
                            self.trainCount += 1
                            self.directionLamp = "none"
                            self.stopGoLamp = "Go"
                            self.update = True
                            BOARD.pinOff(self.pinRightLamp)
                            BOARD.pinOff(self.pinLeftLamp)
                    else:
                        self.time = time()
            elif not self.leftLamp and not self.rightLamp:
                if self.go == False:
                    BOARD.pinOff(self.pinStopLamp)
                    BOARD.pinOn(self.pinGoLamp)
                    self.stopGoLamp = "Go"
                    if self.trainDetect is True:
                        if self.update:
                            self.trainDetect = False
                            self.go = True
                            self.stop = False
            
            if self.update == True:
                try:
                    self.ts = strftime('%Y-%m-%d %H:%M:%S', localtime()) #xxxx-xx-xx xx:xx:xx
                    result = """
                        UPDATE
                            `loratrain`
                        SET
                            `traincount` = '{0}',
                            `directionlamp` = '{1}',
                            `stopgolamp` = '{2}',
                            `timestamps` = '{3}'
                        WHERE
                            `loratrain`.`id` = '1';
                             """.format(self.trainCount, self.directionLamp, self.stopGoLamp, self.ts)
                    #print(result)
                    print("")
                    print(self.ts, ": update database | train_count:", self.trainCount, "direction:", self.directionLamp, "stopgolamp:", self.stopGoLamp)
                    self.cc.execute(result)
                    self.connection.commit()
                    self.update = False
                except pymysql.err.InternalError as msg:
                    print("Command skipped: ", msg)
            sleep(0.5)


lora = LoRaRcvCont(verbose=False)

lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1) #Power Amplifier Boost
lora.set_bw(7) #125kHz
lora.set_spreading_factor(7)
lora.set_coding_rate(CODING_RATE.CR4_5)
lora.set_rx_crc(False)
lora.set_freq(467.5) #467.5MHz

print(lora)
assert(lora.get_agc_auto_on() == 1)

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    sys.stderr.write("KeyboardInterrupt\n")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
