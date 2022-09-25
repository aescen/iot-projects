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
#define NODE_ID 2 // set node address(1-255)
#define HEADER_NODE 'N'
#define HEADER_SERVER 'S'
/**/

/******************************************************************************************** Others/Variables **/
#define RELAY_VITAMIN_PIN 3
#define RELAY_WATER_PIN 3
#define TEST_MODE true // change to false if using sensor
const unsigned long tInterval = 500;
unsigned long tStart = 0;
bool timer = false;

int valRelaySpray, newValRelaySpray;

struct Payload_in {
  float relaySpray;
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

// mesh update using Payload_in
void meshUpdate() {
  mesh.update();

  if (network.available()) {
    RF24NetworkHeader header; network.peek(header);
    if (header.type == HEADER_SERVER) {
      Payload_in payload;
      network.read(header, &payload, sizeof(payload));

      sprintln(F("-received-"));

      //data
      sprint(F("Relay spray: ")); sprintln((int) payload.relaySpray);

      sprintln(F("--"));

      // process data
      newValRelaySpray = (int) payload.relaySpray;
    } else {
      network.read(header, 0, 0); sprint(F("Unknown header type")); sprintln(header.type);
    }
  }
}

/**/

/******************************************************************************************** setup **/
void setup() {
  Serial.begin(115200);
  SPI.begin();
  if (!TEST_MODE) randomSeed(analogRead(A0));

  sprintln(F("-=:: PANTAU PERKEBUNAN JERUK ::=-\n"));
  sprintln(F("-=:: NODE SEMPROT ::=-\n"));

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
    if (valRelaySpray != newValRelaySpray) {
      valRelaySpray = newValRelaySpray;

      //off
      if (valRelaySpray == 0) digitalWrite(RELAY_VITAMIN_PIN, HIGH);
      if (valRelaySpray == 0) digitalWrite(RELAY_WATER_PIN, HIGH);
      //on
      if (valRelaySpray == 1) digitalWrite(RELAY_VITAMIN_PIN, LOW);
      if (valRelaySpray == 2) digitalWrite(RELAY_WATER_PIN, LOW);
    }
  }
  timer = checkTimer();
}
/** end **/
