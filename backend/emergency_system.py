"""
Emergency response system for vehicle communication.
Handles emergency signals and coordinated vehicle responses.
"""

import asyncio
import logging
import time
from typing import Dict, List, Set, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class EmergencyState(Enum):
    """States of the emergency response system."""
    NORMAL = "normal"
    EMERGENCY_ACTIVE = "emergency_active"
    CLEARING_PATH = "clearing_path"
    PATH_CLEARED = "path_cleared"

class EmergencyResponseSystem:
    """Manages emergency signals and vehicle response coordination."""

    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.emergency_state = EmergencyState.NORMAL
        self.active_emergency_device: Optional[str] = None
        self.response_timeout = 30  # seconds
        self.path_clearing_start_time: Optional[float] = None

        # Lane priorities for emergency response
        self.lane_priorities = {
            1: 3,  # Left lane should move to right lane (3)
            2: 3,  # Middle lane should move to right lane (3)
            3: 3   # Right lane stays in right lane (3)
        }

    async def activate_emergency_signal(self, device_id: str) -> bool:
        """Activate emergency signal for a device."""
        if self.emergency_state != EmergencyState.NORMAL:
            logger.warning(f"Emergency signal rejected - already in state: {self.emergency_state}")
            return False

        # Verify the device exists and can be emergency vehicle
        device_state = self.device_manager.get_device_state(device_id)
        if not device_state:
            logger.error(f"Emergency signal from unknown device: {device_id}")
            return False

        self.emergency_state = EmergencyState.EMERGENCY_ACTIVE
        self.active_emergency_device = device_id
        self.path_clearing_start_time = time.time()

        logger.info(f"Emergency signal activated by device: {device_id}")

        # Broadcast emergency signal to all devices
        await self._broadcast_emergency_signal(device_id)

        # Start path clearing coordination
        asyncio.create_task(self._coordinate_path_clearing())

        return True

    async def deactivate_emergency_signal(self, device_id: str) -> bool:
        """Deactivate emergency signal."""
        if self.active_emergency_device != device_id:
            logger.warning(f"Emergency deactivation from non-active device: {device_id}")
            return False

        self.emergency_state = EmergencyState.NORMAL
        self.active_emergency_device = None
        self.path_clearing_start_time = None

        logger.info(f"Emergency signal deactivated by device: {device_id}")

        # Broadcast emergency cleared signal
        await self._broadcast_emergency_cleared(device_id)

        return True

    async def _broadcast_emergency_signal(self, device_id: str):
        """Broadcast emergency signal to all connected devices."""
        if not self.device_manager.websocket_handler:
            logger.error("No WebSocket handler available for broadcasting")
            return

        emergency_message = {
            'type': 'emergency_signal',
            'emergency_device_id': device_id,
            'state': self.emergency_state.value,
            'message': 'Emergency vehicle approaching - clear path immediately',
            'timestamp': time.time(),
            'target_lanes': self._calculate_target_lanes()
        }

        await self.device_manager.websocket_handler.broadcast_to_all(
            emergency_message,
            exclude_device=device_id
        )

    async def _broadcast_emergency_cleared(self, device_id: str):
        """Broadcast emergency cleared signal."""
        if not self.device_manager.websocket_handler:
            return

        clear_message = {
            'type': 'emergency_cleared',
            'emergency_device_id': device_id,
            'state': self.emergency_state.value,
            'message': 'Emergency vehicle passed - resume normal operation',
            'timestamp': time.time()
        }

        await self.device_manager.websocket_handler.broadcast_to_all(clear_message)

    def _calculate_target_lanes(self) -> Dict[int, int]:
        """Calculate target lanes for each current lane during emergency."""
        targets = {}

        for current_lane in self.lane_priorities:
            targets[current_lane] = self.lane_priorities[current_lane]

        return targets

    async def _coordinate_path_clearing(self):
        """Coordinate the path clearing process."""
        self.emergency_state = EmergencyState.CLEARING_PATH

        logger.info("Starting path clearing coordination")

        # Give vehicles time to respond
        await asyncio.sleep(2)

        # Check if path is clearing
        await self._monitor_path_clearing()

        # Set path cleared state
        self.emergency_state = EmergencyState.PATH_CLEARED
        logger.info("Path clearing coordination completed")

    async def _monitor_path_clearing(self):
        """Monitor the path clearing progress."""
        max_monitor_time = 10  # seconds
        start_time = time.time()

        while (time.time() - start_time) < max_monitor_time:
            # Check if emergency device still exists
            if not self.device_manager.get_device_state(self.active_emergency_device):
                logger.warning("Emergency device disconnected during path clearing")
                break

            # Check response status (simplified - in real system would track acknowledgments)
            vehicles_responded = await self._check_vehicle_responses()

            if vehicles_responded >= len(self.device_manager.devices) * 0.8:  # 80% response rate
                logger.info("Sufficient vehicles have responded to emergency signal")
                break

            await asyncio.sleep(1)

    async def _check_vehicle_responses(self) -> int:
        """Check how many vehicles have responded to emergency signal."""
        # In a real system, this would track acknowledgment messages
        # For simulation, we'll assume immediate response
        return len(self.device_manager.devices)

    def get_emergency_status(self) -> Dict:
        """Get current emergency system status."""
        return {
            'state': self.emergency_state.value,
            'active_emergency_device': self.active_emergency_device,
            'time_since_activation': (
                time.time() - self.path_clearing_start_time
                if self.path_clearing_start_time else None
            ),
            'target_lanes': self._calculate_target_lanes()
        }

    def handle_vehicle_response(self, device_id: str, response_type: str, data: Dict = None):
        """Handle response from a vehicle to emergency signal."""
        if self.emergency_state == EmergencyState.NORMAL:
            return

        logger.info(f"Vehicle {device_id} responded to emergency: {response_type}")

        # Process different types of responses
        if response_type == 'lane_change_completed':
            self._process_lane_change_response(device_id, data)
        elif response_type == 'emergency_acknowledged':
            self._process_acknowledgment_response(device_id)

    def _process_lane_change_response(self, device_id: str, data: Dict):
        """Process lane change completion response."""
        from_lane = data.get('from_lane')
        to_lane = data.get('to_lane')

        logger.info(f"Vehicle {device_id} completed lane change: {from_lane} -> {to_lane}")

        # In a real system, track which vehicles have completed their lane changes

    def _process_acknowledgment_response(self, device_id: str):
        """Process emergency acknowledgment response."""
        logger.info(f"Vehicle {device_id} acknowledged emergency signal")

        # In a real system, track which vehicles have acknowledged the signal

    def is_emergency_active(self) -> bool:
        """Check if emergency mode is currently active."""
        return self.emergency_state != EmergencyState.NORMAL

    def get_emergency_device(self) -> Optional[str]:
        """Get the device ID of the active emergency vehicle."""
        return self.active_emergency_device

    def can_activate_emergency(self, device_id: str) -> bool:
        """Check if a device can activate emergency mode."""
        # Only one emergency vehicle at a time
        if self.is_emergency_active():
            return False

        # Device must exist
        device_state = self.device_manager.get_device_state(device_id)
        if not device_state:
            return False

        # Could add more restrictions here (e.g., only certain vehicle types)
        return True
