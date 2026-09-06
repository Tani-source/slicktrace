# SlickTrace Prototype

SlickTrace is a prototype tracking dashboard designed to visualize synthetic Automatic Identification System (AIS) ship data and detect anomalous "dark ship" behaviors (ships deliberately turning off their transponders). It correlates these tracking anomalies with simulated satellite inferences of oil spills.

## Features

- **Synthetic AIS Data Generator**: Simulates realistic ship movements off the coast of Mumbai (Arabian Sea), complete with physical collision boundaries to prevent ships from moving onto land.
- **Dark Ship Detection**: A FastAPI backend that parses the AIS data and automatically flags vessels with suspicious data gaps (e.g., > 60 minutes).
- **Interactive Dashboard**: A premium, dark-themed React frontend using Leaflet to map ship tracks, highlight anomalies in red, and display the static satellite oil slick inference zone.

## Project Structure

- `generate_ais_mock.py`: Python script to generate the synthetic `data/ais_mock_data.csv` dataset.
- `backend/`: FastAPI server that processes the CSV data and calculates anomaly scores.
- `frontend/`: Vite + React frontend dashboard.

## Local Setup Instructions

### 1. Backend Setup

The backend requires Python 3. Create a virtual environment and install dependencies:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server (runs on http://localhost:8000)
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

The frontend requires Node.js.

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vite development server (runs on http://localhost:5173)
npm run dev
```

### 3. Regenerating Data

If you want to generate a new set of randomized ship data:

```bash
source venv/bin/activate
python generate_ais_mock.py
```
