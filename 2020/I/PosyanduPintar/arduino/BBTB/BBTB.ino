#include "HX711.h"
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
#include <RFID.h>

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

#define SS_PIN 10
#define RST_PIN 9
RFID rfid(SS_PIN, RST_PIN);

RF24 radio(7, 8); //CE,CSN
RF24Network network(radio);
const uint16_t rXNode = 00; //Address of the coordinator in Octal format
const uint16_t thisNode = 01; //Address of this node in Octal format

unsigned long tStart = 0; //For interval
unsigned long tInterval = 2000; //For interval
bool timer = false;

int cID[5];
int cards[][5] = {
  {128, 167, 23, 53, 5}, //Adit
  {4, 57, 111, 212, 134}, //Reza
  {51, 174, 91, 143, 73} //Tyas
};
bool access;

struct Payload_out {
  float cID1; float cID2; float cID3; float cID4; float cID5; float TB; float BB;
};

HX711 scale;
// defines pins numbers
const int trigPin = 4;
const int echoPin = 5;
// defines variables
long duration;
int distance;
void setup() {
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  Serial.begin(115200); // Starts the serial communication
  Serial.println("Initializing the scale");

  // Initialize library with data output pin, clock input pin and gain factor.
  // Channel selection is made by passing the appropriate gain:
  // - With a gain factor of 64 or 128, channel A is selected
  // - With a gain factor of 32, channel B is selected
  // By omitting the gain factor parameter, the library
  // default "128" (Channel A) is used here.
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

  Serial.println(F("Before setting up the scale:"));
  Serial.print(F("read: \t\t"));
  Serial.println(scale.read());      // print a raw reading from the ADC

  Serial.print(F("read average: \t\t"));
  Serial.println(scale.read_average(20));   // print the average of 20 readings from the ADC

  Serial.print(F("get value: \t\t"));
  Serial.println(scale.get_value(5));   // print the average of 5 readings from the ADC minus the tare weight (not set yet)

  Serial.print(F("get units: \t\t"));
  Serial.println(scale.get_units(5), 1);  // print the average of 5 readings from the ADC minus tare weight (not set) divided
  // by the SCALE parameter (not set yet)

  scale.set_scale(2280.f);                      // this value is obtained by calibrating the scale with known weights; see the README for details
  scale.tare();               // reset the scale to 0

  Serial.println(F("After setting up the scale:"));

  Serial.print(F("read: \t\t"));
  Serial.println(scale.read());                 // print a raw reading from the ADC

  Serial.print(F("read average: \t\t"));
  Serial.println(scale.read_average(20));       // print the average of 20 readings from the ADC

  Serial.print(F("get value: \t\t"));
  Serial.println(scale.get_value(5));   // print the average of 5 readings from the ADC minus the tare weight, set with tare()

  Serial.print(F("get units: \t\t"));
  Serial.println(scale.get_units(5), 1);        // print the average of 5 readings from the ADC minus tare weight, divided
  // by the SCALE parameter set with set_scale

  radio.begin();
  network.begin(90, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_2MBPS);
  Serial.println(F("Network begin"));


  rfid.init(); Serial.println(F("Initializing RFID"));
  Serial.println(F("Setup done..."));
}
void loop() {
  while (rfid.isCard()) {
    while (rfid.readCardSerial()) {
      for (int x = 0; x < sizeof(cards); x++) {
        for (int i = 0; i < sizeof(rfid.serNum); i++ ) {
          if (rfid.serNum[i] != cards[x][i]) {
            access = false;
            break;
          } else {
            cID[i] = rfid.serNum[i];
            access = true;
          }
        }
        while (access) {
          // loadcell
          //scale.power_up();              // put the ADC in idle mode
          // Clears the trigPin
          digitalWrite(trigPin, LOW);
          delayMicroseconds(2);
          // Sets the trigPin on HIGH state for 10 micro seconds
          digitalWrite(trigPin, HIGH);
          delayMicroseconds(10);
          digitalWrite(trigPin, LOW);
          // Reads the echoPin, returns the sound wave travel time in microseconds
          duration = pulseIn(echoPin, HIGH);
          // Calculating the distance
          distance = duration * 0.034 / 2;
          // ultrasonic
          float TB = abs(100 - distance);
          // loadcell
          float BB = abs(scale.get_units(10)); //10 reading, averaged
          // Prints the distance on the Serial Monitor
          String id = "ID:" + String(cID[0]) + " " + String(cID[1]) + " " + String(cID[2]) + " " + String(cID[3]) + " " + String(cID[4]);
          Serial.print(id);
          Serial.print(F(" - Tinggi Badan: "));
          Serial.print(TB);
          Serial.print(F(" cm - "));
          //Serial.print(scale.get_units(), 1);
          Serial.print("Berat:");
          Serial.print(BB, 1);
          // nrf
          if (checkTimer()) sendPayload((float)cID[0], (float)cID[1], (float)cID[2], (float)cID[3], (float)cID[4], TB, BB); //Send data
          // loadcell
          //scale.power_down();              // put the ADC in sleep mode
          if (!rfid.isCard()) break;
        }
      }
    }
  }
  rfid.halt();
}

//Send payload
void sendPayload( float cID1, float cID2, float cID3, float cID4, float cID5, float TB, float BB ) {
  RF24NetworkHeader header(rXNode);
  Payload_out payload = { cID1, cID2, cID3, cID4, cID5, TB, BB };
  bool ok = network.write(header, &payload, sizeof(payload));
  if ( ok ) {
    Serial.println(F(" #Send OK"));
  }
  else {
    //PIND |= (1 << LED_BUILTIN); //this toggles the status LED to show transmit failed
    Serial.println(F(" #Send failed!"));
  }
}

//Check timer
bool checkTimer() {
  unsigned long noW = millis(); //get timer value
  if ( noW - tStart >= tInterval  ) //check to see if it is time to transmit based on set interval
  {
    tStart = noW; //reset start time of timer
    return true;
  }
  else return false;
}
