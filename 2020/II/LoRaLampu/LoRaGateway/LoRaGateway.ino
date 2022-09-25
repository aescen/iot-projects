#include "Arduino.h"
#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#include "RTClib.h"
#include "ACS712.h"
#include <Voltmeter.h>

const byte destinationAddress = 0x01; // Server
const byte localAddress = 0xF0;
unsigned long randNumber;
unsigned long tStart = 0; //For interval
const int maxTime = 10000;//10s
const int minTime = 5000;//5s

const uint8_t PIN_HALLSENSOR = A1;
const uint8_t PIN_VOLTMETER = A0;

RTC_DS3231 rtc;
//analogPin, volts, maxADC, mVperA)
ACS712  hallsensor(PIN_HALLSENSOR, 5.0, 1023, 185);
//sensorPin, maxVoltage, readingNumber
Voltmeter voltmeter(PIN_VOLTMETER, 25, 10);

void sendPayload(byte origin, String outgoing) {
  delay(50);
  LoRa.beginPacket();
  LoRa.print(outgoing);                 // add payload
  LoRa.endPacket();                     // finish packet and send it
  LoRa.flush();
  delay(50);
}

void getRandom(long rN = 0) {
  randomSeed(random(0, 1024) + rN);
  randNumber = random(minTime, maxTime);
}

unsigned long getUtc() {
  DateTime now = rtc.now();
  return now.unixtime();
}

float truncateData(float data) {
  int temp = data * 1000;
  float temp2 = temp;
  return temp2 / 1000;
}

bool checkTimer() {
  unsigned long now = millis(); //get timer value
  if ( now - tStart >= randNumber  ) //check to see if it is time to transmit based on set interval
  {
    tStart = now; //reset start time of timer
    return true;
  }
  else return false;
}

void setup() {
  Serial.begin(115200);
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    abort();
  }
  if (rtc.lostPower()) {
    // following line sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }
  voltmeter.initialize();
  // generate a random number from 2000 to 8000
  randNumber = random(minTime, maxTime);
  while (!Serial);

  Serial.println(F("LoRa Gateway"));
  Serial.print(F("Destination address: 0x"));
  Serial.println(destinationAddress, HEX);
  Serial.print(F("Local address: 0x"));
  Serial.println(localAddress, HEX);

  if (!LoRa.begin(467.5E6)) {
    Serial.println(F("Starting LoRa failed!"));
    while (1);
  }
  delay(50);
  //  String json = "{\"o\":160,\"g\":240,\"d\":1,\"m\":{\"t\":2129459,\"i\":0.4428,\"v\":7.557981}}";
  //  sendPayload(byte("0xA0"), json);
  //  Serial.print(F("Sending:"));
  //  Serial.println(json);
}

void loop() {
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // read packet header bytes:
    int destination = LoRa.read();        // destination address
    byte recipient = LoRa.read();         // recipient address (gate)
    byte sender = LoRa.read();            // sender address (origin)
    byte incomingLength = LoRa.read();    // incoming payload length

    // read packet
    String packet;
    while (LoRa.available()) {
      packet += (char)LoRa.read();
    }

    // if the recipient isn't this device or designated gate,
    if (recipient != localAddress && destination != destinationAddress) {
      Serial.print(F("This message is not for me: "));
      Serial.println(packet);
      return;                             // skip rest of function
    }

    if (incomingLength != packet.length()) {   // check length for error
      Serial.print(F("error: message length does not match length: "));
      Serial.println(packet);
      return;                             // skip rest of function
    }

    // Parse json to check if json data is valid
    //String json = "{\"o\":160,\"g\":240,\"d\":1,\"m\":{\"t\":2129459,\"i\":0.4428,\"v\":7.557981}}";
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, packet);
    if (error) return;
    doc.shrinkToFit(); //reduces the capacity of the memory pool to match the current usage
    // Resend packet to server
    DynamicJsonDocument nDoc(1024);
    nDoc["o"] = sender;             //origin
    nDoc["g"] = localAddress;       //gate
    nDoc["d"] = destinationAddress; //dest
    JsonObject m = nDoc.createNestedObject("m");
    nDoc["m"] = doc;             //message
    nDoc.shrinkToFit(); //reduces the capacity of the memory pool to match the current usage
    String payLoad;
    serializeJson(nDoc, payLoad);
    Serial.print(F("Sending packet: "));
    Serial.println(payLoad);
    sendPayload(sender, payLoad);
  }
  
  if(checkTimer()){
	DynamicJsonDocument doc(1024);
    doc["t"] = getUtc();                                  //time
    doc["i"] = truncateData(hallsensor.mA_AC());          //current
    doc["v"] = truncateData(voltmeter.getAverage());      //voltage
    doc.shrinkToFit();
    DynamicJsonDocument nDoc(1024);
    nDoc["o"] = localAddress;       //origin
    nDoc["g"] = localAddress;       //gate
    nDoc["d"] = destinationAddress; //dest
    JsonObject m = nDoc.createNestedObject("m");
    nDoc["m"] = doc;             //message
    nDoc.shrinkToFit(); //reduces the capacity of the memory pool to match the current usage
    String payLoad;
    serializeJson(nDoc, payLoad);
    Serial.print(F("Sending packet: "));
    Serial.println(payLoad);
    sendPayload(sender, payLoad);  
  }
  
  getRandom(randNumber);
}