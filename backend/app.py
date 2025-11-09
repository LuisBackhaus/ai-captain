from flask import Flask, jsonify, request
from flask_cors import CORS
from routes.shiproute import generate_ship_route
from routes.route_optimizer import optimize_route as simple_optimize
from routes.bathymetry_router import BathymetryRouter, estimate_fuel_and_emissions
from data.ports import MAJOR_PORTS, get_port_coordinates, get_all_ports
from haversine import haversine
import traceback
import json

app = Flask(__name__)
CORS(app)

# Initialize bathymetry router (will work with or without bathymetry file)
print("Initializing BathymetryRouter...")
bathy_router = BathymetryRouter(bathymetry_path=None, resolution=0.5)
print("BathymetryRouter initialized successfully")

@app.route('/api/ports', methods=['GET'])
def get_ports():
    """Return list of available ports"""
    return jsonify({
        'success': True,
        'ports': [
            {
                'name': name,
                'lat': data['lat'],
                'lon': data['lon'],
                'country': data['country']
            }
            for name, data in MAJOR_PORTS.items()
        ]
    })

@app.route('/api/generate-route', methods=['POST'])
def generate_route_api():
    """Generate optimized ship route with bathymetry awareness"""
    try:
        data = request.get_json()
        origin = data.get('origin', 'Singapore')
        destination = data.get('destination', 'Shanghai')
        use_bathymetry = data.get('use_bathymetry', True)
        
        print(f"\n=== Route Request ===")
        print(f"Origin: {origin}")
        print(f"Destination: {destination}")
        print(f"Use bathymetry: {use_bathymetry}")
        
        # Get coordinates
        origin_coords = get_port_coordinates(origin)
        destination_coords = get_port_coordinates(destination)
        
        print(f"Origin coords: {origin_coords}")
        print(f"Destination coords: {destination_coords}")
        
        # Compute bathymetry-aware route
        optimized = bathy_router.optimize_route(
            origin_coords, 
            destination_coords,
            use_bathymetry=use_bathymetry
        )
        
        # Compute simple direct route for comparison
        direct_distance = haversine(origin_coords, destination_coords, unit='nmi')
        
        # Estimate costs
        opt_costs = estimate_fuel_and_emissions(
            optimized['total_distance_nm'],
            optimized.get('avg_depth_penalty', 1.0)
        )
        
        direct_costs = estimate_fuel_and_emissions(direct_distance, 1.0)
        
        # TODO [ ]: No hardcoded hazards - can add weather API integration later
        hazards = []
        
        response_data = {
            'success': True,
            'origin': {'name': origin, 'coords': origin_coords},
            'destination': {'name': destination, 'coords': destination_coords},
            'routes': {
                'optimized': optimized['route'],
                'direct': [origin_coords, destination_coords]
            },
            'metrics': {
                'optimized': {
                    'distance_nm': optimized['total_distance_nm'],
                    'fuel_cost_usd': opt_costs['fuel_cost_usd'],
                    'emissions_tons': opt_costs['emissions_tons'],
                    'depth_penalty': optimized.get('avg_depth_penalty', 1.0),
                    'waypoint_count': optimized['waypoint_count']
                },
                'direct': {
                    'distance_nm': round(direct_distance, 2),
                    'fuel_cost_usd': direct_costs['fuel_cost_usd'],
                    'emissions_tons': direct_costs['emissions_tons']
                }
            },
            'hazards': hazards,
            'bathymetry_enabled': optimized.get('bathymetry_enabled', False)
        }
        
        if 'warning' in optimized:
            response_data['warning'] = optimized['warning']
        
        print(f"Route optimized successfully: {optimized['waypoint_count']} waypoints")
        return jsonify(response_data)
    
    except Exception as e:
        print(f"\n=== ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/generate-route-image', methods=['POST'])
def generate_route_image():
    """Legacy endpoint - returns PNG image (backup)"""
    try:
        image_base64 = generate_ship_route()
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{image_base64}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_waypoint_grid(start, end, grid_density=5):
    """Generate intermediate waypoints in a grid"""
    lat1, lon1 = start
    lat2, lon2 = end
    
    waypoints = []
    for i in range(1, grid_density):
        for j in range(1, grid_density):
            lat = lat1 + (lat2 - lat1) * (i / grid_density)
            lon = lon1 + (lon2 - lon1) * (j / grid_density)
            waypoints.append((lat, lon))
    
    return waypoints

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)