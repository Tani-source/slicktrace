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

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bouboulina_ais.csv')

# Oil slick origin coordinate (Brazil, approximate)
SLICK_LAT = -10.0
SLICK_LON = -30.0
slick_point = Point(SLICK_LON, SLICK_LAT)

def calculate_distance(lat, lon):
    # Euclidean distance in degrees for prototype scale
    return slick_point.distance(Point(lon, lat))

@app.get("/vessels")
def get_ships_data():
    if not os.path.exists(DATA_PATH):
        return {"error": "Data file not found"}
        
    df = pd.read_csv(DATA_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by mmsi and timestamp
    df = df.sort_values(by=['mmsi', 'timestamp'])
    
    # Calculate time difference in minutes between consecutive pings for each ship
    df['time_diff'] = df.groupby('mmsi')['timestamp'].diff().dt.total_seconds() / 60.0
    
    results = []
    
    for mmsi, group in df.groupby('mmsi'):
        # 1. Time blackout gap score (40% weight)
        max_gap = group['time_diff'].max()
        gap_minutes = float(max_gap) if pd.notna(max_gap) else 0.0
        # Normalize gap (e.g. 180 mins is max score 1.0)
        gap_score = min(1.0, gap_minutes / 180.0)
        
        # 2. Minimum distance to the oil slick origin coordinate (60% weight)
        min_dist = group.apply(lambda row: calculate_distance(row['lat'], row['lon']), axis=1).min()
        # Normalize distance (e.g. 0 degrees is max score 1.0, >0.15 degrees is 0)
        dist_score = max(0.0, 1.0 - (min_dist / 0.15))
        
        # Composite suspect confidence score
        suspect_confidence_score = (0.4 * gap_score) + (0.6 * dist_score)
        
        # Flag as dark ship if score is high enough
        is_dark_ship = suspect_confidence_score > 0.5
        
        # Get all coordinates
        coordinates = group[['lat', 'lon', 'timestamp']].to_dict(orient='records')
        
        # Convert timestamp to string for JSON serialization
        for c in coordinates:
            c['timestamp'] = c['timestamp'].isoformat()
            
        results.append({
            "mmsi": int(mmsi),
            "is_dark_ship": bool(is_dark_ship),
            "anomaly_score": suspect_confidence_score, # kept for frontend backward compatibility
            "suspect_confidence_score": suspect_confidence_score,
            "max_gap_minutes": gap_minutes,
            "min_distance_to_slick": float(min_dist),
            "track": coordinates
        })
        
    # Return an array of sorted suspect objects ordered by overall risk score
    results.sort(key=lambda x: x['suspect_confidence_score'], reverse=True)
        
    return {"ships": results}
