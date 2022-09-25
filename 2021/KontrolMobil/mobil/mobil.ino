#include <WiFi.h>
#include <FirebaseESP32.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include "DHTesp.h"
#include "EEPROM.h"

#define FIREBASE_HOST "" //project database url
#define FIREBASE_AUTH "" //database secret
#define WIFI_SSID "TEST"
#define WIFI_PASSWORD "123gogogo"

#define dhtPin 26 // DHT
#define ESPADC 4096   //the esp Analog Digital Convertion value
#define ESPVOLTAGE 5000 //the esp voltage supply value
const int relay1 = 15;
const int relay2 = 4;
const int relay3 = 16;

float suhu, Arus, Tegangan, Daya;
String myString;
FirebaseData firebaseData;
DHTesp dht;

void sendFB(float suhu, float Arus, float Tegangan, float Daya) {
  // set string value
  String packet = "";
  packet = ( Firebase.setFloat(firebaseData, "MobilIlham/Suhu", suhu) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  //Serial.println(packet);
  packet = ( Firebase.setFloat(firebaseData, "MobilIlham/Arus", Arus) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  //Serial.println(packet);
  packet = ( Firebase.setFloat(firebaseData, "MobilIlham/Tegangan", Tegangan) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  //Serial.println(packet);
  packet = ( Firebase.setFloat(firebaseData, "MobilIlham/Daya", Daya) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  //Serial.println(packet);
  // handle error
}

/* @note If the type of payload returned from the server is not Boolean,
   the target variable's value will be false.
*/
bool getRelayMesin() {
  String path = "/kong/kontrol/relayMesin";
  if (Firebase.getBool(firebaseData, path)) {
    return firebaseData.boolData();
  } else {
    Serial.println("FAILED!");
    Serial.println(path);
    return false;
  }
}

void setup() {
  Serial.begin(115200);                                                                                 // start serial port
  EEPROM.begin(32);//needed to permit storage of calibration value in eeprom
  uint32_t currentFrequency;
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  pinMode(relay3, OUTPUT);
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
  digitalWrite(relay3, HIGH);
  Serial.begin(115200);
  // Wait until serial port is opened
  while (!Serial) {
    delay(10);
  }

  dht.setup(dhtPin, DHTesp::DHT11);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);                                     //try to connect with wifi
  Serial.print("Connecting to ");
  Serial.print(WIFI_SSID);
  Serial.println("");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("Connected to ");
  Serial.println(WIFI_SSID);
  Serial.print("IP Address is : ");
  Serial.println(WiFi.localIP());                                            //print local IP address

  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
  //Set database read timeout to 1 minute (max 15 minutes)
  Firebase.setReadTimeout(firebaseData, 1000 * 60);
  //tiny, small, medium, large and unlimited.
  //Size and its write timeout e.g. tiny (1s), small (10s), medium (30s) and large (60s).
  Firebase.setwriteSizeLimit(firebaseData, "small");
  Firebase.setFloatDigits(2);
  Firebase.setDoubleDigits(6);
  Serial.println("Siap...");
}

bool relayMesinTmp = false;
void loop() {
  //suhu = dht.getTemperature();
  bool relayMesin = getRelayMesin();
  if (relayMesinTmp != relayMesin) {
    relayMesinTmp = relayMesin;
    if (relayMesin) {
      digitalWrite(relay1, LOW);
      Serial.println("ACC Terhubung");
      delay(1000);
      digitalWrite(relay2, LOW);
      Serial.println("ON Menyala");
      delay(1000);
      digitalWrite(relay3, LOW);
      delay(1000);
      digitalWrite(relay3, HIGH);
      delay(10000);
      Serial.println("Done.");
    } else {
      digitalWrite(relay2, HIGH);
      Serial.println("Mobil Mati");
      delay(500);
      digitalWrite(relay1, HIGH);
      Serial.println("ACC OFF");
      delay(500);
      Serial.println("Done.");
    }
  }

  delay(500);
}
