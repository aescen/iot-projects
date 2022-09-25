#include "globalvars.h"
#include "dotmatrix.h"
#include "db.h"
#include "init.h"

void setup() {
  initialize();
}

void loop() {
  checkDatabase();
  showInfo();
}
