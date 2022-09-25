#include <OneWire.h>
#include <DallasTemperature.h>
#include <Keypad.h>
#include <LiquidCrystal.h>
#include <Servo.h>

const char compile_date[] = __TIME__;

// lcd 16x2
const byte rs = 16, en = 18, d4 = 19, d5 = 20, d6 = 21, d7 = 22;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

byte degreeChar[8] = {0b01100, 0b10010, 0b10010, 0b01100, 0b00000, 0b00000, 0b00000, 0b00000};

// Servo
const byte pinServoLpg = 12;
int16_t servoPos = 0;
Servo servoLpg;

// Sensors
const byte pinTemp = 24;
const byte pinFlame = 31;
const byte pinLpgIgniter = 30;
OneWire oneWire(pinTemp);
DallasTemperature suhu(&oneWire);

// Keyboard
const byte ROWS = 4;
const byte COLS = 4;
//define the cymbols on the buttons of the keypads
char hexaKeys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

byte colPins[COLS] = {0, 1, 2, 3};
byte rowPins[ROWS] = {4, 5, 6, 7};

//initialize an instance of class NewKeypad
Keypad myKbd = Keypad( makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS);

//-- vars
//pid
uint8_t pidMode = 1;
bool runPID = false;
float valPid, valError1, valError2, valSampleT, valSig;
float valSetPoint = -1.0, valKonstProp = -1.0, valKonstInt = -1.0, valKonstDeriv = -1.0;

//sensor
int valSuhu;

//servo
int valSudut = 0;
