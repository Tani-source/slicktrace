import React from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, Polygon } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { AlertTriangle } from 'lucide-react';
import ReactDOMServer from 'react-dom/server';

// Fix default icon issue with webpack/vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom alert icon for dark ships
const alertIconHtml = ReactDOMServer.renderToString(
  <div style={{ color: '#ef4444', filter: 'drop-shadow(0px 2px 2px rgba(0,0,0,0.5))' }}>
    <AlertTriangle size={32} fill="#ef4444" color="white" />
  </div>
);

const alertIcon = new L.DivIcon({
  html: alertIconHtml,
  className: 'custom-alert-icon',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

// Sentinel-1 Oil slick detection polygon centered around -7.2, -33.8 (~700km off Paraíba)
const slickPolygon = [
  [-7.15, -33.85],
  [-7.15, -33.75],
  [-7.25, -33.70],
  [-7.28, -33.82],
  [-7.22, -33.88],
];

const MapComponent = ({ shipsData }) => {
  // Center off the coast of Paraíba, Brazil (NE Coast)
  const mapCenter = [-9.0, -31.5];

  return (
    <MapContainer center={mapCenter} zoom={7} className="leaflet-container">
      {/* Standard OSM tile layer */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
      />

      {/* Sentinel-1 SAR Polygon for Bouboulina Oil Spill Detection */}
      <Polygon
        positions={slickPolygon}
        pathOptions={{ color: '#ef4444', fillColor: '#1e1e24', fillOpacity: 0.85, weight: 2 }}
      >
        <Popup>
           <div style={{ color: '#1e293b' }}>
              <strong>Sentinel-1 SAR Detection</strong><br/>
              2019 Brazil Coast Slick Inference<br/>
              Location: ~700 km off Paraíba
           </div>
        </Popup>
      </Polygon>

      {/* Forward Drift Simulation Trajectory Vector */}
      <Polyline
        positions={[
          [-7.20, -33.80], // Slick origin off Paraíba
          [-7.00, -34.80]  // Forward drift towards Brazilian coast
        ]}
        pathOptions={{ color: '#f59e0b', weight: 3, dashArray: '8, 8' }}
      >
        <Popup>
           <div style={{ color: '#1e293b' }}>
              <strong>OpenDrift Hydrodynamic Model</strong><br/>
              CMEMS + ERA5 Forward Drift Trajectory
           </div>
        </Popup>
      </Polyline>

      {/* Ship Tracks */}
      {shipsData.map((ship) => {
        const positions = ship.track.map(t => [t.lat, t.lon]);
        const isDark = ship.is_dark_ship;
        const color = isDark ? '#ef4444' : '#38bdf8'; // Red for dark ships, Cyan for normal

        return (
          <React.Fragment key={ship.mmsi}>
            <Polyline
              positions={positions}
              pathOptions={{ color, weight: isDark ? 4 : 2, opacity: 0.85 }}
            />
            {isDark && (
              <Marker position={positions[Math.floor(positions.length / 2)]} icon={alertIcon}>
                <Popup>
                  <div style={{ color: '#1e293b' }}>
                    <strong>🚨 Dark Ship Suspect</strong><br/>
                    Vessel: {ship.vessel_name || `MMSI ${ship.mmsi}`}<br/>
                    AIS Blackout Gap: {ship.max_gap_minutes.toFixed(1)} mins<br/>
                    Risk Score: {(ship.suspect_confidence_score * 100).toFixed(1)}%
                  </div>
                </Popup>
              </Marker>
            )}
          </React.Fragment>
        );
      })}
    </MapContainer>
  );
};

export default MapComponent;
