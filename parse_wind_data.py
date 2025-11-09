import re
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import LinearNDInterpolator

# --- STEP 1: Parse data.txt ---
wind_uv = {}

with open("data.txt") as f:
    for line in f:
        match = re.match(r"\(([-\d\.]+),\s*([-\d\.]+)\):\s*\(([-\d\.]+),\s*([-\d\.]+)\)", line)
        if not match:
            continue
        lat, lon, speed, direction = map(float, match.groups())

        # Convert polar → Cartesian (meteorological convention)
        u = -speed * math.sin(math.radians(direction))  # east-west
        v = -speed * math.cos(math.radians(direction))  # north-south
        wind_uv[(lon, lat)] = (u, v)

print(f"Loaded {len(wind_uv)} wind points.")
print("Sample:", list(wind_uv.items())[:3])

# --- STEP 2: Plot the raw wind field ---
lons = np.array([p[0] for p in wind_uv.keys()])
lats = np.array([p[1] for p in wind_uv.keys()])
u = np.array([v[0] for v in wind_uv.values()])
v = np.array([v[1] for v in wind_uv.values()])

plt.figure(figsize=(10, 8))
plt.quiver(lons, lats, u, v, np.hypot(u, v), cmap="plasma", scale=400)
plt.colorbar(label="Wind speed (m/s)")
plt.title("Wind Vectors Parsed from data.txt")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.show()

# --- STEP 3: Create interpolators for continuous field ---
pts = np.array(list(wind_uv.keys()))
u_vals = np.array([val[0] for val in wind_uv.values()])
v_vals = np.array([val[1] for val in wind_uv.values()])

interp_u = LinearNDInterpolator(pts, u_vals)
interp_v = LinearNDInterpolator(pts, v_vals)

def wind_at(lon, lat):
    """Returns interpolated (u, v) components at any lon/lat."""
    return float(interp_u(lon, lat)), float(interp_v(lon, lat))

# Test interpolation at mid-point
test_point = (110, 10)
u_test, v_test = wind_at(*test_point)
print(f"Interpolated wind at {test_point}: u={u_test:.2f}, v={v_test:.2f}")