#!/usr/bin/env python3
"""
Arduino Interface for Emergency Button
Reads serial input from Arduino and triggers emergency signals
"""

import asyncio
import serial
import serial.tools.list_ports
import logging

logger = logging.getLogger(__name__)

class ArduinoInterface:
    """Interface for Arduino emergency button via serial communication."""
    
    def __init__(self, server, baudrate=9600):
        self.server = server
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
        
    def find_arduino_port(self):
        """Auto-detect Arduino serial port."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Check for common Arduino identifiers
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB' in port.description:
                logger.info(f"Found Arduino on port: {port.device}")
                return port.device
        return None
    
    async def connect(self, port=None):
        """Connect to Arduino via serial."""
        try:
            if port is None:
                port = self.find_arduino_port()
            
            if port is None:
                logger.warning("No Arduino found. Emergency button will not be available.")
                return False
            
            self.serial_conn = serial.Serial(port, self.baudrate, timeout=1)
            await asyncio.sleep(2)  # Wait for Arduino to reset
            logger.info(f"Connected to Arduino on {port}")
            self.server.arduino_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            return False
    
    async def read_loop(self):
        """Continuously read from Arduino and trigger emergency signals."""
        self.running = True
        logger.info("Starting Arduino read loop...")
        
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    if line == "EMERGENCY_ON":
                        logger.info("Arduino: Emergency button pressed!")
                        await self.server.trigger_arduino_emergency()
                        
                    elif line == "EMERGENCY_OFF":
                        logger.info("Arduino: Emergency cleared!")
                        await self.server.clear_arduino_emergency()
                        
                await asyncio.sleep(0.1)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logger.error(f"Error reading from Arduino: {e}")
                await asyncio.sleep(1)
    
    def stop(self):
        """Stop the Arduino interface."""
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
            logger.info("Arduino connection closed")

