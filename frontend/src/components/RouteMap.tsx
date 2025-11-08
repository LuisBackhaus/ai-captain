import { MapContainer, TileLayer, Polyline, Circle, Marker, Popup, useMap } from 'react-leaflet';
import { LatLngExpression, latLngBounds } from 'leaflet';
import { useEffect } from 'react';

interface RouteData {
  origin: { name: string; coords: [number, number] };
  destination: { name: string; coords: [number, number] };
  routes: {
    optimized: [number, number][];
    direct: [number, number][];
  };
  hazards: Array<{ center: [number, number]; radius: number; type: string }>;
  metrics?: {
    optimized: {
      distance_nm: number;
      fuel_cost_usd: number;
      emissions_tons: number;
    };
    direct: {
      distance_nm: number;
    };
  };
}

interface RouteMapProps {
  data: RouteData;
}

// Component to auto-fit bounds
function AutoFitBounds({ data }: { data: RouteData }) {
  const map = useMap();
  
  useEffect(() => {
    const allPoints: LatLngExpression[] = [
      ...data.routes.optimized,
      ...data.routes.direct,
    ];
    
    if (allPoints.length > 0) {
      const bounds = latLngBounds(allPoints as [number, number][]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [data, map]);
  
  return null;
}

export function RouteMap({ data }: RouteMapProps) {
  // Calculate center point between origin and destination
  const centerLat = (data.origin.coords[0] + data.destination.coords[0]) / 2;
  const centerLon = (data.origin.coords[1] + data.destination.coords[1]) / 2;

  return (
    <MapContainer
      center={[centerLat, centerLon]}
      zoom={5}
      style={{ height: '600px', width: '100%', borderRadius: '8px' }}
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      <AutoFitBounds data={data} />
      
      {/* Direct route (dashed blue) */}
      <Polyline
        positions={data.routes.direct as LatLngExpression[]}
        color="#1976d2"
        weight={3}
        opacity={0.6}
        dashArray="10, 10"
      />
      
      {/* Optimized route (solid green) */}
      <Polyline
        positions={data.routes.optimized as LatLngExpression[]}
        color="#2e7d32"
        weight={4}
        opacity={0.9}
      />
      
      {/* Origin marker */}
      <Marker position={data.origin.coords as LatLngExpression}>
        <Popup>
          <strong>{data.origin.name}</strong>
          <br />
          Origin Port
        </Popup>
      </Marker>
      
      {/* Destination marker */}
      <Marker position={data.destination.coords as LatLngExpression}>
        <Popup>
          <strong>{data.destination.name}</strong>
          <br />
          Destination Port
        </Popup>
      </Marker>
      
      {/* Hazard zones */}
      {data.hazards.map((hazard, index) => (
        <Circle
          key={index}
          center={hazard.center as LatLngExpression}
          radius={hazard.radius * 111000}  // Convert degrees to meters
          pathOptions={{
            color: '#d32f2f',
            fillColor: '#f44336',
            fillOpacity: 0.3,
          }}
        >
          <Popup>
            <strong>Hazard Zone</strong>
            <br />
            Type: {hazard.type}
            <br />
            Radius: {hazard.radius * 60} nautical miles
          </Popup>
        </Circle>
      ))}
    </MapContainer>
  );
}