"""
Major international container ports by region
Data source: World Shipping Council 2023
"""

MAJOR_PORTS = {
    # Asia-Pacific
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
    },
    "Busan": {
        "lat": 35.1796,
        "lon": 129.0756,
        "country": "South Korea",
        "region": "East Asia",
        "teu_millions": 22.0
    },
    "Hong Kong": {
        "lat": 22.3193,
        "lon": 114.1694,
        "country": "Hong Kong",
        "region": "South China",
        "teu_millions": 17.8
    },
    "Qingdao": {
        "lat": 36.0671,
        "lon": 120.3826,
        "country": "China",
        "region": "East Asia",
        "teu_millions": 15.3
    },
    "Tianjin": {
        "lat": 39.1422,
        "lon": 117.1767,
        "country": "China",
        "region": "North China",
        "teu_millions": 14.5
    },
    "Tokyo": {
        "lat": 35.6532,
        "lon": 139.8395,
        "country": "Japan",
        "region": "East Asia",
        "teu_millions": 5.2
    },
    
    # Middle East & South Asia
    "Dubai": {
        "lat": 25.2769,
        "lon": 55.2962,
        "country": "UAE",
        "region": "Middle East",
        "teu_millions": 14.1
    },
    "Port Klang": {
        "lat": 3.0048,
        "lon": 101.3950,
        "country": "Malaysia",
        "region": "Southeast Asia",
        "teu_millions": 13.6
    },
    "Colombo": {
        "lat": 6.9271,
        "lon": 79.8612,
        "country": "Sri Lanka",
        "region": "South Asia",
        "teu_millions": 7.2
    },
    
    # Europe
    "Rotterdam": {
        "lat": 51.9244,
        "lon": 4.4777,
        "country": "Netherlands",
        "region": "Northern Europe",
        "teu_millions": 14.5
    },
    "Antwerp": {
        "lat": 51.2194,
        "lon": 4.4025,
        "country": "Belgium",
        "region": "Northern Europe",
        "teu_millions": 12.0
    },
    "Hamburg": {
        "lat": 53.5511,
        "lon": 9.9937,
        "country": "Germany",
        "region": "Northern Europe",
        "teu_millions": 8.7
    },
    "Felixstowe": {
        "lat": 51.9542,
        "lon": 1.3515,
        "country": "United Kingdom",
        "region": "Northern Europe",
        "teu_millions": 3.8
    },
    "Valencia": {
        "lat": 39.4699,
        "lon": -0.3763,
        "country": "Spain",
        "region": "Southern Europe",
        "teu_millions": 5.6
    },
    "Piraeus": {
        "lat": 37.9495,
        "lon": 23.6347,
        "country": "Greece",
        "region": "Southern Europe",
        "teu_millions": 5.4
    },
    
    # Americas
    "Los Angeles": {
        "lat": 33.7405,
        "lon": -118.2713,
        "country": "USA",
        "region": "West Coast USA",
        "teu_millions": 10.7
    },
    "Long Beach": {
        "lat": 33.7701,
        "lon": -118.1937,
        "country": "USA",
        "region": "West Coast USA",
        "teu_millions": 9.4
    },
    "New York": {
        "lat": 40.6692,
        "lon": -74.0445,
        "country": "USA",
        "region": "East Coast USA",
        "teu_millions": 7.8
    },
    "Savannah": {
        "lat": 32.0835,
        "lon": -81.0998,
        "country": "USA",
        "region": "East Coast USA",
        "teu_millions": 5.9
    },
    "Santos": {
        "lat": -23.9608,
        "lon": -46.3334,
        "country": "Brazil",
        "region": "South America",
        "teu_millions": 4.4
    },
    "Vancouver": {
        "lat": 49.2827,
        "lon": -123.1207,
        "country": "Canada",
        "region": "West Coast Canada",
        "teu_millions": 3.6
    },
    
    # Africa
    "Tangier": {
        "lat": 35.7595,
        "lon": -5.8340,
        "country": "Morocco",
        "region": "North Africa",
        "teu_millions": 8.6
    },
    "Port Said": {
        "lat": 31.2653,
        "lon": 32.3019,
        "country": "Egypt",
        "region": "North Africa",
        "teu_millions": 6.1
    },
    "Durban": {
        "lat": -29.8587,
        "lon": 31.0218,
        "country": "South Africa",
        "region": "Southern Africa",
        "teu_millions": 2.8
    },
    
    # Oceania
    "Melbourne": {
        "lat": -37.8136,
        "lon": 144.9631,
        "country": "Australia",
        "region": "Oceania",
        "teu_millions": 3.0
    },
    "Sydney": {
        "lat": -33.8688,
        "lon": 151.2093,
        "country": "Australia",
        "region": "Oceania",
        "teu_millions": 2.6
    },
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