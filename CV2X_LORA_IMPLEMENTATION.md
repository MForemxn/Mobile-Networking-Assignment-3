# 🚗 C-V2X Demonstration Using LoRa Technology

## **Real-World Emergency Vehicle Communication Demo**

This implementation demonstrates **C-V2X (Cellular Vehicle-to-Everything)** principles using **LoRa (Long Range)** radio technology as a practical, affordable demonstration platform.

---

## 🎯 **What is C-V2X?**

**C-V2X** is the next-generation vehicle communication standard that enables:
- **Direct vehicle-to-vehicle (V2V)** communication without cellular towers
- **Vehicle-to-infrastructure (V2I)** for traffic lights, road signs
- **Vehicle-to-pedestrian (V2P)** for smartphone alerts
- **Vehicle-to-network (V2N)** for cloud services

### **Key Features:**
- Operates in 5.9 GHz ITS (Intelligent Transportation Systems) band
- Two modes: Direct (PC5) and Network (Uu via 4G/5G)
- Sub-20ms latency for safety applications
- 300-1000m range in urban environments
- Used by: GM, Ford, Volkswagen, BMW, Toyota

### **Use Cases:**
1. **Emergency Vehicle Preemption** ← Your demo!
2. Collision warning systems
3. Cooperative adaptive cruise control
4. Intersection safety alerts
5. Road hazard notifications

---

## 📡 **Why LoRa for This Demo?**

**LoRa** (Long Range) technology operates on similar principles to C-V2X's direct communication mode:

| Aspect | C-V2X Direct Mode | LoRa Demo | Why It Works |
|--------|-------------------|-----------|--------------|
| **Communication** | Direct device-to-device | Direct device-to-device | ✅ Same concept |
| **No Infrastructure** | Works without cellular | Works without WiFi/cellular | ✅ True P2P |
| **Broadcast** | One-to-many messages | One-to-many messages | ✅ Perfect match |
| **Range** | 300-1000m | 2000-5000m | ✅✅ Even better! |
| **Latency** | <20ms | ~50ms | ✅ Good enough for demo |
| **Power** | Low power | Ultra-low power | ✅ Battery friendly |
| **Cost** | $200-800/module | $15-30/module | 💰 Affordable! |
| **Arduino Compatible** | ❌ No | ✅ YES! | 🎉 Easy to build |

**Bottom Line:** LoRa demonstrates the **exact same communication pattern** as C-V2X at a fraction of the cost!

---

## 🛠️ **Hardware Requirements**

### **For Emergency Vehicle (Ambulance Simulator):**
```
1x Arduino Uno/Nano ($5-15)
1x LoRa SX1276/SX1278 Module ($8-15)
1x Push button
1x LED (optional, for feedback)
Total: ~$20
```

### **For Each Regular Vehicle (Optional - if you want physical receivers):**
```
1x ESP32 with built-in LoRa ($25)
OR
1x Arduino + LoRa module ($15)
1x LED to show emergency status
```

### **Recommended: RFM95W LoRa Module**
- Frequency: 915 MHz (US) or 868 MHz (EU)
- Range: 2+ km line-of-sight
- Power: 20 dBm max
- Arduino-compatible via SPI

---

## 📦 **Parts List**

### **Option 1: Budget Build (~$20)**
```
Amazon Search Terms:
- "RFM95W LoRa module Arduino" → $8-12
- "Arduino Nano" → $5-8
- "Push button momentary switch" → $3
```

### **Option 2: Pro Build with Display (~$30)**
```
- "TTGO LoRa32 V2" (ESP32 + LoRa + OLED) → $25-30
  Built-in display shows message transmission!
```

---

## 💻 **Arduino Code: Emergency Vehicle Transmitter**

### **Install Library:**
Arduino IDE → Tools → Manage Libraries → Search "LoRa" by Sandeep Mistry

### **Code:**

