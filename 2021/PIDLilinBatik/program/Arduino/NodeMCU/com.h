#include "utils.h"

uint32_t testTime;
const float testDataSuhu[] PROGMEM = {8,85,22,55,17,78,22,40,42,43,7,10,19,27,53,3,29,32};
uint8_t iterDataSuhu;
void testJson() {
  tick();
  if ((millis() - testTime) >= 2500) {
    //const String jsonTest = "{\"T\":" + String(((float)random(1500, 7200)) / 100, 2)  + ",\"PID\":" + String(((float)random(-102300, 102300)) / 100, 2) + ",\"E\":" + String(((float)random(150, 720)) / 100, 2) + ",\"α\":" + String(random(0, 180)) + ",\"C\":\"" + getTimeLocal() + "\",\"data\":{\"SP\":48.756080,\"KP\":2.302038,\"KI\":11.1231,\"KD\":4.2345}}";
    const String jsonTest = "{\"T\":" + String(testDataSuhu[iterDataSuhu])  + ",\"PID\":" + String(((float)random(-102300, 102300)) / 100, 2) + ",\"E\":" + String(((float)random(150, 720)) / 100, 2) + ",\"α\":" + String(random(0, 180)) + ",\"C\":\"" + getTimeLocal() + "\",\"data\":{\"SP\":48.756080,\"KP\":2.302038,\"KI\":11.1231,\"KD\":4.2345}}";
    iterDataSuhu = (iterDataSuhu < sizeof(testDataSuhu)) ? (iterDataSuhu + 1) : 0;
    testTime = millis();
    DeserializationError error = deserializeJson(globalDoc, jsonTest);
    if (error) return;
    Serial.print("Test json:");
    serializeJson(globalDoc, Serial);
    Serial.println("");
  }
}

void comsUpdate() {
  //-- Receive from ATmega32
  while (SerialATmega32.available() > 0) {
    DeserializationError error = deserializeJson(globalDoc, SerialATmega32);
    if (error) {
      return;
    } else {
      serializeJson(globalDoc, SerialHC05);
      Serial.print("From ATmega32:");
      serializeJson(globalDoc, Serial);
      Serial.println("");
      break;
    }
    yield();
  }

  //-- Send to Bluetooth
  while (Serial.available() > 0) {
    DeserializationError error = deserializeJson(globalDoc, Serial);
    if (error) {
      return;
    } else {
      serializeJson(globalDoc, SerialHC05);
      Serial.print("NodeMCU:");
      serializeJson(globalDoc, Serial);
      Serial.println("");
      break;
    }
    yield();
  }
  delayMicroseconds(10);
  yield();
}
