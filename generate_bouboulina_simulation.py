import json
import os
import numpy as np
from datetime import datetime, timedelta
from shapely.geometry import Polygon, LineString

def generate_simulation():
    # 1. Define the Timeframe and Region
    start_time = datetime(2019, 7, 26, 0, 0, 0)
    end_time = datetime(2019, 7, 30, 23, 55, 0)
    
    # 5-minute intervals
    num_steps = int((end_time - start_time).total_seconds() / 300)
    timestamps = [start_time + timedelta(minutes=5 * i) for i in range(num_steps)]
    
    features = []

    # 2. Kinematic Vector Modeling for the Oil Slick Polygon (Fallback)
    # The slick drifted off the coast of Paraiba (Lat -7.0, Lon -34.0)
    # Simulating a generalized SAR polygon representing the slick size and drift
    slick_polygon = Polygon([
        [-33.8, -6.8],
        [-34.1, -6.9],
        [-34.2, -7.1],
        [-33.9, -7.2],
        [-33.8, -6.8]
    ])
    
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[list(coord) for coord in slick_polygon.exterior.coords]]
        },
        "properties": {
            "type": "oil_slick",
            "description": "2019 Brazil SAR Satellite Oil Slick Detection"
        }
    })

    # 3. Generate Bouboulina Track (Venezuela to Malaysia via South Africa)
    # Passing through the region (Lat -7.0, Lon -34.0) around July 28.
    # Start: ~ Lat 5.0, Lon -45.0 (July 26)
    # End: ~ Lat -20.0, Lon -25.0 (July 30)
    bouboulina_mmsi = 241439000
    start_lat_b, start_lon_b = 5.0, -45.0
    end_lat_b, end_lon_b = -20.0, -25.0
    
    v_lat_b = (end_lat_b - start_lat_b) / num_steps
    v_lon_b = (end_lon_b - start_lon_b) / num_steps
    
    # 6-hour data gap (72 steps) on July 28th
    # July 28th 00:00 is exactly 48 hours in (576 steps)
    gap_start = 576 + int((12 * 60) / 5) # Gap around 12:00 PM on July 28
    gap_end = gap_start + 72
    
    bouboulina_coords = []
    bouboulina_times = []
    
    curr_lat, curr_lon = start_lat_b, start_lon_b
    for step, ts in enumerate(timestamps):
        if gap_start <= step < gap_end:
            # Blackout - no pings emitted
            curr_lat += v_lat_b
            curr_lon += v_lon_b
            continue
            
        bouboulina_coords.append([curr_lon, curr_lat])
        bouboulina_times.append(ts.isoformat())
        curr_lat += v_lat_b
        curr_lon += v_lon_b

    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": bouboulina_coords
        },
        "properties": {
            "type": "vessel",
            "mmsi": bouboulina_mmsi,
            "name": "Bouboulina",
            "timestamps": bouboulina_times
        }
    })

    # 4. Generate 3 Decoy Vessels
    np.random.seed(2019)
    for i in range(1, 4):
        mmsi = 100000000 + i
        # Random start and end points in the general Atlantic bounding box
        s_lat = np.random.uniform(0.0, -10.0)
        s_lon = np.random.uniform(-40.0, -30.0)
        
        e_lat = s_lat + np.random.uniform(-10.0, 10.0)
        e_lon = s_lon + np.random.uniform(-10.0, 10.0)
        
        v_lat_d = (e_lat - s_lat) / num_steps
        v_lon_d = (e_lon - s_lon) / num_steps
        
        d_coords = []
        d_times = []
        
        c_lat, c_lon = s_lat, s_lon
        for ts in timestamps:
            # Continuous pings (no blackout)
            d_coords.append([c_lon, c_lat])
            d_times.append(ts.isoformat())
            c_lat += v_lat_d
            c_lon += v_lon_d
            
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": d_coords
            },
            "properties": {
                "type": "vessel",
                "mmsi": mmsi,
                "name": f"Decoy_Vessel_{i}",
                "timestamps": d_times
            }
        })

    # 5. Export to GeoJSON
    geojson_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    os.makedirs('data', exist_ok=True)
    output_path = 'data/bouboulina_simulation.geojson'
    
    with open(output_path, 'w') as f:
        json.dump(geojson_collection, f, indent=2)
        
    print(f"Historical simulation successfully generated at {output_path}")

if __name__ == "__main__":
    generate_simulation()
