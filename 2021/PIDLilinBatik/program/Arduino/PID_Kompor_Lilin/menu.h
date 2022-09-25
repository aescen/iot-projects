#include "menu_lilin.h"

/* start: var menu main */
const uint8_t totalMenu = 7;
const String menu[7] = {">Entry SP", ">Entry KP", ">Entry KI", ">Entry KD", ">Set Api", ">Set Lilin", ">Run"};
int8_t menuPos = (7)-1; // pos mulai dari 0, jadi di min 1, tinggal edit nilai dalam kurung
bool keyState = false;
bool screenTmp = false;
bool decPoint = false;
/* end: var menu main */

/* start: method menu main */
void textMenuAtas() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(F("Menu"));
  lcd.setCursor(10, 0);
  lcd.print("T:" + (String)(int)valSuhu + (char)223 + "C");
}
void textMenuBawah() {
  clearLcdLine(1);
  lcd.setCursor(0, 1);
  lcd.print(menu[menuPos]);
  keyState = false;
}

void mainMenu() {
  textMenuAtas();
  textMenuBawah();
}

void menuSP() {
  lcd.clear();
  lcd.print(F("Set SP:"));
  lcd.setCursor(0, 1);
  lcd.print(F("*>Simpan  C>Exit"));
  lcd.setCursor(7, 0);
  String valSetPointTmp;
  screenTmp = false;
  decPoint = false;
  while (true) {
    key = getKbd();
    if (key == '*') {
      lcd.clear();
      lcd.print(F("SP ok."));
      valSetPoint = valSetPointTmp.toDouble();
      delay(500);
      mainMenu();
      break;
    } else if (key == 'C') {
      mainMenu();
      break;
    } else {
      if (key != 'X' && key != 'A' && key != 'B' && key != 'C' && key != 'D') {
        if (key == '#' && decPoint == false) {
          if (!(strchr(valSetPointTmp.c_str(), '.'))) {
            if (valSetPointTmp.length() > 0) {
              valSetPointTmp += ".";
            } else {
              valSetPointTmp += "0.";
            }
          }
          decPoint = true;
        } else {
          valSetPointTmp += (String)key;
        }
        screenTmp = true;
      }
    }

    if (screenTmp) {
      clearLcdLine(0);
      lcd.setCursor(0, 0);
      lcd.print(F("Set SP:"));
      lcd.setCursor(7, 0);
      lcd.print(valSetPointTmp);
      screenTmp = false;
    }
  }
}

void menuKP() {
  lcd.clear();
  lcd.print(F("Set KP:"));
  lcd.setCursor(0, 1);
  lcd.print(F("*>Simpan  C>Exit"));
  lcd.setCursor(7, 0);
  String valKonstPropTmp;
  screenTmp = false;
  decPoint = false;
  while (true) {
    key = getKbd();
    if (key == '*') {
      lcd.clear();
      lcd.print(F("KP ok."));
      valKonstProp = valKonstPropTmp.toDouble();
      delay(500);
      mainMenu();
      break;
    } else if (key == 'C') {
      mainMenu();
      break;
    } else {
      if (key != 'X' && key != 'A' && key != 'B' && key != 'C' && key != 'D') {
        if (key == '#' && decPoint == false) {
          if (!(strchr(valKonstPropTmp.c_str(), '.'))) {
            if (valKonstPropTmp.length() > 0) {
              valKonstPropTmp += ".";
            } else {
              valKonstPropTmp += "0.";
            }
          }
          decPoint = true;
        } else {
          valKonstPropTmp += (String)key;
        }
        screenTmp = true;
      }
    }

    if (screenTmp) {
      clearLcdLine(0);
      lcd.setCursor(0, 0);
      lcd.print(F("Set KP:"));
      lcd.setCursor(7, 0);
      lcd.print(valKonstPropTmp);
      screenTmp = false;
    }
  }
}

void menuKI() {
  lcd.clear();
  lcd.print(F("Set KI:"));
  lcd.setCursor(0, 1);
  lcd.print(F("*>Simpan  C>Exit"));
  lcd.setCursor(7, 0);
  String valKonstIntTmp;
  screenTmp = false;
  decPoint = false;
  while (true) {
    key = getKbd();
    if (key == '*') {
      lcd.clear();
      lcd.print(F("KI ok."));
      valKonstInt = valKonstIntTmp.toDouble();
      delay(500);
      mainMenu();
      break;
    } else if (key == 'C') {
      mainMenu();
      break;
    } else {
      if (key != 'X' && key != 'A' && key != 'B' && key != 'C' && key != 'D') {
        if (key == '#' && decPoint == false) {
          if (!(strchr(valKonstIntTmp.c_str(), '.'))) {
            if (valKonstIntTmp.length() > 0) {
              valKonstIntTmp += ".";
            } else {
              valKonstIntTmp += "0.";
            }
          }
          decPoint = true;
        } else {
          valKonstIntTmp += (String)key;
        }
        screenTmp = true;
      }
    }

    if (screenTmp) {
      clearLcdLine(0);
      lcd.setCursor(0, 0);
      lcd.print(F("Set KI:"));
      lcd.setCursor(7, 0);
      lcd.print(valKonstIntTmp);
      screenTmp = false;
    }
  }
}

