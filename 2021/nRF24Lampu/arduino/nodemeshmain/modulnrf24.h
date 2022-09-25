#include <SPI.h>
#include "RF24.h"
#include "RF24Network.h"
#include "RF24Mesh.h"
#include <printf.h>

RF24 radio(8, 9);    /*pin ce,cs*/
RF24Network network(radio);
RF24Mesh mesh(radio, network);

const uint16_t thisNode = 01;
const uint16_t masterNode = 00;

void nrfInit() {
  SPI.begin();
  printf_begin();

  Serial.print(F("Node Id: "));
  mesh.setNodeID(thisNode);
  Serial.println(mesh.getNodeID(), OCT);
  Serial.println(F("Connecting to the mesh..."));
  mesh.begin(97, RF24_1MBPS, 5000); //channel, data rate, timeout
  radio.setRetries(2, 2);
  radio.setAutoAck(true);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setCRCLength(RF24_CRC_8);
  radio.printDetails();

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

struct payloadOut {
  /* arrange variable position from byte->char->int->float (lowest to highest w/o precision) */
  uint16_t nodeId;
  uint32_t epoch;
  float acVolt;
  float dcVolt;
  float dcCurrent;
  float acCurrent;
};
struct payloadIn {
  uint16_t nodeId;
  uint32_t epoch;
  float acVolt;
  float dcVolt;
  float dcCurrent;
  float acCurrent;
};

//functions
void readPayload() {
  RF24NetworkHeader header;
  payloadIn payload;
  network.peek(header);
  network.read(header, &payload, sizeof(payload));
  Serial.print(F("From "));
  switch (header.type) {
    // Display the incoming millis() values from the sensor nodes
    case 'M':
      Serial.print(mesh.getNodeID(header.from_node));
      Serial.print(F(" received \'M\' type. "));
      break;
    case 'N':
      Serial.print(header.from_node);
      Serial.print(F(" received \'N\' type. "));
      break;
    default:
      Serial.print(header.from_node);
      Serial.print(F(" received unknown type. "));
      break;
  }
  //Serial.print((char)header.type);
  Serial.print(F("From: "));
  Serial.print(payload.nodeId);
  Serial.print(F(" data: AC Volt:"));
  Serial.print(payload.acVolt);
  Serial.print(F(", DC Volt:"));
  Serial.print(payload.dcVolt);
  Serial.print(F(", AC Current(I):"));
  Serial.print(payload.acCurrent);
  Serial.print(F(", DC Current(I):"));
  Serial.print(payload.dcCurrent);
  Serial.print(F(". At "));
  Serial.println(payload.epoch);
}

void sendPayload(uint16_t toNodeId, float acv, float dcv, float aci, float dci) {
  payloadOut payload = { thisNode, getUtc(), acv, dcv, aci, dci };
  RF24NetworkHeader header(/*to node*/ toNodeId);

  Serial.print(F("Sending to "));
  Serial.print(toNodeId, OCT);
  Serial.print(F(" data: AC Volt:"));
  Serial.print(payload.acVolt);
  Serial.print(F(", DC Volt:"));
  Serial.print(payload.dcVolt);
  Serial.print(F(", AC Current(I):"));
  Serial.print(payload.acCurrent);
  Serial.print(F(", DC Current(I):"));
  Serial.print(payload.dcCurrent);
  Serial.print(F(". At "));
  Serial.print(payload.epoch);
  //  Serial.print(getUtc());

  if (!mesh.write(&payload, 'M', sizeof(payload), toNodeId)) {
    if ( !mesh.checkConnection() ) {
      Serial.println(F(" Renewing address..."));
      mesh.renewAddress(5000);
    } else {
      Serial.println(F(" Send fail, test Ok"));
    }
  } else {
    Serial.println(F(" Ok."));
  }
}
