import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import io
import base64

def generate_ship_route():
    """Generate ship route visualization and return as base64 encoded image"""
    
    # --- Base setup ---
    fig = plt.figure(figsize=(9, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([95, 130, 0, 35])  # zoom to SEA–China region

    # Add basic map features
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5)

    # --- Data ---
    # Original route: Singapore → Shanghai
    route_original = [
        (103.8198, 1.3521),   # Singapore
        (110, 10),
        (120, 20),
        (121.4737, 31.2304)   # Shanghai
    ]

    # Optimized route (manually adjusted north to avoid storm region)
    route_optimized = [
        (103.8198, 1.3521),   # Singapore
        (108, 5),
        (112, 10),
        (118, 25),
        (121.4737, 31.2304)   # Shanghai
    ]

    # Hurricane area (red circle)
    hurricane_center = (115, 15)
    hurricane_radius = 5  # degrees (rough approximation)
    circle = plt.Circle(hurricane_center, hurricane_radius, color='red', alpha=0.3,
                        transform=ccrs.PlateCarree(), label='Hurricane zone')
    ax.add_patch(circle)

    # --- Plot routes ---
    x1, y1 = zip(*route_original)
    ax.plot(x1, y1, color='blue', linewidth=2.5, label='Original Route')

    x2, y2 = zip(*route_optimized)
    ax.plot(x2, y2, color='green', linewidth=2.5, linestyle='--', label='Optimized Route')

    # Mark start and end
    ax.plot(route_original[0][0], route_original[0][1], 'o', color='black', markersize=6)
    ax.text(103.9, 1.5, 'Singapore', fontsize=9)
    ax.plot(route_original[-1][0], route_original[-1][1], 'o', color='black', markersize=6)
    ax.text(121.7, 31.3, 'Shanghai', fontsize=9)

    # --- Finish ---
    plt.title("Singapore → Shanghai Route (Original vs. Optimized)")
    plt.legend(loc='lower left')
    plt.tight_layout()
    
    # Save to bytes buffer instead of file
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    # Encode to base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    plt.close(fig)
    
    return image_base64