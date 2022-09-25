from types import SimpleNamespace as Namespace
from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
from firebase import Firebase
import json

BOARD.setup()

config = {
  "apiKey": "...",
  "authDomain": "...",
  "databaseURL": "...",
  "storageBucket": "..."
}

firebase = Firebase(config)
fdb = firebase.database()

class LoRaServer(LoRa):
    def __init__(self, localAddress, gateAddress, db, verbose=False):
        super(LoRaServer, self).__init__(verbose)
        dbDataPath = db.child("jtd").child("lora").child("data")
        dbLogPath = db.child("jtd").child("lora").child("logs")
        hexlit = lambda n:int(n, 16)
        self.hexlit = hexlit
        self.localAddress = localAddress
        self.gateAddress = []
        for i in gateAddress:
            self.gateAddress.append(hexlit(i))
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.1)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        packet = bytes(payload).decode("utf8",'ignore')
        try:
            data = json.loads(packet, object_hook=lambda d: Namespace(**d))
            origin = self.hexlit(hex(int(data.o)))
            gate =   self.hexlit(hex(int(data.g)))
            dest =   self.hexlit(hex(int(data.d)))
            if dest == self.hexlit(self.localAddress) and gate in self.gateAddress:
                current = float(data.m.i)
                voltage = float(data.m.v)
                rtcTime = int(data.m.t)
                print("Received from", hex(origin).upper().replace("X", "x"), "Current:", current, "Voltage:", voltage, "Time:", rtcTime)
                self.db.child("jtd").child("lora").child("data").update({"current":current})
                self.db.child("jtd").child("lora").child("data").update({"voltage":voltage})
                self.db.child("jtd").child("lora").child("data").update({"timestamp":rtcTime})
        except Exception as e:
            print("Error parsing JSON data: ", packet)      
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

lora = LoRaServer(localAddress='0x01', gateAddress=['0xF0','0xF1'], db=fdb, verbose=False)

lora.set_pa_config(pa_select=1) #Power Amplifier Boost
lora.set_bw(7) #125kHz
lora.set_spreading_factor(7)
lora.set_coding_rate(CODING_RATE.CR4_5)
lora.set_rx_crc(False)
lora.set_freq(467.5) #467.5MHz

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
    BOARD.teardown()
