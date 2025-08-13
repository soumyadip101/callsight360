import React, { useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  TextField,
  Grid,
  Chip,
  Divider
} from '@mui/material';
import {
  CloudUpload,
  AudioFile,
  CheckCircle,
  Error as ErrorIcon,
  Analytics,
  Refresh
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function AudioUpload() {
  const [file, setFile] = useState(null);
  const [callId, setCallId] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const onDrop = (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setResult(null);
      setError(null);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac']
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    if (callId.trim()) {
      formData.append('call_id', callId.trim());
    }

    try {
      const response = await axios.post('/api/v1/upload-and-analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
        },
      });

              setResult(response.data);
      } catch (error) {
      setError(
        error.response?.data?.detail || 
        error.message || 
        'An error occurred during processing'
      );
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const handleReset = () => {
    setFile(null);
    setCallId('');
    setResult(null);
    setError(null);
    setProgress(0);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };



  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" sx={{ fontWeight: 600, mb: 3, color: '#1f2937' }}>
        Call Analysis
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 4, color: '#6b7280' }}>
        Upload your call recording to instantly understand customer satisfaction, agent performance, and call outcomes.
      </Typography>

      <Grid container spacing={4}>
        {/* Upload Section */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4 }}>
            {/* File Upload Area */}
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : file ? 'success.main' : 'grey.300',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                backgroundColor: isDragActive ? 'primary.50' : file ? 'success.50' : 'grey.50',
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'primary.50',
                },
              }}
            >
              <input {...getInputProps()} />
              
              {file ? (
                <Box>
                  <CheckCircle sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    File Selected
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 1 }}>
                    {file.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatFileSize(file.size)}
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <CloudUpload sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    {isDragActive ? 'Drop your call recording here' : 'Drag & drop your call recording here'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    or click to browse files
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Supports all common audio formats (max 100MB)
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Call ID Input */}
            <Box sx={{ mt: 3 }}>
              <TextField
                fullWidth
                label="Call ID (Optional)"
                value={callId}
                onChange={(e) => setCallId(e.target.value)}
                placeholder="Enter a unique identifier for this call"
                variant="outlined"
                disabled={uploading}
              />
            </Box>

            {/* Action Buttons */}
            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleUpload}
                disabled={!file || uploading}
                startIcon={uploading ? null : <Analytics />}
                sx={{ flex: 1 }}
              >
                {uploading ? 'Analyzing Call...' : 'Analyze Call'}
              </Button>
              
              <Button
                variant="outlined"
                size="large"
                onClick={handleReset}
                disabled={uploading}
                startIcon={<Refresh />}
              >
                Reset
              </Button>
            </Box>

            {/* Progress Bar */}
            {uploading && (
              <Box sx={{ mt: 3 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={progress} 
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary" align="center">
                  {progress < 100 ? `Uploading... ${progress}%` : 'Analyzing your call...'}
                </Typography>
              </Box>
            )}

            {/* Error Display */}
                    {error && (
          <Alert severity="error" sx={{ mt: 3 }} icon={<ErrorIcon />}>
            <strong>Processing Failed:</strong> {error}
          </Alert>
        )}

        {result && !result.success && (
          <Alert severity="warning" sx={{ mt: 3 }}>
            <strong>Transcription Failed:</strong> {result.error}
            {result.audio_url && (
              <div>
                <br />
                However, your audio file was saved and you can still listen to it.
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => navigate(`/results/${result.call_id}`, { state: { result } })}
                  sx={{ ml: 2 }}
                >
                  View Details
                </Button>
              </div>
            )}
          </Alert>
        )}
          </Paper>
        </Grid>

        {/* Info Panel */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center' }}>
                <AudioFile sx={{ mr: 1 }} />
                How It Works
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  STEP 1: TRANSCRIBE
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  Convert your call recording into readable text
                </Typography>

                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  STEP 2: ANALYZE
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  Understand customer emotions and call outcomes
                </Typography>

                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  STEP 3: INSIGHTS
                </Typography>
                <Typography variant="body2">
                  Get actionable recommendations to improve performance
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                WHAT YOU'LL GET
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip label="Customer Satisfaction" size="small" />
                <Chip label="Call Intent" size="small" />
                <Chip label="Agent Performance" size="small" />
                <Chip label="Call Summary" size="small" />
                <Chip label="Key Topics" size="small" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Results Section */}
      {result && (
        <Paper sx={{ mt: 4, p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Call Insights
            </Typography>
                          <Button
                variant="outlined"
                onClick={() => navigate(`/results/${result.call_id}`, { state: { result } })}
                startIcon={<Analytics />}
              >
                View Full Report
              </Button>
          </Box>

          {/* Audio Playback */}
          {result.audio_url && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>Audio Playback</Typography>
              <Paper sx={{ p: 2 }}>
                <audio controls style={{ width: '100%' }}>
                  <source src={result.audio_url} />
                  Your browser does not support the audio element.
                </audio>
              </Paper>
            </Box>
          )}

          <Grid container spacing={3}>
            {/* Quick Stats */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>Quick Summary</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                <Chip 
                  label={`Call ID: ${result.call_id}`} 
                  color="primary" 
                />
                <Chip 
                  label={`Processing Time: ${result.processing_times?.total_seconds}s`} 
                  color="success" 
                />
                <Chip 
                  label={`Confidence: ${Math.round(result.transcription?.confidence * 100)}%`} 
                  color="info" 
                />
              </Box>
            </Grid>

            {/* Key Insights */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>Key Findings</Typography>
              {result.analytics?.sentiment_analysis?.overall_sentiment && (
                <Box sx={{ mb: 1 }}>
                  <Chip 
                    label={`Sentiment: ${result.analytics.sentiment_analysis.overall_sentiment.polarity}`}
                    color={
                      result.analytics.sentiment_analysis.overall_sentiment.polarity === 'positive' ? 'success' :
                      result.analytics.sentiment_analysis.overall_sentiment.polarity === 'negative' ? 'error' : 'default'
                    }
                    sx={{ mr: 1 }}
                  />
                </Box>
              )}
              {result.analytics?.intent_analysis?.primary_intent && (
                <Box sx={{ mb: 1 }}>
                  <Chip 
                    label={`Intent: ${result.analytics.intent_analysis.primary_intent.replace('_', ' ')}`}
                    color="secondary"
                  />
                </Box>
              )}
            </Grid>

            {/* Full Transcript */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Full Transcript
                {result.transcription?.transcript && (
                  <Chip 
                    label={`${result.transcription.transcript.split('\n').length} segments`}
                    size="small" 
                    sx={{ ml: 2 }}
                  />
                )}
              </Typography>
              <Paper sx={{ p: 3, backgroundColor: 'grey.50', maxHeight: 400, overflow: 'auto' }}>
                {result.transcription?.transcript ? (
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontFamily: 'monospace',
                      whiteSpace: 'pre-line',
                      lineHeight: 1.6
                    }}
                  >
                    {result.transcription.transcript}
                  </Typography>
                ) : (
                  <Typography variant="body2" color="error" sx={{ fontStyle: 'italic' }}>
                    No transcript available - transcription may have failed
                  </Typography>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Container>
  );
}

export default AudioUpload; 