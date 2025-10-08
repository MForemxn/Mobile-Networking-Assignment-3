/*
  C-V2X Emergency Vehicle Transmitter
  Simulates emergency vehicle broadcasting using LoRa radio
  
  This demo uses LoRa (Long Range radio) to simulate C-V2X (Cellular Vehicle-to-Everything)
  direct communication mode. In production, this would use 5.9 GHz C-V2X radios.
  
  Hardware Required:
  - Arduino Uno or Nano
  - RFM95W LoRa Module (915 MHz for US, 868 MHz for EU)
  - Push button
  - LED (built-in on pin 13)
  
  Wiring:
  LoRa Module → Arduino:
  - VCC  → 3.3V (IMPORTANT: NOT 5V!)
  - GND  → GND
  - SCK  → Pin 13 (SCK)
  - MISO → Pin 12 (MISO)
  - MOSI → Pin 11 (MOSI)
  - NSS  → Pin 10 (CS)
  - RST  → Pin 9
  - DIO0 → Pin 2
  
  Button → Arduino:
  - One side → Pin 3
  - Other side → GND
  
  LED:
  - Built-in LED on Pin 13 (no wiring needed)
  
  Installation:
  1. Install LoRa library: Arduino IDE → Tools → Manage Libraries → Search "LoRa" by Sandeep Mistry
  2. Upload this sketch to your Arduino
  3. Open Serial Monitor at 115200 baud to see status
  
  Operation:
  - Press button once: Activates emergency broadcast
  - Press button again: Clears emergency
  - LED blinks rapidly when emergency is active
  
  Real-World Context:
  This simulates how C-V2X emergency vehicle preemption works:
  - Emergency vehicle broadcasts BSM (Basic Safety Message) with emergency flag
  - Message transmitted every 100ms (10 Hz) as per SAE J2945/1 standard
  - Other vehicles within range receive and respond
  - In production: 5.9 GHz C-V2X, here: 915 MHz LoRa
*/

#include <SPI.h>
#include <LoRa.h>

// ===============================================
// CONFIGURATION - Adjust for your region
// ===============================================

// Frequency: 915 MHz (US/Australia) or 868 MHz (Europe)
#define LORA_FREQUENCY    915E6   // Change to 868E6 for Europe

// LoRa Settings (optimized for low latency like C-V2X)
#define LORA_TX_POWER     20      // 20 dBm maximum
#define LORA_SPREADING    7       // SF7 = lowest latency (like C-V2X)
#define LORA_BANDWIDTH    250E3   // 250 kHz bandwidth
#define LORA_CODING_RATE  5       // 4/5 coding rate

// Pin Definitions
#define BUTTON_PIN        3       // Emergency button input
#define STATUS_LED        13      // Status LED (built-in)
#define LORA_SS           10      // LoRa chip select
#define LORA_RST          9       // LoRa reset pin
#define LORA_DIO0         2       // LoRa interrupt pin

// Timing (matches C-V2X BSM transmission rate)
#define BSM_INTERVAL      100     // Transmit every 100ms (10 Hz per SAE J2945/1)

// Vehicle Information
const String VEHICLE_ID = "EMG-001";      // Emergency vehicle identifier
const String VEHICLE_TYPE = "AMBULANCE";  // Vehicle type

// ===============================================
// GLOBAL VARIABLES
// ===============================================

bool emergencyActive = false;
unsigned long lastTransmission = 0;
unsigned long emergencyStartTime = 0;
int transmissionCount = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  while (!Serial);
  
  Serial.println(F("\n╔════════════════════════════════════════════╗"));
  Serial.println(F("║   C-V2X Emergency Vehicle Transmitter     ║"));
  Serial.println(F("║   Using LoRa for V2V Communication        ║"));
  Serial.println(F("╚════════════════════════════════════════════╝\n"));
  
  // Configure pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(STATUS_LED, OUTPUT);
  digitalWrite(STATUS_LED, LOW);
  
  // Initialize LoRa module
  Serial.println(F("🔧 Initializing LoRa module..."));
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println(F("❌ ERROR: LoRa initialization failed!"));
    Serial.println(F("   Check wiring and connections."));
    while (1) {
      // Blink LED rapidly to indicate error
      digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
      delay(100);
    }
  }
  
  // Configure LoRa parameters for C-V2X-like performance
  LoRa.setSpreadingFactor(LORA_SPREADING);
  LoRa.setSignalBandwidth(LORA_BANDWIDTH);
  LoRa.setTxPower(LORA_TX_POWER);
  LoRa.setCodingRate4(LORA_CODING_RATE);
  LoRa.enableCrc();
  
  Serial.println(F("✅ LoRa module initialized successfully!\n"));
  Serial.println(F("📡 Configuration:"));
  Serial.print(F("   Frequency:  ")); Serial.print(LORA_FREQUENCY / 1e6); Serial.println(F(" MHz"));
  Serial.print(F("   TX Power:   ")); Serial.print(LORA_TX_POWER); Serial.println(F(" dBm"));
  Serial.print(F("   Spread:     SF")); Serial.println(LORA_SPREADING);
  Serial.print(F("   Bandwidth:  ")); Serial.print(LORA_BANDWIDTH / 1e3); Serial.println(F(" kHz"));
  Serial.println();
  Serial.println(F("🚨 C-V2X Emergency System Ready"));
  Serial.println(F("   Vehicle ID: ") + VEHICLE_ID);
  Serial.println(F("   Type: ") + VEHICLE_TYPE);
  Serial.println(F("\n📍 Press button to activate emergency mode\n"));
}

