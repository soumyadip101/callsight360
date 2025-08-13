import React from 'react';
import { 
  Container, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  Button, 
  Box,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper
} from '@mui/material';
import { 
  AudioFile, 
  BatchPrediction, 
  CheckCircle, 
  Psychology,
  Speed,
  Security,
  CloudOff,
  Analytics
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios from 'axios';

function Dashboard() {
  const { data: healthData } = useQuery('health', () =>
    axios.get('/api/v1/health').then(res => res.data)
  );

  const { data: statsData } = useQuery('stats', () =>
    axios.get('/api/v1/stats').then(res => res.data)
  );

  const features = [
    {
      icon: <AudioFile sx={{ fontSize: 40, color: '#4f46e5' }} />,
      title: 'Smart Transcription',
      description: 'Instantly convert call recordings into accurate text transcripts',
      status: healthData?.capabilities?.audio_transcription ? 'Available' : 'Unavailable'
    },
    {
      icon: <Psychology sx={{ fontSize: 40, color: '#7c3aed' }} />,
      title: 'Call Intelligence',
      description: 'Understand customer emotions, intent, and call outcomes automatically',
      status: healthData?.capabilities?.conversation_analytics ? 'Available' : 'Unavailable'
    },
    {
      icon: <BatchPrediction sx={{ fontSize: 40, color: '#10b981' }} />,
      title: 'Bulk Analysis',
      description: 'Process hundreds of calls at once for comprehensive insights',
      status: healthData?.capabilities?.batch_processing ? 'Available' : 'Unavailable'
    }
  ];

  const benefits = [
    { icon: <Security />, text: 'Secure & Private: Your call data stays on your servers' },
    { icon: <Speed />, text: 'Lightning Fast: Get insights in seconds, not hours' },
    { icon: <CloudOff />, text: 'Works Offline: No internet dependency or cloud costs' },
    { icon: <Analytics />, text: 'Always Accurate: Consistent results you can trust' }
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, color: '#1f2937' }}>
          CallSight360
        </Typography>
        <Typography variant="h5" sx={{ color: '#4f46e5', mb: 2, fontWeight: 600 }}>
          AI-powered call center conversation analytics platform
        </Typography>
        <Typography variant="h6" sx={{ color: '#6b7280', mb: 4, maxWidth: 700, mx: 'auto' }}>
          Transform your call center calls into actionable insights. Improve operational efficiency for a better customer experience.
        </Typography>
        
        {healthData && (
          <Chip
            icon={<CheckCircle />}
            label={`System Status: ${healthData.status}`}
            color="success"
            sx={{ fontSize: '1rem', py: 2, px: 1 }}
          />
        )}
      </Box>

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 6 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)', color: 'white' }}>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <AudioFile sx={{ fontSize: 60, mb: 2 }} />
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
                Analyze Single Call
              </Typography>
              <Typography sx={{ mb: 3, opacity: 0.9 }}>
                Upload any call recording and get instant insights on customer satisfaction and agent performance
              </Typography>
              <Button
                component={Link}
                to="/upload"
                variant="contained"
                size="large"
                sx={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.2)', 
                  '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.3)' },
                  color: 'white',
                  fontWeight: 600
                }}
              >
                Analyze Call
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white' }}>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <BatchPrediction sx={{ fontSize: 60, mb: 2 }} />
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
                Bulk Analysis
              </Typography>
              <Typography sx={{ mb: 3, opacity: 0.9 }}>
                Upload multiple call recordings and discover trends across your entire call center
              </Typography>
              <Button
                component={Link}
                to="/batch"
                variant="contained"
                size="large"
                sx={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.2)', 
                  '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.3)' },
                  color: 'white',
                  fontWeight: 600
                }}
              >
                Start Bulk Analysis
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Features Overview */}
      <Typography variant="h4" sx={{ fontWeight: 600, mb: 3, color: '#1f2937' }}>
        Powerful Features
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 6 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {feature.icon}
                  <Box sx={{ ml: 2, flex: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {feature.title}
                    </Typography>
                    <Chip 
                      label={feature.status} 
                      color={feature.status === 'Available' ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                </Box>
                <Typography color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Benefits and Technology Stack */}
      <Grid container spacing={4}>
        <Grid item xs={12} md={8}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 3, color: '#1f2937' }}>
            Why Choose CallSight360?
          </Typography>
          
          <Paper sx={{ p: 3, height: 'fit-content' }}>
            <List>
              {benefits.map((benefit, index) => (
                <ListItem key={index} sx={{ py: 1 }}>
                  <ListItemIcon>
                    {React.cloneElement(benefit.icon, { sx: { color: '#10b981' } })}
                  </ListItemIcon>
                  <ListItemText 
                    primary={benefit.text}
                    primaryTypographyProps={{ fontWeight: 500 }}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 3, color: '#1f2937' }}>
            Technology Stack
          </Typography>
          
          <Paper sx={{ p: 3, height: 'fit-content' }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              AI TRANSCRIPTION
            </Typography>
            <Typography variant="body2" sx={{ mb: 3 }}>
              Whisper AI (Faster-Whisper)
            </Typography>

            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              ANALYTICS ENGINE
            </Typography>
            <Typography variant="body2" sx={{ mb: 3 }}>
              NLP Powered Analytics
            </Typography>

            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              SUPPORTED AUDIO FORMATS
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {statsData?.capabilities?.transcription?.supported_formats?.join(', ') || 
               '.wav, .mp3, .m4a, .flac, .ogg, .aac, etc.'}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard; 