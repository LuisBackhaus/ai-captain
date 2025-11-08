import geopandas as gpd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import rasterio
from shapely.geometry import Point
from weights import compute_edge_weight  # our custom weighted function

# --- 1. Load land polygons ---
url = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
land = gpd.read_file(f"zip+{url}")

# --- 2. Load bathymetry ---
bathy = rasterio.open("data/ETOPO1_Ice_g_geotiff.tif")  # you can clip later if needed

# --- 3. Define grid region (Southeast Asia, 0.25° resolution) ---
LON_STEP = 1.0
LAT_STEP = 1.0
lons = np.arange(90, 130 + LON_STEP, LON_STEP)
lats = np.arange(-10, 40 + LAT_STEP, LAT_STEP)

nodes = []
for lon in lons:
    for lat in lats:
        p = Point(lon, lat)
        if not land.contains(p).any():  # only keep water nodes
            nodes.append((lon, lat))
print(f"Total water nodes: {len(nodes)}")

# --- 4. Build graph (with bathymetry weighting) ---
G_bathy = nx.Graph()
for lon, lat in nodes:
    for dlon in [-LON_STEP, 0, LON_STEP]:
        for dlat in [-LAT_STEP, 0, LAT_STEP]:
            if dlon == 0 and dlat == 0:
                continue
            nlon, nlat = lon + dlon, lat + dlat
            if (nlon, nlat) in nodes:
                w = compute_edge_weight((lon, lat), (nlon, nlat), bathy)
                G_bathy.add_edge((lon, lat), (nlon, nlat), weight=w)

# --- 5. Build simple graph (no bathymetry) ---
G_normal = nx.Graph()
for lon, lat in nodes:
    for dlon in [-LON_STEP, 0, LON_STEP]:
        for dlat in [-LAT_STEP, 0, LON_STEP]:
            if dlon == 0 and dlat == 0:
                continue
            nlon, nlat = lon + dlon, lat + dlat
            if (nlon, nlat) in nodes:
                dist = np.hypot(dlon, dlat)
                G_normal.add_edge((lon, lat), (nlon, nlat), weight=dist)

# --- 6. Define start & goal ---
start = (103.8, 1.3)   # Singapore
goal = (121.5, 31.2)   # Shanghai

def nearest_node(coord):
    return min(nodes, key=lambda n: np.hypot(n[0]-coord[0], n[1]-coord[1]))

start_n = nearest_node(start)
goal_n  = nearest_node(goal)

# --- 7. Compute paths ---
path_normal = nx.shortest_path(G_normal, source=start_n, target=goal_n, weight='weight')
path_bathy  = nx.shortest_path(G_bathy,  source=start_n, target=goal_n, weight='weight')

# --- 8. Plot both paths ---
fig, ax = plt.subplots(figsize=(10, 8))
land.plot(ax=ax, color="lightgray", edgecolor="black")

ax.plot(*zip(*path_normal), color="orange", linewidth=2, label="Pure water route")
ax.plot(*zip(*path_bathy),  color="blue",   linewidth=2.5, label="Bathymetry-weighted route")

ax.scatter(*start, color="green", s=50, label="Singapore")
ax.scatter(*goal, color="red", s=50, label="Shanghai")

ax.legend()
ax.set_title("Water Routing: Normal vs Bathymetry-Weighted (Singapore → Shanghai)")
plt.show()