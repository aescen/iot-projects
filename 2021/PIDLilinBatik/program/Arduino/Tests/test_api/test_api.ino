#include <LiquidCrystal.h>

const byte pinFlame = 31;
const byte rs = 16, en = 18, d4 = 19, d5 = 20, d6 = 21, d7 = 22;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);


void setup() {
  lcd.begin(16, 2);
  pinMode(pinFlame, INPUT);
}

bool tmp1 = true;
bool tmp2 = true;
void loop() {
  if (digitalRead(pinFlame) == LOW) {
    if (tmp1) {
      lcd.clear();
      lcd.print("Api hidup");
      tmp1 = false;
      tmp2 = true;
    }
  } else {
    if (tmp2) {
      lcd.print("Api mati");
      tmp1 = true;
      tmp2 = false;
    }
  }
  delay(1);
}
