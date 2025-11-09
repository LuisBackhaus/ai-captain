import matplotlib.pyplot as plt
import numpy as np

lons = np.array([p[0] for p in wind_uv.keys()])
lats = np.array([p[1] for p in wind_uv.keys()])
u = np.array([v[0] for v in wind_uv.values()])
v = np.array([v[1] for v in wind_uv.values()])

plt.figure(figsize=(10,8))
plt.quiver(lons, lats, u, v, np.hypot(u, v), cmap="plasma", scale=400)
plt.colorbar(label="Wind speed (m/s)")
plt.title("Wind Vectors Parsed from data.txt")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.show()