#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid PROGMEM = "*";
const char* password PROGMEM = "*";
const char* serverUrl PROGMEM = "http://192.168.1.5/pantaukolam/api/index.php?setTable=turbin&";
const char* updatePhAGetUri PROGMEM = "valPhA=";
const char* updateRpmGetUri PROGMEM = "valRpm=";
const char* updateDayaGetUri PROGMEM = "valDaya=";
const char* updateDebitAGetUri PROGMEM = "valDebitA=";
const char* updateDebitBGetUri PROGMEM = "valDebitB=";
const char* updateNodeIdGetUri PROGMEM = "nodeId=";

const uint16_t nodeId = 0;
float valPhA = -1;
float valRpm = -1;
float valDaya = -1;
float valDebitA = -1;
float valDebitB = -1;
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

void updateDb() {
  WiFiClient client;
  HTTPClient http;
  const String updateData = (String)serverUrl + (String)updatePhAGetUri + (String)valPhA +
                            "&" + (String)updateRpmGetUri + (String)valRpm +
                            "&" + (String)updateDayaGetUri + (String)valDaya +
                            "&" + (String)updateDebitAGetUri + (String)valDebitA +
                            "&" + (String)updateDebitBGetUri + (String)valDebitB +
                            "&" + (String)updateNodeIdGetUri + (String)nodeId;
  http.begin(client, updateData);
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
  Serial.begin(115200);
  WiFiSetup();
}

void loop() {
  float newValPhA = random(44, 78);
  float newValRpm = random(100, 1000);
  float newValDaya = random(1, 100);
  float newValDebitA = random(1, 100);
  float newValDebitB = random(1, 100);
  if (WiFi.status() == WL_CONNECTED) {
    if ((millis() - updateTimer) > updateDelay) {
      if (newValPhA != valPhA || newValRpm != valRpm || newValDaya != valDaya || newValDebitA != valDebitA || newValDebitB != valDebitB) {
        valPhA = newValPhA;
        valRpm = newValRpm;
        valDaya = newValDaya;
        valDebitA = newValDebitA;
        valDebitB = newValDebitB;
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
