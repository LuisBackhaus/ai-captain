import numpy as np

def compute_edge_weight(node_a, node_b, bathy):
    """
    Compute edge cost between two nodes, penalizing shallow water (<100 m depth).
    """
    (lon1, lat1), (lon2, lat2) = node_a, node_b
    base_dist = np.hypot(lon2 - lon1, lat2 - lat1)

    depth_a = get_depth(bathy, lon1, lat1)
    depth_b = get_depth(bathy, lon2, lat2)
    avg_depth = (depth_a + depth_b) / 2

    # penalize shallow water (depth > -100)
    penalty = 5.0 if avg_depth > -100 else 1.0

    return base_dist * penalty


def get_depth(bathy, lon, lat):
    """
    Returns interpolated bathymetry (in meters) at (lon, lat).
    """
    row, col = bathy.index(lon, lat)
    return bathy.read(1)[row, col]