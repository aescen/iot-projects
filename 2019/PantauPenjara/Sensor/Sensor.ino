/********************************************************************************************Includes**/
#include <SPI.h>
#include <Ethernet.h>
/**/
/********************************************************************************************Variables**/
int vibr_Pin1 = 3;
int vibr_Pin2 = 5;
int LED_Pin = 13;
long m3, m4;
/**/
/********************************************************************************************Ethernet setup**/
// Enter a MAC address for your controller below.
// Newer Ethernet shields have a MAC address printed on a sticker on the shield
byte mac[] = {
  0xB8, 0xEA, 0x6D, 0x89, 0xBB, 0x08
};
IPAddress server(192, 168, 100, 13); // numeric IP
EthernetClient client;
/**/
/********************************************************************************************Arduino setup**/
void setup() {
  pinMode(vibr_Pin1, INPUT);
  pinMode(vibr_Pin2, INPUT);
  pinMode(LED_Pin, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  // Ethernet initialization
  Ethernet.init(10);  // Most Arduino shields use pin 10
  // start the Ethernet connection:
  Serial.println("Initialize Ethernet with DHCP:");
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    // Check for Ethernet hardware present
    if (Ethernet.hardwareStatus() == EthernetNoHardware) {
      Serial.println("Ethernet shield was not found.  Sorry, can't run without hardware. :(");
      while (true) {
        delay(10); // do nothing, no point running without Ethernet hardware
      }
    }
    if (Ethernet.linkStatus() == LinkOFF) {
      Serial.println("Ethernet cable is not connected.");
    }
  } else {
    Serial.print("  DHCP assigned IP ");
    Serial.println(Ethernet.localIP());
  }
  // give the Ethernet shield a second to initialize:
  delay(1000);
  Serial.print("connecting to ");
  Serial.print(server);
  Serial.println("...");
}
unsigned long start = 0;
/**/
/********************************************************************************************Loop start**/
void loop() {
  // if you get a connection, report back via serial:
  TP_init();
  delay(50);
  unsigned long now = millis();
  if (now - start >= 5) {
    digitalWrite(LED_Pin, HIGH);
    Serial.print("m3 = "); Serial.println(m3);
    Serial.print("m4 = "); Serial.println(m4);
    //Kirim data
    kirimDb(String(m3), String(m4));
    start = now;
  }
  maintainIP();
}
/**/
/********************************************************************************************Functions goes below**/
void kirimDb(String d1, String d2) {
  // Make a HTTP request:
  if (client.connect(server, 80)) {
    Serial.print("connected to ");
    Serial.println(client.remoteIP());
    
    client.print("GET /ipcamweb/arduino.php?m3=");
    client.print(d1);
    client.print("&m4=");
    client.print(d2);
    client.println(" HTTP/1.1");
    
    client.print("Host: ");
    client.println(server);
    
    client.println("Connection: close");
    client.println();
  } else {
    Serial.println("Connection error!");
  }
}
long TP_init() {
  delay(10);
  m3 = pulseIn (vibr_Pin1, HIGH);
  m4 = pulseIn (vibr_Pin2, HIGH);
}
//Maintain IP address
void maintainIP(void) {
  switch (Ethernet.maintain()) {
    case 1:
      //renewed fail
      Serial.println("Error: renewed fail");
      break;

    case 2:
      //renewed success
      Serial.println("Renewed success");
      //print your local IP address:
      Serial.print("My IP address: ");
      Serial.println(Ethernet.localIP());
      break;

    case 3:
      //rebind fail
      Serial.println("Error: rebind fail");
      break;

    case 4:
      //rebind success
      Serial.println("Rebind success");
      //print your local IP address:
      Serial.print("My IP address: ");
      Serial.println(Ethernet.localIP());
      break;

    default:
      //nothing happened
      break;
  }
}
/**/
