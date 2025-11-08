"""
Top 5 container ports by TEU (Twenty-foot Equivalent Unit) volume
Data source: World Shipping Council 2023
"""

MAJOR_PORTS = {
    "Shanghai": {
        "lat": 31.2304,
        "lon": 121.4737,
        "country": "China",
        "region": "East Asia",
        "teu_millions": 47.3
    },
    "Singapore": {
        "lat": 1.3521,
        "lon": 103.8198,
        "country": "Singapore",
        "region": "Southeast Asia",
        "teu_millions": 37.2
    },
    "Ningbo-Zhoushan": {
        "lat": 29.8683,
        "lon": 121.5440,
        "country": "China",
        "region": "East Asia",
        "teu_millions": 33.4
    },
    "Shenzhen": {
        "lat": 22.5431,
        "lon": 114.0579,
        "country": "China",
        "region": "East Asia",
        "teu_millions": 30.0
    },
    "Guangzhou": {
        "lat": 23.1291,
        "lon": 113.2644,
        "country": "China",
        "region": "South China",
        "teu_millions": 24.2
    }
}

def get_port_coordinates(port_name: str) -> tuple[float, float]:
    """Get (lat, lon) for a port"""
    if port_name not in MAJOR_PORTS:
        raise ValueError(f"Unknown port: {port_name}")
    port = MAJOR_PORTS[port_name]
    return (port["lat"], port["lon"])

def get_all_ports() -> list[str]:
    """Get list of all available port names"""
    return list(MAJOR_PORTS.keys())