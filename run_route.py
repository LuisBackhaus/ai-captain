import pickle
import numpy as np
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio

print("Loading graphs...")
with open("water_graph.pkl", "rb") as f:
    G_dist = pickle.load(f)
with open("water_graph_bathy.pkl", "rb") as f:
    G_bathy = pickle.load(f)

print(f"Graphs loaded: distance={len(G_dist.nodes)}, bathy={len(G_bathy.nodes)}")

def nearest_node(coord, nodes, round_digits=3):
    lon, lat = coord
    lon, lat = round(lon, round_digits), round(lat, round_digits)
    return min(nodes, key=lambda n: np.hypot(n[0]-lon, n[1]-lat))

start = (103.9, 1.1)
goal  = (121.8, 30.8)
nodes = list(G_dist.nodes)

start_n = nearest_node(start, nodes)
goal_n  = nearest_node(goal, nodes)
print(f"Start: {start_n}, Goal: {goal_n}")

path_dist  = nx.shortest_path(G_dist, source=start_n, target=goal_n, weight="weight")
path_bathy = nx.shortest_path(G_bathy, source=start_n, target=goal_n, weight="weight")

def path_length(G, path):
    return sum(G[u][v]["weight"] for u, v in zip(path[:-1], path[1:]))

len_dist  = path_length(G_dist, path_dist)
len_bathy = path_length(G_bathy, path_bathy)

print(f"Distance-only route length: {len_dist:.2f}")
print(f"Bathymetry-optimized route length: {len_bathy:.2f}")

url = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
land = gpd.read_file(f"zip+{url}")
bathy = rasterio.open("data/ETOPO1_Ice_g_geotiff.tif")

min_lon = min(n[0] for n in G_dist.nodes)
max_lon = max(n[0] for n in G_dist.nodes)
min_lat = min(n[1] for n in G_dist.nodes)
max_lat = max(n[1] for n in G_dist.nodes)

window = rasterio.windows.from_bounds(min_lon, min_lat, max_lon, max_lat, bathy.transform)
bathy_data = bathy.read(1, window=window)
bathy_data = np.where(bathy_data == bathy.nodata, np.nan, bathy_data)
valid = bathy_data[~np.isnan(bathy_data)]
vmin, vmax = np.percentile(valid, [2, 98])
bathy_data = np.clip(bathy_data, vmin, vmax)
bathy_bounds = rasterio.windows.bounds(window, bathy.transform)
left, bottom, right, top = bathy_bounds
extent = [left, right, bottom, top]

fig, ax = plt.subplots(figsize=(10, 8))
ax.set_facecolor("#dfe9f3")

im = ax.imshow(bathy_data, extent=extent, cmap="Blues_r", origin="upper", alpha=0.85)
land.plot(ax=ax, color="#f0f0f0", edgecolor="black", linewidth=0.3, zorder=3)

ax.plot(*zip(*path_dist),  color="orange", linewidth=2, label="Distance-only", zorder=4)
ax.plot(*zip(*path_bathy), color="deepskyblue", linewidth=2.5, label="Bathy-optimized", zorder=5)
ax.scatter(*start, color="green", s=60, label="Start", zorder=6)
ax.scatter(*goal,  color="red",   s=60, label="Goal", zorder=6)

ax.legend()
ax.set_title("Distance vs Bathymetry-Optimized Routes", fontsize=13)
ax.set_xlim(min_lon, max_lon)
ax.set_ylim(min_lat, max_lat)
plt.colorbar(im, ax=ax, label="Depth [m]").ax.invert_yaxis()
plt.tight_layout()
plt.show()