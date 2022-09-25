/********************************************************************************************Includes**/
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
#include <RFID.h>
/**/
/********************************************************************************************RFID setup**/
#define SS_PIN 10
#define RST_PIN 2
RFID rfid(SS_PIN, RST_PIN);
/**/
/********************************************************************************************Radio setup**/
RF24 radio(7, 8); //CE,CSN
RF24Network network(radio);
const uint16_t rXNode = 00; //Address of the coordinator in Octal format
const uint16_t thisNode = 02; //Address of this node in Octal format
/**/
/********************************************************************************************Variables**/
float ldr; //Used to store voltage reading from photodiode
unsigned long tStart = 0; //For interval
unsigned long tInterval = 2000; //For interval
bool timer = false;
bool access = true;
bool statusUpdate = true;
int cardID[5] = {0, 0, 0, 0, 0};
/* Card tag serial:
   {213, 105, 65, 226, 31}; //Device 1(SPA)
   {145, 55, 102, 47, 239}; //Device 2(OS)
   {131, 120, 21, 29, 243}; //Device 3(x)
*/
//int cID[5] = {145, 55, 102, 47, 239}; //Node 1
int cID[5] = {213, 105, 65, 226, 31}; //Node 2
//int cID[5] = {131, 120, 21, 29, 243}; //Node 3
float statusCode;
int serNum[5];
struct Payload_out {
  float ldr; //ldr from LDR
  float cIDa; //card serial number octet 1
  float cIDb; //card serial number octet 2
  float cIDc; //card serial number octet 3
  float cIDd; //card serial number octet 4
  float cIDe; //card serial number octet 5
  //
  float cIDf; //card serial number octet 1
  float cIDg; //card serial number octet 2
  float cIDh; //card serial number octet 3
  float cIDi; //card serial number octet 4
  float cIDj; //card serial number octet 5
  float statusType; //access type: 0 device is ready, 1 device is taken, 2 device is wrong)
};
/**/
/********************************************************************************************Arduino Setup**/
void setup() {
  Serial.begin(115200);
  SPI.begin();
  burn8Readings(A0);

  Serial.println(F("Network begin"));
  radio.begin();
  network.begin(90, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_2MBPS);

  //RFID
  Serial.print(F("Initializing RFID..."));
  rfid.init();
  checkDevice();
}
/**/
/********************************************************************************************Loop start**/
void loop() {
  //network.update();
  /*  0:device taken;1:device ready;2:device wrong
      Read ldr, when ldr is low(device is taken) send payload of existing ldrVal + nodeID + cardID + statusCode(0)
      when device is returned back read cardID and compare, if correct send payload of existing ldrVal + nodeID + cardID + statusCode(1)
      otherwise send payload of existing ldrVal + nodeID + cardID + statusCode(2)
  */
  getSensorsData(); //Get ldr value
  while (ldr <= 300) { //ldr value is low, device is taken
    delay(1000);
    if (statusUpdate) {
      Serial.print(F("#Device unloaded!;"));
      statusCode = 1; //Set status to device taken
      Serial.print(F(";LDR:"));
      Serial.print(ldr);
      Serial.print(F(";DeviceID:"));
      for (int i = 0; i < 5; i++) {
        Serial.print(cID[i]);
        if (i <= 3) {
          Serial.print(F(" "));
        }
      }
      Serial.print(F(";Status:"));
      Serial.print((int)statusCode);
      sendPayload(ldr, cID[0], cID[1], cID[2], cID[3], cID[4], statusCode); //Send data
      statusUpdate = false;//node status is already updated to server
    }
    else if (!statusUpdate) {
      timer = checkTimer();
      if (timer) {
        statusCode = 1; //Set status to device taken
        Serial.print(F("#Device not ready!;"));
        Serial.print(F("LDR:"));
        Serial.print(ldr);
        Serial.print(F(";SysDevice ID:"));
        for (int i = 0; i < 5; i++) {
          Serial.print(cID[i]);
          if (i <= 3) {
            Serial.print(F(" "));
          }
        }
        Serial.print(F(";Status:"));
        Serial.println((int)statusCode);
        //network.update();
      }
    }
    getSensorsData();//update ldr value periodically
    if (ldr >= 400) {
      statusUpdate = true;//node status is changed, need to update to server
      break;
    }
  }
  while (ldr >= 400) {//ldr is high, device returned
    if (statusUpdate) {
      Serial.print(F("#Device loaded!"));
      //Comparing cardID
      readCardSerial();
      if (access) { //cardID is correct
        Serial.println(F("#Device correct!"));
        statusCode = 0; //Set status to device is ready(0)
        Serial.print(F("LDR:"));
        Serial.print(ldr);
        Serial.print(F("CardID:"));
        for (int i = 0; i < 5; i++) {
          Serial.print(cardID[i]);
          if (i <= 3) {
            Serial.print(F(" "));
          }
        }
        sendPayload(ldr, cardID[0], cardID[1], cardID[2], cardID[3], cardID[4], statusCode);
        statusUpdate = false;
      }
      else if (!access) { //cardID is wrong
        statusCode = 2;
        Serial.print(F("LDR:"));
        Serial.print(ldr);
        Serial.print(F("CardID:"));
        for (int i = 0; i < 5; i++) {
          Serial.print(cardID[i]);
          if (i <= 3) {
            Serial.print(F(" "));
          }
        }
        Serial.print(F("LDR:"));
        Serial.print((int)statusCode);
        sendPayload(ldr, cardID[0], cardID[1], cardID[2], cardID[3], cardID[4], statusCode);
        while (true) {//Wait until device is back as expected, otherwise loop the RFID cardID reading
          readCardSerial(); //Read cardID
          if (access) { //Device is back
            statusCode = 0;
            sendPayload(ldr, cardID[0], cardID[1], cardID[2], cardID[3], cardID[4], statusCode);
            statusUpdate = false;
            break;
          }
          timer = checkTimer();
          if (timer) {
            Serial.println(F("Please return the correct device to continue!"));
            statusCode = 2;
          }
        }
      }
    }
    else if (!statusUpdate) { //Status already updated
      timer = checkTimer();
      readCardSerial();
      if (timer) {
        Serial.print(F("#Device ready!"));
        statusCode = 0;//Set status to device ready
        Serial.print(F("LDR:"));
        Serial.print(ldr);
        Serial.print(F(";Device ID:"));
        for (int i = 0; i < 5; i++) {
          Serial.print(cardID[i]);
          if (i <= 3) {
            Serial.print(F(" "));
          }
        }
        Serial.print(F(";Status:"));
        Serial.println((int)statusCode);
        //network.update();
      }
    }
    getSensorsData();//update ldr value periodically
    if (ldr <= 300) {
      statusUpdate = true;//node status is changed, need to update to server
      break;
    }
  }
  timer = checkTimer();
}
/**/
/********************************************************************************************Functions goes below**/