```cpp
/*
  C-V2X Emergency Vehicle Demonstration
  Using LoRa for Direct V2V Communication
  
  Simulates: Emergency vehicle broadcasting Basic Safety Message (BSM)
             with emergency status to all nearby vehicles
  
  Hardware:
  - Arduino Uno/Nano
  - LoRa SX1276/1278 Module (RFM95W)
  - Emergency button on pin 2
  - Status LED on pin 13
  
  Wiring (LoRa to Arduino):
  - VCC  → 3.3V (NOT 5V!)
  - GND  → GND
  - SCK  → Pin 13 (on Uno) or Pin D13
  - MISO → Pin 12 (on Uno) or Pin D12
  - MOSI → Pin 11 (on Uno) or Pin D11
  - NSS  → Pin 10 (on Uno) or Pin D10
  - RST  → Pin 9  (on Uno) or Pin D9
  - DIO0 → Pin 2  (on Uno) or Pin D2 (Different from button!)
  
  Note: Use button on different pin if DIO0 uses pin 2
*/

#include <SPI.h>
#include <LoRa.h>

// LoRa Configuration (matches C-V2X principles)
#define LORA_FREQUENCY    915E6  // 915 MHz (US) or 868E6 (EU)
#define LORA_TX_POWER     20     // 20 dBm max
#define LORA_SPREADING    7      // SF7 for low latency (like C-V2X)
#define LORA_BANDWIDTH    250E3  // 250 kHz bandwidth

// Pin Configuration
#define BUTTON_PIN        3      // Emergency button (changed from 2)
#define STATUS_LED        13     // Built-in LED
#define LORA_SS           10     // LoRa chip select
#define LORA_RST          9      // LoRa reset
#define LORA_DIO0         2      // LoRa interrupt (uses pin 2)

// Emergency State
bool emergencyActive = false;
unsigned long lastTransmission = 0;
const unsigned long TRANSMISSION_INTERVAL = 100; // Transmit every 100ms when active

// Vehicle ID (in real C-V2X, this would be unique vehicle identifier)
const String VEHICLE_ID = "EMG-001";

void setup() {
  Serial.begin(115200);
  while (!Serial);
  
  // Configure pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(STATUS_LED, OUTPUT);
  
  Serial.println("🚨 C-V2X Emergency Vehicle Simulator");
  Serial.println("Using LoRa for Direct V2V Communication");
  
  // Initialize LoRa
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("❌ LoRa initialization failed!");
    while (1) {
      digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
      delay(100);
    }
  }
  
  // Configure LoRa for low-latency (C-V2X-like)
  LoRa.setSpreadingFactor(LORA_SPREADING);
  LoRa.setSignalBandwidth(LORA_BANDWIDTH);
  LoRa.setTxPower(LORA_TX_POWER);
  LoRa.setCodingRate4(5); // 4/5 coding rate
  LoRa.enableCrc();
  
  Serial.println("✅ LoRa initialized successfully");
  Serial.println("📡 Frequency: " + String(LORA_FREQUENCY / 1e6) + " MHz");
  Serial.println("📶 TX Power: " + String(LORA_TX_POWER) + " dBm");
  Serial.println("⏱️  Spreading Factor: " + String(LORA_SPREADING));
  Serial.println("\n🚦 Press button to activate emergency mode");
}

void loop() {
  // Check button state
  static bool lastButtonState = HIGH;
  bool currentButtonState = digitalRead(BUTTON_PIN);
  
  if (lastButtonState == HIGH && currentButtonState == LOW) {
    // Button pressed
    delay(50); // Debounce
    if (digitalRead(BUTTON_PIN) == LOW) {
      toggleEmergency();
      while (digitalRead(BUTTON_PIN) == LOW); // Wait for release
      delay(50);
    }
  }
  lastButtonState = currentButtonState;
  
  // Transmit emergency messages periodically when active
  if (emergencyActive && (millis() - lastTransmission > TRANSMISSION_INTERVAL)) {
    transmitEmergencyBSM();
    lastTransmission = millis();
  }
  
  // Blink LED when emergency active
  if (emergencyActive) {
    static unsigned long lastBlink = 0;
    if (millis() - lastBlink > 250) {
      digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
      lastBlink = millis();
    }
  }
}

void toggleEmergency() {
  emergencyActive = !emergencyActive;
  
  if (emergencyActive) {
    Serial.println("\n🚨🚨🚨 EMERGENCY ACTIVATED 🚨🚨🚨");
    Serial.println("Broadcasting emergency status to all vehicles...");
    digitalWrite(STATUS_LED, HIGH);
    
    // Send immediate notification
    transmitEmergencyBSM();
  } else {
    Serial.println("\n🟢 Emergency cleared");
    digitalWrite(STATUS_LED, LOW);
    
    // Send clear message
    transmitClearMessage();
  }
}

void transmitEmergencyBSM() {
  /*
    Simulates C-V2X Basic Safety Message (BSM) with emergency flag
    
    Real BSM contains:
    - Vehicle ID
    - Position (GPS)
    - Speed
    - Heading
    - Acceleration
    - Emergency status
    
    Our demo version:
  */
  
  String message = "BSM|" + VEHICLE_ID + "|EMERGENCY|" + String(millis());
  
  LoRa.beginPacket();
  LoRa.print(message);
  LoRa.endPacket();
  
  Serial.print("📡 TX: ");
  Serial.println(message);
}

void transmitClearMessage() {
  String message = "BSM|" + VEHICLE_ID + "|CLEAR|" + String(millis());
  
  LoRa.beginPacket();
  LoRa.print(message);
  LoRa.endPacket();
  
  Serial.print("📡 TX: ");
  Serial.println(message);
}
```

