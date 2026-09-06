from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI(title="SlickTrace API")

# Enable CORS for potential frontend integration later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ais_mock_data.csv')

@app.get("/api/ships")
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
        # Check if any gap > 60 mins
        max_gap = group['time_diff'].max()
        is_dark_ship = pd.notna(max_gap) and max_gap > 60
        
        # Assign a high anomaly score if flagged as a dark ship
        anomaly_score = 0.95 if is_dark_ship else 0.1
        
        # Get all coordinates
        coordinates = group[['lat', 'lon', 'timestamp']].to_dict(orient='records')
        
        # Convert timestamp to string for JSON serialization
        for c in coordinates:
            c['timestamp'] = c['timestamp'].isoformat()
            
        results.append({
            "mmsi": int(mmsi),
            "is_dark_ship": bool(is_dark_ship),
            "anomaly_score": anomaly_score,
            "max_gap_minutes": float(max_gap) if pd.notna(max_gap) else 0.0,
            "track": coordinates
        })
        
    return {"ships": results}
