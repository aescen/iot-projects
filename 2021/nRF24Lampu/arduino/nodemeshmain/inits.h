//vars
uint32_t millisTimer = millis();
const uint16_t sendDelay = 3690;

void systemInit() {
  Serial.begin(115200);

  rtcInit();
  nrfInit();
  sensorsInit();
}

void systemUpdate() {
  // update mesh network
  mesh.update();

  updateSensorsData();

  if (network.available()) {
    readPayload();
  }

  // update database
  if (millis() - millisTimer >= sendDelay) {
    millisTimer = millis();
    sendPayload(masterNode, sensorData.acVolt, sensorData.dcVolt, sensorData.acCurrent, sensorData.dcCurrent);
  }

  delay(10);
}
