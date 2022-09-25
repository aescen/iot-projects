uint8_t jam, menit, detik;
char keyPressed = 'X';
char key = 'X';
String strTime = "00:00:00";
uint32_t t;

float remap(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

char getKbd() {
  keyPressed = myKbd.getKey();
  if (keyPressed != NO_KEY) {
    return keyPressed;
  } else {
    return 'X';
  }
}

void clearLcdLine(int line) {
  lcd.setCursor(0, line);
  for (int n = 0; n < 16; n++) {
    lcd.print(F(" "));
  }
}

void tick() {
  if (millis() - t >= 1000) {
    t = millis();
    detik += 1;

    if (detik == 59) {
      menit += 1;
      detik = 0;
    }
    if (jam == 59) {
      jam += 1;
      menit = 0;
    }
  }
}

String getT() {
  strTime = "";
  (((String)jam).length() > 1) ? strTime += (String)jam : strTime += "0" + (String)jam;
  (((String)menit).length() > 1) ? strTime += ":" + (String)menit : strTime += ":0" + (String)menit;
  (((String)detik).length() > 1) ? strTime += ":" + (String)detik : strTime += ":0" + (String)detik;
  return strTime;
}


/*uint32_t getT() {
  uint8_t jam = getValue(__TIME__, ':', 0).toInt();
  uint8_t menit = getValue(__TIME__, ':', 1).toInt();
  uint8_t detik = getValue(__TIME__, ':', 2).toInt();
  return ( millis() + (jam * 3600000L) + (menit * 60000) + (detik * 1000));
  }

  String getValue(String dat, char separator, int index) {
  int found = 0;
  int strIndex[] = { 0, -1 };
  int maxIndex = dat.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (dat.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? dat.substring(strIndex[0], strIndex[1]) : "";
  }
*/
