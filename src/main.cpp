
#include <Arduino.h>
#include <AlashTCS3200.h>

AlashTCS3200 sensor;

#define PIN_OUT 0
#define PIN_S0  1
#define PIN_S1  4
#define PIN_S2  5
#define PIN_S3  6
#define PIN_LED 7

void setup() {
  Serial.begin(115200);
  delay(1500);

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);  // Try HIGH later if LEDs remain off

  Serial.println("Starting TCS3200 test...");

  bool ok = sensor.begin(
    PIN_S0, PIN_S1, PIN_S2, PIN_S3, PIN_OUT
  );

  sensor.setLanguage(AlashTCS3200::LANG_EN);

  Serial.print("Sensor signal: ");
  Serial.println(ok ? "OK" : "NO SIGNAL");

  Serial.println(sensor.errorText());

  sensor.diagnose(Serial);
}

void loop() {
  uint32_t r, g, b, c;

  if (sensor.readRaw(r, g, b, c)) {
    Serial.print("R=");
    Serial.print(r);
    Serial.print(" G=");
    Serial.print(g);
    Serial.print(" B=");
    Serial.print(b);
    Serial.print(" C=");
    Serial.println(c);
  } else {
    Serial.print("READ ERROR: ");
    Serial.println(sensor.errorText());
  }

  delay(1000);
}
