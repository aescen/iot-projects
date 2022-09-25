#include "init.h"

void setup(void) {
  ESP.eraseConfig();
  comsInit();
  wifiInit();
  webServerInit();
  Serial.println("Setup selesai.");
}

void loop() {
  comsUpdate();
  //testJson();
  server.handleClient();
}
