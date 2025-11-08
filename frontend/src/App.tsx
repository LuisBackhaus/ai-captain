import { useState } from "react";
import {
  Box,
  Button,
  Typography,
  Paper,
  Container,
  CircularProgress,
  Alert,
} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import DirectionsBoatIcon from "@mui/icons-material/DirectionsBoat";

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

function App() {
  const [showRoute, setShowRoute] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [routeImage, setRouteImage] = useState<string | null>(null);

  const handleGenerateRoute = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/generate-route", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.success) {
        setRouteImage(data.image);
        setShowRoute(true);
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
      <Container maxWidth="lg">
        <Box
          sx={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            py: 4,
          }}
        >
          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 700,
              color: "primary.main",
              mb: 4,
            }}
          >
            AI Captain - Ship Route Generator
          </Typography>

          <Button
            variant="contained"
            size="large"
            startIcon={
              loading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <DirectionsBoatIcon />
              )
            }
            onClick={handleGenerateRoute}
            disabled={loading}
            sx={{
              px: 6,
              py: 2,
              fontSize: "1.1rem",
              fontWeight: 600,
              borderRadius: 2,
              boxShadow: 3,
              "&:hover": {
                boxShadow: 6,
                transform: "translateY(-2px)",
              },
              transition: "all 0.3s ease",
            }}
          >
            {loading ? "Generating..." : "Generate Ship Route"}
          </Button>

          {error && (
            <Alert severity="error" sx={{ mt: 3, width: "100%" }}>
              {error}
            </Alert>
          )}

          {showRoute && routeImage && (
            <Paper
              elevation={4}
              sx={{
                mt: 6,
                p: 3,
                borderRadius: 3,
                width: "100%",
                animation: "fadeIn 0.5s ease-in",
                "@keyframes fadeIn": {
                  from: {
                    opacity: 0,
                    transform: "translateY(20px)",
                  },
                  to: {
                    opacity: 1,
                    transform: "translateY(0)",
                  },
                },
              }}
            >
              <Typography
                variant="h5"
                component="h2"
                gutterBottom
                sx={{
                  fontWeight: 600,
                  color: "text.primary",
                  mb: 3,
                  textAlign: "center",
                }}
              >
                Generated Route
              </Typography>
              <Box
                component="img"
                src={routeImage}
                alt="Ship Route"
                sx={{
                  width: "100%",
                  maxHeight: "500px",
                  objectFit: "contain",
                  borderRadius: 2,
                  boxShadow: 2,
                }}
              />
            </Paper>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
