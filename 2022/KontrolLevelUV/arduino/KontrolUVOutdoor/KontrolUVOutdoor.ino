/******************************************************************************************** Includes **/
#include <SPI.h>
#include <Wire.h>
//#include <printf.h> // include for radio.printDetails()
#include <RF24.h>
#include <RF24Network.h>
#include <RF24Mesh.h>
#include <Adafruit_VEML6070.h>
#include <hp_BH1750.h>
/**/

#define sprint Serial.print
#define sprintln Serial.println

/******************************************************************************************** NRF Radio setup **/
RF24 radio(9, 10, 8000000); //CE, CSN, 8MHz SPI
RF24Network network(radio);
RF24Mesh mesh(radio, network);
#define NODE_ID 2 // set node address(1-255)
/**/

/******************************************************************************************** VEML/Lux setup **/
Adafruit_VEML6070 UVMeter = Adafruit_VEML6070();
float uvL, newUvL;
float uvI, newUvI;
int uvA, newUvA;

hp_BH1750 LuxMeter;
float luxOutdoor, newLuxOutdoor;
/**/

/******************************************************************************************** Others/Variables **/
#define TEST_MODE true // change to false if using sensor
//#define HEADER_SERVER 'S'
#define HEADER_OUTDOOR 'O'
//#define HEADER_INDOOR 'I'
unsigned long tStart = 0;
unsigned long tInterval = 2000;
bool timer = false;

float uvLamp, ledLamp, newUvLamp, newLedLamp;

struct Payload_to_server {
  float uvOutdoor, luxOutdoor;
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
void sendPayload( float uvOutdoor, float luxOutdoor ) {
  RF24NetworkHeader header;
  Payload_to_server payload = { uvOutdoor, luxOutdoor };
  // Send an HEADER_OUTDOOR type message containing the current millis()
  if (!mesh.write(&payload, HEADER_OUTDOOR, sizeof(payload))) {
    // If a write fails, check connectivity to the mesh network
    if ( !mesh.checkConnection() ) {
      //refresh the network address
      sprintln(F("|#Renewing Address"));
      mesh.renewAddress(10000);
      if (!mesh.write(&payload, HEADER_OUTDOOR, sizeof(payload))) {
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

// set/control UV Lamp
void setUVLamp() {
  if (uvLamp != newUvLamp) {
    uvLamp = newUvLamp;

    // code to set uv lamp
    //.....
  }
}

// set/control LED Lamp
void setLEDLamp() {
  if (ledLamp != newLedLamp) {
    ledLamp = newLedLamp;

    // code to set led lamp
    //.....
  }
}

void readSensorsData() {
  if (TEST_MODE) {
    newUvL = random(12);
    newUvI = (newUvL * 0.025);
    newUvA = 100 + (newUvL * 25);
    newLuxOutdoor = random(100000) / 10.0;
  } else {
    newUvL = UVMeter.readUV();
    newUvI = (newUvL * 0.025);
    newUvA = 100 + (newUvL * 25);
    if (newUvL == 0)newUvA = 0;
    newLuxOutdoor = LuxMeter.getLux();
  }
}
/**/

/******************************************************************************************** setup **/
void setup() {
  Serial.begin(115200);
  SPI.begin();
  if (!TEST_MODE) randomSeed(analogRead(A0));

  sprintln(F("-=:: Outdoor Node ::=-\n"));

  delay(500);
  /*  begin() longer time is more precise
      -- integration time constant --
         VEML6070_HALF_T ~62.5ms
         VEML6070_1_T ~125ms
         VEML6070_2_T ~250ms
         VEML6070_4_T ~500ms
      -- end --
  */
  sprintln(F("VEML init..."));
  // pass in the integration time constant
  if (!TEST_MODE) UVMeter.begin(VEML6070_2_T);

  sprintln(F("BH1750 init..."));
  if (!TEST_MODE) LuxMeter.begin(BH1750_TO_GROUND);
  if (!TEST_MODE) LuxMeter.start();

  /* Radio config */
  sprintln(F("NRF24 init..."));

  /* Set a unique nodeID for this node. (Set before mesh.begin) */
  mesh.setNodeID(NODE_ID);

  /* mesh.begin();
    channel: channel The radio channel (1-127) default:97
    data rate: How fast data transfer on the air
      RF24_1MBPS (default)
      RF24_2MBPS
      RF24_250KBPS
    timout: timeout How long to attempOutdoort address renewal in milliseconds default: 7500ms
  */
  mesh.begin(111, RF24_1MBPS, 10000);

  /* Power Amplifier / booster config
     add 10uF capacitor between vcc-gnd to stabilize/boost power if problem occur
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

  delay(500);
  sprintln(F("\n-=:: Setup done ::=-\n"));
}

/******************************************************************************************** main loop **/
void loop() {
  // update mesh network
  meshUpdate();

  // set lamps
  setUVLamp();
  setLEDLamp();

  // Sensor readings
  readSensorsData();

  if (timer) {
    if (uvL != newUvL || luxOutdoor != newLuxOutdoor) {
      sprintln(F("-sys-"));

      // UV reading
      sprint(F("UV:"));
      sprint(F(" level: ")); sprint(newUvL);
      sprint(F(" - intensity: ")); sprint(newUvI);
      sprint(F(" - lambda: ")); sprint(newUvA); sprintln(F("nm"));

      // Lux reading
      sprint(F("Lux: ")); sprintln(newLuxOutdoor);

      sprintln(F("--"));

      uvL = newUvL; // uv level
      uvI = newUvI; // uv intensity
      uvA = newUvA; // uv wave length / lambda
      luxOutdoor = newLuxOutdoor; // lux

      // Upload data
      sendPayload((float)uvL, (float)luxOutdoor);

    }
  }
  timer = checkTimer();
}
/** end **/
