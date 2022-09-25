#include <DMD2.h>
#include <fonts/Font3x5.h>

/*
  | DMD P10 | NODEMCU |
  | ------- | ------- |
  | A       | D0      |
  | B       | D6      |
  | CLK     | D5      |
  | SCK     | D3      |
  | R       | D7      |
  | NOE     | D8      |
  | GND     | GND     |
*/

#define DISPLAYS_WIDE 1
#define DISPLAYS_HIGH 1
SPIDMD dmd(DISPLAYS_WIDE, DISPLAYS_HIGH);
/* dmd, left, top, width, height. ex: dmd, 0, 0, 32, 16 */
DMD_TextBox box(dmd, 0, 0, 32, 16);
const uint8_t *FONT = Font3x5;
const uint8_t TOTALCASE = 6;

uint16_t showInterval = 3000;
uint32_t tShow = millis();
uint8_t showInf;
uint8_t showInfTmp;

void drawInfo(String stringAtas, String stringBawah) {
  dmd.fillScreen(false);
  dmd.scanDisplay();
  dmd.selectFont(FONT);
  dmd.drawString(1, -1, stringAtas);
  dmd.drawString(1, 7, stringBawah);
}

void showInfo() {
  if ( millis() - tShow >= showInterval  ) {
    showInfTmp = (showInfTmp < 6) ? (showInfTmp + 1) : 0;
    tShow = millis();
  }

  if (showInfTmp != showInf) {
    switch (showInf) {
      case 0: {
          drawInfo(F("Air"), F("Quality"));
          Serial.println(F("Show: Air Quality"));
        }
        break;
      case 1: {
          drawInfo(F("CO-1:"), String((int)valSensorCO) + F("ppm"));
          Serial.println(String(F("Show: CO-1(ppm):")) + String(valSensorCO));
        }
        break;
      case 2: {
          drawInfo(F("CO-2:"), String((int)valSensorCO2) + F("ppm"));
          Serial.println(String(F("Show: CO-2(ppm):")) + String(valSensorCO2));
        }
        break;
      case 3: {
          drawInfo(F("CO-3:"), String((int)valSensorCO3) + F("ppm"));
          Serial.println(String(F("Show: CO-3(ppm):")) + String(valSensorCO3));
        }
        break;
      case 4: {
          drawInfo(F("Dust:"), String((int)valSensorDusts) + F("ug/m3"));
          Serial.println(String(F("Show: Dust(ug/m3):")) + String(valSensorDusts));
        }
        break;
      case 5: {
          drawInfo(F("Visitor:"), String(valVisitors));
          Serial.println(String(F("Show: Visitors:")) + String(valVisitors));
        }
        break;
      default: break;
    }
    showInf = showInfTmp;
  }
  yield();
}
