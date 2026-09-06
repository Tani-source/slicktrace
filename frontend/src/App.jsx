import React, { useState, useEffect } from 'react';
import MapComponent from './MapComponent';
import { Ship } from 'lucide-react';
import './App.css';

function App() {
  const [shipsData, setShipsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/ships')
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch data");
        return res.json();
      })
      .then(data => {
        setShipsData(data.ships);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError("Failed to load ship data.");
        setLoading(false);
      });
  }, []);

  const totalShips = shipsData ? shipsData.length : 0;
  const darkShips = shipsData ? shipsData.filter(s => s.is_dark_ship).length : 0;

  return (
    <div className="app-container">
      <header className="header glass">
        <h1 className="title">
          <Ship /> SlickTrace Dashboard
        </h1>
        <div className="stats">
          <div className="stat-item">
            <span className="stat-value">{totalShips}</span>
            <span className="stat-label">Tracked Vessels</span>
          </div>
          <div className="stat-item">
            <span className="stat-value danger">{darkShips}</span>
            <span className="stat-label">Anomalies Detected</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="map-wrapper glass">
          {loading && <div className="loading">Initializing Satellite Data...</div>}
          {error && <div className="error">{error}</div>}
          {!loading && !error && shipsData && <MapComponent shipsData={shipsData} />}
        </div>
      </main>
    </div>
  );
}

export default App;
