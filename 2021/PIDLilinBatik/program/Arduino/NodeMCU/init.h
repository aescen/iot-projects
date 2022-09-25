#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ArduinoJson.h>

#define LED 2

#if defined(ESP8266) && !defined(D5)
#define D5 (14)
#define D6 (12)
#define D7 (13)
#define D8 (15)
#endif

#define BAUD_RATE 57600

SoftwareSerial SerialHC05;
SoftwareSerial SerialATmega32;

//SSID and Password of your WiFi router
const char* ssid = "speedy@1fb0";
const char* password = "6610061404";
//const char* ssid = "ASHP-MARKW";
//const char* password = "123@qWe!aSd?zXc#";

DynamicJsonDocument globalDoc(256);
String valConstants;
String dataJson;

ESP8266WebServer server(80);

#include "com.h"
void comsInit() {
  Serial.begin(BAUD_RATE);
  SerialHC05.begin(BAUD_RATE, SWSERIAL_8N1, D5, D6, false, 256);
  SerialATmega32.begin(BAUD_RATE, SWSERIAL_8N1, D2, D1, false, 256);
  //{"T":23,"PID":768,"E":2.4,"α":48,"C":"00:02:43","data":{"SP":48.756080,"KP":2.302038,"KI":11.1231,"KD":4.2345}}
}

void wifiInit() {
  WiFi.begin(ssid, password);     //Connect to your WiFi router
  comsInit();
  pinMode(LED, OUTPUT);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  //If connection successful show IP address in serial monitor
  Serial.println("");
  Serial.print("Terkoneksi ke ");
  Serial.println(ssid);
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

#include "index.h"
#include "web.h"
void webServerInit() {
  server.on("/", handleRoot);
  server.on("/datas", handle_data);
  server.onNotFound(handleNotFound);
  server.begin();
}
