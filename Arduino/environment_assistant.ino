#include <Arduino.h>

// ---------- PINS ----------
const int lightPin = A0;
const int tempPin = A1;

const int greenLedPin = 9;
const int yellowLedPin = 10;

// ---------- STATE ----------
String incomingCommand = "";
String currentLedMode = "OFF";

unsigned long lastSendTime = 0;
const unsigned long sendInterval = 1000;

bool flashState = false;
unsigned long lastFlashTime = 0;
const unsigned long flashInterval = 500;

// ---------- SENSOR ----------

float readTemperatureC() {
  int raw = analogRead(tempPin);
  float voltage = raw * (5.0 / 1023.0);
  return (voltage - 0.5) * 100.0; // TMP36
}

int readLight() {
  return analogRead(lightPin);
}

// ---------- LED CONTROL ----------

void setLEDs(bool greenOn, bool yellowOn) {
  digitalWrite(greenLedPin, greenOn ? HIGH : LOW);
  digitalWrite(yellowLedPin, yellowOn ? HIGH : LOW);
}

void applySolidMode(String mode) {
  if (mode == "GREEN") {
    setLEDs(true, false);
  }
  else if (mode == "YELLOW") {
    setLEDs(false, true);
  }
  else if (mode == "OFF") {
    setLEDs(false, false);
  }
}

void updateFlashing() {
  if (currentLedMode != "GREEN_FLASH" && currentLedMode != "YELLOW_FLASH") {
    return;
  }

  unsigned long now = millis();
  if (now - lastFlashTime >= flashInterval) {
    lastFlashTime = now;
    flashState = !flashState;

    if (currentLedMode == "GREEN_FLASH") {
      setLEDs(flashState, false);
    }
    else if (currentLedMode == "YELLOW_FLASH") {
      setLEDs(false, flashState);
    }
  }
}

void setMode(String mode) {
  currentLedMode = mode;

  if (mode == "GREEN" || mode == "YELLOW" || mode == "OFF") {
    applySolidMode(mode);
  }
  else {
    flashState = false;
    lastFlashTime = millis();
    setLEDs(false, false);
  }
}

// ---------- SERIAL ----------

void sendData() {
  int light = readLight();
  float temp = readTemperatureC();

  Serial.print("{\"light\":");
  Serial.print(light);
  Serial.print(",\"temp\":");
  Serial.print(temp, 1);
  Serial.println("}");
}

void readCommands() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      incomingCommand.trim();
      setMode(incomingCommand);
      incomingCommand = "";
    } else {
      incomingCommand += c;
    }
  }
}

// ---------- SETUP ----------

void setup() {
  Serial.begin(9600);

  pinMode(greenLedPin, OUTPUT);
  pinMode(yellowLedPin, OUTPUT);

  setLEDs(false, false);
}

// ---------- LOOP ----------

void loop() {
  readCommands();
  updateFlashing();

  if (millis() - lastSendTime >= sendInterval) {
    lastSendTime = millis();
    sendData();
  }
}
