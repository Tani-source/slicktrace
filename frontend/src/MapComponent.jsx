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

// Approximate oil slick polygon centered around -10.0, -30.0 (Brazil)
const slickPolygon = [
  [-9.9, -30.1],
  [-9.9, -29.9],
  [-10.1, -29.9],
  [-10.2, -30.0],
  [-10.1, -30.1],
];

const MapComponent = ({ shipsData }) => {
  // Center off the coast of Paraíba, Brazil
  const mapCenter = [-10.0, -32.0];

  return (
    <MapContainer center={mapCenter} zoom={7} className="leaflet-container">
      {/* Standard OSM tile layer, dark mode is applied via CSS filter */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
      />

      {/* Static Black Polygon for Zenodo Oil Slick Inference */}
      <Polygon
        positions={slickPolygon}
        pathOptions={{ color: '#000000', fillColor: '#000000', fillOpacity: 0.7, weight: 2 }}
      >
        <Popup>
           <div style={{ color: '#1e293b' }}>
              <strong>Zenodo Inference</strong><br/>
              Detected Oil Slick (Brazil)
           </div>
        </Popup>
      </Polygon>

      {/* Backward Drift Path (Simulating currents carrying oil West/Northwest) */}
      <Polyline
        positions={[
          [-10.0, -30.0], // Slick center
          [-11.0, -28.0]  // Southeast drift origin (since oil drifted NW, origin is SE)
        ]}
        pathOptions={{ color: '#f59e0b', weight: 3, dashArray: '10, 10' }}
      >
        <Popup>
           <div style={{ color: '#1e293b' }}>
              <strong>Backward Drift Path</strong><br/>
              Simulated ocean current origin
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
              pathOptions={{ color, weight: isDark ? 4 : 2, opacity: 0.8 }}
            />
            {isDark && (
              <Marker position={positions[positions.length - 1]} icon={alertIcon}>
                <Popup>
                  <div style={{ color: '#1e293b' }}>
                    <strong>🚨 Dark Ship Detected</strong><br/>
                    MMSI: {ship.mmsi}<br/>
                    Max Gap: {ship.max_gap_minutes.toFixed(1)} mins<br/>
                    Anomaly Score: {ship.anomaly_score}
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
