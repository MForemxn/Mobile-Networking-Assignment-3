# Wio-SX1262 + XIAO ESP32S3 Setup Guide

## Hardware Overview

**Wio-SX1262**: LoRa module with SX1262 chip
**XIAO ESP32S3**: Tiny ESP32-S3 board with WiFi/BLE

The Wio-SX1262 is designed to plug directly onto the XIAO ESP32S3 - no wiring needed!

## Pinout Reference

### Automatic Connections (when Wio is mounted on XIAO)

```
SX1262 LoRa Module Pins:
┌─────────────────────────────┐
│  MOSI  → D10 (GPIO 9)       │
│  MISO  → D9  (GPIO 8)       │
│  SCK   → D8  (GPIO 7)       │
│  CS    → D3  (GPIO 5)       │
│  RST   → D2  (GPIO 4)       │
│  DIO1  → D1  (GPIO 3)       │
│  BUSY  → D0  (GPIO 2)       │
└─────────────────────────────┘
```

### XIAO ESP32S3 Full Pinout

```
                  USB-C
     ┌────────────────────────────┐
     │    XIAO ESP32S3            │
     │                            │
D0 ──┤ GPIO2  (BUSY)    5V    ├── 5V
D1 ──┤ GPIO3  (DIO1)    GND   ├── GND
D2 ──┤ GPIO4  (RST)     3V3   ├── 3.3V
D3 ──┤ GPIO5  (CS)      GPIO10├── D10 (MOSI)
D4 ──┤ GPIO6            GPIO9 ├── D9  (MISO)
D5 ──┤ GPIO7  (SCK)     GPIO8 ├── D8
D6 ──┤ GPIO43           GPIO7 ├── D7
     └────────────────────────────┘
```

## Installation Steps

### 1. Install Arduino IDE
Download from: https://www.arduino.cc/en/software

### 2. Add ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to **Tools → Board → Boards Manager**
5. Search for "esp32" by Espressif Systems
6. Install version 2.0.11 or newer

### 3. Install Required Libraries

Go to **Sketch → Include Library → Manage Libraries** and install:

- **RadioLib** by Jan Gromeš (latest version)
  - This handles the SX1262 LoRa module

That's it! WiFi and WebServer libraries are built-in.

### 4. Configure Board Settings

1. **Tools → Board** → Select **XIAO_ESP32S3**
   - If you don't see it, select **ESP32S3 Dev Module**
2. **Tools → Port** → Select your device's port
   - macOS: `/dev/cu.usbmodem*`
   - Windows: `COM*`
   - Linux: `/dev/ttyUSB*` or `/dev/ttyACM*`

### 5. Install Python Dashboard Requirements

The dashboard runs on your laptop and reads serial data from the board.

```bash
pip3 install pyserial flask
```

### 6. Configure Code

**Important**: Change the frequency if you're in Europe:
```cpp
const float frequency = 868.0;  // EU frequency
```

### 7. Upload Receiver Code

1. Connect your Wio-SX1262 + XIAO ESP32S3 via USB-C
2. Open `wio_lora_distance.ino`
3. **Install ArduinoJson library** (Sketch → Include Library → Manage Libraries → search "ArduinoJson")
4. Click **Upload** (→ button)
5. Wait for compilation and upload

### 8. Run Dashboard

Keep the board connected via USB and run:

```bash
python3 lora_dashboard.py
```

The script will:
- Auto-detect your board's serial port
- Start reading data
- Launch web server at http://localhost:5000

Open your browser to `http://localhost:5000` to see the live dashboard!

### 9. Setup Transmitter (Required for Distance Measurement)

To actually measure distance, you need a second device transmitting:

1. Get another Wio-SX1262 + XIAO ESP32S3
2. Upload `wio_lora_transmitter.ino` to it
3. Power it with USB power bank or battery
4. Move it around to see distance change!

## Troubleshooting

### Arduino Issues

**"Board not found" or Upload Fails**

1. **Enter bootloader mode**:
   - Hold **BOOT** button on XIAO
   - Press and release **RESET** button
   - Release **BOOT** button
   - Try uploading again

**"Port not found"**

macOS may need CH340 drivers for some XIAO boards:
```bash
brew tap homebrew/cask-drivers
brew install homebrew/cask-drivers/wch-ch34x-usb-serial-driver
```

**ArduinoJson compilation error**

If you get errors about ArduinoJson, install it: **Sketch → Include Library → Manage Libraries → "ArduinoJson" by Benoit Blanchon**

### LoRa Issues

**Initialization Fails**

- Check the Wio module is fully seated on the XIAO
- Try different frequency: 915.0 (US) or 868.0 (EU)
- Check antenna is connected

**Dashboard Shows No Packets**

- Make sure transmitter is powered and running
- Check both devices use same frequency and LoRa parameters
- Try moving transmitter closer (<10m initially)
- Check antenna is connected on both devices

### Dashboard Issues

**Python script can't find serial port**

Run `python3 -m serial.tools.list_ports` to see available ports, then modify the script if needed.

**"Address already in use" error**

Port 5000 is taken. Change the port in `lora_dashboard.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
```

**No data appearing in dashboard**

1. Check Serial Monitor in Arduino IDE first - if it shows JSON data, the board is working
2. Close Arduino IDE Serial Monitor before running Python script (can't both read serial at once)
3. Try unplugging and replugging the USB cable

## Distance Calibration

The distance estimation uses RSSI (signal strength). For better accuracy:

1. Place transmitter at exactly 1 meter from receiver
2. Note the RSSI value in Serial Monitor
3. Update this line in `wio_lora_distance.ino`:
   ```cpp
   float measuredPower = -40; // Replace -40 with your RSSI at 1m
   ```

## Power Options

**USB-C**: 5V from computer or power adapter
**Battery**: Can use LiPo battery connected to XIAO's BAT pins
**Power Bank**: USB power bank for portable operation

## Bill of Materials

| Item | Quantity | Notes |
|------|----------|-------|
| Seeed Wio-SX1262 | 2 | LoRa module |
| Seeed XIAO ESP32S3 | 2 | MCU board |
| Antenna (868/915 MHz) | 2 | Usually included |
| USB-C Cable | 1-2 | For programming |
| USB Power Bank | 1 | For mobile transmitter |

**Total Cost**: ~$60-80 for complete setup

## Next Steps

- Adjust `pathLossExponent` for your environment (2.0 = free space, 4.0 = urban)
- Add more transmitters to track multiple objects
- Implement trilateration with 3+ receivers for 2D positioning
- Log distance data over time
- Add alerts when object is too close/far

