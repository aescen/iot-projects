#include "RF24Network.h"
#include "RF24.h"
#include "RF24Mesh.h"
#include <SPI.h>
#include <printf.h>

/***** Configure the chosen CE,CS pins *****/
RF24 radio(8, 9);
RF24Network network(radio);
RF24Mesh mesh(radio, network);


void setup() {
  Serial.begin(115200);
  SPI.begin();
  printf_begin();

  mesh.setNodeID(00);
  mesh.begin(96, RF24_1MBPS, 5000); //channel, data rate, timeout
  mesh.setStaticAddress(1, 05); //node id, address

  radio.setRetries(2, 2);
  radio.setPALevel(RF24_PA_MAX);
  radio.printDetails();

  Serial.print(F("Master node: "));
  Serial.println(mesh.getAddress(mesh.getNodeID()), OCT);
}


//vars
struct payloadOut {
  float acVolt;
  float dcVolt;
  float current;
  double epoch;
};
struct payloadIn {
  float acVolt;
  float dcVolt;
  float current;
  double epoch;
};
uint32_t displayTimer = 0;


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
  Serial.print(F("Data: ACV:"));
  Serial.print(payload.acVolt);
  Serial.print(F(", DCV:"));
  Serial.print(payload.dcVolt);
  Serial.print(F(", Current(I):"));
  Serial.print(payload.dcVolt);
  Serial.print(F(". At "));
  Serial.println((uint32_t)payload.epoch);
}

void sendPayload(uint16_t toNodeId, float acVolt, float dcVolt, float current) {
  double epoch = (double)millis();
  payloadOut payload = { acVolt, dcVolt, current, epoch };
  RF24NetworkHeader header(/*to node*/ toNodeId);

  Serial.print(F("Sending to "));
  Serial.print(toNodeId, OCT);
  Serial.print(F(" data: ACV:"));
  Serial.print(payload.acVolt);
  Serial.print(F(", DCV:"));
  Serial.print(payload.dcVolt);
  Serial.print(F(", Current(I):"));
  Serial.print(payload.dcVolt);
  Serial.print(F(". At "));
  Serial.print((uint32_t)payload.epoch);
  Serial.println( network.write(header, &payload, sizeof(payload)) == 1 ? F("Send ok") : F("Send failed") );
}


void loop() {
  mesh.update();
  mesh.DHCP();

  if (network.available()) {
    readPayload();
  }

  /*
    if (millis() - displayTimer > 5000) {
    displayTimer = millis();
    Serial.println(" ");
    Serial.println(F("********Assigned Addresses********"));
    for (int i = 0; i < mesh.addrListTop; i++) {
      Serial.print(F("NodeId: "));
      Serial.print(mesh.addrList[i].nodeID);
      Serial.print(F(" RF24Network address: 0"));
      Serial.println(mesh.addrList[i].address, OCT);
    }
    Serial.println(F("**********************************"));
    }
  */
}
