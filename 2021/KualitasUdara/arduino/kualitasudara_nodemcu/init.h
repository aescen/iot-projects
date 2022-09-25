/* SETUP WIFI STATION/CLIENT */

const char *ssidST = "AQ-RPiHotSpot";
const char *passST = "123rpi123";

void initialize() {
  /* Serial Interface */
  Serial.begin(115200);
  SPI.begin();

  /* WiFi Client setup */
  Serial.print(F("Connecting to "));
  Serial.println(ssidST);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssidST, passST);
  uint32_t waitWiFi = 1000 * 60 + millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");

    if (millis() >= waitWiFi) {
      Serial.println("Error connecting to WiFi. Restart...");
      setup();
    }
  }
  Serial.println();
  Serial.print(F("Connected: "));
  Serial.println(WiFi.localIP());

  /* DMD */
  dmd.begin();
  dmd.setBrightness(128);
  dmd.fillScreen(false);
  delay(1000);
}
