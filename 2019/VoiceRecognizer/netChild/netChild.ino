/********************************************************************************************Includes**/
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
/**/
/********************************************************************************************Radio setup**/
RF24 radio(8, 9); //CE,CSN
RF24Network network(radio);
const uint16_t thisNode = 021; //Address of this node in Octal format; BC1.011,BC1.021,BC2.012
/**/
/********************************************************************************************Variables**/
int motor = 2;
uint16_t node;
char data;
struct Payload_io {
  char data;
};
/**/
/********************************************************************************************Arduino Setup**/
void setup() {
  Serial.begin(230400);
  SPI.begin();
  pinMode(2, OUTPUT);

  Serial.println(F("Radio init."));
  radio.begin();
  network.begin(90, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  Serial.print(F("Child "));
  Serial.print(thisNode, OCT);
  Serial.println(F(" running."));
}
/**/
/********************************************************************************************Loop start**/
void loop() {
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
    if ( data == 'A' ) {
      digitalWrite(motor, HIGH); delay(1000); digitalWrite(motor, LOW);
    }

    else if ( data == 'B' ) {
      digitalWrite(motor, HIGH); delay(700); digitalWrite(motor, LOW); delay(300);
      digitalWrite(motor, HIGH); delay(700); digitalWrite(motor, LOW);
    }

    else if ( data == 'C' ) {
      digitalWrite(motor, HIGH); delay(700); digitalWrite(motor, LOW); delay(300);
      digitalWrite(motor, HIGH); delay(700); digitalWrite(motor, LOW); delay(300);
      digitalWrite(motor, HIGH); delay(700); digitalWrite(motor, LOW);
    }
  }
}
/**/
/********************************************************************************************Functions goes below**/
