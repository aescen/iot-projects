uint8_t hh, mm, ss;
uint32_t t;
void tick() {
  if (millis() - t >= 1000) {
    t = millis();
    ss += 1;

    if (ss == 59) {
      mm += 1;
      ss = 0;
    }
    if (hh == 59) {
      hh += 1;
      mm = 0;
    }
  }
}

String getTimeLocal() {
  String strTime = "";
  (((String)hh).length() > 1) ? strTime += (String)hh : strTime += "0" + (String)hh;
  (((String)mm).length() > 1) ? strTime += ":" + (String)mm : strTime += ":0" + (String)mm;
  (((String)ss).length() > 1) ? strTime += ":" + (String)ss : strTime += ":0" + (String)ss;
  return strTime;
}
