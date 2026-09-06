# SlickTrace — Data Setup Guide
### Case Study: 2019 Brazil Coast Mystery Oil Spill ("Bouboulina")

This README documents the exact, minimal dataset needed to build and demo the
SlickTrace pipeline (SAR detection → AIS shortlist → forward drift simulation →
matching) using one real, provable historical case instead of scattered generic data.

---

## 1. Why this case

In August 2019, oil began washing up along 2,500+ km of Brazil's coastline with
no known source. Investigators narrowed the search to a handful of candidate
tankers using AIS data and eventually identified the Greek tanker **Bouboulina**,
which had passed ~700 km off Paraíba state on 28–29 July 2019 carrying Venezuelan
crude en route to Malaysia. This is a direct real-world analog of what SlickTrace
does — perfect single-case demo material.

---

## 2. Folder structure

```
slicktrace-data/
├── sar/
│   └── bouboulina_2019_sar_crop.tif      # Sentinel-1 crop, event window
├── ais/
│   └── synthetic_tracks.json              # hand-built + interpolated tracks
├── currents/
│   └── cmems_currents_brazil_2019.nc      # CMEMS subset, 2–4 week window
├── wind/
│   └── era5_wind_brazil_2019.nc           # ERA5 subset, same window
└── scripts/
    ├── generate_ais_tracks.py
    ├── fetch_cmems_currents.py
    └── fetch_era5_wind.py
```

---

## 3. Data sources & steps

### 3.1 SAR imagery (the "evidence")
- Source: **Copernicus Browser** — https://browser.dataspace.copernicus.eu (free)
- Search: Sentinel-1, area = offshore Paraíba / NE Brazil coast, date = late July–Aug 2019
- Download only the **cropped area of interest**, not the full scene (keeps it to a few MB)
- Save to `sar/`

### 3.2 AIS (the ship tracks)
- Real bulk AIS for Brazilian waters in 2019 is not freely downloadable
  (MarineCadastre only covers U.S. waters).
- Instead: hand-seed one real anchor point (Bouboulina, ~700 km off Paraíba,
  28–29 July 2019, Venezuela→Malaysia heading) and interpolate a smooth track
  through it, plus 3 synthetic decoy ships nearby with slightly different
  courses/speeds to simulate a realistic candidate shortlist.
- Script: `scripts/generate_ais_tracks.py` → outputs `ais/synthetic_tracks.json`

### 3.3 Ocean currents
- Source: **CMEMS** — https://data.marine.copernicus.eu (free registration required)
- Pull only the exact bounding box + a 2–4 week window around the event
  (not global or full-year data)
- Script: `scripts/fetch_cmems_currents.py` → outputs `currents/cmems_currents_brazil_2019.nc`

### 3.4 Wind
- Source: **ECMWF ERA5 via CDS** — https://cds.climate.copernicus.eu (free registration required)
- Same bounding box, same date window
- Variables: `10m_u_component_of_wind`, `10m_v_component_of_wind`
- Script: `scripts/fetch_era5_wind.py` → outputs `wind/era5_wind_brazil_2019.nc`

### 3.5 Drift simulation engine
- `pip install opendrift` — no dataset needed, consumes the currents + wind files above.

---

## 4. Prerequisites (accounts you must create manually)

These cannot be automated by any agent — they require human sign-up (email
verification / CAPTCHA):
- [ ] Copernicus Data Space account (dataspace.copernicus.eu) — for SAR browsing
- [ ] Copernicus Marine Service account (data.marine.copernicus.eu) — for CMEMS
- [ ] Copernicus Climate Data Store account (cds.climate.copernicus.eu) — for ERA5

Once created, each gives you an API key/token to store locally
(`.cdsapirc` for CDS, credentials prompt for `copernicusmarine` toolbox).

---

## 5. Verification / test checklist

- [ ] SAR crop opens and visibly shows a dark slick patch against ocean background
- [ ] AIS JSON has ≥4 ship tracks (1 real anchor + 3 decoys), each with lat/lon/time/speed
- [ ] CMEMS `.nc` file covers the correct bbox and date range (check with `xarray`)
- [ ] ERA5 `.nc` file covers the same bbox and date range
- [ ] OpenDrift runs a basic OilDrift simulation using the currents + wind files
      without errors and produces a particle trajectory output
- [ ] Simulated slick polygon (end of drift run) can be visually compared against
      the real SAR crop

---

## 6. Known limitations

- No real AIS ground truth for this region/date — synthetic tracks are a
  stand-in, not verified vessel data.
- Free SAR access is best-effort browsing; exact revisit timing over the event
  window may not perfectly align with when the slick was first visible.
