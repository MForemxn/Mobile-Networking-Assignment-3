import React, { useState } from 'react';
import './LoginPage.css';

const LoginPage = ({ onJoin }) => {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [isJoining, setIsJoining] = useState(false);

  const handleJoin = async (e) => {
    e.preventDefault();
    if (!code.trim() || !name.trim()) return;
    
    setIsJoining(true);
    
    // Simulate a brief loading state
    await new Promise(resolve => setTimeout(resolve, 500));
    
    onJoin(code.trim(), name.trim());
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="logo">
          <div className="logo-icon">🚗</div>
          <h1>C-V2X Demo</h1>
        </div>
        
        <h2>Enter the code to join</h2>
        <p className="subtitle">It's on the screen in front of you.</p>
        
        <form onSubmit={handleJoin} className="login-form">
          <div className="input-group">
            <input
              type="text"
              placeholder="1234 5678"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="code-input"
              maxLength="9"
              required
            />
          </div>
          
          <div className="input-group">
            <input
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="name-input"
              maxLength="20"
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="join-button"
            disabled={isJoining || !code.trim() || !name.trim()}
          >
            {isJoining ? 'Joining...' : 'Join'}
          </button>
        </form>
        
        <div className="demo-info">
          <p>🎓 Interactive C-V2X Emergency Vehicle Demo</p>
          <p>📡 Real LoRa radio communication</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
