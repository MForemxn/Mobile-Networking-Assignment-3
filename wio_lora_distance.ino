/*
 * Wio-SX1262 with XIAO ESP32S3 - LoRa Distance Measurement
 * Serial Communication Version
 * 
 * Hardware: Seeed Studio Wio-SX1262 + XIAO ESP32S3
 * 
 * PINOUT (Wio-SX1262 to XIAO ESP32S3):
 * The Wio-SX1262 module is designed to connect directly to XIAO form factor
 * 
 * SX1262 LoRa connections (built into Wio module):
 * - MOSI: D10 (GPIO 9)
 * - MISO: D9  (GPIO 8)
 * - SCK:  D8  (GPIO 7)
 * - CS:   D3  (GPIO 5)
 * - RST:  D2  (GPIO 4)
 * - DIO1: D1  (GPIO 3)
 * - BUSY: D0  (GPIO 2)
 * 
 * Sends JSON data over Serial USB to laptop
 */

#include <RadioLib.h>
#include <ArduinoJson.h>

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

// Distance data
float estimatedDistance = 0;
int rssi = 0;
float snr = 0;
unsigned long lastPacketTime = 0;
int packetCount = 0;
String lastMessage = "";

// LoRa parameters
const float frequency = 915.0;  // US frequency, use 868.0 for EU
const float bandwidth = 125.0;
const uint8_t spreadingFactor = 7;
const uint8_t codingRate = 5;
const int8_t outputPower = 22;

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  // Send ready signal
  Serial.println("{\"status\":\"initializing\",\"device\":\"Wio-SX1262\"}");
  
  // Initialize SPI
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
  
  // Initialize LoRa
  int state = radio.begin(frequency, bandwidth, spreadingFactor, codingRate, 0x12, outputPower);
  
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("{\"status\":\"ready\",\"message\":\"SX1262 initialized successfully\"}");
  } else {
    Serial.print("{\"status\":\"error\",\"message\":\"SX1262 init failed\",\"code\":");
    Serial.print(state);
    Serial.println("}");
    while (true);
  }
  
  // Set to receive mode
  radio.setDio1Action(setFlag);
  radio.startReceive();
  
  Serial.println("{\"status\":\"listening\",\"frequency\":" + String(frequency) + "}");
}

volatile bool receivedFlag = false;

void setFlag(void) {
  receivedFlag = true;
}

void loop() {
  // Check for received LoRa packet
  if (receivedFlag) {
    receivedFlag = false;
    
    String message;
    int state = radio.readData(message);
    
    if (state == RADIOLIB_ERR_NONE) {
      // Get RSSI and SNR
      rssi = radio.getRSSI();
      snr = radio.getSNR();
      
      // Estimate distance based on RSSI
      float pathLossExponent = 2.5;
      float measuredPower = -40; // RSSI at 1 meter (calibrate this!)
      
      if (rssi < 0) {
        estimatedDistance = pow(10, (measuredPower - rssi) / (10 * pathLossExponent));
      }
      
      lastPacketTime = millis();
      packetCount++;
      lastMessage = message;
      
      // Send JSON data over serial
      sendDataUpdate();
    }
    
    // Put module back to listen mode
    radio.startReceive();
  }
  
  // Send periodic updates even if no new packet (every 1 second)
  static unsigned long lastUpdateTime = 0;
  if (millis() - lastUpdateTime > 1000) {
    lastUpdateTime = millis();
    
    // Reset distance if no packet received in 5 seconds
    if (millis() - lastPacketTime > 5000 && lastPacketTime != 0) {
      estimatedDistance = 0;
      rssi = 0;
      snr = 0;
      lastMessage = "";
    }
    
    sendDataUpdate();
  }
}

void sendDataUpdate() {
  // Create JSON object
  StaticJsonDocument<256> doc;
  
  doc["type"] = "data";
  doc["distance"] = round(estimatedDistance * 10) / 10.0; // Round to 1 decimal
  doc["rssi"] = rssi;
  doc["snr"] = round(snr * 10) / 10.0;
  doc["packets"] = packetCount;
  doc["message"] = lastMessage;
  doc["timestamp"] = millis();
  doc["connected"] = (estimatedDistance > 0);
  
  // Serialize and send
  serializeJson(doc, Serial);
  Serial.println();
}

