import { useState, useEffect } from "react";
import {
  Box,
  Button,
  Typography,
  Paper,
  Container,
  CircularProgress,
  Alert,
  Autocomplete,
  TextField,
} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import DirectionsBoatIcon from "@mui/icons-material/DirectionsBoat";
import { RouteMap } from "./components/RouteMap";
import Grid from "@mui/material/Grid";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#0288d1",
    },
  },
});

interface Port {
  name: string;
  lat: number;
  lon: number;
  country: string;
}

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

function App() {
  const [ports, setPorts] = useState<Port[]>([]);
  const [selectedOrigin, setSelectedOrigin] = useState<Port | null>(null);
  const [selectedDestination, setSelectedDestination] = useState<Port | null>(
    null
  );
  const [routeData, setRouteData] = useState<RouteData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch available ports on mount
  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/ports")
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setPorts(data.ports);
          // Set default values
          setSelectedOrigin(
            data.ports.find((p: Port) => p.name === "Singapore") ||
              data.ports[0]
          );
          setSelectedDestination(
            data.ports.find((p: Port) => p.name === "Rotterdam") ||
              data.ports[1]
          );
        }
      })
      .catch((err) => console.error("Failed to fetch ports:", err));
  }, []);

  const handleGenerateRoute = async () => {
    if (!selectedOrigin || !selectedDestination) {
      setError("Please select both origin and destination ports");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Use the route-with-graph endpoint
      const response = await fetch("http://127.0.0.1:5000/api/generate-route", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin: selectedOrigin.name,
          destination: selectedDestination.name,
          use_bathymetry: false,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setRouteData(data);
        console.log("Route generated:", data);
      } else {
        setError(data.error || "Failed to generate route");
      }
    } catch (err) {
      setError(
        "Failed to connect to backend. Make sure Flask server is running on port 5000."
      );
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xl">
        <Box sx={{ py: 4 }}>
          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 700,
              color: "primary.main",
              mb: 4,
              textAlign: "center",
            }}
          >
            🚢 AI Captain - Maritime Route Optimizer
          </Typography>

          {/* Port Selection */}
          <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 5 }}>
                <Autocomplete
                  options={ports}
                  getOptionLabel={(option) =>
                    `${option.name} (${option.country})`
                  }
                  value={selectedOrigin}
                  onChange={(_, newValue) => setSelectedOrigin(newValue)}
                  renderInput={(params) => (
                    <TextField {...params} label="Origin Port" />
                  )}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 5 }}>
                <Autocomplete
                  options={ports}
                  getOptionLabel={(option) =>
                    `${option.name} (${option.country})`
                  }
                  value={selectedDestination}
                  onChange={(_, newValue) => setSelectedDestination(newValue)}
                  renderInput={(params) => (
                    <TextField {...params} label="Destination Port" />
                  )}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 2 }}>
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  startIcon={
                    loading ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      <DirectionsBoatIcon />
                    )
                  }
                  onClick={handleGenerateRoute}
                  disabled={loading || !selectedOrigin || !selectedDestination}
                  sx={{ height: "56px" }}
                >
                  {loading ? "Calculating..." : "Optimize Route"}
                </Button>
              </Grid>
            </Grid>
          </Paper>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Route Map */}
          {routeData && (
            <Paper elevation={4} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h5" gutterBottom>
                Route Visualization
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                🔵 Dashed line = Direct route | 🟢 Solid line = Optimized route
              </Typography>

              {/* Display metrics as a summary above the map */}
              {routeData.metrics && (
                <Box sx={{ mb: 2, display: "flex", gap: 3, flexWrap: "wrap" }}>
                  <Typography variant="body1">
                    <strong>Distance:</strong>{" "}
                    {routeData.metrics.optimized.distance_nm.toFixed(0)} NM
                  </Typography>
                  <Typography variant="body1">
                    <strong>Fuel Cost:</strong> $
                    {routeData.metrics.optimized.fuel_cost_usd.toLocaleString()}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Emissions:</strong>{" "}
                    {routeData.metrics.optimized.emissions_tons.toFixed(1)} tons
                    CO₂
                  </Typography>
                </Box>
              )}

              <RouteMap data={routeData} />
            </Paper>
          )}

          {/* Initial State Message */}
          {!routeData && !loading && (
            <Paper
              elevation={2}
              sx={{
                p: 5,
                textAlign: "center",
                backgroundColor: "#f5f5f5",
              }}
            >
              <DirectionsBoatIcon
                sx={{ fontSize: 60, color: "primary.main", mb: 2 }}
              />
              <Typography variant="h5" gutterBottom>
                Select ports and click "Optimize Route" to begin
              </Typography>
              <Typography variant="body1" color="textSecondary">
                The system will generate an optimal maritime route avoiding land
                and considering navigational constraints.
              </Typography>
            </Paper>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
