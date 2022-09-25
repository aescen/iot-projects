/********************************************************************************************Includes**/
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
#include <SoftwareSerial.h>
#include <VoiceRecognitionV3.h>
/**/
/********************************************************************************************Radio setup**/
RF24 radio(9, 10); //CE,CSN
RF24Network network(radio);
const uint16_t thisNode = 00; //Address of this node in Octal format
/**/
/********************************************************************************************Voice recognition setup**/
/* Connection
   Arduino    VoiceRecognitionModule
    2   ------->     TX
    3   ------->     RX
*/
VR myVR(2, 3);   // 3:RX 2:TX, you can choose your favourite pins.
uint8_t record[7]; // save record
uint8_t buf[64];
#define group0        (0)//switchRecord
#define group1        (8)
#define group2        (16)
#define group3        (24)

#define takbir01       (1)
#define takbir02       (2)
#define takbir03       (3)
#define takbir04       (4)
#define itidal0        (5)
#define salam0         (6)

#define takbir11       (9)
#define takbir12       (10)
#define takbir13       (11)
#define takbir14       (12)
#define itidal1        (13)
#define salam1         (14)

#define takbir21       (17)
#define takbir22       (18)
#define takbir23       (19)
#define takbir24       (20)
#define itidal2        (21)
#define salam2         (22)
/********************************************************************************************Variables**/
int ledVR = 6;
int uWSensorLed = 4;
uint16_t nodeAddr[2] = { 01, 02 };
int sensor = 5;
char data;
struct Payload_out {
  char data;
};
/**/
/********************************************************************************************Arduino Setup**/
void setup() {
  //Serial and pinout initialization
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  pinMode(ledVR, OUTPUT);
  pinMode(uWSensorLed, OUTPUT);

  //Radio initialization
  Serial.println(F("Radio init."));
  radio.begin();
  network.begin(90, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  Serial.print(F("Master node "));
  Serial.print(thisNode, OCT);
  Serial.println(F(" running."));
  data = 'A';sendData();data = ' ';//Test
  
  // VRec initialization
  myVR.begin(9600);
  Serial.println("Elechouse Voice Recognition V3 Module\r\nMulti Commands sample");
  ////Clearing recognizer
  if (myVR.clear() == 0) {
    Serial.println("Recognizer cleared.");
  } else {
    Serial.println("Not find VoiceRecognitionModule.");
    Serial.println("Please check connection and restart Arduino.");
    while (1);
  }
  ////Load records
  record[0] = group0; //switchRecord
  record[1] = group1; //group0Record1
  record[2] = group2;
  record[3] = group3;
  if (myVR.load(record, 7) >= 0) {
    printRecord(record, 7);
    Serial.println(F("loaded."));
  }
}
/**/
/********************************************************************************************Loop start**/
void loop() {
  int datasensor = digitalRead(sensor);
  if (datasensor == HIGH) {
    digitalWrite(uWSensorLed, HIGH);
  } else {
    digitalWrite(uWSensorLed, LOW);
  }
  int ret;
  ret = myVR.recognize(buf, 50);
  if (ret > 0) {
    switch (buf[1]) {
      case group0:  //switchRecord
        myVR.clear();
        record[0] = group0;
        record[1] = takbir01;
        record[2] = takbir02;
        record[3] = takbir03;
        record[4] = takbir04;
        record[5] = itidal0;
        record[6] = salam0;
        if (myVR.load(record, 7) >= 0) {
          printRecord(record, 7);
          Serial.println(F("loaded."));
        }
        break;
      case group1:
        myVR.clear();
        record[0] = group1;
        record[1] = takbir11;
        record[2] = takbir12;
        record[3] = takbir13;
        record[4] = takbir14;
        record[5] = itidal1;
        record[6] = salam1;
        if (myVR.load(record, 7) >= 0) {
          printRecord(record, 7);
          Serial.println(F("loaded."));
        }
        break;
      case group2:
        myVR.clear();
        record[0] = group2;
        record[1] = takbir21;
        record[2] = takbir22;
        record[3] = takbir23;
        record[4] = takbir24;
        record[5] = itidal2;
        record[6] = salam2;
        if (myVR.load(record, 7) >= 0) {
          printRecord(record, 7);
          Serial.println(F("loaded."));
        }
        break;
      case salam0: case salam1: case salam2:
        digitalWrite(ledVR, LOW);
        data = 'C';
        sendData();
        Serial.println(data);
        break;
      default:
        break;
    }
    if (datasensor == HIGH) {
      switch (buf[1]) {
        case itidal0: case itidal1: case itidal2:
          digitalWrite(ledVR, LOW);
          data = 'B';
          //sendData();
          Serial.println(data);
          break;
        case takbir01: case takbir02: case takbir03: case takbir04:
          digitalWrite(ledVR, HIGH);
          data = 'A';
          //sendData();
          Serial.println(data);
          break;
        case takbir11: case takbir12: case takbir13: case takbir14:
          digitalWrite(ledVR, HIGH);
          data = 'A';
          //sendData();
          Serial.println(data);
          break;
        case takbir21: case takbir22: case takbir23: case takbir24:
          digitalWrite(ledVR, HIGH);
          data = 'A';
          //sendData();
          Serial.println(data);
          break;
          //      default:
          //        break;
      }
    }
    /** voice recognized */
    printVR(buf);
    sendData(); //kirim();   //<--tempat untuk perintah kirim data
  }


}
/**/
/********************************************************************************************Functions goes below**/
/**
  @brief   Print signature, if the character is invisible,
           print hexible value instead.
  @param   buf     --> command length
           len     --> number of parameters
*/
void printSignature(uint8_t *buf, int len) {
  int i;
  for (i = 0; i < len; i++) {
    if (buf[i] > 0x19 && buf[i] < 0x7F) {
      Serial.write(buf[i]);
    }
    else {
      Serial.print("[");
      Serial.print(buf[i], HEX);
      Serial.print("]");
    }
  }
}

/**
  @brief   Print signature, if the character is invisible,
           print hexible value instead.
  @param   buf  -->  VR module return value when voice is recognized.
             buf[0]  -->  Group mode(FF: None Group, 0x8n: User, 0x0n:System
             buf[1]  -->  number of record which is recognized.
             buf[2]  -->  Recognizer index(position) value of the recognized record.
             buf[3]  -->  Signature length
             buf[4]~buf[n] --> Signature
*/
void printVR(uint8_t *buf) {
  Serial.println("VR Index\tGroup\tRecordNum\tSignature");

  Serial.print(buf[2], DEC);
  Serial.print("\t\t");

  if (buf[0] == 0xFF) {
    Serial.print("NONE");
  }
  else if (buf[0] & 0x80) {
    Serial.print("UG ");
    Serial.print(buf[0] & (~0x80), DEC);
  }
  else {
    Serial.print("SG ");
    Serial.print(buf[0], DEC);
  }
  Serial.print("\t");

  Serial.print(buf[1], DEC);
  Serial.print("\t\t");
  if (buf[3] > 0) {
    printSignature(buf + 4, buf[3]);
  }
  else {
    Serial.print("NONE");
  }
  //  Serial.println("\r\n");
  Serial.println();
}

void printRecord(uint8_t *buf, uint8_t len) {
  Serial.print(F("Record: "));
  for (int i = 0; i < len; i++) {
    Serial.print(buf[i], DEC);
    Serial.print(", ");
  }
}

//Send payload data
void sendData() {
  for (int i = 0; i < sizeof(nodeAddr); i++) {
    Serial.print(F("Sending to node:"));
    Serial.print(nodeAddr[i], OCT);
    uint16_t node = nodeAddr[i];

    RF24NetworkHeader header(node);
    Payload_out payload = { data };
    //send data onto network and make sure it gets there
    if (!network.write(header, &payload, sizeof(payload))) {
      digitalWrite(LED_BUILTIN, LOW); //transmit was successful so make sure status LED is off
      Serial.println(F("#Send failed!"));
    }
    else  { //transmit failed, try again
      Serial.println(F("#Sent!"));
      digitalWrite(LED_BUILTIN, LOW); //transmit was failed so turn on status LED
    }
    delay(50);
  }
}
/**/
