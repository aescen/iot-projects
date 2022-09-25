#include <OneWire.h>
#include <DallasTemperature.h>
#include <LiquidCrystal.h>

// lcd 16x2
const byte rs = 16, en = 18, d4 = 19, d5 = 20, d6 = 21, d7 = 22;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// Sensors
const byte pinTemp = 24;
int valSuhu;
OneWire oneWire(pinTemp);
DallasTemperature suhu(&oneWire);

byte degreeChar[8] = {0b01100, 0b10010, 0b10010, 0b01100, 0b00000, 0b00000, 0b00000, 0b00000};

double getTempCel() {
  suhu.requestTemperatures();
  return suhu.getTempCByIndex(0);
}

void setup() {
  lcd.begin(16, 2);
  lcd.createChar(0, degreeChar);
  suhu.begin();
  valSuhu = getTempCel();
  
}

void loop() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(F("Menu"));
  lcd.setCursor(10, 0);
  lcd.print("T:" + (String)(int)valSuhu + (char)223 + "C");
}
