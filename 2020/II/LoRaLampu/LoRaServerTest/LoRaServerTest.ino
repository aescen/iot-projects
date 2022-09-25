#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>

byte localAddress = 0x01;
byte senderAddress = 0xF0; // Gate

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println(F("LoRa Server"));
  Serial.print(F("Server address: 0x"));
  Serial.println(localAddress, HEX);
  Serial.print(F("Gateway address: 0x"));
  Serial.println(senderAddress, HEX);

  LoRa.setTxPower(17, PA_OUTPUT_PA_BOOST_PIN);
  LoRa.setSignalBandwidth(250E3);
  LoRa.setCodingRate4(8);
  LoRa.setSpreadingFactor(12);
  LoRa.enableCrc();
  LoRa.setPreambleLength(8);
  LoRa.setSyncWord('0x12');
  if (!LoRa.begin(467.5E6)) {
    Serial.println(F("Starting LoRa failed!"));
    while (1);
  }
  delay(1);
}

void loop() {
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // read packet
    String packet;
    while (LoRa.available()) {
      packet += (char)LoRa.read();
    }
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, packet);
    if (error) {
      Serial.println(F("Error parsing JSON."));
      return;
    }
    doc.shrinkToFit(); //reduces the capacity of the memory pool to match the current usage
    uint8_t origin = doc["o"];
    uint8_t gate = doc["g"];
    uint8_t dest = doc["d"];
    String message = doc["m"];

    // if the recipient isn't this device or designated gate,
    if (dest != localAddress && gate != senderAddress) {
      Serial.println(F("This message is not for me."));
      return;                             // skip rest of function
    } else {
      // Parse message json
      //char json[] = "{\"servo\":0,\"relay\":0,\"ph\":302.1,\"moist\":990.4,\"type\":1}";
      Serial.println("Received from: 0x" + String(gate, HEX));
      Serial.println("Sent to: 0x" + String(dest, HEX));
      Serial.println("Originated from: 0x" + String(origin, HEX));
      Serial.println(packet);
      doc.clear();
      error = deserializeJson(doc, message);
      if (error) {
        Serial.println(F("Error parsing JSON message."));
        return;
      }
      long rtcTime = doc["t"];
      float current = doc["i"];
      float voltage = doc["v"];
    }
  }
}
