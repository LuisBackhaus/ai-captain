import networkx as nx
from haversine import haversine

def calculate_weather_risk(point1, point2, weather_data):
    """Calculate weather risk between two points (0-1 scale)"""
    # TODO: Integrate with real weather API
    # For now, check if route intersects hardcoded hazard zones
    if weather_data:
        for hazard in weather_data:
            # Simple check: if midpoint is near hazard center
            midpoint = ((point1[0] + point2[0])/2, (point1[1] + point2[1])/2)
            hazard_center = (hazard["center"][0], hazard["center"][1])
            distance_to_hazard = haversine(midpoint, hazard_center)
            
            if distance_to_hazard < hazard.get("radius", 5) * 111:  # degrees to km
                return 0.8  # High risk
    return 0.0  # No risk

def estimate_fuel_cost(distance_nm, weather_penalty):
    """Estimate fuel cost in USD for given nautical miles"""
    # Typical container ship: ~0.3 tons fuel per nautical mile
    # Fuel price: ~$600/ton (IFO 380 bunker fuel)
    base_cost = distance_nm * 0.3 * 600
    return base_cost * (1 + weather_penalty * 0.5)

def calculate_emissions(distance_nm, weather_penalty):
    """Calculate CO2 emissions in tons"""
    # ~3.1 kg CO2 per kg fuel burned
    fuel_tons = distance_nm * 0.3 * (1 + weather_penalty * 0.5)
    return fuel_tons * 3.1

def create_route_graph(waypoints, weather_data=None):
    """Create weighted graph of possible routes"""
    G = nx.Graph()
    MAX_SEGMENT_NM = 500  # Maximum direct sailing distance in nautical miles
    
    for i, point1 in enumerate(waypoints):
        for j, point2 in enumerate(waypoints):
            if i >= j:  # Avoid duplicates and self-loops
                continue
            
            # Calculate distance in nautical miles
            distance_nm = haversine(point1, point2, unit='nmi')
            
            # Only connect nearby waypoints
            if distance_nm > MAX_SEGMENT_NM:
                continue
            
            # Calculate penalties
            weather_penalty = calculate_weather_risk(point1, point2, weather_data or [])
            fuel_cost = estimate_fuel_cost(distance_nm, weather_penalty)
            emissions = calculate_emissions(distance_nm, weather_penalty)
            
            # Combined weight (coefficients can be adjusted)
            weight = (
                0.4 * distance_nm +      # Distance priority
                0.3 * (fuel_cost/1000) + # Normalize fuel cost
                0.2 * weather_penalty * 1000 +  # Weather safety
                0.1 * (emissions/10)     # Normalize emissions
            )
            
            G.add_edge(i, j, 
                      weight=weight, 
                      distance=distance_nm, 
                      fuel_cost=fuel_cost, 
                      emissions=emissions,
                      weather_risk=weather_penalty)
    
    return G

def optimize_route(start_coords, end_coords, waypoints, weather_data=None):
    """
    Find optimal route using A* algorithm
    
    Args:
        start_coords: (lat, lon) tuple for origin
        end_coords: (lat, lon) tuple for destination
        waypoints: List of (lat, lon) tuples representing possible waypoints
        weather_data: List of hazard zones (optional)
    
    Returns:
        dict with route coordinates and metadata
    """
    # Add start and end to waypoints
    all_waypoints = [start_coords] + waypoints + [end_coords]
    
    # Create graph
    G = create_route_graph(all_waypoints, weather_data)
    
    # Find path using A* with haversine heuristic
    try:
        route_indices = nx.astar_path(
            G, 
            0,  # Start index
            len(all_waypoints) - 1,  # End index
            heuristic=lambda n1, n2: haversine(all_waypoints[n1], all_waypoints[n2], unit='nmi'),
            weight='weight'
        )
        
        # Extract route coordinates and calculate totals
        route_coords = [all_waypoints[i] for i in route_indices]
        
        # Calculate total metrics
        total_distance = 0
        total_fuel_cost = 0
        total_emissions = 0
        
        for i in range(len(route_indices) - 1):
            edge_data = G[route_indices[i]][route_indices[i+1]]
            total_distance += edge_data['distance']
            total_fuel_cost += edge_data['fuel_cost']
            total_emissions += edge_data['emissions']
        
        return {
            "route": route_coords,
            "total_distance_nm": round(total_distance, 2),
            "total_fuel_cost_usd": round(total_fuel_cost, 2),
            "total_emissions_tons": round(total_emissions, 2),
            "waypoint_count": len(route_coords)
        }
    
    except nx.NetworkXNoPath:
        # No path found - return direct route
        return {
            "route": [start_coords, end_coords],
            "total_distance_nm": haversine(start_coords, end_coords, unit='nmi'),
            "total_fuel_cost_usd": 0,
            "total_emissions_tons": 0,
            "waypoint_count": 2,
            "warning": "No optimal path found, returning direct route"
        }