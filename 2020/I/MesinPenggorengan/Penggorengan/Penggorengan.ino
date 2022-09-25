#include <ESP8266WiFi.h>
#include "FirebaseESP8266.h"
#include <SoftwareSerial.h>
SoftwareSerial data_serial(D6, D5);

#define FIREBASE_HOST "..." //project database url
#define FIREBASE_AUTH "..." //database secret  
#define WIFI_SSID "..."
#define WIFI_PASSWORD "..."
#define relayGorengFBPath "/jtd-transfer/Berlinbaru/RelayGoreng"

String dt[10];
String dataIn;
const int pinRelay = 7;
int i = 0;
String suhu1, suhu2, pressure;
FirebaseData firebaseData;

const uint32_t t_perendaman = 1000 * 60 * 20; //20m
uint32_t perendaman = millis();

const uint32_t t_goreng = 1000 * 60 * 15; //15m
uint32_t goreng = millis();

const uint32_t t_istirahat = 1000 * 60 * 5; //5m
uint32_t istirahat = millis();

const uint8_t x_goyang = 3;
uint8_t cnt = 1;
uint32_t goyang = millis();

bool mulaiProses = true;
bool mulaiRendam = true;
bool mulaiGoreng = false;
bool mulaiIstirahat = false;

bool getMulaiGorengFB() {
  String packet = "";
  packet = ( Firebase.getBool(firebaseData, (String)relayGorengFBPath) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  return firebaseData.boolData();
}

void sendFB(String suhu1, String suhu2, String pressure) {
  // set string value
  //FirebaseJsonArray arr; arr.set("/[0]", rgb[0]); arr.set("/[1]", rgb[1]); arr.set("/[2]", rgb[2]);
  String packet = "";
  packet = ( Firebase.setString(firebaseData, "Berlinbaru/Suhu1", suhu1) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  //Serial.println(packet);
  packet = ( Firebase.setString(firebaseData, "Berlinbaru/Suhu2", suhu2) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  //Serial.println(packet);
  packet = ( Firebase.setString(firebaseData, "Berlinbaru/Preessure", pressure) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  //Serial.println(packet);
  // handle error
}

void setup() {
  Serial.begin(9600);
  data_serial.begin(9600);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("connecting");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("connected: ");
  Serial.println(WiFi.localIP());
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
}

void loop() {
  dataIn = "";
  while (data_serial.available() > 0) {
    delay(15);
    char c = data_serial.read();
    dataIn = dataIn + c;
  }
  if (dataIn.length() > 2) {
    Serial.println(dataIn);
    parsingData();
  }

  processPenggorengan();

}

void processPenggorengan() {
  if (getMulaiGorengFB() && !mulaiProses) {
    mulaiProses = true;
    mulaiRendam = true;
    mulaiGoreng = false;
    mulaiIstirahat = false;
    Serial.print("Mulai proses perendaman:");
    Serial.print(millis() / 1000);
    perendaman = millis();
  }
  //} else { relayOff(relayPin); mulaiRendam = false; mulaiGoreng = false; mulaiIstirahat = false; cnt = 1; }
  if ((millis() - perendaman > t_perendaman) && mulaiProses && mulaiRendam && !mulaiGoreng && !mulaiIstirahat) {
    relayOn(relayPin);
    mulaiRendam = false;
    mulaiGoreng = true;
    Serial.print("Mulai penggorengan ke:");
    Serial.print(cnt);
    Serial.print("T");
    Serial.println(millis() / 1000);
    goreng = millis();
  }
  if ((millis() - goreng > t_goreng) && mulaiProses && !mulaiRendam && mulaiGoreng && !mulaiIstirahat) {
    relayOff(relayPin);
    mulaiGoreng = false;
    mulaiIstirahat = true;
    Serial.print("Mulai istirahat:");
    Serial.print(cnt);
    Serial.print("T");
    Serial.println(millis() / 1000);
    istirahat = millis();
  }
  if ((millis() - istirahat > t_istirahat) && mulaiProses && !mulaiRendam && !mulaiGoreng && mulaiIstirahat) {
    Serial.print("Istirahat selesai:");
    Serial.print(cnt);
    Serial.print("T");
    Serial.println(millis() / 1000);
    mulaiIstirahat = false;
    mulaiRendam = true;
    cnt++;
  }
  if (cnt == x_goyang && mulaiProses && mulaiRendam && !mulaiGoreng && !mulaiIstirahat) {
    Serial.print("-========================= ");
    Serial.print(cnt);
    Serial.println("x Penggorengan selesai =========================-");
    Serial.print("C1 : ");
    Serial.println(suhu1);
    Serial.print("C2 : ");
    Serial.println(suhu2);
    Serial.print("Pressure : ");
    Serial.println(pressure);
    Serial.println("-===================================&===================================-");
    sendFB(suhu1, suhu2, pressure);
    relayOff(relayPin);
    mulaiProses = false;
    mulaiRendam = false;
    mulaiGoreng = false;
    mulaiIstirahat = false;
    cnt = 1;
  }
}

void parsingData() {
  int j = 0;
  Serial.print("data masuk : ");
  Serial.println(dataIn);
  dt[j] = "";
  for (i = 1; i < dataIn.length(); i++) {
    if (dataIn[i] == '_') {
      j++;
      dt[j] = "";
    }
    else {
      dt[j] = dt[j] + dataIn[i];
    }
  }
  //  Serial.print("C1 : ");
  //  Serial.println(dt[0]);
  suhu1 = dt[0];
  //  Serial.print("C2 : ");
  //  Serial.println(dt[1]);
  suhu2 = dt[1];
  //  Serial.print("Pressure : ");
  //  Serial.println(dt[2]);
  pressure = dt[2];
  //  Serial.println("========================================");
  //  sendFB(suhu1, suhu2, pressure);
}

//void kirimData(String volume, String kapasitif, String ph) {
//  Firebase.setString("Device/volume", volume);
//  if (Firebase.failed()) {
//    Serial.print("setting /message failed:");
//    Serial.println(Firebase.error());
//    return;
//  }
//  Firebase.setString("Device/kapasitif", kapasitif);
//  if (Firebase.failed()) {
//    Serial.print("setting /message failed:");
//    Serial.println(Firebase.error());
//    return;
//  }
//  Firebase.setString("Device/ph", ph);
//  if (Firebase.failed()) {
//    Serial.print("setting /message failed:");
//    Serial.println(Firebase.error());
//    return;
//  }
//}
