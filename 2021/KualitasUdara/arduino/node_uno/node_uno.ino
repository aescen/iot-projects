#include <Wire.h>
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
#include <printf.h>

const byte pinSensor = A0; /* mendefinisikan bahwa pin yang digunakan untuk membaca sensor adalah pin A0 */
const byte pinSensor2  = A1;

const uint16_t RL = 1000; /* 1000 ohm */
const uint16_t RO = 830; /* 830 ohm (SILAHKAN DISESUAIKAN) */

RF24 radio(7, 8); /* CE, CSN */
RF24Network network(radio);
const uint16_t masterNode = 00;
const uint16_t nodeId = 02;

struct Payload_out {
  float ppm2;
  float ppm3;
  float dummy;
  float dataId;
};

void sendPayload( const float ppm2, const float ppm3, const uint16_t id = 1 );
void sendPayload( const float ppm2, const float ppm3, const uint16_t id ) {
  RF24NetworkHeader header(masterNode, '2');
  Payload_out payload = { ppm2, ppm3, 0, (float)id };
  if ( !network.write(header, &payload, sizeof(payload), masterNode) ) {
    Serial.println(F("|#Send fail."));
  } else {
    Serial.println(F("|#Send OK."));
  }
}

uint32_t tTimer;
uint16_t processInterval = 5000;
bool theTime() {
  bool state = false;
  if ((millis() - tTimer) >= processInterval) {
    state = true;
    tTimer = millis();
  }
  return state;
}

void setup() {
  Serial.begin(115200);
  SPI.begin();
  printf_begin();

  Serial.println(F("nRF24 begin"));
  radio.begin();
  network.begin(2, nodeId);
  radio.setRetries(2, 2);
  radio.setAutoAck(true);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setCRCLength(RF24_CRC_8);
  Serial.print(F("Connected to the nRF24 network, node id: "));
  Serial.println(nodeId);
  radio.printDetails();
}


float ppm2, ppm3;
void loop() {
  network.update();
  if (theTime()) {
    /* membaca nilai ADC dari sensor */
    int sensorvalue = analogRead(pinSensor);
    int sensorvalue2 = analogRead(pinSensor2);

    /* mengubah nilai ADC ( 0 - 1023 ) menjadi nilai voltase ( 0 - 5.00 volt ) */
    /* ppm = 100 * ((Rs/ro)^-1.53); */
    float VRL = sensorvalue * 5.00 / 1024;
    float Rs = ( 5.00 * RL / VRL ) - RL;
    float ppm2tmp = 100 * pow(Rs / RO, -1.53);

    float VRL2 = sensorvalue2 * 5.00 / 1024;
    float Rs2 = ( 5.00 * RL / VRL2 ) - RL;
    float ppm3tmp = 100 * pow(Rs2 / RO, -1.53);

    if (ppm2 != ppm2tmp || ppm2 != ppm2tmp) {
      /* Kirim ke master node */
      ppm2 = ppm2tmp;
      ppm3 = ppm3tmp;
      sendPayload(ppm2, ppm3);

      /* Kirim ke serial */
      Serial.print("CO-2 : ");
      Serial.print(ppm2);
      Serial.println(" ppm");

      Serial.print("CO-3 : ");
      Serial.print(ppm3);
      Serial.println(" ppm");
    }
  }

}
