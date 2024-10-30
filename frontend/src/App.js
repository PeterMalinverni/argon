import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Box,
  CssBaseline,
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

function App() {
  const [query, setQuery] = useState('');
  const [steps, setSteps] = useState(0);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!query) {
      alert('Please enter a search term.');
      return;
    }

    setLoading(true);
    setResults([]);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:5000/search?q=${encodeURIComponent(query)}&steps=${steps}`
      );
      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResults(data);
      }
    } catch (err) {
      console.error('Error:', err);
      setError('An error occurred while fetching data.');
    } finally {
      setLoading(false);
    }
  };

  // Create a dark theme
  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#1976d2',
      },
    },
  });

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline /> {/* This applies the theme's background color */}
      <Container className="App">
        <Typography variant="h4" gutterBottom>
          Clinical Trials Search
        </Typography>
        <form onSubmit={handleSubmit}>
          <Box mb={2}>
            <TextField
              label="Enter search terms (e.g., NSCLC immunotherapy)"
              variant="outlined"
              fullWidth
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
              InputLabelProps={{
                style: { color: darkTheme.palette.text.primary },
              }}
            />
          </Box>
          <Box mb={2}>
            <Select
              value={steps}
              onChange={(e) => setSteps(e.target.value)}
              fullWidth
              variant="outlined"
            >
              <MenuItem value={0}>Direct matches only</MenuItem>
              <MenuItem value={1}>1 step away</MenuItem>
              <MenuItem value={2}>2 steps away</MenuItem>
              <MenuItem value={3}>3 steps away</MenuItem>
            </Select>
          </Box>
          <Box mb={2}>
            <Button type="submit" variant="contained" color="primary" fullWidth>
              Search
            </Button>
          </Box>
        </form>
        {loading && (
          <Box display="flex" justifyContent="center" my={2}>
            <CircularProgress />
          </Box>
        )}
        {error && (
          <Box my={2}>
            <Alert severity="error">{error}</Alert>
          </Box>
        )}
        {results.length > 0 && (
          <Typography variant="subtitle1" gutterBottom>
            Showing {results.length} result{results.length === 1 ? '' : 's'}
          </Typography>
        )}
        {results.length > 0 && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>NCT Number</TableCell>
                  <TableCell>Study Title</TableCell>
                  <TableCell>Conditions</TableCell>
                  <TableCell>Interventions</TableCell>
                  <TableCell>Study Status</TableCell>
                  <TableCell>Study URL</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((trial) => (
                  <TableRow key={trial['NCT Number']}>
                    <TableCell>{trial['NCT Number']}</TableCell>
                    <TableCell>{trial['Study Title']}</TableCell>
                    <TableCell>{trial['Conditions']}</TableCell>
                    <TableCell>{trial['Interventions']}</TableCell>
                    <TableCell>{trial['Study Status']}</TableCell>
                    <TableCell>
                      <a
                        href={trial['Study URL']}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="App-link"
                        style={{ color: darkTheme.palette.primary.main }}
                      >
                        View
                      </a>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;
