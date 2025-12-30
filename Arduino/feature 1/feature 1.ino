#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

const int buttonPin = 2;
const int ledPin = 13;
const int buzzerPin = 12;  // Buzzer pin
String gpsString = "";

void setup() {
  Serial.begin(9600);

  if (!oled.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    while (true);
  }

  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(buttonPin, INPUT);

  oled.clearDisplay();
  oled.setTextSize(2);
  oled.setTextColor(WHITE);
  oled.setCursor(0, 10);
  oled.println("Reading");
  oled.println("---------");
  oled.display();
  delay(2000);
}

void loop() {
  gpsString = "";

  // Read the serial input from Python
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    gpsString += inChar;
  }

  oled.clearDisplay();
  oled.setTextSize(2);
  oled.setTextColor(WHITE);
  oled.setCursor(0, 10);

  // Crowd Detection Logic
  if (gpsString == "No") {
    digitalWrite(ledPin, LOW);
    digitalWrite(buzzerPin, LOW);
    oled.println("No");
  } else if (gpsString == "Detected") {
    digitalWrite(ledPin, HIGH);
    digitalWrite(buzzerPin, HIGH);  // Turn on buzzer
    oled.println("Crowd Detected");
  } else {
    digitalWrite(buzzerPin, LOW);
    oled.println("Waiting...");
  }

  oled.display();
  delay(2000);
}
