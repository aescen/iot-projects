// On ESP8266:
// At 80MHz runs up 57600bps, and at 160MHz CPU frequency up to 115200bps with only negligible errors.
// Connect pin 12 to 14.

#include <SoftwareSerial.h>
#include <ArduinoJson.h>

#if defined(ESP8266) && !defined(D5)
#define D5 (14)
#define D6 (12)
#define D7 (13)
#define D8 (15)
#endif

#define BAUD_RATE 115200

// Reminder: the buffer size optimizations here, in particular the isrBufSize that only accommodates
// a single 8N1 word, are on the basis that any char written to the loopback SoftwareSerial adapter gets read
// before another write is performed. Block writes with a size greater than 1 would usually fail.
SoftwareSerial SerialHC05;
SoftwareSerial SerialATmega32;

void serialTest() {
  //--receive from bluetooth
  if (SerialHC05.available() > 0) {
    Serial.print("From Bluetooth:");
    while (SerialHC05.available() > 0) {
      const char c = SerialHC05.read();
      Serial.write(c);
      SerialATmega32.write(c);
      yield();
    }
  }
  //--send to bluetooth & ATmega32
  if (Serial.available() > 0) {
    Serial.print("To Bluetooth & ATmega32:");
    SerialHC05.print("From NodeMCU:");
    while (Serial.available() > 0) {
      const char c = Serial.read();
      Serial.write(c);
      SerialHC05.write(c);
      SerialATmega32.write(c);
      yield();
    }
    Serial.println("");
    SerialHC05.println("");
    SerialATmega32.println("");

  }

  //--receive from atmega32
  if (SerialATmega32.available() > 0) {
    Serial.print("From ATmega32:");
    SerialHC05.print("From ATmega32:");
    while (SerialATmega32.available() > 0) {
      const char c = SerialATmega32.read();
      Serial.write(c);
      SerialHC05.write(c);
      yield();
    }
  }
}

void setup() {
  Serial.begin(115200);
  SerialHC05.begin(BAUD_RATE, SWSERIAL_8N1, D5, D6, false, 256);
  SerialATmega32.begin(BAUD_RATE, SWSERIAL_8N1, D2, D1, false, 256);
  //SerialHC05.print("{sSuhu:23,sPid:768,sErr:2.4,sSudut:48,sTime:1645345134,dataPID:{sSp:48.756080,sKp:2.302038,sKi:11.1231,sKd:4.2345}}");
}

void loop() {

  //-- Receive from ATmega32
  while (SerialATmega32.available() > 0) {
    
    //    Serial.print("From ATmega32:");
    //    while (SerialATmega32.available() > 0) {
    //      const char c = SerialATmega32.read();
    //      Serial.write(c);
    //      yield();
    //    }
    //    Serial.println("");
    
    DynamicJsonDocument doc32(256);
    DeserializationError error = deserializeJson(doc32, SerialATmega32);
    if (error) {
      //      Serial.print(F("deserializeJson() failed: "));
      //      Serial.println(error.f_str());
      return;
    } else {
      doc32.shrinkToFit();
      serializeJson(doc32, SerialHC05);
      Serial.print("From ATmega32:");
      serializeJson(doc32, Serial);
      Serial.println("");
      break;
    }
    yield();
  }

  //-- Send to Bluetooth
  while (Serial.available() > 0) {
    DynamicJsonDocument docNode(256);
    DeserializationError error = deserializeJson(docNode, Serial);
    if (error) {
      //      Serial.print(F("deserializeJson() failed: "));
      //      Serial.println(error.f_str());
      return;
    } else {
      docNode.shrinkToFit();
      serializeJson(docNode, SerialHC05);
      Serial.print("NodeMCU:");
      serializeJson(docNode, Serial);
      Serial.println("");
      break;
    }
    yield();
  }
  delay(1);
  yield();
}
