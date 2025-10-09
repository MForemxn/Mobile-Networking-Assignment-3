#!/usr/bin/env python3
"""
Emergency Simulator - Test Your Demo Without Arduino Hardware

This script simulates the LoRa receiver sending emergency signals
to test the entire system before hardware arrives.

Usage:
1. Start backend server: python3 backend/main.py
2. Start frontend: npm start (in frontend/)
3. Run this script: python3 test_emergency_simulator.py
4. Press 'e' to trigger emergency, 'c' to clear, 'q' to quit

This simulates what the ESP32 receiver would send via serial.
"""

import asyncio
import websockets
import json
import sys
import termios
import tty
import threading

class EmergencySimulator:
    def __init__(self, server_url='ws://localhost:8765'):
        self.server_url = server_url
        self.websocket = None
        self.emergency_active = False
        self.connected = False
        
    async def connect(self):
        """Connect to WebSocket server."""
        try:
            print(f"🔌 Connecting to server: {self.server_url}")
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            print("✅ Connected to server!\n")
            
            # Wait for welcome message
            welcome = await self.websocket.recv()
            data = json.loads(welcome)
            print(f"📨 Received: {data.get('type')}")
            print(f"   Device ID: {data.get('device_id')}\n")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("   Make sure backend server is running!")
            sys.exit(1)
    
    async def trigger_emergency(self):
        """Simulate emergency button press."""
        if not self.emergency_active:
            self.emergency_active = True
            
            print("\n╔═══════════════════════════════════════════╗")
            print("║  🚨 SIMULATING LORA EMERGENCY! 🚨        ║")
            print("╚═══════════════════════════════════════════╝")
            print("📡 Sending emergency_takeover to all clients...")
            
            message = {
                'type': 'register_emergency',
                'device_id': 'SIMULATED_LORA',
                'source': 'cv2x_lora',
                'rssi': -45,
                'snr': 8.5
            }
            
            try:
                await asyncio.wait_for(
                    self.websocket.send(json.dumps(message)),
                    timeout=2.0
                )
                print("✅ Emergency signal sent!")
                print("   Check student devices - controls should LOCK\n")
            except asyncio.TimeoutError:
                print("❌ Timeout sending emergency signal!")
                print("   Check if backend is running\n")
            except Exception as e:
                print(f"❌ Error sending: {e}\n")
    
    async def clear_emergency(self):
        """Simulate emergency clear."""
        if self.emergency_active:
            self.emergency_active = False
            
            print("\n╔═══════════════════════════════════════════╗")
            print("║  🟢 CLEARING EMERGENCY 🟢                ║")
            print("╚═══════════════════════════════════════════╝")
            print("📡 Sending clear signal to all clients...")
            
            message = {
                'type': 'clear_emergency',
                'device_id': 'SIMULATED_LORA',
                'source': 'cv2x_lora'
            }
            
            try:
                await asyncio.wait_for(
                    self.websocket.send(json.dumps(message)),
                    timeout=2.0
                )
                print("✅ Clear signal sent!")
                print("   Check student devices - controls should UNLOCK\n")
            except asyncio.TimeoutError:
                print("❌ Timeout sending clear signal!")
                print("   Check if backend is running\n")
            except Exception as e:
                print(f"❌ Error sending: {e}\n")
    
    async def run(self):
        """Main loop."""
        await self.connect()
        
        print("╔════════════════════════════════════════════╗")
        print("║   Emergency Simulator - Test Mode         ║")
        print("╚════════════════════════════════════════════╝")
        print()
        print("Commands:")
        print("  [E] - Trigger Emergency (locks student controls)")
        print("  [C] - Clear Emergency (unlocks student controls)")
        print("  [Q] - Quit")
        print()
        print("Instructions:")
        print("1. Open http://localhost:3000 in multiple browser tabs")
        print("2. Press 'E' to test emergency takeover")
        print("3. Watch all tabs - controls should lock!")
        print("4. Press 'C' to return control")
        print()
        print("Ready! Press a key...\n")
        
        # Start keyboard listener in background
        self.loop = asyncio.get_event_loop()
        self.loop.run_in_executor(None, self.keyboard_listener)
        
        # Keep connection alive
        try:
            while self.connected:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n🛑 Simulator stopped")
    
    def keyboard_listener(self):
        """Listen for keyboard input."""
        # Get terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            tty.setcbreak(sys.stdin.fileno())
            
            while self.connected:
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1).lower()
                    
                    if key == 'e':
                        asyncio.run_coroutine_threadsafe(
                            self.trigger_emergency(),
                            self.loop
                        )
                    elif key == 'c':
                        asyncio.run_coroutine_threadsafe(
                            self.clear_emergency(),
                            self.loop
                        )
                    elif key == 'q':
                        print("\n👋 Quitting...")
                        self.connected = False
                        break
                        
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

# For systems without termios (Windows), use simple input
def simple_keyboard_interface(simulator):
    """Simplified keyboard input for Windows/systems without termios."""
    print("\n⚠️  Advanced keyboard mode not available")
    print("Using simple input mode instead.\n")
    
    while True:
        try:
            cmd = input("Enter command [e/c/q]: ").lower().strip()
            
            if cmd == 'e':
                asyncio.run(simulator.trigger_emergency())
            elif cmd == 'c':
                asyncio.run(simulator.clear_emergency())
            elif cmd == 'q':
                print("👋 Quitting...")
                break
            else:
                print("Invalid command. Use: e (emergency), c (clear), q (quit)")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped")
            break

if __name__ == '__main__':
    print("\n🧪 Emergency System Simulator")
    print("Testing C-V2X demo without Arduino hardware\n")
    
    simulator = EmergencySimulator()
    
    # Check if termios available (Unix/Mac/Linux)
    try:
        import select
        # Unix-based keyboard interface
        asyncio.run(simulator.run())
    except (ImportError, AttributeError):
        # Windows or no termios - use simple mode
        asyncio.run(simulator.connect())
        simple_keyboard_interface(simulator)