void loop() {
  // Check button state (with debouncing)
  static bool lastButtonState = HIGH;
  static unsigned long lastDebounceTime = 0;
  const unsigned long DEBOUNCE_DELAY = 50;
  
  bool currentButtonState = digitalRead(BUTTON_PIN);
  
  if (currentButtonState != lastButtonState) {
    lastDebounceTime = millis();
  }
  
  if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
    if (currentButtonState == LOW && lastButtonState == HIGH) {
      // Button pressed (falling edge)
      toggleEmergency();
    }
  }
  
  lastButtonState = currentButtonState;
  
  // Transmit emergency BSM periodically when active
  if (emergencyActive && (millis() - lastTransmission >= BSM_INTERVAL)) {
    transmitEmergencyBSM();
    lastTransmission = millis();
  }
  
  // LED feedback when emergency active
  if (emergencyActive) {
    // Rapid blink pattern (250ms on/off)
    static unsigned long lastBlink = 0;
    if (millis() - lastBlink > 250) {
      digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
      lastBlink = millis();
    }
  } else {
    // LED off when inactive
    digitalWrite(STATUS_LED, LOW);
  }
}

void toggleEmergency() {
  emergencyActive = !emergencyActive;
  
  if (emergencyActive) {
    // Emergency ACTIVATED
    Serial.println(F("\n╔═══════════════════════════════════════╗"));
    Serial.println(F("║  🚨 EMERGENCY MODE ACTIVATED 🚨      ║"));
    Serial.println(F("╚═══════════════════════════════════════╝"));
    Serial.println(F("Broadcasting emergency BSM messages..."));
    Serial.println(F("Transmission rate: 10 Hz (every 100ms)\n"));
    
    emergencyStartTime = millis();
    transmissionCount = 0;
    digitalWrite(STATUS_LED, HIGH);
    
    // Send immediate emergency notification
    transmitEmergencyBSM();
    lastTransmission = millis();
    
  } else {
    // Emergency CLEARED
    unsigned long duration = (millis() - emergencyStartTime) / 1000;
    
    Serial.println(F("\n╔═══════════════════════════════════════╗"));
    Serial.println(F("║  🟢 EMERGENCY MODE CLEARED 🟢        ║"));
    Serial.println(F("╚═══════════════════════════════════════╝"));
    Serial.print(F("Duration: ")); Serial.print(duration); Serial.println(F(" seconds"));
    Serial.print(F("Messages sent: ")); Serial.println(transmissionCount);
    Serial.println();
    
    digitalWrite(STATUS_LED, LOW);
    
    // Send clear message
    transmitClearMessage();
  }
}

void transmitEmergencyBSM() {
  /*
    Simulates C-V2X Basic Safety Message (BSM) Part I
    
    Real BSM contains (per SAE J2735):
    - Message ID
    - Vehicle ID (temporary ID rotated for privacy)
    - Timestamp (DSecond - 1/100 sec resolution)
    - Position (Latitude/Longitude)
    - Elevation
    - Positional Accuracy
    - Speed
    - Heading
    - Steering Wheel Angle
    - Acceleration (longitudinal/lateral/vertical/yaw)
    - Brake System Status
    - Vehicle Size
    - SPECIAL: Emergency Vehicle Alert flag
    
    Our simplified demo version includes:
    - Message type (BSM)
    - Vehicle ID
    - Status (EMERGENCY)
    - Timestamp
    - Transmission count
  */
  
  transmissionCount++;
  
  // Build BSM message (format: BSM|VehicleID|Status|Timestamp|Count)
  String bsm = "BSM|" + VEHICLE_ID + "|EMERGENCY|" + 
               String(millis()) + "|" + String(transmissionCount);
  
  // Transmit via LoRa
  LoRa.beginPacket();
  LoRa.print(bsm);
  LoRa.endPacket();
  
  // Log transmission
  Serial.print(F("📡 TX ["));
  Serial.print(transmissionCount);
  Serial.print(F("]: "));
  Serial.println(bsm);
}

void transmitClearMessage() {
  // Send emergency clear message
  String clearMsg = "BSM|" + VEHICLE_ID + "|CLEAR|" + String(millis());
  
  LoRa.beginPacket();
  LoRa.print(clearMsg);
  LoRa.endPacket();
  
  Serial.print(F("📡 TX: "));
  Serial.println(clearMsg);
}

