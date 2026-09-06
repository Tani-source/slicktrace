# SlickTrace: 2019 Brazil Oil Spill Forensics

SlickTrace is a prototype tracking dashboard designed to visualize synthetic Automatic Identification System (AIS) ship data and detect anomalous "dark ship" behaviors (ships deliberately turning off their transponders). It correlates these tracking anomalies with simulated satellite inferences of oil spills.

This repository is currently configured to simulate and investigate the **2019 Brazil Oil Spill** off the coast of Paraíba.

## Features

- **Synthetic AIS Data Generator**: Simulates 48 hours of realistic ship movements off the coast of Brazil. It generates decoys and a specific suspect vessel ("Bouboulina") which executes a deliberate 6-hour AIS blackout precisely when passing 700km offshore.
- **Forensic API Backend**: A FastAPI backend that parses the AIS data and calculates a composite `suspect_confidence_score` for each vessel based on time blackout gaps and proximity to the oil slick origin.
- **Interactive Dashboard**: A premium, dark-themed React frontend using Leaflet. Features include:
  - **Ranked Suspect Panel**: Automatically sorts vessels by their anomaly risk score, highlighting high-risk suspects in red.
  - **Forensic Dossier Export**: Instantly download a comprehensive JSON evidence report for the top-ranked suspect.
  - **Ocean Current Drift Path**: Visualizes the backward drift path from the oil slick polygon to trace the origin of the spill.

## Project Structure

- `generate_ais_mock.py`: Python script to generate the synthetic `data/bouboulina_ais.csv` dataset.
- `backend/`: FastAPI server that processes the CSV data and serves it to the frontend.
- `frontend/`: Vite + React frontend dashboard.
- `render.yaml`: Infrastructure-as-Code blueprint for deploying the backend to Render.

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

## Cloud Deployment

This project is configured for seamless free deployment:
- **Backend (Render)**: Connect your GitHub repository to [Render.com](https://render.com). It will automatically detect the `render.yaml` file and deploy the FastAPI server (or you can manually deploy it as a Web Service).
- **Frontend (Vercel)**: Connect your GitHub repository to [Vercel.com](https://vercel.com). Select the `frontend` directory as the Root Directory, choose `Vite` as the framework preset, and set the `VITE_API_URL` environment variable to your deployed Render URL.
