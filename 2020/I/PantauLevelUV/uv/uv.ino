/********************************************************************************************Includes**/
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
#include <Wire.h>
#include "Adafruit_VEML6070.h"
#include "DHT.h"
#include <hp_BH1750.h>
/**/

/********************************************************************************************Radio setup**/
RF24 radio(9, 10); //CE,CSN
RF24Network network(radio);
const uint16_t rXNode = 00; //Address of the coordinator in Octal format
const uint16_t thisNode = 02; //Address of this node in Octal format, node address(1-255)
/**/

/********************************************************************************************DHT setup**/
#define DHTPIN 4     // what pin we're connected to
#define DHTTYPE DHT11   // DHT 11 
DHT dht(DHTPIN, DHTTYPE);
float h = -1.0;
float t = -1.0;
/**/

/********************************************************************************************VEML/UV/Lux setup**/
Adafruit_VEML6070 uv = Adafruit_VEML6070();
float uvL = -1;
float uvI = -1;
int uvP = -1;
hp_BH1750 BH1750;
float lux = -1;
/**/

/********************************************************************************************Others/Variables**/
#define F_CPU 16000000UL
int pinFan = 7;
bool fanRelay, lampRelay;
int pinLamp = 6;
unsigned long displayTimer = 0;
unsigned long tStart = 0; //For interval
unsigned long tInterval = 2000; //For interval
int fan = -1;
int lamp = -1;
bool timer = false;
struct Payload_out {
  float humid, temp, uvL, lux, fan, lamp;
};
/**/

/********************************************************************************************Functions goes below**/
//Check timer
bool checkTimer() {
  unsigned long now = millis(); //get timer value
  if ( now - tStart >= tInterval  ) //check to see if it is time to transmit based on set interval
  {
    tStart = now; //reset start time of timer
    return true;
  }
  else return false;
}

//Send payload
void sendPayload( float humid, float temp, float uvL, float lux, float fan, float lamp ) {
  radio.stopListening();
  RF24NetworkHeader header(rXNode);
  Payload_out payload = { humid, temp, uvL, lux, fan, lamp };
  if ( network.write(header, &payload, sizeof(payload)) ) {
    Serial.println(F(" #Send OK"));
  }
  else {
    //PIND |= (1 << LED_BUILTIN); //this toggles the status LED to show transmit failed
    Serial.println(F(" #Send failed!"));
  }
  radio.startListening();
}
/**/

void setup() {
  Serial.begin(115200);
  /*  begin() longer time is more precise
      VEML6070_HALF_T ~62.5ms
      VEML6070_1_T ~125ms
      VEML6070_2_T ~250ms
      VEML6070_4_T ~500ms
  */
  uv.begin(VEML6070_2_T);  // pass in the integration time constant
  BH1750.begin(BH1750_TO_GROUND);

  //Relays
  pinMode(pinFan, OUTPUT);// Relay on pin 7
  digitalWrite(pinFan, LOW);//Deactivate relay
  fanRelay = false;
  pinMode(pinLamp, OUTPUT);// Relay on pin 6
  digitalWrite(pinLamp, LOW);//Deactivate relay
  lampRelay = false;

  //Radio
  radio.begin();
  network.begin(90, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  Serial.println(F("UV Monitoring..."));
}


void loop() {
  network.update();
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensorUV)
  float nH = dht.readHumidity();
  float nT = dht.readTemperature();
  float nuvL = uv.readUV();
  float nuvI = (nuvL * 0.025);
  float nuvP = 100 + (nuvL * 25);
  if (nuvL == 0)nuvP = 0;
  float nLux;

  BH1750.start(); nLux = BH1750.getLux();

  if (timer) {
    // check if returns are valid, if they are NaN (not a number) then something went wrong!
    if (isnan(nT) || isnan(nH)) {
      Serial.println(F("Failed to read from DHT"));
      nT = 0; nH = 0;
    }
    else {
      if (h != nH || t != nT || uvL != nuvL || lux != nLux) {
        Serial.print(F("Humidity: ")); Serial.print(nH); Serial.print(F(" % - Temperature: ")); Serial.print(nT); Serial.println(F(" ˚C"));
        // UV & Luxreading
        Serial.print(F("     - UV light level: ")); Serial.print(nuvL); Serial.print(F(" - UV light intensity: ")); Serial.print(nuvI); Serial.print(F(" - UV light lambda: ")); Serial.print(nuvP); Serial.print(F(" - Lux level: ")); Serial.print(nLux);
        h = nH;
        t = nT;
        uvL = nuvL;
        uvI = nuvI;
        uvP = nuvP;
        lux = nLux;

        //relay 0 is fan, relay 1 is lamp
        //Relay fan
        if (t >= 31) { // Hot air, turn fan ON
          digitalWrite(pinFan, LOW); //Activate fan relay
          fanRelay = 1;
          fan = 1;
          Serial.print(F(" - Fan: ON"));
        }
        else if (t <= 30) { //Normal air, turn fan OFF
          digitalWrite(pinFan, HIGH); //Deactivate fan relay
          fanRelay = 0;
          fan = 0;
          Serial.print(F(" - Fan: OFF"));
        }
        else {
          fan = 2;
          Serial.print(F(" - Fan: null"));
          digitalWrite(pinFan, HIGH); //Deactivate fan relay
          fanRelay = -1;
        }

        //Relay lamp
        if (uvP >= 199 && uvP <= 399) { //turn lamp ON
          digitalWrite(pinLamp, LOW); //Activate lamp relay
          lampRelay = 1;
          lamp = 1;
          Serial.print(F(" - lamp: ON"));
        }
        else if (uvP <= 198 || uvP >= 400) { // turn lamp OFF
          digitalWrite(pinLamp, HIGH); //Deactivate lamp relay
          lampRelay = 0;
          lamp = 0;
          Serial.print(F(" - lamp: OFF"));
        }
        else {
          lamp = 2;
          Serial.print(F(" - lamp: null"));
          digitalWrite(pinLamp, HIGH); //Deactivate lamp relay
          lampRelay = -1;
        }

        // Upload data
        sendPayload((float)h, (float)t, (float)uvL, (float)lux, (float)fan, (float)lamp);
      }
    }
  }
  timer = checkTimer();
}
