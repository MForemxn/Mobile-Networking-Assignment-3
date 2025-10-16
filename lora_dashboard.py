#!/usr/bin/env python3
"""
LoRa Distance Dashboard
Reads serial data from Wio-SX1262 and displays in web browser
"""

import serial
import serial.tools.list_ports
import json
import time
from flask import Flask, render_template_string, jsonify
from threading import Thread, Lock
import sys

app = Flask(__name__)

# Global data storage
current_data = {
    'distance': 0,
    'rssi': 0,
    'snr': 0,
    'packets': 0,
    'message': '',
    'connected': False,
    'timestamp': 0,
    'status': 'Disconnected'
}
data_lock = Lock()

# Serial connection
ser = None

HTML_TEMPLATE = """
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
            max-width: 700px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 0.9em;
        }
        .metric {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            transition: transform 0.2s;
            color: white;
        }
        .metric:hover {
            transform: translateY(-2px);
        }
        .metric-label {
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        .metric-value {
            font-size: 3.5em;
            font-weight: bold;
            font-variant-numeric: tabular-nums;
        }
        .metric-unit {
            font-size: 0.5em;
            margin-left: 5px;
            opacity: 0.8;
        }
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            transition: transform 0.2s;
        }
        .stat:hover {
            transform: translateY(-2px);
            background: #e9ecef;
        }
        .stat-label {
            color: #666;
            font-size: 0.85em;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-value {
            color: #333;
            font-size: 2em;
            font-weight: bold;
            font-variant-numeric: tabular-nums;
        }
        .message-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-family: 'Courier New', monospace;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        .status {
            text-align: center;
            padding: 15px;
            border-radius: 10px;
            font-weight: 500;
            font-size: 1em;
        }
        .status.connected {
            background: #d4edda;
            color: #155724;
        }
        .status.disconnected {
            background: #f8d7da;
            color: #721c24;
        }
        .pulse {
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #999;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 LoRa Distance</h1>
        <div class="subtitle">Real-time monitoring via Serial</div>
        
        <div class="metric">
            <div class="metric-label">Distance</div>
            <div class="metric-value">
                <span id="distance">--</span>
                <span class="metric-unit">meters</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-label">RSSI</div>
                <div class="stat-value"><span id="rssi">--</span> <span style="font-size: 0.5em;">dBm</span></div>
            </div>
            <div class="stat">
                <div class="stat-label">SNR</div>
                <div class="stat-value"><span id="snr">--</span> <span style="font-size: 0.5em;">dB</span></div>
            </div>
            <div class="stat">
                <div class="stat-label">Packets</div>
                <div class="stat-value" id="packets">0</div>
            </div>
            <div class="stat">
                <div class="stat-label">Last Update</div>
                <div class="stat-value" id="lastUpdate" style="font-size: 1.3em;">--</div>
            </div>
        </div>
        
        <div class="message-box">
            <strong>Last Message:</strong> <span id="message">--</span>
        </div>
        
        <div id="status" class="status disconnected">
            Waiting for data...
        </div>
        
        <div class="footer">
            Wio-SX1262 + XIAO ESP32S3
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
                    document.getElementById('message').textContent = data.message || '--';
                    
                    const now = new Date();
                    document.getElementById('lastUpdate').textContent = 
                        now.getHours().toString().padStart(2, '0') + ':' + 
                        now.getMinutes().toString().padStart(2, '0') + ':' + 
                        now.getSeconds().toString().padStart(2, '0');
                    
                    const status = document.getElementById('status');
                    if (data.connected && data.distance > 0) {
                        status.textContent = '✓ ' + data.status;
                        status.className = 'status connected';
                    } else {
                        status.textContent = '⚠ ' + data.status;
                        status.className = 'status disconnected';
                    }
                })
                .catch(err => {
                    console.error('Error fetching data:', err);
                    document.getElementById('status').textContent = '✗ Dashboard connection error';
                    document.getElementById('status').className = 'status disconnected';
                });
        }
        
        // Update every 500ms
        setInterval(updateData, 500);
        updateData();
    </script>
</body>
</html>
"""

def find_serial_port():
    """Find the XIAO ESP32S3 serial port automatically"""
    ports = serial.tools.list_ports.comports()
    
    # Common identifiers for ESP32 and XIAO boards
    esp32_keywords = ['usb', 'serial', 'uart', 'ch340', 'cp210', 'esp32', 'xiao']
    
    print("Available serial ports:")
    for port in ports:
        print(f"  {port.device}: {port.description}")
        # Check if port matches known ESP32/XIAO identifiers
        port_str = (port.device + port.description).lower()
        if any(keyword in port_str for keyword in esp32_keywords):
            print(f"  → Looks like an ESP32! Using {port.device}")
            return port.device
    
    if ports:
        print(f"\nNo ESP32 detected, using first available port: {ports[0].device}")
        return ports[0].device
    
    return None

def read_serial():
    """Read serial data in background thread"""
    global ser, current_data
    
    while True:
        try:
            if ser and ser.is_open:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8').strip()
                    
                    # Try to parse JSON
                    try:
                        data = json.loads(line)
                        
                        with data_lock:
                            if data.get('type') == 'data':
                                current_data['distance'] = data.get('distance', 0)
                                current_data['rssi'] = data.get('rssi', 0)
                                current_data['snr'] = data.get('snr', 0)
                                current_data['packets'] = data.get('packets', 0)
                                current_data['message'] = data.get('message', '')
                                current_data['connected'] = data.get('connected', False)
                                current_data['timestamp'] = data.get('timestamp', 0)
                                current_data['status'] = 'Receiving LoRa packets'
                            elif 'status' in data:
                                current_data['status'] = data.get('message', data['status'])
                                print(f"Status: {current_data['status']}")
                    except json.JSONDecodeError:
                        # Not JSON, just print it
                        if line:
                            print(f"Serial: {line}")
            else:
                time.sleep(1)
        except Exception as e:
            print(f"Serial read error: {e}")
            time.sleep(1)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/data')
def data():
    with data_lock:
        return jsonify(current_data)

def main():
    global ser
    
    print("=" * 60)
    print("LoRa Distance Dashboard")
    print("=" * 60)
    
    # Find serial port
    port = find_serial_port()
    
    if not port:
        print("\n❌ No serial ports found!")
        print("Make sure your Wio-SX1262 + XIAO ESP32S3 is connected via USB")
        sys.exit(1)
    
    # Open serial connection
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print(f"\n✓ Connected to {port} at 115200 baud")
        time.sleep(2)  # Wait for Arduino to reset
    except Exception as e:
        print(f"\n❌ Failed to open serial port: {e}")
        sys.exit(1)
    
    # Start serial reading thread
    serial_thread = Thread(target=read_serial, daemon=True)
    serial_thread.start()
    print("✓ Serial reader started")
    
    # Start Flask server
    print("\n" + "=" * 60)
    print("Dashboard is running!")
    print("Open your browser to: http://localhost:5000")
    print("=" * 60)
    print("\nPress Ctrl+C to exit\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        if ser:
            ser.close()
        sys.exit(0)

if __name__ == '__main__':
    main()

