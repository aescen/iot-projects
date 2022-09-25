void testInit() {
  lcd.clear();
  lcd.print(F("Servo 0"));
  setServo(0);
  delay(1000);

  lcd.print(F("Servo 45"));
  setServo(45);
  delay(1000);

  lcd.clear();
  lcd.print(F("Servo 180"));
  setServo(180);
  delay(1000);

  lcd.clear();
  lcd.print(F("Servo 45"));
  setServo(45);
  delay(1000);

  lcd.clear();
  lcd.print(F("Servo 180"));
  setServo(180);
  delay(1000);

  lcd.clear();
  lcd.print(F("Pemantik ON"));
  digitalWrite(pinLpgIgniter, HIGH);
  delay(3000);
  lcd.clear();
  lcd.print(F("Pemantik OFF"));
  digitalWrite(pinLpgIgniter, LOW);

  lcd.clear();
  lcd.print("Suhu: " + (String)getTempCel());

  lcd.clear();
  lcd.print("Flame:" + (String)digitalRead(pinFlame));
}
