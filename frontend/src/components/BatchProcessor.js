import React, { useState, useRef, useEffect } from 'react';
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
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Collapse,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Tabs,
  Tab
} from '@mui/material';
import {
  Delete,
  CheckCircle,
  Error as ErrorIcon,
  BatchPrediction,
  Refresh,
  ExpandMore,
  ExpandLess,
  AudioFile,
  SentimentSatisfied,
  Psychology,
  Assessment,
  TrendingUp,
  PlayArrow,
  RecordVoiceOver,
  Pause
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import axios from 'axios';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`batch-tabpanel-${index}`}
      aria-labelledby={`batch-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}



function BatchProcessor() {
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [expandedResults, setExpandedResults] = useState({});
  const [activeAnalysisTab, setActiveAnalysisTab] = useState(0);
  const [audioStates, setAudioStates] = useState({}); // Track audio playing states
  const audioRefs = useRef({}); // Store audio references

  const onDrop = (acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending'
    }));
    setFiles(prev => [...prev, ...newFiles]);
    setResults(null);
    setError(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac']
    },
    multiple: true,
    maxSize: 100 * 1024 * 1024 // 100MB per file
  });

  const removeFile = (fileId) => {
    setFiles(files.filter(f => f.id !== fileId));
  };

  const handleBatchProcess = async () => {
    if (files.length === 0) return;

    setProcessing(true);
    setError(null);

    const formData = new FormData();
    files.forEach(({ file }) => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post('/api/v1/batch-analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResults(response.data);
    } catch (error) {
      setError(
        error.response?.data?.detail || 
        error.message || 
        'An error occurred during batch processing'
      );
    } finally {
      setProcessing(false);
    }
  };

  const handleReset = () => {
    setFiles([]);
    setResults(null);
    setError(null);
    setExpandedResults({});
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const toggleResultExpansion = (index) => {
    setExpandedResults(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const getStatusColor = (success) => {
    return success ? 'success' : 'error';
  };

  const getStatusIcon = (success) => {
    return success ? <CheckCircle color="success" /> : <ErrorIcon color="error" />;
  };

  const handleAnalysisTabChange = (event, newValue) => {
    setActiveAnalysisTab(newValue);
  };

  const formatScore = (score) => {
    return Math.round(score * 100);
  };

  const toggleAudioPlayer = async (index) => {
    const audioRef = audioRefs.current[index];
    const isCurrentlyPlaying = audioStates[index];
    
    try {
      if (isCurrentlyPlaying) {
        // Pause the audio
        if (audioRef) {
          audioRef.pause();
        }
        setAudioStates(prev => ({
          ...prev,
          [index]: false
        }));
      } else {
        // Play the audio
        if (audioRef) {
          await audioRef.play();
          setAudioStates(prev => ({
            ...prev,
            [index]: true
          }));
        }
      }
    } catch (error) {
      console.error('Audio playback error:', error);
      setAudioStates(prev => ({
        ...prev,
        [index]: false
      }));
    }
  };

  const handleAudioEnded = (index) => {
    setAudioStates(prev => ({
      ...prev,
      [index]: false
    }));
  };

  const initializeAudioRef = (index, audioUrl) => {
    if (!audioRefs.current[index] && audioUrl) {
      const audio = new Audio(audioUrl);
      audio.preload = 'metadata';
      audio.onended = () => handleAudioEnded(index);
      audio.onerror = (error) => {
        console.error('Audio loading error:', error);
        setAudioStates(prev => ({
          ...prev,
          [index]: false
        }));
      };
      audioRefs.current[index] = audio;
    }
  };

  // Calculate cumulative statistics
  const getCumulativeStats = () => {
    if (!results || !results.results) return null;

    const successfulResults = results.results.filter(r => r.success && r.analytics);
    
    if (successfulResults.length === 0) return null;

    // Sentiment distribution
    const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
    const intentCounts = {};
    const qualityScores = [];
    const resolutionCounts = { resolved: 0, unresolved: 0, in_progress: 0 };
    const totalWords = [];
    const totalDurations = [];

    successfulResults.forEach(result => {
      // Sentiment
      const sentiment = result.analytics.sentiment_analysis?.overall_sentiment?.polarity || 'neutral';
      sentimentCounts[sentiment]++;

      // Intent
      const intent = result.analytics.intent_analysis?.primary_intent || 'unknown';
      intentCounts[intent] = (intentCounts[intent] || 0) + 1;

      // Quality
      if (result.analytics.quality_metrics?.quality_score) {
        qualityScores.push(result.analytics.quality_metrics.quality_score);
      }

      // Resolution
      const outcome = result.analytics.quality_metrics?.call_outcome || 'unknown';
      if (resolutionCounts.hasOwnProperty(outcome)) {
        resolutionCounts[outcome]++;
      }

      // Metrics
      if (result.analytics.conversation_metrics?.total_words) {
        totalWords.push(result.analytics.conversation_metrics.total_words);
      }
      if (result.analytics.conversation_metrics?.estimated_duration_minutes) {
        totalDurations.push(result.analytics.conversation_metrics.estimated_duration_minutes);
      }
    });

    const avgQuality = qualityScores.length > 0 ? qualityScores.reduce((a, b) => a + b, 0) / qualityScores.length : 0;
    const avgWords = totalWords.length > 0 ? totalWords.reduce((a, b) => a + b, 0) / totalWords.length : 0;
    const avgDuration = totalDurations.length > 0 ? totalDurations.reduce((a, b) => a + b, 0) / totalDurations.length : 0;

    return {
      sentimentCounts,
      intentCounts,
      qualityScores,
      resolutionCounts,
      avgQuality,
      avgWords,
      avgDuration,
      successfulCount: successfulResults.length
    };
  };

  const cumulativeStats = getCumulativeStats();

  // Chart data
  const getSentimentChartData = () => {
    if (!cumulativeStats) return [];
    return [
      { name: 'Positive', value: cumulativeStats.sentimentCounts.positive, color: '#10b981' },
      { name: 'Neutral', value: cumulativeStats.sentimentCounts.neutral, color: '#6b7280' },
      { name: 'Negative', value: cumulativeStats.sentimentCounts.negative, color: '#ef4444' }
    ].filter(item => item.value > 0);
  };

  const getIntentChartData = () => {
    if (!cumulativeStats) return [];
    return Object.entries(cumulativeStats.intentCounts).map(([intent, count]) => ({
      name: intent.replace('_', ' '),
      value: count
    }));
  };

  const getQualityTrendData = () => {
    if (!results || !results.results) return [];
    return results.results
      .filter(r => r.success && r.analytics?.quality_metrics?.quality_score)
      .map((result, index) => ({
        call: index + 1,
        quality: formatScore(result.analytics.quality_metrics.quality_score),
        filename: result.filename?.substring(0, 10) + '...'
      }));
  };

  useEffect(() => {
    return () => {
      // Cleanup function to stop all audio when component unmounts
      // Copy the current ref value to avoid stale closure issues
      const currentAudioRefs = audioRefs.current;
      Object.values(currentAudioRefs).forEach(audio => {
        if (audio) {
          audio.pause();
          audio.src = ''; // Clear the source to stop loading
        }
      });
    };
  }, []);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" sx={{ fontWeight: 600, mb: 3, color: '#1f2937' }}>
        Bulk Call Analysis
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 4, color: '#6b7280' }}>
        Upload multiple call recordings to discover patterns and trends across your entire call center operation.
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
                borderColor: isDragActive ? 'primary.main' : files.length > 0 ? 'success.main' : 'grey.300',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                backgroundColor: isDragActive ? 'primary.50' : files.length > 0 ? 'success.50' : 'grey.50',
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'primary.50',
                },
              }}
            >
              <input {...getInputProps()} />
              
              <BatchPrediction sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                {isDragActive ? 'Drop your call recordings here' : 'Drag & drop your call recordings here'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                or click to browse multiple files
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Supports all common audio formats (max 100MB each)
              </Typography>
            </Box>

            {/* File List */}
            {files.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Selected Files ({files.length})
                </Typography>
                <List>
                  {files.map((fileItem) => (
                    <ListItem
                      key={fileItem.id}
                      sx={{
                        border: '1px solid',
                        borderColor: 'grey.200',
                        borderRadius: 1,
                        mb: 1,
                        backgroundColor: 'grey.50'
                      }}
                    >
                      <ListItemIcon>
                        <AudioFile />
                      </ListItemIcon>
                      <ListItemText
                        primary={fileItem.file.name}
                        secondary={formatFileSize(fileItem.file.size)}
                      />
                      <IconButton
                        edge="end"
                        onClick={() => removeFile(fileItem.id)}
                        disabled={processing}
                      >
                        <Delete />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Action Buttons */}
            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleBatchProcess}
                disabled={files.length === 0 || processing}
                startIcon={processing ? null : <BatchPrediction />}
                sx={{ flex: 1 }}
              >
                {processing ? 'Analyzing Calls...' : `Analyze ${files.length} Calls`}
              </Button>
              
              <Button
                variant="outlined"
                size="large"
                onClick={handleReset}
                disabled={processing}
                startIcon={<Refresh />}
              >
                Reset
              </Button>
            </Box>

            {/* Progress Bar */}
            {processing && (
              <Box sx={{ mt: 3 }}>
                <LinearProgress sx={{ mb: 1 }} />
                <Typography variant="body2" color="text.secondary" align="center">
                  Analyzing {files.length} call recordings...
                </Typography>
              </Box>
            )}

            {/* Error Display */}
            {error && (
              <Alert severity="error" sx={{ mt: 3 }} icon={<ErrorIcon />}>
                <strong>Batch Processing Failed:</strong> {error}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Info Panel */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center' }}>
                <BatchPrediction sx={{ mr: 1 }} />
                Bulk Analysis
              </Typography>
              
              <Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
                Analyze hundreds of calls at once to uncover trends, patterns, and opportunities for improvement.
              </Typography>

              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                INSIGHTS PER CALL
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                <Chip label="Customer Satisfaction" size="small" />
                <Chip label="Agent Performance" size="small" />
                <Chip label="Call Outcomes" size="small" />
                <Chip label="Key Topics" size="small" />
                <Chip label="Call Summary" size="small" />
              </Box>

              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                BEST PRACTICES
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Upload calls from different time periods for better trends
                • Mix different call types for comprehensive insights
                • Results include both successful and failed analyses
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Enhanced Results Section */}
      {results && (
        <Paper sx={{ mt: 4, p: 0 }}>
          <Box sx={{ p: 4, pb: 0 }}>
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
              Batch Analysis Results
            </Typography>

            {/* Summary Stats */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary" sx={{ fontWeight: 700 }}>
                      {results.batch_summary?.total_files || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Calls
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="success.main" sx={{ fontWeight: 700 }}>
                      {results.batch_summary?.successful || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Successful
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="error.main" sx={{ fontWeight: 700 }}>
                      {results.batch_summary?.failed || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Failed
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="info.main" sx={{ fontWeight: 700 }}>
                      {results.batch_summary?.total_processing_time_seconds || 0}s
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Time
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Enhanced Analytics Section */}
            {cumulativeStats && (
              <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={3}>
                  <Card sx={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white' }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <SentimentSatisfied sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {formatScore(cumulativeStats.avgQuality)}%
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Avg Quality Score
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card sx={{ background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)', color: 'white' }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Psychology sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {Math.round(cumulativeStats.avgWords)}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Avg Words/Call
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card sx={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', color: 'white' }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Assessment sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {cumulativeStats.avgDuration.toFixed(1)}m
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Avg Duration
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card sx={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', color: 'white' }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <TrendingUp sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {cumulativeStats.resolutionCounts.resolved || 0}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Resolved Calls
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}
          </Box>

          {/* Analysis Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeAnalysisTab} onChange={handleAnalysisTabChange}>
              <Tab label="Individual Results" icon={<AudioFile />} />
              <Tab label="Sentiment Overview" icon={<SentimentSatisfied />} />
              <Tab label="Intent Analysis" icon={<Psychology />} />
              <Tab label="Quality Trends" icon={<TrendingUp />} />
            </Tabs>
          </Box>

          {/* Individual Results Tab */}
          <TabPanel value={activeAnalysisTab} index={0}>
            <Box sx={{ px: 4 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Individual Call Analysis
              </Typography>
              
              {results.results?.map((result, index) => (
                <Card key={index} sx={{ mb: 2 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                        {getStatusIcon(result.success)}
                        <Box sx={{ ml: 2 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                            {result.filename}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                            <Chip 
                              label={result.success ? 'Success' : 'Failed'} 
                              color={getStatusColor(result.success)} 
                              size="small" 
                            />
                            {result.success && result.analytics?.intent_analysis?.primary_intent && (
                              <Chip 
                                label={result.analytics.intent_analysis.primary_intent.replace('_', ' ')} 
                                size="small" 
                                variant="outlined"
                              />
                            )}
                            {result.success && result.analytics?.sentiment_analysis?.overall_sentiment && (
                              <Chip 
                                label={`${result.analytics.sentiment_analysis.overall_sentiment.polarity} sentiment`}
                                color={
                                  result.analytics.sentiment_analysis.overall_sentiment.polarity === 'positive' ? 'success' :
                                  result.analytics.sentiment_analysis.overall_sentiment.polarity === 'negative' ? 'error' : 'default'
                                }
                                size="small"
                              />
                            )}
                            {result.success && result.analytics?.quality_metrics?.quality_score && (
                              <Chip 
                                label={`Quality: ${formatScore(result.analytics.quality_metrics.quality_score)}%`}
                                size="small"
                                color="info"
                              />
                            )}
                            {result.audio_url && (
                              <Chip 
                                icon={audioStates[index] ? <Pause /> : <PlayArrow />}
                                label={audioStates[index] ? "Pause Audio" : "Play Audio"}
                                size="small"
                                color="secondary"
                                variant={audioStates[index] ? "filled" : "outlined"}
                                onClick={() => {
                                  initializeAudioRef(index, result.audio_url);
                                  toggleAudioPlayer(index);
                                }}
                                sx={{ 
                                  cursor: 'pointer',
                                  '&:hover': {
                                    backgroundColor: audioStates[index] ? 'secondary.dark' : 'secondary.light',
                                    color: audioStates[index] ? 'white' : 'secondary.dark'
                                  }
                                }}
                              />
                            )}
                          </Box>
                        </Box>
                      </Box>
                      
                      <IconButton onClick={() => toggleResultExpansion(index)}>
                        {expandedResults[index] ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    </Box>

                    {!result.success && (
                      <Alert severity="error" sx={{ mt: 2 }}>
                        <strong>Error:</strong> {result.error}
                      </Alert>
                    )}

                    <Collapse in={expandedResults[index]} timeout="auto" unmountOnExit>
                      <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                        {result.success && (
                          <Grid container spacing={3}>
                            {/* Transcript Section */}
                            <Grid item xs={12}>
                              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                                <RecordVoiceOver sx={{ mr: 1, verticalAlign: 'middle' }} />
                                Full Transcript
                              </Typography>
                              {result.transcription?.transcript ? (
                                <Paper sx={{ p: 2, backgroundColor: 'grey.50', maxHeight: 200, overflow: 'auto' }}>
                                  <Typography variant="body2" sx={{ fontFamily: 'monospace', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                                    {result.transcription.transcript}
                                  </Typography>
                                </Paper>
                              ) : (
                                <Paper sx={{ p: 2, backgroundColor: 'grey.50', textAlign: 'center' }}>
                                  <Typography variant="body2" color="text.secondary">
                                    No transcript available
                                  </Typography>
                                </Paper>
                              )}
                            </Grid>

                            {/* Analytics Summary */}
                            <Grid item xs={12} md={6}>
                              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                                Key Metrics
                              </Typography>
                              <TableContainer component={Paper} sx={{ backgroundColor: 'grey.50' }}>
                                <Table size="small">
                                  <TableBody>
                                    <TableRow>
                                      <TableCell><strong>Sentiment</strong></TableCell>
                                      <TableCell>
                                        <Chip 
                                          label={result.analytics?.sentiment_analysis?.overall_sentiment?.polarity || 'N/A'}
                                          size="small"
                                          color={
                                            result.analytics?.sentiment_analysis?.overall_sentiment?.polarity === 'positive' ? 'success' :
                                            result.analytics?.sentiment_analysis?.overall_sentiment?.polarity === 'negative' ? 'error' : 'default'
                                          }
                                        />
                                      </TableCell>
                                    </TableRow>
                                    <TableRow>
                                      <TableCell><strong>Intent</strong></TableCell>
                                      <TableCell>{result.analytics?.intent_analysis?.primary_intent?.replace('_', ' ') || 'N/A'}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                      <TableCell><strong>Quality Score</strong></TableCell>
                                      <TableCell>{result.analytics?.quality_metrics?.quality_score ? `${formatScore(result.analytics.quality_metrics.quality_score)}%` : 'N/A'}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                      <TableCell><strong>Call Outcome</strong></TableCell>
                                      <TableCell>
                                        <Chip 
                                          label={result.analytics?.quality_metrics?.call_outcome || 'N/A'}
                                          size="small"
                                          color={result.analytics?.quality_metrics?.call_outcome === 'resolved' ? 'success' : 'warning'}
                                        />
                                      </TableCell>
                                    </TableRow>
                                    <TableRow>
                                      <TableCell><strong>Duration</strong></TableCell>
                                      <TableCell>{result.analytics?.conversation_metrics?.estimated_duration_minutes ? `${result.analytics.conversation_metrics.estimated_duration_minutes} min` : 'N/A'}</TableCell>
                                    </TableRow>
                                  </TableBody>
                                </Table>
                              </TableContainer>
                            </Grid>

                            {/* Key Insights */}
                            <Grid item xs={12} md={6}>
                              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                                Key Insights
                              </Typography>
                              <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                                {result.analytics?.summary?.summary_points ? (
                                  <List dense>
                                    {result.analytics.summary.summary_points.map((point, idx) => (
                                      <ListItem key={idx} sx={{ py: 0.5 }}>
                                        <Typography variant="body2">• {point}</Typography>
                                      </ListItem>
                                    ))}
                                  </List>
                                ) : (
                                  <Typography variant="body2" color="text.secondary">
                                    No summary available
                                  </Typography>
                                )}
                              </Paper>
                              
                              {result.analytics?.summary?.key_phrases && (
                                <Box sx={{ mt: 2 }}>
                                  <Typography variant="subtitle2" gutterBottom>Key Phrases:</Typography>
                                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                    {result.analytics.summary.key_phrases.slice(0, 6).map((phrase, idx) => (
                                      <Chip key={idx} label={phrase} size="small" variant="outlined" />
                                    ))}
                                  </Box>
                                </Box>
                              )}
                            </Grid>


                          </Grid>
                        )}
                      </Box>
                    </Collapse>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </TabPanel>

          {/* Sentiment Overview Tab */}
          <TabPanel value={activeAnalysisTab} index={1}>
            <Box sx={{ px: 4 }}>
              <Typography variant="h6" sx={{ mb: 3 }}>
                Sentiment Analysis Overview
              </Typography>
              
              {cumulativeStats && getSentimentChartData().length > 0 ? (
                <Grid container spacing={4}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Overall Sentiment Distribution
                    </Typography>
                    <Box sx={{ height: 300 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={getSentimentChartData()}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={120}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {getSentimentChartData().map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </Box>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Sentiment Statistics
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Card sx={{ textAlign: 'center', backgroundColor: '#f0fdf4' }}>
                          <CardContent>
                            <Typography variant="h4" color="success.main" sx={{ fontWeight: 700 }}>
                              {cumulativeStats.sentimentCounts.positive}
                            </Typography>
                            <Typography variant="body2">Positive</Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={4}>
                        <Card sx={{ textAlign: 'center', backgroundColor: '#f9fafb' }}>
                          <CardContent>
                            <Typography variant="h4" color="text.secondary" sx={{ fontWeight: 700 }}>
                              {cumulativeStats.sentimentCounts.neutral}
                            </Typography>
                            <Typography variant="body2">Neutral</Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={4}>
                        <Card sx={{ textAlign: 'center', backgroundColor: '#fef2f2' }}>
                          <CardContent>
                            <Typography variant="h4" color="error.main" sx={{ fontWeight: 700 }}>
                              {cumulativeStats.sentimentCounts.negative}
                            </Typography>
                            <Typography variant="body2">Negative</Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>

                    <Box sx={{ mt: 3 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Sentiment Insights
                      </Typography>
                      <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                        <Typography variant="body2">
                          • {((cumulativeStats.sentimentCounts.positive / cumulativeStats.successfulCount) * 100).toFixed(1)}% of calls had positive sentiment
                        </Typography>
                        <Typography variant="body2">
                          • {((cumulativeStats.sentimentCounts.negative / cumulativeStats.successfulCount) * 100).toFixed(1)}% of calls had negative sentiment
                        </Typography>
                        <Typography variant="body2">
                          • Average quality score: {formatScore(cumulativeStats.avgQuality)}%
                        </Typography>
                      </Paper>
                    </Box>
                  </Grid>
                </Grid>
              ) : (
                <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: 'grey.50' }}>
                  <Typography variant="body1" color="text.secondary">
                    No sentiment data available from successful analyses
                  </Typography>
                </Paper>
              )}
            </Box>
          </TabPanel>

          {/* Intent Analysis Tab */}
          <TabPanel value={activeAnalysisTab} index={2}>
            <Box sx={{ px: 4 }}>
              <Typography variant="h6" sx={{ mb: 3 }}>
                Intent Analysis Overview
              </Typography>
              
              {cumulativeStats && getIntentChartData().length > 0 ? (
                <Grid container spacing={4}>
                  <Grid item xs={12} md={8}>
                    <Typography variant="subtitle1" gutterBottom>
                      Intent Distribution
                    </Typography>
                    <Box sx={{ height: 300 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={getIntentChartData()}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="value" fill="#4f46e5" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle1" gutterBottom>
                      Intent Breakdown
                    </Typography>
                    <List>
                      {getIntentChartData().map((intent, index) => (
                        <ListItem key={index} sx={{ py: 1 }}>
                          <ListItemText
                            primary={intent.name}
                            secondary={`${intent.value} calls (${((intent.value / cumulativeStats.successfulCount) * 100).toFixed(1)}%)`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>
                </Grid>
              ) : (
                <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: 'grey.50' }}>
                  <Typography variant="body1" color="text.secondary">
                    No intent data available from successful analyses
                  </Typography>
                </Paper>
              )}
            </Box>
          </TabPanel>

          {/* Quality Trends Tab */}
          <TabPanel value={activeAnalysisTab} index={3}>
            <Box sx={{ px: 4 }}>
              <Typography variant="h6" sx={{ mb: 3 }}>
                Quality Trends & Performance
              </Typography>
              
              {getQualityTrendData().length > 0 ? (
                <Grid container spacing={4}>
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom>
                      Quality Score Trend Across Calls
                    </Typography>
                    <Box sx={{ height: 300 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={getQualityTrendData()}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="call" />
                          <YAxis domain={[0, 100]} />
                          <Tooltip />
                          <Line type="monotone" dataKey="quality" stroke="#4f46e5" strokeWidth={2} />
                        </LineChart>
                      </ResponsiveContainer>
                    </Box>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Resolution Status
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Card sx={{ textAlign: 'center', backgroundColor: '#f0fdf4' }}>
                          <CardContent>
                            <Typography variant="h4" color="success.main" sx={{ fontWeight: 700 }}>
                              {cumulativeStats?.resolutionCounts.resolved || 0}
                            </Typography>
                            <Typography variant="body2">Resolved</Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={4}>
                        <Card sx={{ textAlign: 'center', backgroundColor: '#fffbeb' }}>
                          <CardContent>
                            <Typography variant="h4" color="warning.main" sx={{ fontWeight: 700 }}>
                              {cumulativeStats?.resolutionCounts.in_progress || 0}
                            </Typography>
                            <Typography variant="body2">In Progress</Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={4}>
                        <Card sx={{ textAlign: 'center', backgroundColor: '#fef2f2' }}>
                          <CardContent>
                            <Typography variant="h4" color="error.main" sx={{ fontWeight: 700 }}>
                              {cumulativeStats?.resolutionCounts.unresolved || 0}
                            </Typography>
                            <Typography variant="body2">Unresolved</Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Performance Insights
                    </Typography>
                    <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        • Average quality score: <strong>{formatScore(cumulativeStats?.avgQuality || 0)}%</strong>
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        • Average call duration: <strong>{cumulativeStats?.avgDuration?.toFixed(1) || 0} minutes</strong>
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        • Average words per call: <strong>{Math.round(cumulativeStats?.avgWords || 0)}</strong>
                      </Typography>
                      <Typography variant="body2">
                        • Resolution rate: <strong>{cumulativeStats ? ((cumulativeStats.resolutionCounts.resolved / cumulativeStats.successfulCount) * 100).toFixed(1) : 0}%</strong>
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              ) : (
                <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: 'grey.50' }}>
                  <Typography variant="body1" color="text.secondary">
                    No quality data available from successful analyses
                  </Typography>
                </Paper>
              )}
            </Box>
          </TabPanel>
        </Paper>
      )}
    </Container>
  );
}

export default BatchProcessor; 