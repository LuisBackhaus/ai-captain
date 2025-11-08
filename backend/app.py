from flask import Flask, jsonify, send_file
from flask_cors import CORS
from routes.shiproute import generate_ship_route
import io
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

@app.route('/api/generate-route', methods=['POST'])
def generate_route():
    """Generate ship route and return image"""
    try:
        # Generate the route image
        image_base64 = generate_ship_route()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{image_base64}',
            'message': 'Route generated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)