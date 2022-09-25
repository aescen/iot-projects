import sys
import serial
from urllib import request, parse
import time

#Serial initialization
ser = serial.Serial('COM39',115200,timeout=10)
ser.isOpen()
print("To input a command press Ctrl-C!")
while True:
    try:
        dataRead = ser.readline().decode().strip("\r\n")
        if 'Coordinator' not in dataRead:
            print("Data: " + dataRead)
            dataSplit = dataRead.split(';')
            node = dataSplit[0]
            temp = dataSplit[1]
            RH = dataSplit[2]
            moist = dataSplit[3]
			
            f int(moist) <= 40:
                cmd = 'N0'+str(node)+'R0'+str(relay)+'&'
                ser.write(str.encode(cmd))

            url = "http://localhost/wsn/setsensor.php"
            data = {'node': node, 'temp': temp, 'RH': RH, 'moist': moist}
            data = parse.urlencode(data).encode()
            req = request.Request(url, data=data)
            response = request.urlopen(req)
            #print(response.read())
            dataRead = ""
            time.sleep(1)
    except KeyboardInterrupt:
        cmd = input("Enter 'c' to command a node or 'x' to terminate script!\n")
        if cmd.strip() == 'c':
            print("Entering command...!")
            print("All inbound feeds from serial are ignored.")

            # Ask for the node address to command
            node = input("Please enter node address to command: \n")
            try:
                node = int(node)
                # Ask for the relay address to command
                relay = input("Please enter relay address to set: \n")    
                #Sending command
                cmd = 'N0'+str(node)+'&'
                ser.write(str.encode(cmd))
                print(cmd)
                time.sleep(1)
                cmd = ''
            except ValueError:
                print("This is not a number")
        elif cmd.strip() == 'x':
            sys.exit()