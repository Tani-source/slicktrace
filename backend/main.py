from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os
from shapely.geometry import Point

app = FastAPI(title="SlickTrace API")

# Enable CORS for potential frontend integration later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bouboulina_ais.csv')
DATA_PATH_FALLBACK = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ais_mock_data.csv')

# Oil slick origin coordinate: Offshore Paraíba, Brazil (~700 km off coast)
SLICK_LAT = -7.2
SLICK_LON = -33.8
slick_point = Point(SLICK_LON, SLICK_LAT)

def calculate_distance(lat, lon):
    # Euclidean distance in degrees for prototype scale
    return slick_point.distance(Point(lon, lat))

VESSEL_NAMES = {
    240000000: "Bouboulina (Greek Tanker)",
    100000003: "Atlas Sky",
    100000004: "Ocean Pioneer",
    100000005: "Pacific Carrier"
}

@app.get("/vessels")
def get_ships_data():
    data_file = DATA_PATH_CSV if os.path.exists(DATA_PATH_CSV) else DATA_PATH_FALLBACK
    if not os.path.exists(data_file):
        return {"error": "Data file not found"}
        
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by mmsi and timestamp
    df = df.sort_values(by=['mmsi', 'timestamp'])
    
    # Calculate time difference in minutes between consecutive pings for each ship
    df['time_diff'] = df.groupby('mmsi')['timestamp'].diff().dt.total_seconds() / 60.0
    
    results = []
    
    for mmsi, group in df.groupby('mmsi'):
        # 1. Time blackout gap score (50% weight)
        max_gap = group['time_diff'].max()
        gap_minutes = float(max_gap) if pd.notna(max_gap) else 0.0
        # Normalize gap (e.g. 180 mins is max score 1.0)
        gap_score = min(1.0, gap_minutes / 180.0)
        
        # 2. Minimum distance to the oil slick origin coordinate (50% weight)
        min_dist = group.apply(lambda row: calculate_distance(row['lat'], row['lon']), axis=1).min()
        # Normalize distance for offshore scale (e.g. 5 degrees is max threshold)
        dist_score = max(0.0, 1.0 - (min_dist / 5.0))
        
        # Composite suspect confidence score
        suspect_confidence_score = (0.5 * gap_score) + (0.5 * dist_score)
        
        # Flag as dark ship if score is high enough or has significant blackout gap (> 60m)
        is_dark_ship = suspect_confidence_score > 0.5 or gap_minutes > 60.0
        
        # Get all coordinates
        coordinates = group[['lat', 'lon', 'timestamp']].to_dict(orient='records')
        
        # Convert timestamp to string for JSON serialization
        for c in coordinates:
            c['timestamp'] = c['timestamp'].isoformat()
            
        vessel_name = VESSEL_NAMES.get(int(mmsi), f"MMSI-{mmsi}")
            
        results.append({
            "mmsi": int(mmsi),
            "vessel_name": vessel_name,
            "is_dark_ship": bool(is_dark_ship),
            "anomaly_score": round(suspect_confidence_score, 4),
            "suspect_confidence_score": round(suspect_confidence_score, 4),
            "max_gap_minutes": gap_minutes,
            "min_distance_to_slick": float(min_dist),
            "track": coordinates
        })
        
    # Return an array of sorted suspect objects ordered by overall risk score
    results.sort(key=lambda x: x['suspect_confidence_score'], reverse=True)
        
    return {"ships": results}
