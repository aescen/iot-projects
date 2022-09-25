/********************************************************************************************Includes**/
#include <RF24.h>
#include <RF24Network.h>
#include <RF24Mesh.h>
#include <SPI.h>
#include <SharpIR.h>
/**/
/********************************************************************************************Radio setup**/
RF24 radio(7, 8); //CE,CSN
RF24Network network(radio);
RF24Mesh mesh(radio, network);
#define nodeId 1 // set node address(1-255)
/**/
/********************************************************************************************Variables**/
#define IRPin A1
#define model 20150
float soil, s; //Used to store voltage reading from soil moisture sensor
int tinggi_cm, t_cm;
unsigned long displayTimer = 0;
unsigned long tStart = 0; //For interval
unsigned long tInterval = 2000; //For interval
bool timer = false;
struct Payload_out {
  float soil;
  float tinggi;
  float systemNodeID;
};
SharpIR mySensor = SharpIR(IRPin, model);
/**/
/********************************************************************************************Arduino Setup**/
void setup() {
  Serial.begin(115200);
  SPI.begin();
  //Warming up adc
  burn8Readings(A0);
  soil, s = getSoil();
  tinggi_cm, t_cm = mySensor.distance();

  //Radio
  mesh.setNodeID(nodeId);
  //Connect to the mesh
  Serial.println(F("Mesh begin"));
  mesh.begin(97, RF24_1MBPS, 5000);
  radio.setPALevel(RF24_PA_MAX);
  Serial.println(F("Connected to the mesh network..."));
  Serial.print(F("Soil:"));
  Serial.print(soil);
  Serial.print(F(" %"));
  Serial.print(F("Tinggi benih: "));
  Serial.print(tinggi_cm);
  Serial.print(F(" cm"));
  sendPayload((float)soil, (float)tinggi_cm);
}
/**/
/********************************************************************************************Loop start**/
void loop() {
  mesh.update();
  if (timer) {
    t_cm = mySensor.distance();
    s = getSoil();
    if (s != soil || t_cm != tinggi_cm) {
      soil = s;
      tinggi_cm = t_cm;
      Serial.print(F("Soil:"));
      Serial.print(soil);
      Serial.print(F(" %"));
      Serial.print(F("Tinggi benih: "));
      Serial.print(tinggi_cm);
      Serial.print(F(" cm"));
      sendPayload((float)s, (float)t_cm);
    }
  }
  timer = checkTimer();

}
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
void sendPayload( float soil, float tinggi ) {
  float systemNodeID = (float)nodeId;
  RF24NetworkHeader header;
  Payload_out payload = { soil, tinggi, systemNodeID };
  // Send an 'M' type message containing the current millis()
  if (!mesh.write(&payload, 'M', sizeof(payload))) {
    // If a write fails, check connectivity to the mesh network
    if ( !mesh.checkConnection() ) {
      //refresh the network address
      Serial.println(F("|#Renewing Address"));
      mesh.renewAddress(10000);
      if (!mesh.write(&payload, 'M', sizeof(payload))) {
        // If a write STILL fails, mesh network is error
        Serial.println(F("|#Send fail, mesh network is error"));
      }
    } else {
      Serial.println(F("|#Send fail, test OK"));
    }
  } else {
    Serial.print(F("|#Send OK|Assigned node:"));
    Serial.println(mesh.mesh_address);
  }
}

//used to average multiple ADC values together
//This can help eliminate noise in measurements
float averageADCReadings(int aDCpin, int avgCount) {
  float aDCAvg = 0;
  for (int i = 0; i < avgCount; i++) {
    aDCAvg = aDCAvg + analogRead(aDCpin);
  }

  return (aDCAvg / avgCount);
}

//This function makes 8 ADC measurements but does nothing with them
//Since after a reference change the ADC can return bad readings. This function is used to get rid of the first
//8 readings to ensure next reading is accurate
void burn8Readings(int pin) {
  for (int i = 0; i < 8; i++) {
    analogRead(pin);
  }
}

int getSoil() {
  int data = (int)round(averageADCReadings(A0, 8));
  return data;
}
/**/
