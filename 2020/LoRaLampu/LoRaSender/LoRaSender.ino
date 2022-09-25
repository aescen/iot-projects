#include "Arduino.h"
#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#include "RTClib.h"
#include "ACS712.h"
#include <Voltmeter.h>

const byte destinationAddress = 0x01; // Server
const byte gateAddress = 0xF0; // Gateway
const byte localAddress = 0xA0;// Nodes: 0xA0, 0xA1, 0xA2, 0xA3
unsigned long tStart = 0; //For interval
unsigned long randNumber;
const int maxTime = 10000;//10s
const int minTime = 5000;//5s

const uint8_t PIN_HALLSENSOR = A1;
const uint8_t PIN_VOLTMETER = A0;

RTC_DS3231 rtc;
//analogPin, volts, maxADC, mVperA)
ACS712  hallsensor(PIN_HALLSENSOR, 5.0, 1023, 185);
//sensorPin, maxVoltage, readingNumber
Voltmeter voltmeter(PIN_VOLTMETER, 25, 10);

void sendPayload(String outgoing) {
  LoRa.beginPacket();
  LoRa.write(destinationAddress);       // add destination address
  LoRa.write(gateAddress);              // add gateway address
  LoRa.write(localAddress);             // add sender address
  LoRa.write(outgoing.length());        // add payload length
  LoRa.print(outgoing);                 // add payload
  LoRa.endPacket();
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
  if ( now - tStart >= 300000  ) //check to see if it is time to transmit based on set interval
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

  Serial.println(F("LoRa Sender"));
  Serial.print(F("Destination address: 0x"));
  Serial.println(destinationAddress, HEX);
  Serial.print(F("Gateway address: 0x"));
  Serial.println(gateAddress, HEX);
  Serial.print(F("Local address: 0x"));
  Serial.println(localAddress, HEX);

  if (!LoRa.begin(467.5E6)) {
    Serial.println(F("Starting LoRa failed!"));
    while (1);
  }
  delay(10);
}

void loop() {
  if(checkTimer()){
    String data;
    DynamicJsonDocument doc(1024);
    doc["t"] = getUtc();                                  //time
    doc["i"] = truncateData(hallsensor.mA_AC());          //current
    doc["v"] = truncateData(voltmeter.getAverage());      //voltage
    doc.shrinkToFit(); //reduces the capacity of the memory pool to match the current usage
    serializeJson(doc, data);
    Serial.print(F("Sending packet: "));
    Serial.println(data);
    sendPayload(data);
    getRandom(randNumber);
    delay(randNumber); // Interval to send data, random from 5s-10s
    LoRa.flush();
  }
}
