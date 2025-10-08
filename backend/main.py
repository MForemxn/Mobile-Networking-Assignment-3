#!/usr/bin/env python3
"""
Simple Emergency Vehicle Communication System - WebSocket Server
Basic WebSocket server for testing the frontend without complex dependencies.
"""

import asyncio
import json
import logging
import uuid
import websockets
from websockets import WebSocketServerProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleVehicleServer:
    """Simple WebSocket server for vehicle communication simulation."""

    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.connections = {}  # device_id -> websocket
        self.device_states = {}  # device_id -> state info
        self.emergency_active = False
        self.emergency_device = None

    def generate_device_id(self):
        """Generate a unique device ID."""
        return str(uuid.uuid4())[:8]

    async def register_device(self, websocket: WebSocketServerProtocol, device_type: str = None):
        """Register a new device."""
        device_id = self.generate_device_id()
        self.connections[device_id] = websocket

        # Initialize device state
        self.device_states[device_id] = {
            'device_id': device_id,
            'vehicle_type': device_type or 'regular_car',
            'current_lane': 2,  # Middle lane
            'position_x': 0,
            'position_y': 50,
            'speed': 50,
            'is_emergency_active': device_type == 'emergency_vehicle'
        }

        logger.info(f"Device registered: {device_id}")
        return device_id

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

            if message_type == 'register_emergency':
                self.emergency_active = True
                self.emergency_device = device_id

                # Broadcast emergency signal
                emergency_msg = {
                    'type': 'emergency_signal',
                    'device_id': device_id,
                    'message': 'Emergency vehicle approaching - clear the way!'
                }
                await self.broadcast_message(emergency_msg, exclude_device=device_id)

            elif message_type == 'clear_emergency':
                self.emergency_active = False
                self.emergency_device = None

                # Broadcast emergency cleared
                clear_msg = {
                    'type': 'emergency_cleared',
                    'device_id': device_id
                }
                await self.broadcast_message(clear_msg)

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
        """Start the WebSocket server."""
        logger.info(f"Starting Emergency Vehicle Server on {self.host}:{self.port}")

        async with websockets.serve(
            self.connection_handler,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        ):
            logger.info("Server started successfully")
            await asyncio.Future()  # Run forever

    def run(self):
        """Run the server."""
        asyncio.run(self.start_server())

if __name__ == '__main__':
    server = SimpleVehicleServer()
    server.run()
