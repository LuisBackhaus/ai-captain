import geopandas as gpd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from shapely import contains_xy

"""Purely computes the shortest water-only path between Hamburg and Amsterdam"""

# --- 1. Load land polygons (Europe scale) ---
url = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
land = gpd.read_file(f"zip+{url}")

# --- 2. Define grid region (Europe, fine enough for North Sea) ---
STEP_SIZE = 2  # ~25 km spacing
lons = np.arange(3, 10 + STEP_SIZE, STEP_SIZE)    # covers Netherlands to NW Germany
lats = np.arange(52, 56 + STEP_SIZE, STEP_SIZE)   # North Sea coast

start = (9.99, 53.55)   # Hamburg
goal = (4.90, 52.37)    # Amsterdam

# --- 3. Compute water zones ---
land_union = land.union_all()  # merge polygons once
LON, LAT = np.meshgrid(lons, lats)
mask = contains_xy(land_union, LON, LAT)  # True = land

water_lons = LON[~mask]
water_lats = LAT[~mask]
nodes = list(zip(water_lons, water_lats))
print(f"Total water nodes: {len(nodes)}")

# --- 4. Build graph ---
G = nx.Graph()
node_set = set(nodes)
for lon, lat in nodes:
    for dlon in [-STEP_SIZE, 0, STEP_SIZE]:
        for dlat in [-STEP_SIZE, 0, STEP_SIZE]:
            if dlon == 0 and dlat == 0:
                continue
            nlon, nlat = lon + dlon, lat + dlat
            if (nlon, nlat) in node_set:
                dist = np.hypot(dlon, dlat)
                G.add_edge((lon, lat), (nlon, nlat), weight=dist)

# --- 5. Find nearest nodes ---
def nearest_node(coord):
    return min(nodes, key=lambda n: np.hypot(n[0]-coord[0], n[1]-coord[1]))

start_n = nearest_node(start)
goal_n  = nearest_node(goal)

# --- 6. Compute shortest path ---
path = nx.shortest_path(G, source=start_n, target=goal_n, weight='weight')

# --- 7. Plot ---
fig, ax = plt.subplots(figsize=(8, 8))
land.plot(ax=ax, color="lightgray", edgecolor="black")
ax.plot(*zip(*path), color="orange", linewidth=2, label="Shortest water path")
ax.scatter(*start, color="green", s=60, label="Hamburg")
ax.scatter(*goal, color="red", s=60, label="Amsterdam")
ax.set_xlim(3, 10)
ax.set_ylim(52, 56)
ax.legend()
ax.set_title("Shortest Route: Hamburg → Amsterdam")
plt.show()