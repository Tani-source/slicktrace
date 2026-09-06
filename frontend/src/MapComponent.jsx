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

// Approximate oil slick polygon centered around 18.95, 72.85
const slickPolygon = [
  [18.96, 72.84],
  [18.96, 72.86],
  [18.94, 72.87],
  [18.93, 72.85],
  [18.94, 72.84],
];

const MapComponent = ({ shipsData }) => {
  // Center roughly off the coast of Mumbai
  const mapCenter = [18.95, 72.85];

  return (
    <MapContainer center={mapCenter} zoom={11} className="leaflet-container">
      {/* Dark theme tile layer for premium aesthetic */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      />

      {/* Static Black Polygon for Zenodo Oil Slick Inference */}
      <Polygon
        positions={slickPolygon}
        pathOptions={{ color: '#000000', fillColor: '#000000', fillOpacity: 0.7, weight: 2 }}
      >
        <Popup>
           <div style={{ color: '#1e293b' }}>
              <strong>Zenodo Inference</strong><br/>
              Detected Oil Slick
           </div>
        </Popup>
      </Polygon>

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
