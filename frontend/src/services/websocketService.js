/**
 * WebSocket service for emergency vehicle communication
 */

class WebSocketService {
  constructor() {
    this.websocket = null;
    this._isConnected = false;
    this.deviceId = null;
    this.vehicleType = null;
    this.isEmergencyVehicle = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.listeners = new Map();
  }

  /**
   * Connect to the WebSocket server
   */
  connect(name, color, role = 'student') {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.hostname}:8765`;

      console.log('Connecting to WebSocket:', wsUrl);
      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('WebSocket connected');
        this._isConnected = true;
        this.reconnectAttempts = 0;
        this.emit('connected');

        // Request current system state
        this.send({ type: 'get_system_state' });

        // Send user registration (name/color)
        if (name) {
          this.send({ type: 'register_user', name, color, role });
        }
      };

      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.websocket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this._isConnected = false;
        this.emit('disconnected', { code: event.code, reason: event.reason });

        if (event.code !== 1000) { // Not a normal closure
          this.attemptReconnect();
        }
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };

    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.emit('error', error);
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect() {
    if (this.websocket) {
      this.websocket.close(1000, 'Client disconnect');
      this.websocket = null;
    }
    this._isConnected = false;
  }

  /**
   * Send a message through the WebSocket
   */
  send(data) {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(data));
      return true;
    }
    console.warn('Cannot send message: WebSocket not connected');
    return false;
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(data) {
    switch (data.type) {
      case 'welcome':
        this.deviceId = data.device_id;
        this.vehicleType = data.vehicle_type;
        this.isEmergencyVehicle = data.vehicle_type === 'emergency_vehicle';
        this.emit('welcome', data);
        break;

      case 'system_state':
        this.emit('systemState', data);
        break;

      case 'roster_update':
        this.emit('rosterUpdate', data);
        break;

      case 'position_update':
        this.emit('positionUpdate', data);
        break;

      case 'lane_change':
        this.emit('laneChange', data);
        break;

      case 'emergency_signal':
        this.emit('emergencySignal', data);
        break;

      case 'emergency_cleared':
        this.emit('emergencyCleared', data);
        break;

      case 'pong':
        this.emit('pong', data);
        break;

      default:
        this.emit('message', data);
    }
  }

  /**
   * Attempt to reconnect to the server
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    setTimeout(() => {
      this.connect();
    }, this.reconnectDelay);
  }

  /**
   * Send emergency signal
   */
  sendEmergencySignal() {
    if (this.isEmergencyVehicle) {
      return this.send({
        type: 'register_emergency',
        device_id: this.deviceId
      });
    }
    console.warn('Cannot send emergency signal: Not an emergency vehicle');
    return false;
  }

  /**
   * Clear emergency signal
   */
  clearEmergencySignal() {
    if (this.isEmergencyVehicle) {
      return this.send({
        type: 'clear_emergency',
        device_id: this.deviceId
      });
    }
    console.warn('Cannot clear emergency signal: Not an emergency vehicle');
    return false;
  }

  /**
   * Send position update
   */
  sendPositionUpdate(position) {
    return this.send({
      type: 'position_update',
      device_id: this.deviceId,
      position: position
    });
  }

  /**
   * Send lane change request
   */
  sendLaneChange(newLane, reason = 'manual') {
    return this.send({
      type: 'lane_change',
      device_id: this.deviceId,
      new_lane: newLane,
      reason: reason
    });
  }

  /**
   * Send ping to server
   */
  ping() {
    return this.send({ type: 'ping' });
  }

  /**
   * Add event listener
   */
  addEventListener(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  /**
   * Remove event listener
   */
  removeEventListener(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Emit event to listeners
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in event listener:', error);
        }
      });
    }
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      isConnected: this.websocket && this.websocket.readyState === WebSocket.OPEN,
      deviceId: this.deviceId,
      vehicleType: this.vehicleType,
      isEmergencyVehicle: this.isEmergencyVehicle,
      reconnectAttempts: this.reconnectAttempts
    };
  }

  /**
   * Check if WebSocket is connected
   */
  get isConnected() {
    return this._isConnected;
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
