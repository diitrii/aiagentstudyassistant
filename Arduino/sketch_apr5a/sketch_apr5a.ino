#include <Arduino.h>
#include <math.h>

// ---------- PINS ----------
const int lightPin = A0;
const int tempPin = A1;

const int greenLedPin = 10;
const int yellowLedPin = 9;
const int redLedPin = 8;
const int blueLedPin = 7;

// ---------- TIMING ----------
unsigned long lastSampleTime = 0;
const unsigned long sampleInterval = 500;

// ---------- THRESHOLDS ----------
const int lightThreshold = 300;

const float lowTempThreshold = 55.0;
const float highTempThreshold = 60.0;

// ---------- SENSOR FUNCTIONS ----------
float readTemperatureC() {
  int raw = analogRead(tempPin);

  float resistance = (1023.0 - raw) * 100000.0 / raw;

  float temperature =
      1.0 / (log(resistance / 100000.0) / 4275.0 + 1 / 298.15) - 273.15;

  return temperature;
}

int readLight() {
  return analogRead(lightPin);
}

// ---------- LED CONTROL ----------
void setLEDs(bool greenOn, bool yellowOn, bool redOn, bool blueOn) {
  digitalWrite(greenLedPin, greenOn ? HIGH : LOW);
  digitalWrite(yellowLedPin, yellowOn ? HIGH : LOW);
  digitalWrite(redLedPin, redOn ? HIGH : LOW);
  digitalWrite(blueLedPin, blueOn ? HIGH : LOW);
}
// ---------- SETUP ----------
void setup() {
  Serial.begin(9600);

  pinMode(greenLedPin, OUTPUT);
  pinMode(yellowLedPin, OUTPUT);
  pinMode(redLedPin, OUTPUT);
  pinMode(blueLedPin, OUTPUT);

  setLEDs(false, false, false, false);
}

// ---------- LOOP ----------
void loop() {
  unsigned long now = millis();

  if (now - lastSampleTime >= sampleInterval) {
    lastSampleTime = now;

    int light = readLight();
    float temp = readTemperatureC();

    // Print readings
    Serial.print("Light: ");
    Serial.print(light);
    Serial.print(" | Temp: ");
    Serial.print(temp);
    Serial.println(" C");

    // Priority:
    // 1. Too hot -> red
    // 2. Too cold -> blue
    // 3. Too dark -> yellow
    // 4. Otherwise -> green

    if (temp > highTempThreshold) {
      setLEDs(false, false, true, false);
    }
    else if (temp < lowTempThreshold) {
      setLEDs(false, false, false, true);
    }
    else if (light > lightThreshold) {
      setLEDs(false, true, false, false);
    }
    else {
      setLEDs(true, false, false, false);
    }
  }
}