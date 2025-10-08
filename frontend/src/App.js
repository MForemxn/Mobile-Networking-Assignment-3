import React, { useState, useEffect, useRef, useCallback } from 'react';
import './index.css';
import websocketService from './services/websocketService';

const VEHICLE_TYPES = {
  regular_car: { name: 'Car', color: 'regular', width: 40, height: 20 },
  truck: { name: 'Truck', color: 'truck', width: 50, height: 20 },
  motorcycle: { name: 'Motorcycle', color: 'motorcycle', width: 30, height: 15 },
  emergency_vehicle: { name: 'Emergency', color: 'emergency', width: 40, height: 20 }
};

const LANES = {
  1: { name: 'Left Lane', y: 0 },
  2: { name: 'Middle Lane', y: 50 },
  3: { name: 'Right Lane', y: 100 }
};

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [deviceId, setDeviceId] = useState(null);
  const [vehicleType, setVehicleType] = useState(null);
  const [isEmergencyVehicle, setIsEmergencyVehicle] = useState(false);
  const [emergencyActive, setEmergencyActive] = useState(false);
  const [vehicles, setVehicles] = useState({});
  const [connectionError, setConnectionError] = useState(null);
  const [laneChanges, setLaneChanges] = useState({});

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data) => {
    switch (data.type) {
      case 'welcome':
        setDeviceId(data.device_id);
        setVehicleType(data.vehicle_type);
        setIsEmergencyVehicle(data.vehicle_type === 'emergency_vehicle');
        break;

      case 'system_state':
        setVehicles(data.devices || {});
        if (data.emergency_status?.active_emergency_device) {
          setEmergencyActive(true);
        }
        break;

      case 'position_update':
        setVehicles(prev => ({
          ...prev,
          [data.device_id]: {
            ...prev[data.device_id],
            ...data.position
          }
        }));
        break;

      case 'lane_change':
        // Handle lane change animation
        setLaneChanges(prev => ({
          ...prev,
          [data.device_id]: {
            fromLane: data.old_lane,
            toLane: data.new_lane,
            reason: data.reason,
            timestamp: Date.now()
          }
        }));

        // Update vehicle lane after animation
        setTimeout(() => {
          setVehicles(prev => ({
            ...prev,
            [data.device_id]: {
              ...prev[data.device_id],
              current_lane: data.new_lane
            }
          }));
          setLaneChanges(prev => {
            const updated = { ...prev };
            delete updated[data.device_id];
            return updated;
          });
        }, 2000);
        break;

      case 'emergency_signal':
        setEmergencyActive(true);
        console.log('Emergency signal received:', data.message);
        break;

      case 'emergency_cleared':
        setEmergencyActive(false);
        console.log('Emergency cleared');
        break;

      default:
        console.log('Unhandled message type:', data.type);
    }
  }, []);

  // Initialize WebSocket connection and event listeners
  useEffect(() => {
    // Set up event listeners
    const handleConnected = () => {
      setIsConnected(true);
      setConnectionError(null);
    };

    const handleDisconnected = (event) => {
      setIsConnected(false);
      if (event.code !== 1000) {
        setConnectionError('Connection lost. Retrying...');
      }
    };

    const handleError = (error) => {
      setConnectionError('Connection error');
      console.error('WebSocket error:', error);
    };

    const handleMaxReconnectAttemptsReached = () => {
      setConnectionError('Failed to connect to server. Please refresh the page.');
    };

    // Add event listeners
    websocketService.addEventListener('connected', handleConnected);
    websocketService.addEventListener('disconnected', handleDisconnected);
    websocketService.addEventListener('error', handleError);
    websocketService.addEventListener('maxReconnectAttemptsReached', handleMaxReconnectAttemptsReached);
    websocketService.addEventListener('welcome', handleWebSocketMessage);
    websocketService.addEventListener('systemState', handleWebSocketMessage);
    websocketService.addEventListener('positionUpdate', handleWebSocketMessage);
    websocketService.addEventListener('laneChange', handleWebSocketMessage);
    websocketService.addEventListener('emergencySignal', handleWebSocketMessage);
    websocketService.addEventListener('emergencyCleared', handleWebSocketMessage);

    // Initialize connection
    if (!websocketService.isConnected) {
      websocketService.connect();
    } else {
      setIsConnected(true);
    }

    // Cleanup function
    return () => {
      websocketService.removeEventListener('connected', handleConnected);
      websocketService.removeEventListener('disconnected', handleDisconnected);
      websocketService.removeEventListener('error', handleError);
      websocketService.removeEventListener('maxReconnectAttemptsReached', handleMaxReconnectAttemptsReached);
      websocketService.removeEventListener('welcome', handleWebSocketMessage);
      websocketService.removeEventListener('systemState', handleWebSocketMessage);
      websocketService.removeEventListener('positionUpdate', handleWebSocketMessage);
      websocketService.removeEventListener('laneChange', handleWebSocketMessage);
      websocketService.removeEventListener('emergencySignal', handleWebSocketMessage);
      websocketService.removeEventListener('emergencyCleared', handleWebSocketMessage);
    };
  }, [handleWebSocketMessage]);

  // Send emergency signal
  const sendEmergencySignal = () => {
    if (isConnected && isEmergencyVehicle) {
      websocketService.sendEmergencySignal();
      setEmergencyActive(true);
    }
  };

  // Clear emergency signal
  const clearEmergencySignal = () => {
    if (isConnected && isEmergencyVehicle) {
      websocketService.clearEmergencySignal();
      setEmergencyActive(false);
    }
  };

  // Send position update
  const sendPositionUpdate = (position) => {
    if (isConnected && deviceId) {
      websocketService.sendPositionUpdate(position);
    }
  };

  // Get vehicle style based on type and state
  const getVehicleStyle = (vehicle) => {
    const baseStyle = {
      left: `${vehicle.position_x || 0}px`,
      top: `${(vehicle.current_lane - 1) * 50 + 10}px`,
      width: `${VEHICLE_TYPES[vehicle.vehicle_type]?.width || 40}px`,
      height: `${VEHICLE_TYPES[vehicle.vehicle_type]?.height || 20}px`,
    };

    // Add lane changing animation
    if (laneChanges[vehicle.device_id]) {
      const change = laneChanges[vehicle.device_id];
      const progress = Math.min((Date.now() - change.timestamp) / 2000, 1);
      const startY = (change.fromLane - 1) * 50 + 10;
      const endY = (change.toLane - 1) * 50 + 10;
      const currentY = startY + (endY - startY) * progress;

      return {
        ...baseStyle,
        top: `${currentY}px`,
        transform: `scale(${0.8 + progress * 0.2})`,
      };
    }

    return baseStyle;
  };

  const totalVehicles = Object.keys(vehicles).length;
  const emergencyVehicles = Object.values(vehicles).filter(v => v.is_emergency_active).length;

  return (
    <div className="App">
      {/* Connection Status */}
      <div className="connection-status">
        <div className={`status-dot ${isConnected ? 'connected' : ''}`} />
        <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
      </div>

      {/* Vehicle Counter */}
      <div className="vehicle-counter">
        Vehicles: {totalVehicles} | Emergency: {emergencyVehicles}
      </div>

      {/* Control Panel */}
      <div className="control-panel">
        <h3>Vehicle Control</h3>

        <div className={`device-info ${isConnected ? 'connected' : 'disconnected'}`}>
          <div className={`status-badge ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
          <div><strong>Device ID:</strong> {deviceId || 'Not assigned'}</div>
          <div><strong>Vehicle:</strong> {vehicleType ? VEHICLE_TYPES[vehicleType]?.name : 'Unknown'}</div>
        </div>

        {isEmergencyVehicle && (
          <div className="emergency-controls">
            <button
              className={`emergency-button ${emergencyActive ? 'emergency-active' : ''}`}
              onClick={emergencyActive ? clearEmergencySignal : sendEmergencySignal}
              disabled={!isConnected}
            >
              {emergencyActive ? '🛑 Clear Emergency' : '🚨 Activate Emergency'}
            </button>
          </div>
        )}

        {connectionError && (
          <div style={{ color: '#dc3545', fontSize: '12px', marginTop: '10px' }}>
            {connectionError}
          </div>
        )}
      </div>

      {/* Highway Simulation */}
      <div className="highway-container">
        <div className="highway">
          {/* Lane Dividers */}
          {Object.entries(LANES).map(([laneNum, lane]) => (
            <div
              key={laneNum}
              className="lane"
              style={{
                width: `${100 / Object.keys(LANES).length}%`,
                left: `${((laneNum - 1) / Object.keys(LANES).length) * 100}%`
              }}
            />
          ))}

          {/* Vehicles */}
          {Object.entries(vehicles).map(([id, vehicle]) => (
            <div
              key={id}
              className={`vehicle ${VEHICLE_TYPES[vehicle.vehicle_type]?.color || 'regular'} ${laneChanges[id] ? 'lane-changing' : ''}`}
              style={getVehicleStyle(vehicle)}
              title={`${VEHICLE_TYPES[vehicle.vehicle_type]?.name} (${id.substring(0, 8)})`}
            >
              {VEHICLE_TYPES[vehicle.vehicle_type]?.name.substring(0, 2)}
            </div>
          ))}
        </div>
      </div>

      {/* Loading/Error States */}
      {!isConnected && !connectionError && (
        <div className="loading">
          <div className="loading-spinner" />
          <div>Connecting to server...</div>
        </div>
      )}

      {connectionError && (
        <div className="error-message">
          <h3>Connection Error</h3>
          <p>{connectionError}</p>
          <button onClick={() => window.location.reload()} style={{ marginTop: '10px' }}>
            Retry Connection
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
