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
/**/

/******************************************************************************************** Others/Variables **/
#define THRES_TEGANGAN_PENUH 12.35
#define THRES_ARUS_BERLEBIH 2.5
#define TEST_MODE true // change to false if using sensor
unsigned long tStart = 0;
unsigned long tInterval = 2000;
bool timer = false;

float valArus1, valArus2, valTegangan, newValArus1, newValArus2, newValTegangan;
uint8_t valRelay1, valRelay2, valBaterai, valOvercharged;

struct Payload_to_server {
  float valArus1, valArus2, valTegangan, valBaterai, valOvercharged, valRelay1, valRelay2, nid;
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
void sendPayloadData( float valArus1, float valArus2, float valTegangan, uint8_t valBaterai, uint8_t valOvercharged, uint8_t valRelay1, uint8_t valRelay2) {
  RF24NetworkHeader header;
  Payload_to_server payload = { valArus1, valArus2, valTegangan, (float) valBaterai, (float) valOvercharged, (float) valRelay1, (float) valRelay2, (float) NODE_ID };
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
}

void updateRelays() {
  //if(valArus1 ...) {
  // valRelay1 = ;
  //} else {
  // valRelay1 = ;
  //}

  //...
  //valRelay2 = ;
}

void readSensorsData() {
  if (TEST_MODE) {
    newValArus1 = random(12);
    newValArus2 = random(12);
    newValTegangan = random(123);
  } else {
    //newValArus1 = CurrentMeter1.getValue();
    //newValArus2 = CurrentMeter2.getValue();
    //newValTegangan = VoltMeter.getValue();
    //newValDaya = PowerMeter.getValue();
  }


}
/**/

/******************************************************************************************** setup **/
void setup() {
  Serial.begin(115200);
  SPI.begin();
  if (TEST_MODE) randomSeed(analogRead(A0));

  sprintln(F("-=:: ENERGY-MAN NODE 1 ::=-\n"));

  delay(500);

  /* Radio config */
  sprintln(F("NRF24 init..."));

  /* Set a unique NODE_ID for this node. (Set before mesh.begin) */
  mesh.setNodeID(NODE_ID);
  if (!radio.begin()) {
    sprint("Radio hardware not responding!");
    while (true) delay(100);
  }

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
  radio.setPALevel(RF24_PA_HIGH);

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

  // Sensor readings
  readSensorsData();

  if (timer) {
    if (valArus1 != newValArus1 || valArus2 != newValArus2 || valTegangan != newValTegangan) {
      valArus1 = newValArus1;
      valArus2 = newValArus2;
      valTegangan = newValTegangan;

      valRelay1 = valArus1 > 0 ? 1 : 0 ;
      valRelay2 = valArus2 > 0 ? 1 : 0 ;
      updateRelays();

      bool isFull = valTegangan >= THRES_TEGANGAN_PENUH;
      bool isOvercharged = (valArus1 + valArus2) >= THRES_ARUS_BERLEBIH;
      valBaterai = isFull ? 1 : 0;
      valOvercharged = isOvercharged ? 1 : 0;

      sprint(F("Arus 1: ")); sprintln(newValArus1);
      sprint(F("Arus 2: ")); sprintln(newValArus2);
      sprint(F("Tegangan: ")); sprintln(newValTegangan);
      sprint(F("Baterai: ")); sprintln(valBaterai);
      sprint(F("Overcharge: ")); sprintln(valOvercharged);
      sprint(F("Relay 1: ")); sprintln(valRelay1); // panel
      sprint(F("Relay 2: ")); sprintln(valRelay2); // turbine

      // Upload data
      sendPayloadData(valArus1, valArus2, valTegangan, valBaterai, valOvercharged, valRelay1, valRelay2);
    }
  }
  timer = checkTimer();
}
/** end **/
