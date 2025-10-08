# Emergency Vehicle Highway Communication System

## Project Overview

This project demonstrates a proof-of-concept for an emergency vehicle communication system that uses WebSocket technology to simulate Bluetooth Low Energy (BLE) communication between vehicles. The system allows an emergency vehicle (ambulance) to broadcast a signal that causes all other vehicles on a simulated multilane highway to simultaneously move out of the way, clearing a path for emergency response.

## Architecture

### System Components

1. **Python WebSocket Server** (`backend/`)
   - Simulates Bluetooth devices via WebSocket connections
   - Each instance represents a vehicle with a unique device ID
   - Handles message routing between connected devices
   - Manages emergency signal broadcasting

2. **React Frontend** (`frontend/`)
   - Renders a multilane highway simulation with 6-7 vehicles
   - Provides UI for emergency vehicle operators
   - Visualizes vehicle movement and emergency response
   - Connects to WebSocket server for real-time communication

### Communication Flow

```
Emergency Vehicle → WebSocket Server → Other Vehicles
       ↓                ↓                    ↓
   Button Press → Emergency Signal → Lane Change
```

## Technology Stack

- **Backend**: Python 3.8+, asyncio, websockets library
- **Frontend**: React 18+, TypeScript, CSS3
- **Communication**: WebSocket protocol (simulating Bluetooth BLE)
- **Deployment**: Local development servers

## Features

### Core Functionality
- ✅ Real-time WebSocket communication between multiple vehicle instances
- ✅ Emergency vehicle identification and signaling system
- ✅ Simultaneous lane change response from all vehicles
- ✅ Visual highway simulation with multiple lanes
- ✅ Vehicle movement animation and collision avoidance

### Technical Features
- Device registration and unique ID assignment
- Message broadcasting and routing
- Emergency signal priority handling
- Real-time position updates
- Responsive UI with smooth animations

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ and npm
- Git

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend/
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the WebSocket server:**
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend/
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

## Usage

### Running Multiple Vehicle Instances

1. **Emergency Vehicle (Ambulance):**
   - Open browser to `http://localhost:3000`
   - Click "I'm an Emergency Vehicle" button
   - Use the emergency signal button when needed

2. **Regular Vehicles:**
   - Open multiple browser tabs/windows to `http://localhost:3000`
   - Each instance represents a different vehicle
   - Vehicles will automatically respond to emergency signals

### Emergency Response Flow

1. Emergency vehicle operator presses the emergency signal button
2. Signal is broadcast to all connected vehicles via WebSocket
3. All non-emergency vehicles simultaneously move to the right lane
4. Emergency vehicle can proceed through the cleared path
5. After emergency passes, vehicles can return to normal positions

## Project Structure

```
assignment-3/
├── backend/                 # Python WebSocket server
│   ├── main.py             # Main server application
│   ├── websocket_handler.py # WebSocket connection management
│   ├── device_manager.py   # Device registration and routing
│   ├── emergency_system.py # Emergency signal handling
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # WebSocket client service
│   │   ├── types/          # TypeScript type definitions
│   │   └── styles/         # CSS styles
│   ├── public/             # Static assets
│   └── package.json        # Node dependencies
└── README.md              # This file
```

## Configuration

### WebSocket Settings
- **Port**: 8765 (default)
- **Protocol**: ws:// (WebSocket)

### Simulation Parameters
- **Number of vehicles**: 6-7
- **Number of lanes**: 3-4
- **Animation speed**: 2-5 seconds for lane changes

## Development

### Adding New Features

1. **Backend changes:**
   - Modify `websocket_handler.py` for connection logic
   - Update `device_manager.py` for device management
   - Extend `emergency_system.py` for new signal types

2. **Frontend changes:**
   - Add new components in `src/components/`
   - Update WebSocket service in `src/services/`
   - Modify vehicle logic in highway simulation

### Testing

Run the test suite:
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test
```

## Deployment

For production deployment:

1. **Backend**: Deploy to cloud server (Heroku, AWS, etc.)
2. **Frontend**: Build and deploy to static hosting (Netlify, Vercel)
3. **WebSocket**: Use secure WebSocket (wss://) in production

## Future Enhancements

- GPS integration for real vehicle positioning
- Mobile app development for actual vehicle integration
- Machine learning for traffic pattern optimization
- Integration with existing emergency response systems
- Multi-city deployment with regional coordination

## Academic Context

This project serves as a proof-of-concept for mobile networking principles, demonstrating:
- Real-time communication protocols
- Distributed system coordination
- Mobile device interaction patterns
- Network topology and message routing

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For questions or issues, please create an issue in the GitHub repository.
