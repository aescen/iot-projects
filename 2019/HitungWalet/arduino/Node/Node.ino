/********************************************************************************************Includes**/
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
/**/
/********************************************************************************************PIR setup**/
int calTime = 30; //calibration time
long unsigned int lowIn; //time when the sensor outputs a low state pulse
long unsigned int pause = 5000; //how long the sensor has to be in low state before assuming no motion is detected
bool lockLow = true;
bool takeLowTime;
int pirPin = 2;
int ledPin = 3;
/**/
/********************************************************************************************Radio setup**/
RF24 radio(7, 8); //CE,CSN
RF24Network network(radio);
const uint16_t rXNode = 00; //Address of the coordinator in Octal format
const uint16_t thisNode = 02; //Address of this node in Octal format
/**/
/********************************************************************************************Variables**/
float pirDetect; //PIR detection
struct Payload_out {
  int pirDetect; //temperature from DHT22 sensor
};
/**/
/********************************************************************************************Arduino Setup**/
void setup() {
  Serial.begin(1000000);
  SPI.begin();
  //PIR
  pinMode(pirPin, INPUT);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  ////Give the sensor some time to calibrate
  Serial.print(F("Calibrating sensor"));
  for (int i = 0; i < calTime; i++) {
    Serial.print(F("."));
    delay(1000);
  }
  Serial.println(F("PIR sensor calibrated!"));
  delay(50);
  //NRF
  Serial.println(F("Network begin"));
  radio.begin();
  network.begin(90, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_2MBPS);
}
/**/
/********************************************************************************************Loop start**/
void loop() {
  network.update();
  if (digitalRead(pirPin) == HIGH) {
    digitalWrite(ledPin, HIGH);
    if (lockLow) {
      lockLow = false;
      pirDetect = 1;
      sendPayload(pirDetect);
      Serial.print(F("---"));
      Serial.print(F("Motion detected at "));
      Serial.print(millis() / 1000);
      Serial.println(F("s"));
      delay(50);
    }
    takeLowTime = true;
  }
  if (digitalRead(pirPin) == LOW) {
    digitalWrite(ledPin, LOW);
  }
  if (!lockLow && millis() - lowIn > pause) {
    pirDetect = 0;
    sendPayload(pirDetect);
    lockLow = true;
    Serial.print(F("Motion ended at "));
    Serial.print((millis() - pause) / 1000);
    Serial.println(F("s"));
    delay(50);
  }
}
/**/
/********************************************************************************************Functions goes below**/
//Send payload
void sendPayload( int pirDetect ) {
  RF24NetworkHeader header;
  Payload_out payload = { pirDetect };
  if ( !network.write(header, &payload, sizeof(payload)) ) {
    // Retry
    if ( !network.write(header, &payload, sizeof(payload)) ) {
      PIND |= (1 << LED_BUILTIN); //this toggles the status LED at LED_BUILTIN to show transmit failed
      Serial.println(F("Send failed"));
    } else {
      Serial.println(F("#Send OK"));
    }
  } else {
    Serial.println(F("#Send OK"));
  }
}
/**/
