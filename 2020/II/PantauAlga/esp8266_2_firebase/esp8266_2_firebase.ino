/********************************************************************************************Includes**/
#include "FirebaseESP8266.h"
#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <TimeLib.h>
/**/
/********************************************************************************************Firebase setup**/
#define FIREBASE_HOST "..." //project database url
#define FIREBASE_AUTH ""..." //database secret
#define WIFI_SSID ""..."
#define WIFI_PASSWORD ""..."
//Define FirebaseESP8266 data object
FirebaseData firebaseData;
//data
#define servoPath "/jtd/alga/data/servo"
#define relayPath "/jtd/alga/data/relay"
#define phPath    "/jtd/alga/data/ph"
#define moistPath "/jtd/alga/data/moist"
//logs
#define servoLogsPath "/jtd/alga/logs/servo"
#define relayLogsPath "/jtd/alga/logs/relay"
#define phLogsPath    "/jtd/alga/logs/ph"
#define moistLogsPath "/jtd/alga/logs/moist"
/**/
/********************************************************************************************NTP setup**/
// NTP Servers:
IPAddress timeServer(202, 65, 114, 202); //ntp.citra.net.id
const int timeZone = 0;
WiFiUDP Udp;
unsigned int localPort = 8888;  // local port to listen for UDP packets
unsigned long epoch;
unsigned long dataSync;
unsigned long logsSync;
/**/
/********************************************************************************************Functions**/
/*-------- Send data code ----------*/
void ESPSendData(int data1 = 0, int data2 = 0, float data3 = 0.0, float data4 = 0.0, int type = 1, bool printSerial = false) {
  String packet = "";
  if (type == 1) {
    packet = ( Firebase.setInt(firebaseData, servoPath, data1) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
    (!printSerial) ? : Serial.println(packet);
    packet = ( Firebase.setInt(firebaseData, relayPath, data2) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
    (!printSerial) ?  : Serial.println(packet);
    packet = ( Firebase.setFloat(firebaseData, phPath, data3) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
    (!printSerial) ?  : Serial.println(packet);
    packet = ( Firebase.setFloat(firebaseData, moistPath, data4) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
    (!printSerial) ?  : Serial.println(packet);
  }
  else if (type == 2) {
    //sync epoch
    setSyncProvider(getNtpTime);
    //arrange paths
    //String e = 1579935586;
    //String newPath1 = servoLogsPath + "/" + e;
    //String newPath2 = relayLogsPath + "/" + e;
    //String newPath3 = phLogsPath + "/" + e;
    //String newPath4 = moistLogsPath + "/" + e;
    String newPath1 = (String)servoLogsPath + "/" + String(epoch);
    String newPath2 = (String)relayLogsPath + "/" + String(epoch);
    String newPath3 = (String)phLogsPath + "/" + String(epoch);
    String newPath4 = (String)moistLogsPath + "/" + String(epoch);
    packet = ( Firebase.setInt(firebaseData, newPath1, data1) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
    (!printSerial) ?  : Serial.println(packet);
    packet = ( Firebase.setInt(firebaseData, newPath2, data2) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
    (!printSerial) ?  : Serial.println(packet);
    packet = ( Firebase.setFloat(firebaseData, newPath3, data3) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
    (!printSerial) ?  : Serial.println(packet);
    packet = ( Firebase.setFloat(firebaseData, newPath4, data4) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
    (!printSerial) ?  : Serial.println(packet);
  }
}

/*-------- NTP code ----------*/
const int NTP_PACKET_SIZE = 48; // NTP time is in the first 48 bytes of message
byte packetBuffer[NTP_PACKET_SIZE]; //buffer to hold incoming & outgoing packets
time_t getNtpTime() {
  while (Udp.parsePacket() > 0) ; // discard any previously received packets
  //Serial.println("Transmit NTP Request");
  sendNTPpacket(timeServer);
  uint32_t beginWait = millis();
  while (millis() - beginWait < 1500) {
    int size = Udp.parsePacket();
    if (size >= NTP_PACKET_SIZE) {
      //Serial.println("Receive NTP Response");
      Udp.read(packetBuffer, NTP_PACKET_SIZE);  // read packet into the buffer
      unsigned long secsSince1900;
      // convert four bytes starting at location 40 to a long integer
      secsSince1900 =  (unsigned long)packetBuffer[40] << 24;
      secsSince1900 |= (unsigned long)packetBuffer[41] << 16;
      secsSince1900 |= (unsigned long)packetBuffer[42] << 8;
      secsSince1900 |= (unsigned long)packetBuffer[43];
      epoch = secsSince1900 - 2208988800UL + timeZone * SECS_PER_HOUR;
      return epoch;
    }
  }
  //Serial.println("No NTP Response :-(");
  return 0; // return 0 if unable to get the time
}

// send an NTP request to the time server at the given address
void sendNTPpacket(IPAddress &address) {
  // set all bytes in the buffer to 0
  memset(packetBuffer, 0, NTP_PACKET_SIZE);
  // Initialize values needed to form NTP request
  // (see URL above for details on the packets)
  packetBuffer[0] = 0b11100011;   // LI, Version, Mode
  packetBuffer[1] = 0;     // Stratum, or type of clock
  packetBuffer[2] = 6;     // Polling Interval
  packetBuffer[3] = 0xEC;  // Peer Clock Precision
  // 8 bytes of zero for Root Delay & Root Dispersion
  packetBuffer[12]  = 49;
  packetBuffer[13]  = 0x4E;
  packetBuffer[14]  = 49;
  packetBuffer[15]  = 52;
  // all NTP fields have been given values, now
  // you can send a packet requesting a timestamp:
  Udp.beginPacket(address, 123); //NTP requests are to port 123
  Udp.write(packetBuffer, NTP_PACKET_SIZE);
  Udp.endPacket();
}
/**/
/********************************************************************************************Init setup**/
void setup() {
  Serial.begin(9600);
  while (!Serial) continue;

  // We start by connecting to a WiFi network
  /*
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(WIFI_SSID);
  */

  /* Explicitly set the ESP8266 to be a WiFi-client, otherwise, it by default,
     would try to act as both a client and an access-point and could cause
     network-issues with your other WiFi-devices on your WiFi-network. */
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    //Serial.print(".");
  }
  /*
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  */
  //Firebase initialization
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
  //Set database read timeout to 1 minute (max 15 minutes)
  Firebase.setReadTimeout(firebaseData, 1000 * 60);
  //tiny, small, medium, large and unlimited.
  //Size and its write timeout e.g. tiny (1s), small (10s), medium (30s) and large (60s).
  Firebase.setwriteSizeLimit(firebaseData, "tiny");

  //Serial.println("Starting UDP");
  Udp.begin(localPort);
  setSyncProvider(getNtpTime);
  /*
    Serial.print("Local port: ");
    Serial.println(Udp.localPort());
    Serial.println("waiting for sync");
    Serial.print("Epoch:");
    Serial.println(epoch);
  */
  //Serial.print("Epoch:");
  //Serial.println(epoch);
  //Initiate firebase
  ESPSendData();
}
/**/
/********************************************************************************************Loop**/
void loop() {
  while (!Serial) continue;
  // tes json {"servo":0,"relay":0,"ph":302.12,"moist":990.42,"type":1}
  //char json[] = "{\"servo\":0,\"relay\":0,\"ph\":302.12,\"moist\":990.42,\"type\":1}";
  StaticJsonDocument<1024> doc;
  //DeserializationError error = deserializeJson(doc, json);
  DeserializationError error = deserializeJson(doc, Serial);
  if (error) return;
  int servo = doc["servo"];
  int relay = doc["relay"];
  float ph = doc["ph"];
  float moist = doc["moist"];
  float type = doc["type"];

  //Serial.print("Servo : "); Serial.println(servo);
  //Serial.print("Relay : "); String d2 = ((int)relay == 1) ? "ON" : "OFF"; Serial.println(d2);
  //Serial.print("pH level : "); Serial.println(ph);
  //Serial.print("Moist level : "); Serial.println(moist);

  ESPSendData(servo, relay, ph, moist, type);

  yield();
}
/**/
