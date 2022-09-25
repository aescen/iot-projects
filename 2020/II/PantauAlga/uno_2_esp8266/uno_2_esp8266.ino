#include <Servo.h>
#include <ArduinoJson.h>

//servo
Servo myservo;

//Vars
int pinMoist = A1;
int pinPH = A0;
int pinRelay = 2;
int pinServo = 3;
int servoPos = -1, relay = -1, nServoPos = -1, nRelay = -1, servoPosLog = -1, relayLog = -1;
float ph = -1.0, moist = -1.0, nPh = -1.0, nMoist = -1.0, phLog = -1.0, moistLog = -1.0;
unsigned long logsSync, dataSync;

void servoBuka() {
  for (servoPos = 0; servoPos <= 180; servoPos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(servoPos);              // tell servoPos to go to servoPosPosition in variable 'servoPosPos'
    delay(20);                       // waits 20ms for the servoPos to reach the servoPosPosition
  }
  nServoPos = servoPos - 1;
}

void servoTutup() {
  for (servoPos = 180; servoPos >= 0; servoPos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(servoPos);              // tell servoPos to go to servoPosPosition in variable 'servoPosPos'
    delay(20);                       // waits 20ms for the servoPos to reach the servoPosPosition
  }
  nServoPos = servoPos + 1;
}

void rOff() {
  digitalWrite(pinRelay, HIGH);
  nRelay = 0;
  delay(1);
}

void rOn() {
  digitalWrite(pinRelay, LOW);
  nRelay = 1;
  delay(1);
}

//used to average multiple ADC values together
//This can help eliminate noise in measurements
float averageADCReadings(int aDCpin, int avgCount) {
  float aDCAvg = 0;
  for (int i = 0; i < avgCount; i++) {
    aDCAvg = aDCAvg + analogRead(aDCpin);
    delay(10);
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
  delay(1);
}

void syncData(int data1 = 0, int data2 = 0, float data3 = 0, float data4 = 0, int type = 1) {
  if (type == 1) {
    StaticJsonDocument<1024> doc;
    doc["servo"] = data1;
    doc["relay"] = data2;
    doc["ph"] = data3;
    doc["moist"] = data4;
    doc["type"] = 1;
    serializeJson(doc, Serial);
    delay(1);
  }
  if (type == 2) {
    StaticJsonDocument<1024> doc;
    doc["servo"] = data1;
    doc["relay"] = data2;
    doc["ph"] = data3;
    doc["moist"] = data4;
    doc["type"] = 2;
    serializeJson(doc, Serial);
    delay(1);
  }
}

void setup() {
  Serial.begin(9600);
  while (!Serial) continue;

  //servo
  myservo.attach(pinServo);
  myservo.write(0);
  servoPos = 0;

  //relay
  pinMode(pinRelay, OUTPUT);
  digitalWrite(pinRelay, HIGH);
  relay = 0;

  burn8Readings(pinPH);
  burn8Readings(pinMoist);
}

void loop() {
  while (!Serial) continue;
  nPh = averageADCReadings(pinPH, 8);
  nMoist = averageADCReadings(pinMoist, 8);

  if ( (millis() - dataSync) >= 2500 ) { //sync time every 2.5 seconds
    if ( (servoPos != nServoPos) || (relay != nRelay) || ((int)ph != (int)nPh) || ((int)moist != (int)nMoist) ) {
      syncData(nServoPos, nRelay, nPh, nMoist, 1);
      servoPos = nServoPos; relay = nRelay; ph = nPh; moist = nMoist;
    }
    dataSync = millis();
  }

  //update logs every 1 minutes
  if ( (millis() - logsSync) >= 60000 ) { //sync time every 10 minutes
    if ( (servoPosLog != servoPos) || (relayLog != relay) || ((int)phLog != (int)ph) || ((int)moistLog != (int)moist) ) {
      syncData(servoPos, relay, ph, moist, 2);
      servoPosLog = servoPos; relayLog = relay; phLog = ph; moistLog = moist;
    }
    logsSync = millis();
  }
}
