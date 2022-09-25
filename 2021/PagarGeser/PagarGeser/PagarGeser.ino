#include <ESP8266WiFi.h>
#include <AccelStepper.h>
#include <FirebaseESP8266.h>


#define FIREBASE_HOST "*"
#define FIREBASE_AUTH "*"
#define WIFI_SSID "*"
#define WIFI_PASSWORD "*"
#define pathGate "/aish/kontrol/pagarGeser"

FirebaseData firebaseData;

/*
   28BYJ-48 motor has 5.625 degrees per step
   360 degrees / 5.625 = 64 steps per revolution
   Example with degreeToSteps(45):
   (64 / 5.625) * 45 = 512 steps
*/
const uint8_t stepsPerRevolution = 64;
const float degreePerRevolution = 5.625;
const float gearCircumference = 12; //cm
const float gateLength = 16.5; //cm
const byte motorPin1 = D1;
const byte motorPin2 = D2;
const byte motorPin3 = D3;
const byte motorPin4 = D4;
AccelStepper stepper(AccelStepper::HALF4WIRE, motorPin1, motorPin3, motorPin2, motorPin4);

void sendFB(float suhu, float Arus, float Tegangan, float Daya) {
  // set string value
  //  String packet = "";
  //  packet = ( Firebase.setFloat(firebaseData, "MobilIlham/Suhu", suhu) ) ? "Firebase success: " + (String)firebaseData.payload() : "Firebase Error: " + (String)firebaseData.errorReason(); delay(1);
  //  Serial.println(packet);
}

bool getGateFB() {
  if (Firebase.getBool(firebaseData, pathGate)) {
    return firebaseData.boolData();
  } else {
    Serial.println(F("FAILED!"));
    Serial.println(pathGate);
    return false;
  }
}

void setGate(bool direc) {
  int16_t GATE_CLOSE = 0;
  int16_t GATE_OPEN = distanceToSteps(gateLength);
  if (direc) {
    stepper.moveTo(GATE_OPEN);
    while (stepper.currentPosition() != GATE_OPEN) {
      stepper.run();
      yield();
    }
    stepper.stop();
    stepper.runToPosition();
  } else {
    stepper.moveTo(GATE_CLOSE);
    while (stepper.currentPosition() != GATE_CLOSE) {
      stepper.run();
      yield();
    }
    stepper.stop();
    stepper.runToPosition();
  }
}

float degreeToSteps(float deg) {
  return (stepsPerRevolution / degreePerRevolution) * deg;
}

float distanceToSteps(float dist) {
  return degreeToSteps(360.0 / gearCircumference * dist);
}

void setup() {
  Serial.begin(115200);
  stepper.setMaxSpeed(1000.0);
  stepper.setAcceleration(200.0);
  stepper.setSpeed(100);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
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
  Serial.println(WiFi.localIP());

  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
  //Set database read timeout to 1 minute (max 15 minutes)
  Firebase.setReadTimeout(firebaseData, 1000 * 60);
  //tiny, small, medium, large and unlimited.
  //Size and its write timeout e.g. tiny (1s), small (10s), medium (30s) and large (60s).
  Firebase.setwriteSizeLimit(firebaseData, "small");
  Firebase.setFloatDigits(2);
  Firebase.setDoubleDigits(6);
  Serial.println("Set gate: false");
  setGate(false);
  Serial.println("Setup done.");
}
bool gateTmp = false;
void loop() {
  bool newGate = getGateFB();
  if (gateTmp != newGate) {
    setGate(newGate);
    gateTmp = newGate;
    Serial.print("Set gate: ");
    Serial.println(gateTmp);
  }
  delay(1);
  yield();
}
