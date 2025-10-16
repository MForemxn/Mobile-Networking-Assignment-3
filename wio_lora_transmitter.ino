/*
 * LoRa Transmitter (Second Device)
 * 
 * This code runs on a second Wio-SX1262 module that transmits packets
 * so the receiver can measure distance
 * 
 * Same pinout as the receiver
 */

#include <RadioLib.h>

// SX1262 pin definitions for Wio-SX1262 + XIAO ESP32S3
#define LORA_CS    5   // D3
#define LORA_DIO1  3   // D1
#define LORA_RST   4   // D2
#define LORA_BUSY  2   // D0
#define LORA_MOSI  9   // D10
#define LORA_MISO  8   // D9
#define LORA_SCK   7   // D8

// LoRa module
SX1262 radio = new Module(LORA_CS, LORA_DIO1, LORA_RST, LORA_BUSY);

// LoRa parameters (must match receiver!)
const float frequency = 915.0;  // US frequency, use 868.0 for EU
const float bandwidth = 125.0;
const uint8_t spreadingFactor = 7;
const uint8_t codingRate = 5;
const int8_t outputPower = 22;

int packetCounter = 0;

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Serial.println("LoRa Transmitter");
  Serial.println("================");
  
  // Initialize SPI
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
  
  // Initialize LoRa
  Serial.print("Initializing SX1262... ");
  int state = radio.begin(frequency, bandwidth, spreadingFactor, codingRate, 0x12, outputPower);
  
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("Success!");
  } else {
    Serial.print("Failed, code: ");
    Serial.println(state);
    while (true);
  }
  
  Serial.println("Transmitting packets every second...");
}

void loop() {
  Serial.print("Sending packet ");
  Serial.print(packetCounter);
  Serial.print("... ");
  
  String message = "Ping " + String(packetCounter);
  
  int state = radio.transmit(message);
  
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("Success!");
  } else {
    Serial.print("Failed, code: ");
    Serial.println(state);
  }
  
  packetCounter++;
  delay(1000);
}

