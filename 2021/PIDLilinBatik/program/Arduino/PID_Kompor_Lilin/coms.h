void sendData() {
  delay(10);
  Serial.flush();
  Serial.print(F("{\"T\":")); Serial.print(valSuhu);
  Serial.print(F(",\"PID\":")); Serial.print(valPid);
  Serial.print(F(",\"E\":")); Serial.print(valError1);
  Serial.print(F(",\"α\":")); Serial.print(valSudut);
  Serial.print(F(",\"C\":")); Serial.print("\"" + getT() + "\"");
  Serial.print(F(",\"data\":{\"SP\":")); Serial.print(valSetPoint, 4);
  Serial.print(F(",\"KP\":")); Serial.print(valKonstProp, 4);
  Serial.print(F(",\"KI\":")); Serial.print(valKonstInt, 4);
  Serial.print(F(",\"KD\":")); Serial.print(valKonstDeriv, 4);
  Serial.print(F("}}"));
  Serial.flush();
}


void checkSerial() {
  bool l = false;
  while (true) {
    if (Serial) {
      lcd.clear();
      lcd.print("Serial ok!");
      lcd.setCursor(0, 1);
      delay(1000);
      break;
    }

    if (!l) {
      lcd.clear();
      lcd.print("Serial error!");
      lcd.setCursor(0, 1);
      lcd.print("Periksa koneksi.");
      l = true;
    }

    Serial.end();
    delay(500);
    Serial.begin(115200);
    delay(500);
  }
}
