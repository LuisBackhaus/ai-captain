import numpy as np
import networkx as nx
from haversine import haversine
import geopandas as gpd
from shapely.geometry import Point
import rasterio
from typing import List, Tuple, Dict

class BathymetryRouter:
    """Advanced router using bathymetry and land avoidance"""
    
    def __init__(self, bathymetry_path: str = None, resolution: float = 0.5):
        """
        Initialize router with optional bathymetry data
        
        Args:
            bathymetry_path: Path to ETOPO or GEBCO bathymetry file
            resolution: Grid resolution in degrees (0.5° = ~55km at equator)
        """
        self.resolution = resolution
        self.bathymetry = None
        self.land_polygons = None
        
        # Load bathymetry if available
        if bathymetry_path:
            try:
                self.bathymetry = rasterio.open(bathymetry_path)
            except Exception as e:
                print(f"Warning: Could not load bathymetry: {e}")
        
        # Load land polygons for collision avoidance
        try:
            url = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
            self.land_polygons = gpd.read_file(f"zip+{url}")
            print(f"Loaded {len(self.land_polygons)} land polygons")
        except Exception as e:
            print(f"Warning: Could not load land polygons: {e}")
    
    def get_depth(self, lon: float, lat: float) -> float:
        """Get bathymetry depth at coordinates (negative = underwater)"""
        if not self.bathymetry:
            return -1000  # Assume deep water if no data
        
        try:
            row, col = self.bathymetry.index(lon, lat)
            depth = self.bathymetry.read(1)[row, col]
            return float(depth)
        except:
            return -1000
    
    def is_on_land(self, lon: float, lat: float) -> bool:
        """Check if point is on land"""
        if self.land_polygons is None or self.land_polygons.empty:
            return False
        
        try:
            point = Point(lon, lat)
            # Use within() to check if point is within any land polygon
            result = self.land_polygons.geometry.contains(point)
            return result.any()  # Returns True if any polygon contains the point
        except Exception as e:
            print(f"Error checking land collision for ({lon}, {lat}): {e}")
            return False
    
    def generate_water_grid(self, start: Tuple[float, float], 
                           end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Generate grid of water waypoints between start and end
        
        Returns:
            List of (lat, lon) tuples representing navigable water nodes
        """
        # Define bounding box with padding
        min_lon = min(start[1], end[1]) - 5
        max_lon = max(start[1], end[1]) + 5
        min_lat = min(start[0], end[0]) - 5
        max_lat = max(start[0], end[0]) + 5
        
        # Generate grid
        lons = np.arange(min_lon, max_lon + self.resolution, self.resolution)
        lats = np.arange(min_lat, max_lat + self.resolution, self.resolution)
        
        water_nodes = []
        total_checked = 0
        land_count = 0
        
        for lon in lons:
            for lat in lats:
                total_checked += 1
                if not self.is_on_land(lon, lat):
                    water_nodes.append((lat, lon))  # (lat, lon) format
                else:
                    land_count += 1
        
        print(f"Grid generation: checked {total_checked} points, found {len(water_nodes)} water nodes, {land_count} on land")
        return water_nodes
    
    def compute_edge_weight(self, node_a: Tuple[float, float], 
                           node_b: Tuple[float, float],
                           use_bathymetry: bool = True) -> float:
        """
        Compute weighted cost between two nodes
        
        Penalties:
        - Shallow water (<100m): 5x penalty
        - Very shallow (<50m): 10x penalty
        - Base: nautical mile distance
        """
        # Base distance in nautical miles
        base_dist = haversine(node_a, node_b, unit='nmi')
        
        if not use_bathymetry or not self.bathymetry:
            return base_dist
        
        # Sample depths
        depth_a = self.get_depth(node_a[1], node_a[0])  # (lon, lat)
        depth_b = self.get_depth(node_b[1], node_b[0])
        avg_depth = (depth_a + depth_b) / 2
        
        # Apply depth penalties
        if avg_depth > -50:  # Very shallow
            penalty = 10.0
        elif avg_depth > -100:  # Shallow
            penalty = 5.0
        elif avg_depth > -200:  # Moderate
            penalty = 2.0
        else:  # Deep water
            penalty = 1.0
        
        return base_dist * penalty
    
    def build_graph(self, nodes: List[Tuple[float, float]], 
                   use_bathymetry: bool = True) -> nx.Graph:
        """
        Build navigation graph with weighted edges
        
        Args:
            nodes: List of (lat, lon) water waypoints
            use_bathymetry: Whether to apply depth penalties
        
        Returns:
            NetworkX graph with weighted edges
        """
        G = nx.Graph()
        
        # Maximum connection distance (in degrees, ~250nm)
        MAX_CONNECT_DIST = 4.0
        
        edges_added = 0
        for i, node_a in enumerate(nodes):
            for j, node_b in enumerate(nodes[i+1:], start=i+1):
                # Check if nodes are close enough to connect
                dist_deg = np.hypot(node_b[0] - node_a[0], node_b[1] - node_a[1])
                
                if dist_deg <= MAX_CONNECT_DIST:
                    weight = self.compute_edge_weight(node_a, node_b, use_bathymetry)
                    distance_nm = haversine(node_a, node_b, unit='nmi')
                    
                    G.add_edge(
                        i, j,
                        weight=weight,
                        distance=distance_nm,
                        depth_penalty=weight / distance_nm if distance_nm > 0 else 1.0
                    )
                    edges_added += 1
        
        print(f"Graph built: {len(nodes)} nodes, {edges_added} edges")
        return G
    
    def find_nearest_node(self, coord: Tuple[float, float], 
                         nodes: List[Tuple[float, float]]) -> int:
        """Find nearest node index to given coordinates"""
        distances = [haversine(coord, node, unit='nmi') for node in nodes]
        nearest_idx = int(np.argmin(distances))
        nearest_dist = distances[nearest_idx]
        print(f"Nearest node to {coord}: index {nearest_idx}, distance {nearest_dist:.2f} NM")
        return nearest_idx
    
    def optimize_route(self, start_coords: Tuple[float, float], 
                      end_coords: Tuple[float, float],
                      use_bathymetry: bool = True) -> Dict:
        """
        Compute optimal maritime route
        
        Args:
            start_coords: (lat, lon) origin
            end_coords: (lat, lon) destination
            use_bathymetry: Use depth-aware routing
        
        Returns:
            Dictionary with route data
        """
        print(f"Optimizing route from {start_coords} to {end_coords}")
        
        # Generate water grid
        nodes = self.generate_water_grid(start_coords, end_coords)
        
        if len(nodes) < 2:
            # Fallback to direct route
            print("Warning: Insufficient water nodes, using direct route")
            return {
                "route": [start_coords, end_coords],
                "total_distance_nm": round(haversine(start_coords, end_coords, unit='nmi'), 2),
                "waypoint_count": 2,
                "avg_depth_penalty": 1.0,
                "bathymetry_enabled": False,
                "warning": "Insufficient water nodes, using direct route"
            }
        
        # Build graph
        G = self.build_graph(nodes, use_bathymetry)
        
        if G.number_of_edges() == 0:
            print("Warning: No edges in graph, using direct route")
            return {
                "route": [start_coords, end_coords],
                "total_distance_nm": round(haversine(start_coords, end_coords, unit='nmi'), 2),
                "waypoint_count": 2,
                "avg_depth_penalty": 1.0,
                "bathymetry_enabled": False,
                "warning": "No navigable path found, using direct route"
            }
        
        # Find nearest nodes to start/end
        start_idx = self.find_nearest_node(start_coords, nodes)
        end_idx = self.find_nearest_node(end_coords, nodes)
        
        # Find optimal path
        try:
            path_indices = nx.astar_path(
                G,
                start_idx,
                end_idx,
                heuristic=lambda n1, n2: haversine(nodes[n1], nodes[n2], unit='nmi'),
                weight='weight'
            )
            
            print(f"Path found with {len(path_indices)} waypoints")
            
            # Extract coordinates
            route_coords = [nodes[i] for i in path_indices]
            
            # Calculate metrics
            total_distance = sum(
                G[path_indices[i]][path_indices[i+1]]['distance']
                for i in range(len(path_indices) - 1)
            )
            
            avg_penalty = np.mean([
                G[path_indices[i]][path_indices[i+1]]['depth_penalty']
                for i in range(len(path_indices) - 1)
            ]) if len(path_indices) > 1 else 1.0
            
            return {
                "route": route_coords,
                "total_distance_nm": round(total_distance, 2),
                "waypoint_count": len(route_coords),
                "avg_depth_penalty": round(avg_penalty, 2),
                "bathymetry_enabled": use_bathymetry
            }
        
        except nx.NetworkXNoPath:
            print(f"No path found between nodes {start_idx} and {end_idx}")
            return {
                "route": [start_coords, end_coords],
                "total_distance_nm": round(haversine(start_coords, end_coords, unit='nmi'), 2),
                "waypoint_count": 2,
                "avg_depth_penalty": 1.0,
                "bathymetry_enabled": False,
                "warning": "No path found, using direct route"
            }


def estimate_fuel_and_emissions(distance_nm: float, depth_penalty: float = 1.0) -> Dict:
    """
    Estimate fuel cost and emissions based on distance and depth penalty
    
    Shallow water increases drag and fuel consumption
    """
    # Base consumption: 0.3 tons/nm for container ship
    fuel_tons = distance_nm * 0.3 * depth_penalty
    fuel_cost_usd = fuel_tons * 600  # $600/ton IFO 380
    emissions_tons = fuel_tons * 3.1  # 3.1 kg CO2 per kg fuel
    
    return {
        "fuel_cost_usd": round(fuel_cost_usd, 2),
        "emissions_tons": round(emissions_tons, 2)
    }