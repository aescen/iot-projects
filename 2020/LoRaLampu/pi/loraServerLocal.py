from types import SimpleNamespace as Namespace
from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import json, sys, pymysql, time

BOARD.setup()

# Database setup..
## Create connection to MySQL server
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
#----------------------------------------------------------------------------------------->

class LoRaServer(LoRa):
    def __init__(self, localAddress, gateAddress, connection, verbose=False):
        super(LoRaServer, self).__init__(verbose)
        hexlit = lambda n:int(n, 16)
        self.localAddress = localAddress
        self.connection = connection
        self.cc = self.connection.cursor()
        self.hexlit = hexlit
        self.gateAddress = []
        for i in gateAddress:
            self.gateAddress.append(self.hexlit(i))
        #self.set_mode(MODE.SLEEP)
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
                ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rtcTime)) #xxxx-xx-xx xx:xx:xx
                try:
                    result = """
                        UPDATE
                            `lampu`
                        SET
                            `current` = '{1}',
                            `voltage` = '{2}',
                            `timestamp` = '{3}'
                        WHERE
                            `lampu`.`id` = '{0}';
                             """.format(hex(origin).upper().replace("0X", ""), current, voltage, ts)
                    print(result)
                    self.cc.execute(result)
                    self.connection.commit()
                except pymysql.err.InternalError as msg:
                    print("Command skipped: ", msg)
        except Exception as e:
            print("Error parsing JSON data: ", packet)      
        #self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

lora = LoRaServer(localAddress='0x01', gateAddress=['0xF0','0xF1'], connection=conn, verbose=False)

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
    sys.exit()
finally:
    sys.stdout.flush()
    print("")
    #lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
