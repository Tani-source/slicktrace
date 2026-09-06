import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_ais_data():
    start_time = datetime(2026, 9, 6, 0, 0, 0)
    num_steps = 12 * 60 // 5 # 12 hours, 5 min intervals = 144 steps
    timestamps = [start_time + timedelta(minutes=5 * i) for i in range(num_steps)]
    
    records = []
    
    # 10 Normal Ships
    np.random.seed(42)
    for i in range(1, 11):
        mmsi = 100000000 + i
        # Ensure start locations are strictly in the Arabian Sea (West of Mumbai)
        start_lat = np.random.uniform(18.85, 19.05)
        start_lon = np.random.uniform(72.5, 72.75)
        
        # Random constant velocity in degrees per step
        v_lat = np.random.uniform(-0.003, 0.003)
        v_lon = np.random.uniform(-0.003, 0.003)
        
        curr_lat = start_lat
        curr_lon = start_lon
        
        for step, ts in enumerate(timestamps):
            curr_lat += v_lat
            curr_lon += v_lon
            
            # Simple collision detection with the coast (approx longitude 72.75 is safe water)
            if curr_lon > 72.75:
                curr_lon = 72.75
                v_lon = -abs(v_lon) # Bounce back West away from the coast
                
            records.append({'mmsi': mmsi, 'timestamp': ts, 'lat': curr_lat, 'lon': curr_lon})
            
    # Dark Ship (MMSI: 999999999)
    dark_mmsi = 999999999
    start_lat_dark = 18.85
    start_lon_dark = 72.65
    spill_lat = 18.95
    spill_lon = 72.75
    
    # Timeline for dark ship:
    # 0 to 4 hours (48 steps): move towards spill zone
    # 4 to 7 hours (36 steps): GAP (no pings)
    # 7 to 12 hours (60 steps): reappear and move away
    
    gap_start_step = 48
    gap_end_step = gap_start_step + 36
    
    # Velocity to reach spill zone exactly at gap_start_step
    v_lat_in = (spill_lat - start_lat_dark) / gap_start_step
    v_lon_in = (spill_lon - start_lon_dark) / gap_start_step
    
    # Velocity moving away after gap
    v_lat_out = -v_lat_in * 0.8
    v_lon_out = -v_lon_in * 0.8
    
    curr_lat = start_lat_dark
    curr_lon = start_lon_dark
    
    for step, ts in enumerate(timestamps):
        if step < gap_start_step:
            curr_lat = start_lat_dark + v_lat_in * step
            curr_lon = start_lon_dark + v_lon_in * step
            records.append({'mmsi': dark_mmsi, 'timestamp': ts, 'lat': curr_lat, 'lon': curr_lon})
        elif gap_start_step <= step < gap_end_step:
            # GAP: The ship is deliberately turning off its AIS transponder
            # We don't record any pings, but it keeps moving in the real world
            # Let's say it idles or moves slightly during the gap
            curr_lat += v_lat_in * 0.1 
            curr_lon += v_lon_in * 0.1
            pass # No append to records
        else:
            # Reappears and moves away from the zone
            curr_lat += v_lat_out
            curr_lon += v_lon_out
            records.append({'mmsi': dark_mmsi, 'timestamp': ts, 'lat': curr_lat, 'lon': curr_lon})
            
    df = pd.DataFrame(records)
    
    # Sort chronologically
    df = df.sort_values(by=['timestamp', 'mmsi']).reset_index(drop=True)
    
    # Ensure data folder exists and save to CSV
    os.makedirs('data', exist_ok=True)
    output_path = 'data/ais_mock_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Synthetic AIS data successfully generated and saved to {output_path}")
    print(f"Total records: {len(df)}")
    print(f"Normal ship pings: {len(df[df['mmsi'] != dark_mmsi])}")
    print(f"Dark ship pings (notice the gap): {len(df[df['mmsi'] == dark_mmsi])}")

if __name__ == "__main__":
    generate_ais_data()
