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
#define THRES_WATT 20 // 20 watt max
#define TEST_MODE true // change to false if using sensor
const String infoStr[2] = {"NORMAL", "BERLEBIH"}; // 0: NORMAL, 1: BERLEBIH

float valDaya, newValDaya;
uint8_t valInfo;

struct Payload_to_server {
  float valDaya, valInfo, nid;
};

/**/

/******************************************************************************************** Functions goes below **/
// Check timer
const uint16_t tInterval = 2000;
unsigned long tStart = 0;
bool timerDb = false;
bool checkTimerDb() {
  unsigned long now = millis(); // get timer value
  if ( now - tStart >= tInterval  ) // check to see if it is time to transmit based on set interval
  {
    tStart = now; //reset start time of timer
    return true;
  }
  else return false;
}

const uint8_t sInterval = 125;
unsigned long sStart = 0;
bool timerSensor = false;
bool checkTimerSensor() {
  unsigned long now = millis(); // get timer value
  if ( now - sStart >= sInterval  ) // check to see if it is time to transmit based on set interval
  {
    sStart = now; //reset start time of timer
    return true;
  }
  else return false;
}

// Send payload using Payload_to_server
void sendPayload( float valDaya, int valInfo) {
  RF24NetworkHeader header;
  Payload_to_server payload = { valDaya, (float)valInfo, (float)NODE_ID };
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


void setRelayBeban() {
  //.....
}

void readSensorData() {
  if (TEST_MODE) {
    newValDaya = random(123);
  } else {
    //newValDaya = PowerMeter1.getValue();
  }
}

void updateDb() {
  if (valDaya != newValDaya) {
    valDaya = newValDaya;

    valInfo = valDaya > THRES_WATT ? 1 : 0;

    sprintln(F("\n-sys-"));
    sprint(F("Daya: ")); sprintln(newValDaya);
    sprint(F("Info: ")); sprintln(infoStr[valInfo]);

    // Upload data
    sendPayload( valDaya, valInfo );
  }
}

/**/

/******************************************************************************************** setup **/
void setup() {
  Serial.begin(115200);
  SPI.begin();
  if (!TEST_MODE) randomSeed(analogRead(A0));

  sprintln(F("-=:: OTOBUS ::=-"));
  sprint(F("NODE: ")); sprintln(NODE_ID);

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
  mesh.begin(99, RF24_1MBPS, 10000);

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
  sprintln(F("-=:: Setup done ::=-\n"));
}

/******************************************************************************************** main loop **/
void loop() {
  // update mesh network
  meshUpdate();
  if (timerSensor) readSensorData();
  timerSensor = checkTimerSensor();

  if (timerDb) updateDb();
  timerDb = checkTimerDb();
}
/** end **/