---

## 🖥️ **Receiving End: Bridge to Web App**

Since student laptops don't have LoRa radios built-in, we'll use a **bridge device** that converts LoRa signals to WebSocket:

### **Option 1: ESP32 LoRa Gateway**

```cpp
/*
  LoRa to WebSocket Gateway
  Receives LoRa emergency broadcasts and forwards to web server
  
  Hardware: TTGO LoRa32 or ESP32 + LoRa module
*/

#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <WebSocketsClient.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";
const char* websocket_server = "192.168.1.100"; // Your server IP
const int websocket_port = 8765;

WebSocketsClient webSocket;

void setup() {
  Serial.begin(115200);
  
  // Initialize LoRa receiver
  if (!LoRa.begin(915E6)) {
    Serial.println("LoRa init failed!");
    while (1);
  }
  LoRa.setSpreadingFactor(7);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  
  // Connect to WebSocket server
  webSocket.begin(websocket_server, websocket_port, "/");
  webSocket.onEvent(webSocketEvent);
  
  Serial.println("LoRa→WebSocket Gateway Ready!");
}

void loop() {
  webSocket.loop();
  
  // Check for LoRa packets
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String message = "";
    while (LoRa.available()) {
      message += (char)LoRa.read();
    }
    
    Serial.print("LoRa RX: ");
    Serial.println(message);
    
    // Parse message: "BSM|EMG-001|EMERGENCY|12345"
    if (message.indexOf("EMERGENCY") >= 0) {
      // Forward to WebSocket as JSON
      String json = "{\"type\":\"register_emergency\",\"device_id\":\"LORA_VEHICLE\",\"source\":\"cv2x\"}";
      webSocket.sendTXT(json);
      Serial.println("Forwarded emergency to WebSocket");
    }
    else if (message.indexOf("CLEAR") >= 0) {
      String json = "{\"type\":\"clear_emergency\",\"device_id\":\"LORA_VEHICLE\",\"source\":\"cv2x\"}";
      webSocket.sendTXT(json);
      Serial.println("Forwarded clear to WebSocket");
    }
  }
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_CONNECTED) {
    Serial.println("WebSocket Connected!");
  }
}
```

---

## 🎭 **Demo Architecture**

```
[Emergency Vehicle]                     [Regular Vehicles - Student Devices]
    Arduino + LoRa                              Web Browsers
         │                                            ▲
         │                                            │
         │ LoRa Radio (2km range)                    │ WebSocket
         │ 915 MHz, SF7, 250kHz                      │
         │ Direct broadcast                          │
         │ No infrastructure!                        │
         ▼                                            │
    [LoRa Gateway]  ─────────────────────────────────┘
    ESP32 + LoRa                        WebSocket Server
    Receives LoRa                          Python Backend
    Forwards to WebSocket                  Port 8765
```

### **Why This is Realistic:**

1. **Direct Radio Comm** - Emergency vehicle broadcasts via LoRa (simulates C-V2X PC5)
2. **Roadside Unit (RSU)** - Gateway acts like RSU that bridges to infrastructure
3. **Vehicle OBU** - Each student device represents an On-Board Unit receiving via network
4. **Real-World Analog** - In reality, vehicles would have C-V2X radios, but many also use cellular fallback!

---

## 🎓 **Educational Value**

### **What This Demonstrates:**

1. **Direct V2V Communication**
   - No cellular towers needed
   - Real radio broadcasts
   - Long range (classroom + hallway)

2. **C-V2X Principles**
   - Basic Safety Messages (BSM)
   - Emergency vehicle preemption
   - Broadcast communication
   - Low latency critical messaging

3. **Hybrid Architecture**
   - Direct radio (LoRa/C-V2X)
   - Infrastructure bridge (RSU)
   - Network distribution (WebSocket)

4. **Real-World Parallel**
   ```
   Your Demo          Real C-V2X
   ─────────          ──────────
   LoRa radio    →    C-V2X radio (5.9 GHz)
   915 MHz       →    5.9 GHz ITS band
   Gateway       →    Roadside Unit (RSU)
   WebSocket     →    Cellular/Cloud backend
   Students      →    Vehicle OBUs
   ```

---

## 📊 **Performance Comparison**

