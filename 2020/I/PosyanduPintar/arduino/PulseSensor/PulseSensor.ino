#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
#include <RFID.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#define USE_ARDUINO_INTERRUPTS true // Set-up low-level interrupts for most acurate BPM math.
#include <PulseSensorPlayground.h> // Includes the PulseSensorPlayground Library.
//#include<LiquidCrystal.h>
//LiquidCrystal lcd(7, 6, 5, 4, 3, 2);

const int PulseWire = 0; // PulseSensor PURPLE WIRE connected to ANALOG PIN 0
const int LED13 = 13; // The on-board Arduino LED, close to PIN 13.
int Threshold = 550; // Determine which Signal to "count as a beat" and which to ignore.

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
PulseSensorPlayground pulseSensor;

#define SS_PIN 10
#define RST_PIN 9
RFID rfid(SS_PIN, RST_PIN);

RF24 radio(7, 8); //CE,CSN
RF24Network network(radio);
const uint16_t rXNode = 00; //Address of the coordinator in Octal format
const uint16_t thisNode = 02; //Address of this node in Octal format

unsigned long tStart = 0; //For interval
unsigned long tInterval = 2000; //For interval

int cID[5];
int cards[][5] = {
  {128, 167, 23, 53, 5}, //Adit
  {4, 57, 111, 212, 134}, //Reza
  {51, 174, 91, 143, 73} //Tyas
};

struct Payload_out {
  float cID1; float cID2; float cID3; float cID4; float cID5; float TB; float BB;
};

void setup() {
  Serial.begin(115200);
  mlx.begin();
  Serial.println("Adafruit MLX90614 init");
  pulseSensor.analogInput(PulseWire);
  pulseSensor.blinkOnPulse(LED13); //auto-magically blink Arduino's LED with heartbeat.
  pulseSensor.setThreshold(Threshold);
  if (pulseSensor.begin()) {
    Serial.println("pulseSensor Object init"); //This prints one time at Arduino power-up, or on Arduino reset.
    //lcd.setCursor(0, 0);
    //lcd.print(" Heart Rate Monitor");
  }
  radio.begin();
  network.begin(90, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_2MBPS);
  radio.stopListening();
  Serial.println(F("Network begin"));

  rfid.init(); Serial.println(F("Initializing RFID"));
  Serial.println(F("Setup done..."));

}

void loop() {
  while (rfid.isCard()) {
    while (rfid.readCardSerial()) {
      for (int x = 0; x < sizeof(cards); x++) {
        bool access;
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
          float tempA = mlx.readAmbientTempC();
          float tempO = mlx.readObjectTempC();
          int myBPM = pulseSensor.getBeatsPerMinute(); // Calls function on our pulseSensor object that returns BPM as an "int".
          if (checkTimer()) {
            Serial.print("BPM: "); // Print phrase "BPM: "
            Serial.print(myBPM); // Print the value inside of myBPM.
            float tempA = mlx.readAmbientTempC();
            float tempO = mlx.readObjectTempC();
            Serial.print("\tAmbient = "); Serial.print(tempA);
            Serial.print("*C\tObject = "); Serial.print(tempO); Serial.print("*C");
            sendPayload((float)cID[0], (float)cID[1], (float)cID[2], (float)cID[3], (float)cID[4], myBPM, tempA); //Send data
          }
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
  radio.stopListening();
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
