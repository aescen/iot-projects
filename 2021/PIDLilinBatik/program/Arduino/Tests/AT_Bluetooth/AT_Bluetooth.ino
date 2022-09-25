//  Sketc: basicSerialWithNL_001
//
//  Uses hardware serial to talk to the host computer and software serial
//  for communication with the Bluetooth module
//  Intended for Bluetooth devices that require line end characters "\r\n"
//
//  Pins
//  Arduino 5V out TO BT VCC
//  Arduino GND to BT GND
//  Arduino D9 to BT RX through a voltage divider
//  Arduino D8 BT TX (no need voltage divider)
//
//  When a command is entered in the serial monitor on the computer
//  the Arduino will relay it to the bluetooth module and display the result.
//


#include <SoftwareSerial.h>
SoftwareSerial BTserial(D5, D6); // RX | TX

#if defined(ESP8266) && !defined(D5)
#define D5 (14)
#define D6 (12)
#define D7 (13)
#define D8 (15)
#endif

const long baudRate = 38400;
char c = ' ';
boolean NL = true;

void setup()
{
  Serial.begin(115200);
  Serial.print("Sketch:   ");   Serial.println(__FILE__);
  Serial.print("Uploaded: ");   Serial.println(__DATE__);
  Serial.println(" ");

  BTserial.begin(baudRate, SWSERIAL_8N1, D5, D6, false, 256);
  Serial.print("BTserial started at "); Serial.println(baudRate);
  Serial.println(" ");
}

void loop() {
  // Read from the Bluetooth module and send to the Arduino Serial Monitor
  while (BTserial.available()) {
    c = BTserial.read();
    Serial.write(c);
    yield();
  }

  // Read from the Serial Monitor and send to the Bluetooth module
  while (Serial.available()) {
    c = Serial.read();
    BTserial.write(c);

    // Echo the user input to the main window. The ">" character indicates the user entered text.
    if (NL) {
      Serial.print(">");
      NL = false;
    }
    Serial.write(c);
    if (c == 10) {
      NL = true;
    }
    yield();
  }
  yield();
}
