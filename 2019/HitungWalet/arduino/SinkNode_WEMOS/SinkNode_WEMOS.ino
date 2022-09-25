/********************************************************************************************Includes**/
#include <FirebaseESP8266.h>
#include <FirebaseESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <SPI.h>
#include <RF24.h>
#include <RF24Network.h>
#include <WiFiUdp.h>
#include <TimeLib.h>
/**/
/********************************************************************************************Firebase setup**/
#define FIREBASE_HOST "..."
#define FIREBASE_AUTH "..."
#define WIFI_SSID "..."
#define WIFI_PASSWORD "..."
//Define FirebaseESP8266 data object
FirebaseData firebaseData;
String totalPath = "/data/total";
String tempPath = "/data/temp";
String humidPath = "/data/humid";
/**/
/********************************************************************************************NTP setup**/
// NTP Servers:
IPAddress timeServer(202, 65, 114, 202);
const int timeZone = 0;
WiFiUDP Udp;
unsigned int localPort = 8888;  // local port to listen for UDP packets
unsigned long epoch;
unsigned long time_sync;
/**/
/********************************************************************************************Radio setup**/
RF24 radio(0, 16); //CE,CSN using R1 pin layout
RF24Network network(radio);
const uint16_t thisNode = 00; //Address of the coordinator in Octal format
/**/
/********************************************************************************************Variables**/
unsigned long displayTimer = 0;
unsigned long tStart = 0; //For interval
unsigned long tInterval = 2000; //For interval
bool timer = false;
unsigned int birdsTotal = 0;
bool bT = false;
int pirDetect = -1; //PIR detection
float humid, temp, newHumid, newTemp;
struct Payload_pirDetect {
  int pirDetect; //pir detect
};
struct Payload_sensors {
  float humid; //humidity from DHT22 sensor
  float temp; //temperature from DHT22 sensor
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
  //Firebase.enableClassicRequest(firebaseData, true);

  Serial.println("Starting UDP");
  Udp.begin(localPort);
  Serial.print("Local port: ");
  Serial.println(Udp.localPort());
  Serial.println("waiting for sync");
  setSyncProvider(getNtpTime);

  Serial.print("Epoch:");
  Serial.println(epoch);

  //Radio initialization
  radio.begin();
  network.begin(110, thisNode);
  radio.setRetries(4, 4);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  Serial.println(F("Coordinator is online....."));

  //Show total birds left
  if (Firebase.getInt(firebaseData, totalPath)) {
    birdsTotal = firebaseData.intData();
  } else {
    Serial.println("Firebase Error: " + firebaseData.errorReason());
  }
  Serial.print(F("Total bird left:"));
  Serial.println(birdsTotal);
}
/**/
/********************************************************************************************Loop start**/
void loop() {
  network.update();
  if ( network.available() ) {
    RF24NetworkHeader header; //create header variable
    network.peek(header);
    if (header.from_node == 01) {
      if (header.type == 'P') {
        Payload_pirDetect payloadin; //create payloadin variable
        network.read(header, &payloadin, sizeof(payloadin));
        Serial.print(F("Node "));
        Serial.print(header.from_node);
        Serial.print(F(":"));
        if (payloadin.pirDetect == 1) {
          Serial.println(F("Incoming detected!"));
          pirDetect = payloadin.pirDetect;
        }
        else if (payloadin.pirDetect == 0) {
          Serial.println(F("Outgoing detected!"));
          pirDetect = payloadin.pirDetect;
        }
        else if (payloadin.pirDetect == -1) {
          Serial.println(F("dummy!"));
        }
      }
      else if (header.type == 'S') {
        Payload_sensors payloadin; //create payloadin variable
        network.read(header, &payloadin, sizeof(payloadin));
        Serial.print(F("Node "));
        Serial.print(header.from_node);
        Serial.print(F(":"));
        newHumid = payloadin.humid;
        newTemp = payloadin.temp;
        Serial.print(F("humid:"));
        Serial.print(newHumid);
        Serial.print(F(":temp:"));
        Serial.println(newTemp);
      }
    }
    if (humid != newHumid && newHumid != -1) {
      humid = newHumid;
      if (!Firebase.setFloat(firebaseData, humidPath, humid)) {
        Serial.println("Firebase Error: " + firebaseData.errorReason());
      }
    }
    if (temp != newTemp && newTemp != -1) {
      temp = newTemp;
      if (!Firebase.setFloat(firebaseData, tempPath, temp)) {
        Serial.println("Firebase Error: " + firebaseData.errorReason());
      }
    }
    if (pirDetect == 1) {
      birdsTotal++;
      Serial.print(F("Total bird left (+1):"));
      Serial.println(birdsTotal);
      setTS((int)birdsTotal, "/logs/total");
      if (!Firebase.setInt(firebaseData, totalPath, birdsTotal)) {
        Serial.println("Firebase Error: " + firebaseData.errorReason());
      }
      pirDetect = -1;
      if (birdsTotal == 0) {
        bT = false;
      }
    }
    else if ( birdsTotal != 0 && pirDetect == 0) {
      birdsTotal--;
      Serial.print(F("Total bird left (-1):"));
      Serial.println(birdsTotal);
      setTS((int)birdsTotal, "/logs/total");
      if (!Firebase.setInt(firebaseData, totalPath, birdsTotal)) {
        Serial.println("Firebase Error: " + firebaseData.errorReason());
      }
      pirDetect = -1;
      if (birdsTotal == 0) {
        bT = false;
      }
    }
    if ( !birdsTotal && !bT ) {
      Serial.println(F("No bird left!"));
      setTS((int)birdsTotal, "/logs/total");
      if (!Firebase.setInt(firebaseData, totalPath, birdsTotal)) {
        Serial.println("Firebase Error: " + firebaseData.errorReason());
      }
      bT = true;
    }
    //update logs every 10 minutes
    if (millis() - time_sync >= 600000 ) { //sync time every 10 minutes
      setTS((int)humid, "/logs/humid");
      setTS((int)temp, "/logs/temp");
      //setTS((int)birdsTotal, "/logs/total");
      time_sync = millis();
    }
  }
}
/**/
/********************************************************************************************Function**/
void setTS(int data, String path) {
  setSyncProvider(getNtpTime);
  String newPath = path + "/" + String(epoch);
  if (!Firebase.setInt(firebaseData, newPath, (int)data)) {
    Serial.println("Firebase Error: " + firebaseData.errorReason());
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
  Serial.println("No NTP Response :-(");
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
