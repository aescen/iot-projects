#include <LiquidCrystal.h>

const byte rs = 16, en = 18, d4 = 19, d5 = 20, d6 = 21, d7 = 22;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// max custom char number is 8
// saved to 0 - 7 address
// □ ■

byte heartChar[8] = {
  0b00000,              // □ □ □ □ □
  0b01010,              // □ ■ □ ■ □
  0b11111,              // ■ ■ ■ ■ ■
  0b11111,              // ■ ■ ■ ■ ■
  0b01110,              // □ ■ ■ ■ □
  0b00100,              // □ □ ■ □ □
  0b00000,              // □ □ □ □ □
  0b00000               // □ □ □ □ □
};

byte degreeChar[8] = {
  0b01100,              // □ ■ ■ □ □
  0b10010,              // ■ □ □ ■ □
  0b10010,              // ■ □ □ ■ □
  0b01100,              // □ ■ ■ □ □
  0b00000,              // □ □ □ □ □
  0b00000,              // □ □ □ □ □
  0b00000,              // □ □ □ □ □
  0b00000               // □ □ □ □ □
};

void setup() {
  lcd.begin(16, 2);
  lcd.createChar(0, heartChar);
  lcd.createChar(1, degreeChar);
  lcd.setCursor(0, 0);
  lcd.write((byte)0);
  lcd.setCursor(1, 0);
  lcd.write((byte)1);
  lcd.setCursor(14, 0);
  lcd.write((byte)1);
  lcd.setCursor(15, 0);
  lcd.write((byte)0);
  lcd.setCursor(0, 1);
  lcd.write((byte)0);
  lcd.setCursor(1, 1);
  lcd.write((byte)1);
  lcd.setCursor(14, 1);
  lcd.write((byte)1);
  lcd.setCursor(15, 1);
  lcd.write((byte)0);
}

void loop() {}
