/*
  LoRa to WebSocket Gateway
  Acts as Roadside Unit (RSU) bridging C-V2X-style LoRa messages to network
  
  This gateway receives LoRa emergency broadcasts from the emergency vehicle
  and forwards them to the WebSocket server for distribution to all connected
  web clients (representing vehicles with network connectivity).
  
  Hardware Required:
  - TTGO LoRa32 V2 (ESP32 + LoRa + OLED display) - RECOMMENDED
    OR
  - ESP32 + RFM95W LoRa Module
  
  Installation:
  1. Install Arduino ESP32 board support:
     File → Preferences → Additional Board URLs:
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  
  2. Install required libraries:
     - LoRa by Sandeep Mistry
     - WebSockets by Markus Sattler
     - (TTGO only) U8g2 for OLED display
  
  3. Update WiFi credentials below
  4. Update WebSocket server IP below
  5. Upload to ESP32
  
  Operation:
  - Connects to WiFi and WebSocket server
  - Listens for LoRa emergency broadcasts
  - Forwards messages to web server
  - Displays status on OLED (if TTGO)
  
  Real-World Context:
  This represents a Roadside Unit (RSU) in C-V2X infrastructure.
  RSUs bridge direct V2V communication to network infrastructure.
*/

#include <WiFi.h>
#include <WebSocketsClient.h>
#include <SPI.h>
#include <LoRa.h>

// OLED Display support (for TTGO LoRa32)
#define HAS_DISPLAY true  // Set to false if using basic ESP32
#if HAS_DISPLAY
#include <Wire.h>
#include <U8g2lib.h>
U8G2_SSD1306_128X64_NONAME_F_HW_I2C display(U8G2_R0, /* reset=*/ 16, /* clock=*/ 15, /* data=*/ 4);
#endif

// ===============================================
// CONFIGURATION - UPDATE THESE!
// ===============================================

// WiFi Settings
const char* WIFI_SSID = "YOUR_WIFI_NAME";        // Change this!
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // Change this!

// WebSocket Server Settings
const char* WS_HOST = "192.168.1.100";  // Your laptop IP - Change this!
const uint16_t WS_PORT = 8765;
const char* WS_PATH = "/";

// LoRa Settings (must match emergency vehicle)
#define LORA_FREQUENCY    915E6   // 915 MHz (US) or 868E6 (EU)
#define LORA_SPREADING    7
#define LORA_BANDWIDTH    250E3

// TTGO LoRa32 V2 Pin Configuration
#define LORA_SS           18
#define LORA_RST          14
#define LORA_DIO0         26

// ===============================================
// GLOBAL VARIABLES
// ===============================================

WebSocketsClient webSocket;
bool wifiConnected = false;
bool wsConnected = false;
unsigned long lastStatusUpdate = 0;
int messagesReceived = 0;
int messagesForwarded = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println(F("\n╔════════════════════════════════════════════╗"));
  Serial.println(F("║   LoRa → WebSocket Gateway (RSU)          ║"));
  Serial.println(F("║   C-V2X Infrastructure Bridge             ║"));
  Serial.println(F("╚════════════════════════════════════════════╝\n"));
  
  // Initialize display if available
  #if HAS_DISPLAY
  display.begin();
  display.clearBuffer();
  display.setFont(u8g2_font_6x10_tf);
  display.drawStr(0, 10, "C-V2X Gateway");
  display.drawStr(0, 25, "Initializing...");
  display.sendBuffer();
  #endif
  
  // Initialize LoRa
  Serial.println(F("🔧 Initializing LoRa receiver..."));
  SPI.begin(5, 19, 27, 18);  // TTGO LoRa32 V2 SPI pins
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println(F("❌ LoRa initialization failed!"));
    #if HAS_DISPLAY
    display.clearBuffer();
    display.drawStr(0, 30, "LoRa FAILED!");
    display.sendBuffer();
    #endif
    while (1) {
      delay(1000);
    }
  }
  
  // Configure LoRa
  LoRa.setSpreadingFactor(LORA_SPREADING);
  LoRa.setSignalBandwidth(LORA_BANDWIDTH);
  
  Serial.println(F("✅ LoRa receiver ready"));
  Serial.print(F("   Frequency: ")); Serial.print(LORA_FREQUENCY / 1e6); Serial.println(F(" MHz"));
  
  // Connect to WiFi
  Serial.println(F("\n📶 Connecting to WiFi..."));
  Serial.print(F("   SSID: ")); Serial.println(WIFI_SSID);
  
  #if HAS_DISPLAY
  display.clearBuffer();
  display.drawStr(0, 10, "Connecting WiFi");
  display.drawStr(0, 25, WIFI_SSID);
  display.sendBuffer();
  #endif
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println(F("\n✅ WiFi connected!"));
    Serial.print(F("   IP Address: ")); Serial.println(WiFi.localIP());
    
    #if HAS_DISPLAY
    display.clearBuffer();
    display.drawStr(0, 10, "WiFi OK!");
    display.drawStr(0, 25, WiFi.localIP().toString().c_str());
    display.sendBuffer();
    delay(2000);
    #endif
    
    // Connect to WebSocket server
    connectWebSocket();
  } else {
    Serial.println(F("\n❌ WiFi connection failed!"));
    #if HAS_DISPLAY
    display.clearBuffer();
    display.drawStr(0, 30, "WiFi FAILED!");
    display.sendBuffer();
    #endif
  }
  
  Serial.println(F("\n🚀 Gateway operational"));
  Serial.println(F("   Listening for LoRa emergency broadcasts...\n"));
}

