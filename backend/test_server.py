#!/usr/bin/env python3
"""
Test script for the Emergency Vehicle Communication Server.
"""

import asyncio
import json
import websockets
import uuid

async def test_server():
    """Test the WebSocket server functionality."""

    # Test 1: Connect as regular vehicle
    print("Test 1: Connecting as regular vehicle...")
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            welcome_data = json.loads(welcome_msg)
            print(f"✓ Received welcome: {welcome_data}")

            device_id = welcome_data['device_id']
            print(f"✓ Device ID: {device_id}")

            # Send position update
            position_update = {
                'type': 'position_update',
                'device_id': device_id,
                'position': {'x': 100, 'y': 50, 'speed': 1.0}
            }
            await websocket.send(json.dumps(position_update))
            print("✓ Sent position update")

            # Test ping/pong
            ping_msg = {'type': 'ping'}
            await websocket.send(json.dumps(ping_msg))

            pong_msg = await websocket.recv()
            pong_data = json.loads(pong_msg)
            print(f"✓ Ping/pong test: {pong_data}")

    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
        return False

    # Test 2: Connect as emergency vehicle
    print("\nTest 2: Connecting as emergency vehicle...")
    try:
        async with websockets.connect("ws://localhost:8765?type=emergency") as websocket:
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            welcome_data = json.loads(welcome_msg)
            print(f"✓ Emergency vehicle welcome: {welcome_data}")

            emergency_device_id = welcome_data['device_id']

            # Activate emergency signal
            emergency_signal = {
                'type': 'register_emergency',
                'device_id': emergency_device_id
            }
            await websocket.send(json.dumps(emergency_signal))
            print("✓ Sent emergency signal")

            # Should receive emergency signal response
            response_msg = await websocket.recv()
            response_data = json.loads(response_msg)
            print(f"✓ Emergency response: {response_data}")

    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
        return False

    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    print("Testing Emergency Vehicle Communication Server...")
    print("Make sure the server is running on ws://localhost:8765")
    print("Press Ctrl+C to stop this test.\n")

    try:
        success = asyncio.run(test_server())
        if success:
            print("\n🎉 Server test completed successfully!")
        else:
            print("\n❌ Server test failed!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nTest error: {e}")
