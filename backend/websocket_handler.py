"""
WebSocket connection handler for vehicle communication system.
"""

import json
import logging
import asyncio
from typing import Dict, Set
from websockets import WebSocketServerProtocol

logger = logging.getLogger(__name__)

class WebSocketHandler:
    """Handles WebSocket connections and message routing."""

    def __init__(self, server_instance):
        self.server = server_instance
        self.device_connections: Dict[str, WebSocketServerProtocol] = {}
        self.emergency_devices: Set[str] = set()

    async def register_connection(self, device_id: str, websocket: WebSocketServerProtocol):
        """Register a new device connection."""
        self.device_connections[device_id] = websocket
        logger.info(f"Device connection registered: {device_id}")

    async def unregister_connection(self, device_id: str):
        """Unregister a device connection."""
        if device_id in self.device_connections:
            del self.device_connections[device_id]
        if device_id in self.emergency_devices:
            self.emergency_devices.discard(device_id)
        logger.info(f"Device connection unregistered: {device_id}")

    async def broadcast_to_all(self, message: dict, exclude_device: str = None):
        """Broadcast message to all connected devices."""
        message_str = json.dumps(message)

        disconnected_devices = []
        for device_id, websocket in self.device_connections.items():
            if device_id != exclude_device:
                try:
                    await websocket.send(message_str)
                except Exception as e:
                    logger.warning(f"Failed to send to {device_id}: {e}")
                    disconnected_devices.append(device_id)

        # Clean up disconnected devices
        for device_id in disconnected_devices:
            await self.unregister_connection(device_id)

    async def send_to_device(self, device_id: str, message: dict):
        """Send message to specific device."""
        if device_id in self.device_connections:
            try:
                websocket = self.device_connections[device_id]
                await websocket.send(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed to send to {device_id}: {e}")
                await self.unregister_connection(device_id)

    async def handle_incoming_message(self, device_id: str, message_data: dict):
        """Process incoming message from device."""
        message_type = message_data.get('type')

        if message_type == 'emergency_signal':
            await self._handle_emergency_signal(device_id)
        elif message_type == 'position_update':
            await self._handle_position_update(device_id, message_data)
        elif message_type == 'lane_change':
            await self._handle_lane_change(device_id, message_data)
        elif message_type == 'device_info':
            await self._handle_device_info(device_id, message_data)

    async def _handle_emergency_signal(self, device_id: str):
        """Handle emergency signal activation."""
        self.emergency_devices.add(device_id)

        emergency_message = {
            'type': 'emergency_active',
            'emergency_device': device_id,
            'message': 'Emergency vehicle approaching - clear all lanes'
        }

        await self.broadcast_to_all(emergency_message, exclude_device=device_id)
        logger.info(f"Emergency signal activated by device: {device_id}")

    async def _handle_position_update(self, device_id: str, message_data: dict):
        """Handle position update from device."""
        position = message_data.get('position', {})

        # Update server-side position tracking if needed
        if hasattr(self.server, 'device_positions'):
            self.server.device_positions[device_id] = position

        # Broadcast position update to other devices
        position_message = {
            'type': 'position_update',
            'device_id': device_id,
            'position': position
        }

        await self.broadcast_to_all(position_message, exclude_device=device_id)

    async def _handle_lane_change(self, device_id: str, message_data: dict):
        """Handle lane change notification."""
        new_lane = message_data.get('new_lane')
        reason = message_data.get('reason', 'normal')

        lane_change_message = {
            'type': 'lane_change',
            'device_id': device_id,
            'new_lane': new_lane,
            'reason': reason
        }

        await self.broadcast_to_all(lane_change_message, exclude_device=device_id)
        logger.info(f"Device {device_id} changed to lane {new_lane} ({reason})")

    async def _handle_device_info(self, device_id: str, message_data: dict):
        """Handle device information update."""
        device_info = message_data.get('info', {})

        info_message = {
            'type': 'device_info',
            'device_id': device_id,
            'info': device_info
        }

        await self.broadcast_to_all(info_message, exclude_device=device_id)

    def get_connected_devices(self) -> list:
        """Get list of currently connected device IDs."""
        return list(self.device_connections.keys())

    def get_emergency_devices(self) -> list:
        """Get list of devices that have emergency status."""
        return list(self.emergency_devices)

    def is_emergency_device(self, device_id: str) -> bool:
        """Check if device is an emergency vehicle."""
        return device_id in self.emergency_devices
