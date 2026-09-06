import React, { useState, useEffect } from 'react';
import MapComponent from './MapComponent';
import { Ship, Download } from 'lucide-react';
import './App.css';

function App() {
  const [shipsData, setShipsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
    fetch(`${apiUrl}/vessels`)
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

  const exportDossier = () => {
    if (!shipsData || shipsData.length === 0) return;
    const topSuspect = shipsData[0];
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(topSuspect, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `forensic_dossier_MMSI_${topSuspect.mmsi}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <div className="app-container">
      <header className="header glass">
        <div>
          <h1 className="title">
            <Ship /> SlickTrace Dashboard
          </h1>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8', marginLeft: '2.2rem' }}>
            Case Study: 2019 Brazil Coast Mystery Oil Spill ("Bouboulina")
          </span>
        </div>
        <div className="stats">
          <div className="stat-item">
            <span className="stat-value">{totalShips}</span>
            <span className="stat-label">Tracked Vessels</span>
          </div>
          <div className="stat-item">
            <span className="stat-value danger">{darkShips}</span>
            <span className="stat-label">Anomalies Flagged</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="side-panel glass">
          <h2>Ranked Suspects</h2>
          <button className="export-btn" onClick={exportDossier}>
            <Download size={18} /> Export Forensic Dossier
          </button>
          
          <div className="suspect-list">
            {shipsData && shipsData.map((ship, index) => (
              <div key={ship.mmsi} className={`suspect-card ${ship.is_dark_ship ? 'high-risk' : ''}`}>
                <div className="suspect-title">
                  <span>#{index + 1} {ship.vessel_name || `MMSI: ${ship.mmsi}`}</span>
                  {ship.is_dark_ship && <span className="danger">⚠ ALERT</span>}
                </div>
                <div className="suspect-score" style={{ fontSize: '0.75rem', color: '#64748b' }}>MMSI: {ship.mmsi}</div>
                <div className="suspect-score">Confidence Score: {(ship.suspect_confidence_score * 100).toFixed(1)}%</div>
                <div className="suspect-score">Max Blackout Gap: {ship.max_gap_minutes.toFixed(1)}m</div>
                <div className="suspect-score">Slick Proximity: {ship.min_distance_to_slick.toFixed(3)}°</div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="map-wrapper glass">
          {loading && <div className="loading">Fetching Vessel Data...</div>}
          {error && <div className="error">{error}</div>}
          {!loading && !error && shipsData && <MapComponent shipsData={shipsData} />}
        </div>
      </main>
    </div>
  );
}

export default App;
