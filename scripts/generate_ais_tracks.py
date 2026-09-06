import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

def generate_brazil_ais_tracks():
    # July 28-29, 2019 (48 hours)
    start_time = datetime(2019, 7, 28, 0, 0, 0)
    num_steps = 48 * 60 // 5 # 576 steps at 5-min intervals
    timestamps = [start_time + timedelta(minutes=5 * i) for i in range(num_steps)]
    
    csv_records = []
    json_tracks = {}
    
    # -------------------------------------------------------------
    # 1. Target Vessel: Bouboulina (MMSI 240000000)
    # Anchor point: ~700 km off Paraíba, Brazil on July 28-29, 2019
    # Heading SE: start Lat -7.0, Lon -34.0 -> end Lat -12.0, Lon -28.0
    # -------------------------------------------------------------
    bouboulina_mmsi = 240000000
    start_lat_b, start_lon_b = -7.0, -34.0
    end_lat_b, end_lon_b = -12.0, -28.0
    
    v_lat_b = (end_lat_b - start_lat_b) / num_steps
    v_lon_b = (end_lon_b - start_lon_b) / num_steps
    
    # Deliberate 6-hour AIS blackout (72 intervals of 5 mins)
    gap_start = int(num_steps * 0.45) # ~21.6 hours into voyage
    gap_end = gap_start + 72
    
    b_points = []
    curr_lat, curr_lon = start_lat_b, start_lon_b
    
    for step, ts in enumerate(timestamps):
        is_gap = (gap_start <= step < gap_end)
        
        # Calculate speed in knots (~14.5 knots typical crude tanker speed)
        speed_knots = 0.0 if is_gap else 14.5
        course_deg = 130.0 # Southeast direction
        
        point_data = {
            'timestamp': ts.isoformat(),
            'lat': round(curr_lat, 5),
            'lon': round(curr_lon, 5),
            'speed_knots': speed_knots,
            'course_deg': course_deg
        }
        
        if not is_gap:
            csv_records.append({
                'mmsi': bouboulina_mmsi,
                'timestamp': ts.isoformat(),
                'lat': round(curr_lat, 5),
                'lon': round(curr_lon, 5),
                'speed_knots': speed_knots,
                'course_deg': course_deg
            })
            b_points.append(point_data)
            
        curr_lat += v_lat_b
        curr_lon += v_lon_b
        
    json_tracks[str(bouboulina_mmsi)] = {
        'vessel_name': 'Bouboulina',
        'mmsi': bouboulina_mmsi,
        'vessel_type': 'Tanker',
        'track': b_points
    }
    
    # -------------------------------------------------------------
    # 2. Decoy Ships (MMSIs 100000003, 100000004, 100000005)
    # Continuous pings across the same bounding box
    # -------------------------------------------------------------
    np.random.seed(42)
    decoy_names = ['Atlas Sky', 'Ocean Pioneer', 'Pacific Carrier']
    
    for idx, i in enumerate(range(3, 6)):
        mmsi = 100000000 + i
        vessel_name = decoy_names[idx]
        
        start_lat_d = np.random.uniform(-11.0, -7.5)
        start_lon_d = np.random.uniform(-33.5, -29.0)
        
        v_lat_d = np.random.uniform(-0.010, 0.010)
        v_lon_d = np.random.uniform(-0.010, 0.010)
        course_d = float(np.degrees(np.arctan2(v_lon_d, v_lat_d)) % 360)
        
        c_lat, c_lon = start_lat_d, start_lon_d
        d_points = []
        
        for step, ts in enumerate(timestamps):
            speed_d = round(float(np.random.uniform(11.0, 15.0)), 1)
            
            p_data = {
                'timestamp': ts.isoformat(),
                'lat': round(c_lat, 5),
                'lon': round(c_lon, 5),
                'speed_knots': speed_d,
                'course_deg': round(course_d, 1)
            }
            
            csv_records.append({
                'mmsi': mmsi,
                'timestamp': ts.isoformat(),
                'lat': round(c_lat, 5),
                'lon': round(c_lon, 5),
                'speed_knots': speed_d,
                'course_deg': round(course_d, 1)
            })
            d_points.append(p_data)
            
            c_lat += v_lat_d
            c_lon += v_lon_d
            
        json_tracks[str(mmsi)] = {
            'vessel_name': vessel_name,
            'mmsi': mmsi,
            'vessel_type': 'Cargo/Container',
            'track': d_points
        }
        
    # Save outputs
    os.makedirs('ais', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    json_path = os.path.join('ais', 'synthetic_tracks.json')
    csv_path = os.path.join('data', 'bouboulina_ais.csv')
    
    with open(json_path, 'w') as f:
        json.dump(json_tracks, f, indent=2)
        
    df = pd.DataFrame(csv_records)
    df = df.sort_values(by=['timestamp', 'mmsi']).reset_index(drop=True)
    df.to_csv(csv_path, index=False)
    
    print(f"[OK] Generated JSON tracks: {json_path}")
    print(f"[OK] Generated CSV dataset: {csv_path}")

if __name__ == "__main__":
    generate_brazil_ais_tracks()
