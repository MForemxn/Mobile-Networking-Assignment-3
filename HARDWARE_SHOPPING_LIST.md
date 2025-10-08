# 🛒 C-V2X Demo Hardware Shopping List

## **Complete Kit for Emergency Vehicle Communication Demo**

Total Cost: **~$60-70** | Setup Time: **30 minutes**

---

## 📦 **Required Components**

### **1. Emergency Vehicle Transmitter**

#### **Arduino Board** (Choose ONE)
```
✅ RECOMMENDED: Arduino Nano
   Price: $8-12
   Amazon: Search "Arduino Nano ATmega328P"
   Why: Small, cheap, perfect for this project
   
   Alternative: Arduino Uno
   Price: $15-20
   Amazon: Search "Arduino Uno R3"
   Why: More pins, easier to work with for beginners
```

#### **LoRa Module for Transmitter**
```
✅ REQUIRED: RFM95W LoRa Module
   Price: $8-15
   Frequency: 915 MHz (US/Canada/Australia)
            OR 868 MHz (Europe)
   
   Amazon Search: "RFM95W 915MHz LoRa module Arduino"
   Key features:
   - Works with 3.3V (important!)
   - Long range (2+ km)
   - Low power
   - SPI interface
   
   ⚠️ IMPORTANT: Check your region's frequency!
   - US/Canada/Australia: 915 MHz
   - Europe/UK: 868 MHz
   - Asia: Check local regulations
```

#### **Button & Miscellaneous**
```
Push Button (Momentary Switch)
   Price: $2-5 for pack of 10
   Amazon: Search "momentary push button arduino"
   
Jumper Wires (Male-to-Male and Male-to-Female)
   Price: $5-8
   Amazon: Search "dupont jumper wire kit"
   
Breadboard (optional, makes prototyping easier)
   Price: $5-8
   Amazon: Search "breadboard 830 points"
```

**Subtotal for Transmitter: ~$25-35**

---

### **2. LoRa Gateway (Roadside Unit)**

#### **OPTION A: TTGO LoRa32 V2 (HIGHLY RECOMMENDED)**
```
✅ BEST CHOICE: TTGO LoRa32 V2.1 1.6
   Price: $25-30
   Amazon: Search "TTGO LoRa32 V2 ESP32"
   AliExpress: $18-22 (slower shipping)
   
   What you get ALL-IN-ONE:
   - ESP32 (WiFi + Bluetooth)
   - LoRa SX1276 radio built-in
   - OLED display (shows status!)
   - USB-C or Micro-USB
   - Battery connector
   - NO WIRING NEEDED! 🎉
   
   This is the easiest option - everything in one board!
```

#### **OPTION B: DIY ESP32 + LoRa Module**
```
If TTGO is out of stock:

ESP32 DevKit
   Price: $8-12
   Amazon: Search "ESP32 DevKit V1"
   
RFM95W LoRa Module (same as transmitter)
   Price: $8-15
   
Wiring required, but more flexible
```

**Subtotal for Gateway: ~$25-30 (TTGO) or ~$18-25 (DIY)**

---

## 📋 **Complete Shopping List**

### **Minimum Working Demo:**
```
Quantity | Item                          | Price    | Link/Search Term
---------|-------------------------------|----------|------------------
1x       | Arduino Nano                  | $10      | "Arduino Nano ATmega328P"
1x       | RFM95W LoRa 915MHz           | $12      | "RFM95W 915MHz LoRa Arduino"
1x       | TTGO LoRa32 V2               | $28      | "TTGO LoRa32 V2 ESP32"
1x       | Push Button                   | $3       | "momentary push button"
1x       | Jumper Wire Kit               | $6       | "dupont jumper wire kit"
---------|-------------------------------|----------|------------------
TOTAL:                                    $59

Ships in 2-3 days with Amazon Prime!
```

