import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import TrafficGrid from './TrafficGrid';

// Check URL parameter for demo mode
const urlParams = new URLSearchParams(window.location.search);
const demoMode = urlParams.get('mode') || 'highway';  // 'highway' or 'traffic'

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    {demoMode === 'traffic' ? <TrafficGrid /> : <App />}
  </React.StrictMode>
);
