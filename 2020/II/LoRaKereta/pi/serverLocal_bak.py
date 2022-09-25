#!/usr/bin/env python3
from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import pymysql
from SX127x.LoRaArgumentParser import LoRaArgumentParser

try:
    conn = pymysql.connect(host='localhost',
                                 user='pi',
                                 password='raspberry',
                                 db='pi',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.Error as msg:
    print("Connection error: ", msg)
    sys.exit()

parser = LoRaArgumentParser("Lora tester")
BOARD.setup()

class LoRaRcvCont(LoRa):
    def __init__(self, localAddress, clientsAddress, connection, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        hexlit = lambda n:int(n, 16)
        self.localAddress = localAddress
        self.clientsAddress = []
        self.connection = connection
        self.cc = self.connection.cursor()
        self.hexlit = hexlit
        for i in clientsAddress:
            self.clientsAddress.append(self.hexlit(i))
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        

    def on_rx_done(self):
        BOARD.led_on()
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        length = payload[2]
        data = payload[3:]
        
        if len(data) is length:
            receiver = self.hexlit(hex(int(payload[0])))
            sender = self.hexlit(hex(int(payload[1])))
            data = int(bytes(data).decode("utf8",'ignore'))
            
            if receiver is self.hexlit(self.localAddress) and sender in self.clientsAddress:
                rssi_value = self.get_rssi_value()
                status = self.get_modem_status()
                sys.stdout.flush()
                sys.stdout.write("\rreceiver:%d sender:%d data:%d RSSI:%d rx:%d modem:%d" % (receiver, sender, data, rssi_value, status['rx_ongoing'], status['modem_clear']))
                #print("\rreceiver:%d sender:%d data:%d RSSI:%d rx:%d modem:%d" % (receiver, sender, data, rssi_value, status['rx_ongoing'], status['modem_clear']))
        
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
        while True:
            sleep(.1)


lora = LoRaRcvCont(localAddress='0x00', clientsAddress=['0x01','0x02'], connection=conn, verbose=False)
args = parser.parse_args(lora)

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
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    print(lora)
    BOARD.teardown()
