import geopandas as gpd
import numpy as np
import networkx as nx
import rasterio
import itertools
from shapely import contains_xy
from shapely.ops import unary_union
import pickle
from tqdm import tqdm

print("⚙️ Building bathymetry-aware graph (optimized)...")

# --- 1. Load land polygons ---
url = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
land = gpd.read_file(f"zip+{url}")
land_union = unary_union(land.geometry)

# --- 2. Load bathymetry ---
bathy_path = "data/ETOPO1_Ice_g_geotiff.tif"
bathy = rasterio.open(bathy_path)
bathy_data = bathy.read(1)
transform = bathy.transform
nodata = bathy.nodata

# --- 3. Define grid ---
STEP_SIZE = 0.1
LON_STEP = STEP_SIZE
LAT_STEP = STEP_SIZE
round_digits = 3

lons = np.arange(90, 130 + LON_STEP, LON_STEP)
lats = np.arange(-10, 40 + LAT_STEP, LAT_STEP)
LON, LAT = np.meshgrid(lons, lats)
mask = contains_xy(land_union, LON, LAT)

# --- 4. Water nodes ---
water_lons = np.round(LON[~mask], round_digits)
water_lats = np.round(LAT[~mask], round_digits)
nodes = [(float(lon), float(lat)) for lon, lat in zip(water_lons, water_lats)]
node_set = set(nodes)
print(f"💧 Water nodes: {len(nodes)}")

# --- 5. Precompute all depths into cache ---
def get_depth_fast(lon, lat):
    try:
        row, col = bathy.index(lon, lat)
        if (
            0 <= row < bathy_data.shape[0]
            and 0 <= col < bathy_data.shape[1]
        ):
            val = bathy_data[row, col]
            return np.nan if val == nodata else abs(val)
    except Exception:
        pass
    return np.nan

print("🔹 Caching depths...")
depth_cache = {node: get_depth_fast(*node) for node in tqdm(nodes)}

# --- 6. Build weighted graph ---
target_depth = 3000.0       # desired depth (m)
penalty_factor = 0.8        # how strong the penalty is
G = nx.Graph()

print("🔹 Building weighted edges...")
offsets = [(dlon, dlat) for dlon, dlat in itertools.product([-LON_STEP, 0, LON_STEP], repeat=2) if not (dlon == 0 and dlat == 0)]

for lon, lat in tqdm(nodes):
    depth_a = depth_cache[(lon, lat)]
    for dlon, dlat in offsets:
        nlon = round(lon + dlon, round_digits)
        nlat = round(lat + dlat, round_digits)
        if (nlon, nlat) in node_set:
            depth_b = depth_cache[(nlon, nlat)]
            if np.isnan(depth_a) or np.isnan(depth_b):
                continue
            dist = np.hypot(dlon, dlat)
            avg_depth = np.nanmean([depth_a, depth_b])
            penalty = 1.0 + penalty_factor * abs(avg_depth - target_depth) / target_depth
            penalty = min(penalty, 3.0)
            G.add_edge((lon, lat), (nlon, nlat), weight=dist * penalty)

print(f"✅ Graph built with {len(G.nodes)} nodes and {len(G.edges)} edges.")

# --- 7. Save graph ---
with open("water_graph_bathy.pkl", "wb") as f:
    pickle.dump(G, f)

print("💾 Saved as water_graph_bathy.pkl")
print("🏁 Done — optimized bathymetry graph ready!")