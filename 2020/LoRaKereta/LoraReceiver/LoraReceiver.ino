#include <SPI.h>
#include <LoRa.h>

const byte senderAddressA = 0xA1; // Sender
const byte senderAddressB = 0xA2; // Sender
const byte localAddress = 0xA0;  //Server

const int pinLampuStop = 6;
const int pinLampuJalan = 5;
const int pinLampuKanan = 8;
const int pinLampuKiri = 7;
const int jarakKereta = 30;
bool lampuKanan;
bool lampuKiri;
int jarakKanan = 100;
int jarakKiri = 100;
int waktuTunggu = 0.1; //menit

void setup() {
  Serial.begin(115200);
  while (!Serial);

  //Relays
  pinMode(pinLampuStop, OUTPUT);// Relay on pin
  digitalWrite(pinLampuStop, HIGH);//Deactivate relay
  pinMode(pinLampuJalan, OUTPUT);// Relay on pin
  digitalWrite(pinLampuJalan, HIGH);//Deactivate relay
  pinMode(pinLampuKanan, OUTPUT);// Relay on pin
  digitalWrite(pinLampuKanan, HIGH);//Deactivate relay
  lampuKanan = false;
  pinMode(pinLampuKiri, OUTPUT);// Relay on pin
  digitalWrite(pinLampuKiri, HIGH);//Deactivate relay
  lampuKiri = false;

  Serial.println(F("LoRa Receiver"));
  Serial.print(F("Local address: 0x"));
  Serial.println(localAddress, HEX);
  Serial.print(F("Sender address A: 0x"));
  Serial.println(senderAddressA, HEX);
  Serial.print(F("Sender address B: 0x"));
  Serial.println(senderAddressB, HEX);

  if (!LoRa.begin(467.5E6)) {
    Serial.println(F("Starting LoRa failed!"));
    while (1);
  }
  delay(10);
}

void loop() {
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  byte sender;
  if (packetSize) {
    // read packet header bytes:
    byte destination = LoRa.read();        // destination address (server)
    sender = LoRa.read();            // sender address (origin)
    byte incomingLength = LoRa.read();    // incoming payload length

    // read packet
    String packet;
    while (LoRa.available()) {
      packet += (char)LoRa.read();
    }

    if (incomingLength != packet.length()) {   // check length for error
      Serial.print(F("error: message length does not match length - "));
      Serial.println(packet);
      return;                             // skip rest of function
    }

    if (sender == senderAddressA) {
      jarakKanan = packet.toInt();
    } else if (sender == senderAddressB) {
      jarakKiri = packet.toInt();
    }
  }

  if (jarakKanan > 0) {
    if (!lampuKiri) {
      digitalWrite(pinLampuKanan, LOW); //Activate lamp relay
      lampuKanan = true;
      Serial.print(F("0x"));
      Serial.print(sender, HEX);
      Serial.println(F(" Lampu kanan: ON"));
      delay(1000 * 60 * waktuTunggu);
    } else {
      digitalWrite(pinLampuKanan, HIGH); //Deactivate lamp relay
      lampuKanan = false;
      Serial.print(F("0x"));
      Serial.print(sender, HEX);
      Serial.println(F(" Lampu kanan: OFF"));
    }
  }

  if (jarakKiri > 0) {
    if (!lampuKanan) {
      digitalWrite(pinLampuKiri, LOW); //Activate lamp relay
      lampuKiri = true;
      Serial.print(F("0x"));
      Serial.print(sender, HEX);
      Serial.println(F(" Lampu kiri: ON"));
      delay(1000 * 60 * waktuTunggu);
    } else {
      digitalWrite(pinLampuKiri, HIGH); //Deactivate lamp relay
      lampuKiri = false;
      Serial.print(F("0x"));
      Serial.print(sender, HEX);
      Serial.println(F(" Lampu kiri: OFF"));
    }
  }

  if (lampuKiri || lampuKanan) {
    digitalWrite(pinLampuStop, LOW); //Activate lamp relay
    digitalWrite(pinLampuJalan, HIGH); //Deactivate lamp relay
  } else if (!lampuKiri && !lampuKanan) {
    digitalWrite(pinLampuStop, HIGH); //Deactivate lamp relay
    digitalWrite(pinLampuJalan, LOW); //Activate lamp relay
  }

}
