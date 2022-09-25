#include <ArduinoJson.h>
#include <ESP8266WiFi.h>

const char* ssid     = "..."; //access point wifi name (SSID)
const char* password = "..."; //access point wifi password

const char* host = "api.thingspeak.com";
const uint16_t port = 443;

// SHA1 fingerprint of the certificate
const char fingerprint[] PROGMEM = "F9:C2:65:6C:F9:EF:7F:66:8B:F7:35:FE:15:EA:82:9F:5F:55:54:3E";

//WiFiClientSecure client;
int data1 = -1, data2 = -1, data3 = -1, data4 = -1;

void ESPSendData(int data1, int data2, int data3, int data4) {
  char buf[128];
  sprintf(buf, "GET /update?api_key=...&field1=%lu&field2=%lu&field3=%lu&field4=%lu HTTP/1.1\r\nHost: api.thingspeak.com\r\n\r\n", data1, data2, data3, data4);
  WiFiClientSecure client;
  //Serial.printf("Using fingerprint '%s'\n", fingerprint);
  client.setFingerprint(fingerprint);
  if (!client.connect("api.thingspeak.com", 443)) {
    //Serial.println("Failed to connect with 'api.thingspeak.com' !");
  }
  else {
    int timeout = millis() + 5000;
    client.print(buf);
    while (client.available() == 0) {
      if (timeout - millis() < 0) {
        //Serial.println(">>> Client Timeout !");
        client.stop();
        return;
      }
    }
    int size;
    while ((size = client.available()) > 0) {
      uint8_t* msg = (uint8_t*)malloc(size);
      size = client.read(msg, size);
      //Serial.write(msg, size);
      free(msg);
    }
  }
}

void setup() {
  Serial.begin(9600);
  while (!Serial) continue;

  // We start by connecting to a WiFi network
  /*
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
  */

  /* Explicitly set the ESP8266 to be a WiFi-client, otherwise, it by default,
     would try to act as both a client and an access-point and could cause
     network-issues with your other WiFi-devices on your WiFi-network. */
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    //Serial.print(".");
  }

  /*Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  */
}

void loop() {
  // Connect or reconnect to WiFi
  if (WiFi.status() != WL_CONNECTED) {
    //Serial.print("Attempting to connect to SSID: ");
    //Serial.println(ssid);
    while (WiFi.status() != WL_CONNECTED) {
      WiFi.begin(ssid, password);  // Connect to WPA/WPA2 network. Change this line if using open or WEP network
      //Serial.print(".");
      delay(5000);
    }
    //Serial.println("\nConnected.");
  }

  //char json[] = "{\"servo\":0,\"relay\":0,\"ph\":302.1,\"moist\":990.4}";
  StaticJsonDocument<1024> doc;
  //DeserializationError error = deserializeJson(doc, json);
  DeserializationError error = deserializeJson(doc, Serial);
  if (error) return;
  int ndata1 = doc["servo"];
  int ndata2 = doc["relay"];
  int ndata3 = doc["ph"];
  int ndata4 = doc["moist"];

  /*
    Serial.print("Servo : "); Serial.println(data1);
    Serial.print("Relay : "); String d2 = ((int)data2 == 1) ? "ON" : "OFF"; Serial.println(d2);
    Serial.print("pH level : "); Serial.println(data3);
    Serial.print("Moist level : "); Serial.println(data4);
  */

  if ( (ndata1 != data1) || (ndata2 != data2) || (ndata3 != data3) || (ndata4 != data4) ) {
    ESPSendData(ndata1, ndata2, ndata3, ndata4);
    data1 = ndata1; data2 = ndata2; data3 = ndata3; data4 = ndata4;
  }

  delay(20000); // 20 detik
}
