import React from 'react';
import { MapContainer, TileLayer, Polygon, Polyline, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default Leaflet icon paths
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const MapComponent = ({ simulationData, suspectsData }) => {
  // Center off the coast of Paraíba, Brazil
  const mapCenter = [-10.0, -32.0];

  // Extract the oil slick feature directly from GeoJSON
  let slickPositions = [];
  let slickCentroid = null;
  if (simulationData && simulationData.features) {
      const slickFeature = simulationData.features.find(f => f.properties.type === 'oil_slick');
      if (slickFeature && slickFeature.geometry.type === 'Polygon') {
          // Leaflet expects [lat, lon] but GeoJSON is [lon, lat]
          const coords = slickFeature.geometry.coordinates[0];
          slickPositions = coords.map(coord => [coord[1], coord[0]]);
          
          if (slickPositions.length > 0) {
              // Calculate rough centroid for the drift line origin
              const lats = slickPositions.map(p => p[0]);
              const lons = slickPositions.map(p => p[1]);
              slickCentroid = [
                  (Math.max(...lats) + Math.min(...lats)) / 2,
                  (Math.max(...lons) + Math.min(...lons)) / 2
              ];
          }
      }
  }

  // Create a map of high-risk mmsis for quick lookup
  const highRiskMmsis = new Set(
      suspectsData?.filter(s => s.is_dark_ship).map(s => s.mmsi) || []
  );

  return (
    <MapContainer center={mapCenter} zoom={6} className="leaflet-container">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
      />

      {/* Dynamic Polygon for GeoJSON Oil Slick */}
      {slickPositions.length > 0 && (
          <Polygon
            positions={slickPositions}
            pathOptions={{ color: '#000000', fillColor: '#000000', fillOpacity: 0.7, weight: 2 }}
          >
            <Popup>
               <div style={{ color: '#1e293b' }}>
                  <strong>SAR Inference</strong><br/>
                  Detected Oil Slick
               </div>
            </Popup>
          </Polygon>
      )}

      {/* Backward Drift Path */}
      {slickCentroid && (
          <Polyline
            positions={[
              slickCentroid,
              [slickCentroid[0] - 2.0, slickCentroid[1] + 2.0]  // Southeast drift origin approximation
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
      )}

      {/* Ship Tracks from GeoJSON */}
      {simulationData && simulationData.features && simulationData.features.map((feature, idx) => {
          if (feature.properties.type !== 'vessel') return null;
          
          const mmsi = feature.properties.mmsi;
          const isHighRisk = highRiskMmsis.has(mmsi);
          const coords = feature.geometry.coordinates;
          const positions = coords.map(c => [c[1], c[0]]); // GeoJSON lon, lat -> Leaflet lat, lon
          
          return (
             <Polyline
               key={`track-${idx}`}
               positions={positions}
               pathOptions={{
                 color: isHighRisk ? '#ef4444' : '#3b82f6',
                 weight: isHighRisk ? 4 : 2,
                 opacity: isHighRisk ? 1.0 : 0.6
               }}
             >
               <Popup>
                 <div style={{ color: '#1e293b' }}>
                   <strong>MMSI: {mmsi}</strong><br/>
                   Name: {feature.properties.name}<br/>
                   {isHighRisk && <span style={{color: 'red'}}>HIGH RISK ANOMALY</span>}
                 </div>
               </Popup>
             </Polyline>
          );
      })}
    </MapContainer>
  );
};

export default MapComponent;
