#!/usr/bin/env python3

# system imports
from datetime import datetime
import os
import sys
import time
import argparse
import pymysql

# project imports
from utils import *

#const vars
APP_NAME = "SERVER APLIKASI MANAJEMEN ENERGI"
HEADER_SERVER = 'S'
HEADER_NODE = 'N'
NODE_1_ID = 1
NODE_2_ID = 2

BAT_RUSAK = 0.0
BAT_RENDAH = 12.0
BAT_NORMAL = 13.8
BAT_BERLEBIH = 13.8

def main():
    def meshUpdate():
        try:
            mesh.DHCP()
            mesh.update()
        except Exception as e:
            print(e)

    def readMeshNetwork(headerProp):
        payload = { 'id': None, 'nid': None, 'type': None, 'data': None }
        data = {}
        if network.available():
            try:
                header, data = network.read(32)
                if chr(header.type) in headerProp['type']:
                    ststr = headerProp[chr(header.type)]
                    payload['id'] = int(header.from_node)
                    payload['type'] = chr(header.type)
                    payload['data'] = unpack(ststr, bytes(data))
                    return payload
                else:
                    print('Rcv bad type {} from 0{:o}'.format(chr(header.type), header.from_node));
                    return payload
            except Exception as e:
                print('Error', e, ', payload length', len(data))
                return payload
            except Exception as e:
                print(e)
                return payload
        return payload

    def getDbConnection(host='localhost', user='pi', password='raspberry', db='pi', charset='utf8'):
        try:
            connection = pymysql.connect(host=host,
                                         user=user,
                                         password=password,
                                         db=db,
                                         charset=charset,
                                         cursorclass=pymysql.cursors.DictCursor)
            return connection
        except pymysql.err.Error as msg:
            print("Connection error: ", msg)
            sys.exit()

    def saveStatusDataToDb(nid):
        # save to db
        try:
            result =  f"""
                    UPDATE
                        `energyman`
                    SET 
                         `current_1` = '{valArus1}',
                         `current_2` = '{valArus2}',
                         `voltage` = '{valTegangan}',
                         `battery` = '{valBaterai}',
                         `charge` = '{valPengisian}',
                         `relay_1` = '{valRelay1}',
                         `relay_2` = '{valRelay2}'
                    WHERE
                        `energyman`.`name` = '{nid}'
                    """
            dbCursor.execute(result)
            dbConnection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)
    
    def saveChargingDataToDb(nid, loc):
        # save to db
        try:
            result = f"""
                       INSERT INTO
                         `energyman_charging_log` ( `id`,
                            `name`,
                            `current_1`,
                            `current_2`,
                            `voltage`,
                            `battery`,
                            `charge`,
                            `overcharged`,
                            `health`,
                            `location`,
                            `time_stamp` )
                       VALUES ( NULL,
                            '{nid}',
                            '{valArus1}',
                            '{valArus2}',
                            '{valTegangan}',
                            '{valBaterai}',
                            '{valPengisian}',
                            '{valTeganganLebih}',
                            '{valKondisiBaterai}',
                            '{loc}',
                            current_timestamp() )
                     """
            row = dbCursor.execute(result)
            dbConnection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)
    
    def saveTransmissionDataToDb(nid, total):
        def checkIfExist():
            sql = f"""
                    SELECT * FROM `energyman_transmission_log`
                        WHERE `name` = '{nid}'
                        AND `time_stamp` = '{datetime.now().strftime('%Y-%m-%d')}'
                """
            rowCount = dbCursor.execute(sql)
            if rowCount == 1:
                return True
            return False
        # save to db
        try:
            isExist = checkIfExist()
            if isExist:
                result = f"""
                        UPDATE `energyman_transmission_log` SET `total` = '{total}'
                            WHERE
                                `energyman_transmission_log`.`name` = '{nid}'
                            AND
                                `energyman_transmission_log`.`time_stamp` = '{datetime.now().strftime('%Y-%m-%d')}'
                    """
            else:
                result = f"""
                        INSERT INTO `energyman_transmission_log` (`id`, `name`, `total`, `time_stamp`)
                        VALUES (NULL, '{nid}', '{total}', '{datetime.now().strftime('%Y-%m-%d')}')
                    """
            row = dbCursor.execute(result)
            dbConnection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)
    
    def getBatteryHealth(volt):
        if volt == BAT_RUSAK:
            return 'RUSAK'
        elif volt > BAT_RUSAK and volt <= BAT_NORMAL:
            return 'TEGANGAN RENDAH'
        elif volt > BAT_NORMAL and volt <= BAT_BERLEBIH:
            return 'NORMAL'
        elif volt > BAT_BERLEBIH:
            return 'TEGANGAN BERLEBIH'

    # Database setup..
    dbConnection = getDbConnection()
    dbCursor = dbConnection.cursor()

    # NRF radio setup
    radio = RF24(22, 0)
    network = RF24Network(radio)
    mesh = RF24Mesh(radio, network)

    mesh.setNodeID(0)
    if not radio.begin():
        print("Radio hardware not responding!")
        sys.exit()
    mesh.begin(111, RF24_1MBPS, 10000)
    radio.setRetries(2, 8)
    radio.setPALevel(RF24_PA_MAX) # Power Amplifier
    time.sleep(.1)
    radio.printPrettyDetails()
    print(APP_NAME)

    # sensor/status vars
    updateStatus = True
    valArus1 = 0
    valArus2 = 0
    valTegangan = 0
    valBaterai = 0
    valPengisian = 0
    newValArus1 = 0
    newValArus2 = 0
    newValTegangan = 0
    newValBaterai = 0
    newValPengisian = 0
    
    valRelay1 = 0
    valRelay2 = 0
    newValRelay1 = 0
    newValRelay2 = 0
    
    #charging vars
    updateCharging = True
    valTeganganLebih = 0
    valKondisiBaterai = 0
    newValTeganganLebih = 0
    newValKondisiBaterai = 0

    # timer vars
    dataUpdateTimer = millis()
    dataUpdateInterval = 1000 #2000ms
    
    chargingUpdateTimer = seconds()
    chargingUpdateInterval = 6 #60s
    
    transmissionUpdateTimer = seconds()
    transmissionUpdateInterval = 3 #30s

    # mesh vars
    headerProperties = {
        HEADER_NODE: 'ffff ffff',
        HEADER_SERVER: 'f',
        'type': [HEADER_NODE, HEADER_SERVER]
    }
    
    nodeTransmissionTotal = {
        NODE_1_ID: 0,
        NODE_2_ID: 0
    }
    
    nodeLocations = {
        NODE_1_ID: 'Gd. A1',
        NODE_2_ID: 'Atap'
    }
    
    nodeIds = {
        NODE_1_ID: 'NODE 1',
        NODE_2_ID: 'NODE 2',
    }

    ##------------------------------------------------------------------------------

    time.sleep(1)
    print('[INFO] Running ...')

    while True:
        try:
            # mesh
            meshUpdate()
            meshData = readMeshNetwork(headerProperties)

            if meshData['data'] != None:
                if meshData['type'] == HEADER_NODE:
                    i1, i2, v, b, c, r1, r2, nid = meshData['data']
                    newValArus1 = float(i1)
                    newValArus2 = float(i2)
                    newValTegangan = float(v)
                    newValBaterai = int(b)
                    newValPengisian = int(c)
                    newValRelay1 = int(r1)
                    newValRelay2 = int(r2)
                    nid = int(nid)
                    meshData['nid'] = nid
                    # add transmission
                    nodeTransmissionTotal[meshData['nid']] += 1
                    updateStatus = True
                    updateCharging = True
                    print(datetime.now().strftime(
                        '%H:%M:%S-%d/%m/%Y'),
                        f"Node: {meshData['nid']} - "
                        f"Arus 1: {i1:.2f} - "
                        f"Arus 2: {i2:.2f} - "
                        f"Tegangan: {v:.2f} - "
                        f"Baterai: {int(b)} - "
                        f"Overcharge: {int(c)} - "
                        f"Relay 1: {int(r1)} - "
                        f"Relay 2: {int(r2)}"
                    )
                    
            # sensor data
            if millis() - dataUpdateTimer > dataUpdateInterval and meshData['data'] != None:
                if ( valArus1 != newValArus1
                  or valArus2 != newValArus2
                  or valTegangan != newValTegangan
                  or valBaterai != newValBaterai
                  or valPengisian != newValPengisian
                  or valRelay1 != newValRelay1
                  or valRelay2 != newValRelay2
                  or updateStatus ):
                    valArus1 = newValArus1
                    valArus2 = newValArus2
                    valTegangan = newValTegangan
                    valBaterai = newValBaterai
                    valPengisian = newValPengisian
                    valRelay1 = newValRelay1
                    valRelay2 = newValRelay2
                    saveStatusDataToDb(nodeIds[meshData['nid']])
                    updateStatus = False

                dataUpdateTimer = millis()
            
            # charging
            if seconds() - chargingUpdateTimer > chargingUpdateInterval and meshData['data'] != None:
                if ( valArus1 != newValArus1
                  or valArus2 != newValArus2
                  or valTegangan != newValTegangan
                  or valBaterai != newValBaterai
                  or valPengisian != newValPengisian
                  or valRelay1 != newValRelay1
                  or valRelay2 != newValRelay2
                  or updateCharging ):
                    valArus1 = newValArus1
                    valArus2 = newValArus2
                    valTegangan = newValTegangan
                    valBaterai = newValBaterai
                    valPengisian = newValPengisian
                    valRelay1 = newValRelay1
                    valRelay2 = newValRelay2
                    valKondisiBaterai = getBatteryHealth(valTegangan)
                    valTeganganLebih = 0 if valTegangan - 13.8 < 0 else valTegangan - 13.8
                    saveChargingDataToDb(nodeIds[meshData['nid']], nodeLocations[meshData['nid']])
                    updateCharging = True

                chargingUpdateTimer = seconds()
            
            # transmissions
            if seconds() - transmissionUpdateTimer > transmissionUpdateInterval and meshData['data'] != None:
                saveTransmissionDataToDb(nodeIds[meshData['nid']], nodeTransmissionTotal[meshData['nid']])
                saveTransmissionDataToDb(nodeIds[meshData['nid']], nodeTransmissionTotal[meshData['nid']])

                transmissionUpdateTimer = seconds()

        except KeyboardInterrupt:
            print("[INFO] exiting...")
            radio.powerDown()
            sys.exit()

if __name__ == '__main__':
    main()
