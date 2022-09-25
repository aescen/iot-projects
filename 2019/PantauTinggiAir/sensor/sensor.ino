#include <SPI.h>
#include <Ethernet.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <SimpleKalmanFilter.h>
#include <NewPing.h>

#define TRIGGER_PIN  2  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     3  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.
#define led 13

// Enter a MAC address for your controller below.
// Newer Ethernet shields have a MAC address printed on a sticker on the shield
byte mac[] = {
  0xB8, 0xEA, 0x6D, 0x80, 0xBC, 0xA8
};
// Set the static IP address to use if the DHCP fails to assign
IPAddress ip(192, 168, 137, 177);
IPAddress myDns(192, 168, 137, 1);
IPAddress server(192, 168, 137, 1); // numeric IP
EthernetClient client;

//Servo
Servo myservo;

//LCD
LiquidCrystal_I2C lcd(0x3f, 16, 2);

//Measurement Uncertainty , Estimation Uncertainty , Process Noise
SimpleKalmanFilter simpleKalmanFilter(2, 2, 0.01);

//Sonar
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

//Vars
int jarak, jarak_filter, pos;
unsigned long starT = 0;

void baca_ultrasonik() {
  jarak = sonar.ping_cm();
  jarak_filter = simpleKalmanFilter.updateEstimate(jarak);
}

void tampil_lcd() {
  lcd.setCursor(0, 0);
  lcd.print("Sebelum  : ");
  lcd.print(jarak);
  lcd.print("   ");
  lcd.setCursor(0, 1);
  lcd.print("Filter   : ");
  lcd.print(jarak_filter);
  lcd.print("   ");

  lcd.setCursor(14, 0);
  lcd.print("cm");
  lcd.setCursor(14, 1);
  lcd.print("cm");
}

void tampil_serial() {
  Serial.print(jarak);
  Serial.println();
  Serial.print(jarak_filter);
}


void setup() {
  Serial.begin(115200);

  pinMode(led, OUTPUT);

  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("starting");

  myservo.attach(9);
  myservo.write(150);
  delay(1000);
  myservo.write(50);

  lcd.clear();

  SPI.begin();
  // Ethernet initialization
  Ethernet.init(10);  // Most Arduino shields use pin 10
  // start the Ethernet connection:
  Ethernet.begin(mac, ip, myDns);
  // give the Ethernet shield a second to initialize:
  delay(1000);
  Serial.print("connecting to ");
  Serial.print(server);
  Serial.println("...");
}

void loop() {
  baca_ultrasonik();
  if (jarak_filter <= 10) {
    if (pos == 0) {
      buka();
    }
  } else if (jarak_filter > 10) {
    if (pos == 90) {
      tutup();
    }
  }
  tampil_lcd();
  tampil_serial();
  unsigned long noW = millis();
  if (noW - starT >= 2500) {
    digitalWrite(led, HIGH);
    Serial.print("jarak = "); Serial.println(jarak);
    Serial.print("jarak terfilter = "); Serial.println(jarak_filter);
    //Kirim data
    kirimDb(String(jarak), String(jarak_filter));
    starT = noW;
  }
  delay(100);
}

void buka() {
  for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  pos = 180;
}

void tutup() {
  for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  pos = 180;
}

void kirimDb(String d1, String d2) {
  // Make a HTTP GET request:
  if (client.connect(server, 80)) {
    Serial.print("connected to ");
    Serial.println(client.remoteIP());

    client.print("GET /sonar/arduino.php?data1=");
    client.print(d1);
    client.print("&data2=");
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