void loop() {
  // Handle WebSocket
  if (wifiConnected) {
    webSocket.loop();
  }
  
  // Check for LoRa packets
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    handleLoRaPacket();
  }
  
  // Update display periodically
  #if HAS_DISPLAY
  if (millis() - lastStatusUpdate > 1000) {
    updateDisplay();
    lastStatusUpdate = millis();
  }
  #endif
  
  // Reconnect WebSocket if disconnected
  if (wifiConnected && !wsConnected && (millis() % 5000 == 0)) {
    connectWebSocket();
  }
}

void connectWebSocket() {
  Serial.println(F("🔌 Connecting to WebSocket server..."));
  Serial.print(F("   Host: ")); Serial.print(WS_HOST); 
  Serial.print(F(":")); Serial.println(WS_PORT);
  
  webSocket.begin(WS_HOST, WS_PORT, WS_PATH);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      wsConnected = false;
      Serial.println(F("⚠️  WebSocket disconnected"));
      break;
      
    case WStype_CONNECTED:
      wsConnected = true;
      Serial.println(F("✅ WebSocket connected!"));
      Serial.println(F("   Ready to forward emergency broadcasts\n"));
      
      // Register as gateway device
      String registerMsg = "{\"type\":\"register\",\"device_id\":\"LORA_GATEWAY\",\"device_type\":\"gateway\"}";
      webSocket.sendTXT(registerMsg);
      break;
      
    case WStype_TEXT:
      Serial.print(F("📥 WS RX: "));
      Serial.println((char*)payload);
      break;
  }
}

void handleLoRaPacket() {
  messagesReceived++;
  
  // Read LoRa message
  String message = "";
  int rssi = LoRa.packetRssi();
  float snr = LoRa.packetSnr();
  
  while (LoRa.available()) {
    message += (char)LoRa.read();
  }
  
  Serial.println(F("📡 LoRa RX:"));
  Serial.print(F("   Message: ")); Serial.println(message);
  Serial.print(F("   RSSI: ")); Serial.print(rssi); Serial.println(F(" dBm"));
  Serial.print(F("   SNR: ")); Serial.print(snr); Serial.println(F(" dB"));
  
  // Parse message format: "BSM|EMG-001|EMERGENCY|123456|1"
  if (message.startsWith("BSM|")) {
    int firstPipe = message.indexOf('|');
    int secondPipe = message.indexOf('|', firstPipe + 1);
    int thirdPipe = message.indexOf('|', secondPipe + 1);
    
    if (secondPipe > 0 && thirdPipe > 0) {
      String vehicleId = message.substring(firstPipe + 1, secondPipe);
      String status = message.substring(secondPipe + 1, thirdPipe);
      
      Serial.print(F("   Vehicle: ")); Serial.println(vehicleId);
      Serial.print(F("   Status: ")); Serial.println(status);
      
      // Forward to WebSocket server
      if (wsConnected) {
        String jsonMsg;
        
        if (status == "EMERGENCY") {
          jsonMsg = "{\"type\":\"register_emergency\",\"device_id\":\"" + vehicleId + 
                    "\",\"source\":\"cv2x_lora\",\"rssi\":" + String(rssi) + 
                    ",\"snr\":" + String(snr) + "}";
        } else if (status == "CLEAR") {
          jsonMsg = "{\"type\":\"clear_emergency\",\"device_id\":\"" + vehicleId + 
                    "\",\"source\":\"cv2x_lora\"}";
        }
        
        if (jsonMsg.length() > 0) {
          webSocket.sendTXT(jsonMsg);
          messagesForwarded++;
          Serial.println(F("   ✅ Forwarded to WebSocket server"));
        }
      } else {
        Serial.println(F("   ⚠️  WebSocket not connected, message not forwarded"));
      }
      
      Serial.println();
    }
  }
}

#if HAS_DISPLAY
void updateDisplay() {
  display.clearBuffer();
  
  // Title
  display.setFont(u8g2_font_6x10_tf);
  display.drawStr(0, 10, "C-V2X RSU Gateway");
  display.drawLine(0, 12, 128, 12);
  
  // WiFi Status
  display.drawStr(0, 25, wifiConnected ? "WiFi: OK" : "WiFi: --");
  
  // WebSocket Status
  display.drawStr(65, 25, wsConnected ? "WS: OK" : "WS: --");
  
  // Message counters
  String rxStr = "RX: " + String(messagesReceived);
  String fwStr = "FW: " + String(messagesForwarded);
  display.drawStr(0, 40, rxStr.c_str());
  display.drawStr(65, 40, fwStr.c_str());
  
  // Signal info
  if (messagesReceived > 0) {
    display.drawStr(0, 55, "Last RSSI:");
    display.drawStr(60, 55, String(LoRa.packetRssi()).c_str());
  }
  
  display.sendBuffer();
}
#endif

