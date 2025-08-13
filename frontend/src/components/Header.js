import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Chip } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { AudioFile, Dashboard, BatchPrediction } from '@mui/icons-material';

function Header() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <AppBar position="static" elevation={0} sx={{ 
      background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
    }}>
      <Toolbar sx={{ minHeight: '72px' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <AudioFile sx={{ fontSize: 32, marginRight: 2 }} />
          <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: '-0.5px' }}>
            CallSight360
          </Typography>
          <Chip 
            label="v2.0" 
            size="small" 
            sx={{ 
              ml: 2, 
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              fontWeight: 600
            }} 
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            component={Link}
            to="/"
            startIcon={<Dashboard />}
            sx={{
              color: 'white',
              backgroundColor: isActive('/') ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
              '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
              borderRadius: 2,
              px: 3,
              fontWeight: 500
            }}
          >
            Dashboard
          </Button>
          
          <Button
            component={Link}
            to="/upload"
            startIcon={<AudioFile />}
            sx={{
              color: 'white',
              backgroundColor: isActive('/upload') ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
              '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
              borderRadius: 2,
              px: 3,
              fontWeight: 500
            }}
          >
            Analyze Call
          </Button>

          <Button
            component={Link}
            to="/batch"
            startIcon={<BatchPrediction />}
            sx={{
              color: 'white',
              backgroundColor: isActive('/batch') ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
              '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
              borderRadius: 2,
              px: 3,
              fontWeight: 500
            }}
          >
            Bulk Analysis
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header; 