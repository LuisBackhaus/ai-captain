import geopandas as gpd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import rasterio
from shapely import contains_xy
from shapely.ops import unary_union

print("NOW EXECUTING MAIN SCRIPT")

# --- 1. Load land polygons ---
url = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
land = gpd.read_file(f"zip+{url}")

# --- 2. Load bathymetry (optional weighting) ---
bathy = rasterio.open("data/ETOPO1_Ice_g_geotiff.tif")

# --- 3. Define grid region (Southeast Asia, fine resolution) ---
STEP_SIZE = 0.1
LON_STEP = STEP_SIZE
LAT_STEP = STEP_SIZE
lons = np.arange(90, 130 + LON_STEP, LON_STEP)
lats = np.arange(-10, 40 + LAT_STEP, LAT_STEP)

start = (103.9, 1.1)   # near Singapore
goal  = (121.8, 30.8)  # near Shanghai

# --- 4. Compute water zones ---
land_union = unary_union(land.geometry)
LON, LAT = np.meshgrid(lons, lats)

# faster contains using vectorized approach
mask = contains_xy(land_union, LON, LAT)  # True = land

round_digits = 3
water_lons = np.round(LON[~mask], round_digits)
water_lats = np.round(LAT[~mask], round_digits)
nodes = [(float(lon), float(lat)) for lon, lat in zip(water_lons, water_lats)]
node_set = set(nodes)

print(f"Total water nodes: {len(nodes)}")

# --- 5. Build graph ---
G_normal = nx.Graph()

for lon, lat in nodes:
    for dlon in [-LON_STEP, 0, LON_STEP]:
        for dlat in [-LAT_STEP, 0, LON_STEP]:
            if dlon == 0 and dlat == 0:
                continue
            nlon = round(lon + dlon, round_digits)
            nlat = round(lat + dlat, round_digits)
            if (nlon, nlat) in node_set:
                dist = np.hypot(dlon, dlat)
                G_normal.add_edge((lon, lat), (nlon, nlat), weight=dist)

# --- 6. Find nearest nodes ---
def nearest_node(coord):
    lon, lat = coord
    lon, lat = round(lon, round_digits), round(lat, round_digits)
    return min(nodes, key=lambda n: np.hypot(n[0] - lon, n[1] - lat))

start_n = nearest_node(start)
goal_n  = nearest_node(goal)

if start_n not in G_normal or goal_n not in G_normal:
    raise ValueError("Start or goal not in graph — check land proximity or reduce STEP_SIZE.")

print(f"Start node: {start_n}, Goal node: {goal_n}")

# --- 7. Compute shortest path ---
path_normal = nx.shortest_path(G_normal, source=start_n, target=goal_n, weight='weight')

# --- 8. Plot ---
fig, ax = plt.subplots(figsize=(10, 8))
land.plot(ax=ax, color="lightgray", edgecolor="black")
ax.plot(*zip(*path_normal), color="orange", linewidth=2, label="Shortest Water Route")
ax.scatter(*start, color="green", s=50, label="Singapore")
ax.scatter(*goal, color="red", s=50, label="Shanghai")
ax.legend()
ax.set_title("Optimized Maritime Route (Water Only)")
ax.set_xlim(min(lons), max(lons))
ax.set_ylim(min(lats), max(lats))
plt.show()