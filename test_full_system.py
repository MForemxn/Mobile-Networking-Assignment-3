#!/usr/bin/env python3
"""
Comprehensive test suite for the Emergency Vehicle Communication System.
Tests both backend and frontend integration.
"""

import asyncio
import json
import subprocess
import sys
import time
import threading
import requests
from pathlib import Path

class SystemTester:
    """Comprehensive testing suite for the emergency vehicle system."""

    def __init__(self):
        self.backend_process = None
        self.test_results = {}
        self.errors = []

    def log(self, message, level="INFO"):
        """Log a message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def start_backend_server(self):
        """Start the backend WebSocket server."""
        try:
            self.log("Starting backend server...")
            self.backend_process = subprocess.Popen(
                [sys.executable, "backend/main.py"],
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)  # Give server time to start
            self.log("Backend server started successfully")
            return True
        except Exception as e:
            self.log(f"Failed to start backend server: {e}", "ERROR")
            return False

    def stop_backend_server(self):
        """Stop the backend server."""
        if self.backend_process:
            self.log("Stopping backend server...")
            self.backend_process.terminate()
            self.backend_process.wait()
            self.log("Backend server stopped")

    def test_backend_imports(self):
        """Test that all backend modules can be imported."""
        try:
            self.log("Testing backend module imports...")

            # Test main imports
            import backend.main
            import backend.device_manager
            import backend.websocket_handler
            import backend.emergency_system

            self.log("✓ All backend modules imported successfully")
            return True
        except ImportError as e:
            self.log(f"✗ Import error: {e}", "ERROR")
            self.errors.append(f"Import error: {e}")
            return False

    def test_websocket_server(self):
        """Test WebSocket server functionality."""
        try:
            import websockets
            import asyncio

            async def test_websocket():
                try:
                    # Test connection
                    async with websockets.connect("ws://localhost:8765") as websocket:
                        self.log("✓ WebSocket connection established")

                        # Test welcome message
                        welcome_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        welcome_data = json.loads(welcome_msg)

                        if welcome_data.get('type') == 'welcome':
                            self.log(f"✓ Welcome message received: {welcome_data.get('device_id')[:8]}...")
                        else:
                            raise Exception("No welcome message received")

                        # Test system state request
                        state_request = {'type': 'get_system_state'}
                        await websocket.send(json.dumps(state_request))

                        state_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        state_data = json.loads(state_msg)

                        if state_data.get('type') == 'system_state':
                            self.log("✓ System state received successfully")
                        else:
                            raise Exception("No system state received")

                        # Test ping/pong
                        ping_msg = {'type': 'ping'}
                        await websocket.send(json.dumps(ping_msg))

                        pong_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        pong_data = json.loads(pong_msg)

                        if pong_data.get('type') == 'pong':
                            self.log("✓ Ping/pong test passed")
                        else:
                            raise Exception("No pong response received")

                    return True

                except Exception as e:
                    self.log(f"✗ WebSocket test failed: {e}", "ERROR")
                    self.errors.append(f"WebSocket test failed: {e}")
                    return False

            # Run the async test
            return asyncio.run(test_websocket())

        except ImportError:
            self.log("✗ WebSocket library not available", "ERROR")
            self.errors.append("WebSocket library not available")
            return False

    def test_emergency_system(self):
        """Test emergency vehicle functionality."""
        try:
            import websockets
            import asyncio

            async def test_emergency():
                try:
                    # Connect as emergency vehicle
                    async with websockets.connect("ws://localhost:8765?type=emergency") as ws1:
                        welcome_msg = await ws1.recv()
                        welcome_data = json.loads(welcome_msg)
                        emergency_device_id = welcome_data['device_id']
                        self.log(f"✓ Emergency vehicle connected: {emergency_device_id[:8]}...")

                        # Connect as regular vehicle
                        async with websockets.connect("ws://localhost:8765") as ws2:
                            welcome_msg2 = await ws2.recv()
                            welcome_data2 = json.loads(welcome_msg2)
                            regular_device_id = welcome_data2['device_id']
                            self.log(f"✓ Regular vehicle connected: {regular_device_id[:8]}...")

                            # Activate emergency signal
                            emergency_signal = {
                                'type': 'register_emergency',
                                'device_id': emergency_device_id
                            }
                            await ws1.send(json.dumps(emergency_signal))
                            self.log("✓ Emergency signal sent")

                            # Regular vehicle should receive emergency signal
                            emergency_received = await asyncio.wait_for(ws2.recv(), timeout=5.0)
                            emergency_data = json.loads(emergency_received)

                            if emergency_data.get('type') == 'emergency_signal':
                                self.log("✓ Emergency signal received by regular vehicle")
                            else:
                                raise Exception("Emergency signal not received")

                            # Clear emergency
                            clear_signal = {
                                'type': 'clear_emergency',
                                'device_id': emergency_device_id
                            }
                            await ws1.send(json.dumps(clear_signal))
                            self.log("✓ Emergency cleared")

                            # Should receive clear signal
                            clear_received = await asyncio.wait_for(ws2.recv(), timeout=5.0)
                            clear_data = json.loads(clear_received)

                            if clear_data.get('type') == 'emergency_cleared':
                                self.log("✓ Emergency clear received by regular vehicle")
                            else:
                                raise Exception("Emergency clear not received")

                    return True

                except Exception as e:
                    self.log(f"✗ Emergency system test failed: {e}", "ERROR")
                    self.errors.append(f"Emergency system test failed: {e}")
                    return False

            return asyncio.run(test_emergency())

        except ImportError:
            self.log("✗ WebSocket library not available for emergency test", "ERROR")
            return False

    def test_frontend_build(self):
        """Test that the frontend can be built."""
        try:
            self.log("Testing frontend build...")

            frontend_dir = Path(__file__).parent / "frontend"
            if not frontend_dir.exists():
                self.log("✗ Frontend directory not found", "ERROR")
                return False

            # Check if package.json exists
            package_json = frontend_dir / "package.json"
            if not package_json.exists():
                self.log("✗ package.json not found", "ERROR")
                return False

            # Try to run npm install (dry run check)
            try:
                result = subprocess.run(
                    ["npm", "install", "--dry-run"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    self.log("✓ Frontend dependencies check passed")
                    return True
                else:
                    self.log(f"✗ Frontend dependency issue: {result.stderr}", "ERROR")
                    return False

            except subprocess.TimeoutExpired:
                self.log("✗ Frontend dependency check timed out", "ERROR")
                return False
            except FileNotFoundError:
                self.log("✗ npm not found - please install Node.js", "ERROR")
                return False

        except Exception as e:
            self.log(f"✗ Frontend build test failed: {e}", "ERROR")
            self.errors.append(f"Frontend build test failed: {e}")
            return False

    def test_system_integration(self):
        """Test full system integration."""
        try:
            self.log("Testing system integration...")

            # Check if all necessary files exist
            required_files = [
                "backend/main.py",
                "backend/device_manager.py",
                "backend/websocket_handler.py",
                "backend/emergency_system.py",
                "frontend/package.json",
                "frontend/src/App.js",
                "frontend/src/services/websocketService.js"
            ]

            missing_files = []
            for file_path in required_files:
                full_path = Path(__file__).parent / file_path
                if not full_path.exists():
                    missing_files.append(file_path)

            if missing_files:
                self.log(f"✗ Missing required files: {missing_files}", "ERROR")
                self.errors.extend([f"Missing file: {f}" for f in missing_files])
                return False

            self.log("✓ All required files present")
            return True

        except Exception as e:
            self.log(f"✗ System integration test failed: {e}", "ERROR")
            self.errors.append(f"System integration test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all tests and report results."""
        self.log("Starting comprehensive system test...")

        tests = [
            ("Backend Imports", self.test_backend_imports),
            ("System Integration", self.test_system_integration),
            ("Frontend Build", self.test_frontend_build),
        ]

        # Start backend server for WebSocket tests
        if self.start_backend_server():
            tests.extend([
                ("WebSocket Server", self.test_websocket_server),
                ("Emergency System", self.test_emergency_system),
            ])

            # Run tests
            for test_name, test_func in tests:
                self.log(f"Running test: {test_name}")
                try:
                    result = test_func()
                    self.test_results[test_name] = result
                    if result:
                        self.log(f"✓ {test_name} passed")
                    else:
                        self.log(f"✗ {test_name} failed")
                except Exception as e:
                    self.log(f"✗ {test_name} error: {e}", "ERROR")
                    self.test_results[test_name] = False
                    self.errors.append(f"{test_name} error: {e}")

            # Stop backend server
            self.stop_backend_server()
        else:
            self.log("Skipping WebSocket tests due to server startup failure", "WARNING")
            # Run non-WebSocket tests anyway
            for test_name, test_func in tests[:3]:  # Only run first 3 tests
                self.log(f"Running test: {test_name}")
                try:
                    result = test_func()
                    self.test_results[test_name] = result
                    if result:
                        self.log(f"✓ {test_name} passed")
                    else:
                        self.log(f"✗ {test_name} failed")
                except Exception as e:
                    self.log(f"✗ {test_name} error: {e}", "ERROR")
                    self.test_results[test_name] = False
                    self.errors.append(f"{test_name} error: {e}")

        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print a summary of all test results."""
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)

        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("❌ Some tests failed")

        print(f"\nTest Results:")
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {test_name}")

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        print("="*60)

def main():
    """Main test function."""
    tester = SystemTester()
    tester.run_all_tests()

    # Exit with appropriate code
    passed = sum(1 for result in tester.test_results.values() if result)
    total = len(tester.test_results)
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
