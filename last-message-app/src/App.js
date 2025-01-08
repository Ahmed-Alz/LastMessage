// src/App.js
import React, { useState } from 'react';
import './App.css'; // Import the CSS file
import beaconImage from './assets/beaconImage.png';  // Relative path


function App() {
  // State for capturing user input
  const [userInfo, setUserInfo] = useState({
    username: '',
    userEmail: '',
    recipientEmail: '',
    messageBody: '',
    checkInPeriod: 24, // in hours
    gracePeriod: 30, // in minutes
    isWarningEnabled: false,
    warningDuration: 5, // in minutes
  });

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setUserInfo((prevState) => ({
      ...prevState,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    // Mock sending data to the backend
    console.log('User Info:', userInfo);
    alert('Form submitted!');
  };

  return (
    <div className="App">
      <h1>Last Message</h1>
      {/* <h2>Settings</h2> */}
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Username:
            <input
              type="text"
              name="username"
              value={userInfo.username}
              onChange={handleChange}
              required
            />
          </label>
        </div>

        <div>
          <label>
            Your Email:
            <input
              type="email"
              name="userEmail"
              value={userInfo.userEmail}
              onChange={handleChange}
              required
            />
          </label>
        </div>

        <div>
          <label>
            Recipient's Email:
            <input
              type="email"
              name="recipientEmail"
              value={userInfo.recipientEmail}
              onChange={handleChange}
              required
            />
          </label>
        </div>

        <div>
          <label>
            Last Message:
            <textarea
              name="messageBody"
              value={userInfo.messageBody}
              onChange={handleChange}
              required
            />
          </label>
        </div>

        <div>
          <label>
            Check-in Period (in hours):
            <input
              type="number"
              name="checkInPeriod"
              value={userInfo.checkInPeriod}
              onChange={handleChange}
              min="1"
              max="72"
              required
            />
          </label>
        </div>

        <div>
          <label>
            Grace Period (in hours):
            <input
              type="number"
              name="gracePeriod"
              value={userInfo.gracePeriod}
              onChange={handleChange}
              min="1"
              max="120"
              required
            />
          </label>
        </div>

        <div>
          <label>
            Enable Reminder:
            <input
              type="checkbox"
              name="isWarningEnabled"
              checked={userInfo.isWarningEnabled}
              onChange={handleChange}
              style={{ marginBottom: '5px' }}  // Smaller margin for this checkbox
            />
          </label>
        </div>

        {userInfo.isWarningEnabled && (
          <div>
            <label>
              Warning Duration (in minutes):
              <input
                type="number"
                name="warningDuration"
                value={userInfo.warningDuration}
                onChange={handleChange}
                min="1"
                max="120"
              />
            </label>
          </div>
        )}

        <button type="submit">Save Settings</button>
      </form>
      {/* Add the beacon image at the bottom */}
      <img
        src={beaconImage}
        alt="Beacon"
        style={{ display: 'block', margin: '20px auto', width: '140px' }}
      />
      <h2>© LL 2025</h2>
    </div>
  );
}

export default App;