//Read card or tag serial
void readCardSerial() {
  while (rfid.isCard()) {
    while (rfid.readCardSerial()) {
      for (int i = 0; i < 5; i++ ) {
        if (rfid.serNum[i] != cID[i]) {
          access = false; //Device ID is wrong!
          statusCode = 2;
          cardID[i] = rfid.serNum[i];
        }
        else if ( rfid.serNum[i] == cID[i] ) {
          statusCode = 0;
          access = true; //Device ID is correct!
          cardID[i] = rfid.serNum[i];
        }
      }
      break;
    }
    break;
  }
  rfid.halt();
}

//Check Device
void checkDevice() {
  Serial.println(F("Checking device..."));
  while (true) {
    while (!rfid.isCard()) {
      timer = checkTimer();
      if (timer) {
        Serial.println(F("Device not detected or no device found!"));
        statusCode = 2;
        getSensorsData();
        sendPayload(ldr, cardID[0], cardID[1], cardID[2], cardID[3], cardID[4], statusCode);
        if (rfid.isCard()) {
          checkDevice();
        }
      }
    }
    readCardSerial(); //Read cardID
    readCardSerial();
    if (access) { //Wait until device is back as expected, otherwise loop the RFID cardID reading
      statusCode = 0;
      getSensorsData(); //Get ldr value
      sendPayload(ldr, cardID[0], cardID[1], cardID[2], cardID[3], cardID[4], statusCode);
      //statusUpdate = false;
      break;
    }
    readCardSerial();
    if (!access) {
      timer = checkTimer();
      if (timer) {
        Serial.println(F("Please return the correct device to continue!"));
        statusCode = 2;
        getSensorsData(); //Get ldr value
        sendPayload(ldr, cardID[0], cardID[1], cardID[2], cardID[3], cardID[4], statusCode);
      }
    }
  }
}

//Check timer
bool checkTimer() {
  unsigned long now = millis(); //get timer value
  if ( now - tStart >= tInterval  ) //check to see if it is time to transmit based on set interval
  {
    tStart = now; //reset start time of timer
    return true;
  }
  else return false;
}

//Send payload
void sendPayload( float ldr, float cIDa, float cIDb, float cIDc, float cIDd, float cIDe, float statusCode ) {
  RF24NetworkHeader header(rXNode);
  Payload_out payload = { ldr, cIDa, cIDb, cIDc, cIDd, cIDe, cID[0], cID[1], cID[2], cID[3], cID[4], statusCode };
  if ( !network.write(header, &payload, sizeof(payload)) ) {
    // Retry
    if ( !network.write(header, &payload, sizeof(payload)) ) {
      PIND |= (1 << LED_BUILTIN); //this toggles the status LED at LED_BUILTIN to show transmit failed
      Serial.println(F("Send failed"));
    } else {
      delay(100);
      network.write(header, &payload, sizeof(payload));
      Serial.println(F("#Send OK"));
    }
  } else {
    delay(100);
    network.write(header, &payload, sizeof(payload));
    Serial.println(F("#Send OK"));
  }
}

//used to average multiple ADC values together
//This can help eliminate noise in measurements
float averageADCReadings(int aDCpin, int avgCount) {
  float aDCAvg = 0;
  for (int i = 0; i < avgCount; i++) {
    aDCAvg = aDCAvg + analogRead(aDCpin);
	delay(1);
  }

  return (aDCAvg / avgCount);
}

//This function makes 8 ADC measurements but does nothing with them
//Since after a reference change the ADC can return bad readings. This function is used to get rid of the first
//8 readings to ensure next reading is accurate
void burn8Readings(int pin) {
  for (int i = 0; i < 8; i++) {
    analogRead(pin);
  }
}

void getSensorsData() {
  //Get sensors data
  ldr = round(averageADCReadings(A0, 8) + 0.5);
  //Serial.print(F(";ldr:"));
  //Serial.print(ldr, 4);
}
