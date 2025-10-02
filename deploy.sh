#!/bin/bash

# Emergency Vehicle Communication System - Deployment Script
# This script sets up and runs the complete system for production or demo

set -e  # Exit on any error

echo "🚀 Emergency Vehicle Communication System Deployment"
echo "=================================================="

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ Node.js/npm is required but not installed."; exit 1; }

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p frontend/build

# Backend setup
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Go back to root directory
cd ..

# Frontend setup
echo "⚛️  Setting up frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Build the frontend for production
echo "Building frontend for production..."
npm run build

# Go back to root directory
cd ..

# Create startup script
cat > start_system.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Emergency Vehicle Communication System"
echo "================================================="

# Start backend server in background
echo "🔧 Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

echo "✅ Backend server started (PID: $BACKEND_PID)"

# Serve frontend
echo "⚛️  Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Frontend server started (PID: $FRONTEND_PID)"

# Wait for both processes
echo "📊 System is running!"
echo "   Backend: http://localhost:8765"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
EOF

chmod +x start_system.sh

# Create systemd service file (optional, for Linux servers)
cat > emergency-vehicle.service << EOF
[Unit]
Description=Emergency Vehicle Communication System
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/start_system.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "Quick Start:"
echo "  1. Run: ./start_system.sh"
echo "  2. Open: http://localhost:3000"
echo "  3. Connect multiple browser tabs as different vehicles"
echo ""
echo "Production Deployment:"
echo "  - Copy files to your server"
echo "  - Run: sudo cp emergency-vehicle.service /etc/systemd/system/"
echo "  - Run: sudo systemctl enable emergency-vehicle"
echo "  - Run: sudo systemctl start emergency-vehicle"
echo ""
echo "Testing:"
echo "  - Run: python test_full_system.py"
echo ""
echo "📚 See README.md for detailed documentation"
