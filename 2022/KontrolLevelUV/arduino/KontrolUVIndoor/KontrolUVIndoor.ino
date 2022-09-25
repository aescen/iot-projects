/******************************************************************************************** Includes **/
#include <SPI.h>
#include <Wire.h>
//#include <printf.h> // include for radio.printDetails()
#include <RF24.h>
#include <RF24Network.h>
#include <RF24Mesh.h>
#include <Adafruit_VEML6070.h>
#include <DHT.h>
#include <hp_BH1750.h>
/**/

#define sprint Serial.print
#define sprintln Serial.println

/******************************************************************************************** NRF Radio setup **/
RF24 radio(9, 10, 8000000); //CE, CSN, 8MHz SPI
RF24Network network(radio);
RF24Mesh mesh(radio, network);
#define NODE_ID 1 // set node address(1-255)
/**/

/******************************************************************************************** Power Meter setup **/
//PowerMeterSensor PowerMeter = PowerMeterSensor();
float powerUsage, newPowerUsage;
/**/

/******************************************************************************************** DHT setup **/
DHT Dht(4, DHT11); //pin, DHT type
float humidIndoor, newHumidIndoor;
float tempIndoor, newTempIndoor;
/**/

/******************************************************************************************** VEML/Lux setup **/
Adafruit_VEML6070 UVMeter = Adafruit_VEML6070();
float uvL, newUvL;
float uvI, newUvI;
int uvA, newUvA;

hp_BH1750 LuxMeter;
float luxIndoor, newLuxIndoor;
float luxOutdoor, newLuxOutdoor;
/**/

/******************************************************************************************** Others/Variables **/
#define TEST_SENSOR_MODE true // change to false if using sensor
#define TEST_RELAY_MODE true
#define HEADER_SERVER 'S'
//#define HEADER_Indoor 'O'
#define HEADER_INDOOR 'I'
//personCount = 1: relay 1 led 1,2
//personCount > 10: relay 2 led 3,4
//personCount = 0: relay 3 uv
#define PERSON_THRESH_RELAY_1 1
#define PERSON_THRESH_RELAY_2 10
#define PERSON_THRESH_RELAY_3 0
#define RELAY_1_PIN 8
#define RELAY_2_PIN 7
#define RELAY_3_PIN 6

bool relay1, relay2, relay3;

unsigned long tStart = 0;
const unsigned long tInterval = 2000;
bool timer = false;

int uvLamp, ledLamp, newUvLamp, newLedLamp;
int personCount, newPersonCount;

struct Payload_to_server {
  float humidIndoor, tempIndoor, uvIndoor, luxIndoor, powerUsage;
};

