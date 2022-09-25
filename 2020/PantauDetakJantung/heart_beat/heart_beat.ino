#include <Wire.h>
#include <WiFi.h>
#include "MAX30100_PulseOximeter.h"
#include <FirebaseESP32.h>

#define REPORTING_PERIOD_MS 1000

#define FIREBASE_HOST "..." //project database url
#define FIREBASE_AUTH "..." //database secret
#define WIFI_SSID "..."
#define WIFI_PASSWORD "..."
//Define FirebaseESP32 data object
FirebaseData firebaseData;

#define detakPath "/jtd/Adit/data/DetakJantung"
#define oksigenPath "/jtd/Adit/data/Oksigen"

void sendFB(float detakjantung, float Oksigen, bool printSerial = false) {
  // set string value
  String packet = "";
  packet = ( Firebase.setFloat(firebaseData, detakPath, detakjantung) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  printSerial ? Serial.println(packet) : Serial.print("");
  packet = ( Firebase.setFloat(firebaseData, oksigenPath, Oksigen) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  printSerial ? Serial.println(packet) : Serial.print("");
}

// PulseOximeter is the higher level interface to the sensor
// it offers:
// * beat detection reporting
// * heart rate calculation
// * SpO2 (oxidation level) calculation
PulseOximeter pox;

uint32_t tsLastReport = 0;

// Callback (registered below) fired when a pulse is detected
void onBeatDetected(){
  Serial.println("Beat!");
}

void setup()
{
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  //Firebase initialization
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
  //Set database read timeout to 10 seconds (max 15 minutes)
  Firebase.setReadTimeout(firebaseData, 10000);
  //tiny, small, medium, large and unlimited.
  //Size and its write timeout e.g. tiny (1s), small (10s), medium (30s) and large (60s).
  Firebase.setwriteSizeLimit(firebaseData, "tiny");

  Serial.print("Initializing pulse oximeter..");

  // Initialize the PulseOximeter instance
  // Failures are generally due to an improper I2C wiring, missing power supply
  // or wrong target chip
  if (!pox.begin()) {
    Serial.println("FAILED");
    for (;;) {
      delay(100);
    }
  } else {
    Serial.println("SUCCESS");
  }

  // The default current for the IR LED is 50mA and it could be changed
  // by uncommenting the following line. Check MAX30100_Registers.h for all the
  // available options.
  // pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);

  // Register a callback for the beat detection
  pox.setOnBeatDetectedCallback(onBeatDetected);
}

void loop()
{
  // Make sure to call update as fast as possible
  pox.update();

  // Asynchronously dump heart rate and oxidation levels to the serial
  // For both, a value of 0 means "invalid"
  if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
    Serial.print("Heart rate:");
    float detakjantung = pox.getHeartRate();
    float Oksigen = pox.getSpO2();
    Serial.print(detakjantung);
    Serial.print("bpm / SpO2:");
    Serial.print(Oksigen);
    Serial.println("%");

    tsLastReport = millis();
    sendFB(detakjantung, Oksigen);
  }
}
