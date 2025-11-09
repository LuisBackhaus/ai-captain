import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import math
import re

# --- 1. Load Natural Earth land polygons ---
url = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
land = gpd.read_file(f"zip+{url}")

# --- 2. Load and parse data.txt ---
with open("data.txt") as f:
    text = f.read()

# Extract tuples like: (lat, lon): (speed, dir)
matches = re.findall(r"\(([-\d.]+), ([-\d.]+)\): \(([-\d.]+), ([-\d.]+)\)", text)
results = {(float(lat), float(lon)): (float(speed), float(direction)) for lat, lon, speed, direction in matches}

# --- 3. Extract arrays ---
lats = np.array([k[0] for k in results.keys()])
lons = np.array([k[1] for k in results.keys()])
speeds = np.array([v[0] for v in results.values()])
dirs = np.array([v[1] for v in results.values()])

# --- 4. Convert direction → components ---
u = -speeds * np.sin(np.radians(dirs))
v = -speeds * np.cos(np.radians(dirs))

# --- 5. Plot base map + wind field ---
fig, ax = plt.subplots(figsize=(10, 8))
land.plot(ax=ax, color="lightgray", edgecolor="black")

q = ax.quiver(lons, lats, u, v, speeds, cmap="plasma", scale=400)
plt.colorbar(q, ax=ax, label="Wind Speed (m/s)")

ax.set_xlim(85, 125)
ax.set_ylim(-15, 35)
ax.set_title("Wind Field (10m, Open-Meteo) over Natural Earth Land")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.grid(True)

plt.tight_layout()
plt.show()