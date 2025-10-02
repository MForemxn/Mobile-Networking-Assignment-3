"""
Device management system for vehicle communication.
Handles device registration, identification, and state management.
"""

import json
import logging
import uuid
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class VehicleType(Enum):
    """Types of vehicles in the simulation."""
    REGULAR_CAR = "regular_car"
    EMERGENCY_VEHICLE = "emergency_vehicle"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"

class LanePosition(Enum):
    """Lane positions on the highway."""
    LEFT_LANE = 1
    MIDDLE_LANE = 2
    RIGHT_LANE = 3

@dataclass
class DeviceState:
    """Represents the state of a connected device."""
    device_id: str
    vehicle_type: VehicleType
    current_lane: LanePosition
    position_x: float
    position_y: float
    speed: float
    is_emergency_active: bool = False
    connection_status: str = "connected"

    def to_dict(self) -> dict:
        """Convert state to dictionary for JSON serialization."""
        return {
            **asdict(self),
            'vehicle_type': self.vehicle_type.value,
            'current_lane': self.current_lane.value,
            'connection_status': self.connection_status
        }

class DeviceManager:
    """Manages all connected devices and their states."""

    def __init__(self):
        self.devices: Dict[str, DeviceState] = {}
        self.websocket_handler = None

    def set_websocket_handler(self, handler):
        """Set the WebSocket handler for message broadcasting."""
        self.websocket_handler = handler

    def register_device(self, websocket, device_type: str = None) -> str:
        """Register a new device and return its unique ID."""
        device_id = str(uuid.uuid4())

        # Determine vehicle type
        if device_type == 'emergency':
            vehicle_type = VehicleType.EMERGENCY_VEHICLE
        else:
            # Randomly assign vehicle type for simulation
            vehicle_type = random.choice([
                VehicleType.REGULAR_CAR,
                VehicleType.TRUCK,
                VehicleType.MOTORCYCLE
            ])

        # Assign random starting lane and position
        start_lane = random.choice(list(LanePosition))
        start_x = random.uniform(0, 100)
        start_y = start_lane.value * 50  # Lanes are vertically separated

        device_state = DeviceState(
            device_id=device_id,
            vehicle_type=vehicle_type,
            current_lane=start_lane,
            position_x=start_x,
            position_y=start_y,
            speed=random.uniform(0.8, 1.2),  # Varied speeds
            is_emergency_active=(vehicle_type == VehicleType.EMERGENCY_VEHICLE)
        )

        self.devices[device_id] = device_state
        logger.info(f"Registered device: {device_id} as {vehicle_type.value}")

        return device_id

    def unregister_device(self, device_id: str):
        """Remove a device from the system."""
        if device_id in self.devices:
            device_state = self.devices[device_id]
            logger.info(f"Unregistering device: {device_id} ({device_state.vehicle_type.value})")
            del self.devices[device_id]

    def get_device_state(self, device_id: str) -> Optional[DeviceState]:
        """Get the current state of a device."""
        return self.devices.get(device_id)

    def update_device_position(self, device_id: str, x: float, y: float, speed: float = None):
        """Update device position."""
        if device_id in self.devices:
            device = self.devices[device_id]
            device.position_x = x
            device.position_y = y
            if speed is not None:
                device.speed = speed

            # Update lane based on y position
            lane_value = round(y / 50)  # Assuming 50 units per lane
            try:
                device.current_lane = LanePosition(lane_value)
            except ValueError:
                # Keep current lane if calculation is invalid
                pass

    def update_device_lane(self, device_id: str, new_lane: LanePosition, reason: str = "manual"):
        """Update device lane position."""
        if device_id in self.devices:
            old_lane = self.devices[device_id].current_lane
            self.devices[device_id].current_lane = new_lane

            # Adjust y position based on new lane
            self.devices[device_id].position_y = new_lane.value * 50

            logger.info(f"Device {device_id} moved from lane {old_lane.value} to {new_lane.value} ({reason})")

            # Broadcast lane change if WebSocket handler is available
            if self.websocket_handler:
                lane_message = {
                    'type': 'lane_change',
                    'device_id': device_id,
                    'old_lane': old_lane.value,
                    'new_lane': new_lane.value,
                    'reason': reason
                }
                # This would need to be awaited if called from async context
                asyncio.create_task(self.websocket_handler.broadcast_to_all(lane_message, exclude_device=device_id))

    def activate_emergency_mode(self, device_id: str):
        """Activate emergency mode for a device."""
        if device_id in self.devices:
            self.devices[device_id].is_emergency_active = True

            logger.info(f"Emergency mode activated for device: {device_id}")

            # Broadcast emergency signal
            if self.websocket_handler:
                emergency_message = {
                    'type': 'emergency_signal',
                    'device_id': device_id,
                    'message': 'Emergency vehicle approaching - clear path immediately'
                }
                asyncio.create_task(self.websocket_handler.broadcast_to_all(emergency_message, exclude_device=device_id))

    def deactivate_emergency_mode(self, device_id: str):
        """Deactivate emergency mode for a device."""
        if device_id in self.devices:
            self.devices[device_id].is_emergency_active = False

            logger.info(f"Emergency mode deactivated for device: {device_id}")

            # Broadcast emergency cleared signal
            if self.websocket_handler:
                clear_message = {
                    'type': 'emergency_cleared',
                    'device_id': device_id
                }
                asyncio.create_task(self.websocket_handler.broadcast_to_all(clear_message))

    def get_all_devices_state(self) -> Dict[str, dict]:
        """Get state of all devices as dictionary."""
        return {device_id: device.to_dict() for device_id, device in self.devices.items()}

    def get_devices_by_type(self, vehicle_type: VehicleType) -> List[str]:
        """Get list of device IDs by vehicle type."""
        return [
            device_id for device_id, device in self.devices.items()
            if device.vehicle_type == vehicle_type
        ]

    def get_devices_by_lane(self, lane: LanePosition) -> List[str]:
        """Get list of device IDs in a specific lane."""
        return [
            device_id for device_id, device in self.devices.items()
            if device.current_lane == lane
        ]

    def get_emergency_devices(self) -> List[str]:
        """Get list of device IDs with active emergency status."""
        return [
            device_id for device_id, device in self.devices.items()
            if device.is_emergency_active
        ]

    def simulate_vehicle_movement(self, delta_time: float = 1.0):
        """Simulate vehicle movement over time."""
        for device_id, device in self.devices.items():
            # Simple movement simulation
            movement_distance = device.speed * delta_time * 10  # Arbitrary scaling
            device.position_x += movement_distance

            # Reset position if vehicle goes off screen
            if device.position_x > 800:  # Assuming 800px width
                device.position_x = -50

    def get_road_state(self) -> Dict[str, Any]:
        """Get complete road state for frontend."""
        return {
            'devices': self.get_all_devices_state(),
            'lanes': {
                'left': self.get_devices_by_lane(LanePosition.LEFT_LANE),
                'middle': self.get_devices_by_lane(LanePosition.MIDDLE_LANE),
                'right': self.get_devices_by_lane(LanePosition.RIGHT_LANE)
            },
            'emergency_active': len(self.get_emergency_devices()) > 0,
            'total_vehicles': len(self.devices)
        }
