#!/usr/bin/env python3

from __future__ import print_function
from flask import Flask, render_template, request
from flask_talisman import Talisman
from struct import *
from RF24 import *
from RF24Network import *
from RF24Mesh import *
from array import array
from datetime import datetime
import time
import sys
import re
import pymysql

def octlit(val): return int(val, 8)
def millis(): return int(round(time.time() * 1000)) & 0xffffffff


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        result = request.form.to_dict()
        for key, value in result.items():
            if key == 'penggilingan':
                if value == 'on':
                    _ISPENGGILINGAN = True
                else:
                    _ISPENGGILINGAN = False
            elif key == 'takaran':
                _TAKARAN = int(value)
        return render_template('index.html', data=result)
    else:
        return render_template('index.html')


@app.route('/hello')
def hello_world():
    return 'hello world'


def sendPayload(_nodeID, _COMMAND):
    for i in mesh.addrListTop:
        if mesh.addrList[i].nodeID == _nodeID:
            _payload = pack("LL", octlit('00'), _COMMAND), ord('M')
            if not mesh.write(RF24NetworkHeader(octlit(_nodeID)), _payload):
                print("Send fail!")
            else:
                print("Send ok:", _nodeID, "->", _COMMAND)


def millis():
    return time.time()


def penggilingan(takaran, stop=False):
    if takaran == 1:
        pass
    elif takaran == 2:
        pass
    elif takaran == 3:
        pass


def miniGerbang(s):
    if s == _OPEN_GATE:
        pass
    else:
        pass

app = Flask(__name__)
Talisman(app)

try:
    connection = pymysql.connect(host='localhost',
                                 user='pi',
                                 password='raspberry',
                                 db='pi',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.Error as msg:
    print('Connection error: ', msg)
    exit()
cc = connection.cursor()

_BUFFER_SIZE = 8
radio = RF24(25, 0)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)
mesh.setNodeID(0)
radio.setPALevel(RF24_PA_MAX)
radio.printDetails()
print('Start server node:', mesh.getNodeID())

_ISPENGGILINGAN = False  # True=on, False=off
_PENGGILINGAN_STATUS = 0  # 0=kosong, 1=bekerja, 2=selesai
_KOSONG = 0
_BEKERJA = 1
_SELESAI = 2
_TAKARAN = 0
_MINIGERBANG_STATUS = 0
_t_minig = 2000
_m_minig = millis()
# Command
_ISREADY = 0
_OPEN_GATE = 1
_CLOSE_GATE = 2
# Response
_NODE_WORKING = 10
_NODE_READY = 11
_NODES_STATUS = {'01': _NODE_READY, '02': _NODE_READY, '03': _NODE_READY}
_t_check = 1000
_m_check = millis()
if __name__ == '__main__':
    app.run(host='192.168.137.254',port=8080,debug=True)  # default to localhost:5000
    # Main loop
    try:
        while True:
            mesh.update()
            mesh.DHCP()
            if network.available():
                _header, _payload = network.read(_BUFFER_SIZE)
                try:
                    if chr(_header.type) == 'M':
                        nodeID, response = unpack('LL', bytes(_payload))
                        meshID = "0" + str(nodeID)
                        meshID = "0" + str(_header.from_node)
                        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        response = int(response)
                        if response == _NODE_READY:
                            _NODES_STATUS[nodeID] = _NODE_READY
                        elif response == _NODE_WORKING:
                            _NODES_STATUS[nodeID] = _NODE_WORKING

                except Exception as e:
                    print('Error', e, ', payload length', len(_payload))
                    try:
                        _BUFFER_SIZE = int(re.findall(
                            r'\b\d+\b', str(e))[0])  # regexp
                        print('Will try with BUFFER_SIZE:',
                              _BUFFER_SIZE, ' instead...')
                    except Exception as t:
                        print('Error:', t, '- cannot change buffer size.')

            if _PENGGILINGAN_STATUS == _SELESAI and millis() - _m_check >= _t_check:
                _m_check = millis()
                for node, status in _NODES_STATUS:
                    if status == _NODE_READY:
                        miniGerbang(_OPEN_GATE)
                        sendPayload(node, _OPEN_GATE)
                    else:
                        sendPayload(node, _ISREADY)
            elif _ISPENGGILINGAN:
                penggilingan(_TAKARAN)
                _PENGGILINGAN_STATUS = _BEKERJA
            elif not _ISPENGGILINGAN and _PENGGILINGAN_STATUS == _BEKERJA:
                penggilingan(stop=True)
                _PENGGILINGAN_STATUS = _SELESAI

            if _MINIGERBANG_STATUS == _OPEN_GATE and millis() - _m_minig >= _t_minig:
                _m_minig = millis()
                miniGerbang(_CLOSE_GATE)

    except KeyboardInterrupt:
        radio.powerDown()
        sys.exit()
