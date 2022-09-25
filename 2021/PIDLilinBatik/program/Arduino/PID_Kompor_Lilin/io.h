double getTempCel() {
  //suhu.setWaitForConversion(false);
  suhu.requestTemperatures();
  //suhu.setWaitForConversion(true);
  //const uint8_t resolution = 9;
  //delay(750 / (1 << (12 - resolution)));
  return suhu.getTempCByIndex(0);
}

void setLpgIgniter(uint8_t igniter) {
  (igniter == HIGH) ? digitalWrite(pinLpgIgniter, HIGH) : digitalWrite(pinLpgIgniter, LOW);
}

void setServo(int16_t sudut) {
  if (sudut != servoPos) {
    servoLpg.attach(pinServoLpg);
    int16_t pos;
    if (servoPos < sudut) {
      //lcd.clear();
      //lcd.print(F("Servo up:"));
      //lcd.setCursor(0, 1);
      //lcd.print((String)servoPos + " -> " + sudut);
      for (pos = servoPos; pos <= sudut; pos += 1) {
        servoLpg.write(pos);
        delay(15);
      }
      servoPos = pos - 1;
    } else {
      //lcd.clear();
      //lcd.print(F("Servo down:"));
      //lcd.setCursor(0, 1);
      //lcd.print((String)servoPos + " -> " + sudut);
      for (pos = servoPos; pos >= sudut; pos -= 1) {
        servoLpg.write(pos);
        delay(15);
      }
      servoPos = pos + 1;
    }
    servoLpg.detach();
  }
  //else {
  //  lcd.clear();
  //  lcd.print(F("Servo done:"));
  //  lcd.setCursor(0, 1);
  //  lcd.print((String)servoPos + " = " + sudut);
  //}
}
