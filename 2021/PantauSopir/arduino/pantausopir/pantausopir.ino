#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid PROGMEM = "*";
const char* password PROGMEM = "*";
const char* serverUrl PROGMEM = "http://192.168.1.5/pantausopir/api/index.php?";
const char* updateBpmGetUri PROGMEM = "valBpm=";
const char* updateOxyGetUri PROGMEM = "valOxy=";
const char* updateIsCapturePictureGetUri PROGMEM = "valIsCapturePicture=";
const char* updateNodeIdGetUri PROGMEM = "nodeId=";

const uint16_t nodeId = 0;
float valBpm = -1;
float valOxy = -1;
float valIsCapturePicture = -1;
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
  const String updateData = (String)serverUrl + (String)updateBpmGetUri + (String)valBpm +
                            "&" + (String)updateOxyGetUri + (String)valOxy +
                            "&" + (String)updateIsCapturePictureGetUri + (String)valIsCapturePicture +
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
  float newValBpm = random(44, 78);
  float newValOxy = random(90, 99);
  float newValIsCapturePicture = random(0, 2);
  if (WiFi.status() == WL_CONNECTED) {
    if ((millis() - updateTimer) > updateDelay) {
      if (newValBpm != valBpm || newValOxy != valOxy || newValIsCapturePicture != valIsCapturePicture) {
        valBpm = newValBpm;
        valOxy = newValOxy;
        valIsCapturePicture = newValIsCapturePicture;
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
