#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "TDS.h"

const char* ssid PROGMEM = "*";
const char* password PROGMEM = "*";
const char* serverUrl PROGMEM = "http://192.168.1.5/pantausungai/api/index.php?";
const char* updateKekeruhanGetUri PROGMEM = "valTurbidity=";

/* Wiring:
  terminal 5V -> 5V arduino
  terminal output ->  A0 arduino
  terminal GND -> GND arduino
*/
const byte tdsPin = A0;
const float vRef = 3.3;

TDS tds(tdsPin, vRef);
float kekeruhan = -1;
bool tmp1 = false;
const uint16_t updateDelay = 1000;
uint32_t updateTimer = millis();

void WiFiReconnect() {
  WiFi.disconnect();
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
  }
}

void WiFiSetup() {
  WiFi.disconnect();
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");
  Serial.print(F("Connecting "));
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    digitalWrite(2, 1);
    Serial.print (F("."));
    delay(250);
    digitalWrite(2, 0);
  }
  Serial.println("");
  Serial.print(F("WiFi IP Address: "));
  Serial.println(WiFi.localIP());
}

void preheatPinADC(byte pin, uint8_t times = 8);
void preheatPinADC(byte pin, uint8_t times) {
  for (int i = 0; i < times; i++) analogRead(pin);
}

void updateDb() {
  WiFiClient client;
  HTTPClient http;
  const String updateKekeruhan = (String)serverUrl + (String)updateKekeruhanGetUri + (String)kekeruhan;
  http.begin(client, updateKekeruhan);
  int httpCode = http.GET();
  if (httpCode > 0) {
    Serial.print(F("[HTTP] GET code: "));
    Serial.println(httpCode);
    String payload = http.getString();
    Serial.print(F("[HTTP] Response: "));
    Serial.println(payload);
  } else {
    Serial.print(F("[HTTP] GET failed, error code: "));
    Serial.println(http.errorToString(httpCode));
  }
  http.end();
}

void setup() {
  // preheat adc to stabilize reading
  preheatPinADC(tdsPin);
  pinMode(2, OUTPUT);
  Serial.begin(115200);
  WiFiSetup();
}

void loop() {
  tds.update();
  if (WiFi.status() == WL_CONNECTED) {
    if ((millis() - updateTimer) > updateDelay) {
      float newKekeruhan = tds.getTdsPercent();
      /*
        Serial.println(tds.getTdsAdc());
        Serial.println(tds.getTdsVolt());
        Serial.println(tds.getTdsPercent());
      */
      if (newKekeruhan != kekeruhan) {
        kekeruhan = newKekeruhan;
        updateDb();
      }

      tmp1 = false;
      updateTimer = millis();
    }
  } else {
    if (!tmp1) {
      Serial.println(F("WiFi Disconnected"));
      tmp1 = true;
      delay(500);
      WiFiReconnect();
    }
  }

  delay(10);
}