### **Recommended Complete Kit:**
```
Add these for better experience:

1x       | Breadboard                    | $6       | "breadboard 830 points"
1x       | USB Cables (if needed)        | $5-10    | "micro USB cable" / "USB-C cable"
1x       | Project Box (optional)        | $8-12    | "project enclosure box"
---------|-------------------------------|----------|------------------
TOTAL WITH EXTRAS:                        $78-87
```

---

## 🛍️ **Where to Buy**

### **Fast Shipping (2-3 days):**
1. **Amazon** - Prime shipping, easy returns
   - Search terms above
   - Filter by "Prime" for fast delivery
   
2. **Adafruit** - High quality, US-based
   - https://www.adafruit.com
   - Educational discount available
   
3. **SparkFun** - Excellent tutorials included
   - https://www.sparkfun.com
   - Good for beginners

### **Budget Options (1-3 weeks):**
1. **AliExpress** - Cheapest prices
   - TTGO: $18-22
   - Arduino clones: $3-5
   - Total kit: ~$35-40
   
2. **eBay** - Hit or miss on quality
   - Sometimes has local sellers

---

## 🔧 **What's NOT Needed**

You DON'T need:
- ❌ Soldering iron (use jumper wires)
- ❌ Special tools
- ❌ Additional sensors
- ❌ Antenna (modules come with antenna or U.FL connector)
- ❌ Power supply (USB powers everything)

---

## 📦 **Recommended Buying Strategy**

### **Option 1: "I need it this weekend"**
```
Day 1 (Today):
- Order on Amazon Prime
- Get Arduino Nano, RFM95W, TTGO, button, wires
- Pay ~$10 extra for Prime, but get it in 2 days

Day 2-3:
- Components arrive
- Start building

Total: ~$70, arrives in 2-3 days
```

### **Option 2: "I have 2-3 weeks"**
```
Week 1:
- Order on AliExpress
- Pay ~$40 total for complete kit
- Free shipping

Week 2-3:
- Components arrive
- Test and build

Total: ~$40, arrives in 2-3 weeks
```

### **Option 3: "Local electronics store"**
```
Check for:
- Micro Center (US)
- Frys Electronics (US)  
- Maplin (UK)
- Jaycar (Australia)

Pros: Get it today!
Cons: Usually more expensive ($80-100 total)
```

---

## 🎯 **Exact Amazon Links Template**

Search these exact terms on Amazon:

### **For US (915 MHz):**
```
1. "Arduino Nano ATmega328P USB CH340"
2. "RFM95W 915MHz LoRa module SPI"
3. "TTGO LoRa32 V2.1 915MHz ESP32"
4. "momentary push button switch arduino"
5. "dupont jumper wire kit 120pcs"
```

### **For Europe (868 MHz):**
```
1. "Arduino Nano ATmega328P USB CH340"
2. "RFM95W 868MHz LoRa module SPI"
3. "TTGO LoRa32 V2.1 868MHz ESP32"
4. "momentary push button switch arduino"
5. "dupont jumper wire kit 120pcs"
```

---

## ⚠️ **Important Notes**

### **Frequency Regulations:**
```
✅ Legal frequencies by region:
   US/Canada/Australia: 915 MHz (ISM band)
   Europe: 868 MHz (SRD band)
   Asia: Varies by country (often 433 MHz or 920-925 MHz)

⚠️ Double-check your country's regulations!
   Using wrong frequency can violate radio regulations.
```

### **Power Requirements:**
```
LoRa modules: 3.3V ONLY!
   ❌ Connecting to 5V will damage the module
   ✅ Arduino has 3.3V pin - use this
   ✅ TTGO is all 3.3V - no worries

Power consumption:
   - Arduino: ~20mA
   - LoRa RX: ~12mA
   - LoRa TX: ~120mA (brief pulses)
   - USB power is plenty!
```

---

## 📊 **Price Comparison**

