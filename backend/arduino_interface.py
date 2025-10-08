#!/usr/bin/env python3
"""
LoRa Receiver Interface for Emergency Detection
Reads serial input from ESP32/Arduino LoRa receiver
Triggers emergency takeover when LoRa signal detected
"""

import asyncio
import serial
import serial.tools.list_ports
import logging

logger = logging.getLogger(__name__)

class ArduinoInterface:
    """Interface for LoRa receiver via serial communication."""
    
    def __init__(self, server, baudrate=115200):  # ESP32 uses 115200
        self.server = server
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
        self.emergency_active = False
        
    def find_arduino_port(self):
        """Auto-detect LoRa receiver serial port."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Check for ESP32, Arduino, or common USB identifiers
            if any(x in port.description for x in ['CP2102', 'CP2104', 'CH340', 'Arduino', 'USB', 'UART', 'ESP32']):
                logger.info(f"Found device on port: {port.device} ({port.description})")
                return port.device
        return None
    
    async def connect(self, port=None):
        """Connect to LoRa receiver via serial."""
        try:
            if port is None:
                port = self.find_arduino_port()
            
            if port is None:
                logger.warning("⚠️  No LoRa receiver found. System will work without RF demo.")
                logger.warning("   Connect ESP32 receiver via USB for full C-V2X demo")
                return False
            
            self.serial_conn = serial.Serial(port, self.baudrate, timeout=1)
            await asyncio.sleep(2)  # Wait for ESP32/Arduino to reset
            logger.info(f"📡 Connected to LoRa receiver on {port}")
            self.server.arduino_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to receiver: {e}")
            return False
    
    async def read_loop(self):
        """Continuously read from LoRa receiver and trigger emergency signals."""
        self.running = True
        logger.info("📡 Starting LoRa receiver monitor...")
        logger.info("   Waiting for RF emergency broadcasts...\n")
        
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    
                    # Log all serial output for debugging
                    if line and not line.startswith("Message:") and not line.startswith("RSSI"):
                        logger.debug(f"Serial: {line}")
                    
                    if line == "EMERGENCY_DETECTED":
                        if not self.emergency_active:
                            self.emergency_active = True
                            logger.info("╔═══════════════════════════════════════════╗")
                            logger.info("║  🚨 RF EMERGENCY DETECTED VIA LORA! 🚨   ║")
                            logger.info("╚═══════════════════════════════════════════╝")
                            logger.info("📡 LoRa receiver confirmed RF signal reception")
                            logger.info("🎮 Initiating emergency takeover mode...")
                            await self.server.trigger_lora_emergency()
                        
                    elif line == "EMERGENCY_CLEAR":
                        if self.emergency_active:
                            self.emergency_active = False
                            logger.info("╔═══════════════════════════════════════════╗")
                            logger.info("║  🟢 EMERGENCY CLEARED VIA LORA 🟢        ║")
                            logger.info("╚═══════════════════════════════════════════╝")
                            logger.info("📡 LoRa receiver confirmed clear signal")
                            logger.info("🎮 Returning control to students...\n")
                            await self.server.clear_lora_emergency()
                    
                    elif line == "RECEIVER_READY":
                        logger.info("✅ LoRa receiver initialized and ready!")
                        
                await asyncio.sleep(0.05)  # 50ms poll rate
                
            except Exception as e:
                logger.error(f"Error reading from receiver: {e}")
                await asyncio.sleep(1)
    
    def stop(self):
        """Stop the Arduino interface."""
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
            logger.info("Arduino connection closed")

