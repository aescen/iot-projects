/*
   //--   Sistem Kontrol PID    --//
   //-- Suhu Tungku Malam Batik --//

   Komponen utama:
   1. Tungku malam
   2. Sensor suhu
   3. Pemantik api
   4. Sensor api
   5. Relay (pemantik api)
   6. Motor servo (keran gas)
   7. ATMega32
   8. Modul LCD 16x8
   9. Matrix Keypad 4x4
   8. NodeMCU
   9. Modul bluetooth
   10. PSU/Adaptor DC5V 2A

   Library:
   Built-in: OneWire, LiquidCrystal, Servo
   DallasTemperature: v3.9.0 - Miles Burton
   Keypad: v3.1.1 - Mark Stanley

   Board: MightyCore (https://mcudude.github.io/MightyCore/package_MCUdude_MightyCore_index.json)
*/

#include "init.h"
#include "utils.h"
#include "io.h"
#include "coms.h"
#include "menu.h"
#include "pid.h"
//#include "tests.h"

void setup() {
  lcd.begin(16, 2);
  lcd.createChar(0, degreeChar);
  servoLpg.attach(pinServoLpg);
  servoLpg.write(180); /* servo 180: tutup, 0: buka */
  suhu.begin();
  Serial.begin(57600);
  pinMode(pinFlame, INPUT);
  pinMode(pinLpgIgniter, OUTPUT);
  delay(1000);
  setLpgIgniter(LOW);
  setServo(valSudut);
  valSuhu = getTempCel();

  //testInit();
  welcomeText();
  checkSerial();
  mainMenu();
}

void loop() {
  tick();
  menuState();
  if (keyState) {
    textMenuBawah();
  }
  if (runPID) {
    PID(pidMode);
  }
  delay(1);
}
