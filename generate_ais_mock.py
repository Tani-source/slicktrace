import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_brazil_spill_data():
    # Dates: July 28-29, 2019 (48 hours)
    start_time = datetime(2019, 7, 28, 0, 0, 0)
    # 5-minute intervals
    num_steps = 48 * 60 // 5
    timestamps = [start_time + timedelta(minutes=5 * i) for i in range(num_steps)]
    
    records = []
    
    # Ship 1: The Suspect (Bouboulina)
    bouboulina_mmsi = 240000000
    # Start near Paraíba coast (Lat -7.0, Lon -34.0)
    start_lat_b = -7.0
    start_lon_b = -34.0
    
    # Trajectory heading Southeast over 48 hours
    end_lat_b = -12.0
    end_lon_b = -28.0
    v_lat_b = (end_lat_b - start_lat_b) / num_steps
    v_lon_b = (end_lon_b - start_lon_b) / num_steps
    
    # Approx 700km offshore is ~6.3 degrees longitude East from -34.0 (so ~ -27.7)
    # We'll trigger the gap when longitude crosses -29.0 for demonstration
    # Let's calculate the step for blackout:
    # A 6-hour gap is 72 steps (6 * 60 / 5)
    gap_start = int(num_steps * 0.6) # starts after ~28 hours
    gap_end = gap_start + 72
    
    curr_lat = start_lat_b
    curr_lon = start_lon_b
    for step, ts in enumerate(timestamps):
        if gap_start <= step < gap_end:
            # 6-hour Deliberate AIS Blackout
            curr_lat += v_lat_b
            curr_lon += v_lon_b
            continue
            
        records.append({'mmsi': bouboulina_mmsi, 'timestamp': ts, 'lat': curr_lat, 'lon': curr_lon})
        curr_lat += v_lat_b
        curr_lon += v_lon_b
        
    # Ships 2, 3, and 4: Decoys
    np.random.seed(42)
    for i in range(2, 5):
        mmsi = 100000000 + i
        # Start intersecting trajectories in the same bounding box
        start_lat_d = np.random.uniform(-12.0, -7.0)
        start_lon_d = np.random.uniform(-34.0, -28.0)
        
        # Constant velocities across the box
        v_lat_d = np.random.uniform(-0.015, 0.015)
        v_lon_d = np.random.uniform(-0.015, 0.015)
        
        c_lat = start_lat_d
        c_lon = start_lon_d
        for step, ts in enumerate(timestamps):
            # Perfect, continuous 5-minute ping intervals (no gaps)
            records.append({'mmsi': mmsi, 'timestamp': ts, 'lat': c_lat, 'lon': c_lon})
            c_lat += v_lat_d
            c_lon += v_lon_d
            
    df = pd.DataFrame(records)
    
    # Sort chronologically
    df = df.sort_values(by=['timestamp', 'mmsi']).reset_index(drop=True)
    
    # Save to data folder
    os.makedirs('data', exist_ok=True)
    output_path = 'data/bouboulina_ais.csv'
    df.to_csv(output_path, index=False)
    print(f"2019 Brazil Oil Spill synthetic dataset saved to {output_path}")

if __name__ == "__main__":
    generate_brazil_spill_data()