void menuKD() {
  lcd.clear();
  lcd.print(F("Set KD:"));
  lcd.setCursor(0, 1);
  lcd.print(F("*>Simpan  C>Exit"));
  lcd.setCursor(7, 0);
  String valKonstDerivTmp;
  screenTmp = false;
  decPoint = false;
  while (true) {
    key = getKbd();
    if (key == '*') {
      lcd.clear();
      lcd.print(F("KD ok."));
      valKonstDeriv = valKonstDerivTmp.toDouble();
      delay(500);
      mainMenu();
      break;
    } else if (key == 'C') {
      mainMenu();
      break;
    } else {
      if (key != 'X' && key != 'A' && key != 'B' && key != 'C' && key != 'D') {
        if (key == '#' && decPoint == false) {
          if (!(strchr(valKonstDerivTmp.c_str(), '.'))) {
            if (valKonstDerivTmp.length() > 0) {
              valKonstDerivTmp += ".";
            } else {
              valKonstDerivTmp += "0.";
            }
          }
          decPoint = true;
        } else {
          valKonstDerivTmp += (String)key;
        }
        screenTmp = true;
      }
    }

    if (screenTmp) {
      clearLcdLine(0);
      lcd.setCursor(0, 0);
      lcd.print(F("Set KD:"));
      lcd.setCursor(7, 0);
      lcd.print(valKonstDerivTmp);
      screenTmp = false;
    }
  }
}

void menuSetApi() {
  digitalWrite(pinLpgIgniter, HIGH);
  delay(100);
  setServo(45);
  lcd.clear();
  lcd.print(F("Pemantik ON"));
  lcd.setCursor(0, 1);
  lcd.print(F("C>Exit"));
  lcd.setCursor(7, 0);
  while (true) {
    key = getKbd();
    if (key == 'C') {
      lcd.clear();
      lcd.print(F("Pemantik OFF"));
      digitalWrite(pinLpgIgniter, LOW);
      delay(500);
      setServo(180);
      mainMenu();
      break;
    }
  }
}

void cekApi() {
  while (digitalRead(pinFlame) == HIGH) delay(1);
}

void menuRun() {
  lcd.clear();
  lcd.print("Menyalakan api.");
  setServo(90);
  delay(100);
  digitalWrite(pinLpgIgniter, HIGH);
  cekApi();
  digitalWrite(pinLpgIgniter, LOW);
  delay(500);
  setServo(0);
  pidMode = 1;
  runPID = true;
}

/*
void menuSisRes() {
  lcd.clear();
  lcd.print("Menyalakan api.");
  setServo(90);
  delay(100);
  digitalWrite(pinLpgIgniter, HIGH);
  cekApi();
  digitalWrite(pinLpgIgniter, LOW);
  delay(500);
  setServo(0);
  pidMode = 3;
  runPID = true;
}
*/

void welcomeText() {
  lcd.clear();
  lcd.print(F("   ANALISIS    "));
  lcd.setCursor(0, 1);
  lcd.print(F("  PERFORMANCE  "));
  delay(2000);
  lcd.clear();
  lcd.print(F("     SISTEM     "));
  lcd.setCursor(0, 1);
  lcd.print(F("  KONTROL  PID  "));
  delay(1500);
  lcd.clear();
  lcd.print(F(" UNTUK  OTOMASI "));
  lcd.setCursor(0, 1);
  lcd.print(F("    KENDALI     "));
  delay(1500);
  lcd.clear();
  lcd.print(F("  TEMPERATURE   "));
  lcd.setCursor(0, 1);
  lcd.print(F("     TUNGKU     "));
  delay(1500);
  lcd.clear();
  lcd.print(F("    PENCAIR     "));
  lcd.setCursor(0, 1);
  lcd.print(F("  LILIN  BATIK  "));
  delay(1500);
  lcd.clear();
  lcd.print(F("  SKRIPSI 2021  "));
  lcd.setCursor(0, 1);
  lcd.print(F("  AHMAD AFIF M  "));
  delay(1500);
}

void menuState() {
  key = getKbd();
  if (key == 'A') {
    keyState = true;
    menuPos = (menuPos == 0) ? totalMenu : --menuPos;
  } else if (key == 'B') {
    keyState = true;
    menuPos = (menuPos == totalMenu) ? 0 : ++menuPos;
  }

  if (key == 'D') {
    if (menuPos == 0) {
      menuSP();
    } else if (menuPos == 1) {
      menuKP();
    } else if (menuPos == 2) {
      menuKI();
    } else if (menuPos == 3) {
      menuKD();
    } else if (menuPos == 4) {
      menuSetApi();
    } else if (menuPos == 5) {
      menuLilin();
    } else if (menuPos == 6) {
      menuRun();
    }
    /*
    else if (menuPos == 7) {
      menuSisRes();
    }
    */
  }
}
/* end: method menu main */
