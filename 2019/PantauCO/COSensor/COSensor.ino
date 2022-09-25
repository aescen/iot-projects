#include <ESP8266WiFi.h>
#include <WiFiClient.h>

#include <TimeLib.h>
#include <DMD2.h>
#include <fonts/Font3x5.h>
#include <fonts/angka6x13.h>

#include <FirebaseArduino.h>
#include <ArduinoJson.h>

// Set these to run example.
#define FIREBASE_HOST "xxx.firebaseio.com"
#define FIREBASE_AUTH "xxx"

#ifndef STSSID
#define STSSID "xxx"  //Nama SSID (edit)
#define STPSK  "xxx" //Password SSID (edit)
#endif

//MQ7 coefs
/*
  The coefficients are estimated from the sensitivity characteristics graph
  of the MQ7 sensor for CO (Carbon Monoxide) gas by using Correlation function.

  Explanation :
  The graph in the datasheet is represented with the function
  f(x) = a * (x ^ b).
  where
    f(x) = ppm
    x = Rs/R0
  The values were mapped with this function to determine the coefficients a and b.
*/
#define coefficient_A 19.32
#define coefficient_B -0.64

//Load resistance 10 Kohms on the sensor output
#define R_Load 9.9 //use ohmmeter!

//SETUP DMD
SPIDMD dmd(1, 1); // Jumlah Panel P10 yang digunakan (KOLOM,BARIS)
DMD_TextBox box(dmd);  // "box" provides a text box to automatically write to/scroll the display

//SETUP WIFI STATION/CLIENT
/* Set these to your desired credentials. */
const char *ssidST = STSSID;
const char *passST = STPSK;

//Vars
unsigned long tHeat, tFb, tTampil;
int tampil;
bool heated = false;
const char nodeID = 'A';      //ID node
const int pinSensor1 = 5; //D1
const int pinSensor2 = 4; //D2
const int pinKipas1 = 2; //D4
//const int s5Volt = xxx; //xxx
//const int s1_4Volt = xxx; //xxx
//bool 5v = true;
int valKipas1 = -1;
int valSensor1, valSensor2, newValSensor1, newValSensor2, newValKipas1;
float valSensorAnalog, newValSensorAnalog;
const String coSensor1 = "sensors/coSensor1"; //alamat firebase, sensor 1
const String coSensor2 = "sensors/coSensor2"; //alamat firebase, sensor 2
const String coPPM = "sensors/coPPM"; //alamat firebase, PPM
const String relayKipas1 = "relays/relayKipas1";  //alamat firebase, kipas

void setup() {
  Serial.begin(230400); //aktifkan serial pada baud rate 230400
  Serial.print("Node:"); Serial.print(nodeID); Serial.println(" - CO sensor init.");

  pinMode(pinSensor1, INPUT); //mq7
  pinMode(pinSensor2, INPUT); //mq7
  pinMode(pinKipas1, OUTPUT); //kipas
  digitalWrite(pinKipas1, HIGH);//OFF

  /* WiFi Client setup */
  Serial.print("Connecting to ");
  Serial.println(ssidST);
  WiFi.mode(WIFI_STA); // set mode wifi ke station (sebagai client)
  WiFi.begin(ssidST, passST); // aktifkan koneksi wifi ke SSID yg telah didefinisikan
  while (WiFi.status() != WL_CONNECTED) { // menunggu koneksi WiFi terhubung
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected: ");
  Serial.println(WiFi.localIP()); // tampilkan IP WiFi yg didapatkan dari Hotspot

  /* Firebase setup */
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH); // aktifkan koneksi firebase menggunakan alamat host database beserta kode otentifikasinya

  valSensor1 = digitalRead(pinSensor1); // nilai awal pembacaan sensor pada pin D4
  valSensor2 = digitalRead(pinSensor2); // nilai awal pembacaan sensor pada pin D5
  valKipas1 = -1;
  Firebase.setInt(coSensor1, valSensor1); // tulis data pembacaan co sensor 1 ke firebase
  Serial.print(nodeID); Serial.print(F(":CO Sensor 1:")); Serial.println(valSensor1);
  if (Firebase.failed()) { // apabila penulisan ke firebase gagal tampilkan error ke serial
    Serial.print("Setting /"); Serial.print(coSensor1); Serial.print(" failed:");
    Serial.println(Firebase.error());
    return;
  }
  Firebase.setInt(coSensor2, valSensor2);// tulis data pembacaan co sensor 2 ke firebase
  Serial.print(nodeID); Serial.print(F(":CO Sensor 2:")); Serial.println(valSensor2);
  if (Firebase.failed()) { // apabila penulisan ke firebase gagal tampilkan error ke serial
    Serial.print("Setting /"); Serial.print(coSensor2); Serial.print(" failed:");
    Serial.println(Firebase.error());
    return;
  }

  //DMD
  dmd.begin(); // aktifkan driver panel P10
  // INTRO BRANDING
  dmd.clearScreen(); // hapus layar panel P10
  dmd.selectFont(Font3x5); // set jenis tulisan
  dmd.drawString(4, -1, "SENSOR", GRAPHICS_INVERSE); // tampilkan teks
  dmd.drawString(11, 7, "CO", GRAPHICS_INVERSE); // tampilkan teks
  delay(2000);
}

