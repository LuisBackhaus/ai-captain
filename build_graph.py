import geopandas as gpd
import numpy as np
import networkx as nx
import pickle
from shapely import contains_xy
from shapely.ops import unary_union

print("Building graph...")

# --- 1. Land polygons ---
url = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
land = gpd.read_file(f"zip+{url}")
land_union = unary_union(land.geometry)

# --- 2. Grid definition ---
STEP_SIZE = 0.1
LON_STEP = STEP_SIZE
LAT_STEP = STEP_SIZE
round_digits = 3

lons = np.arange(90, 130 + LON_STEP, LON_STEP)
lats = np.arange(-10, 40 + LAT_STEP, LAT_STEP)
LON, LAT = np.meshgrid(lons, lats)
mask = contains_xy(land_union, LON, LAT)

# --- 3. Node extraction ---
water_lons = np.round(LON[~mask], round_digits)
water_lats = np.round(LAT[~mask], round_digits)
nodes = [(float(lon), float(lat)) for lon, lat in zip(water_lons, water_lats)]
node_set = set(nodes)
print(f"Water nodes: {len(nodes)}")

# --- 4. Build graph ---
G = nx.Graph()
for lon, lat in nodes:
    for dlon in [-LON_STEP, 0, LON_STEP]:
        for dlat in [-LAT_STEP, 0, LON_STEP]:
            if dlon == 0 and dlat == 0:
                continue
            nlon = round(lon + dlon, round_digits)
            nlat = round(lat + dlat, round_digits)
            if (nlon, nlat) in node_set:
                dist = np.hypot(dlon, dlat)
                G.add_edge((lon, lat), (nlon, nlat), weight=dist)

# --- 5. Save graph ---
with open("water_graph.pkl", "wb") as f:
    pickle.dump(G, f)

print("✅ Graph built and saved as water_graph.pkl")