/*
  C-V2X Emergency Receiver with LED Indicator
  Receives LoRa emergency broadcasts and provides visual confirmation
  
  This device:
  1. Receives LoRa emergency broadcasts from transmitter
  2. Lights LED to PROVE RF communication is working
  3. Forwards messages to computer via USB serial
  4. Computer controls the web-based simulation
  
  Hardware Required:
  - TTGO LoRa32 V2 (ESP32 + LoRa + OLED) - RECOMMENDED
    OR
  - ESP32 + RFM95W LoRa Module
  
  Additional:
  - LED on GPIO pin (built-in LED works)
  - Buzzer (optional) for audio feedback
  
  TTGO LoRa32 V2 Pinout:
  - Built-in LoRa (no wiring!)
  - Built-in OLED display
  - Built-in LED on GPIO 25 or use external on any GPIO
  - USB for serial to computer
  
  Installation:
  1. Install ESP32 board support in Arduino IDE
  2. Install libraries: LoRa, U8g2 (for OLED)
  3. Select board: "TTGO LoRa32-OLED V1" or "ESP32 Dev Module"
  4. Upload this sketch
  5. Connect to computer via USB
  6. Open Serial Monitor at 115200 baud
  
  Operation:
  - Continuously listens for LoRa messages
  - When emergency received:
    → LED turns ON (solid)
    → OLED shows "EMERGENCY!"
    → Sends to computer: "EMERGENCY_DETECTED"
  - When clear received:
    → LED turns OFF
    → OLED shows "Clear"
    → Sends to computer: "EMERGENCY_CLEAR"
*/

#include <SPI.h>
#include <LoRa.h>
#include <Wire.h>
#include <U8g2lib.h>

// ===============================================
// CONFIGURATION
// ===============================================

// LoRa Settings (MUST match transmitter!)
#define LORA_FREQUENCY    915E6   // 915 MHz (US) or 868E6 (EU)
#define LORA_SPREADING    7
#define LORA_BANDWIDTH    250E3

// TTGO LoRa32 V2 Pin Configuration
#define LORA_SS           18
#define LORA_RST          14
#define LORA_DIO0         26

// LED and Buzzer
#define LED_PIN           25      // TTGO built-in LED (or change to your pin)
#define BUZZER_PIN        -1      // Set to GPIO pin if using buzzer, -1 to disable

// Display (TTGO has built-in OLED)
U8G2_SSD1306_128X64_NONAME_F_HW_I2C display(U8G2_R0, /* reset=*/ 16, /* clock=*/ 15, /* data=*/ 4);

// ===============================================
// GLOBAL VARIABLES
// ===============================================

bool emergencyActive = false;
unsigned long lastMessageTime = 0;
int messagesReceived = 0;
String lastVehicleId = "";
int lastRSSI = 0;
float lastSNR = 0.0;

void setup() {
  // Initialize serial for computer communication
  Serial.begin(115200);
  delay(1000);
  
  Serial.println(F("\n╔════════════════════════════════════════════╗"));
  Serial.println(F("║   C-V2X Emergency Receiver (RSU)          ║"));
  Serial.println(F("║   LoRa → LED → Serial → Computer          ║"));
  Serial.println(F("╚════════════════════════════════════════════╝\n"));
  
  // Initialize LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Initialize buzzer if enabled
  if (BUZZER_PIN >= 0) {
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
  }
  
  // Initialize OLED display
  display.begin();
  display.clearBuffer();
  display.setFont(u8g2_font_6x10_tf);
  display.drawStr(0, 10, "C-V2X Receiver");
  display.drawStr(0, 25, "Initializing...");
  display.sendBuffer();
  
  // Initialize LoRa
  SPI.begin(5, 19, 27, 18);  // TTGO LoRa32 V2 SPI pins
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  
  Serial.println(F("🔧 Initializing LoRa receiver..."));
  
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println(F("❌ LoRa initialization failed!"));
    display.clearBuffer();
    display.drawStr(0, 30, "LoRa FAILED!");
    display.sendBuffer();
    
    // Blink LED rapidly to show error
    while (1) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      delay(100);
    }
  }
  
  // Configure LoRa (match transmitter settings)
  LoRa.setSpreadingFactor(LORA_SPREADING);
  LoRa.setSignalBandwidth(LORA_BANDWIDTH);
  LoRa.enableCrc();
  
  Serial.println(F("✅ LoRa receiver ready!"));
  Serial.print(F("   Frequency: ")); Serial.print(LORA_FREQUENCY / 1e6); Serial.println(F(" MHz"));
  Serial.print(F("   Spread: SF")); Serial.println(LORA_SPREADING);
  Serial.println(F("\n🎧 Listening for emergency broadcasts...\n"));
  
  // Update display
  display.clearBuffer();
  display.drawStr(0, 10, "C-V2X Receiver");
  display.drawLine(0, 12, 128, 12);
  display.drawStr(0, 25, "Status: Ready");
  String freqStr = String(LORA_FREQUENCY / 1e6, 0) + " MHz";
  display.drawStr(0, 40, freqStr.c_str());
  display.drawStr(0, 55, "Waiting...");
  display.sendBuffer();
  
  // Startup beep if buzzer enabled
  if (BUZZER_PIN >= 0) {
    tone(BUZZER_PIN, 1000, 100);
  }
  
  // Flash LED to show ready
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
  
  // Send ready signal to computer
  Serial.println("RECEIVER_READY");
}

