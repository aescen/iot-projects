# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 19:16:12 2019

@author: ricoen & avryan
"""

#import library dan inisialisasi
import pandas as pd
import numpy as np
import pymysql, sys, time
from sklearn import preprocessing
import serial

print("Connecting ...")
try:
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='hujanasam',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
except pymysql.err.Error as msg:
    print("Connection error: ", msg)
    exit()
## Create cursor
cc = connection.cursor()

#pendefinisian data input dari serial arduino
#ser = serial.Serial('/dev/ttyACM0')

while True:
    try:
        s = ser.readline()
        s1 = s.split() #parsing data serial
        a_test = float(s1[0])
        b_test = int(s1[1])
        data_pH = float(s1[0])
        data_karbon = int(s1[1])
        '''a_test = 1.7
        b_test = 12
        data_pH = 7.2
        data_karbon = 200'''
        
        #import data
        data = pd.read_csv('data_train.csv')
        data.head()

        #cek data
        #print (data)

        #sorting data
        pH = data.iloc[0:280,1]
        co2 = data.iloc[0:280,2]
        hujan = data.iloc[0:280,3]

        #labelEncoder
        le = preprocessing.LabelEncoder()

        #konvert string dari data ke integer
        hujan_encode = le.fit_transform(hujan)

        #kombinasi data pH dan CO2
        kondisi = list(zip(pH, co2))

        #konvert label hujan ke array
        hujan = np.array(hujan_encode)
        kondisi = np.array(kondisi)

        #Variable baru untuk data latih
        X_train = (kondisi)
        y_train = (hujan)

        #algoritma machine learning
        from sklearn.naive_bayes import GaussianNB
        clf = GaussianNB()

        #pengklasifikasian data latih (X, y train)
        clf.fit(X_train,y_train)

        #membuat prediksi dan menghitung nilai probabilistik
        y_test = clf.predict([[a_test, b_test]])
        prob = clf.predict_proba([[a_test, b_test]])
        #nilai akurasi dataset
        akurasi = clf.score(X_train,y_train)*100

        if y_test == 1:
            prediksi = 'normal'
        else:
            prediksi = 'asam'

        #tampilkan variabel pH (a) dan CO2 (b) pada data uji (X_test)
        print ('nilai pH: {}'.format(data_pH))
        print ('nilai pH: {}'.format(data_karbon))
        print ('Hasil prediksi GNB: hujan {}'.format(prediksi))
        print ('Nilai probabilistik GNB nilai kondisi (pH dan CO2) terhadap terjadinya hujan asam: {}'.format(prob))
        print ('Nilai akurasi GNB dengan panjang dataset 280 data: {:.5}%'.format(akurasi))
        try:
            result = """
                     UPDATE `prediksi`
                      SET
                       `ph`='{0}',
                       `co2` = '{1}',
                       `hasilprediksiGNB`='{2}',
                       `nilaiprobabilistikGNBPH`='{3}',
                       `nilaiprobabilistikGNBCO2`='{4}',
                       `nilaiakurasi`='{5}'
                      WHERE
                       `prediksi`.`id` = 1;
                     """.format(data_pH, data_karbon, prediksi, float(prob[:,0]), float(prob[:,1]), akurasi)
            cc.execute(result)
            connection.commit()
        except pymysql.err.InternalError as msg:
            print("Command skipped: ", msg)
        time.sleep(5)

    except KeyboardInterrupt:
        connection.close()
        sys.exit()