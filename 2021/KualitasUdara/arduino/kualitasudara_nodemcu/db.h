#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

//const String SERVER_IP = "192.168.43.252"; /* PC */
const String& SERVER_IP = "192.168.1.1"; /* RPi */
const String LOAD_DATA_URI = "http://" + SERVER_IP + "/kualitasudara/io/index.php/loaddata/";
const String UPDATE_DATA_URI = "http://" + SERVER_IP + "/kualitasudara/io/index.php/updatedata";

StaticJsonDocument<512> globalDoc;
uint16_t loadDataInterval = 2000;
uint32_t tLoadDb = millis();
uint16_t updateDataInterval = 2000;
uint32_t tUpdateDb = millis();

bool loadData(String payload) {
  WiFiClient client;
  HTTPClient http;
  if ((WiFi.status() == WL_CONNECTED)) {
    //    Serial.print("[HTTP] begin...\n");
    http.begin(client, LOAD_DATA_URI + payload);
    http.addHeader("Access-Control-Allow-Origin", "*");

    //    Serial.print("[HTTP] GET...\n");
    //    Serial.println(LOAD_DATA_URI + payload);
    // start connection and send HTTP header and body
    int httpCode = http.GET();

    // httpCode will be negative on error
    if (httpCode > 0) {
      // HTTP header has been send and Server response header has been handled
      //      Serial.printf("[HTTP] GET... code: %d\n", httpCode);

      // file found at server
      if (httpCode == HTTP_CODE_OK) {
        payload = http.getString();
        payload = payload.substring(payload.indexOf('[') + 1, payload.indexOf(']'));
        //        Serial.println("received payload:\n<<");
        //        Serial.println(payload);
        //        Serial.println(">>");
        DeserializationError error = deserializeJson(globalDoc, payload);
        if (error) {
          Serial.printf("[HTTP] GET... failed, error: json deserialization error\n");
          http.end();
          return false;
        }
        //        Serial.print("Load data json:");
        //        serializeJson(globalDoc, Serial);
        http.end();
        return true;
      }
    } else {
      Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
  }
  http.end();
  return false;
}

bool updateData(String payload) {
  WiFiClient client;
  HTTPClient http;
  if ((WiFi.status() == WL_CONNECTED)) {
    //    Serial.print("[HTTP] begin...\n");
    http.begin(client, UPDATE_DATA_URI); //HTTP
    http.addHeader("Content-Type", "application/json; charset=utf-8");
    http.addHeader("Access-Control-Allow-Origin", "*");

    //    Serial.print("[HTTP] POST...\n");
    //    Serial.println(UPDATE_DATA_URI);
    // start connection and send HTTP header and body
    int httpCode = http.POST(payload);

    // httpCode will be negative on error
    if (httpCode > 0) {
      // HTTP header has been send and Server response header has been handled
      //      Serial.printf("[HTTP] POST... code: %d\n", httpCode);

      // file found at server
      if (httpCode == HTTP_CODE_OK) {
        payload = http.getString();
        //        Serial.println("received payload:\n<<");
        //        Serial.println(payload);
        //        Serial.println(">>");
        DeserializationError error = deserializeJson(globalDoc, payload);
        if (error) {
          Serial.printf("[HTTP] POST... failed, error: json deserialization error\n");
          http.end();
          return false;
        }
        //        Serial.print("Update data json:");
        //        serializeJson(globalDoc, Serial);
        bool ok = (bool) globalDoc["update"];
        if (ok) {
          http.end();
          return true;
        }
      }
    } else {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
  }
  http.end();
  return false;
}

void checkDatabase(uint16_t valId = 1);
void checkDatabase(uint16_t valId) {
  if ( millis() - tLoadDb >= loadDataInterval  ) {

    bool ok = loadData("?id=" + (String)valId);
    if (ok) {
      valSensorCO = (float) globalDoc["ppm1"];
      valSensorCO2 = (float) globalDoc["ppm2"];
      valSensorCO3 = (float) globalDoc["ppm3"];
      valSensorDusts = (float) globalDoc["dust"];
      valVisitors = (int) globalDoc["jumlah"];
    }

    tLoadDb = millis();
  }
  yield();
}

void updateDatabase(uint16_t valId = 1);
void updateDatabase(uint16_t valId) {
  if ( millis() - tUpdateDb >= updateDataInterval  ) {
    globalDoc["id"] = valId;
    globalDoc["ppm1"] = valSensorCO;
    globalDoc["ppm2"] = valSensorCO2;
    globalDoc["ppm3"] = valSensorCO3;
    globalDoc["dust"] = valSensorDusts;
    globalDoc["jumlah"] = valVisitors;
    String payload;
    serializeJson(globalDoc, payload);
    updateData(payload);

    tUpdateDb = millis();
  }
  yield();
}
