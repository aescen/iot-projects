/********************************************************************************************Includes**/
#include <FirebaseESP8266.h>
#include <FirebaseESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <SPI.h>
#include <RF24.h>
#include <RF24Network.h>
/**/
/********************************************************************************************Firebase setup**/
#define FIREBASE_HOST "..."
#define FIREBASE_AUTH "..."
#define WIFI_SSID "..."
#define WIFI_PASSWORD "..."
//Define FirebaseESP8266 data object
FirebaseData firebaseData;
/**/
/********************************************************************************************Radio setup**/
//RF24 radio(0, 16); //CE,CSN using WeMos R1 pin layout
RF24 radio(4, 5); //CE,CSN using Lolin NodeMCU v3 pin layout
RF24Network network(radio);
const uint16_t thisNode = 00; //Address of the coordinator in Octal format
/**/
/********************************************************************************************Variables**/
float temp, pHAsam, flow;
int turbidity;
float newTemp = -1, newPH = -1, newFlow = -1;
int newTurbidity = -1;
struct Payload_sensors {
  float temp;
  float turbidity;
  float pHAsam;
  float flowml;
};
/**/
/********************************************************************************************Arduino setup**/
void setup() {
  Serial.begin(230400);
  SPI.begin();

  // connect to wifi.
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("Connected: ");
  Serial.println(WiFi.localIP());

  //Firebase initialization
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
  //Set database read timeout to 1 minute (max 15 minutes)
  Firebase.setReadTimeout(firebaseData, 1000 * 60);
  //tiny, small, medium, large and unlimited.
  //Size and its write timeout e.g. tiny (1s), small (10s), medium (30s) and large (60s).
  Firebase.setwriteSizeLimit(firebaseData, "tiny");
  Firebase.enableClassicRequest(firebaseData, true);

  //Radio initialization
  radio.begin();
  network.begin(110, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  Serial.println(F("Coordinator is online....."));
}
/**/
/********************************************************************************************Loop start**/
void loop() {
  network.update();
  if ( network.available() ) {
    RF24NetworkHeader header; //create header variable
    network.peek(header);
    if (header.from_node == 03) {
      if (header.type == 'P') {
        Payload_sensors payloadin; //create payloadin variable
        network.read(header, &payloadin, sizeof(payloadin));
        Serial.print(F("Node "));
        Serial.print(header.from_node);
        Serial.print(F(":"));
        Serial.print("Temp:");
        Serial.print(payloadin.temp);
        newTemp = (float)payloadin.temp;
        Serial.print("#Turbidity:");
        Serial.print(payloadin.turbidity);
        newTurbidity = (int)payloadin.turbidity;
        Serial.print("#PH:");
        Serial.print(payloadin.pHAsam);
        newPH = (float)payloadin.pHAsam;
        Serial.print("#Flow(ml):");
        Serial.print(payloadin.flowml);
        newFlow = (float)payloadin.flowml;

        if ((int)temp != (int)newTemp && (int)newTemp != -1) {
          temp = newTemp;
          if (!Firebase.setFloat(firebaseData, "/sensors/temp", temp)) {
            Serial.println("Firebase Error: " + firebaseData.errorReason());
          } else {
            Serial.println("#Update OK!");
          }
        } else {
          Serial.println();
        }
        if (turbidity != newTurbidity && newTurbidity != -1) {
          turbidity = newTurbidity;
          if (!Firebase.setInt(firebaseData, "/sensors/turbidity", turbidity)) {
            Serial.println("Firebase Error: " + firebaseData.errorReason());
          } else {
            Serial.println("#Update OK!");
          }
        } else {
          Serial.println();
        }
        if ((int)pHAsam != (int)newPH && (int)newPH != -1) {
          pHAsam = newPH;
          if (!Firebase.setFloat(firebaseData, "/sensors/ph", pHAsam)) {
            Serial.println("Firebase Error: " + firebaseData.errorReason());
          } else {
            Serial.println("#Update OK!");
          }
        } else {
          Serial.println();
        }
        if ((int)flow != (int)newFlow && (int)newFlow != -1) {
          flow = newFlow;
          if (!Firebase.setFloat(firebaseData, "/sensors/flow", flow)) {
            Serial.println("Firebase Error: " + firebaseData.errorReason());
          }
          else {
            Serial.println("#Update OK!");
          }
        } else {
          Serial.println();
        }
      }
    }
  }
}
/**/
