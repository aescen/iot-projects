/******************************************************************************************** Includes **/
#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
/**/

#define sprint Serial.print
#define sprintln Serial.println

/******************************************************************************************** Radio setup **/
const byte destinationAddress = 0x01; // Server
const byte clientAddress = 0xA0;// Nodes: 0xA0, 0xA1
unsigned long randNumber;
const int maxTime = 5555;//5.5s
const int minTime = 2222;//2.2s
#define NODE_ID 1
/**/

/******************************************************************************************** Others/Variables **/
#define TEST_MODE true // change to false if using sensor
const unsigned long tInterval = 2000;
unsigned long tStart = 0;
bool timer = false;

float valMoist, valTemp, valPh, valNPK, valHumidDHT, valTempDHT;
float newValMoist, newValTemp, newValPh, newValNPK, newValHumidDHT, newValTempDHT;

/**/

/******************************************************************************************** Functions goes below **/
// Check timer
bool checkTimer() {
  unsigned long now = millis(); // get timer value
  if ( now - tStart >= tInterval ) // check to see if it is time to transmit based on set interval
  {
    tStart = now; //reset start time of timer
    return true;
  }
  else return false;
}

// Send payload using Payload_to_server
void sendPayload(String outgoing) {
  while (LoRa.beginPacket() == 0) {
    Serial.print("waiting for radio ... ");
    delay(10);
  }
  LoRa.beginPacket();
  delay(2);
  LoRa.print(outgoing);
  LoRa.endPacket(true);
  delay(2);
  LoRa.flush();
  delay(10);
}

void getRandom(long rN = 0) {
  randomSeed(random(0, 1024) + rN);
  randNumber = random(minTime, maxTime);
}

float truncateData(float data) {
  int temp = data * 1000;
  float temp2 = temp;
  return temp2 / 1000;
}

void readSensorsData() {
  if (TEST_MODE) {
    newValMoist = random(12);
    newValTemp = random(36);
    newValPh = random(12);
    newValNPK = random(12);
    newValHumidDHT = random(100);
    newValTempDHT = random(36);
  } else {
    //newValMoist = MoistMeter.getValue();
    //newValPh = PHMeter.getValue();
  }


}
/**/

/******************************************************************************************** setup **/
void setup() {
  Serial.begin(115200);
  if (!TEST_MODE) randomSeed(analogRead(A0));

  sprintln(F("-=:: KUD SUBUR ::=-\n"));
  sprintln(F("-=:: NODE KUALITAS TANAH ::=-\n"));

  delay(500);
  randNumber = random(minTime, maxTime);

  /* Radio config */
  Serial.println(F("LoRa Sender"));
  Serial.print(F("Destination address: 0x"));
  Serial.println(destinationAddress, HEX);
  Serial.print(F("Client address: 0x"));
  Serial.println(clientAddress, HEX);

  if (!LoRa.begin(467.5E6)) {
    Serial.println(F("Starting LoRa failed!"));
    while (100);
  }
  delay(10);
  sprintln(F("\n-=:: Setup done ::=-\n"));
}

/******************************************************************************************** main loop **/
void loop() {
  // Sensor readings
  readSensorsData();

  if (timer) {
    if (valMoist != newValMoist
        || valTemp != newValTemp
        || valPh != newValPh
        || valNPK != newValNPK
        || valHumidDHT != newValHumidDHT
        || valTempDHT != newValTempDHT) {
      sprint(F("Soil Moisture: ")); /**/ sprintln(newValMoist);
      sprint(F("Soil Temp: ")); /******/ sprintln(newValTemp);
      sprint(F("Soil PH: ")); /********/ sprintln(newValPh);
      sprint(F("Soil NPK: ")); /*******/ sprintln(newValNPK);
      sprint(F("Humid: ")); /**********/ sprintln(newValHumidDHT);
      sprint(F("Temp DHT: ")); /*******/ sprintln(newValTempDHT);

      valMoist = newValMoist;
      valTemp = newValTemp;
      valPh = newValPh;
      valNPK = newValNPK;
      valHumidDHT = newValHumidDHT;
      valTempDHT = newValTempDHT;

      // Upload data
      DynamicJsonDocument packet(256);
      packet["c"] = clientAddress;
      packet["s"] = destinationAddress; //dest
      JsonObject data = packet.createNestedObject("d");
      data["i"] = NODE_ID;
      data["sm"] = valMoist;
      data["st"] = valTemp;
      data["sp"] = valPh;
      data["n"] = valNPK;
      data["dh"] = valHumidDHT;
      data["dt"] = valTempDHT;
      packet.shrinkToFit();

      String payload;
      serializeJson(packet, payload);
      Serial.print(F("Sending packet: "));
      Serial.println(payload);
      sendPayload(payload);

      getRandom(randNumber);
      delay(randNumber);
    }
  }
  timer = checkTimer();
}
/** end **/