| Metric | C-V2X Direct | Your LoRa Demo |
|--------|--------------|----------------|
| Range | 300-1000m | 2000+ m ✅ |
| Latency | <20ms | ~50ms ✅ |
| Bandwidth | 6-27 Mbps | ~27 kbps ⚠️ |
| Power | Low | Ultra-low ✅ |
| Cost | $200-800 | $20-30 ✅✅✅ |
| Arduino Compatible | ❌ | ✅✅✅ |

**For emergency alert demo:** Bandwidth doesn't matter (just sending "EMERGENCY" string), so LoRa is perfect!

---

## 🚀 **Demo Script**

### **Setup (Show to Class):**
1. Show emergency vehicle Arduino with LoRa antenna
2. Show gateway device receiving signals
3. Explain: "This simulates C-V2X, the technology that will be in all new cars by 2026"

### **Presentation:**

> "In a real deployment, emergency vehicles have C-V2X radios that broadcast directly to other vehicles within 300-1000 meters. Those vehicles respond immediately—no cell towers, no WiFi, just direct radio communication.
> 
> Today, I'm demonstrating this with LoRa radio, which works on the same principles as C-V2X's direct mode. When I press this button, the emergency vehicle broadcasts via radio..."

*PRESS BUTTON*

> "...the gateway receives it via LoRa—just like a roadside unit would receive C-V2X—and distributes it to all your devices. In a real scenario, your vehicles would have C-V2X radios and respond directly. This demonstrates the same coordination mechanism!"

### **Technical Deep Dive:**

> "C-V2X operates on two modes:
> 1. **PC5 (Direct)**: What we're simulating—vehicle-to-vehicle radio
> 2. **Uu (Network)**: Through 4G/5G towers for longer range
> 
> Major automakers like GM, Ford, and VW are deploying C-V2X now. By 2026, it's expected in most new vehicles. This demo shows how emergency preemption will work in that future."

---

## 💰 **Shopping List**

### **Minimum Working Demo:**
```
1x RFM95W LoRa Module                    $12
1x Arduino Nano                          $8
1x TTGO LoRa32 (ESP32+LoRa) for gateway  $28
1x Push button                           $2
Jumper wires                             $3
─────────────────────────────────────────────
Total:                                   ~$53
```

**Amazon Search Terms:**
- "RFM95W 915MHz LoRa module"
- "TTGO LoRa32 V2 ESP32"
- "Arduino Nano"

---

## 📚 **Presentation Slides Content**

### **Slide 1: What is C-V2X?**
- Cellular Vehicle-to-Everything
- Next-gen vehicle communication
- Direct + Network modes
- Used by major automakers

### **Slide 2: Technology Comparison**
| Feature | DSRC (Old) | C-V2X (New) |
|---------|------------|-------------|
| Range | 300m | 1000m ✅ |
| Penetration | Poor | Better ✅ |
| 5G Ready | No | Yes ✅ |
| Adoption | Limited | Growing ✅ |

### **Slide 3: Our Demo**
- Uses LoRa to simulate C-V2X
- Same principles, affordable hardware
- Demonstrates direct V2V communication
- Shows emergency vehicle coordination

---

## 🎯 **Expected Questions & Answers**

**Q: "Why not use actual C-V2X?"**  
A: "C-V2X modules cost $200-800 and require FCC certification for the 5.9 GHz band. LoRa operates in the unlicensed ISM band and demonstrates the same communication principles at 1/10th the cost."

**Q: "Can LoRa really compare to C-V2X?"**  
A: "For this demo, yes! LoRa actually has better range (2km+ vs 300-1000m) and similar latency for simple messages. C-V2X has much higher bandwidth for video/sensor data, but for emergency alerts, LoRa is perfect."

**Q: "Are real vehicles getting this?"**  
A: "Yes! GM committed to C-V2X in all new vehicles. Ford, VW, and Toyota are deploying it. The FCC allocated 5.9 GHz specifically for vehicle safety communications."

---

## 🏆 **Why This Approach Wins**

✅ **Authentic** - Uses real radio communication (not just WiFi)  
✅ **Educational** - Demonstrates actual V2V principles  
✅ **Affordable** - Under $60 total  
✅ **Scalable** - Can add multiple receivers  
✅ **Impressive** - Physical radio broadcasts! 📡  
✅ **Future-proof** - Based on technology being deployed NOW  

---

## 📖 **References**

- **C-V2X Overview**: https://www.5gaa.org/c-v2x-technology/
- **3GPP Specs**: Release 14 (LTE-V2X), Release 16 (5G-V2X)
- **LoRa Specs**: Semtech SX1276/78
- **FCC 5.9 GHz Band**: https://www.fcc.gov/5-9-ghz-band

---

**Bottom Line:** You're building a demo of the ACTUAL technology that will be in cars within 2-3 years, using hardware that's available and affordable today. This is production-level thinking! 🚀

