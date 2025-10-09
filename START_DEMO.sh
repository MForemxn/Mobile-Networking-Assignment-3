#!/bin/bash
# Quick start script for C-V2X Emergency Vehicle Demo

echo "╔════════════════════════════════════════════════╗"
echo "║  🚀 Starting C-V2X Emergency Vehicle Demo     ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Kill any existing services
echo "🧹 Cleaning up existing services..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8765 | xargs kill -9 2>/dev/null
pkill -f test_emergency_simulator 2>/dev/null
sleep 2

# Start backend
echo "🔧 Starting backend server..."
cd backend
source venv/bin/activate
python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 5

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║           ✅ ALL SERVICES RUNNING!            ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "🎓 ADMIN URL (Your Screen - Ambulance):"
echo "   http://localhost:3000?admin=1"
echo ""
echo "👥 STUDENT URL (Share with class):"
echo "   http://localhost:3000"
echo ""
echo "🌐 Network URL:"
echo "   http://$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}'):3000"
echo ""
echo "📡 Backend: ws://localhost:8765"
echo "⚡ Updates: 2x per second"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f backend/backend.log"
echo "   Frontend: tail -f frontend/frontend.log"
echo ""
echo "🛑 To stop: kill $BACKEND_PID $FRONTEND_PID"
echo ""

