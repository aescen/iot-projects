#include "modulrtc.h"
#include "modulnrf24.h"
#include "modulsensor.h"
#include "inits.h"

void setup() {
  systemInit();
}

void loop() {
  systemUpdate();
}
