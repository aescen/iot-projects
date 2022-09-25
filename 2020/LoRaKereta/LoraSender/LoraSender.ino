#include <SPI.h>
#include <LoRa.h>
const int trigPin = 4;
const int echoPin = 5;
// defines variables
long duration;
int distance = 0;
const int jarakKereta = 30;

const byte receiverAddress = 0xA0; // Server
const byte localAddress = 0xA2;//0xA1(kanan), 0xA2(kiri)
const int maxTime = 3000;
const int minTime = 1000;
long randNumber;

void sendPayload(String outgoing) {
  LoRa.beginPacket();
  LoRa.write(receiverAddress);              // add receiver address
  LoRa.write(localAddress);             // add sender address
  LoRa.write(outgoing.length());        // add payload length
  LoRa.print(outgoing);                 // add payload
  LoRa.endPacket();
  LoRa.flush();
}

void getRandom(long rN = 0) {
  randomSeed(random(0, 1024) + rN);
  randNumber = random(minTime, maxTime);
}

void setup() {
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  Serial.begin(115200);
  // generate a random number from 2000 to 8000
  randNumber = random(minTime, maxTime);
  while (!Serial);

  Serial.println(F("LoRa Sender"));
  Serial.print(F("Server address: 0x"));
  Serial.println(receiverAddress, HEX);
  Serial.print(F("Local address: 0x"));
  Serial.println(localAddress, HEX);

  if (!LoRa.begin(467.5E6)) {
    Serial.println(F("Starting LoRa failed!"));
    while (1);
  }
  delay(10);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2;
  Serial.print("Sending packet:");
  Serial.println(distance);
  // send packet
  sendPayload(String(distance));

  getRandom(randNumber);
  delay(randNumber); // Interval to send data, random from 5s-10s
}
