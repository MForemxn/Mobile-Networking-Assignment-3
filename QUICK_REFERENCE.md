# ⚡ Quick Reference Card - C-V2X Demo

## **🧪 TEST RIGHT NOW (Without Hardware)**

```bash
# Terminal 1 - Backend
cd backend && python3 main.py

# Terminal 2 - Frontend
cd frontend && npm start

# Terminal 3 - Simulator
python3 test_emergency_simulator.py

# Browser - Open 3 tabs
http://localhost:3000

# Test
Press 'E' → All tabs lock
Press 'C' → All tabs unlock
```

**✅ Works?** You're ready for hardware!

---

## 🛒 **Shopping List**

```
Amazon Search Terms:
1. "RFM95W 915MHz LoRa Arduino"    $12
2. "Arduino Nano ATmega328P"       $10
3. "TTGO LoRa32 V2 ESP32 OLED"    $28
4. "Push button momentary"         $3
5. "Dupont jumper wires"           $6
                          TOTAL:   $59
```

---

## 📡 **Arduino Sketches**

```
Transmitter: arduino_cv2x_emergency.ino
→ Upload to Arduino Nano
→ Wiring in CV2X_LORA_IMPLEMENTATION.md

Receiver: esp32_receiver_with_led.ino
→ Upload to TTGO LoRa32
→ LED on GPIO 25
→ USB to computer
```

---

## 🎯 **Demo Modes**

```
Highway:      http://YOUR_IP:3000
Traffic Grid: http://YOUR_IP:3000?mode=traffic
```

---

## 🎬 **Demo Flow**

```
1. Students join URL
2. Drive vehicles (30 sec)
3. Show transmitter/receiver
4. Press button
5. LED lights (PROOF!)
6. Controls lock
7. Vehicles move right
8. Press again
9. Controls unlock
10. Switch to traffic mode
11. Press button
12. Green wave!
```

---

## 🐛 **Quick Fixes**

```
Issue: Students can't connect
Fix: Same WiFi + correct IP

Issue: LED doesn't light
Fix: Check antennas + frequency match

Issue: Controls don't lock
Fix: Check simulator works first
```

---

## 📞 **Files You Need**

```
Setup: START_HERE.md
Buy: BUY_THESE_NOW.md
Test: TEST_WITHOUT_HARDWARE.md
Present: REFINED_DEMO_GUIDE.md
```

---

**🚀 GO BUILD IT!**