// the loop function runs over and over again forever
void loop() {
  if ( millis() - tHeat >= 60000  ) { // tunggu 60 detik sebelum pembacaan ulang nilai PPM sensor co
    newValSensorAnalog = avgReading(A0, 10); // baca data analog 10x dan rata-rata nilainya, tiap pembacaan terdapat delay 100ms sehingga 10 berarti 1s
    Serial.print("Analog0:"); Serial.print(newValSensorAnalog); Serial.print("[]PPM:"); Serial.print(raw2ppm(newValSensorAnalog));
    Serial.print("[]Digital1:"); Serial.print(newValSensor1); Serial.print("[]Digital2:"); Serial.println(newValSensor2);
    if ( valSensorAnalog != newValSensorAnalog ) {// cek perubahan data PPM sensor co. bila ada perubahan maka update data firebase
      Firebase.setInt(coPPM, (int)raw2ppm(newValSensorAnalog)); // tulis data PPM ke firebase
      Serial.print(nodeID); Serial.print(":"); Serial.print(coPPM); Serial.print(":"); Serial.println(raw2ppm(newValSensorAnalog));
      if (Firebase.failed()) { // tampilkan error bila terjadi kesalahan
        Serial.print("Setting /"); Serial.print(coPPM); Serial.print(" failed:");
        Serial.println(Firebase.error());
        return;
      }
      valSensorAnalog = newValSensorAnalog; // sinkronkan variabel data sensor PPM
    }
    tHeat = millis();
  }

  if ( millis() - tFb >= 1000  ) // lakukan pengecekan data sensor co tiap 1s bila perlu update data firebase
  {
    //cek beda nilai sensor co 1, bila ada maka update firebase
	newValSensor1 = digitalRead(pinSensor1); //nilai sensor 1 pada pin D1; 1 baik; 0 buruk
    if ( valSensor1 != newValSensor1 ) {
      Firebase.setInt(coSensor1, newValSensor1); // tulis data sensor co ke firebase
      Serial.print(nodeID); Serial.print(":"); Serial.print(coSensor1); Serial.print(":"); Serial.println(newValSensor1);
      if (Firebase.failed()) { // tampilkan error bila terjadi kesalahan
        Serial.print("Setting /"); Serial.print(coSensor1); Serial.print(" failed:");
        Serial.println(Firebase.error());
        return;
      }
      valSensor1 = newValSensor1; // sinkronkan variabel data sensor 1
    }
	//cek beda nilai sensor co 1, bila ada maka update firebase
	newValSensor2 = digitalRead(pinSensor2); //nilai sensor 2 pada pin D2
    if (valSensor2 != newValSensor2 ) {
      Firebase.setInt(coSensor2, newValSensor2); // tulis data sensor co ke firebase
      Serial.print(nodeID); Serial.print(":"); Serial.print(coSensor2); Serial.print(":"); Serial.println(newValSensor2);
      if (Firebase.failed()) { // tampilkan error bila terjadi kesalahan
        Serial.print("Setting /"); Serial.print(coSensor2); Serial.print(" failed:");
        Serial.println(Firebase.error());
        return;
      }
      valSensor2 = newValSensor2; // sinkronkan variabel data sensor 2
    }

    if ( valSensor1 == 0 || valSensor2 == 0) { // cek bila terdapat sensor dalam keadaan buruk
      newValKipas1 = 1; // atur kipas ke mode on
    }
    else if ( valSensor1 == 1 && valSensor2 == 1 ) { // cek bila sensor dalam keadaan baik semua
      newValKipas1 = 0; // atur kipas ke mode off
    }
    tFb = millis();
  }

  if ( valKipas1 != newValKipas1 ) { // cek perubahan data kipas
    if (newValKipas1) {// bila kipas mode on maka aktifkan relay
      digitalWrite(pinKipas1, LOW);
      valKipas1 = newValKipas1;
      Serial.println("KIPAS:" + onoff(valKipas1));
    }
    else if (!newValKipas1) {// bila kipas mode off maka matikan relay
      digitalWrite(pinKipas1, HIGH);
      valKipas1 = newValKipas1;
      Serial.println("KIPAS:" + onoff(valKipas1));
    }
	Firebase.setInt(relayKipas1, valKipas1); // tulis data sensor co ke firebase
	Serial.print(nodeID); Serial.print(":"); Serial.print(relayKipas1); Serial.print(":"); Serial.println(valKipas1);
	if (Firebase.failed()) { // tampilkan error bila terjadi kesalahan
	  Serial.print("Setting /"); Serial.print(relayKipas1); Serial.print(" failed:");
	  Serial.println(Firebase.error());
	  return;
	}
  }
  //Tampil info pada panel P10
  if ( millis() - tTampil >= 3000  ) { // ubah tampilan panel P10 tiap 3s
    switch (tampil) {
      case 0: { // tampilkan info sensor co 1
          String co1[2] = {"CO 1:", bb(valSensor1)};
          Serial.println("Tampil: " + co1[0] + co1[1]);
          tampilInfo(co1);
          tampil = 1; // set tampil info selanjutnya ke sensor 1
        }
        break;
      case 1: { // tampilkan info sensor co 2
          String co2[2] = {"CO 2:", bb(valSensor2)};
          Serial.println("Tampil: " + co2[0] + co2[1]);
          tampilInfo(co2);
          if (int(valSensorAnalog) != -1) { // akan menampilkan info kadar PPM bila kadar PPM telah didapatkan
            tampil = 2; // set tampil info selanjutnya ke info kadar PPM
          } else { // akan menampilkan info kipas langsung bila kadar PPM belum didapatkan
            tampil = 3; // set tampil info selanjutnya ke kipas
          }
        }
        break;
      case 2: { // tampilkan info kadar PPM
          String analog = String((int)raw2ppm(valSensorAnalog)) + "PPM";
          String coA0[2] = {"KADAR:", analog};
          Serial.println("Tampil: " + coA0[0] + coA0[1]);
          tampilInfo(coA0);
          tampil = 3; // set tampil info selanjutnya ke kadar PPM
        }
        break;
      case 3: { // tampilkan info mode kipas
          String kipas[2] = {"KIPAS:", onoff(valKipas1)};
          Serial.println("Tampil: " + kipas[0] + kipas[1]);
          tampilInfo(kipas);
          tampil = 0; // set tampil info selanjutnya ke sensor 1
        }
        break;
    }
    tTampil = millis(); // update counter waktu untuk tampilan info
  }
}

/* Functions */
//tampil info
void tampilInfo(String inf[2]) {
  int pos[2] = {inf[0].length(), inf[2].length()};
  dmd.selectFont(Font3x5);
  dmd.clearScreen();
  dmd.drawString( 1, -1, inf[0], GRAPHICS_INVERSE);
  dmd.drawString( 1, 7, inf[1], GRAPHICS_INVERSE);
}
//ON atau OFF
String onoff(int in) {
  if (in) {
    return "ON";
  } else {
    return "OFF";
  }
}
//baik atau buruk
String bb(int in) {
  if (in) {
    return "BAIK";
  } else {
    return "BURUK";
  }
}
// rata - rata nilai analog
float avgReading(int pin, int t) {
  float avg;
  for (int i = 0; i < t; i++) {
    avg = avg + analogRead(pin);
    delay(100);
    yield();
  }
  yield();
  avg = avg / t;
  return avg;
}
//nilai analog ke PPM
float raw2ppm(float value) {
  float v_in = 5.0;
  float v_out = value * (v_in / 1023.0);
  float ratio = (v_in - v_out) / v_out;
  return (float)(coefficient_A * pow(ratio, coefficient_B));
}
