/******************************************************************************************** Includes **/
#include <SPI.h>
#include <Wire.h>
//#include <printf.h> // include for radio.printDetails()
#include <RF24.h>
#include <RF24Network.h>
#include <RF24Mesh.h>
/**/

#define sprint Serial.print
#define sprintln Serial.println

/******************************************************************************************** NRF Radio setup **/
RF24 radio(9, 10, 8000000); //CE, CSN, 8MHz SPI
RF24Network network(radio);
RF24Mesh mesh(radio, network);
#define NODE_ID 1 // set node address(1-255)
#define HEADER_NODE 'N'
#define HEADER_SERVER 'S'
/**/

/******************************************************************************************** Others/Variables **/
#define TEST_MODE true // change to false if using sensor
const unsigned long tInterval = 500;
unsigned long tStart = 0;
bool timer = false;

float valMoist, valPh;
float newValMoist, newValPh;

struct Payload_to_server {
  float valPh, valMoist, nodeId;
};

/**/

/******************************************************************************************** Functions goes below **/
// Check timer
bool checkTimer() {
  unsigned long now = millis(); // get timer value
  if ( now - tStart >= tInterval  ) // check to see if it is time to transmit based on set interval
  {
    tStart = now; //reset start time of timer
    return true;
  }
  else return false;
}

// Send payload using Payload_to_server
void sendPayload( float valPh, float valMoist) {
  RF24NetworkHeader header;
  Payload_to_server payload = { valPh, valMoist, (float)NODE_ID };
  if (!mesh.write(&payload, HEADER_NODE, sizeof(payload))) {
    // If a write fails, check connectivity to the mesh network
    if ( !mesh.checkConnection() ) {
      //refresh the network address
      sprintln(F("|#Renewing Address"));
      mesh.renewAddress(10000);
      if (!mesh.write(&payload, HEADER_NODE, sizeof(payload))) {
        // If a write STILL fails, mesh network is error
        sprintln(F("|#Send fail, mesh network is error"));
      }
    } else {
      sprintln(F("|#Send fail, test OK"));
    }
  } /*else {
    sprint(F("|#Send OK|Assigned node:"));
    sprintln(mesh.mesh_address);
  }*/
}

// mesh update using Payload_in
void meshUpdate() {
  mesh.update();
  //...
}

void readSensorData() {
  if (TEST_MODE) {
    newValPh = random(14);
    newValMoist = random(100);
  } else {
    //
  }
}

void updateDb() {
  if ( valPh != newValPh || valMoist != newValMoist) {
    valPh = newValPh;
    valMoist = newValMoist;

    sprintln(F("\n-sys-"));
    sprint(F("PH: ")); sprintln(valPh);
    sprint(F("Moist: ")); sprintln(valMoist);

    // Upload data
    sendPayload( valPh, valMoist );
  }
}

/**/

/******************************************************************************************** setup **/
void setup() {
  Serial.begin(115200);
  SPI.begin();
  if (!TEST_MODE) randomSeed(analogRead(A0));

  sprintln(F("-=:: PANTAU PERKEBUNAN JERUK ::=-\n"));
  sprintln(F("-=:: NODE MONITORING ::=-\n"));

  delay(500);

  /* Radio config */
  sprintln(F("NRF24 init..."));

  /* Set a unique NODE_ID for this node. (Set before mesh.begin) */
  mesh.setNodeID(NODE_ID);

  /* mesh begin
    channel: channel The radio channel (1-127) default:97
    data rate: How fast data transfer on the air
      RF24_1MBPS (default)
      RF24_2MBPS
      RF24_250KBPS
    timout: timeout How long to attempt address renewal in milliseconds default: 7500ms
  */
  mesh.begin(111, RF24_1MBPS, 10000);

  /* Power Amplifier / booster config
     add 10uF capacitor between vcc-gnd to stabilize/boost power if problem occur(unable to configure device)
     NRF24L01 min to max: -18dBm, -12dBm, -6dBm and 0dBm
     RF24_PA_MIN
     RF24_PA_LOW
     RF24_PA_HIGH
     RF24_PA_MAX (default)
  */
  radio.setPALevel(RF24_PA_LOW);

  /* number, delay: delay (0-15) is multiple of 250us (max 4ms) default 5, 15 */
  radio.setRetries(2, 8);

  /* CRC Length.  How big (if any) of a CRC is included.
    RF24_CRC_DISABLED
    RF24_CRC_8
    RF24_CRC_16 (default)
  */
  //radio.setCRCLength(RF24_CRC_8);

  /* print details to stdout */
  //radio.printDetails();

  delay(500);
  sprintln(F("\n-=:: Setup done ::=-\n"));
}

/******************************************************************************************** main loop **/
void loop() {
  // update mesh network
  meshUpdate();

  if (timer) {
    readSensorData();
    updateDb();
  }
  timer = checkTimer();
}
/** end **/
