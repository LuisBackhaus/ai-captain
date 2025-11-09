import requests
import numpy as np
import time

# Define grid of coordinates (you can tighten later)
lats = np.arange(-10, 40, 1)   # [-10, 0, 10, 20, 30]
lons = np.arange(90, 130, 1)   # [90, 100, 110, 120]

url = "https://api.open-meteo.com/v1/forecast"

def get_wind(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wind_speed_10m,wind_direction_10m",
        "forecast_days": 1,
        "timezone": "GMT",
        "cell_selection": "sea"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    d = r.json()
    speed = d["hourly"]["wind_speed_10m"][0]
    direction = d["hourly"]["wind_direction_10m"][0]
    return speed, direction

results = {}
for lat in lats:
    for lon in lons:
        try:
            s, d = get_wind(lat, lon)
            results[(lat, lon)] = (s, d)
            print(f"({lat}, {lon}) → {s} m/s @ {d}°")
            time.sleep(0.2)  # be polite to API
        except Exception as e:
            print(f"({lat}, {lon}) failed: {e}")

print("\nCollected", len(results), "wind samples.")