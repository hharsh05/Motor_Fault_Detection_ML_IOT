#include <Arduino.h>
#include <Wire.h>
#include <MPU6050.h>

// -------- PIN DEFINITIONS --------
#define CURRENT_PIN 34
#define TEMP_PIN 35
#define HALL_PIN 5
#define HX_DOUT 6
#define HX_SCK 7

MPU6050 mpu;

// -------- VARIABLES --------
volatile int pulseCount = 0;
unsigned long lastTime = 0;

float sensitivity = 0.185;   // ACS712 (5A)
float offsetVoltage = 0;

// Pressure calibration
float pressureOffset = 1640000;
float pressureScale = 0.0001;

// -------- INTERRUPT --------
void IRAM_ATTR countPulse() {
  pulseCount++;
}

// -------- HX READ --------
long readHX() {
  long count = 0;

  while (digitalRead(HX_DOUT));

  for (int i = 0; i < 24; i++) {
    digitalWrite(HX_SCK, HIGH);
    delayMicroseconds(1);

    count = count << 1;

    digitalWrite(HX_SCK, LOW);
    delayMicroseconds(1);

    if (digitalRead(HX_DOUT)) count++;
  }

  digitalWrite(HX_SCK, HIGH);
  delayMicroseconds(1);
  digitalWrite(HX_SCK, LOW);

  if (count & 0x800000) {
    count |= ~0xFFFFFF;
  }

  return count;
}

// -------- SETUP --------
void setup() {
  Serial.begin(115200);

  pinMode(HALL_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(HALL_PIN), countPulse, FALLING);

  pinMode(HX_DOUT, INPUT);
  pinMode(HX_SCK, OUTPUT);

  Wire.begin(8, 9);
  mpu.initialize();

  // Current sensor calibration
  float sum = 0;
  for (int i = 0; i < 200; i++) {
    sum += analogRead(CURRENT_PIN);
    delay(5);
  }

  float avg = sum / 200.0;
  offsetVoltage = avg * (3.3 / 4095.0);

  lastTime = millis();
}

// -------- LOOP --------
void loop() {

  // -------- CURRENT --------
  float sum = 0;
  for (int i = 0; i < 50; i++) {
    sum += analogRead(CURRENT_PIN);
  }

  float avgADC = sum / 50.0;
  float voltage = avgADC * (3.3 / 4095.0);
  float current = (voltage - offsetVoltage) / sensitivity;

  // -------- TEMPERATURE --------
  int tempADC = analogRead(TEMP_PIN);
  float tempVoltage = tempADC * (3.3 / 4095.0);
  float temperature = tempVoltage * 100;

  // -------- RPM --------
  int rpm = 0;
  if (millis() - lastTime >= 1000) {
    rpm = pulseCount * 60;
    pulseCount = 0;
    lastTime = millis();
  }

  // -------- MPU6050 --------
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);

  // -------- PRESSURE --------
  long pressureRaw = readHX();
  float pressurePSI = (pressureRaw - pressureOffset) * pressureScale;

  // -------- CSV OUTPUT --------
  Serial.print(current);
  Serial.print(",");
  Serial.print(rpm);
  Serial.print(",");
  Serial.print(temperature);
  Serial.print(",");
  Serial.print(ax);
  Serial.print(",");
  Serial.print(ay);
  Serial.print(",");
  Serial.print(az);
  Serial.print(",");
  Serial.println(pressurePSI);

  delay(500);
}
