/********************************************************************************************Includes**/
#include <Arduino.h>
#include <TinyMPU6050.h>
#include <Wire.h>
#include <FirebaseESP32.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <SPIFFS.h>
//#include <WiFiAP.h>
#include <ESPAsyncWebServer.h>
#include <WiFiUdp.h>
#include <TimeLib.h>
#include "index.h"
#include "vars.h"
#include "soc/timer_group_struct.h"
#include "soc/timer_group_reg.h"
/*---ADC2 only---*/
#include "soc/sens_reg.h" // needed for manipulating ADC2 control register
//#define getVarName(var, str)  sprintf(str, "%s", #var)
uint64_t reg_b; // Used to store ADC2 control register
/**/
/********************************************************************************************MPU setup**/
TaskHandle_t TaskMPU;
MPU6050 mpu (Wire);
/**/
/********************************************************************************************Firebase setup**/
#define FIREBASE_HOST "..." //project database url
#define FIREBASE_AUTH "..." //database secret
#define WIFI_SSID "..."
#define WIFI_PASSWORD "..."
//Define FirebaseESP32 data object
FirebaseData firebaseData;
//data
#define rightPath "/jtd/bisindo/data/right"
#define leftPath "/jtd/bisindo/data/left"
//logs
#define rightLogPath "/jtd/bisindo/logs/right"
#define leftLogPath "/jtd/bisindo/logs/left"
/**/
/********************************************************************************************NTP setup**/
IPAddress timeServer(202, 65, 114, 202); //ntp.citra.net.id
static const unsigned int timeZone = 0;
WiFiUDP Udp;
unsigned int localPort = 8888;  // local port to listen for UDP packets
unsigned long epoch;
unsigned long dataSync;
unsigned long logsSync;
/**/
/********************************************************************************************PIN setup**
  A0 - A4 : FLEX SENSOR
  D4&D5 : FOR BLUETOOTH RX AND TX
  A5&A6 : XPIN AND YPIN FOR ACCELROMETER

*/
//const char* apssid = "ESP32AP"; // devices will connect
//const char* apsecret = "SmellFishy"; // password for it
bool calibratingFLEX = false;
bool calibratingMPU = false;
String upd[2] = {"0", "0"}; //file changes:true/false, file name
AsyncWebServer server(80);
const char* PARAM_JSON = "inputJson";
const char* PARAM_RCF = "inputRecalibrateFlex";
const char* PARAM_RCM = "inputRecalibrateMPU";
const char* PARAM_RCA = "inputRecalibrateAll";
const String vars[] = {"1000", "1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009",
                       "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                       "assalamualaikum", "halo", "dosen", "terimakasih", "selamatjalan", "waalaikumsalam"
                      };

void notFound(AsyncWebServerRequest *request) {
  request->send(404, "text/plain", "Not found");
}

String readFile(fs::FS &fs, const char * path) {
  Serial.printf("Reading file: %s\r\n", path);
  File file = fs.open(path, "r");
  if (!file || file.isDirectory()) {
    Serial.println("- empty file or failed to open file");
    return String();
  }
  Serial.println("- read from file:");
  String fileContent;
  while (file.available()) {
    fileContent += String((char)file.read());
  }
  //Serial.println(fileContent);
  return fileContent;
}

void writeFile(fs::FS &fs, const char * path, const char * message, const char * n) {
  Serial.printf("Writing file: %s\r\n", path);
  File file = fs.open(path, "w");
  if (!file) {
    Serial.println("- failed to open file for writing");
    return;
  }
  if (file.print(message)) {
    Serial.println("- file written");
  } else {
    Serial.println("- write failed");
  }
  upd[0] = "1";
  upd[1] = String(n);
}

unsigned long timer = 0;

// use first channel of 16 channels (started from zero)
#define LEDC_CHANNEL_0     0

// use 13 bit precission for LEDC timer
#define LEDC_TIMER_13_BIT  13

// use 5000 Hz as a LEDC base frequency
#define LEDC_BASE_FREQ     5000

// fade LED PIN (replace with LED_BUILTIN constant for built-in LED)
#define LED_PIN            2

int brightness = 0;    // how bright the LED is
int fadeAmount = 5;    // how many points to fade the LED by

static const bool pos = true;// false = left, true = right ====================================== Position ======================================
String temp = "0";
int symbolTemp = 0;
/*
  A0 = 36;
  A3 = 39;
  A4 = 32;
  A5 = 33;
  A6 = 34;
  A7 = 35;
  A10 = 4;
  A11 = 0;
  A12 = 2;
  A13 = 15;
  A14 = 13;
  A15 = 12;
  A16 = 14;
  A17 = 27;
  A18 = 25;
  A19 = 26;
  int xpin = A5;
  int xadc = 0;
  int xmax = 0;
  int xmin = 2048;

  int ypin = A6;
  int yadc = 0;
  int ymax = 0;
  int ymin = 2048;
*/
static const unsigned int FLEX_PIN1 = 13;
unsigned int flexADC1 = 0;
unsigned int sensorMin1 = 4095; //
unsigned int sensorMax1 = 0; //

static const unsigned int FLEX_PIN2 = 12;
unsigned int flexADC2 = 0;
unsigned int sensorMin2 = 4095;
unsigned int sensorMax2 = 0;

static const unsigned int FLEX_PIN3 = 14;
unsigned int flexADC3 = 0;
unsigned int sensorMin3 = 4095;
unsigned int sensorMax3 = 0;

static const unsigned int FLEX_PIN4 = 27;
unsigned int flexADC4 = 0;
unsigned int sensorMin4 = 4095;
unsigned int sensorMax4 = 0;

