/********************************************************************************************Includes**/
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
/**/
/********************************************************************************************Radio setup**/
RF24 radio(9, 10); //CE,CSN
RF24Network network(radio);
const uint16_t thisNode = 00; //Address of this node in Octal format
/**/
/********************************************************************************************Variables**/
uint16_t nodeAddr[2] = { 01, 02 };
char data;
struct Payload_out {
  char data;
};
/**/
/********************************************************************************************Arduino Setup**/
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(230400);
  SPI.begin();

  Serial.println(F("Radio init."));
  radio.begin();
  network.begin(90, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  Serial.print(F("Master node "));
  Serial.print(thisNode, OCT);
  Serial.println(F(" running."));
}
/**/
/********************************************************************************************Loop start**/
void loop() {
  //Input data
  network.update();
  Serial.print(F("Input data:"));
  while (!Serial.available()) {}
  data = Serial.read();
  if (data == 'A' || data == 'B' || data == 'C') {
    //Send data
    for (int i = 0; i < sizeof(nodeAddr); i++) {
      Serial.print(F("Sending to node:"));
      Serial.print(nodeAddr[i], OCT);
      sendData(data, nodeAddr[i]);
    }
    Serial.end();
    delay(10);
    Serial.begin(230400);
  }
  else{
    Serial.println("Wrong input! Input 'A' or 'B' or 'C'!");
    Serial.end();
    delay(10);
    Serial.begin(230400);
    }
}
/**/
/********************************************************************************************Functions goes below**/
//Send payload
void sendData( char data, uint16_t node ) {
  RF24NetworkHeader header(node);
  Payload_out payload = { data };
  //send data onto network and make sure it gets there
  if (!network.write(header, &payload, sizeof(payload))) {
    digitalWrite(LED_BUILTIN, LOW); //transmit was successful so make sure status LED is off
    Serial.println(F("#Send failed!"));
  }
  else  { //transmit failed, try again
    Serial.println(F("#Sent!"));
    /*
      if (!network.write(header, &payload, sizeof(payload))) {
      PIND |= (1 << LED_BUILTIN); //this toggles the status LED at LED_BUILTIN to show transmit failed
      Serial.println(F("#Send failed!"));
      }
      else {
      digitalWrite(LED_BUILTIN, LOW); //transmit was successful so make sure status LED is off
      Serial.println(F("#Sent"));
      }*/
  }
}
