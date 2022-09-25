#include <RF24.h>
#include <RF24Network.h>
#include <RF24Mesh.h>
#include <SPI.h>
#include <printf.h>

/**** Configure the nrf24l01 CE and CS pins ****/
//const uint8_t nodeId = 1;
uint8_t nodeId = 1;
const uint8_t toNodeId = 0;
RF24 radio(9, 10);
RF24Network network(radio);
RF24Mesh mesh(radio, network);

struct payloadOut {
  float status;
  float total;
  float nodeId;
};


void setup() {
  Serial.begin(115200);
  SPI.begin();
  printf_begin();

  Serial.print(F("Node Id: "));
  mesh.setNodeID(nodeId);
  Serial.println(mesh.getNodeID(), OCT);
  Serial.println(F("Connecting to the mesh..."));
  mesh.begin(97, RF24_1MBPS, 5000); //channel, data rate, timeout
  radio.setRetries(2, 2);
  radio.setAutoAck(true);
  radio.setPALevel(RF24_PA_HIGH);
  radio.setDataRate(RF24_1MBPS);
  radio.setCRCLength(RF24_CRC_8);
  radio.printPrettyDetails();

  mesh.renewAddress(5000);
  Serial.print(F("Get addressId: "));
  int16_t addressId = mesh.getAddress(mesh.getNodeID());    /* Master will return and send 00 address for a nodeID with address 0, -1 if not found */
  Serial.println(addressId);
  if (addressId <= 0) {
    Serial.print(F("Renew addressId: "));
    mesh.renewAddress(5000);
    Serial.println(mesh.getAddress(mesh.getNodeID()), OCT);
  }
}

void sendNrf(float s, float t, float id = 1);
void sendNrf(float s, float t, float id) {
  payloadOut payload = { s, t, id };
  RF24NetworkHeader header(/*to node*/ toNodeId);
  String p = String("Send OK: ") + String("Status: ") + String(s) + String(" | Total: ") + String(t);
  if (!mesh.write(&payload, 'M', sizeof(payload), toNodeId)) {
    if (!mesh.checkConnection()) {
      Serial.print("Renewing AddressId: ");
      mesh.renewAddress(5000);
      Serial.println(mesh.getAddress(mesh.getNodeID()), OCT);
    }
    else Serial.println("Send fail, Test OK");
  }
  else Serial.println(p);
}

uint8_t status = 2;
uint32_t total = 0;
uint32_t sendTimer = millis();
uint16_t sendDelay = 2000;
void loop() {
  mesh.update();

  if ((millis() - sendTimer) >= sendDelay) {
    status = random(1, 4);/* random number from 1 to 3 */
    total = random(0, 1023);
    nodeId = random(1, 4);
    sendNrf(status, total, nodeId);

    sendTimer = millis();
  }
}