struct Payload_in {
  float luxOutdoor, uvOutdoor, ledLamp, uvLamp, personCount;
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
void sendPayload(  float humidIndoor, float tempIndoor, float uvIndoor, float luxIndoor, float powerUsage ) {
  RF24NetworkHeader header;
  Payload_to_server payload = { humidIndoor, tempIndoor, uvIndoor, luxIndoor, powerUsage };
  // Send an HEADER_INDOOR type message containing the current millis()
  if (!mesh.write(&payload, HEADER_INDOOR, sizeof(payload))) {
    // If a write fails, check connectivity to the mesh network
    if ( !mesh.checkConnection() ) {
      //refresh the network address
      sprintln(F("|#Renewing Address"));
      mesh.renewAddress(10000);
      if (!mesh.write(&payload, HEADER_INDOOR, sizeof(payload))) {
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

  if (network.available()) {
    RF24NetworkHeader header; network.peek(header);
    if (header.type == HEADER_SERVER) {
      Payload_in payload;
      network.read(header, &payload, sizeof(payload));

      sprintln(F("-received-"));

      //data
      sprint(F("Lux Outdoor: ")); sprint(payload.luxOutdoor);
      sprint(F(" - UV Outdoor: ")); sprintln(payload.uvOutdoor);
      sprint(F("LED: ")); sprint((int) payload.ledLamp);
      sprint(F(" - UV: ")); sprintln((int) payload.uvLamp);
      sprint(F("Person: ")); sprintln((int) payload.personCount);

      sprintln(F("--"));

      // process data
      newUvLamp = (int) payload.uvLamp;
      newLedLamp = (int) payload.ledLamp;
      newPersonCount = (int) payload.personCount;
      newLuxOutdoor = payload.luxOutdoor;
    } else {
      network.read(header, 0, 0); sprint(F("Unknown header type")); sprintln(header.type);
    }
  }
}

void setLamps() {
  relay1 = (personCount == PERSON_THRESH_RELAY_1);
  relay2 = (personCount >= PERSON_THRESH_RELAY_2);
  relay3 = (personCount == PERSON_THRESH_RELAY_3);
  setRelay(RELAY_1_PIN, relay1); //led
  setRelay(RELAY_2_PIN, relay2); //led
  setRelay(RELAY_3_PIN, relay3); //uv
}

void setRelay(int pin, bool state) {
  digitalWrite(pin, state);
  delay(5);
}

void readSensorsData() {
  if (TEST_SENSOR_MODE) {
    newHumidIndoor = random(500, 600) / 10.0;
    newTempIndoor = random(230, 270) / 10.0;
    newUvL = random(12);
    newUvI = (newUvL * 0.025);
    newUvA = 100 + (newUvL * 25);
    newLuxIndoor = random(100000) / 10.0;
    newPowerUsage = random(1000) / 10.0;
  } else {
    // Reading tempIndoorerature or humidIndoority takes about 250 milliseconds!
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    newHumidIndoor = Dht.readHumidity();
    newTempIndoor = Dht.readTemperature();
    if (isnan(newTempIndoor) || isnan(newHumidIndoor)) {
      sprintln(F("Failed to read from DHT"));
      // set value to last value
      newHumidIndoor = humidIndoor; newTempIndoor = tempIndoor;
    }

    newUvL = UVMeter.readUV();
    newUvI = (newUvL * 0.025);
    newUvA = 100 + (newUvL * 25);
    if (newUvL == 0) newUvA = 0;
    //newLuxIndoor = LuxMeter.getLux();
    //newPowerUsage = PowerMeter.getPower();
  }


}
/**/

/******************************************************************************************** setup **/
void setup() {
  pinMode(RELAY_1_PIN, OUTPUT);
  pinMode(RELAY_2_PIN, OUTPUT);
  pinMode(RELAY_3_PIN, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  if (!TEST_SENSOR_MODE) randomSeed(analogRead(A0));

  sprintln(F("-=:: Indoor Node ::=-\n"));

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
  if (!TEST_SENSOR_MODE) UVMeter.begin(VEML6070_2_T);

  sprintln(F("BH1750 init..."));
  if (!TEST_SENSOR_MODE) LuxMeter.begin(BH1750_TO_GROUND);
  if (!TEST_SENSOR_MODE) LuxMeter.start();

  if (!TEST_RELAY_MODE) {

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
  }

  delay(500);
  sprintln(F("\n-=:: Setup done ::=-\n"));
}

/******************************************************************************************** main loop **/
void loop() {
  // update mesh network
  if (!TEST_RELAY_MODE) meshUpdate();

  // set lamps
  if (TEST_RELAY_MODE) {
    personCount = 0;
    sprint(F("Person:")); sprintln(personCount);
    setLamps();
    delay(2000);

    personCount = 1;
    sprint(F("Person:")); sprintln(personCount);
    setLamps();
    delay(2000);

    personCount = 11;
    sprint(F("Person:")); sprintln(personCount);
    setLamps();
    delay(2000);
  }
  else setLamps();

  // Sensor readings
  readSensorsData();

  if (timer) {
    if (humidIndoor != newHumidIndoor || tempIndoor != newTempIndoor || uvL != newUvL || luxIndoor != newLuxIndoor || powerUsage != newPowerUsage) {
      sprintln(F("-sys-"));

      // DHT reading
      sprint(F("DHT:"));
      sprint(F(" humid: ")); sprint(newHumidIndoor); sprint(F("%"));
      sprint(F(" - temp: ")); sprint(newTempIndoor); sprintln(F("˚C"));

      // UV reading
      sprint(F("UV:"));
      sprint(F(" level: ")); sprint(newUvL);
      sprint(F(" - intensity: ")); sprint(newUvI);
      sprint(F(" - lambda: ")); sprint(newUvA); sprintln(F("nm"));

      // Lux reading
      sprint(F("Lux: ")); sprintln(newLuxIndoor);

      // Power usage reading
      sprint(F("Power usage: ")); sprintln(newPowerUsage);

      sprintln(F("--"));

      humidIndoor = newHumidIndoor; // humid
      tempIndoor = newTempIndoor; // temp
      uvL = newUvL; // uv level
      uvI = newUvI; // uv intensity
      uvA = newUvA; // uv wave length / lambda
      luxIndoor = newLuxIndoor; // lux
      powerUsage = newPowerUsage; //power usage

      // Upload data
      if (!TEST_RELAY_MODE) sendPayload((float)humidIndoor, (float)tempIndoor, uvL, luxIndoor, powerUsage);
    }
  }
  timer = checkTimer();
}
/** end **/