static const unsigned int FLEX_PIN5 = 26;
unsigned int flexADC5 = 0;
unsigned int sensorMin5 = 4095;
unsigned int sensorMax5 = 0;
/**/
/********************************************************************************************Functions**/
/*-------- ledc code ----------*/
void ledcAnalogWrite(uint8_t channel, uint32_t value, uint32_t valueMax = 255) {
  // calculate duty, 8191 from 2 ^ 13 - 1
  uint32_t duty = (8191 / valueMax) * min(value, valueMax);

  // write duty to LEDC
  ledcWrite(channel, duty);
}
/*-------- Send data code ----------*/
void sendData(int symbol, bool type, bool printSerial = false) {
  String packet = "";
  if (type == true) {
    if (pos == true) { //right
      packet = ( Firebase.setInt(firebaseData, rightPath, symbol) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
      (!printSerial) ? Serial.print("") : Serial.println(packet);
    }
    else { //left
      packet = ( Firebase.setInt(firebaseData, leftPath, symbol) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
      (!printSerial) ? Serial.print("") : Serial.println(packet);
    }
  }
  else {
    //sync epoch
    setSyncProvider(getNtpTime);
    //arrange paths
    String newPath1 = (String)rightLogPath + "/" + String(epoch);
    String newPath2 = (String)leftLogPath + "/" + String(epoch);
    if (pos == true) { //right
      packet = ( Firebase.setInt(firebaseData, newPath1, symbol) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
      (!printSerial) ? Serial.print("") : Serial.println(packet);
    }
    else { //left
      packet = ( Firebase.setInt(firebaseData, newPath2, symbol) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
      (!printSerial) ? Serial.print("") : Serial.println(packet);
    }
  }
}
void sendOnce(int symbol) { //to avoid printing repeating symbols
  if (symbol != symbolTemp) {
    sendData(symbol, true); //data, as data, serial print
    symbolTemp = symbol;
  }
}

/*-------- NTP code ----------*/
const unsigned int NTP_PACKET_SIZE = 48; // NTP time is in the first 48 bytes of message
byte packetBuffer[NTP_PACKET_SIZE]; //buffer to hold incoming & outgoing packets
time_t getNtpTime() {
  while (Udp.parsePacket() > 0) ; // discard any previously received packets
  //Serial.println("Transmit NTP Request");
  sendNTPpacket(timeServer);
  unsigned long beginWait = millis();
  while (millis() - beginWait < 1500) {
    unsigned int size = Udp.parsePacket();
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

/*-------- read sensor(ADC2 only) code ----------*/
unsigned int readSensor(unsigned int pin) {
  // ADC2 control register restoring
  WRITE_PERI_REG(SENS_SAR_READ_CTRL2_REG, reg_b);
  //VERY IMPORTANT: DO THIS TO NOT HAVE INVERTED VALUES!
  SET_PERI_REG_MASK(SENS_SAR_READ_CTRL2_REG, SENS_SAR2_DATA_INV);
  //We have to do the 2 previous instructions BEFORE EVERY readSensor() calling!
  int raw = analogRead(pin);
  delay(1);
  return raw;
}

/*-------- calibration code ----------*/
void calibration() {
  unsigned long cal = millis();
  while ( millis() - cal < 20000) {
    // set the brightness on LEDC channel 0
    ledcAnalogWrite(LEDC_CHANNEL_0, brightness);

    // change the brightness for next time through the loop:
    brightness = brightness + fadeAmount;

    // reverse the direction of the fading at the ends of the fade:
    if (brightness <= 0 || brightness >= 255) {
      fadeAmount = -fadeAmount;
    }
    // wait for 30 milliseconds to see the dimming effect
    delay(30);

    flexADC1 = readSensor(FLEX_PIN1);
    flexADC2 = readSensor(FLEX_PIN2);
    flexADC3 = readSensor(FLEX_PIN3);
    flexADC4 = readSensor(FLEX_PIN4);
    flexADC5 = readSensor(FLEX_PIN5);

    //Sensor 1
    if (flexADC1 < sensorMin1) {
      sensorMin1 = flexADC1;
    }
    if (flexADC1 > sensorMax1) {
      sensorMax1 = flexADC1;
    }

    //Sensor 2
    if (flexADC2 < sensorMin2) {
      sensorMin2 = flexADC2;
    }
    if (flexADC2 > sensorMax2) {
      sensorMax2 = flexADC2;
    }

    //Sensor 3
    if (flexADC3 < sensorMin3) {
      sensorMin3 = flexADC3;
    }
    if (flexADC3 > sensorMax3) {
      sensorMax3 = flexADC3;
    }

    //Sensor 4
    if (flexADC4 < sensorMin4) {
      sensorMin4 = flexADC4;
    }
    if (flexADC4 > sensorMax4) {
      sensorMax4 = flexADC4;
    }

    //Sensor 5
    if (flexADC5 < sensorMin5) {
      sensorMin5 = flexADC5;
    }
    if (flexADC5 > sensorMax5) {
      sensorMax5 = flexADC5;
    }
  }
  //turn off ledc
  ledcAnalogWrite(LEDC_CHANNEL_0, 0);
  //calibrated = true;
  //writeFile(SPIFFS, "/inputCal.txt", '1");
  Serial.print("Sensor 1 min :"); Serial.print(sensorMin1); Serial.print("\tSensor 1 max :"); Serial.println(sensorMax1);
  Serial.print("Sensor 2 min :"); Serial.print(sensorMin2); Serial.print("\tSensor 2 max :"); Serial.println(sensorMax2);
  Serial.print("Sensor 3 min :"); Serial.print(sensorMin3); Serial.print("\tSensor 3 max :"); Serial.println(sensorMax3);
  Serial.print("Sensor 4 min :"); Serial.print(sensorMin4); Serial.print("\tSensor 4 max :"); Serial.println(sensorMax4);
  Serial.print("Sensor 5 min :"); Serial.print(sensorMin5); Serial.print("\tSensor 5 max :"); Serial.println(sensorMax5);
}

/*-------- print code ----------*/
void printOnce(String cp) { //to avoid printing repeating symbols
  if (cp != temp) {
    Serial.print("-======================== ");
    Serial.print(cp);
    Serial.println(" (RIGHT) ========================-");
    temp = cp;
  }
}

/*-------- detectchar code ----------*/
int detectChar(int angle1, int angle2, int angle3, int angle4, int angle5, int pitch, int roll, int yaw) {
  int val = 0;
  if (pos == true) {
    if (((angle1 >= a1rLower) && (angle1 <= a1rUpper)) && ((angle2 >= a2rLower) && (angle2 <= a2rUpper)) && ((angle3 >= a3rLower) && (angle3 <= a3rUpper)) && ((angle4 >= a4rLower) && (angle4 <= a4rUpper)) && ((angle5 >= a5rLower) && (angle5 <= a5rUpper)) && ((pitch >= aprLower) && (pitch <= aprUpper)) && ((roll >= arrLower) && (roll <= arrUpper)) && ((yaw >= ayrLower) && (yaw <= ayrUpper)) ) {
      printOnce("A");
      val =  1;
      return val;
    } else if (((angle1 >= b1rLower) && (angle1 <= b1rUpper)) && ((angle2 >= b2rLower) && (angle2 <= b2rUpper)) && ((angle3 >= b3rLower) && (angle3 <= b3rUpper)) && ((angle4 >= b4rLower) && (angle4 <= b4rUpper)) && ((angle5 >= b5rLower) && (angle5 <= b5rUpper)) && ((pitch >= bprLower) && (pitch <= bprUpper)) && ((roll >= brrLower) && (roll <= brrUpper)) && ((yaw >= byrLower) && (yaw <= byrUpper)) ) {
      printOnce("B");
      val =  3;
      return val;
    } else if (((angle1 >= c1rLower) && (angle1 <= c1rUpper)) && ((angle2 >= c2rLower) && (angle2 <= c2rUpper)) && ((angle3 >= c3rLower) && (angle3 <= c3rUpper)) && ((angle4 >= c4rLower) && (angle4 <= c4rUpper)) && ((angle5 >= c5rLower) && (angle5 <= c5rUpper)) && ((pitch >= cprLower) && (pitch <= cprUpper)) && ((roll >= crrLower) && (roll <= crrUpper)) && ((yaw >= cyrLower) && (yaw <= cyrUpper)) ) {
      printOnce("C");
      val =  5;
      return val;
    } else if (((angle1 >= d1rLower) && (angle1 <= d1rUpper)) && ((angle2 >= d2rLower) && (angle2 <= d2rUpper)) && ((angle3 >= d3rLower) && (angle3 <= d3rUpper)) && ((angle4 >= d4rLower) && (angle4 <= d4rUpper)) && ((angle5 >= d5rLower) && (angle5 <= d5rUpper)) && ((pitch >= dprLower) && (pitch <= dprUpper)) && ((roll >= drrLower) && (roll <= drrUpper)) && ((yaw >= dyrLower) && (yaw <= dyrUpper)) ) {
      printOnce("D");
      val =  7;
      return val;
    } else if (((angle1 >= e1rLower) && (angle1 <= e1rUpper)) && ((angle2 >= e2rLower) && (angle2 <= e2rUpper)) && ((angle3 >= e3rLower) && (angle3 <= e3rUpper)) && ((angle4 >= e4rLower) && (angle4 <= e4rUpper)) && ((angle5 >= e5rLower) && (angle5 <= e5rUpper)) && ((pitch >= eprLower) && (pitch <= eprUpper)) && ((roll >= errLower) && (roll <= errUpper)) && ((yaw >= eyrLower) && (yaw <= eyrUpper)) ) {
      printOnce("E");
      val =  9;
      return val;
    } else if (((angle1 >= f1rLower) && (angle1 <= f1rUpper)) && ((angle2 >= f2rLower) && (angle2 <= f2rUpper)) && ((angle3 >= f3rLower) && (angle3 <= f3rUpper)) && ((angle4 >= f4rLower) && (angle4 <= f4rUpper)) && ((angle5 >= f5rLower) && (angle5 <= f5rUpper)) && ((pitch >= fprLower) && (pitch <= fprUpper)) && ((roll >= frrLower) && (roll <= frrUpper)) && ((yaw >= fyrLower) && (yaw <= fyrUpper)) ) {
      printOnce("F");
      val =  11;
      return val;
    } else if (((angle1 >= g1rLower) && (angle1 <= g1rUpper)) && ((angle2 >= g2rLower) && (angle2 <= g2rUpper)) && ((angle3 >= g3rLower) && (angle3 <= g3rUpper)) && ((angle4 >= g4rLower) && (angle4 <= g4rUpper)) && ((angle5 >= g5rLower) && (angle5 <= g5rUpper)) && ((pitch >= gprLower) && (pitch <= gprUpper)) && ((roll >= grrLower) && (roll <= grrUpper)) && ((yaw >= gyrLower) && (yaw <= gyrUpper)) ) {
      printOnce("G");
      val =  13;
      return val;
    } else if (((angle1 >= h1rLower) && (angle1 <= h1rUpper)) && ((angle2 >= h2rLower) && (angle2 <= h2rUpper)) && ((angle3 >= h3rLower) && (angle3 <= h3rUpper)) && ((angle4 >= h4rLower) && (angle4 <= h4rUpper)) && ((angle5 >= h5rLower) && (angle5 <= h5rUpper)) && ((pitch >= hprLower) && (pitch <= hprUpper)) && ((roll >= hrrLower) && (roll <= hrrUpper)) && ((yaw >= hyrLower) && (yaw <= hyrUpper)) ) {
      printOnce("H");
      val =  15;
      return val;
    } else if (((angle1 >= i1rLower) && (angle1 <= i1rUpper)) && ((angle2 >= i2rLower) && (angle2 <= i2rUpper)) && ((angle3 >= i3rLower) && (angle3 <= i3rUpper)) && ((angle4 >= i4rLower) && (angle4 <= i4rUpper)) && ((angle5 >= i5rLower) && (angle5 <= i5rUpper)) && ((pitch >= iprLower) && (pitch <= iprUpper)) && ((roll >= irrLower) && (roll <= irrUpper)) && ((yaw >= iyrLower) && (yaw <= iyrUpper)) ) {
      printOnce("I");
      val =  17;
      return val;
    } else if (((angle1 >= j1rLower) && (angle1 <= j1rUpper)) && ((angle2 >= j2rLower) && (angle2 <= j2rUpper)) && ((angle3 >= j3rLower) && (angle3 <= j3rUpper)) && ((angle4 >= j4rLower) && (angle4 <= j4rUpper)) && ((angle5 >= j5rLower) && (angle5 <= j5rUpper)) && ((pitch >= jprLower) && (pitch <= jprUpper)) && ((roll >= jrrLower) && (roll <= jrrUpper)) && ((yaw >= jyrLower) && (yaw <= jyrUpper)) ) {
      printOnce("J");
      val =  19;
      return val;
    } else if (((angle1 >= k1rLower) && (angle1 <= k1rUpper)) && ((angle2 >= k2rLower) && (angle2 <= k2rUpper)) && ((angle3 >= k3rLower) && (angle3 <= k3rUpper)) && ((angle4 >= k4rLower) && (angle4 <= k4rUpper)) && ((angle5 >= k5rLower) && (angle5 <= k5rUpper)) && ((pitch >= kprLower) && (pitch <= kprUpper)) && ((roll >= krrLower) && (roll <= krrUpper)) && ((yaw >= kyrLower) && (yaw <= kyrUpper)) ) {
      printOnce("K");
      val =  21;
      return val;
    } else if (((angle1 >= l1rLower) && (angle1 <= l1rUpper)) && ((angle2 >= l2rLower) && (angle2 <= l2rUpper)) && ((angle3 >= l3rLower) && (angle3 <= l3rUpper)) && ((angle4 >= l4rLower) && (angle4 <= l4rUpper)) && ((angle5 >= l5rLower) && (angle5 <= l5rUpper)) && ((pitch >= lprLower) && (pitch <= lprUpper)) && ((roll >= lrrLower) && (roll <= lrrUpper)) && ((yaw >= lyrLower) && (yaw <= lyrUpper)) ) {
      printOnce("L");
      val =  23;
      return val;
    } else if (((angle1 >= m1rLower) && (angle1 <= m1rUpper)) && ((angle2 >= m2rLower) && (angle2 <= m2rUpper)) && ((angle3 >= m3rLower) && (angle3 <= m3rUpper)) && ((angle4 >= m4rLower) && (angle4 <= m4rUpper)) && ((angle5 >= m5rLower) && (angle5 <= m5rUpper)) && ((pitch >= mprLower) && (pitch <= mprUpper)) && ((roll >= mrrLower) && (roll <= mrrUpper)) && ((yaw >= myrLower) && (yaw <= myrUpper)) ) {
      printOnce("M");
      val =  25;
      return val;
    } else if (((angle1 >= n1rLower) && (angle1 <= n1rUpper)) && ((angle2 >= n2rLower) && (angle2 <= n2rUpper)) && ((angle3 >= n3rLower) && (angle3 <= n3rUpper)) && ((angle4 >= n4rLower) && (angle4 <= n4rUpper)) && ((angle5 >= n5rLower) && (angle5 <= n5rUpper)) && ((pitch >= nprLower) && (pitch <= nprUpper)) && ((roll >= nrrLower) && (roll <= nrrUpper)) && ((yaw >= nyrLower) && (yaw <= nyrUpper)) ) {
      printOnce("N");
      val =  27;
      return val;
    } else if (((angle1 >= o1rLower) && (angle1 <= o1rUpper)) && ((angle2 >= o2rLower) && (angle2 <= o2rUpper)) && ((angle3 >= o3rLower) && (angle3 <= o3rUpper)) && ((angle4 >= o4rLower) && (angle4 <= o4rUpper)) && ((angle5 >= o5rLower) && (angle5 <= o5rUpper)) && ((pitch >= oprLower) && (pitch <= oprUpper)) && ((roll >= orrLower) && (roll <= orrUpper)) && ((yaw >= oyrLower) && (yaw <= oyrUpper)) ) {
      printOnce("O");
      val =  29;
      return val;
    } else if (((angle1 >= p1rLower) && (angle1 <= p1rUpper)) && ((angle2 >= p2rLower) && (angle2 <= p2rUpper)) && ((angle3 >= p3rLower) && (angle3 <= p3rUpper)) && ((angle4 >= p4rLower) && (angle4 <= p4rUpper)) && ((angle5 >= p5rLower) && (angle5 <= p5rUpper)) && ((pitch >= pprLower) && (pitch <= pprUpper)) && ((roll >= prrLower) && (roll <= prrUpper)) && ((yaw >= pyrLower) && (yaw <= pyrUpper)) ) {
      printOnce("P");
      val =  31;
      return val;
    } else if (((angle1 >= q1rLower) && (angle1 <= q1rUpper)) && ((angle2 >= q2rLower) && (angle2 <= q2rUpper)) && ((angle3 >= q3rLower) && (angle3 <= q3rUpper)) && ((angle4 >= q4rLower) && (angle4 <= q4rUpper)) && ((angle5 >= q5rLower) && (angle5 <= q5rUpper)) && ((pitch >= qprLower) && (pitch <= qprUpper)) && ((roll >= qrrLower) && (roll <= qrrUpper)) && ((yaw >= qyrLower) && (yaw <= qyrUpper)) ) {
      printOnce("Q");
      val =  33;
      return val;
    } else if (((angle1 >= r1rLower) && (angle1 <= r1rUpper)) && ((angle2 >= r2rLower) && (angle2 <= r2rUpper)) && ((angle3 >= r3rLower) && (angle3 <= r3rUpper)) && ((angle4 >= r4rLower) && (angle4 <= r4rUpper)) && ((angle5 >= r5rLower) && (angle5 <= r5rUpper)) && ((pitch >= rprLower) && (pitch <= rprUpper)) && ((roll >= rrrLower) && (roll <= rrrUpper)) && ((yaw >= ryrLower) && (yaw <= ryrUpper)) ) {
      printOnce("R");
      val =  35;
      return val;
    } else if (((angle1 >= s1rLower) && (angle1 <= s1rUpper)) && ((angle2 >= s2rLower) && (angle2 <= s2rUpper)) && ((angle3 >= s3rLower) && (angle3 <= s3rUpper)) && ((angle4 >= s4rLower) && (angle4 <= s4rUpper)) && ((angle5 >= s5rLower) && (angle5 <= s5rUpper)) && ((pitch >= sprLower) && (pitch <= sprUpper)) && ((roll >= srrLower) && (roll <= srrUpper)) && ((yaw >= syrLower) && (yaw <= syrUpper)) ) {
      printOnce("S");
      val =  37;
      return val;
    } else if (((angle1 >= t1rLower) && (angle1 <= t1rUpper)) && ((angle2 >= t2rLower) && (angle2 <= t2rUpper)) && ((angle3 >= t3rLower) && (angle3 <= t3rUpper)) && ((angle4 >= t4rLower) && (angle4 <= t4rUpper)) && ((angle5 >= t5rLower) && (angle5 <= t5rUpper)) && ((pitch >= tprLower) && (pitch <= tprUpper)) && ((roll >= trrLower) && (roll <= trrUpper)) && ((yaw >= tyrLower) && (yaw <= tyrUpper)) ) {
      printOnce("T");
      val =  39;
      return val;
    } else if (((angle1 >= u1rLower) && (angle1 <= u1rUpper)) && ((angle2 >= u2rLower) && (angle2 <= u2rUpper)) && ((angle3 >= u3rLower) && (angle3 <= u3rUpper)) && ((angle4 >= u4rLower) && (angle4 <= u4rUpper)) && ((angle5 >= u5rLower) && (angle5 <= u5rUpper)) && ((pitch >= uprLower) && (pitch <= uprUpper)) && ((roll >= urrLower) && (roll <= urrUpper)) && ((yaw >= uyrLower) && (yaw <= uyrUpper)) ) {
      printOnce("U");
      val =  41;
      return val;
    } else if (((angle1 >= v1rLower) && (angle1 <= v1rUpper)) && ((angle2 >= v2rLower) && (angle2 <= v2rUpper)) && ((angle3 >= v3rLower) && (angle3 <= v3rUpper)) && ((angle4 >= v4rLower) && (angle4 <= v4rUpper)) && ((angle5 >= v5rLower) && (angle5 <= v5rUpper)) && ((pitch >= vprLower) && (pitch <= vprUpper)) && ((roll >= vrrLower) && (roll <= vrrUpper)) && ((yaw >= vyrLower) && (yaw <= vyrUpper)) ) {
      printOnce("V");
      val =  43;
      return val;
    } else if (((angle1 >= w1rLower) && (angle1 <= w1rUpper)) && ((angle2 >= w2rLower) && (angle2 <= w2rUpper)) && ((angle3 >= w3rLower) && (angle3 <= w3rUpper)) && ((angle4 >= w4rLower) && (angle4 <= w4rUpper)) && ((angle5 >= w5rLower) && (angle5 <= w5rUpper)) && ((pitch >= wprLower) && (pitch <= wprUpper)) && ((roll >= wrrLower) && (roll <= wrrUpper)) && ((yaw >= wyrLower) && (yaw <= wyrUpper)) ) {
      printOnce("W");
      val =  45;
      return val;
    } else if (((angle1 >= x1rLower) && (angle1 <= x1rUpper)) && ((angle2 >= x2rLower) && (angle2 <= x2rUpper)) && ((angle3 >= x3rLower) && (angle3 <= x3rUpper)) && ((angle4 >= x4rLower) && (angle4 <= x4rUpper)) && ((angle5 >= x5rLower) && (angle5 <= x5rUpper)) && ((pitch >= xprLower) && (pitch <= xprUpper)) && ((roll >= xrrLower) && (roll <= xrrUpper)) && ((yaw >= xyrLower) && (yaw <= xyrUpper)) ) {
      printOnce("X");
      val =  47;
      return val;
    } else if (((angle1 >= y1rLower) && (angle1 <= y1rUpper)) && ((angle2 >= y2rLower) && (angle2 <= y2rUpper)) && ((angle3 >= y3rLower) && (angle3 <= y3rUpper)) && ((angle4 >= y4rLower) && (angle4 <= y4rUpper)) && ((angle5 >= y5rLower) && (angle5 <= y5rUpper)) && ((pitch >= yprLower) && (pitch <= yprUpper)) && ((roll >= yrrLower) && (roll <= yrrUpper)) && ((yaw >= yyrLower) && (yaw <= yyrUpper)) ) {
      printOnce("Y");
      val =  49;
      return val;
    } else if (((angle1 >= z1rLower) && (angle1 <= z1rUpper)) && ((angle2 >= z2rLower) && (angle2 <= z2rUpper)) && ((angle3 >= z3rLower) && (angle3 <= z3rUpper)) && ((angle4 >= z4rLower) && (angle4 <= z4rUpper)) && ((angle5 >= z5rLower) && (angle5 <= z5rUpper)) && ((pitch >= zprLower) && (pitch <= zprUpper)) && ((roll >= zrrLower) && (roll <= zrrUpper)) && ((yaw >= zyrLower) && (yaw <= zyrUpper)) ) {
      printOnce("Z");
      val =  51;
      return val;
    } else if (((angle1 >= assalamualaikum1rLower) && (angle1 <= assalamualaikum1rUpper)) && ((angle2 >= assalamualaikum2rLower) && (angle2 <= assalamualaikum2rUpper)) && ((angle3 >= assalamualaikum3rLower) && (angle3 <= assalamualaikum3rUpper)) && ((angle4 >= assalamualaikum4rLower) && (angle4 <= assalamualaikum4rUpper)) && ((angle5 >= assalamualaikum5rLower) && (angle5 <= assalamualaikum5rUpper)) && ((pitch >= assalamualaikumprLower) && (pitch <= assalamualaikumprUpper)) && ((roll >= assalamualaikumrrLower) && (roll <= assalamualaikumrrUpper)) && ((yaw >= assalamualaikumyrLower) && (yaw <= assalamualaikumyrUpper)) ) {
      printOnce("Assalamualaikum");
      val =  53;
      return val;
    } else if (((angle1 >= halo1rLower) && (angle1 <= halo1rUpper)) && ((angle2 >= halo2rLower) && (angle2 <= halo2rUpper)) && ((angle3 >= halo3rLower) && (angle3 <= halo3rUpper)) && ((angle4 >= halo4rLower) && (angle4 <= halo4rUpper)) && ((angle5 >= halo5rLower) && (angle5 <= halo5rUpper)) && ((pitch >= haloprLower) && (pitch <= haloprUpper)) && ((roll >= halorrLower) && (roll <= halorrUpper)) && ((yaw >= haloyrLower) && (yaw <= haloyrUpper)) ) {
      printOnce("Halo");
      val =  55;
      return val;
    } else if (((angle1 >= dosen1rLower) && (angle1 <= dosen1rUpper)) && ((angle2 >= dosen2rLower) && (angle2 <= dosen2rUpper)) && ((angle3 >= dosen3rLower) && (angle3 <= dosen3rUpper)) && ((angle4 >= dosen4rLower) && (angle4 <= dosen4rUpper)) && ((angle5 >= dosen5rLower) && (angle5 <= dosen5rUpper)) && ((pitch >= dosenprLower) && (pitch <= dosenprUpper)) && ((roll >= dosenrrLower) && (roll <= dosenrrUpper)) && ((yaw >= dosenyrLower) && (yaw <= dosenyrUpper)) ) {
      printOnce("Dosen");
      val =  57;
      return val;
    } else if (((angle1 >= terimakasih1rLower) && (angle1 <= terimakasih1rUpper)) && ((angle2 >= terimakasih2rLower) && (angle2 <= terimakasih2rUpper)) && ((angle3 >= terimakasih3rLower) && (angle3 <= terimakasih3rUpper)) && ((angle4 >= terimakasih4rLower) && (angle4 <= terimakasih4rUpper)) && ((angle5 >= terimakasih5rLower) && (angle5 <= terimakasih5rUpper)) && ((pitch >= terimakasihprLower) && (pitch <= terimakasihprUpper)) && ((roll >= terimakasihrrLower) && (roll <= terimakasihrrUpper)) && ((yaw >= terimakasihyrLower) && (yaw <= terimakasihyrUpper)) ) {
      printOnce("Terimakasih");
      val =  59;
      return val;
    } else if (((angle1 >= selamatJalan1rLower) && (angle1 <= selamatJalan1rUpper)) && ((angle2 >= selamatJalan2rLower) && (angle2 <= selamatJalan2rUpper)) && ((angle3 >= selamatJalan3rLower) && (angle3 <= selamatJalan3rUpper)) && ((angle4 >= selamatJalan4rLower) && (angle4 <= selamatJalan4rUpper)) && ((angle5 >= selamatJalan5rLower) && (angle5 <= selamatJalan5rUpper)) && ((pitch >= selamatJalanprLower) && (pitch <= selamatJalanprUpper)) && ((roll >= selamatJalanrrLower) && (roll <= selamatJalanrrUpper)) && ((yaw >= selamatJalanyrLower) && (yaw <= selamatJalanyrUpper)) ) {
      printOnce("Selamat Jalan");
      val =  61;
      return val;
    } else if (((angle1 >= waalaikumsalam1rLower) && (angle1 <= waalaikumsalam1rUpper)) && ((angle2 >= waalaikumsalam2rLower) && (angle2 <= waalaikumsalam2rUpper)) && ((angle3 >= waalaikumsalam3rLower) && (angle3 <= waalaikumsalam3rUpper)) && ((angle4 >= waalaikumsalam4rLower) && (angle4 <= waalaikumsalam4rUpper)) && ((angle5 >= waalaikumsalam5rLower) && (angle5 <= waalaikumsalam5rUpper)) && ((pitch >= waalaikumsalamprLower) && (pitch <= waalaikumsalamprUpper)) && ((roll >= waalaikumsalamrrLower) && (roll <= waalaikumsalamrrUpper)) && ((yaw >= waalaikumsalamyrLower) && (yaw <= waalaikumsalamyrUpper)) ) {
      printOnce("Waalaikumsalam");
      val =  63;
      return val;
    } else if (((angle1 >= n0_1rLower) && (angle1 <= n0_1rUpper)) && ((angle2 >= n0_2rLower) && (angle2 <= n0_2rUpper)) && ((angle3 >= n0_3rLower) && (angle3 <= n0_3rUpper)) && ((angle4 >= n0_4rLower) && (angle4 <= n0_4rUpper)) && ((angle5 >= n0_5rLower) && (angle5 <= n0_5rUpper)) && ((pitch >= n0_prLower) && (pitch <= n0_prUpper)) && ((roll >= n0_rrLower) && (roll <= n0_rrUpper)) && ((yaw >= n0_yrLower) && (yaw <= n0_yrUpper)) ) {
      printOnce("0");
      val =  999;
      return val;
    } else if (((angle1 >= n1_1rLower) && (angle1 <= n1_1rUpper)) && ((angle2 >= n1_2rLower) && (angle2 <= n1_2rUpper)) && ((angle3 >= n1_3rLower) && (angle3 <= n1_3rUpper)) && ((angle4 >= n1_4rLower) && (angle4 <= n1_4rUpper)) && ((angle5 >= n1_5rLower) && (angle5 <= n1_5rUpper)) && ((pitch >= n1_prLower) && (pitch <= n1_prUpper)) && ((roll >= n1_rrLower) && (roll <= n1_rrUpper)) && ((yaw >= n1_yrLower) && (yaw <= n1_yrUpper)) ) {
      printOnce("1");
      val =  1001;
      return val;
    } else if (((angle1 >= n2_1rLower) && (angle1 <= n2_1rUpper)) && ((angle2 >= n2_2rLower) && (angle2 <= n2_2rUpper)) && ((angle3 >= n2_3rLower) && (angle3 <= n2_3rUpper)) && ((angle4 >= n2_4rLower) && (angle4 <= n2_4rUpper)) && ((angle5 >= n2_5rLower) && (angle5 <= n2_5rUpper)) && ((pitch >= n2_prLower) && (pitch <= n2_prUpper)) && ((roll >= n2_rrLower) && (roll <= n2_rrUpper)) && ((yaw >= n2_yrLower) && (yaw <= n2_yrUpper)) ) {
      printOnce("2");
      val =  1003;
      return val;
    } else if (((angle1 >= n3_1rLower) && (angle1 <= n3_1rUpper)) && ((angle2 >= n3_2rLower) && (angle2 <= n3_2rUpper)) && ((angle3 >= n3_3rLower) && (angle3 <= n3_3rUpper)) && ((angle4 >= n3_4rLower) && (angle4 <= n3_4rUpper)) && ((angle5 >= n3_5rLower) && (angle5 <= n3_5rUpper)) && ((pitch >= n3_prLower) && (pitch <= n3_prUpper)) && ((roll >= n3_rrLower) && (roll <= n3_rrUpper)) && ((yaw >= n3_yrLower) && (yaw <= n3_yrUpper)) ) {
      printOnce("3");
      val =  1005;
      return val;
    } else if (((angle1 >= n4_1rLower) && (angle1 <= n4_1rUpper)) && ((angle2 >= n4_2rLower) && (angle2 <= n4_2rUpper)) && ((angle3 >= n4_3rLower) && (angle3 <= n4_3rUpper)) && ((angle4 >= n4_4rLower) && (angle4 <= n4_4rUpper)) && ((angle5 >= n4_5rLower) && (angle5 <= n4_5rUpper)) && ((pitch >= n4_prLower) && (pitch <= n4_prUpper)) && ((roll >= n4_rrLower) && (roll <= n4_rrUpper)) && ((yaw >= n4_yrLower) && (yaw <= n4_yrUpper)) ) {
      printOnce("4");
      val =  1007;
      return val;
    } else if (((angle1 >= n5_1rLower) && (angle1 <= n5_1rUpper)) && ((angle2 >= n5_2rLower) && (angle2 <= n5_2rUpper)) && ((angle3 >= n5_3rLower) && (angle3 <= n5_3rUpper)) && ((angle4 >= n5_4rLower) && (angle4 <= n5_4rUpper)) && ((angle5 >= n5_5rLower) && (angle5 <= n5_5rUpper)) && ((pitch >= n5_prLower) && (pitch <= n5_prUpper)) && ((roll >= n5_rrLower) && (roll <= n5_rrUpper)) && ((yaw >= n5_yrLower) && (yaw <= n5_yrUpper)) ) {
      printOnce("5");
      val =  1009;
      return val;
    } else if (((angle1 >= n6_1rLower) && (angle1 <= n6_1rUpper)) && ((angle2 >= n6_2rLower) && (angle2 <= n6_2rUpper)) && ((angle3 >= n6_3rLower) && (angle3 <= n6_3rUpper)) && ((angle4 >= n6_4rLower) && (angle4 <= n6_4rUpper)) && ((angle5 >= n6_5rLower) && (angle5 <= n6_5rUpper)) && ((pitch >= n6_prLower) && (pitch <= n6_prUpper)) && ((roll >= n6_rrLower) && (roll <= n6_rrUpper)) && ((yaw >= n6_yrLower) && (yaw <= n6_yrUpper)) ) {
      printOnce("6");
      val =  1011;
      return val;
    } else if (((angle1 >= n7_1rLower) && (angle1 <= n7_1rUpper)) && ((angle2 >= n7_2rLower) && (angle2 <= n7_2rUpper)) && ((angle3 >= n7_3rLower) && (angle3 <= n7_3rUpper)) && ((angle4 >= n7_4rLower) && (angle4 <= n7_4rUpper)) && ((angle5 >= n7_5rLower) && (angle5 <= n7_5rUpper)) && ((pitch >= n7_prLower) && (pitch <= n7_prUpper)) && ((roll >= n7_rrLower) && (roll <= n7_rrUpper)) && ((yaw >= n7_yrLower) && (yaw <= n7_yrUpper)) ) {
      printOnce("7");
      val =  1013;
      return val;
    } else if (((angle1 >= n8_1rLower) && (angle1 <= n8_1rUpper)) && ((angle2 >= n8_2rLower) && (angle2 <= n8_2rUpper)) && ((angle3 >= n8_3rLower) && (angle3 <= n8_3rUpper)) && ((angle4 >= n8_4rLower) && (angle4 <= n8_4rUpper)) && ((angle5 >= n8_5rLower) && (angle5 <= n8_5rUpper)) && ((pitch >= n8_prLower) && (pitch <= n8_prUpper)) && ((roll >= n8_rrLower) && (roll <= n8_rrUpper)) && ((yaw >= n8_yrLower) && (yaw <= n8_yrUpper)) ) {
      printOnce("8");
      val =  1015;
      return val;
    } else if (((angle1 >= n9_1rLower) && (angle1 <= n9_1rUpper)) && ((angle2 >= n9_2rLower) && (angle2 <= n9_2rUpper)) && ((angle3 >= n9_3rLower) && (angle3 <= n9_3rUpper)) && ((angle4 >= n9_4rLower) && (angle4 <= n9_4rUpper)) && ((angle5 >= n9_5rLower) && (angle5 <= n9_5rUpper)) && ((pitch >= n9_prLower) && (pitch <= n9_prUpper)) && ((roll >= n9_rrLower) && (roll <= n9_rrUpper)) && ((yaw >= n9_yrLower) && (yaw <= n9_yrUpper)) ) {
      printOnce("9");
      val =  1017;
      return val;
    }
  } else if (pos == false) {
    if (((angle1 >= a1lLower) && (angle1 <= a1lUpper)) && ((angle2 >= a2lLower) && (angle2 <= a2lUpper)) && ((angle3 >= a3lLower) && (angle3 <= a3lUpper)) && ((angle4 >= a4lLower) && (angle4 <= a4lUpper)) && ((angle5 >= a5lLower) && (angle5 <= a5lUpper)) && ((pitch >= aplLower) && (pitch <= aplUpper)) && ((roll >= arlLower) && (roll <= arlUpper)) && ((yaw >= aylLower) && (yaw <= aylUpper)) ) {
      printOnce("A");
      val =  2;
      return val;
    } else if (((angle1 >= b1lLower) && (angle1 <= b1lUpper)) && ((angle2 >= b2lLower) && (angle2 <= b2lUpper)) && ((angle3 >= b3lLower) && (angle3 <= b3lUpper)) && ((angle4 >= b4lLower) && (angle4 <= b4lUpper)) && ((angle5 >= b5lLower) && (angle5 <= b5lUpper)) && ((pitch >= bplLower) && (pitch <= bplUpper)) && ((roll >= brlLower) && (roll <= brlUpper)) && ((yaw >= bylLower) && (yaw <= bylUpper)) ) {
      printOnce("B");
      val =  4;
      return val;
    } else if (((angle1 >= c1lLower) && (angle1 <= c1lUpper)) && ((angle2 >= c2lLower) && (angle2 <= c2lUpper)) && ((angle3 >= c3lLower) && (angle3 <= c3lUpper)) && ((angle4 >= c4lLower) && (angle4 <= c4lUpper)) && ((angle5 >= c5lLower) && (angle5 <= c5lUpper)) && ((pitch >= cplLower) && (pitch <= cplUpper)) && ((roll >= crlLower) && (roll <= crlUpper)) && ((yaw >= cylLower) && (yaw <= cylUpper)) ) {
      printOnce("C");
      val =  6;
      return val;
    } else if (((angle1 >= d1lLower) && (angle1 <= d1lUpper)) && ((angle2 >= d2lLower) && (angle2 <= d2lUpper)) && ((angle3 >= d3lLower) && (angle3 <= d3lUpper)) && ((angle4 >= d4lLower) && (angle4 <= d4lUpper)) && ((angle5 >= d5lLower) && (angle5 <= d5lUpper)) && ((pitch >= dplLower) && (pitch <= dplUpper)) && ((roll >= drlLower) && (roll <= drlUpper)) && ((yaw >= dylLower) && (yaw <= dylUpper)) ) {
      printOnce("D");
      val =  8;
      return val;
    } else if (((angle1 >= e1lLower) && (angle1 <= e1lUpper)) && ((angle2 >= e2lLower) && (angle2 <= e2lUpper)) && ((angle3 >= e3lLower) && (angle3 <= e3lUpper)) && ((angle4 >= e4lLower) && (angle4 <= e4lUpper)) && ((angle5 >= e5lLower) && (angle5 <= e5lUpper)) && ((pitch >= eplLower) && (pitch <= eplUpper)) && ((roll >= erlLower) && (roll <= erlUpper)) && ((yaw >= eylLower) && (yaw <= eylUpper)) ) {
      printOnce("E");
      val =  10;
      return val;
    } else if (((angle1 >= f1lLower) && (angle1 <= f1lUpper)) && ((angle2 >= f2lLower) && (angle2 <= f2lUpper)) && ((angle3 >= f3lLower) && (angle3 <= f3lUpper)) && ((angle4 >= f4lLower) && (angle4 <= f4lUpper)) && ((angle5 >= f5lLower) && (angle5 <= f5lUpper)) && ((pitch >= fplLower) && (pitch <= fplUpper)) && ((roll >= frlLower) && (roll <= frlUpper)) && ((yaw >= fylLower) && (yaw <= fylUpper)) ) {
      printOnce("F");
      val =  12;
      return val;
    } else if (((angle1 >= g1lLower) && (angle1 <= g1lUpper)) && ((angle2 >= g2lLower) && (angle2 <= g2lUpper)) && ((angle3 >= g3lLower) && (angle3 <= g3lUpper)) && ((angle4 >= g4lLower) && (angle4 <= g4lUpper)) && ((angle5 >= g5lLower) && (angle5 <= g5lUpper)) && ((pitch >= gplLower) && (pitch <= gplUpper)) && ((roll >= grlLower) && (roll <= grlUpper)) && ((yaw >= gylLower) && (yaw <= gylUpper)) ) {
      printOnce("G");
      val =  14;
      return val;
    } else if (((angle1 >= h1lLower) && (angle1 <= h1lUpper)) && ((angle2 >= h2lLower) && (angle2 <= h2lUpper)) && ((angle3 >= h3lLower) && (angle3 <= h3lUpper)) && ((angle4 >= h4lLower) && (angle4 <= h4lUpper)) && ((angle5 >= h5lLower) && (angle5 <= h5lUpper)) && ((pitch >= hplLower) && (pitch <= hplUpper)) && ((roll >= hrlLower) && (roll <= hrlUpper)) && ((yaw >= hylLower) && (yaw <= hylUpper)) ) {
      printOnce("H");
      val =  16;
      return val;
    } else if (((angle1 >= i1lLower) && (angle1 <= i1lUpper)) && ((angle2 >= i2lLower) && (angle2 <= i2lUpper)) && ((angle3 >= i3lLower) && (angle3 <= i3lUpper)) && ((angle4 >= i4lLower) && (angle4 <= i4lUpper)) && ((angle5 >= i5lLower) && (angle5 <= i5lUpper)) && ((pitch >= iplLower) && (pitch <= iplUpper)) && ((roll >= irlLower) && (roll <= irlUpper)) && ((yaw >= iylLower) && (yaw <= iylUpper)) ) {
      printOnce("I");
      val =  18;
      return val;
    } else if (((angle1 >= j1lLower) && (angle1 <= j1lUpper)) && ((angle2 >= j2lLower) && (angle2 <= j2lUpper)) && ((angle3 >= j3lLower) && (angle3 <= j3lUpper)) && ((angle4 >= j4lLower) && (angle4 <= j4lUpper)) && ((angle5 >= j5lLower) && (angle5 <= j5lUpper)) && ((pitch >= jplLower) && (pitch <= jplUpper)) && ((roll >= jrlLower) && (roll <= jrlUpper)) && ((yaw >= jylLower) && (yaw <= jylUpper)) ) {
      printOnce("J");
      val =  20;
      return val;
    } else if (((angle1 >= k1lLower) && (angle1 <= k1lUpper)) && ((angle2 >= k2lLower) && (angle2 <= k2lUpper)) && ((angle3 >= k3lLower) && (angle3 <= k3lUpper)) && ((angle4 >= k4lLower) && (angle4 <= k4lUpper)) && ((angle5 >= k5lLower) && (angle5 <= k5lUpper)) && ((pitch >= kplLower) && (pitch <= kplUpper)) && ((roll >= krlLower) && (roll <= krlUpper)) && ((yaw >= kylLower) && (yaw <= kylUpper)) ) {
      printOnce("K");
      val =  22;
      return val;
    } else if (((angle1 >= l1lLower) && (angle1 <= l1lUpper)) && ((angle2 >= l2lLower) && (angle2 <= l2lUpper)) && ((angle3 >= l3lLower) && (angle3 <= l3lUpper)) && ((angle4 >= l4lLower) && (angle4 <= l4lUpper)) && ((angle5 >= l5lLower) && (angle5 <= l5lUpper)) && ((pitch >= lplLower) && (pitch <= lplUpper)) && ((roll >= lrlLower) && (roll <= lrlUpper)) && ((yaw >= lylLower) && (yaw <= lylUpper)) ) {
      printOnce("L");
      val =  24;
      return val;
    } else if (((angle1 >= m1lLower) && (angle1 <= m1lUpper)) && ((angle2 >= m2lLower) && (angle2 <= m2lUpper)) && ((angle3 >= m3lLower) && (angle3 <= m3lUpper)) && ((angle4 >= m4lLower) && (angle4 <= m4lUpper)) && ((angle5 >= m5lLower) && (angle5 <= m5lUpper)) && ((pitch >= mplLower) && (pitch <= mplUpper)) && ((roll >= mrlLower) && (roll <= mrlUpper)) && ((yaw >= mylLower) && (yaw <= mylUpper)) ) {
      printOnce("M");
      val =  26;
      return val;
    } else if (((angle1 >= n1lLower) && (angle1 <= n1lUpper)) && ((angle2 >= n2lLower) && (angle2 <= n2lUpper)) && ((angle3 >= n3lLower) && (angle3 <= n3lUpper)) && ((angle4 >= n4lLower) && (angle4 <= n4lUpper)) && ((angle5 >= n5lLower) && (angle5 <= n5lUpper)) && ((pitch >= nplLower) && (pitch <= nplUpper)) && ((roll >= nrlLower) && (roll <= nrlUpper)) && ((yaw >= nylLower) && (yaw <= nylUpper)) ) {
      printOnce("N");
      val =  28;
      return val;
    } else if (((angle1 >= o1lLower) && (angle1 <= o1lUpper)) && ((angle2 >= o2lLower) && (angle2 <= o2lUpper)) && ((angle3 >= o3lLower) && (angle3 <= o3lUpper)) && ((angle4 >= o4lLower) && (angle4 <= o4lUpper)) && ((angle5 >= o5lLower) && (angle5 <= o5lUpper)) && ((pitch >= oplLower) && (pitch <= oplUpper)) && ((roll >= orlLower) && (roll <= orlUpper)) && ((yaw >= oylLower) && (yaw <= oylUpper)) ) {
      printOnce("O");
      val =  30;
      return val;
    } else if (((angle1 >= p1lLower) && (angle1 <= p1lUpper)) && ((angle2 >= p2lLower) && (angle2 <= p2lUpper)) && ((angle3 >= p3lLower) && (angle3 <= p3lUpper)) && ((angle4 >= p4lLower) && (angle4 <= p4lUpper)) && ((angle5 >= p5lLower) && (angle5 <= p5lUpper)) && ((pitch >= pplLower) && (pitch <= pplUpper)) && ((roll >= prlLower) && (roll <= prlUpper)) && ((yaw >= pylLower) && (yaw <= pylUpper)) ) {
      printOnce("P");
      val =  32;
      return val;
    } else if (((angle1 >= q1lLower) && (angle1 <= q1lUpper)) && ((angle2 >= q2lLower) && (angle2 <= q2lUpper)) && ((angle3 >= q3lLower) && (angle3 <= q3lUpper)) && ((angle4 >= q4lLower) && (angle4 <= q4lUpper)) && ((angle5 >= q5lLower) && (angle5 <= q5lUpper)) && ((pitch >= qplLower) && (pitch <= qplUpper)) && ((roll >= qrlLower) && (roll <= qrlUpper)) && ((yaw >= qylLower) && (yaw <= qylUpper)) ) {
      printOnce("Q");
      val =  34;
      return val;
    } else if (((angle1 >= r1lLower) && (angle1 <= r1lUpper)) && ((angle2 >= r2lLower) && (angle2 <= r2lUpper)) && ((angle3 >= r3lLower) && (angle3 <= r3lUpper)) && ((angle4 >= r4lLower) && (angle4 <= r4lUpper)) && ((angle5 >= r5lLower) && (angle5 <= r5lUpper)) && ((pitch >= rplLower) && (pitch <= rplUpper)) && ((roll >= rrlLower) && (roll <= rrlUpper)) && ((yaw >= rylLower) && (yaw <= rylUpper)) ) {
      printOnce("R");
      val =  36;
      return val;
    } else if (((angle1 >= s1lLower) && (angle1 <= s1lUpper)) && ((angle2 >= s2lLower) && (angle2 <= s2lUpper)) && ((angle3 >= s3lLower) && (angle3 <= s3lUpper)) && ((angle4 >= s4lLower) && (angle4 <= s4lUpper)) && ((angle5 >= s5lLower) && (angle5 <= s5lUpper)) && ((pitch >= splLower) && (pitch <= splUpper)) && ((roll >= srlLower) && (roll <= srlUpper)) && ((yaw >= sylLower) && (yaw <= sylUpper)) ) {
      printOnce("S");
      val =  38;
      return val;
    } else if (((angle1 >= t1lLower) && (angle1 <= t1lUpper)) && ((angle2 >= t2lLower) && (angle2 <= t2lUpper)) && ((angle3 >= t3lLower) && (angle3 <= t3lUpper)) && ((angle4 >= t4lLower) && (angle4 <= t4lUpper)) && ((angle5 >= t5lLower) && (angle5 <= t5lUpper)) && ((pitch >= tplLower) && (pitch <= tplUpper)) && ((roll >= trlLower) && (roll <= trlUpper)) && ((yaw >= tylLower) && (yaw <= tylUpper)) ) {
      printOnce("T");
      val =  40;
      return val;
    } else if (((angle1 >= u1lLower) && (angle1 <= u1lUpper)) && ((angle2 >= u2lLower) && (angle2 <= u2lUpper)) && ((angle3 >= u3lLower) && (angle3 <= u3lUpper)) && ((angle4 >= u4lLower) && (angle4 <= u4lUpper)) && ((angle5 >= u5lLower) && (angle5 <= u5lUpper)) && ((pitch >= uplLower) && (pitch <= uplUpper)) && ((roll >= urlLower) && (roll <= urlUpper)) && ((yaw >= uylLower) && (yaw <= uylUpper)) ) {
      printOnce("U");
      val =  42;
      return val;
    } else if (((angle1 >= v1lLower) && (angle1 <= v1lUpper)) && ((angle2 >= v2lLower) && (angle2 <= v2lUpper)) && ((angle3 >= v3lLower) && (angle3 <= v3lUpper)) && ((angle4 >= v4lLower) && (angle4 <= v4lUpper)) && ((angle5 >= v5lLower) && (angle5 <= v5lUpper)) && ((pitch >= vplLower) && (pitch <= vplUpper)) && ((roll >= vrlLower) && (roll <= vrlUpper)) && ((yaw >= vylLower) && (yaw <= vylUpper)) ) {
      printOnce("V");
      val =  44;
      return val;
    } else if (((angle1 >= w1lLower) && (angle1 <= w1lUpper)) && ((angle2 >= w2lLower) && (angle2 <= w2lUpper)) && ((angle3 >= w3lLower) && (angle3 <= w3lUpper)) && ((angle4 >= w4lLower) && (angle4 <= w4lUpper)) && ((angle5 >= w5lLower) && (angle5 <= w5lUpper)) && ((pitch >= wplLower) && (pitch <= wplUpper)) && ((roll >= wrlLower) && (roll <= wrlUpper)) && ((yaw >= wylLower) && (yaw <= wylUpper)) ) {
      printOnce("W");
      val =  46;
      return val;
    } else if (((angle1 >= x1lLower) && (angle1 <= x1lUpper)) && ((angle2 >= x2lLower) && (angle2 <= x2lUpper)) && ((angle3 >= x3lLower) && (angle3 <= x3lUpper)) && ((angle4 >= x4lLower) && (angle4 <= x4lUpper)) && ((angle5 >= x5lLower) && (angle5 <= x5lUpper)) && ((pitch >= xplLower) && (pitch <= xplUpper)) && ((roll >= xrlLower) && (roll <= xrlUpper)) && ((yaw >= xylLower) && (yaw <= xylUpper)) ) {
      printOnce("X");
      val =  48;
      return val;
    } else if (((angle1 >= y1lLower) && (angle1 <= y1lUpper)) && ((angle2 >= y2lLower) && (angle2 <= y2lUpper)) && ((angle3 >= y3lLower) && (angle3 <= y3lUpper)) && ((angle4 >= y4lLower) && (angle4 <= y4lUpper)) && ((angle5 >= y5lLower) && (angle5 <= y5lUpper)) && ((pitch >= yplLower) && (pitch <= yplUpper)) && ((roll >= yrlLower) && (roll <= yrlUpper)) && ((yaw >= yylLower) && (yaw <= yylUpper)) ) {
      printOnce("Y");
      val =  50;
      return val;
    } else if (((angle1 >= z1lLower) && (angle1 <= z1lUpper)) && ((angle2 >= z2lLower) && (angle2 <= z2lUpper)) && ((angle3 >= z3lLower) && (angle3 <= z3lUpper)) && ((angle4 >= z4lLower) && (angle4 <= z4lUpper)) && ((angle5 >= z5lLower) && (angle5 <= z5lUpper)) && ((pitch >= zplLower) && (pitch <= zplUpper)) && ((roll >= zrlLower) && (roll <= zrlUpper)) && ((yaw >= zylLower) && (yaw <= zylUpper)) ) {
      printOnce("Z");
      val =  52;
      return val;
    } else if (((angle1 >= assalamualaikum1lLower) && (angle1 <= assalamualaikum1lUpper)) && ((angle2 >= assalamualaikum2lLower) && (angle2 <= assalamualaikum2lUpper)) && ((angle3 >= assalamualaikum3lLower) && (angle3 <= assalamualaikum3lUpper)) && ((angle4 >= assalamualaikum4lLower) && (angle4 <= assalamualaikum4lUpper)) && ((angle5 >= assalamualaikum5lLower) && (angle5 <= assalamualaikum5lUpper)) && ((pitch >= assalamualaikumplLower) && (pitch <= assalamualaikumplUpper)) && ((roll >= assalamualaikumrlLower) && (roll <= assalamualaikumrlUpper)) && ((yaw >= assalamualaikumylLower) && (yaw <= assalamualaikumylUpper)) ) {
      printOnce("Assalamualaikum");
      val =  54;
      return val;
    } else if (((angle1 >= halo1lLower) && (angle1 <= halo1lUpper)) && ((angle2 >= halo2lLower) && (angle2 <= halo2lUpper)) && ((angle3 >= halo3lLower) && (angle3 <= halo3lUpper)) && ((angle4 >= halo4lLower) && (angle4 <= halo4lUpper)) && ((angle5 >= halo5lLower) && (angle5 <= halo5lUpper)) && ((pitch >= haloplLower) && (pitch <= haloplUpper)) && ((roll >= halorlLower) && (roll <= halorlUpper)) && ((yaw >= haloylLower) && (yaw <= haloylUpper)) ) {
      printOnce("Halo");
      val =  56;
      return val;
    } else if (((angle1 >= dosen1lLower) && (angle1 <= dosen1lUpper)) && ((angle2 >= dosen2lLower) && (angle2 <= dosen2lUpper)) && ((angle3 >= dosen3lLower) && (angle3 <= dosen3lUpper)) && ((angle4 >= dosen4lLower) && (angle4 <= dosen4lUpper)) && ((angle5 >= dosen5lLower) && (angle5 <= dosen5lUpper)) && ((pitch >= dosenplLower) && (pitch <= dosenplUpper)) && ((roll >= dosenrlLower) && (roll <= dosenrlUpper)) && ((yaw >= dosenylLower) && (yaw <= dosenylUpper)) ) {
      printOnce("Dosen");
      val =  58;
      return val;
    } else if (((angle1 >= terimakasih1lLower) && (angle1 <= terimakasih1lUpper)) && ((angle2 >= terimakasih2lLower) && (angle2 <= terimakasih2lUpper)) && ((angle3 >= terimakasih3lLower) && (angle3 <= terimakasih3lUpper)) && ((angle4 >= terimakasih4lLower) && (angle4 <= terimakasih4lUpper)) && ((angle5 >= terimakasih5lLower) && (angle5 <= terimakasih5lUpper)) && ((pitch >= terimakasihplLower) && (pitch <= terimakasihplUpper)) && ((roll >= terimakasihrlLower) && (roll <= terimakasihrlUpper)) && ((yaw >= terimakasihylLower) && (yaw <= terimakasihylUpper)) ) {
      printOnce("Terimakasih");
      val =  60;
      return val;
    } else if (((angle1 >= selamatJalan1lLower) && (angle1 <= selamatJalan1lUpper)) && ((angle2 >= selamatJalan2lLower) && (angle2 <= selamatJalan2lUpper)) && ((angle3 >= selamatJalan3lLower) && (angle3 <= selamatJalan3lUpper)) && ((angle4 >= selamatJalan4lLower) && (angle4 <= selamatJalan4lUpper)) && ((angle5 >= selamatJalan5lLower) && (angle5 <= selamatJalan5lUpper)) && ((pitch >= selamatJalanplLower) && (pitch <= selamatJalanplUpper)) && ((roll >= selamatJalanrlLower) && (roll <= selamatJalanrlUpper)) && ((yaw >= selamatJalanylLower) && (yaw <= selamatJalanylUpper)) ) {
      printOnce("Selamat Jalan");
      val =  62;
      return val;
    } else if (((angle1 >= waalaikumsalam1lLower) && (angle1 <= waalaikumsalam1lUpper)) && ((angle2 >= waalaikumsalam2lLower) && (angle2 <= waalaikumsalam2lUpper)) && ((angle3 >= waalaikumsalam3lLower) && (angle3 <= waalaikumsalam3lUpper)) && ((angle4 >= waalaikumsalam4lLower) && (angle4 <= waalaikumsalam4lUpper)) && ((angle5 >= waalaikumsalam5lLower) && (angle5 <= waalaikumsalam5lUpper)) && ((pitch >= waalaikumsalamplLower) && (pitch <= waalaikumsalamplUpper)) && ((roll >= waalaikumsalamrlLower) && (roll <= waalaikumsalamrlUpper)) && ((yaw >= waalaikumsalamylLower) && (yaw <= waalaikumsalamylUpper)) ) {
      printOnce("Waalaikumsalam");
      val =  64;
      return val;
    } else if (((angle1 >= n0_1lLower) && (angle1 <= n0_1lUpper)) && ((angle2 >= n0_2lLower) && (angle2 <= n0_2lUpper)) && ((angle3 >= n0_3lLower) && (angle3 <= n0_3lUpper)) && ((angle4 >= n0_4lLower) && (angle4 <= n0_4lUpper)) && ((angle5 >= n0_5lLower) && (angle5 <= n0_5lUpper)) && ((pitch >= n0_plLower) && (pitch <= n0_plUpper)) && ((roll >= n0_rlLower) && (roll <= n0_rlUpper)) && ((yaw >= n0_ylLower) && (yaw <= n0_ylUpper)) ) {
      printOnce("0");
      val =  1000;
      return val;
    } else if (((angle1 >= n1_1lLower) && (angle1 <= n1_1lUpper)) && ((angle2 >= n1_2lLower) && (angle2 <= n1_2lUpper)) && ((angle3 >= n1_3lLower) && (angle3 <= n1_3lUpper)) && ((angle4 >= n1_4lLower) && (angle4 <= n1_4lUpper)) && ((angle5 >= n1_5lLower) && (angle5 <= n1_5lUpper)) && ((pitch >= n1_plLower) && (pitch <= n1_plUpper)) && ((roll >= n1_rlLower) && (roll <= n1_rlUpper)) && ((yaw >= n1_ylLower) && (yaw <= n1_ylUpper)) ) {
      printOnce("1");
      val =  1002;
      return val;
    } else if (((angle1 >= n2_1lLower) && (angle1 <= n2_1lUpper)) && ((angle2 >= n2_2lLower) && (angle2 <= n2_2lUpper)) && ((angle3 >= n2_3lLower) && (angle3 <= n2_3lUpper)) && ((angle4 >= n2_4lLower) && (angle4 <= n2_4lUpper)) && ((angle5 >= n2_5lLower) && (angle5 <= n2_5lUpper)) && ((pitch >= n2_plLower) && (pitch <= n2_plUpper)) && ((roll >= n2_rlLower) && (roll <= n2_rlUpper)) && ((yaw >= n2_ylLower) && (yaw <= n2_ylUpper)) ) {
      printOnce("2");
      val =  1004;
      return val;
    } else if (((angle1 >= n3_1lLower) && (angle1 <= n3_1lUpper)) && ((angle2 >= n3_2lLower) && (angle2 <= n3_2lUpper)) && ((angle3 >= n3_3lLower) && (angle3 <= n3_3lUpper)) && ((angle4 >= n3_4lLower) && (angle4 <= n3_4lUpper)) && ((angle5 >= n3_5lLower) && (angle5 <= n3_5lUpper)) && ((pitch >= n3_plLower) && (pitch <= n3_plUpper)) && ((roll >= n3_rlLower) && (roll <= n3_rlUpper)) && ((yaw >= n3_ylLower) && (yaw <= n3_ylUpper)) ) {
      printOnce("3");
      val =  1006;
      return val;
    } else if (((angle1 >= n4_1lLower) && (angle1 <= n4_1lUpper)) && ((angle2 >= n4_2lLower) && (angle2 <= n4_2lUpper)) && ((angle3 >= n4_3lLower) && (angle3 <= n4_3lUpper)) && ((angle4 >= n4_4lLower) && (angle4 <= n4_4lUpper)) && ((angle5 >= n4_5lLower) && (angle5 <= n4_5lUpper)) && ((pitch >= n4_plLower) && (pitch <= n4_plUpper)) && ((roll >= n4_rlLower) && (roll <= n4_rlUpper)) && ((yaw >= n4_ylLower) && (yaw <= n4_ylUpper)) ) {
      printOnce("4");
      val =  1008;
      return val;
    } else if (((angle1 >= n5_1lLower) && (angle1 <= n5_1lUpper)) && ((angle2 >= n5_2lLower) && (angle2 <= n5_2lUpper)) && ((angle3 >= n5_3lLower) && (angle3 <= n5_3lUpper)) && ((angle4 >= n5_4lLower) && (angle4 <= n5_4lUpper)) && ((angle5 >= n5_5lLower) && (angle5 <= n5_5lUpper)) && ((pitch >= n5_plLower) && (pitch <= n5_plUpper)) && ((roll >= n5_rlLower) && (roll <= n5_rlUpper)) && ((yaw >= n5_ylLower) && (yaw <= n5_ylUpper)) ) {
      printOnce("5");
      val =  1010;
      return val;
    } else if (((angle1 >= n6_1lLower) && (angle1 <= n6_1lUpper)) && ((angle2 >= n6_2lLower) && (angle2 <= n6_2lUpper)) && ((angle3 >= n6_3lLower) && (angle3 <= n6_3lUpper)) && ((angle4 >= n6_4lLower) && (angle4 <= n6_4lUpper)) && ((angle5 >= n6_5lLower) && (angle5 <= n6_5lUpper)) && ((pitch >= n6_plLower) && (pitch <= n6_plUpper)) && ((roll >= n6_rlLower) && (roll <= n6_rlUpper)) && ((yaw >= n6_ylLower) && (yaw <= n6_ylUpper)) ) {
      printOnce("6");
      val =  1012;
      return val;
    } else if (((angle1 >= n7_1lLower) && (angle1 <= n7_1lUpper)) && ((angle2 >= n7_2lLower) && (angle2 <= n7_2lUpper)) && ((angle3 >= n7_3lLower) && (angle3 <= n7_3lUpper)) && ((angle4 >= n7_4lLower) && (angle4 <= n7_4lUpper)) && ((angle5 >= n7_5lLower) && (angle5 <= n7_5lUpper)) && ((pitch >= n7_plLower) && (pitch <= n7_plUpper)) && ((roll >= n7_rlLower) && (roll <= n7_rlUpper)) && ((yaw >= n7_ylLower) && (yaw <= n7_ylUpper)) ) {
      printOnce("7");
      val =  1014;
      return val;
    } else if (((angle1 >= n8_1lLower) && (angle1 <= n8_1lUpper)) && ((angle2 >= n8_2lLower) && (angle2 <= n8_2lUpper)) && ((angle3 >= n8_3lLower) && (angle3 <= n8_3lUpper)) && ((angle4 >= n8_4lLower) && (angle4 <= n8_4lUpper)) && ((angle5 >= n8_5lLower) && (angle5 <= n8_5lUpper)) && ((pitch >= n8_plLower) && (pitch <= n8_plUpper)) && ((roll >= n8_rlLower) && (roll <= n8_rlUpper)) && ((yaw >= n8_ylLower) && (yaw <= n8_ylUpper)) ) {
      printOnce("8");
      val =  1016;
      return val;
    } else if (((angle1 >= n9_1lLower) && (angle1 <= n9_1lUpper)) && ((angle2 >= n9_2lLower) && (angle2 <= n9_2lUpper)) && ((angle3 >= n9_3lLower) && (angle3 <= n9_3lUpper)) && ((angle4 >= n9_4lLower) && (angle4 <= n9_4lUpper)) && ((angle5 >= n9_5lLower) && (angle5 <= n9_5lUpper)) && ((pitch >= n9_plLower) && (pitch <= n9_plUpper)) && ((roll >= n9_rlLower) && (roll <= n9_rlUpper)) && ((yaw >= n9_ylLower) && (yaw <= n9_ylUpper)) ) {
      printOnce("9");
      val =  1018;
      return val;
    }
  }
  /**/
  return val;
}

bool isdigit( char c ) {
  if ( c >= '0' && c <= '9' ) return true ;
  return false;
}

void updateVars() {
  Serial.print(F("Updating calibration data:"));
  Serial.println(upd[1]);
  int cases = 0;
  String casesStr = "";
  for (int i = 0; i < upd[1].length(); ++i) {
    //Check if char is digit
    if (isdigit(upd[1][i])) {
      casesStr += upd[1][i];
    }
  }
  if (casesStr.length() == 0) {
    if (upd[1].length() == 1) {
      char casesChr = upd[1][0];
      switch (casesChr) {
        case 'a':
          cases = 0;
          break;
        case 'b':
          cases = 1;
          break;
        case 'c':
          cases = 2;
          break;
        case 'd':
          cases = 3;
          break;
        case 'e':
          cases = 4;
          break;
        case 'f':
          cases = 5;
          break;
        case 'g':
          cases = 6;
          break;
        case 'h':
          cases = 7;
          break;
        case 'i':
          cases = 8;
          break;
        case 'j':
          cases = 9;
          break;
        case 'k':
          cases = 10;
          break;
        case 'l':
          cases = 11;
          break;
        case 'm':
          cases = 12;
          break;
        case 'n':
          cases = 13;
          break;
        case 'o':
          cases = 14;
          break;
        case 'p':
          cases = 15;
          break;
        case 'q':
          cases = 16;
          break;
        case 'r':
          cases = 17;
          break;
        case 's':
          cases = 18;
          break;
        case 't':
          cases = 19;
          break;
        case 'u':
          cases = 20;
          break;
        case 'v':
          cases = 21;
          break;
        case 'w':
          cases = 22;
          break;
        case 'x':
          cases = 23;
          break;
        case 'y':
          cases = 24;
          break;
        case 'z':
          cases = 25;
          break;
      }
    } else {
      if (upd[1].startsWith(String("assalamualaikum"))) {
        cases = 100;
      } else if (upd[1].startsWith(String("halo"))) {
        cases = 101;
      } else if (upd[1].startsWith(String("dosen"))) {
        cases = 102;
      } else if (upd[1].startsWith(String("terimakasih"))) {
        cases = 103;
      } else if (upd[1].startsWith(String("selamatjalan"))) {
        cases = 104;
      } else if (upd[1].startsWith(String("waalaikumsalam"))) {
        cases = 105;
      }
    }
  } else {
    cases = atoi(casesStr.c_str());
  }
  String path = "/inputJson_" + String(upd[1]) + ".txt";
  String Json = readFile(SPIFFS, path.c_str());
  if (Json.length() > 0 && upd[1] != "0") {
    DynamicJsonDocument doc(2048);
    DeserializationError error = deserializeJson(doc, Json);
    if (error) {
      Serial.println(F("Error parsing JSON(update vars)"));
      return;
    }
    doc.shrinkToFit(); //reduces the capacity of the memory pool to match the current usage
    Serial.print("Json:");
    serializeJson(doc, Serial);
    switch (cases) {
      case 0:
        a1rLower = doc["data"]["a1rLower"]; a2rLower = doc["data"]["a2rLower"]; a3rLower = doc["data"]["a3rLower"]; a4rLower = doc["data"]["a4rLower"]; a5rLower = doc["data"]["a5rLower"]; aprLower = doc["data"]["aprLower"]; arrLower = doc["data"]["arrLower"]; ayrLower = doc["data"]["ayrLower"];
        a1rUpper = doc["data"]["a1rUpper"]; a2rUpper = doc["data"]["a2rUpper"]; a3rUpper = doc["data"]["a3rUpper"]; a4rUpper = doc["data"]["a4rUpper"]; a5rUpper = doc["data"]["a5rUpper"]; aprUpper = doc["data"]["aprUpper"]; arrUpper = doc["data"]["arrUpper"]; ayrUpper = doc["data"]["ayrUpper"];
        a1lLower = doc["data"]["a1lLower"]; a2lLower = doc["data"]["a2lLower"]; a3lLower = doc["data"]["a3lLower"]; a4lLower = doc["data"]["a4lLower"]; a5lLower = doc["data"]["a5lLower"]; aplLower = doc["data"]["aplLower"]; arlLower = doc["data"]["arlLower"]; aylLower = doc["data"]["aylLower"];
        a1lUpper = doc["data"]["a1lUpper"]; a2lUpper = doc["data"]["a2lUpper"]; a3lUpper = doc["data"]["a3lUpper"]; a4lUpper = doc["data"]["a4lUpper"]; a5lUpper = doc["data"]["a5lUpper"]; aplUpper = doc["data"]["aplUpper"]; arlUpper = doc["data"]["arlUpper"]; aylUpper = doc["data"]["aylUpper"];
        path += "\n (a) loaded.";
        break;
      case 1:
        b1rLower = doc["data"]["b1rLower"]; b2rLower = doc["data"]["b2rLower"]; b3rLower = doc["data"]["b3rLower"]; b4rLower = doc["data"]["b4rLower"]; b5rLower = doc["data"]["b5rLower"]; bprLower = doc["data"]["bprLower"]; brrLower = doc["data"]["brrLower"]; byrLower = doc["data"]["byrLower"];
        b1rUpper = doc["data"]["b1rUpper"]; b2rUpper = doc["data"]["b2rUpper"]; b3rUpper = doc["data"]["b3rUpper"]; b4rUpper = doc["data"]["b4rUpper"]; b5rUpper = doc["data"]["b5rUpper"]; bprUpper = doc["data"]["bprUpper"]; brrUpper = doc["data"]["brrUpper"]; byrUpper = doc["data"]["byrUpper"];
        b1lLower = doc["data"]["b1lLower"]; b2lLower = doc["data"]["b2lLower"]; b3lLower = doc["data"]["b3lLower"]; b4lLower = doc["data"]["b4lLower"]; b5lLower = doc["data"]["b5lLower"]; bplLower = doc["data"]["bplLower"]; brlLower = doc["data"]["brlLower"]; bylLower = doc["data"]["bylLower"];
        b1lUpper = doc["data"]["b1lUpper"]; b2lUpper = doc["data"]["b2lUpper"]; b3lUpper = doc["data"]["b3lUpper"]; b4lUpper = doc["data"]["b4lUpper"]; b5lUpper = doc["data"]["b5lUpper"]; bplUpper = doc["data"]["bplUpper"]; brlUpper = doc["data"]["brlUpper"]; bylUpper = doc["data"]["bylUpper"];
        path += "\n (b) loaded.";
        break;
      case 2:
        c1rLower = doc["data"]["c1rLower"]; c2rLower = doc["data"]["c2rLower"]; c3rLower = doc["data"]["c3rLower"]; c4rLower = doc["data"]["c4rLower"]; c5rLower = doc["data"]["c5rLower"]; cprLower = doc["data"]["cprLower"]; crrLower = doc["data"]["crrLower"]; cyrLower = doc["data"]["cyrLower"];
        c1rUpper = doc["data"]["c1rUpper"]; c2rUpper = doc["data"]["c2rUpper"]; c3rUpper = doc["data"]["c3rUpper"]; c4rUpper = doc["data"]["c4rUpper"]; c5rUpper = doc["data"]["c5rUpper"]; cprUpper = doc["data"]["cprUpper"]; crrUpper = doc["data"]["crrUpper"]; cyrUpper = doc["data"]["cyrUpper"];
        c1lLower = doc["data"]["c1lLower"]; c2lLower = doc["data"]["c2lLower"]; c3lLower = doc["data"]["c3lLower"]; c4lLower = doc["data"]["c4lLower"]; c5lLower = doc["data"]["c5lLower"]; cplLower = doc["data"]["cplLower"]; crlLower = doc["data"]["crlLower"]; cylLower = doc["data"]["cylLower"];
        c1lUpper = doc["data"]["c1lUpper"]; c2lUpper = doc["data"]["c2lUpper"]; c3lUpper = doc["data"]["c3lUpper"]; c4lUpper = doc["data"]["c4lUpper"]; c5lUpper = doc["data"]["c5lUpper"]; cplUpper = doc["data"]["cplUpper"]; crlUpper = doc["data"]["crlUpper"]; cylUpper = doc["data"]["cylUpper"];
        path += "\n (c) loaded.";
        break;
      case 3:
        d1rLower = doc["data"]["d1rLower"]; d2rLower = doc["data"]["d2rLower"]; d3rLower = doc["data"]["d3rLower"]; d4rLower = doc["data"]["d4rLower"]; d5rLower = doc["data"]["d5rLower"]; dprLower = doc["data"]["dprLower"]; drrLower = doc["data"]["drrLower"]; dyrLower = doc["data"]["dyrLower"];
        d1rUpper = doc["data"]["d1rUpper"]; d2rUpper = doc["data"]["d2rUpper"]; d3rUpper = doc["data"]["d3rUpper"]; d4rUpper = doc["data"]["d4rUpper"]; d5rUpper = doc["data"]["d5rUpper"]; dprUpper = doc["data"]["dprUpper"]; drrUpper = doc["data"]["drrUpper"]; dyrUpper = doc["data"]["dyrUpper"];
        d1lLower = doc["data"]["d1lLower"]; d2lLower = doc["data"]["d2lLower"]; d3lLower = doc["data"]["d3lLower"]; d4lLower = doc["data"]["d4lLower"]; d5lLower = doc["data"]["d5lLower"]; dplLower = doc["data"]["dplLower"]; drlLower = doc["data"]["drlLower"]; dylLower = doc["data"]["dylLower"];
        d1lUpper = doc["data"]["d1lUpper"]; d2lUpper = doc["data"]["d2lUpper"]; d3lUpper = doc["data"]["d3lUpper"]; d4lUpper = doc["data"]["d4lUpper"]; d5lUpper = doc["data"]["d5lUpper"]; dplUpper = doc["data"]["dplUpper"]; drlUpper = doc["data"]["drlUpper"]; dylUpper = doc["data"]["dylUpper"];
        path += "\n (d) loaded.";
        break;
      case 4:
        e1rLower = doc["data"]["e1rLower"]; e2rLower = doc["data"]["e2rLower"]; e3rLower = doc["data"]["e3rLower"]; e4rLower = doc["data"]["e4rLower"]; e5rLower = doc["data"]["e5rLower"]; eprLower = doc["data"]["eprLower"]; errLower = doc["data"]["errLower"]; eyrLower = doc["data"]["eyrLower"];
        e1rUpper = doc["data"]["e1rUpper"]; e2rUpper = doc["data"]["e2rUpper"]; e3rUpper = doc["data"]["e3rUpper"]; e4rUpper = doc["data"]["e4rUpper"]; e5rUpper = doc["data"]["e5rUpper"]; eprUpper = doc["data"]["eprUpper"]; errUpper = doc["data"]["errUpper"]; eyrUpper = doc["data"]["eyrUpper"];
        e1lLower = doc["data"]["e1lLower"]; e2lLower = doc["data"]["e2lLower"]; e3lLower = doc["data"]["e3lLower"]; e4lLower = doc["data"]["e4lLower"]; e5lLower = doc["data"]["e5lLower"]; eplLower = doc["data"]["eplLower"]; erlLower = doc["data"]["erlLower"]; eylLower = doc["data"]["eylLower"];
        e1lUpper = doc["data"]["e1lUpper"]; e2lUpper = doc["data"]["e2lUpper"]; e3lUpper = doc["data"]["e3lUpper"]; e4lUpper = doc["data"]["e4lUpper"]; e5lUpper = doc["data"]["e5lUpper"]; eplUpper = doc["data"]["eplUpper"]; erlUpper = doc["data"]["erlUpper"]; eylUpper = doc["data"]["eylUpper"];
        path += "\n (e) loaded.";
        break;
      case 5:
        f1rLower = doc["data"]["f1rLower"]; f2rLower = doc["data"]["f2rLower"]; f3rLower = doc["data"]["f3rLower"]; f4rLower = doc["data"]["f4rLower"]; f5rLower = doc["data"]["f5rLower"]; fprLower = doc["data"]["fprLower"]; frrLower = doc["data"]["frrLower"]; fyrLower = doc["data"]["fyrLower"];
        f1rUpper = doc["data"]["f1rUpper"]; f2rUpper = doc["data"]["f2rUpper"]; f3rUpper = doc["data"]["f3rUpper"]; f4rUpper = doc["data"]["f4rUpper"]; f5rUpper = doc["data"]["f5rUpper"]; fprUpper = doc["data"]["fprUpper"]; frrUpper = doc["data"]["frrUpper"]; fyrUpper = doc["data"]["fyrUpper"];
        f1lLower = doc["data"]["f1lLower"]; f2lLower = doc["data"]["f2lLower"]; f3lLower = doc["data"]["f3lLower"]; f4lLower = doc["data"]["f4lLower"]; f5lLower = doc["data"]["f5lLower"]; fplLower = doc["data"]["fplLower"]; frlLower = doc["data"]["frlLower"]; fylLower = doc["data"]["fylLower"];
        f1lUpper = doc["data"]["f1lUpper"]; f2lUpper = doc["data"]["f2lUpper"]; f3lUpper = doc["data"]["f3lUpper"]; f4lUpper = doc["data"]["f4lUpper"]; f5lUpper = doc["data"]["f5lUpper"]; fplUpper = doc["data"]["fplUpper"]; frlUpper = doc["data"]["frlUpper"]; fylUpper = doc["data"]["fylUpper"];
        path += "\n (f) loaded.";
        break;
      case 6:
        g1rLower = doc["data"]["g1rLower"]; g2rLower = doc["data"]["g2rLower"]; g3rLower = doc["data"]["g3rLower"]; g4rLower = doc["data"]["g4rLower"]; g5rLower = doc["data"]["g5rLower"]; gprLower = doc["data"]["gprLower"]; grrLower = doc["data"]["grrLower"]; gyrLower = doc["data"]["gyrLower"];
        g1rUpper = doc["data"]["g1rUpper"]; g2rUpper = doc["data"]["g2rUpper"]; g3rUpper = doc["data"]["g3rUpper"]; g4rUpper = doc["data"]["g4rUpper"]; g5rUpper = doc["data"]["g5rUpper"]; gprUpper = doc["data"]["gprUpper"]; grrUpper = doc["data"]["grrUpper"]; gyrUpper = doc["data"]["gyrUpper"];
        g1lLower = doc["data"]["g1lLower"]; g2lLower = doc["data"]["g2lLower"]; g3lLower = doc["data"]["g3lLower"]; g4lLower = doc["data"]["g4lLower"]; g5lLower = doc["data"]["g5lLower"]; gplLower = doc["data"]["gplLower"]; grlLower = doc["data"]["grlLower"]; gylLower = doc["data"]["gylLower"];
        g1lUpper = doc["data"]["g1lUpper"]; g2lUpper = doc["data"]["g2lUpper"]; g3lUpper = doc["data"]["g3lUpper"]; g4lUpper = doc["data"]["g4lUpper"]; g5lUpper = doc["data"]["g5lUpper"]; gplUpper = doc["data"]["gplUpper"]; grlUpper = doc["data"]["grlUpper"]; gylUpper = doc["data"]["gylUpper"];
        path += "\n (g) loaded.";
        break;
      case 7:
        h1rLower = doc["data"]["h1rLower"]; h2rLower = doc["data"]["h2rLower"]; h3rLower = doc["data"]["h3rLower"]; h4rLower = doc["data"]["h4rLower"]; h5rLower = doc["data"]["h5rLower"]; hprLower = doc["data"]["hprLower"]; hrrLower = doc["data"]["hrrLower"]; hyrLower = doc["data"]["hyrLower"];
        h1rUpper = doc["data"]["h1rUpper"]; h2rUpper = doc["data"]["h2rUpper"]; h3rUpper = doc["data"]["h3rUpper"]; h4rUpper = doc["data"]["h4rUpper"]; h5rUpper = doc["data"]["h5rUpper"]; hprUpper = doc["data"]["hprUpper"]; hrrUpper = doc["data"]["hrrUpper"]; hyrUpper = doc["data"]["hyrUpper"];
        h1lLower = doc["data"]["h1lLower"]; h2lLower = doc["data"]["h2lLower"]; h3lLower = doc["data"]["h3lLower"]; h4lLower = doc["data"]["h4lLower"]; h5lLower = doc["data"]["h5lLower"]; hplLower = doc["data"]["hplLower"]; hrlLower = doc["data"]["hrlLower"]; hylLower = doc["data"]["hylLower"];
        h1lUpper = doc["data"]["h1lUpper"]; h2lUpper = doc["data"]["h2lUpper"]; h3lUpper = doc["data"]["h3lUpper"]; h4lUpper = doc["data"]["h4lUpper"]; h5lUpper = doc["data"]["h5lUpper"]; hplUpper = doc["data"]["hplUpper"]; hrlUpper = doc["data"]["hrlUpper"]; hylUpper = doc["data"]["hylUpper"];
        path += "\n (h) loaded.";
        break;
      case 8:
        i1rLower = doc["data"]["i1rLower"]; i2rLower = doc["data"]["i2rLower"]; i3rLower = doc["data"]["i3rLower"]; i4rLower = doc["data"]["i4rLower"]; i5rLower = doc["data"]["i5rLower"]; iprLower = doc["data"]["iprLower"]; irrLower = doc["data"]["irrLower"]; iyrLower = doc["data"]["iyrLower"];
        i1rUpper = doc["data"]["i1rUpper"]; i2rUpper = doc["data"]["i2rUpper"]; i3rUpper = doc["data"]["i3rUpper"]; i4rUpper = doc["data"]["i4rUpper"]; i5rUpper = doc["data"]["i5rUpper"]; iprUpper = doc["data"]["iprUpper"]; irrUpper = doc["data"]["irrUpper"]; iyrUpper = doc["data"]["iyrUpper"];
        i1lLower = doc["data"]["i1lLower"]; i2lLower = doc["data"]["i2lLower"]; i3lLower = doc["data"]["i3lLower"]; i4lLower = doc["data"]["i4lLower"]; i5lLower = doc["data"]["i5lLower"]; iplLower = doc["data"]["iplLower"]; irlLower = doc["data"]["irlLower"]; iylLower = doc["data"]["iylLower"];
        i1lUpper = doc["data"]["i1lUpper"]; i2lUpper = doc["data"]["i2lUpper"]; i3lUpper = doc["data"]["i3lUpper"]; i4lUpper = doc["data"]["i4lUpper"]; i5lUpper = doc["data"]["i5lUpper"]; iplUpper = doc["data"]["iplUpper"]; irlUpper = doc["data"]["irlUpper"]; iylUpper = doc["data"]["iylUpper"];
        path += "\n (i) loaded.";
        break;
      case 9:
        j1rLower = doc["data"]["j1rLower"]; j2rLower = doc["data"]["j2rLower"]; j3rLower = doc["data"]["j3rLower"]; j4rLower = doc["data"]["j4rLower"]; j5rLower = doc["data"]["j5rLower"]; jprLower = doc["data"]["jprLower"]; jrrLower = doc["data"]["jrrLower"]; jyrLower = doc["data"]["jyrLower"];
        j1rUpper = doc["data"]["j1rUpper"]; j2rUpper = doc["data"]["j2rUpper"]; j3rUpper = doc["data"]["j3rUpper"]; j4rUpper = doc["data"]["j4rUpper"]; j5rUpper = doc["data"]["j5rUpper"]; jprUpper = doc["data"]["jprUpper"]; jrrUpper = doc["data"]["jrrUpper"]; jyrUpper = doc["data"]["jyrUpper"];
        j1lLower = doc["data"]["j1lLower"]; j2lLower = doc["data"]["j2lLower"]; j3lLower = doc["data"]["j3lLower"]; j4lLower = doc["data"]["j4lLower"]; j5lLower = doc["data"]["j5lLower"]; jplLower = doc["data"]["jplLower"]; jrlLower = doc["data"]["jrlLower"]; jylLower = doc["data"]["jylLower"];
        j1lUpper = doc["data"]["j1lUpper"]; j2lUpper = doc["data"]["j2lUpper"]; j3lUpper = doc["data"]["j3lUpper"]; j4lUpper = doc["data"]["j4lUpper"]; j5lUpper = doc["data"]["j5lUpper"]; jplUpper = doc["data"]["jplUpper"]; jrlUpper = doc["data"]["jrlUpper"]; jylUpper = doc["data"]["jylUpper"];
        path += "\n (j) loaded.";
        break;
      case 10:
        k1rLower = doc["data"]["k1rLower"]; k2rLower = doc["data"]["k2rLower"]; k3rLower = doc["data"]["k3rLower"]; k4rLower = doc["data"]["k4rLower"]; k5rLower = doc["data"]["k5rLower"]; kprLower = doc["data"]["kprLower"]; krrLower = doc["data"]["krrLower"]; kyrLower = doc["data"]["kyrLower"];
        k1rUpper = doc["data"]["k1rUpper"]; k2rUpper = doc["data"]["k2rUpper"]; k3rUpper = doc["data"]["k3rUpper"]; k4rUpper = doc["data"]["k4rUpper"]; k5rUpper = doc["data"]["k5rUpper"]; kprUpper = doc["data"]["kprUpper"]; krrUpper = doc["data"]["krrUpper"]; kyrUpper = doc["data"]["kyrUpper"];
        k1lLower = doc["data"]["k1lLower"]; k2lLower = doc["data"]["k2lLower"]; k3lLower = doc["data"]["k3lLower"]; k4lLower = doc["data"]["k4lLower"]; k5lLower = doc["data"]["k5lLower"]; kplLower = doc["data"]["kplLower"]; krlLower = doc["data"]["krlLower"]; kylLower = doc["data"]["kylLower"];
        k1lUpper = doc["data"]["k1lUpper"]; k2lUpper = doc["data"]["k2lUpper"]; k3lUpper = doc["data"]["k3lUpper"]; k4lUpper = doc["data"]["k4lUpper"]; k5lUpper = doc["data"]["k5lUpper"]; kplUpper = doc["data"]["kplUpper"]; krlUpper = doc["data"]["krlUpper"]; kylUpper = doc["data"]["kylUpper"];
        path += "\n (k) loaded.";
        break;
      case 11:
        l1rLower = doc["data"]["l1rLower"]; l2rLower = doc["data"]["l2rLower"]; l3rLower = doc["data"]["l3rLower"]; l4rLower = doc["data"]["l4rLower"]; l5rLower = doc["data"]["l5rLower"]; lprLower = doc["data"]["lprLower"]; lrrLower = doc["data"]["lrrLower"]; lyrLower = doc["data"]["lyrLower"];
        l1rUpper = doc["data"]["l1rUpper"]; l2rUpper = doc["data"]["l2rUpper"]; l3rUpper = doc["data"]["l3rUpper"]; l4rUpper = doc["data"]["l4rUpper"]; l5rUpper = doc["data"]["l5rUpper"]; lprUpper = doc["data"]["lprUpper"]; lrrUpper = doc["data"]["lrrUpper"]; lyrUpper = doc["data"]["lyrUpper"];
        l1lLower = doc["data"]["l1lLower"]; l2lLower = doc["data"]["l2lLower"]; l3lLower = doc["data"]["l3lLower"]; l4lLower = doc["data"]["l4lLower"]; l5lLower = doc["data"]["l5lLower"]; lplLower = doc["data"]["lplLower"]; lrlLower = doc["data"]["lrlLower"]; lylLower = doc["data"]["lylLower"];
        l1lUpper = doc["data"]["l1lUpper"]; l2lUpper = doc["data"]["l2lUpper"]; l3lUpper = doc["data"]["l3lUpper"]; l4lUpper = doc["data"]["l4lUpper"]; l5lUpper = doc["data"]["l5lUpper"]; lplUpper = doc["data"]["lplUpper"]; lrlUpper = doc["data"]["lrlUpper"]; lylUpper = doc["data"]["lylUpper"];
        path += "\n (l) loaded.";
        break;
      case 12:
        m1rLower = doc["data"]["m1rLower"]; m2rLower = doc["data"]["m2rLower"]; m3rLower = doc["data"]["m3rLower"]; m4rLower = doc["data"]["m4rLower"]; m5rLower = doc["data"]["m5rLower"]; mprLower = doc["data"]["mprLower"]; mrrLower = doc["data"]["mrrLower"]; myrLower = doc["data"]["myrLower"];
        m1rUpper = doc["data"]["m1rUpper"]; m2rUpper = doc["data"]["m2rUpper"]; m3rUpper = doc["data"]["m3rUpper"]; m4rUpper = doc["data"]["m4rUpper"]; m5rUpper = doc["data"]["m5rUpper"]; mprUpper = doc["data"]["mprUpper"]; mrrUpper = doc["data"]["mrrUpper"]; myrUpper = doc["data"]["myrUpper"];
        m1lLower = doc["data"]["m1lLower"]; m2lLower = doc["data"]["m2lLower"]; m3lLower = doc["data"]["m3lLower"]; m4lLower = doc["data"]["m4lLower"]; m5lLower = doc["data"]["m5lLower"]; mplLower = doc["data"]["mplLower"]; mrlLower = doc["data"]["mrlLower"]; mylLower = doc["data"]["mylLower"];
        m1lUpper = doc["data"]["m1lUpper"]; m2lUpper = doc["data"]["m2lUpper"]; m3lUpper = doc["data"]["m3lUpper"]; m4lUpper = doc["data"]["m4lUpper"]; m5lUpper = doc["data"]["m5lUpper"]; mplUpper = doc["data"]["mplUpper"]; mrlUpper = doc["data"]["mrlUpper"]; mylUpper = doc["data"]["mylUpper"];
        path += "\n (m) loaded.";
        break;
      case 13:
        n1rLower = doc["data"]["n1rLower"]; n2rLower = doc["data"]["n2rLower"]; n3rLower = doc["data"]["n3rLower"]; n4rLower = doc["data"]["n4rLower"]; n5rLower = doc["data"]["n5rLower"]; nprLower = doc["data"]["nprLower"]; nrrLower = doc["data"]["nrrLower"]; nyrLower = doc["data"]["nyrLower"];
        n1rUpper = doc["data"]["n1rUpper"]; n2rUpper = doc["data"]["n2rUpper"]; n3rUpper = doc["data"]["n3rUpper"]; n4rUpper = doc["data"]["n4rUpper"]; n5rUpper = doc["data"]["n5rUpper"]; nprUpper = doc["data"]["nprUpper"]; nrrUpper = doc["data"]["nrrUpper"]; nyrUpper = doc["data"]["nyrUpper"];
        n1lLower = doc["data"]["n1lLower"]; n2lLower = doc["data"]["n2lLower"]; n3lLower = doc["data"]["n3lLower"]; n4lLower = doc["data"]["n4lLower"]; n5lLower = doc["data"]["n5lLower"]; nplLower = doc["data"]["nplLower"]; nrlLower = doc["data"]["nrlLower"]; nylLower = doc["data"]["nylLower"];
        n1lUpper = doc["data"]["n1lUpper"]; n2lUpper = doc["data"]["n2lUpper"]; n3lUpper = doc["data"]["n3lUpper"]; n4lUpper = doc["data"]["n4lUpper"]; n5lUpper = doc["data"]["n5lUpper"]; nplUpper = doc["data"]["nplUpper"]; nrlUpper = doc["data"]["nrlUpper"]; nylUpper = doc["data"]["nylUpper"];
        path += "\n (n) loaded.";
        break;
      case 14:
        o1rLower = doc["data"]["o1rLower"]; o2rLower = doc["data"]["o2rLower"]; o3rLower = doc["data"]["o3rLower"]; o4rLower = doc["data"]["o4rLower"]; o5rLower = doc["data"]["o5rLower"]; oprLower = doc["data"]["oprLower"]; orrLower = doc["data"]["orrLower"]; oyrLower = doc["data"]["oyrLower"];
        o1rUpper = doc["data"]["o1rUpper"]; o2rUpper = doc["data"]["o2rUpper"]; o3rUpper = doc["data"]["o3rUpper"]; o4rUpper = doc["data"]["o4rUpper"]; o5rUpper = doc["data"]["o5rUpper"]; oprUpper = doc["data"]["oprUpper"]; orrUpper = doc["data"]["orrUpper"]; oyrUpper = doc["data"]["oyrUpper"];
        o1lLower = doc["data"]["o1lLower"]; o2lLower = doc["data"]["o2lLower"]; o3lLower = doc["data"]["o3lLower"]; o4lLower = doc["data"]["o4lLower"]; o5lLower = doc["data"]["o5lLower"]; oplLower = doc["data"]["oplLower"]; orlLower = doc["data"]["orlLower"]; oylLower = doc["data"]["oylLower"];
        o1lUpper = doc["data"]["o1lUpper"]; o2lUpper = doc["data"]["o2lUpper"]; o3lUpper = doc["data"]["o3lUpper"]; o4lUpper = doc["data"]["o4lUpper"]; o5lUpper = doc["data"]["o5lUpper"]; oplUpper = doc["data"]["oplUpper"]; orlUpper = doc["data"]["orlUpper"]; oylUpper = doc["data"]["oylUpper"];
        path += "\n (o) loaded.";
        break;
      case 15:
        p1rLower = doc["data"]["p1rLower"]; p2rLower = doc["data"]["p2rLower"]; p3rLower = doc["data"]["p3rLower"]; p4rLower = doc["data"]["p4rLower"]; p5rLower = doc["data"]["p5rLower"]; pprLower = doc["data"]["pprLower"]; prrLower = doc["data"]["prrLower"]; pyrLower = doc["data"]["pyrLower"];
        p1rUpper = doc["data"]["p1rUpper"]; p2rUpper = doc["data"]["p2rUpper"]; p3rUpper = doc["data"]["p3rUpper"]; p4rUpper = doc["data"]["p4rUpper"]; p5rUpper = doc["data"]["p5rUpper"]; pprUpper = doc["data"]["pprUpper"]; prrUpper = doc["data"]["prrUpper"]; pyrUpper = doc["data"]["pyrUpper"];
        p1lLower = doc["data"]["p1lLower"]; p2lLower = doc["data"]["p2lLower"]; p3lLower = doc["data"]["p3lLower"]; p4lLower = doc["data"]["p4lLower"]; p5lLower = doc["data"]["p5lLower"]; pplLower = doc["data"]["pplLower"]; prlLower = doc["data"]["prlLower"]; pylLower = doc["data"]["pylLower"];
        p1lUpper = doc["data"]["p1lUpper"]; p2lUpper = doc["data"]["p2lUpper"]; p3lUpper = doc["data"]["p3lUpper"]; p4lUpper = doc["data"]["p4lUpper"]; p5lUpper = doc["data"]["p5lUpper"]; pplUpper = doc["data"]["pplUpper"]; prlUpper = doc["data"]["prlUpper"]; pylUpper = doc["data"]["pylUpper"];
        path += "\n (p) loaded.";
        break;
      case 16:
        q1rLower = doc["data"]["q1rLower"]; q2rLower = doc["data"]["q2rLower"]; q3rLower = doc["data"]["q3rLower"]; q4rLower = doc["data"]["q4rLower"]; q5rLower = doc["data"]["q5rLower"]; qprLower = doc["data"]["qprLower"]; qrrLower = doc["data"]["qrrLower"]; qyrLower = doc["data"]["qyrLower"];
        q1rUpper = doc["data"]["q1rUpper"]; q2rUpper = doc["data"]["q2rUpper"]; q3rUpper = doc["data"]["q3rUpper"]; q4rUpper = doc["data"]["q4rUpper"]; q5rUpper = doc["data"]["q5rUpper"]; qprUpper = doc["data"]["qprUpper"]; qrrUpper = doc["data"]["qrrUpper"]; qyrUpper = doc["data"]["qyrUpper"];
        q1lLower = doc["data"]["q1lLower"]; q2lLower = doc["data"]["q2lLower"]; q3lLower = doc["data"]["q3lLower"]; q4lLower = doc["data"]["q4lLower"]; q5lLower = doc["data"]["q5lLower"]; qplLower = doc["data"]["qplLower"]; qrlLower = doc["data"]["qrlLower"]; qylLower = doc["data"]["qylLower"];
        q1lUpper = doc["data"]["q1lUpper"]; q2lUpper = doc["data"]["q2lUpper"]; q3lUpper = doc["data"]["q3lUpper"]; q4lUpper = doc["data"]["q4lUpper"]; q5lUpper = doc["data"]["q5lUpper"]; qplUpper = doc["data"]["qplUpper"]; qrlUpper = doc["data"]["qrlUpper"]; qylUpper = doc["data"]["qylUpper"];
        path += "\n (q) loaded.";
        break;
      case 17:
        r1rLower = doc["data"]["r1rLower"]; r2rLower = doc["data"]["r2rLower"]; r3rLower = doc["data"]["r3rLower"]; r4rLower = doc["data"]["r4rLower"]; r5rLower = doc["data"]["r5rLower"]; rprLower = doc["data"]["rprLower"]; rrrLower = doc["data"]["rrrLower"]; ryrLower = doc["data"]["ryrLower"];
        r1rUpper = doc["data"]["r1rUpper"]; r2rUpper = doc["data"]["r2rUpper"]; r3rUpper = doc["data"]["r3rUpper"]; r4rUpper = doc["data"]["r4rUpper"]; r5rUpper = doc["data"]["r5rUpper"]; rprUpper = doc["data"]["rprUpper"]; rrrUpper = doc["data"]["rrrUpper"]; ryrUpper = doc["data"]["ryrUpper"];
        r1lLower = doc["data"]["r1lLower"]; r2lLower = doc["data"]["r2lLower"]; r3lLower = doc["data"]["r3lLower"]; r4lLower = doc["data"]["r4lLower"]; r5lLower = doc["data"]["r5lLower"]; rplLower = doc["data"]["rplLower"]; rrlLower = doc["data"]["rrlLower"]; rylLower = doc["data"]["rylLower"];
        r1lUpper = doc["data"]["r1lUpper"]; r2lUpper = doc["data"]["r2lUpper"]; r3lUpper = doc["data"]["r3lUpper"]; r4lUpper = doc["data"]["r4lUpper"]; r5lUpper = doc["data"]["r5lUpper"]; rplUpper = doc["data"]["rplUpper"]; rrlUpper = doc["data"]["rrlUpper"]; rylUpper = doc["data"]["rylUpper"];
        path += "\n (r) loaded.";
        break;
      case 18:
        s1rLower = doc["data"]["s1rLower"]; s2rLower = doc["data"]["s2rLower"]; s3rLower = doc["data"]["s3rLower"]; s4rLower = doc["data"]["s4rLower"]; s5rLower = doc["data"]["s5rLower"]; sprLower = doc["data"]["sprLower"]; srrLower = doc["data"]["srrLower"]; syrLower = doc["data"]["syrLower"];
        s1rUpper = doc["data"]["s1rUpper"]; s2rUpper = doc["data"]["s2rUpper"]; s3rUpper = doc["data"]["s3rUpper"]; s4rUpper = doc["data"]["s4rUpper"]; s5rUpper = doc["data"]["s5rUpper"]; sprUpper = doc["data"]["sprUpper"]; srrUpper = doc["data"]["srrUpper"]; syrUpper = doc["data"]["syrUpper"];
        s1lLower = doc["data"]["s1lLower"]; s2lLower = doc["data"]["s2lLower"]; s3lLower = doc["data"]["s3lLower"]; s4lLower = doc["data"]["s4lLower"]; s5lLower = doc["data"]["s5lLower"]; splLower = doc["data"]["splLower"]; srlLower = doc["data"]["srlLower"]; sylLower = doc["data"]["sylLower"];
        s1lUpper = doc["data"]["s1lUpper"]; s2lUpper = doc["data"]["s2lUpper"]; s3lUpper = doc["data"]["s3lUpper"]; s4lUpper = doc["data"]["s4lUpper"]; s5lUpper = doc["data"]["s5lUpper"]; splUpper = doc["data"]["splUpper"]; srlUpper = doc["data"]["srlUpper"]; sylUpper = doc["data"]["sylUpper"];
        path += "\n (s) loaded.";
        break;
      case 19:
        t1rLower = doc["data"]["t1rLower"]; t2rLower = doc["data"]["t2rLower"]; t3rLower = doc["data"]["t3rLower"]; t4rLower = doc["data"]["t4rLower"]; t5rLower = doc["data"]["t5rLower"]; tprLower = doc["data"]["tprLower"]; trrLower = doc["data"]["trrLower"]; tyrLower = doc["data"]["tyrLower"];
        t1rUpper = doc["data"]["t1rUpper"]; t2rUpper = doc["data"]["t2rUpper"]; t3rUpper = doc["data"]["t3rUpper"]; t4rUpper = doc["data"]["t4rUpper"]; t5rUpper = doc["data"]["t5rUpper"]; tprUpper = doc["data"]["tprUpper"]; trrUpper = doc["data"]["trrUpper"]; tyrUpper = doc["data"]["tyrUpper"];
        t1lLower = doc["data"]["t1lLower"]; t2lLower = doc["data"]["t2lLower"]; t3lLower = doc["data"]["t3lLower"]; t4lLower = doc["data"]["t4lLower"]; t5lLower = doc["data"]["t5lLower"]; tplLower = doc["data"]["tplLower"]; trlLower = doc["data"]["trlLower"]; tylLower = doc["data"]["tylLower"];
        t1lUpper = doc["data"]["t1lUpper"]; t2lUpper = doc["data"]["t2lUpper"]; t3lUpper = doc["data"]["t3lUpper"]; t4lUpper = doc["data"]["t4lUpper"]; t5lUpper = doc["data"]["t5lUpper"]; tplUpper = doc["data"]["tplUpper"]; trlUpper = doc["data"]["trlUpper"]; tylUpper = doc["data"]["tylUpper"];
        path += "\n (t) loaded.";
        break;
      case 20:
        u1rLower = doc["data"]["u1rLower"]; u2rLower = doc["data"]["u2rLower"]; u3rLower = doc["data"]["u3rLower"]; u4rLower = doc["data"]["u4rLower"]; u5rLower = doc["data"]["u5rLower"]; uprLower = doc["data"]["uprLower"]; urrLower = doc["data"]["urrLower"]; uyrLower = doc["data"]["uyrLower"];
        u1rUpper = doc["data"]["u1rUpper"]; u2rUpper = doc["data"]["u2rUpper"]; u3rUpper = doc["data"]["u3rUpper"]; u4rUpper = doc["data"]["u4rUpper"]; u5rUpper = doc["data"]["u5rUpper"]; uprUpper = doc["data"]["uprUpper"]; urrUpper = doc["data"]["urrUpper"]; uyrUpper = doc["data"]["uyrUpper"];
        u1lLower = doc["data"]["u1lLower"]; u2lLower = doc["data"]["u2lLower"]; u3lLower = doc["data"]["u3lLower"]; u4lLower = doc["data"]["u4lLower"]; u5lLower = doc["data"]["u5lLower"]; uplLower = doc["data"]["uplLower"]; urlLower = doc["data"]["urlLower"]; uylLower = doc["data"]["uylLower"];
        u1lUpper = doc["data"]["u1lUpper"]; u2lUpper = doc["data"]["u2lUpper"]; u3lUpper = doc["data"]["u3lUpper"]; u4lUpper = doc["data"]["u4lUpper"]; u5lUpper = doc["data"]["u5lUpper"]; uplUpper = doc["data"]["uplUpper"]; urlUpper = doc["data"]["urlUpper"]; uylUpper = doc["data"]["uylUpper"];
        path += "\n (u) loaded.";
        break;
      case 21:
        v1rLower = doc["data"]["v1rLower"]; v2rLower = doc["data"]["v2rLower"]; v3rLower = doc["data"]["v3rLower"]; v4rLower = doc["data"]["v4rLower"]; v5rLower = doc["data"]["v5rLower"]; vprLower = doc["data"]["vprLower"]; vrrLower = doc["data"]["vrrLower"]; vyrLower = doc["data"]["vyrLower"];
        v1rUpper = doc["data"]["v1rUpper"]; v2rUpper = doc["data"]["v2rUpper"]; v3rUpper = doc["data"]["v3rUpper"]; v4rUpper = doc["data"]["v4rUpper"]; v5rUpper = doc["data"]["v5rUpper"]; vprUpper = doc["data"]["vprUpper"]; vrrUpper = doc["data"]["vrrUpper"]; vyrUpper = doc["data"]["vyrUpper"];
        v1lLower = doc["data"]["v1lLower"]; v2lLower = doc["data"]["v2lLower"]; v3lLower = doc["data"]["v3lLower"]; v4lLower = doc["data"]["v4lLower"]; v5lLower = doc["data"]["v5lLower"]; vplLower = doc["data"]["vplLower"]; vrlLower = doc["data"]["vrlLower"]; vylLower = doc["data"]["vylLower"];
        v1lUpper = doc["data"]["v1lUpper"]; v2lUpper = doc["data"]["v2lUpper"]; v3lUpper = doc["data"]["v3lUpper"]; v4lUpper = doc["data"]["v4lUpper"]; v5lUpper = doc["data"]["v5lUpper"]; vplUpper = doc["data"]["vplUpper"]; vrlUpper = doc["data"]["vrlUpper"]; vylUpper = doc["data"]["vylUpper"];
        path += "\n (v) loaded.";
        break;
      case 22:
        w1rLower = doc["data"]["w1rLower"]; w2rLower = doc["data"]["w2rLower"]; w3rLower = doc["data"]["w3rLower"]; w4rLower = doc["data"]["w4rLower"]; w5rLower = doc["data"]["w5rLower"]; wprLower = doc["data"]["wprLower"]; wrrLower = doc["data"]["wrrLower"]; wyrLower = doc["data"]["wyrLower"];
        w1rUpper = doc["data"]["w1rUpper"]; w2rUpper = doc["data"]["w2rUpper"]; w3rUpper = doc["data"]["w3rUpper"]; w4rUpper = doc["data"]["w4rUpper"]; w5rUpper = doc["data"]["w5rUpper"]; wprUpper = doc["data"]["wprUpper"]; wrrUpper = doc["data"]["wrrUpper"]; wyrUpper = doc["data"]["wyrUpper"];
        w1lLower = doc["data"]["w1lLower"]; w2lLower = doc["data"]["w2lLower"]; w3lLower = doc["data"]["w3lLower"]; w4lLower = doc["data"]["w4lLower"]; w5lLower = doc["data"]["w5lLower"]; wplLower = doc["data"]["wplLower"]; wrlLower = doc["data"]["wrlLower"]; wylLower = doc["data"]["wylLower"];
        w1lUpper = doc["data"]["w1lUpper"]; w2lUpper = doc["data"]["w2lUpper"]; w3lUpper = doc["data"]["w3lUpper"]; w4lUpper = doc["data"]["w4lUpper"]; w5lUpper = doc["data"]["w5lUpper"]; wplUpper = doc["data"]["wplUpper"]; wrlUpper = doc["data"]["wrlUpper"]; wylUpper = doc["data"]["wylUpper"];
        path += "\n (w) loaded.";
        break;
      case 23:
        x1rLower = doc["data"]["x1rLower"]; x2rLower = doc["data"]["x2rLower"]; x3rLower = doc["data"]["x3rLower"]; x4rLower = doc["data"]["x4rLower"]; x5rLower = doc["data"]["x5rLower"]; xprLower = doc["data"]["xprLower"]; xrrLower = doc["data"]["xrrLower"]; xyrLower = doc["data"]["xyrLower"];
        x1rUpper = doc["data"]["x1rUpper"]; x2rUpper = doc["data"]["x2rUpper"]; x3rUpper = doc["data"]["x3rUpper"]; x4rUpper = doc["data"]["x4rUpper"]; x5rUpper = doc["data"]["x5rUpper"]; xprUpper = doc["data"]["xprUpper"]; xrrUpper = doc["data"]["xrrUpper"]; xyrUpper = doc["data"]["xyrUpper"];
        x1lLower = doc["data"]["x1lLower"]; x2lLower = doc["data"]["x2lLower"]; x3lLower = doc["data"]["x3lLower"]; x4lLower = doc["data"]["x4lLower"]; x5lLower = doc["data"]["x5lLower"]; xplLower = doc["data"]["xplLower"]; xrlLower = doc["data"]["xrlLower"]; xylLower = doc["data"]["xylLower"];
        x1lUpper = doc["data"]["x1lUpper"]; x2lUpper = doc["data"]["x2lUpper"]; x3lUpper = doc["data"]["x3lUpper"]; x4lUpper = doc["data"]["x4lUpper"]; x5lUpper = doc["data"]["x5lUpper"]; xplUpper = doc["data"]["xplUpper"]; xrlUpper = doc["data"]["xrlUpper"]; xylUpper = doc["data"]["xylUpper"];
        path += "\n (x) loaded.";
        break;
      case 24:
        y1rLower = doc["data"]["y1rLower"]; y2rLower = doc["data"]["y2rLower"]; y3rLower = doc["data"]["y3rLower"]; y4rLower = doc["data"]["y4rLower"]; y5rLower = doc["data"]["y5rLower"]; yprLower = doc["data"]["yprLower"]; yrrLower = doc["data"]["yrrLower"]; yyrLower = doc["data"]["yyrLower"];
        y1rUpper = doc["data"]["y1rUpper"]; y2rUpper = doc["data"]["y2rUpper"]; y3rUpper = doc["data"]["y3rUpper"]; y4rUpper = doc["data"]["y4rUpper"]; y5rUpper = doc["data"]["y5rUpper"]; yprUpper = doc["data"]["yprUpper"]; yrrUpper = doc["data"]["yrrUpper"]; yyrUpper = doc["data"]["yyrUpper"];
        y1lLower = doc["data"]["y1lLower"]; y2lLower = doc["data"]["y2lLower"]; y3lLower = doc["data"]["y3lLower"]; y4lLower = doc["data"]["y4lLower"]; y5lLower = doc["data"]["y5lLower"]; yplLower = doc["data"]["yplLower"]; yrlLower = doc["data"]["yrlLower"]; yylLower = doc["data"]["yylLower"];
        y1lUpper = doc["data"]["y1lUpper"]; y2lUpper = doc["data"]["y2lUpper"]; y3lUpper = doc["data"]["y3lUpper"]; y4lUpper = doc["data"]["y4lUpper"]; y5lUpper = doc["data"]["y5lUpper"]; yplUpper = doc["data"]["yplUpper"]; yrlUpper = doc["data"]["yrlUpper"]; yylUpper = doc["data"]["yylUpper"];
        path += "\n (y) loaded.";
        break;
      case 25:
        z1rLower = doc["data"]["z1rLower"]; z2rLower = doc["data"]["z2rLower"]; z3rLower = doc["data"]["z3rLower"]; z4rLower = doc["data"]["z4rLower"]; z5rLower = doc["data"]["z5rLower"]; zprLower = doc["data"]["zprLower"]; zrrLower = doc["data"]["zrrLower"]; zyrLower = doc["data"]["zyrLower"];
        z1rUpper = doc["data"]["z1rUpper"]; z2rUpper = doc["data"]["z2rUpper"]; z3rUpper = doc["data"]["z3rUpper"]; z4rUpper = doc["data"]["z4rUpper"]; z5rUpper = doc["data"]["z5rUpper"]; zprUpper = doc["data"]["zprUpper"]; zrrUpper = doc["data"]["zrrUpper"]; zyrUpper = doc["data"]["zyrUpper"];
        z1lLower = doc["data"]["z1lLower"]; z2lLower = doc["data"]["z2lLower"]; z3lLower = doc["data"]["z3lLower"]; z4lLower = doc["data"]["z4lLower"]; z5lLower = doc["data"]["z5lLower"]; zplLower = doc["data"]["zplLower"]; zrlLower = doc["data"]["zrlLower"]; zylLower = doc["data"]["zylLower"];
        z1lUpper = doc["data"]["z1lUpper"]; z2lUpper = doc["data"]["z2lUpper"]; z3lUpper = doc["data"]["z3lUpper"]; z4lUpper = doc["data"]["z4lUpper"]; z5lUpper = doc["data"]["z5lUpper"]; zplUpper = doc["data"]["zplUpper"]; zrlUpper = doc["data"]["zrlUpper"]; zylUpper = doc["data"]["zylUpper"];
        path += "\n (z) loaded.";
        break;
      case 100:
        assalamualaikum1rLower = doc["data"]["assalamualaikum1rLower"]; assalamualaikum2rLower = doc["data"]["assalamualaikum2rLower"]; assalamualaikum3rLower = doc["data"]["assalamualaikum3rLower"]; assalamualaikum4rLower = doc["data"]["assalamualaikum4rLower"]; assalamualaikum5rLower = doc["data"]["assalamualaikum5rLower"]; assalamualaikumprLower = doc["data"]["assalamualaikumprLower"]; assalamualaikumrrLower = doc["data"]["assalamualaikumrrLower"]; assalamualaikumyrLower = doc["data"]["assalamualaikumyrLower"];
        assalamualaikum1rUpper = doc["data"]["assalamualaikum1rUpper"]; assalamualaikum2rUpper = doc["data"]["assalamualaikum2rUpper"]; assalamualaikum3rUpper = doc["data"]["assalamualaikum3rUpper"]; assalamualaikum4rUpper = doc["data"]["assalamualaikum4rUpper"]; assalamualaikum5rUpper = doc["data"]["assalamualaikum5rUpper"]; assalamualaikumprUpper = doc["data"]["assalamualaikumprUpper"]; assalamualaikumrrUpper = doc["data"]["assalamualaikumrrUpper"]; assalamualaikumyrUpper = doc["data"]["assalamualaikumyrUpper"];
        assalamualaikum1lLower = doc["data"]["assalamualaikum1lLower"]; assalamualaikum2lLower = doc["data"]["assalamualaikum2lLower"]; assalamualaikum3lLower = doc["data"]["assalamualaikum3lLower"]; assalamualaikum4lLower = doc["data"]["assalamualaikum4lLower"]; assalamualaikum5lLower = doc["data"]["assalamualaikum5lLower"]; assalamualaikumplLower = doc["data"]["assalamualaikumplLower"]; assalamualaikumrlLower = doc["data"]["assalamualaikumrlLower"]; assalamualaikumylLower = doc["data"]["assalamualaikumylLower"];
        assalamualaikum1lUpper = doc["data"]["assalamualaikum1lUpper"]; assalamualaikum2lUpper = doc["data"]["assalamualaikum2lUpper"]; assalamualaikum3lUpper = doc["data"]["assalamualaikum3lUpper"]; assalamualaikum4lUpper = doc["data"]["assalamualaikum4lUpper"]; assalamualaikum5lUpper = doc["data"]["assalamualaikum5lUpper"]; assalamualaikumplUpper = doc["data"]["assalamualaikumplUpper"]; assalamualaikumrlUpper = doc["data"]["assalamualaikumrlUpper"]; assalamualaikumylUpper = doc["data"]["assalamualaikumylUpper"];
        path += "\n (assalamualaikum) loaded.";
        break;
      case 101:
        halo1rLower = doc["data"]["halo1rLower"]; halo2rLower = doc["data"]["halo2rLower"]; halo3rLower = doc["data"]["halo3rLower"]; halo4rLower = doc["data"]["halo4rLower"]; halo5rLower = doc["data"]["halo5rLower"]; haloprLower = doc["data"]["haloprLower"]; halorrLower = doc["data"]["halorrLower"]; haloyrLower = doc["data"]["haloyrLower"];
        halo1rUpper = doc["data"]["halo1rUpper"]; halo2rUpper = doc["data"]["halo2rUpper"]; halo3rUpper = doc["data"]["halo3rUpper"]; halo4rUpper = doc["data"]["halo4rUpper"]; halo5rUpper = doc["data"]["halo5rUpper"]; haloprUpper = doc["data"]["haloprUpper"]; halorrUpper = doc["data"]["halorrUpper"]; haloyrUpper = doc["data"]["haloyrUpper"];
        halo1lLower = doc["data"]["halo1lLower"]; halo2lLower = doc["data"]["halo2lLower"]; halo3lLower = doc["data"]["halo3lLower"]; halo4lLower = doc["data"]["halo4lLower"]; halo5lLower = doc["data"]["halo5lLower"]; haloplLower = doc["data"]["haloplLower"]; halorlLower = doc["data"]["halorlLower"]; haloylLower = doc["data"]["haloylLower"];
        halo1lUpper = doc["data"]["halo1lUpper"]; halo2lUpper = doc["data"]["halo2lUpper"]; halo3lUpper = doc["data"]["halo3lUpper"]; halo4lUpper = doc["data"]["halo4lUpper"]; halo5lUpper = doc["data"]["halo5lUpper"]; haloplUpper = doc["data"]["haloplUpper"]; halorlUpper = doc["data"]["halorlUpper"]; haloylUpper = doc["data"]["haloylUpper"];
        path += "\n (halo) loaded.";
        break;
      case 102:
        dosen1rLower = doc["data"]["dosen1rLower"]; dosen2rLower = doc["data"]["dosen2rLower"]; dosen3rLower = doc["data"]["dosen3rLower"]; dosen4rLower = doc["data"]["dosen4rLower"]; dosen5rLower = doc["data"]["dosen5rLower"]; dosenprLower = doc["data"]["dosenprLower"]; dosenrrLower = doc["data"]["dosenrrLower"]; dosenyrLower = doc["data"]["dosenyrLower"];
        dosen1rUpper = doc["data"]["dosen1rUpper"]; dosen2rUpper = doc["data"]["dosen2rUpper"]; dosen3rUpper = doc["data"]["dosen3rUpper"]; dosen4rUpper = doc["data"]["dosen4rUpper"]; dosen5rUpper = doc["data"]["dosen5rUpper"]; dosenprUpper = doc["data"]["dosenprUpper"]; dosenrrUpper = doc["data"]["dosenrrUpper"]; dosenyrUpper = doc["data"]["dosenyrUpper"];
        dosen1lLower = doc["data"]["dosen1lLower"]; dosen2lLower = doc["data"]["dosen2lLower"]; dosen3lLower = doc["data"]["dosen3lLower"]; dosen4lLower = doc["data"]["dosen4lLower"]; dosen5lLower = doc["data"]["dosen5lLower"]; dosenplLower = doc["data"]["dosenplLower"]; dosenrlLower = doc["data"]["dosenrlLower"]; dosenylLower = doc["data"]["dosenylLower"];
        dosen1lUpper = doc["data"]["dosen1lUpper"]; dosen2lUpper = doc["data"]["dosen2lUpper"]; dosen3lUpper = doc["data"]["dosen3lUpper"]; dosen4lUpper = doc["data"]["dosen4lUpper"]; dosen5lUpper = doc["data"]["dosen5lUpper"]; dosenplUpper = doc["data"]["dosenplUpper"]; dosenrlUpper = doc["data"]["dosenrlUpper"]; dosenylUpper = doc["data"]["dosenylUpper"];
        path += "\n (dosen) loaded.";
        break;
      case 103:
        terimakasih1rLower = doc["data"]["terimakasih1rLower"]; terimakasih2rLower = doc["data"]["terimakasih2rLower"]; terimakasih3rLower = doc["data"]["terimakasih3rLower"]; terimakasih4rLower = doc["data"]["terimakasih4rLower"]; terimakasih5rLower = doc["data"]["terimakasih5rLower"]; terimakasihprLower = doc["data"]["terimakasihprLower"]; terimakasihrrLower = doc["data"]["terimakasihrrLower"]; terimakasihyrLower = doc["data"]["terimakasihyrLower"];
        terimakasih1rUpper = doc["data"]["terimakasih1rUpper"]; terimakasih2rUpper = doc["data"]["terimakasih2rUpper"]; terimakasih3rUpper = doc["data"]["terimakasih3rUpper"]; terimakasih4rUpper = doc["data"]["terimakasih4rUpper"]; terimakasih5rUpper = doc["data"]["terimakasih5rUpper"]; terimakasihprUpper = doc["data"]["terimakasihprUpper"]; terimakasihrrUpper = doc["data"]["terimakasihrrUpper"]; terimakasihyrUpper = doc["data"]["terimakasihyrUpper"];
        terimakasih1lLower = doc["data"]["terimakasih1lLower"]; terimakasih2lLower = doc["data"]["terimakasih2lLower"]; terimakasih3lLower = doc["data"]["terimakasih3lLower"]; terimakasih4lLower = doc["data"]["terimakasih4lLower"]; terimakasih5lLower = doc["data"]["terimakasih5lLower"]; terimakasihplLower = doc["data"]["terimakasihplLower"]; terimakasihrlLower = doc["data"]["terimakasihrlLower"]; terimakasihylLower = doc["data"]["terimakasihylLower"];
        terimakasih1lUpper = doc["data"]["terimakasih1lUpper"]; terimakasih2lUpper = doc["data"]["terimakasih2lUpper"]; terimakasih3lUpper = doc["data"]["terimakasih3lUpper"]; terimakasih4lUpper = doc["data"]["terimakasih4lUpper"]; terimakasih5lUpper = doc["data"]["terimakasih5lUpper"]; terimakasihplUpper = doc["data"]["terimakasihplUpper"]; terimakasihrlUpper = doc["data"]["terimakasihrlUpper"]; terimakasihylUpper = doc["data"]["terimakasihylUpper"];
        path += "\n (terimakasih) loaded.";
        break;
      case 104:
        selamatJalan1rLower = doc["data"]["selamatJalan1rLower"]; selamatJalan2rLower = doc["data"]["selamatJalan2rLower"]; selamatJalan3rLower = doc["data"]["selamatJalan3rLower"]; selamatJalan4rLower = doc["data"]["selamatJalan4rLower"]; selamatJalan5rLower = doc["data"]["selamatJalan5rLower"]; selamatJalanprLower = doc["data"]["selamatJalanprLower"]; selamatJalanrrLower = doc["data"]["selamatJalanrrLower"]; selamatJalanyrLower = doc["data"]["selamatJalanyrLower"];
        selamatJalan1rUpper = doc["data"]["selamatJalan1rUpper"]; selamatJalan2rUpper = doc["data"]["selamatJalan2rUpper"]; selamatJalan3rUpper = doc["data"]["selamatJalan3rUpper"]; selamatJalan4rUpper = doc["data"]["selamatJalan4rUpper"]; selamatJalan5rUpper = doc["data"]["selamatJalan5rUpper"]; selamatJalanprUpper = doc["data"]["selamatJalanprUpper"]; selamatJalanrrUpper = doc["data"]["selamatJalanrrUpper"]; selamatJalanyrUpper = doc["data"]["selamatJalanyrUpper"];
        selamatJalan1lLower = doc["data"]["selamatJalan1lLower"]; selamatJalan2lLower = doc["data"]["selamatJalan2lLower"]; selamatJalan3lLower = doc["data"]["selamatJalan3lLower"]; selamatJalan4lLower = doc["data"]["selamatJalan4lLower"]; selamatJalan5lLower = doc["data"]["selamatJalan5lLower"]; selamatJalanplLower = doc["data"]["selamatJalanplLower"]; selamatJalanrlLower = doc["data"]["selamatJalanrlLower"]; selamatJalanylLower = doc["data"]["selamatJalanylLower"];
        selamatJalan1lUpper = doc["data"]["selamatJalan1lUpper"]; selamatJalan2lUpper = doc["data"]["selamatJalan2lUpper"]; selamatJalan3lUpper = doc["data"]["selamatJalan3lUpper"]; selamatJalan4lUpper = doc["data"]["selamatJalan4lUpper"]; selamatJalan5lUpper = doc["data"]["selamatJalan5lUpper"]; selamatJalanplUpper = doc["data"]["selamatJalanplUpper"]; selamatJalanrlUpper = doc["data"]["selamatJalanrlUpper"]; selamatJalanylUpper = doc["data"]["selamatJalanylUpper"];
        path += "\n (selamatJalan) loaded.";
        break;
      case 105:
        waalaikumsalam1rLower = doc["data"]["waalaikumsalam1rLower"]; waalaikumsalam2rLower = doc["data"]["waalaikumsalam2rLower"]; waalaikumsalam3rLower = doc["data"]["waalaikumsalam3rLower"]; waalaikumsalam4rLower = doc["data"]["waalaikumsalam4rLower"]; waalaikumsalam5rLower = doc["data"]["waalaikumsalam5rLower"]; waalaikumsalamprLower = doc["data"]["waalaikumsalamprLower"]; waalaikumsalamrrLower = doc["data"]["waalaikumsalamrrLower"]; waalaikumsalamyrLower = doc["data"]["waalaikumsalamyrLower"];
        waalaikumsalam1rUpper = doc["data"]["waalaikumsalam1rUpper"]; waalaikumsalam2rUpper = doc["data"]["waalaikumsalam2rUpper"]; waalaikumsalam3rUpper = doc["data"]["waalaikumsalam3rUpper"]; waalaikumsalam4rUpper = doc["data"]["waalaikumsalam4rUpper"]; waalaikumsalam5rUpper = doc["data"]["waalaikumsalam5rUpper"]; waalaikumsalamprUpper = doc["data"]["waalaikumsalamprUpper"]; waalaikumsalamrrUpper = doc["data"]["waalaikumsalamrrUpper"]; waalaikumsalamyrUpper = doc["data"]["waalaikumsalamyrUpper"];
        waalaikumsalam1lLower = doc["data"]["waalaikumsalam1lLower"]; waalaikumsalam2lLower = doc["data"]["waalaikumsalam2lLower"]; waalaikumsalam3lLower = doc["data"]["waalaikumsalam3lLower"]; waalaikumsalam4lLower = doc["data"]["waalaikumsalam4lLower"]; waalaikumsalam5lLower = doc["data"]["waalaikumsalam5lLower"]; waalaikumsalamplLower = doc["data"]["waalaikumsalamplLower"]; waalaikumsalamrlLower = doc["data"]["waalaikumsalamrlLower"]; waalaikumsalamylLower = doc["data"]["waalaikumsalamylLower"];
        waalaikumsalam1lUpper = doc["data"]["waalaikumsalam1lUpper"]; waalaikumsalam2lUpper = doc["data"]["waalaikumsalam2lUpper"]; waalaikumsalam3lUpper = doc["data"]["waalaikumsalam3lUpper"]; waalaikumsalam4lUpper = doc["data"]["waalaikumsalam4lUpper"]; waalaikumsalam5lUpper = doc["data"]["waalaikumsalam5lUpper"]; waalaikumsalamplUpper = doc["data"]["waalaikumsalamplUpper"]; waalaikumsalamrlUpper = doc["data"]["waalaikumsalamrlUpper"]; waalaikumsalamylUpper = doc["data"]["waalaikumsalamylUpper"];
        path += "\n (waalaikumsalam) loaded.";
        break;
      case 1000:
        n0_1rLower = doc["data"]["n0_1rLower"]; n0_2rLower = doc["data"]["n0_2rLower"]; n0_3rLower = doc["data"]["n0_3rLower"]; n0_4rLower = doc["data"]["n0_4rLower"]; n0_5rLower = doc["data"]["n0_5rLower"]; n0_prLower = doc["data"]["n0_prLower"]; n0_rrLower = doc["data"]["n0_rrLower"]; n0_yrLower = doc["data"]["n0_yrLower"];
        n0_1rUpper = doc["data"]["n0_1rUpper"]; n0_2rUpper = doc["data"]["n0_2rUpper"]; n0_3rUpper = doc["data"]["n0_3rUpper"]; n0_4rUpper = doc["data"]["n0_4rUpper"]; n0_5rUpper = doc["data"]["n0_5rUpper"]; n0_prUpper = doc["data"]["n0_prUpper"]; n0_rrUpper = doc["data"]["n0_rrUpper"]; n0_yrUpper = doc["data"]["n0_yrUpper"];
        n0_1lLower = doc["data"]["n0_1lLower"]; n0_2lLower = doc["data"]["n0_2lLower"]; n0_3lLower = doc["data"]["n0_3lLower"]; n0_4lLower = doc["data"]["n0_4lLower"]; n0_5lLower = doc["data"]["n0_5lLower"]; n0_plLower = doc["data"]["n0_plLower"]; n0_rlLower = doc["data"]["n0_rlLower"]; n0_ylLower = doc["data"]["n0_ylLower"];
        n0_1lUpper = doc["data"]["n0_1lUpper"]; n0_2lUpper = doc["data"]["n0_2lUpper"]; n0_3lUpper = doc["data"]["n0_3lUpper"]; n0_4lUpper = doc["data"]["n0_4lUpper"]; n0_5lUpper = doc["data"]["n0_5lUpper"]; n0_plUpper = doc["data"]["n0_plUpper"]; n0_rlUpper = doc["data"]["n0_rlUpper"]; n0_ylUpper = doc["data"]["n0_ylUpper"];
        path += "\n (0) loaded.";
        break;
      case 1001:
        n1_1rLower = doc["data"]["n1_1rLower"]; n1_2rLower = doc["data"]["n1_2rLower"]; n1_3rLower = doc["data"]["n1_3rLower"]; n1_4rLower = doc["data"]["n1_4rLower"]; n1_5rLower = doc["data"]["n1_5rLower"]; n1_prLower = doc["data"]["n1_prLower"]; n1_rrLower = doc["data"]["n1_rrLower"]; n1_yrLower = doc["data"]["n1_yrLower"];
        n1_1rUpper = doc["data"]["n1_1rUpper"]; n1_2rUpper = doc["data"]["n1_2rUpper"]; n1_3rUpper = doc["data"]["n1_3rUpper"]; n1_4rUpper = doc["data"]["n1_4rUpper"]; n1_5rUpper = doc["data"]["n1_5rUpper"]; n1_prUpper = doc["data"]["n1_prUpper"]; n1_rrUpper = doc["data"]["n1_rrUpper"]; n1_yrUpper = doc["data"]["n1_yrUpper"];
        n1_1lLower = doc["data"]["n1_1lLower"]; n1_2lLower = doc["data"]["n1_2lLower"]; n1_3lLower = doc["data"]["n1_3lLower"]; n1_4lLower = doc["data"]["n1_4lLower"]; n1_5lLower = doc["data"]["n1_5lLower"]; n1_plLower = doc["data"]["n1_plLower"]; n1_rlLower = doc["data"]["n1_rlLower"]; n1_ylLower = doc["data"]["n1_ylLower"];
        n1_1lUpper = doc["data"]["n1_1lUpper"]; n1_2lUpper = doc["data"]["n1_2lUpper"]; n1_3lUpper = doc["data"]["n1_3lUpper"]; n1_4lUpper = doc["data"]["n1_4lUpper"]; n1_5lUpper = doc["data"]["n1_5lUpper"]; n1_plUpper = doc["data"]["n1_plUpper"]; n1_rlUpper = doc["data"]["n1_rlUpper"]; n1_ylUpper = doc["data"]["n1_ylUpper"];
        path += "\n (1) loaded.";
        break;
      case 1002:
        n2_1rLower = doc["data"]["n2_1rLower"]; n2_2rLower = doc["data"]["n2_2rLower"]; n2_3rLower = doc["data"]["n2_3rLower"]; n2_4rLower = doc["data"]["n2_4rLower"]; n2_5rLower = doc["data"]["n2_5rLower"]; n2_prLower = doc["data"]["n2_prLower"]; n2_rrLower = doc["data"]["n2_rrLower"]; n2_yrLower = doc["data"]["n2_yrLower"];
        n2_1rUpper = doc["data"]["n2_1rUpper"]; n2_2rUpper = doc["data"]["n2_2rUpper"]; n2_3rUpper = doc["data"]["n2_3rUpper"]; n2_4rUpper = doc["data"]["n2_4rUpper"]; n2_5rUpper = doc["data"]["n2_5rUpper"]; n2_prUpper = doc["data"]["n2_prUpper"]; n2_rrUpper = doc["data"]["n2_rrUpper"]; n2_yrUpper = doc["data"]["n2_yrUpper"];
        n2_1lLower = doc["data"]["n2_1lLower"]; n2_2lLower = doc["data"]["n2_2lLower"]; n2_3lLower = doc["data"]["n2_3lLower"]; n2_4lLower = doc["data"]["n2_4lLower"]; n2_5lLower = doc["data"]["n2_5lLower"]; n2_plLower = doc["data"]["n2_plLower"]; n2_rlLower = doc["data"]["n2_rlLower"]; n2_ylLower = doc["data"]["n2_ylLower"];
        n2_1lUpper = doc["data"]["n2_1lUpper"]; n2_2lUpper = doc["data"]["n2_2lUpper"]; n2_3lUpper = doc["data"]["n2_3lUpper"]; n2_4lUpper = doc["data"]["n2_4lUpper"]; n2_5lUpper = doc["data"]["n2_5lUpper"]; n2_plUpper = doc["data"]["n2_plUpper"]; n2_rlUpper = doc["data"]["n2_rlUpper"]; n2_ylUpper = doc["data"]["n2_ylUpper"];
        path += "\n (2) loaded.";
        break;
      case 1003:
        n3_1rLower = doc["data"]["n3_1rLower"]; n3_2rLower = doc["data"]["n3_2rLower"]; n3_3rLower = doc["data"]["n3_3rLower"]; n3_4rLower = doc["data"]["n3_4rLower"]; n3_5rLower = doc["data"]["n3_5rLower"]; n3_prLower = doc["data"]["n3_prLower"]; n3_rrLower = doc["data"]["n3_rrLower"]; n3_yrLower = doc["data"]["n3_yrLower"];
        n3_1rUpper = doc["data"]["n3_1rUpper"]; n3_2rUpper = doc["data"]["n3_2rUpper"]; n3_3rUpper = doc["data"]["n3_3rUpper"]; n3_4rUpper = doc["data"]["n3_4rUpper"]; n3_5rUpper = doc["data"]["n3_5rUpper"]; n3_prUpper = doc["data"]["n3_prUpper"]; n3_rrUpper = doc["data"]["n3_rrUpper"]; n3_yrUpper = doc["data"]["n3_yrUpper"];
        n3_1lLower = doc["data"]["n3_1lLower"]; n3_2lLower = doc["data"]["n3_2lLower"]; n3_3lLower = doc["data"]["n3_3lLower"]; n3_4lLower = doc["data"]["n3_4lLower"]; n3_5lLower = doc["data"]["n3_5lLower"]; n3_plLower = doc["data"]["n3_plLower"]; n3_rlLower = doc["data"]["n3_rlLower"]; n3_ylLower = doc["data"]["n3_ylLower"];
        n3_1lUpper = doc["data"]["n3_1lUpper"]; n3_2lUpper = doc["data"]["n3_2lUpper"]; n3_3lUpper = doc["data"]["n3_3lUpper"]; n3_4lUpper = doc["data"]["n3_4lUpper"]; n3_5lUpper = doc["data"]["n3_5lUpper"]; n3_plUpper = doc["data"]["n3_plUpper"]; n3_rlUpper = doc["data"]["n3_rlUpper"]; n3_ylUpper = doc["data"]["n3_ylUpper"];
        path += "\n (3) loaded.";
        break;
      case 1004:
        n4_1rLower = doc["data"]["n4_1rLower"]; n4_2rLower = doc["data"]["n4_2rLower"]; n4_3rLower = doc["data"]["n4_3rLower"]; n4_4rLower = doc["data"]["n4_4rLower"]; n4_5rLower = doc["data"]["n4_5rLower"]; n4_prLower = doc["data"]["n4_prLower"]; n4_rrLower = doc["data"]["n4_rrLower"]; n4_yrLower = doc["data"]["n4_yrLower"];
        n4_1rUpper = doc["data"]["n4_1rUpper"]; n4_2rUpper = doc["data"]["n4_2rUpper"]; n4_3rUpper = doc["data"]["n4_3rUpper"]; n4_4rUpper = doc["data"]["n4_4rUpper"]; n4_5rUpper = doc["data"]["n4_5rUpper"]; n4_prUpper = doc["data"]["n4_prUpper"]; n4_rrUpper = doc["data"]["n4_rrUpper"]; n4_yrUpper = doc["data"]["n4_yrUpper"];
        n4_1lLower = doc["data"]["n4_1lLower"]; n4_2lLower = doc["data"]["n4_2lLower"]; n4_3lLower = doc["data"]["n4_3lLower"]; n4_4lLower = doc["data"]["n4_4lLower"]; n4_5lLower = doc["data"]["n4_5lLower"]; n4_plLower = doc["data"]["n4_plLower"]; n4_rlLower = doc["data"]["n4_rlLower"]; n4_ylLower = doc["data"]["n4_ylLower"];
        n4_1lUpper = doc["data"]["n4_1lUpper"]; n4_2lUpper = doc["data"]["n4_2lUpper"]; n4_3lUpper = doc["data"]["n4_3lUpper"]; n4_4lUpper = doc["data"]["n4_4lUpper"]; n4_5lUpper = doc["data"]["n4_5lUpper"]; n4_plUpper = doc["data"]["n4_plUpper"]; n4_rlUpper = doc["data"]["n4_rlUpper"]; n4_ylUpper = doc["data"]["n4_ylUpper"];
        path += "\n (4) loaded.";
        break;
      case 1005:
        n5_1rLower = doc["data"]["n5_1rLower"]; n5_2rLower = doc["data"]["n5_2rLower"]; n5_3rLower = doc["data"]["n5_3rLower"]; n5_4rLower = doc["data"]["n5_4rLower"]; n5_5rLower = doc["data"]["n5_5rLower"]; n5_prLower = doc["data"]["n5_prLower"]; n5_rrLower = doc["data"]["n5_rrLower"]; n5_yrLower = doc["data"]["n5_yrLower"];
        n5_1rUpper = doc["data"]["n5_1rUpper"]; n5_2rUpper = doc["data"]["n5_2rUpper"]; n5_3rUpper = doc["data"]["n5_3rUpper"]; n5_4rUpper = doc["data"]["n5_4rUpper"]; n5_5rUpper = doc["data"]["n5_5rUpper"]; n5_prUpper = doc["data"]["n5_prUpper"]; n5_rrUpper = doc["data"]["n5_rrUpper"]; n5_yrUpper = doc["data"]["n5_yrUpper"];
        n5_1lLower = doc["data"]["n5_1lLower"]; n5_2lLower = doc["data"]["n5_2lLower"]; n5_3lLower = doc["data"]["n5_3lLower"]; n5_4lLower = doc["data"]["n5_4lLower"]; n5_5lLower = doc["data"]["n5_5lLower"]; n5_plLower = doc["data"]["n5_plLower"]; n5_rlLower = doc["data"]["n5_rlLower"]; n5_ylLower = doc["data"]["n5_ylLower"];
        n5_1lUpper = doc["data"]["n5_1lUpper"]; n5_2lUpper = doc["data"]["n5_2lUpper"]; n5_3lUpper = doc["data"]["n5_3lUpper"]; n5_4lUpper = doc["data"]["n5_4lUpper"]; n5_5lUpper = doc["data"]["n5_5lUpper"]; n5_plUpper = doc["data"]["n5_plUpper"]; n5_rlUpper = doc["data"]["n5_rlUpper"]; n5_ylUpper = doc["data"]["n5_ylUpper"];
        path += "\n (5) loaded.";
        break;
      case 1006:
        n6_1rLower = doc["data"]["n6_1rLower"]; n6_2rLower = doc["data"]["n6_2rLower"]; n6_3rLower = doc["data"]["n6_3rLower"]; n6_4rLower = doc["data"]["n6_4rLower"]; n6_5rLower = doc["data"]["n6_5rLower"]; n6_prLower = doc["data"]["n6_prLower"]; n6_rrLower = doc["data"]["n6_rrLower"]; n6_yrLower = doc["data"]["n6_yrLower"];
        n6_1rUpper = doc["data"]["n6_1rUpper"]; n6_2rUpper = doc["data"]["n6_2rUpper"]; n6_3rUpper = doc["data"]["n6_3rUpper"]; n6_4rUpper = doc["data"]["n6_4rUpper"]; n6_5rUpper = doc["data"]["n6_5rUpper"]; n6_prUpper = doc["data"]["n6_prUpper"]; n6_rrUpper = doc["data"]["n6_rrUpper"]; n6_yrUpper = doc["data"]["n6_yrUpper"];
        n6_1lLower = doc["data"]["n6_1lLower"]; n6_2lLower = doc["data"]["n6_2lLower"]; n6_3lLower = doc["data"]["n6_3lLower"]; n6_4lLower = doc["data"]["n6_4lLower"]; n6_5lLower = doc["data"]["n6_5lLower"]; n6_plLower = doc["data"]["n6_plLower"]; n6_rlLower = doc["data"]["n6_rlLower"]; n6_ylLower = doc["data"]["n6_ylLower"];
        n6_1lUpper = doc["data"]["n6_1lUpper"]; n6_2lUpper = doc["data"]["n6_2lUpper"]; n6_3lUpper = doc["data"]["n6_3lUpper"]; n6_4lUpper = doc["data"]["n6_4lUpper"]; n6_5lUpper = doc["data"]["n6_5lUpper"]; n6_plUpper = doc["data"]["n6_plUpper"]; n6_rlUpper = doc["data"]["n6_rlUpper"]; n6_ylUpper = doc["data"]["n6_ylUpper"];
        path += "\n (6) loaded.";
        break;
      case 1007:
        n7_1rLower = doc["data"]["n7_1rLower"]; n7_2rLower = doc["data"]["n7_2rLower"]; n7_3rLower = doc["data"]["n7_3rLower"]; n7_4rLower = doc["data"]["n7_4rLower"]; n7_5rLower = doc["data"]["n7_5rLower"]; n7_prLower = doc["data"]["n7_prLower"]; n7_rrLower = doc["data"]["n7_rrLower"]; n7_yrLower = doc["data"]["n7_yrLower"];
        n7_1rUpper = doc["data"]["n7_1rUpper"]; n7_2rUpper = doc["data"]["n7_2rUpper"]; n7_3rUpper = doc["data"]["n7_3rUpper"]; n7_4rUpper = doc["data"]["n7_4rUpper"]; n7_5rUpper = doc["data"]["n7_5rUpper"]; n7_prUpper = doc["data"]["n7_prUpper"]; n7_rrUpper = doc["data"]["n7_rrUpper"]; n7_yrUpper = doc["data"]["n7_yrUpper"];
        n7_1lLower = doc["data"]["n7_1lLower"]; n7_2lLower = doc["data"]["n7_2lLower"]; n7_3lLower = doc["data"]["n7_3lLower"]; n7_4lLower = doc["data"]["n7_4lLower"]; n7_5lLower = doc["data"]["n7_5lLower"]; n7_plLower = doc["data"]["n7_plLower"]; n7_rlLower = doc["data"]["n7_rlLower"]; n7_ylLower = doc["data"]["n7_ylLower"];
        n7_1lUpper = doc["data"]["n7_1lUpper"]; n7_2lUpper = doc["data"]["n7_2lUpper"]; n7_3lUpper = doc["data"]["n7_3lUpper"]; n7_4lUpper = doc["data"]["n7_4lUpper"]; n7_5lUpper = doc["data"]["n7_5lUpper"]; n7_plUpper = doc["data"]["n7_plUpper"]; n7_rlUpper = doc["data"]["n7_rlUpper"]; n7_ylUpper = doc["data"]["n7_ylUpper"];
        path += "\n (7) loaded.";
        break;
      case 1008:
        n8_1rLower = doc["data"]["n8_1rLower"]; n8_2rLower = doc["data"]["n8_2rLower"]; n8_3rLower = doc["data"]["n8_3rLower"]; n8_4rLower = doc["data"]["n8_4rLower"]; n8_5rLower = doc["data"]["n8_5rLower"]; n8_prLower = doc["data"]["n8_prLower"]; n8_rrLower = doc["data"]["n8_rrLower"]; n8_yrLower = doc["data"]["n8_yrLower"];
        n8_1rUpper = doc["data"]["n8_1rUpper"]; n8_2rUpper = doc["data"]["n8_2rUpper"]; n8_3rUpper = doc["data"]["n8_3rUpper"]; n8_4rUpper = doc["data"]["n8_4rUpper"]; n8_5rUpper = doc["data"]["n8_5rUpper"]; n8_prUpper = doc["data"]["n8_prUpper"]; n8_rrUpper = doc["data"]["n8_rrUpper"]; n8_yrUpper = doc["data"]["n8_yrUpper"];
        n8_1lLower = doc["data"]["n8_1lLower"]; n8_2lLower = doc["data"]["n8_2lLower"]; n8_3lLower = doc["data"]["n8_3lLower"]; n8_4lLower = doc["data"]["n8_4lLower"]; n8_5lLower = doc["data"]["n8_5lLower"]; n8_plLower = doc["data"]["n8_plLower"]; n8_rlLower = doc["data"]["n8_rlLower"]; n8_ylLower = doc["data"]["n8_ylLower"];
        n8_1lUpper = doc["data"]["n8_1lUpper"]; n8_2lUpper = doc["data"]["n8_2lUpper"]; n8_3lUpper = doc["data"]["n8_3lUpper"]; n8_4lUpper = doc["data"]["n8_4lUpper"]; n8_5lUpper = doc["data"]["n8_5lUpper"]; n8_plUpper = doc["data"]["n8_plUpper"]; n8_rlUpper = doc["data"]["n8_rlUpper"]; n8_ylUpper = doc["data"]["n8_ylUpper"];
        path += "\n (8) loaded.";
        break;
      case 1009:
        n9_1rLower = doc["data"]["n9_1rLower"]; n9_2rLower = doc["data"]["n9_2rLower"]; n9_3rLower = doc["data"]["n9_3rLower"]; n9_4rLower = doc["data"]["n9_4rLower"]; n9_5rLower = doc["data"]["n9_5rLower"]; n9_prLower = doc["data"]["n9_prLower"]; n9_rrLower = doc["data"]["n9_rrLower"]; n9_yrLower = doc["data"]["n9_yrLower"];
        n9_1rUpper = doc["data"]["n9_1rUpper"]; n9_2rUpper = doc["data"]["n9_2rUpper"]; n9_3rUpper = doc["data"]["n9_3rUpper"]; n9_4rUpper = doc["data"]["n9_4rUpper"]; n9_5rUpper = doc["data"]["n9_5rUpper"]; n9_prUpper = doc["data"]["n9_prUpper"]; n9_rrUpper = doc["data"]["n9_rrUpper"]; n9_yrUpper = doc["data"]["n9_yrUpper"];
        n9_1lLower = doc["data"]["n9_1lLower"]; n9_2lLower = doc["data"]["n9_2lLower"]; n9_3lLower = doc["data"]["n9_3lLower"]; n9_4lLower = doc["data"]["n9_4lLower"]; n9_5lLower = doc["data"]["n9_5lLower"]; n9_plLower = doc["data"]["n9_plLower"]; n9_rlLower = doc["data"]["n9_rlLower"]; n9_ylLower = doc["data"]["n9_ylLower"];
        n9_1lUpper = doc["data"]["n9_1lUpper"]; n9_2lUpper = doc["data"]["n9_2lUpper"]; n9_3lUpper = doc["data"]["n9_3lUpper"]; n9_4lUpper = doc["data"]["n9_4lUpper"]; n9_5lUpper = doc["data"]["n9_5lUpper"]; n9_plUpper = doc["data"]["n9_plUpper"]; n9_rlUpper = doc["data"]["n9_rlUpper"]; n9_ylUpper = doc["data"]["n9_ylUpper"];
        path += "\n (9) loaded.";
        break;
      default:
        path += "\n nothing loaded.";
        break;
    }
    Serial.println(path);
  }
  upd[0] = "0";
  upd[1] = "0";
}

void listAllFiles() {
  File root = SPIFFS.open("/");
  File file = root.openNextFile();
  while (file) {
    Serial.print("FILE: ");
    Serial.println(file.name());
    file = root.openNextFile();
  }
}

void TaskMPUcode( void * parameter) {
  Serial.print("Task MPU running on core ");
  Serial.print(xPortGetCoreID());
  Serial.print(" with stack size:");
  Serial.println(uxTaskGetStackHighWaterMark(NULL));
  for (;;) {//loop forever
    while (!calibratingMPU) {
      //update mpu values
      mpu.Execute();
    }
    TIMERG0.wdt_wprotect = TIMG_WDT_WKEY_VALUE;
    TIMERG0.wdt_feed = 1;
    TIMERG0.wdt_wprotect = 0;
    delay(1000);
  }
  //  Serial.println("Ending task MPU");
  //  vTaskDelete( NULL );
}

bool ro = false;
void checkCore() {
  Serial.print("Task Main running on core ");
  Serial.print(xPortGetCoreID());
  Serial.print(" with stack size:");
  Serial.println(uxTaskGetStackHighWaterMark(NULL));
  ro = true;
}

void initVars() {
  const int arrsize = sizeof(vars) / sizeof(String);
  for (int i = 0; i < arrsize; i++) {
    Serial.print("Loading...");
    Serial.println(vars[i]);
    upd[0] = "1";
    upd[1] = vars[i];
    updateVars();
    delay(10);
  }
}
/**/

void setup() {
  // Setup ledc (dimming light) timer and attach timer to a led pin
  ledcSetup(LEDC_CHANNEL_0, LEDC_BASE_FREQ, LEDC_TIMER_13_BIT);
  ledcAttachPin(LED_PIN, LEDC_CHANNEL_0);

  if (!SPIFFS.begin(true)) {
    Serial.println("An Error has occurred while mounting SPIFFS");
    return;
  }

  Serial.begin(115200);
  //  while (!Serial) {
  //    ; // wait for serial port to connect. Needed for native USB port only, disable when running with battery !!!
  //  }
  //ADC2 only -  Save ADC2 control register value : Do this before begin Wifi/Bluetooth
  reg_b = READ_PERI_REG(SENS_SAR_READ_CTRL2_REG);

  WiFi.mode(WIFI_STA);
  //  WiFi.mode(WIFI_AP_STA);
  //  //access point
  //  Serial.println("Creating Accesspoint...");
  //  WiFi.softAP(apssid,apsecret,7,0,5);
  //  Serial.print("IP address:\t");
  //  Serial.println(WiFi.softAPIP());
  //station
  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  Serial.println(pos ? "-======================== RIGHT HAND ========================-" : "-======================== LEFT HAND ========================-");

  // Send web page with input fields to client
  server.on("/", HTTP_GET, [](AsyncWebServerRequest * request) {
    request->send_P(200, "text/html", index_html);
    String inputMessage;
    // GET inputJson value on <ESP_IP>/?inputJson=<inputMessage>
    if (request->hasParam(PARAM_JSON)) {
      inputMessage = request->getParam(PARAM_JSON)->value();
      //Serial.println(inputMessage);
      DynamicJsonDocument doc(2048);
      DeserializationError error = deserializeJson(doc, inputMessage);
      if (error) {
        Serial.println(F("Error parsing JSON (server.on)"));
        return;
      }
      doc["data"] = "";
      doc.shrinkToFit(); //reduces the capacity of the memory pool to match the current usage
      String lbl = doc["label"];
      if (lbl.length() > 0) {
        String path = "/inputJson_" + lbl + ".txt";
        writeFile(SPIFFS, path.c_str(), inputMessage.c_str(), lbl.c_str());
        doc.clear();
      } else {
        Serial.println("Json label not found!");
      }
    } else if (request->hasParam(PARAM_RCF)) {
      calibratingFLEX = true;
      Serial.println("Flex sensor calibration start...");
      //  if (!calibrated) calibration();
      calibration();
      Serial.println("Calibration end...");
      calibratingFLEX = false;
    } else if (request->hasParam(PARAM_RCM)) {
      calibratingMPU = true;
      Serial.println("MPU sensor calibration start after 5s...");
      // Initialization
      mpu.Initialize();
      delay(4000);
      ledcAnalogWrite(LEDC_CHANNEL_0, 255);
      delay(500);
      ledcAnalogWrite(LEDC_CHANNEL_0, 0);
      delay(500);
      ledcAnalogWrite(LEDC_CHANNEL_0, 255);
      Serial.println("MPU calibration start...");
      mpu.Calibrate();
      Serial.println("MPU calibration complete!");
      ledcAnalogWrite(LEDC_CHANNEL_0, 0);
      calibratingMPU = false;
    } else if (request->hasParam(PARAM_RCA)) {
      calibratingFLEX = true;
      calibratingMPU = true;
      Serial.println("Flex sensor calibration start...");
      //  if (!calibrated) calibration();
      calibration();
      Serial.println("Calibration end...");
      Serial.println("MPU sensor calibration start after 5s...");
      // Initialization
      mpu.Initialize();
      delay(4000);
      ledcAnalogWrite(LEDC_CHANNEL_0, 255);
      delay(500);
      ledcAnalogWrite(LEDC_CHANNEL_0, 0);
      delay(500);
      ledcAnalogWrite(LEDC_CHANNEL_0, 255);
      Serial.println("MPU calibration start...");
      mpu.Calibrate();
      Serial.println("MPU calibration complete!");
      ledcAnalogWrite(LEDC_CHANNEL_0, 0);
      calibratingFLEX = false;
      calibratingMPU = false;
    } else {
      inputMessage = "No message sent";
    }
    request->send(200);
  });
  server.onNotFound(notFound);
  server.begin();

  //Firebase initialization
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
  //Set database read timeout to 10 seconds (max 15 minutes)
  Firebase.setReadTimeout(firebaseData, 10000);
  //tiny, small, medium, large and unlimited.
  //Size and its write timeout e.g. tiny (1s), small (10s), medium (30s) and large (60s).
  Firebase.setwriteSizeLimit(firebaseData, "tiny");

  // callibrating the sensors for adaptivity with different bends
  //  calibrated = (readFile(SPIFFS, "/inputCal.txt") == 1) ? true : false;
  Serial.println("Flex sensor calibration start...");
  //  if (!calibrated) calibration();
  calibration();
  Serial.println("Calibration end...");
  Serial.println("MPU sensor calibration start after 5s...");
  // Initialization
  mpu.Initialize();
  delay(4000);
  ledcAnalogWrite(LEDC_CHANNEL_0, 255);
  delay(500);
  ledcAnalogWrite(LEDC_CHANNEL_0, 0);
  delay(500);
  ledcAnalogWrite(LEDC_CHANNEL_0, 255);
  Serial.println("MPU calibration start...");
  mpu.Calibrate();
  Serial.println("MPU calibration complete!");
  ledcAnalogWrite(LEDC_CHANNEL_0, 0);
  Serial.println("Loading vars:");
  initVars();
  xTaskCreatePinnedToCore(
    TaskMPUcode, /* Function to implement the task */
    "TaskMPU", /* Name of the task */
    10240,  /* Stack size in words */
    NULL,  /* Task input parameter */
    5,  /* Priority of the task 0-5(lowest-highest) */
    &TaskMPU,  /* Task handle. */
    0); /* Core where the task should run */
  delay(1000);
}
/**/
/********************************************************************************************Loop**/
void loop() {//main loop automatically run on esp32 processor core 1
  while (!calibratingFLEX && !calibratingMPU) {
    if (!ro) checkCore();
    if (upd[0] == "1") updateVars();
    // reading sensor value
    flexADC1 = readSensor(FLEX_PIN1);
    flexADC2 = readSensor(FLEX_PIN2);
    flexADC3 = readSensor(FLEX_PIN3);
    flexADC4 = readSensor(FLEX_PIN4);
    flexADC5 = readSensor(FLEX_PIN5);
    // map value between min and high
    // value, min ,max
    unsigned int cFlexADC1 = constrain(flexADC1, sensorMin1, sensorMax1);
    unsigned int cFlexADC2 = constrain(flexADC2, sensorMin2, sensorMax2);
    unsigned int cFlexADC3 = constrain(flexADC3, sensorMin3, sensorMax3);
    unsigned int cFlexADC4 = constrain(flexADC4, sensorMin4, sensorMax4);
    unsigned int cFlexADC5 = constrain(flexADC5, sensorMin5, sensorMax5);

    // convert value to a new range (0˚ - 90˚)
    // value, oldrangemin, oldrangemax, newrangemin, newrangemax
    int angle1 = map(cFlexADC1, sensorMin1, sensorMax1, 0, 90);
    int angle2 = map(cFlexADC2, sensorMin2, sensorMax2, 0, 90);
    int angle3 = map(cFlexADC3, sensorMin3, sensorMax3, 0, 90);
    int angle4 = map(cFlexADC4, sensorMin4, sensorMax4, 0, 90);
    int angle5 = map(cFlexADC5, sensorMin5, sensorMax5, 0, 90);

    float Ax = mpu.GetAccX();
    float Ay = mpu.GetAccY();
    float Az = mpu.GetAccZ();
    float Gx = mpu.GetGyroX();
    float Gy = mpu.GetGyroY();
    float Gz = mpu.GetGyroZ();
    float Axangle = mpu.GetAngAccX();
    float Ayangle = mpu.GetAngAccY();
    float Gxangle = mpu.GetAngGyroX();
    float Gyangle = mpu.GetAngGyroY();
    float Gzangle = mpu.GetAngGyroZ();
    float roll = mpu.GetAngX();
    float pitch = mpu.GetAngY();
    float yaw = mpu.GetAngZ();
    if (millis() - timer > 2000) {
      Serial.print(millis() / 1000);
      printf("\tFx1 raw:%d Fx1 val:%d Fx1 angle:%d˚\n", flexADC1, cFlexADC1, angle1);
      Serial.print(millis() / 1000);
      printf(" \tFx2 raw:%d Fx2 val:%d Fx2 angle:%d˚\n", flexADC2, cFlexADC2, angle2);
      Serial.print(millis() / 1000);
      printf("\tFx3 raw:%d Fx3 val:%d Fx3 angle:%d˚\n", flexADC3, cFlexADC3, angle3);
      Serial.print(millis() / 1000);
      printf("\tFx4 raw:%d Fx4 val:%d Fx4 angle:%d˚\n", flexADC4, cFlexADC4, angle4);
      Serial.print(millis() / 1000);
      printf("\tFx5 raw:%d Fx5 val:%d Fx5 angle:%d˚\n", flexADC5, cFlexADC5, angle5);

      Serial.print(millis() / 1000);
      printf("\tAx=%.3f g Ay=%.3f g Az=%.3f g Gx=%.3f °/s Gy=%.3f °/s Gz=%.3f °/s\n", Ax, Ay, Az, Gx, Gy, Gz);
      printf("\tAxangle=%.3f° Ayangle=%.3f° Gxangle=%.3f° Gyangle=%.3f° Gzangle=%.3f°\n", Axangle, Ayangle, Gxangle, Gyangle, Gzangle);
      printf("\tRoll=%.3f° Pitch=%.3f° Yaw=%.3f°\n", roll, pitch, yaw);

      //printf(" %d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n", a1rLower, a2rLower, a3rLower, a4rLower, a5rLower, aprLower, arrLower, ayrLower, a1rUpper, a2rUpper, a3rUpper, a4rUpper, a5rUpper, aprUpper, arrUpper, ayrUpper, a1lLower, a2lLower, a3lLower, a4lLower, a5lLower, aplLower, arlLower, aylLower, a1lUpper, a2lUpper, a3lUpper, a4lUpper, a5lUpper, aplUpper, arlUpper, aylUpper);

      /* fbase test */
      //sendData((int)random(1, 9), true); //data, as data, serial print
      timer = millis();
      temp = "0";
      symbolTemp = -1;
    }

    /* detect character */
    //sendOnce(detectChar(angle1, angle2, angle3, angle4, angle5, pitch, roll, yaw));
    sendData(detectChar(angle1, angle2, angle3, angle4, angle5, pitch, roll, yaw), true);
    delay(50);
  }
  TIMERG0.wdt_wprotect = TIMG_WDT_WKEY_VALUE;
  TIMERG0.wdt_feed = 1;
  TIMERG0.wdt_wprotect = 0;
  delay(100);
}
/**/
