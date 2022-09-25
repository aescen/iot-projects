/* start: var menu lilin */
const uint8_t totalMenuLilin = 3;
const String menuLilin[3] = {">Lilin 1", ">Lilin 2", , ">Kembali"};
int8_t menuLilinPos = (1)-1;
bool keyStateMenuLilin = false;
/* end: var menu lilin */

/* start: method menu lilin */
void textMenuLilinAtas() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(F("Pilih Lilin"));
}
void textMenuLilinBawah() {
  clearLcdLine(1);
  lcd.setCursor(0, 1);
  lcd.print(menuLilin[menuLilinPos]);
  keyStateMenuLilin = false;
}

void menuLilin() {
  textMenuLilinAtas();
  textMenuLilinBawah();
}

void tampilInfoSetLilin() {
  delay(10);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(F("Set Lilin: "));
  lcd.print((String)(menuLilinPos + 1));
  lcd.setCursor(10, 0);
  lcd.print("SP:" + (String)(int)valSetPoint);
  lcd.setCursor(0, 1);
  lcd.print("KP:" + (String)(int)valKonstProp + "KI:" + (String)(int)valKonstInt + "KD:" + (String)(int)valKonstDeriv);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(F("Set Lilin: "));
  lcd.print((String)(menuLilinPos + 1));
  lcd.setCursor(0, 1);
  lcd.print(F("OK!"));
  delay(1000);
}

void menuLilin1() {
  valKonstProp = 123.123;
  valKonstInt = 123.123;
  valKonstDeriv = 123.123;
  tampilInfoSetLilin();
  // langkah selanjutnya?
  menuPos = 0; // set main menu ke posisi run?
  mainMenu(); // kembali ke main menu?
}

void menuLilin2() {
  valKonstProp = 123.123;
  valKonstInt = 123.123;
  valKonstDeriv = 123.123;
  // langkah selanjutnya?
  menuPos = 0; // set main menu ke posisi run?
  mainMenu(); // kembali ke main menu?
}

void menuLilinState() {
  key = getKbd();
  if (key == 'A') {
    keyStateMenuLilin = true;
    menuLilinPos = (menuLilinPos == 0) ? totalMenuLilin : --menuLilinPos;
  } else if (key == 'B') {
    keyStateMenuLilin = true;
    menuLilinPos = (menuLilinPos == totalMenuLilin) ? 0 : ++menuLilinPos;
  }

  if (key == 'D') {
    if (menuLilinPos == 0) {
      menuLilin1();
    } else if (menuLilinPos == 1) {
      menuLilin2();
    } else if (menuLilinPos == 2) {
      mainMenu();
    }
  }
}
/* end: method menu lilin */
