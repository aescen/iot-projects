//#include <LiquidCrystal.h>
//const byte rs = 16, en = 18, d4 = 19, d5 = 20, d6 = 21, d7 = 22;
//LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("{\"s\":\"Hello from ATmega32\"}");
  //  lcd.begin(16, 2);
  //  lcd.clear();
  //  lcd.print("Serial test.");

}
int i;
void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    //    lcd.clear();
    char buff[24];
    uint8_t i = 0;
    while (Serial.available() > 0) {
      buff[i] = (char) Serial.read();
      i++;
    }
    //    lcd.print(String(buff));
    Serial.print(String(buff));
  }

  i++;
  String s = "{\"i\":" + (String)i + "}";
  Serial.println(s);
  delay(2000);
}
