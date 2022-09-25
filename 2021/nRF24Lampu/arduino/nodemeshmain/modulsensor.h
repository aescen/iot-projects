#include "ACS712.h"
#include <Voltmeter.h>

const byte PIN_HALLSENSOR_DC = A0;
const byte PIN_VOLTMETER_AC = A1;
const byte PIN_VOLTMETER_DC = A2;
const byte PIN_HALLSENSOR_AC = A3;

// ACS712 5A  uses 185 mV per A
// ACS712 20A uses 100 mV per A
// ACS712 30A uses  66 mV per A
// Arduino UNO ADC pin has 5.0 volt peak with a max ADC value of 1023 steps
// analogPin, volts, maxADC, mVperA)
ACS712  dcHallsensor(PIN_HALLSENSOR_DC, 5, 1023, 185);
ACS712  acHallsensor(PIN_HALLSENSOR_AC, 240, 1023, 66);

//sensorPin, maxVoltage, readingNumber for averaging
Voltmeter dcVoltMeter(PIN_VOLTMETER_DC, 5, 8);
Voltmeter acVoltMeter(PIN_VOLTMETER_AC, 240, 8);

struct sensorsData {
  float acVolt; float dcVolt; float acCurrent; float dcCurrent;
};

sensorsData sensorData;

void sensorsInit() {
  acVoltMeter.initialize();
  dcVoltMeter.initialize();
}

float truncateData(float f) {
  int temp = f * 1000;
  float temp2 = temp;
  return temp2 / 1000;
}

void updateSensorsData() {
  sensorData.acVolt = truncateData(acVoltMeter.getAverage());
  sensorData.dcVolt = truncateData(dcVoltMeter.getAverage());
  sensorData.acCurrent = truncateData(dcHallsensor.mA_AC());
  sensorData.dcCurrent = truncateData(dcHallsensor.mA_DC());
}
