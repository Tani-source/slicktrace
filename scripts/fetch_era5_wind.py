"""
Script: fetch_era5_wind.py
Description: Downloads ECMWF ERA5 10m wind velocity components (u10, v10) for NE Brazil
              bounding box surrounding the July/August 2019 spill location.
Prerequisite: `pip install cdsapi` + CDS account (.cdsapirc configuration file)
"""

import os
import sys

def fetch_era5_wind():
    output_dir = "wind"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "era5_wind_brazil_2019.nc")

    # Spatial Bounding Box: [North, West, South, East]
    # NE Brazil Coast / Paraíba Offshore
    area = [-5.0, -38.0, -15.0, -25.0]

    print(f"Fetching ECMWF ERA5 10m Wind Data...")
    print(f"   Area [N, W, S, E]: {area}")
    print(f"   Date Range: 2019-07-20 to 2019-08-15")

    try:
        import cdsapi

        c = cdsapi.Client()
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'variable': [
                    '10m_u_component_of_wind',
                    '10m_v_component_of_wind',
                ],
                'year': '2019',
                'month': ['07', '08'],
                'day': [
                    '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31',
                    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15'
                ],
                'time': [
                    '00:00', '06:00', '12:00', '18:00',
                ],
                'area': area,
            },
            output_file
        )
        print(f"[OK] Successfully downloaded ERA5 wind dataset to: {output_file}")
    except ImportError:
        print("[WARNING] 'cdsapi' package not installed.")
        print("   Install via: pip install cdsapi")
        print("   Sign up for a free account at: https://cds.climate.copernicus.eu")
    except Exception as e:
        print(f"[ERROR] Error fetching ERA5 wind data: {e}")

if __name__ == "__main__":
    fetch_era5_wind()
