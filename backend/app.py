from flask import Flask, jsonify, request
from flask_cors import CORS
from routes.shiproute import generate_ship_route  # Keep for backup
from routes.route_optimizer import optimize_route
from data.ports import MAJOR_PORTS, get_port_coordinates, get_all_ports

app = Flask(__name__)
CORS(app)

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
    """Generate optimized ship route"""
    try:
        data = request.get_json()
        origin = data.get('origin', 'Singapore')
        destination = data.get('destination', 'Shanghai')
        
        # Get coordinates
        origin_coords = get_port_coordinates(origin)
        destination_coords = get_port_coordinates(destination)
        
        # Generate waypoints (simplified grid for MVP)
        waypoints = generate_waypoint_grid(origin_coords, destination_coords)
        
        # Hardcoded hazards for demo (replace with weather API later)
        hazards = [
            {"center": [15, 115], "radius": 5, "type": "tropical_storm"}
        ]
        
        # Optimize route
        optimized = optimize_route(origin_coords, destination_coords, waypoints, hazards)
        
        # Also generate comparison: direct route (no optimization)
        direct_route = {
            "route": [origin_coords, destination_coords],
            "total_distance_nm": optimized["total_distance_nm"] * 0.8  # Direct is shorter
        }
        
        return jsonify({
            'success': True,
            'origin': {'name': origin, 'coords': origin_coords},
            'destination': {'name': destination, 'coords': destination_coords},
            'routes': {
                'optimized': optimized['route'],
                'direct': direct_route['route']
            },
            'metrics': {
                'optimized': {
                    'distance_nm': optimized['total_distance_nm'],
                    'fuel_cost_usd': optimized['total_fuel_cost_usd'],
                    'emissions_tons': optimized['total_emissions_tons']
                },
                'direct': {
                    'distance_nm': direct_route['total_distance_nm']
                }
            },
            'hazards': hazards
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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