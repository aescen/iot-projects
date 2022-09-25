#include <math.h>
#include <SoftwareSerial.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <TimeLib.h>
#include "FirebaseESP8266.h"
#include <ESP8266WiFi.h>

#define FIREBASE_HOST "..." //project database url
#define FIREBASE_AUTH "..." //database secret
#define WIFI_SSID "..."
#define WIFI_PASSWORD "..."

#define POWERWINDOW "powerwindow"
#define KIPAS "kipas"
#define POMPA "pompa"
#define ONE_WIRE_BUS 14
#define pinRelayPowerWindow D2 //16 // powerwindow
#define pinRelayKipas D3 //0
#define pinRelayPompa D8 //5
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
float Celcius = 0.0;
float Fahrenheit = 0.0;
float Soil = 0.0;
unsigned long timer = millis();
FirebaseData firebaseData;

#define CelciusPath "/jtd/PengeringPadi/data/Suhu_C"
#define FahrenheitPath "/jtd/PengeringPadi/data/Suhu_F"
#define soilPath "/jtd/PengeringPadi/data/Soil"
#define relayPowerWindowPath "/jtd/PengeringPadi/data/RelayPowerWindow"
#define relayKipasPath "/jtd/PengeringPadi/data/RelayKipas"
#define relayPompaPath "/jtd/PengeringPadi/data/RelayPompa"

int getRelayFB(String modes) {
  String packet = "";
  if (modes == "powerwindow") {
    packet = ( Firebase.getInt(firebaseData, (String)relayPowerWindowPath) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  } else if (modes == "kipas") {
    packet = ( Firebase.getInt(firebaseData, (String)relayKipasPath) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  } else if (modes = "pompa") {
    packet = ( Firebase.getInt(firebaseData, (String)relayPompaPath) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  } else {
    Serial.println(F("Unknown mode,"));
    Serial.print(modes);
    Serial.println("");
    return -1;
  }
  int relay = (firebaseData.intData() == 1) ? 1 : 0;
  return relay;
}

void SendFB(float C, float F, float S) {
  String packet = "";
  packet = ( Firebase.setFloat(firebaseData, (String)CelciusPath, C) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  packet = ( Firebase.setFloat(firebaseData, (String)FahrenheitPath, F) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  packet = ( Firebase.setFloat(firebaseData, (String)soilPath, S) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
}

float getADC(int aDCpin, int avgCount = 10) {
  burn8Readings(A0);
  float aDCAvg = 0;
  for (int i = 0; i < avgCount; i++) {
    aDCAvg = aDCAvg + analogRead(aDCpin);
    delay(1);
  }
  aDCAvg = aDCAvg / avgCount;
  return aDCAvg;
}

void burn8Readings(int pin) {
  for (int i = 0; i < 8; i++) {
    analogRead(pin);
  }
}

void setup(void) {
  //relay
  pinMode(pinRelayPowerWindow, OUTPUT);
  pinMode(pinRelayKipas, OUTPUT);
  pinMode(pinRelayPompa, OUTPUT);

  Serial.begin(115200);
  Serial.setDebugOutput(true);

  sensors.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);                                     //try to connect with wifi
  Serial.print(F("Connecting to "));
  Serial.print(WIFI_SSID);
  Serial.println(F(""));
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(F("."));
    delay(500);
  }
  Serial.println();
  Serial.print(F("Connected to "));
  Serial.println(WIFI_SSID);
  Serial.print(F("IP Address is : "));
  Serial.println(WiFi.localIP());                                            //print local IP address

  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
  //Set database read timeout to 1 minute (max 15 minutes)
  Firebase.setReadTimeout(firebaseData, 1000 * 60);
  //tiny, small, medium, large and unlimited.
  //Size and its write timeout e.g. tiny (1s), small (10s), medium (30s) and large (60s).
  Firebase.setwriteSizeLimit(firebaseData, "tiny");
}

void loop(void) {
  sensors.requestTemperatures();
  float nC = sensors.getTempCByIndex(0) + 1.6;
  float nF = sensors.toFahrenheit(nC);
  float nS = getADC(A0);
  nC = roundf(nC * 1000) / 1000;
  nF = roundf(nF * 1000) / 1000;
  nS = roundf(nS * 1000) / 1000;
  float nSN = map(nS, 0.0, 1024.0, 100.0, 0.0) + 14;
  if (nSN > 100) nSN = 100.0;

  String s = "";
  if (getRelayFB(POWERWINDOW) == 1) {
    digitalWrite(pinRelayPowerWindow, LOW);
    s += " - PowerWindow: ON";
  } else if (getRelayFB(POWERWINDOW) == 0) {
    digitalWrite(pinRelayPowerWindow, HIGH);
    s += " - PowerWindow: OFF";
  } else {
    s += " - PowerWindow: null";
  }

  if (getRelayFB(KIPAS) == 1) {
    digitalWrite(pinRelayKipas, LOW);
    s += " - Kipas: ON";
  } else if (getRelayFB(KIPAS) == 0) {
    digitalWrite(pinRelayKipas, HIGH);
    s += " - Kipas: OFF";
  } else {
    s += " - Kipas: null";
  }

  if (getRelayFB(POMPA) == 1) {
    digitalWrite(pinRelayPompa, LOW);
    s += " - Pompa: ON";
  } else if (getRelayFB(POMPA) == 0) {
    digitalWrite(pinRelayPompa, HIGH);
    s += " - Pompa: OFF";
  } else {
    s += " - Pompa: null";
  }

  if (millis() - timer >= 1000) {
    if ( nC != Celcius || nF != Fahrenheit || nSN != Soil ) {
      SendFB(nC, nF, nSN);
      Celcius = nC;
      Fahrenheit = nF;
      Soil = nS;
    }
    Serial.print(F(" C: "));
    Serial.print(Celcius);
    Serial.print(F(" F: "));
    Serial.print(Fahrenheit);
    Serial.print(F(" Soil: "));
    Serial.print(Soil);
    Serial.print(F(" ("));
    Serial.print(nSN);
    Serial.print(F("%)"));
    Serial.println(s);
  }

  delay(100);
}
