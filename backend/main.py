#!/usr/bin/env python3
"""
Emergency Vehicle Communication System - WebSocket Server
Main entry point for the vehicle communication simulation server.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Set
import websockets
from websockets import WebSocketServerProtocol

from device_manager import DeviceManager
from websocket_handler import WebSocketHandler
from emergency_system import EmergencyResponseSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VehicleCommunicationServer:
    """Main WebSocket server for vehicle communication simulation."""

    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port

        # Initialize core systems
        self.device_manager = DeviceManager()
        self.websocket_handler = WebSocketHandler(self)
        self.emergency_system = EmergencyResponseSystem(self.device_manager)

        # Set up cross-references
        self.device_manager.set_websocket_handler(self.websocket_handler)

    async def register_device(self, websocket: WebSocketServerProtocol, device_type: str = None) -> str:
        """Register a new device and return its unique ID."""
        device_id = self.device_manager.register_device(websocket, device_type)
        await self.websocket_handler.register_connection(device_id, websocket)

        logger.info(f"Device registered: {device_id}")
        return device_id

    async def unregister_device(self, device_id: str):
        """Remove a device from the system."""
        self.device_manager.unregister_device(device_id)
        await self.websocket_handler.unregister_connection(device_id)

        logger.info(f"Device unregistered: {device_id}")

    async def broadcast_message(self, message: dict, exclude_device: str = None):
        """Broadcast a message to all connected devices except optionally one."""
        await self.websocket_handler.broadcast_to_all(message, exclude_device)

    async def handle_emergency_signal(self, device_id: str):
        """Handle emergency signal from a device."""
        if self.emergency_system.can_activate_emergency(device_id):
            success = await self.emergency_system.activate_emergency_signal(device_id)
            if not success:
                logger.warning(f"Failed to activate emergency signal for device: {device_id}")
        else:
            logger.warning(f"Device {device_id} cannot activate emergency signal")

    async def handle_position_update(self, device_id: str, position_data: dict):
        """Handle position update from a device."""
        if device_id in self.device_manager.devices:
            self.device_manager.update_device_position(
                device_id,
                position_data.get('x', 0),
                position_data.get('y', 0),
                position_data.get('speed')
            )

        # Broadcast position update to other devices
        position_message = {
            'type': 'position_update',
            'device_id': device_id,
            'position': self.device_manager.get_device_state(device_id).to_dict() if device_id in self.device_manager.devices else {}
        }

        await self.broadcast_message(position_message, exclude_device=device_id)

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming message from a device."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            device_id = data.get('device_id')

            # If device_id not in message, find it from websocket connection
            if not device_id:
                for did, ws in self.websocket_handler.device_connections.items():
                    if ws == websocket:
                        device_id = did
                        break

            if not device_id:
                logger.warning("Received message from unregistered device")
                return

            if message_type == 'register_emergency':
                await self.handle_emergency_signal(device_id)

            elif message_type == 'clear_emergency':
                await self.emergency_system.deactivate_emergency_signal(device_id)
                clear_message = {
                    'type': 'emergency_cleared',
                    'device_id': device_id
                }
                await self.broadcast_message(clear_message)

            elif message_type == 'position_update':
                await self.handle_position_update(device_id, data.get('position', {}))

            elif message_type == 'lane_change':
                # Handle lane change requests
                new_lane = data.get('new_lane')
                reason = data.get('reason', 'manual')
                if new_lane and device_id in self.device_manager.devices:
                    from device_manager import LanePosition
                    try:
                        lane_enum = LanePosition(new_lane)
                        self.device_manager.update_device_lane(device_id, lane_enum, reason)
                    except ValueError:
                        logger.warning(f"Invalid lane number: {new_lane}")

            elif message_type == 'ping':
                # Respond to ping with pong
                pong_message = {'type': 'pong', 'timestamp': asyncio.get_event_loop().time()}
                await websocket.send(json.dumps(pong_message))

            elif message_type == 'get_system_state':
                # Send current system state
                system_state = {
                    'type': 'system_state',
                    'devices': self.device_manager.get_all_devices_state(),
                    'emergency_status': self.emergency_system.get_emergency_status(),
                    'road_state': self.device_manager.get_road_state()
                }
                await websocket.send(json.dumps(system_state))

        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def connection_handler(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection."""
        device_id = None

        try:
            # Register the device (check for device type in query params)
            device_type = None
            if '?' in path:
                query = path.split('?')[1]
                if 'type=emergency' in query:
                    device_type = 'emergency'

            device_id = await self.register_device(websocket, device_type)

            # Send welcome message with device ID
            welcome_message = {
                'type': 'welcome',
                'device_id': device_id,
                'vehicle_type': self.device_manager.get_device_state(device_id).vehicle_type.value if device_id in self.device_manager.devices else 'unknown',
                'message': f'Device {device_id} connected successfully'
            }
            await websocket.send(json.dumps(welcome_message))

            # Send current state
            state_message = {
                'type': 'system_state',
                'devices': self.device_manager.get_all_devices_state(),
                'emergency_status': self.emergency_system.get_emergency_status(),
                'road_state': self.device_manager.get_road_state()
            }
            await websocket.send(json.dumps(state_message))

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
        logger.info(f"Starting Emergency Vehicle Communication Server on {self.host}:{self.port}")

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
        """Run the server (blocking call)."""
        asyncio.run(self.start_server())

if __name__ == '__main__':
    server = VehicleCommunicationServer()
    server.run()
