#!/usr/bin/env python3
"""
Simple Emergency Vehicle Communication System - WebSocket Server
Basic WebSocket server for testing the frontend without complex dependencies.
Supports Arduino emergency button integration for classroom demos.
"""

import asyncio
import json
import logging
import uuid
import websockets
from websockets import WebSocketServerProtocol
from arduino_interface import ArduinoInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleVehicleServer:
    """Simple WebSocket server for vehicle communication simulation."""

    def __init__(self, host: str = '0.0.0.0', port: int = 8765):
        self.host = host
        self.port = port
        self.connections = {}  # device_id -> websocket
        self.device_states = {}  # device_id -> state info
        self.emergency_active = False
        self.emergency_device = None
        self.session_id = "classroom_demo_2024"  # Single shared session for everyone
        self.arduino_connected = False

    def generate_device_id(self):
        """Generate a unique device ID."""
        return str(uuid.uuid4())[:8]

    async def register_device(self, websocket: WebSocketServerProtocol, device_type: str = None):
        """Register a new device."""
        device_id = self.generate_device_id()
        self.connections[device_id] = websocket

        # Auto-assign vehicle position to avoid overlaps in shared view
        num_vehicles = len(self.device_states)
        lane = (num_vehicles % 3) + 1  # Distribute across 3 lanes
        position_x = (num_vehicles * 150) % 800  # Spread horizontally

        # Initialize device state
        self.device_states[device_id] = {
            'device_id': device_id,
            'vehicle_type': device_type or 'regular_car',
            'current_lane': lane,
            'position_x': position_x,
            'position_y': (lane - 1) * 50 + 25,
            'speed': 50,
            'is_emergency_active': device_type == 'emergency_vehicle',
            'color': self.generate_vehicle_color(num_vehicles)
        }

        logger.info(f"Device registered: {device_id} | Total vehicles: {len(self.device_states)}")
        
        # Broadcast to all that a new vehicle joined
        await self.broadcast_message({
            'type': 'vehicle_joined',
            'device_id': device_id,
            'total_vehicles': len(self.device_states)
        }, exclude_device=device_id)
        
        return device_id
    
    def generate_vehicle_color(self, index):
        """Generate a unique color for each vehicle."""
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
                  '#1abc9c', '#e67e22', '#34495e', '#16a085', '#d35400']
        return colors[index % len(colors)]

    async def unregister_device(self, device_id: str):
        """Remove a device."""
        if device_id in self.connections:
            del self.connections[device_id]
        if device_id in self.device_states:
            del self.device_states[device_id]

        logger.info(f"Device unregistered: {device_id}")

    async def broadcast_message(self, message: dict, exclude_device: str = None):
        """Broadcast message to all connected devices."""
        disconnected = []
        for device_id, websocket in self.connections.items():
            if device_id != exclude_device:
                try:
                    await websocket.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.append(device_id)

        # Clean up disconnected devices
        for device_id in disconnected:
            await self.unregister_device(device_id)

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming message."""
        try:
            data = json.loads(message)
            device_id = data.get('device_id')
            message_type = data.get('type')

            # Find device_id if not provided
            if not device_id:
                for did, ws in self.connections.items():
                    if ws == websocket:
                        device_id = did
                        break

            if not device_id or device_id not in self.connections:
                return

            if message_type == 'register_emergency' or message_type == 'register':
                # Handle emergency from either web client or LoRa gateway
                source = data.get('source', 'vehicle')
                rssi = data.get('rssi', 0)
                snr = data.get('snr', 0)
                
                if source == 'cv2x_lora':
                    logger.info(f"📡 C-V2X LoRa emergency received via gateway | RSSI: {rssi} dBm, SNR: {snr} dB")
                
                await self.trigger_emergency(device_id, source)

            elif message_type == 'clear_emergency':
                source = data.get('source', 'vehicle')
                await self.clear_emergency(device_id, source)

            elif message_type == 'position_update':
                # Update device position
                if device_id in self.device_states:
                    position = data.get('position', {})
                    self.device_states[device_id].update({
                        'position_x': position.get('x', self.device_states[device_id]['position_x']),
                        'position_y': position.get('y', self.device_states[device_id]['position_y']),
                        'speed': position.get('speed', self.device_states[device_id]['speed'])
                    })

                    # Broadcast position update
                    pos_msg = {
                        'type': 'position_update',
                        'device_id': device_id,
                        'position': self.device_states[device_id]
                    }
                    await self.broadcast_message(pos_msg, exclude_device=device_id)

            elif message_type == 'lane_change':
                # Handle lane change
                new_lane = data.get('new_lane')
                if new_lane and device_id in self.device_states:
                    old_lane = self.device_states[device_id]['current_lane']
                    self.device_states[device_id]['current_lane'] = new_lane

                    # Broadcast lane change
                    lane_msg = {
                        'type': 'lane_change',
                        'device_id': device_id,
                        'old_lane': old_lane,
                        'new_lane': new_lane,
                        'reason': data.get('reason', 'manual')
                    }
                    await self.broadcast_message(lane_msg, exclude_device=device_id)

        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def trigger_emergency(self, device_id, source='vehicle'):
        """Trigger emergency signal from a specific device."""
        self.emergency_active = True
        self.emergency_device = device_id

        # Broadcast emergency signal to ALL devices
        message_text = '🚨 EMERGENCY VEHICLE APPROACHING - CLEAR THE WAY!'
        if source == 'cv2x_lora':
            message_text = '📡 C-V2X EMERGENCY BROADCAST RECEIVED - CLEAR ALL LANES!'
        
        emergency_msg = {
            'type': 'emergency_signal',
            'device_id': device_id,
            'message': message_text,
            'source': source
        }
        await self.broadcast_message(emergency_msg)
        
        if source == 'cv2x_lora':
            logger.info(f"🚨 C-V2X Emergency triggered via LoRa: {device_id}")
        else:
            logger.info(f"Emergency triggered by device: {device_id}")
    
    async def clear_emergency(self, device_id, source='vehicle'):
        """Clear emergency signal from a specific device."""
        self.emergency_active = False
        self.emergency_device = None

        # Broadcast emergency cleared to ALL devices
        clear_msg = {
            'type': 'emergency_cleared',
            'device_id': device_id,
            'source': source
        }
        await self.broadcast_message(clear_msg)
        
        if source == 'cv2x_lora':
            logger.info(f"🟢 C-V2X Emergency cleared via LoRa: {device_id}")
        else:
            logger.info(f"Emergency cleared by device: {device_id}")
    
    async def trigger_arduino_emergency(self):
        """Trigger emergency from Arduino button - affects ALL vehicles."""
        if not self.emergency_active:
            self.emergency_active = True
            self.emergency_device = "ARDUINO_BUTTON"

            # Broadcast to EVERYONE
            emergency_msg = {
                'type': 'emergency_signal',
                'device_id': 'ARDUINO',
                'message': '🚨 PHYSICAL EMERGENCY BUTTON PRESSED - CLEAR ALL LANES!',
                'source': 'arduino'
            }
            await self.broadcast_message(emergency_msg)
            logger.info("🔴 ARDUINO EMERGENCY ACTIVATED")
    
    async def clear_arduino_emergency(self):
        """Clear emergency from Arduino button."""
        if self.emergency_active:
            self.emergency_active = False
            self.emergency_device = None

            clear_msg = {
                'type': 'emergency_cleared',
                'device_id': 'ARDUINO',
                'source': 'arduino'
            }
            await self.broadcast_message(clear_msg)
            logger.info("🟢 ARDUINO EMERGENCY CLEARED")

    async def connection_handler(self, websocket):
        """Handle new WebSocket connection."""
        device_id = None

        try:
            # Register device
            device_type = None
            # Check the path from websocket.request if available
            if hasattr(websocket, 'request') and websocket.request:
                path = websocket.request.path
                if '?' in path:
                    query = path.split('?')[1]
                    if 'type=emergency' in query:
                        device_type = 'emergency_vehicle'

            device_id = await self.register_device(websocket, device_type)

            # Send welcome message
            welcome_msg = {
                'type': 'welcome',
                'device_id': device_id,
                'vehicle_type': self.device_states[device_id]['vehicle_type'],
                'message': f'Device {device_id} connected successfully'
            }
            await websocket.send(json.dumps(welcome_msg))

            # Send current system state
            state_msg = {
                'type': 'system_state',
                'devices': self.device_states,
                'emergency_status': {
                    'active': self.emergency_active,
                    'active_emergency_device': self.emergency_device
                }
            }
            await websocket.send(json.dumps(state_msg))

            # Handle incoming messages
            async for message in websocket:
                await self.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for device: {device_id}")
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            if device_id:
                await self.unregister_device(device_id)

    async def start_server(self):
        """Start the WebSocket server and Arduino interface."""
        logger.info(f"🚀 Starting Emergency Vehicle Server on {self.host}:{self.port}")
        logger.info(f"📡 Session ID: {self.session_id}")
        logger.info(f"🌐 Public URL: ws://{self.host}:{self.port}")
        
        # Try to connect to Arduino
        arduino = ArduinoInterface(self)
        arduino_connected = await arduino.connect()
        
        if arduino_connected:
            # Start Arduino reading loop in background
            asyncio.create_task(arduino.read_loop())
            logger.info("✅ Arduino emergency button is ACTIVE")
        else:
            logger.info("⚠️  Arduino not connected - button will not be available")

        async with websockets.serve(
            self.connection_handler,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        ):
            logger.info("✅ Server started successfully - Ready for classroom demo!")
            logger.info("👥 Waiting for students to join...")
            await asyncio.Future()  # Run forever

    def run(self):
        """Run the server."""
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            logger.info("\n🛑 Server stopped by user")

if __name__ == '__main__':
    server = SimpleVehicleServer()
    server.run()
