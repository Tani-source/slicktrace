# Use a Python 3.10 Debian-based image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set the working directory to the project root
WORKDIR /app

# Install system-level geospatial dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libnetcdf-dev \
    libproj-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
# Ensure we have the latest pip and install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Switch working directory to backend where main.py resides
WORKDIR /app/backend

# Expose the port (Render will override this at runtime via the PORT env var)
EXPOSE $PORT

# Start FastAPI via Uvicorn, binding to 0.0.0.0 and the Render PORT
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
