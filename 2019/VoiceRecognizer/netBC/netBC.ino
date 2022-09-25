/********************************************************************************************Includes**/
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
/**/
/********************************************************************************************Radio setup**/
RF24 radio(9, 10); //CE,CSN
RF24Network network(radio);
const uint16_t thisNode = 01; //Address of this node in Octal format
/**/
/********************************************************************************************Variables**/
const uint16_t nAChild[2] = { 011, 021 }; //child of BC node 01, don't forget to change thisNode to 01
//const uint16_t nAChild[2] = { 012 }; //child of BC node 02, don't forget to change thisNode to 02
char data;
struct Payload_io {
  char data;
};
/**/
/********************************************************************************************Arduino Setup**/
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  SPI.begin();

  Serial.println(F("Radio init."));
  radio.begin();
  network.begin(90, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  Serial.print(F("Broadcast "));
  Serial.print(thisNode, OCT);
  Serial.println(F(" running."));
}
/**/
/********************************************************************************************Loop start**/
void loop() {
  //Input data
  network.update();
  RF24NetworkHeader header; //create header variable
  Payload_io pio; //create pio variable
  if ( network.available() == true ) {
    network.read(header, &pio, sizeof(pio));
    data = pio.data;
    Serial.print(F("From:"));
    Serial.print(header.from_node, OCT);
    Serial.print(F("; data:"));
    Serial.println(data);
    sendData();

  }
}
/**/
/********************************************************************************************Functions goes below**/
//Send payload
void sendData() {
  for ( int i = 0; i < sizeof(nAChild); i++ ) {
    Serial.print( F("Sending to node:") );
    Serial.print( nAChild[i], OCT );
    uint16_t node = nAChild[i];

    RF24NetworkHeader header(node);
    Payload_io payload = { data };
    if ( !network.write(header, &payload, sizeof(payload)) ) {
      digitalWrite(LED_BUILTIN, LOW); //transmit was successful so make sure status LED is off
      Serial.println( F("#Send failed!") );
    }
    else  { //transmit failed, try again
      Serial.println( F("#Sent!") );
      digitalWrite(LED_BUILTIN, LOW); //transmit was failed so turn on status LED
    }
  }
}
