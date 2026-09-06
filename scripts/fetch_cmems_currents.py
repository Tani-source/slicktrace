"""
Script: fetch_cmems_currents.py
Description: Downloads CMEMS ocean currents velocity components (uo, vo) for NE Brazil
              bounding box surrounding the July/August 2019 spill location.
Prerequisite: `pip install copernicusmarine` + Copernicus Marine Service account
"""

import os
import sys

def fetch_cmems_currents():
    output_dir = "currents"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "cmems_currents_brazil_2019.nc")

    # Spatial Bounding Box (NE Brazil Coast / Paraíba Offshore)
    min_lat, max_lat = -15.0, -5.0
    min_lon, max_lon = -38.0, -25.0
    
    # Temporal Window (July 20 to August 15, 2019)
    start_date = "2019-07-20"
    end_date = "2019-08-15"

    print(f"Fetching CMEMS Ocean Currents...")
    print(f"   Bounding Box: Lat [{min_lat}, {max_lat}], Lon [{min_lon}, {max_lon}]")
    print(f"   Date Range: {start_date} to {end_date}")

    try:
        import copernicusmarine
        
        copernicusmarine.subset(
            dataset_id="cmems_mod_glo_phy_my_0.083deg_P1D-m",
            variables=["uo", "vo"],
            minimum_longitude=min_lon,
            maximum_longitude=max_lon,
            minimum_latitude=min_lat,
            maximum_latitude=max_lat,
            start_datetime=f"{start_date}T00:00:00",
            end_datetime=f"{end_date}T23:59:59",
            output_filename=output_file,
            force_download=True
        )
        print(f"[OK] Successfully downloaded CMEMS currents to: {output_file}")
    except ImportError:
        print("[WARNING] 'copernicusmarine' package not installed.")
        print("   Install via: pip install copernicusmarine")
        print("   Sign up for a free account at: https://data.marine.copernicus.eu")
    except Exception as e:
        print(f"[ERROR] Error fetching CMEMS data: {e}")

if __name__ == "__main__":
    fetch_cmems_currents()