| Component          | Amazon Prime | AliExpress | Adafruit |
|--------------------|--------------|------------|----------|
| Arduino Nano       | $10          | $3         | $15      |
| RFM95W LoRa        | $12          | $6         | $20      |
| TTGO LoRa32        | $28          | $18        | $35      |
| Accessories        | $10          | $5         | $15      |
| **TOTAL**          | **$60**      | **$32**    | **$85**  |
| **Shipping**       | Free (Prime) | Free       | $8-15    |
| **Arrives**        | 2-3 days     | 2-3 weeks  | 3-5 days |

---

## 🎒 **What Should Arrive in Your Package**

When you receive your order, verify you have:

### **Transmitter Kit:**
- [ ] 1x Arduino Nano or Uno with USB cable
- [ ] 1x RFM95W LoRa module with antenna
- [ ] 1x Push button
- [ ] 10-20x Jumper wires (mix of M-M and M-F)

### **Gateway Kit:**
- [ ] 1x TTGO LoRa32 V2 with antenna and USB cable
  OR
- [ ] 1x ESP32 DevKit + 1x RFM95W LoRa module

### **Check the Antennas!**
Most LoRa modules come with either:
- Spring antenna (already attached) ✅
- U.FL connector antenna (needs to be connected) ⚠️

**NEVER power on LoRa without antenna connected!**

---

## 🚀 **After Ordering**

While waiting for delivery:

1. **Install Software:**
   - Arduino IDE: https://www.arduino.cc/en/software
   - ESP32 board support
   - LoRa library
   - WebSockets library

2. **Read Documentation:**
   - CV2X_LORA_IMPLEMENTATION.md
   - Study the code
   - Plan your demo

3. **Test Setup:**
   - Make sure laptop/WiFi is ready
   - Test the web server
   - Verify students can connect

---

## 💡 **Money-Saving Tips**

1. **Arduino Nano clones work fine!**
   - $3-5 on AliExpress
   - Functionally identical to official

2. **Buy starter kits:**
   - Often include jumper wires, buttons, breadboard
   - Can be cheaper than buying separately

3. **Check for bundles:**
   - Some sellers offer "Arduino + LoRa" kits
   - Can save $5-10

4. **Student discounts:**
   - Adafruit: 10% off with .edu email
   - SparkFun: Educational pricing

---

## 🎓 **For Your Professor/Budget Request**

If requesting funding, use this description:

```
Purpose: Hardware for C-V2X Vehicle Communication Demonstration

Items Required:
- Microcontrollers and radio modules to demonstrate 
  Cellular Vehicle-to-Everything (C-V2X) emergency 
  vehicle preemption
- Simulates technology being deployed in production 
  vehicles by major automakers (GM, Ford, VW)
- Educational demonstration of mobile networking 
  principles

Total Cost: $60-70
Vendors: Amazon (fast delivery), Adafruit (educational)
Justification: Hands-on demonstration of real-world 
               vehicle safety communication protocols
```

---

## ✅ **Quick Start Checklist**

- [ ] Determined my region's frequency (915 or 868 MHz)
- [ ] Ordered Arduino Nano
- [ ] Ordered matching LoRa modules (915 or 868 MHz)
- [ ] Ordered TTGO LoRa32 (same frequency!)
- [ ] Ordered button and wires
- [ ] Installed Arduino IDE
- [ ] Read CV2X_LORA_IMPLEMENTATION.md
- [ ] Waiting for delivery! 📦

---

**Estimated Total Time Investment:**
- Shopping: 20 minutes
- Waiting for delivery: 2-3 days (Prime) or 2-3 weeks (AliExpress)
- Assembly: 30 minutes
- Code upload: 15 minutes
- Testing: 30 minutes
- **TOTAL: Ready to demo in 3 days!**

---

**Questions? Check the troubleshooting section in CV2X_LORA_IMPLEMENTATION.md**

🚗💨 Let's build this thing! 🚨

