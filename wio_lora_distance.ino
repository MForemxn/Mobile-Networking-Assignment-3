/*
 * Wio-SX1262 with XIAO ESP32S3 - LoRa Distance Measurement
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
 */

#include <WiFi.h>
#include <WebServer.h>
#include <RadioLib.h>

// WiFi credentials - CHANGE THESE
const char* ssid = "Nothing Phone (3a)_1378";
const char* password = "password";

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

// Web server
WebServer server(80);

// Distance data
float estimatedDistance = 0;
int rssi = 0;
float snr = 0;
unsigned long lastPacketTime = 0;
int packetCount = 0;

// LoRa parameters
const float frequency = 915.0;  // US frequency, use 868.0 for EU
const float bandwidth = 125.0;
const uint8_t spreadingFactor = 7;
const uint8_t codingRate = 5;
const int8_t outputPower = 22;

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Serial.println("Wio-SX1262 Distance Measurement");
  Serial.println("================================");
  
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
  
  // Set to receive mode
  radio.setDio1Action(setFlag);
  radio.startReceive();
  
  // Connect to WiFi
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Setup web server routes
  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.onNotFound(handleNotFound);
  
  server.begin();
  Serial.println("HTTP server started");
  Serial.println("Open http://" + WiFi.localIP().toString() + " in your browser");
}

volatile bool receivedFlag = false;

void setFlag(void) {
  receivedFlag = true;
}

void loop() {
  server.handleClient();
  
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
      // Free space path loss formula: distance = 10^((TxPower - RSSI - 20*log10(frequency)) / 20)
      // Simplified empirical formula: distance ≈ 10^((TxPower - RSSI) / (10 * n))
      // where n is path loss exponent (2-4, we use 2.5 for typical environments)
      
      float pathLossExponent = 2.5;
      float measuredPower = -40; // RSSI at 1 meter (calibrate this!)
      
      if (rssi < 0) {
        estimatedDistance = pow(10, (measuredPower - rssi) / (10 * pathLossExponent));
      }
      
      lastPacketTime = millis();
      packetCount++;
      
      Serial.println("Packet received!");
      Serial.print("  Message: ");
      Serial.println(message);
      Serial.print("  RSSI: ");
      Serial.print(rssi);
      Serial.println(" dBm");
      Serial.print("  SNR: ");
      Serial.print(snr);
      Serial.println(" dB");
      Serial.print("  Estimated distance: ");
      Serial.print(estimatedDistance);
      Serial.println(" meters");
      Serial.println();
    }
    
    // Put module back to listen mode
    radio.startReceive();
  }
  
  // Reset distance if no packet received in 5 seconds
  if (millis() - lastPacketTime > 5000 && lastPacketTime != 0) {
    estimatedDistance = 0;
    rssi = 0;
    snr = 0;
  }
}

void handleRoot() {
  String html = R"=====(
<!DOCTYPE html>
<html>
<head>
  <title>LoRa Distance Monitor</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }
    .container {
      background: white;
      border-radius: 20px;
      padding: 40px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      max-width: 600px;
      width: 100%;
    }
    h1 {
      color: #333;
      margin-bottom: 30px;
      text-align: center;
      font-size: 2em;
    }
    .metric {
      background: #f8f9fa;
      padding: 25px;
      border-radius: 15px;
      margin-bottom: 20px;
      transition: transform 0.2s;
    }
    .metric:hover {
      transform: translateY(-2px);
    }
    .metric-label {
      color: #666;
      font-size: 0.9em;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }
    .metric-value {
      color: #333;
      font-size: 2.5em;
      font-weight: bold;
      font-variant-numeric: tabular-nums;
    }
    .distance-value {
      color: #667eea;
    }
    .metric-unit {
      color: #999;
      font-size: 0.6em;
      margin-left: 5px;
    }
    .status {
      text-align: center;
      padding: 15px;
      border-radius: 10px;
      margin-top: 20px;
      font-weight: 500;
    }
    .status.connected {
      background: #d4edda;
      color: #155724;
    }
    .status.disconnected {
      background: #f8d7da;
      color: #721c24;
    }
    .stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 15px;
      margin-top: 20px;
    }
    .stat {
      background: #e9ecef;
      padding: 15px;
      border-radius: 10px;
      text-align: center;
    }
    .stat-label {
      color: #666;
      font-size: 0.8em;
      margin-bottom: 5px;
    }
    .stat-value {
      color: #333;
      font-size: 1.5em;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📡 LoRa Distance Monitor</h1>
    
    <div class="metric">
      <div class="metric-label">Distance</div>
      <div class="metric-value distance-value">
        <span id="distance">--</span>
        <span class="metric-unit">m</span>
      </div>
    </div>
    
    <div class="stats">
      <div class="stat">
        <div class="stat-label">RSSI</div>
        <div class="stat-value"><span id="rssi">--</span> dBm</div>
      </div>
      <div class="stat">
        <div class="stat-label">SNR</div>
        <div class="stat-value"><span id="snr">--</span> dB</div>
      </div>
      <div class="stat">
        <div class="stat-label">Packets</div>
        <div class="stat-value" id="packets">0</div>
      </div>
      <div class="stat">
        <div class="stat-label">Last Update</div>
        <div class="stat-value" id="lastUpdate">--</div>
      </div>
    </div>
    
    <div id="status" class="status disconnected">
      Waiting for data...
    </div>
  </div>

  <script>
    function updateData() {
      fetch('/data')
        .then(response => response.json())
        .then(data => {
          document.getElementById('distance').textContent = data.distance.toFixed(1);
          document.getElementById('rssi').textContent = data.rssi;
          document.getElementById('snr').textContent = data.snr.toFixed(1);
          document.getElementById('packets').textContent = data.packets;
          
          const now = new Date();
          document.getElementById('lastUpdate').textContent = 
            now.getHours().toString().padStart(2, '0') + ':' + 
            now.getMinutes().toString().padStart(2, '0') + ':' + 
            now.getSeconds().toString().padStart(2, '0');
          
          const status = document.getElementById('status');
          if (data.distance > 0) {
            status.textContent = '✓ Receiving LoRa packets';
            status.className = 'status connected';
          } else {
            status.textContent = '⚠ No packets received';
            status.className = 'status disconnected';
          }
        })
        .catch(err => {
          console.error('Error fetching data:', err);
          document.getElementById('status').textContent = '✗ Connection error';
          document.getElementById('status').className = 'status disconnected';
        });
    }
    
    // Update every 500ms
    setInterval(updateData, 500);
    updateData();
  </script>
</body>
</html>
)=====";
  
  server.send(200, "text/html", html);
}

void handleData() {
  String json = "{";
  json += "\"distance\":" + String(estimatedDistance, 1) + ",";
  json += "\"rssi\":" + String(rssi) + ",";
  json += "\"snr\":" + String(snr, 1) + ",";
  json += "\"packets\":" + String(packetCount);
  json += "}";
  
  server.send(200, "application/json", json);
}

void handleNotFound() {
  server.send(404, "text/plain", "404: Not found");
}

