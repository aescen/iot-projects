void textStatus() {
  strTime = "";
  (((String)jam).length() > 1) ? strTime += (String)jam : strTime += "0" + (String)jam;
  (((String)menit).length() > 1) ? strTime += ":" + (String)menit : strTime += ":0" + (String)menit;
  (((String)detik).length() > 1) ? strTime += ":" + (String)detik : strTime += ":0" + (String)detik;
  lcd.clear();
  lcd.print("T:" + (String)(int8_t)valSuhu + (char)223 + "C");
  lcd.setCursor(8, 0);
  lcd.print(strTime);
  lcd.setCursor(0, 1);
  lcd.print((String)(int)valSetPoint + ";" + (String)(int)valKonstProp + ";" + (String)(int)valKonstInt + ";" + (String)(int)valKonstDeriv + ";");
  //  lcd.print( "SP:" + (String)(int)valSetPoint);
  //  lcd.setCursor(6, 1);
  //  lcd.print( "PID:" + (String)valPid);
}



void pidMode1() {
  float valI , valP , valD , valResPid , valPid1 , valPid2 ;
  float valDe1, valDe2, valPrePid, valKp1, valKi1, valKd1;
  int valSuhu_w, valSuhu_s;
  int valPid_w ;
  uint32_t statusTime;
  uint32_t sendTime;
  while (true) {
    key = getKbd();
    if (key == 'C') {
      setServo(180);
      runPID = false;
      mainMenu();
      jam = 0; menit = 0; detik = 0;
      break;
    }

    valSuhu = getTempCel();
    valError1 = valSetPoint - valSuhu;
    valDe2 = valError1 - valError2;
    valDe1 = valDe2 / 40;
    valI = valI + valDe1;
    valKp1 = valKonstProp * valError1;
    valKi1 = valKonstInt * valI;
    valKd1 = valKonstDeriv * valDe1;
    valPid1 = valKp1 + valKi1;
    valPid2 = valPid1 + valKd1;
    valPid1 = valPrePid + valPid2;

    if (valPid1 > 1023) {
      valPid1 = 1023;
    }
    if (valPid1 < 0) {
      valPid1 = 0;
    }

    valResPid = valPid1;
    valPrePid = valPid1;
    valSuhu_w = 1023 - valResPid;
    valSuhu_s = valSuhu_w / 7.055;
    valSudut = valSuhu_s + 0;
    valPid_w = valResPid;
    valSuhu_w = valSuhu;
    valPid = valResPid;
    valSudut = constrain(valSudut, 0, 145);
    valSudut = map(valSudut, 0, 145, 0, 180);

    setServo(valSudut);
    valError2 = valError1;

    if ((millis() - statusTime) >= 1000) {
      textStatus();
      statusTime = millis();
    }
    if ((millis() - sendTime) >= 2000) {
      sendData();
      sendTime = millis();
    }
    tick();
  }
}

void pidMode2() {
  valPid = 0; valError1 = 0; valError2 = 0; valSampleT = 0.25 ;
  float valInt, valProp, valDer;
  uint32_t statusTime;
  uint32_t sendTime;
  while (true) {
    key = getKbd();
    if (key == 'C') {
      setServo(180);
      runPID = false;
      mainMenu();
      jam = 0; menit = 0; detik = 0;
      break;
    }
    valSuhu = getTempCel();
    valError1   = valSetPoint - valSuhu;
    valInt += valError1 * valSampleT;
    valDer = (valError1 - valError2) / valSampleT;
    valPid = (valKonstProp * valError1) + (valKonstInt * valInt) + (valKonstDeriv * valDer);

    if (valPid > 255) {
      valPid = 255;
    }
    if (valPid < 0) {
      valPid = 0;
    }

    valSudut = remap(valPid, 0, 255, 180, 0);
    setServo(valSudut);
    valError2 = valError1;
    if ((millis() - statusTime) >= 1000) {
      textStatus();
      statusTime = millis();
    }
    if ((millis() - sendTime) >= 2000) {
      sendData();
      sendTime = millis();
    }
    tick();
    delay(valSampleT * 1000);
  }
}

void pidMode3() {
  valPid = -1;
  valSudut = -1;
  valSetPoint = -1;
  valKonstProp = -1;
  valKonstInt = -1;
  valKonstDeriv = -1;

  uint32_t statusTime;
  uint32_t sendTime;
  while (true) {
    key = getKbd();
    if (key == 'C') {
      setServo(180);
      runPID = false;
      mainMenu();
      jam = 0; menit = 0; detik = 0;
      break;
    }

    valSuhu = getTempCel();

    if ((millis() - statusTime) >= 1000) {
      textStatus();
      statusTime = millis();
    }
    if ((millis() - sendTime) >= 2000) {
      sendData();
      sendTime = millis();
    }
    tick();
  }
}

void PID(int mode = 1);
void PID(int mode) {
  if (valSetPoint == -1.0 && valKonstProp == -1.0 && valKonstInt == -1.0  && valKonstDeriv == -1.0 ) {
    valSetPoint = 40;
    valKonstProp = 16.2;
    valKonstInt = 16;
    valKonstDeriv = 4;
  }
  lcd.clear();
  lcd.print("SP:" + (String)valSetPoint);
  lcd.setCursor(10, 0);
  lcd.print("KP:" + (String)valKonstProp);
  lcd.setCursor(0, 1);
  lcd.print("KI:" + (String)valKonstInt);
  lcd.setCursor(10, 1);
  lcd.print("KD:" + (String)valKonstDeriv);
  delay(1500);
  switch (mode) {
    case 1: pidMode1(); break;
    case 2: pidMode2(); break;
    case 3: pidMode3(); break;
    default: pidMode1(); break;
  }
}
