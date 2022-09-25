#include <Wire.h>
#include <RF24.h>
#include <RF24Network.h>
#include <SPI.h>
#include <printf.h>

int measurePin = A0; /*Connect dust sensor to Arduino A0 pin */
int ledPower = 2;   /*Connect 3 led driver pins of dust sensor to Arduino D2 */

int samplingTime = 280;
int deltaTime = 40;
int sleepTime = 9680;

float voMeasured = 0;
float calcVoltage = 0;
float dustDensity = 0;
int MQSensor = A1;
int irPin1 = 3;
int irPin2 = 4;
int count = 0;
boolean state1 = true;
boolean state2 = true;
boolean insideState = false;
boolean outsideIr = false;
boolean isPeopleExiting = false;
int i = 1;

RF24 radio(7, 8); /* CE, CSN */
RF24Network network(radio);
const uint16_t masterNode = 00;
const uint16_t nodeId = 01;

struct Payload_out {
  float ppm;
  float dusty;
  uint16_t jumlah;
  uint16_t dataId;
};

void sendPayload( const float ppm, const float dusty, const uint16_t jumlah, const uint16_t id = nodeId );
void sendPayload( const float ppm, const float dusty, const uint16_t jumlah, const uint16_t id ) {
  RF24NetworkHeader header(masterNode, '1');
  Payload_out payload = { ppm, dusty, jumlah, id };
  if ( !network.write(header, &payload, sizeof(payload), masterNode) ) {
    Serial.println(F("|#Send fail."));
  } else {
    Serial.print(F("|#Send OK."));
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
  pinMode(irPin1, INPUT);
  pinMode(irPin2, INPUT);
  pinMode(ledPower, OUTPUT);

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

long RL = 1000; /* 1000 Ohm */
long Ro = 830; /* 830 ohm ( SILAHKAN DISESUAIKAN) */

void density() {
  digitalWrite(ledPower, LOW); /* power on the LED */
  delayMicroseconds(samplingTime);

  voMeasured = analogRead(measurePin); /* read the dust value */

  delayMicroseconds(deltaTime);
  digitalWrite(ledPower, HIGH); /* turn the LED off */
  delayMicroseconds(sleepTime);

  /* 0 - 5V mapped to 0 - 1023 integer values */
  /* recover voltage */
  calcVoltage = voMeasured * (5.0 / 1024.0);
  dustDensity = 170 * calcVoltage - 0.1;

  Serial.print("Kadar Debu= ");
  Serial.print(dustDensity); /* unit: ug/m3 */
  Serial.println("  ug/m3");
}

void loop() {
  network.update();

  if (!digitalRead(irPin1) && i == 1 && state1) {
    outsideIr = true;
    delay(100);
    i++;
    state1 = false;
  }

  if (!digitalRead(irPin2) && i == 2 &&   state2) {
    Serial.println("Masuk Kedalam Ruangan");
    outsideIr = true;
    delay(100);
    i = 1 ;
    count++;
    Serial.print("Jumlah orang dalam ruangan: ");
    Serial.println(count);
    state2 = false;
    int sensorvalue = analogRead(MQSensor); /* membaca nilai ADC dari sensor */
    float VRL = sensorvalue * 5.00 / 1024; /* mengubah nilai ADC ( 0 - 1023 ) menjadi nilai voltase ( 0 - 5.00 volt ) */
    float Rs = ( 5.00 * RL / VRL ) - RL;
    float ppm = 100 * pow(Rs / Ro, -1.53); /* ppm = 100 * ((rs/ro)^-1.53); */
    Serial.print("CO : ");
    Serial.print(ppm);
    Serial.println(" ppm");
    density();
    if (count < 0 ) count = 0;
    sendPayload(ppm, dustDensity, count);
  }

  if (!digitalRead(irPin2) && i == 1 && state2 ) {
    outsideIr = true;
    delay(100);
    i = 2 ;
    state2 = false;
  }

  if (!digitalRead(irPin1) && i == 2 && state1 ) {
    Serial.println("Keluar Ruangan");
    outsideIr = true;
    delay(100);
    count--;
    if (count < 0 ) count = 0;
    Serial.print("Jumlah orang dalam ruangan: ");
    Serial.println(count);
    i = 1;
    state1 = false;
    int sensorvalue = analogRead(MQSensor); /* membaca nilai ADC dari sensor */
    float VRL = sensorvalue * 5.00 / 1024; /* mengubah nilai ADC ( 0 - 1023 ) menjadi nilai voltase ( 0 - 5.00 volt ) */
    float Rs = ( 5.00 * RL / VRL ) - RL;
    float ppm = 100 * pow(Rs / Ro, -1.53); /* ppm = 100 * ((rs/ro)^-1.53); */
    Serial.print("CO : ");
    Serial.print(ppm);
    Serial.println(" ppm");
    density();
    sendPayload(ppm, dustDensity, count);
  }

  if (digitalRead(irPin1)) {
    state1 = true;
  }

  if (digitalRead(irPin2)) {
    state2 = true;
  }

}