void loop() {
  // Check for incoming LoRa packets
  int packetSize = LoRa.parsePacket();
  
  if (packetSize) {
    handleLoRaPacket();
  }
  
  // Timeout emergency state if no messages for 5 seconds
  if (emergencyActive && (millis() - lastMessageTime > 5000)) {
    clearEmergencyState();
    Serial.println(F("⚠️  Emergency timeout - no messages for 5 seconds"));
  }
  
  // Update display every second
  static unsigned long lastDisplayUpdate = 0;
  if (millis() - lastDisplayUpdate > 1000) {
    updateDisplay();
    lastDisplayUpdate = millis();
  }
}

void handleLoRaPacket() {
  messagesReceived++;
  lastMessageTime = millis();
  
  // Read packet
  String message = "";
  while (LoRa.available()) {
    message += (char)LoRa.read();
  }
  
  // Get signal quality metrics
  lastRSSI = LoRa.packetRssi();
  lastSNR = LoRa.packetSnr();
  
  // Log reception
  Serial.println(F("┌─────────────────────────────────────┐"));
  Serial.println(F("│  📡 LoRa Message Received          │"));
  Serial.println(F("└─────────────────────────────────────┘"));
  Serial.print(F("Message: ")); Serial.println(message);
  Serial.print(F("RSSI:    ")); Serial.print(lastRSSI); Serial.println(F(" dBm"));
  Serial.print(F("SNR:     ")); Serial.print(lastSNR); Serial.println(F(" dB"));
  Serial.print(F("Count:   ")); Serial.println(messagesReceived);
  
  // Parse BSM message format: "BSM|EMG-001|EMERGENCY|timestamp|count"
  if (message.startsWith("BSM|")) {
    int pipe1 = message.indexOf('|');
    int pipe2 = message.indexOf('|', pipe1 + 1);
    int pipe3 = message.indexOf('|', pipe2 + 1);
    
    if (pipe1 > 0 && pipe2 > 0) {
      String vehicleId = message.substring(pipe1 + 1, pipe2);
      String status = message.substring(pipe2 + 1, pipe3);
      
      lastVehicleId = vehicleId;
      
      if (status == "EMERGENCY") {
        activateEmergency(vehicleId);
      } else if (status == "CLEAR") {
        clearEmergencyState();
      }
    }
  }
  
  Serial.println();
}

void activateEmergency(String vehicleId) {
  if (!emergencyActive) {
    emergencyActive = true;
    
    // Turn on LED (PROOF of RF communication!)
    digitalWrite(LED_PIN, HIGH);
    
    // Sound buzzer if enabled
    if (BUZZER_PIN >= 0) {
      tone(BUZZER_PIN, 2000, 200);  // High pitched beep
    }
    
    Serial.println(F("╔═══════════════════════════════════════╗"));
    Serial.println(F("║  🚨 EMERGENCY DETECTED VIA LORA! 🚨  ║"));
    Serial.println(F("╚═══════════════════════════════════════╝"));
    Serial.print(F("Vehicle: ")); Serial.println(vehicleId);
    Serial.print(F("Signal: ")); Serial.print(lastRSSI); Serial.println(F(" dBm"));
    
    // Send to computer (Python server reads this!)
    Serial.println("EMERGENCY_DETECTED");
    Serial.flush();
  }
  
  // Update display
  updateDisplay();
}

void clearEmergencyState() {
  if (emergencyActive) {
    emergencyActive = false;
    
    // Turn off LED
    digitalWrite(LED_PIN, LOW);
    
    // Beep cleared if buzzer enabled
    if (BUZZER_PIN >= 0) {
      tone(BUZZER_PIN, 1000, 100);  // Lower pitch
    }
    
    Serial.println(F("╔═══════════════════════════════════════╗"));
    Serial.println(F("║  🟢 EMERGENCY CLEARED 🟢             ║"));
    Serial.println(F("╚═══════════════════════════════════════╝"));
    
    // Send to computer
    Serial.println("EMERGENCY_CLEAR");
    Serial.flush();
  }
  
  updateDisplay();
}

void updateDisplay() {
  display.clearBuffer();
  
  // Title
  display.setFont(u8g2_font_6x10_tf);
  display.drawStr(0, 10, "C-V2X Receiver");
  display.drawLine(0, 12, 128, 12);
  
  // Emergency status (large font for visibility)
  if (emergencyActive) {
    display.setFont(u8g2_font_9x15_tf);
    display.drawStr(10, 32, "EMERGENCY!");
    display.setFont(u8g2_font_6x10_tf);
    
    // Blink indicator
    if ((millis() / 500) % 2 == 0) {
      display.drawStr(0, 45, ">>> ACTIVE <<<");
    }
  } else {
    display.setFont(u8g2_font_6x10_tf);
    display.drawStr(0, 30, "Status: Ready");
    display.drawStr(0, 45, "Waiting for signal");
  }
  
  // Stats
  String stats = "RX: " + String(messagesReceived);
  display.drawStr(0, 60, stats.c_str());
  
  if (lastRSSI != 0) {
    String rssi = "RSSI:" + String(lastRSSI);
    display.drawStr(65, 60, rssi.c_str());
  }
  
  display.sendBuffer();
}

