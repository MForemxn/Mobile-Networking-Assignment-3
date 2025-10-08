import React, { useState, useEffect, useCallback } from 'react';
import websocketService from './services/websocketService';

/*
  Traffic Grid Simulation - C-V2X Emergency Signal Preemption
  
  Demonstrates how traffic lights respond to C-V2X emergency broadcasts
  by creating a "green wave" for the ambulance path
  
  Features:
  - Large grid of intersections (e.g., 5x5 = 25 traffic lights)
  - Ambulance controlled by host computer
  - Traffic lights change to green on ambulance's path
  - All students see the same synchronized view (Menti-style)
  - Emergency signal triggers coordinated light changes
*/

const GRID_SIZE = 5;  // 5x5 grid = 25 intersections
const CELL_SIZE = 120;  // Size of each intersection cell in pixels

function TrafficGrid() {
  const [isConnected, setIsConnected] = useState(false);
  const [emergencyActive, setEmergencyActive] = useState(false);
  const [ambulancePos, setAmbulancePos] = useState({ x: 0, y: 2 });  // Start at left, middle
  const [ambulanceDirection, setAmbulanceDirection] = useState('right');
  const [trafficLights, setTrafficLights] = useState({});
  const [viewerCount, setViewerCount] = useState(0);

  // Initialize traffic lights
  useEffect(() => {
    const lights = {};
    for (let x = 0; x < GRID_SIZE; x++) {
      for (let y = 0; y < GRID_SIZE; y++) {
        const key = `${x},${y}`;
        lights[key] = {
          nsLight: Math.random() > 0.5 ? 'green' : 'red',  // North-South
          ewLight: Math.random() > 0.5 ? 'green' : 'red',  // East-West
        };
      }
    }
    setTrafficLights(lights);

    // Cycle traffic lights periodically
    const interval = setInterval(() => {
      setTrafficLights(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(key => {
          if (!emergencyActive) {
            // Normal operation: alternate N-S and E-W
            const light = updated[key];
            if (light.nsLight === 'green') {
              light.nsLight = 'yellow';
            } else if (light.nsLight === 'yellow') {
              light.nsLight = 'red';
              light.ewLight = 'green';
            } else if (light.ewLight === 'green') {
              light.ewLight = 'yellow';
            } else if (light.ewLight === 'yellow') {
              light.ewLight = 'red';
              light.nsLight = 'green';
            }
          }
        });
        return updated;
      });
    }, 3000);  // Change every 3 seconds

    return () => clearInterval(interval);
  }, [emergencyActive]);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data) => {
    switch (data.type) {
      case 'system_state':
        setViewerCount(Object.keys(data.devices || {}).length);
        break;

      case 'emergency_takeover':
      case 'emergency_signal':
        setEmergencyActive(true);
        console.log('🚨 Emergency detected - activating signal preemption');
        break;

      case 'emergency_cleared':
        setEmergencyActive(false);
        console.log('🟢 Emergency cleared - resuming normal operation');
        break;

      case 'ambulance_position':
        // Host controls ambulance position
        setAmbulancePos(data.position);
        setAmbulanceDirection(data.direction);
        greenWaveForAmbulance(data.position, data.direction);
        break;

      default:
        break;
    }
  }, []);

  // Initialize WebSocket
  useEffect(() => {
    const handleConnected = () => setIsConnected(true);
    const handleDisconnected = () => setIsConnected(false);

    websocketService.addEventListener('connected', handleConnected);
    websocketService.addEventListener('disconnected', handleDisconnected);
    websocketService.addEventListener('systemState', handleWebSocketMessage);
    websocketService.addEventListener('emergencySignal', handleWebSocketMessage);
    websocketService.addEventListener('emergencyTakeover', handleWebSocketMessage);
    websocketService.addEventListener('emergencyCleared', handleWebSocketMessage);

    if (!websocketService.isConnected) {
      websocketService.connect();
    } else {
      setIsConnected(true);
    }

    return () => {
      websocketService.removeEventListener('connected', handleConnected);
      websocketService.removeEventListener('disconnected', handleDisconnected);
      websocketService.removeEventListener('systemState', handleWebSocketMessage);
      websocketService.removeEventListener('emergencySignal', handleWebSocketMessage);
      websocketService.removeEventListener('emergencyTakeover', handleWebSocketMessage);
      websocketService.removeEventListener('emergencyCleared', handleWebSocketMessage);
    };
  }, [handleWebSocketMessage]);

  // Create green wave for ambulance
  const greenWaveForAmbulance = (pos, direction) => {
    setTrafficLights(prev => {
      const updated = { ...prev };
      
      // Make current intersection green
      const currentKey = `${pos.x},${pos.y}`;
      if (updated[currentKey]) {
        if (direction === 'right' || direction === 'left') {
          updated[currentKey].ewLight = 'green';
          updated[currentKey].nsLight = 'red';
        } else {
          updated[currentKey].nsLight = 'green';
          updated[currentKey].ewLight = 'red';
        }
      }
      
      // Preempt next 2 intersections ahead
      for (let i = 1; i <= 2; i++) {
        let nextKey;
        if (direction === 'right') nextKey = `${pos.x + i},${pos.y}`;
        else if (direction === 'left') nextKey = `${pos.x - i},${pos.y}`;
        else if (direction === 'down') nextKey = `${pos.x},${pos.y + i}`;
        else if (direction === 'up') nextKey = `${pos.x},${pos.y - i}`;
        
        if (updated[nextKey]) {
          if (direction === 'right' || direction === 'left') {
            updated[nextKey].ewLight = 'green';
            updated[nextKey].nsLight = 'red';
          } else {
            updated[nextKey].nsLight = 'green';
            updated[nextKey].ewLight = 'red';
          }
        }
      }
      
      return updated;
    });
  };

  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h1>🚦 C-V2X Traffic Signal Preemption Demo</h1>
        <div style={{ fontSize: '18px', marginTop: '10px' }}>
          <span style={{ marginRight: '20px' }}>
            👥 Viewers: {viewerCount}
          </span>
          <span style={{ 
            padding: '5px 15px', 
            borderRadius: '20px',
            backgroundColor: emergencyActive ? '#dc3545' : '#28a745',
            color: 'white',
            fontWeight: 'bold'
          }}>
            {emergencyActive ? '🚨 EMERGENCY ACTIVE' : '🟢 NORMAL OPERATION'}
          </span>
        </div>
        <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
          {emergencyActive ? 
            '📡 C-V2X Emergency Signal Received - Creating Green Wave' :
            'Traffic lights operating normally - Waiting for emergency'}
        </div>
      </div>

      {/* Traffic Grid */}
      <div style={{ 
        display: 'inline-block',
        backgroundColor: '#2c3e50',
        padding: '20px',
        borderRadius: '10px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
      }}>
        {Array.from({ length: GRID_SIZE }).map((_, y) => (
          <div key={y} style={{ display: 'flex' }}>
            {Array.from({ length: GRID_SIZE }).map((_, x) => {
              const key = `${x},${y}`;
              const light = trafficLights[key] || { nsLight: 'red', ewLight: 'red' };
              const hasAmbulance = ambulancePos.x === x && ambulancePos.y === y;
              
              return (
                <div
                  key={key}
                  style={{
                    width: `${CELL_SIZE}px`,
                    height: `${CELL_SIZE}px`,
                    backgroundColor: '#34495e',
                    border: '2px solid #1a252f',
                    position: 'relative',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  {/* Roads */}
                  <div style={{
                    position: 'absolute',
                    width: '30%',
                    height: '100%',
                    backgroundColor: '#444',
                    left: '35%'
                  }} />
                  <div style={{
                    position: 'absolute',
                    width: '100%',
                    height: '30%',
                    backgroundColor: '#444',
                    top: '35%'
                  }} />

                  {/* Traffic Lights */}
                  <div style={{ position: 'absolute', zIndex: 10 }}>
                    {/* North-South Light */}
                    <div style={{
                      position: 'absolute',
                      top: '-40px',
                      left: '-5px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '2px'
                    }}>
                      <div style={{
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        backgroundColor: light.nsLight === 'green' ? '#00ff00' : '#003300',
                        boxShadow: light.nsLight === 'green' ? '0 0 10px #00ff00' : 'none'
                      }} />
                      <div style={{
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        backgroundColor: light.nsLight === 'yellow' ? '#ffff00' : '#333300',
                        boxShadow: light.nsLight === 'yellow' ? '0 0 10px #ffff00' : 'none'
                      }} />
                      <div style={{
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        backgroundColor: light.nsLight === 'red' ? '#ff0000' : '#330000',
                        boxShadow: light.nsLight === 'red' ? '0 0 10px #ff0000' : 'none'
                      }} />
                    </div>

                    {/* East-West Light */}
                    <div style={{
                      position: 'absolute',
                      top: '-5px',
                      left: '20px',
                      display: 'flex',
                      gap: '2px'
                    }}>
                      <div style={{
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        backgroundColor: light.ewLight === 'green' ? '#00ff00' : '#003300',
                        boxShadow: light.ewLight === 'green' ? '0 0 10px #00ff00' : 'none'
                      }} />
                      <div style={{
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        backgroundColor: light.ewLight === 'yellow' ? '#ffff00' : '#333300',
                        boxShadow: light.ewLight === 'yellow' ? '0 0 10px #ffff00' : 'none'
                      }} />
                      <div style={{
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        backgroundColor: light.ewLight === 'red' ? '#ff0000' : '#330000',
                        boxShadow: light.ewLight === 'red' ? '0 0 10px #ff0000' : 'none'
                      }} />
                    </div>
                  </div>

                  {/* Ambulance */}
                  {hasAmbulance && (
                    <div style={{
                      position: 'absolute',
                      fontSize: '40px',
                      zIndex: 20,
                      animation: emergencyActive ? 'pulse 1s infinite' : 'none',
                      filter: emergencyActive ? 'drop-shadow(0 0 10px red)' : 'none'
                    }}>
                      🚑
                    </div>
                  )}
                  
                  {/* Grid coordinates (for debugging) */}
                  <div style={{
                    position: 'absolute',
                    bottom: '2px',
                    right: '2px',
                    fontSize: '8px',
                    color: '#666'
                  }}>
                    {x},{y}
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div style={{ marginTop: '20px', fontSize: '14px' }}>
        <h3>How It Works:</h3>
        <ul style={{ lineHeight: '1.8' }}>
          <li>🚦 <strong>Normal Mode:</strong> Traffic lights cycle randomly (red → green → yellow)</li>
          <li>🚨 <strong>Emergency Mode:</strong> When LoRa signal detected, lights turn green on ambulance path</li>
          <li>📡 <strong>C-V2X Signal:</strong> Emergency vehicle broadcasts position & route via LoRa</li>
          <li>🎮 <strong>Host Controls:</strong> Instructor controls ambulance path using arrow keys or interface</li>
          <li>👥 <strong>Synchronized View:</strong> All {viewerCount} viewers see the same traffic grid in real-time</li>
        </ul>
      </div>

      {/* Emergency Indicator */}
      {emergencyActive && (
        <div style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          backgroundColor: 'rgba(220, 53, 69, 0.9)',
          color: 'white',
          padding: '20px 40px',
          borderRadius: '10px',
          fontSize: '24px',
          fontWeight: 'bold',
          zIndex: 1000,
          boxShadow: '0 0 20px rgba(220, 53, 69, 0.8)',
          animation: 'pulse 1s infinite'
        }}>
          🚨 EMERGENCY VEHICLE APPROACHING 🚨
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.05); }
        }
      `}</style>
    </div>
  );
}

export default TrafficGrid;

