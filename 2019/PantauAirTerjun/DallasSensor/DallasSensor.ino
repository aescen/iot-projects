/********************************************************************/
// First we include the libraries
#include <SPI.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <EEPROM.h> // to store last calibration value (blanco, Vclear)
#include <RF24.h>
#include <RF24Network.h>

/********************************************************************/
// Data wire is plugged into pin 2 on the Arduino
#define ONE_WIRE_BUS 3
int sensorValue = 0;
int pHValue = 0;
float voltage = 0.00;
float turbidity = 0;
float Tegangan = 0.00;
float pHAsam = 0.00;
float Vclear = 4.35; //x Output voltage to calibrate (with clear water).
float last = 0 ;

byte sensorInterrupt = 0;  // 0 = digital pin 2
byte sensorPin       = 2;

// The hall-effect flow sensor outputs approximately 4.5 pulses per second per
// litre/minute of flow.
float calibrationFactor = 4.5;

volatile byte Count;

float flowRateMinute;
unsigned int flowMilliLitre;
unsigned long totalMilliLitre;

unsigned long oldTime;


/********************************************************************/
// Setup a oneWire instance to communicate with any OneWire devices
// (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
/********************************************************************/
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);
/********************************************************************/
RF24 radio(7, 8); //CE,CSN
RF24Network network(radio);
const uint16_t rXNode = 00; //Address of the coordinator in Octal format
const uint16_t thisNode = 03; //Address of this node in Octal format
struct Payload_sensors {
  float temp; 
  float turbidity; 
  float pHAsam; 
  float flowml;
};
void setup(void)
{
  // start serial port
  Serial.begin(230400);
  Serial.println("Monitoring Tingkat Layaknya Wisata Air Terjun di Daerah Magetan");
  // Start up the library
  sensors.begin();
  pinMode(3, INPUT);
  digitalWrite(3, HIGH);

  Count        = 0;
  flowRateMinute    = 0.0;
  flowMilliLitre   = 0;
  totalMilliLitre  = 0;
  oldTime           = 0;
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);

  radio.begin();
  network.begin(110, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_HIGH);
  radio.setDataRate(RF24_1MBPS);
  Serial.println(F("Network initialized."));

}
void loop()
{
  int n = 30;
  sensorValue = analogRead(A2);
  for (int i = 1; i < n; i++) {
    sensorValue += analogRead(A2);
    delay(5);
  }
  voltage = sensorValue / n * (5.0 / 1024.0);
  turbidity = 100.00 - (voltage / Vclear) * 100.00;
  {
    int n = 30;
    pHValue = analogRead(A1);
    for (int i = 1; i < n; i++) {
      pHValue += analogRead(A1);
      delay(5);
    }
    // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
    Tegangan = ((pHValue * ((5.0 / 1024.0))));
    pHAsam = 8 - (Tegangan / 119.49);
    //float pHCalibration = -5.70*Tegangan;
  }
  // call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  /********************************************************************/
  //Serial.print(" Requesting temperatures...");
  sensors.requestTemperatures();
  //suhucalibration()=sensors.requestTemperatures()+1.8; // Send the command to get temperature readings
  //Serial.println("DONE");
  /********************************************************************/
  Serial.print(" ~ Temperature is: ");
  Serial.print(sensors.getTempCByIndex(0));// Why "byIndex"?
  // You can have more than one DS18B20 on the same bus.
  // 0 refers to the first IC on the wire
  Serial.print (" ~ Sensor Output (V):");
  Serial.print (voltage);
  Serial.print (" ~ Turbidity(%):");
  Serial.println (turbidity);
  Serial.print(" ~ pHCalibration:");
  Serial.println(pHAsam);
  {

    if ((millis() - oldTime) > 1000)   // Only process counters once per second
    {
      detachInterrupt(sensorInterrupt);
      flowRateMinute = ((1000.0 / (millis() - oldTime)) * Count) / calibrationFactor;
      oldTime = millis();
      flowMilliLitre = (flowRateMinute / 60) * 1000;
      totalMilliLitre += flowMilliLitre;

      if ( abs(last - flowMilliLitre) > 5 ) {
        last = flowMilliLitre ;

        //Serial.println("========================================================>");
        //Serial.println("================== Flow Meter Sensor ===================>");
        //Serial.print("Debit Air / Second :"); Serial.print(flowMilliLitre);Serial.println("mL/Sec");
        //Serial.print("Volume Air :"); Serial.print(totalMilliLitre);Serial.println("L");
        //Serial.println("========================================================>");
      }

      // Reset the pulse counter so we can start incrementing again
      Count = 0;

      // Enable the interrupt again now that we've finished sending output
      attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
    }
  }
  Serial.print(" Debit Air / Second(mL/Sec):");
  Serial.println(flowMilliLitre);
  sendPayload(sensors.getTempCByIndex(0), turbidity, pHAsam, flowMilliLitre);

  delay(1000);
}
void pulseCounter()
{
  // Increment the pulse counter
  Count++;
}

//Send payload
void sendPayload( float temp, float turbidity, float pHAsam, float flowMilliLitre ) {
  RF24NetworkHeader header(rXNode, 'P');
  Payload_sensors payloadout = { temp, turbidity, pHAsam, flowMilliLitre };
  if ( !network.write(header, &payloadout, sizeof(payloadout)) ) {
    // Retry
    if ( !network.write(header, &payloadout, sizeof(payloadout)) ) {
      PIND |= (1 << LED_BUILTIN); //this toggles the status LED at LED_BUILTIN to show transmit failed
      Serial.println(F("Send failed"));
    } else {
      delay(100);
      Serial.println(F("#Send OK"));
    }
  } else {
    delay(100);
    Serial.println(F("#Send OK"));
  }
}
