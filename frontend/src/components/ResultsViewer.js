import React, { useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  LinearProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Slider,
  Alert,
  AlertTitle
} from '@mui/material';
import {
  SentimentSatisfied,
  Psychology,
  Assessment,
  Summarize,
  Star,
  RecordVoiceOver,
  PlayArrow,
  Pause,
  VolumeUp,
  VolumeOff
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock data - in real app this would come from props or API
const mockAnalysisResult = {
  call_id: "call_12345",
  success: true,
  filename: "sample_call.wav",
  audio_url: null, // No audio file for mock data
  transcription: {
    transcript: "Agent: Hello, thank you for calling our support line. How can I help you today? Customer: Hi, I'm having trouble with my billing. I was charged twice for this month's service and I need to get this resolved. Agent: I'm sorry to hear about that billing issue. Let me look into your account right away. Can you please provide me with your account number? Customer: Yes, it's 1234567890. Agent: Thank you. I can see the duplicate charge here. This appears to be a system error on our end. I'll process a refund for the duplicate charge immediately. Customer: Thank you so much! How long will it take for the refund to show up? Agent: The refund should appear in your account within 3-5 business days. Is there anything else I can help you with today? Customer: No, that's perfect. Thank you for resolving this so quickly! Agent: You're very welcome! Have a great day!",
    confidence: 0.92,
    language: "en-US",
    processing_time_seconds: 2.3
  },
  analytics: {
    sentiment_analysis: {
      overall_sentiment: {
        polarity: "positive",
        confidence: 0.78,
        scores: { neg: 0.1, neu: 0.3, pos: 0.6, compound: 0.78 }
      },
      agent_sentiment: {
        polarity: "positive",
        confidence: 0.85,
        scores: { neg: 0.05, neu: 0.25, pos: 0.7, compound: 0.85 }
      },
      customer_sentiment: {
        polarity: "positive",
        confidence: 0.72,
        scores: { neg: 0.15, neu: 0.35, pos: 0.5, compound: 0.72 }
      },
      actionable_insights: [
        {
          category: "Customer Satisfaction",
          insight: "Customer expressed satisfaction with the quick resolution of their billing issue.",
          action: "Follow up with customer satisfaction survey to maintain high service quality.",
          priority: "low"
        },
        {
          category: "Process Efficiency",
          insight: "Issue was resolved in a single call without escalation.",
          action: "Document this successful resolution approach for training purposes.",
          priority: "medium"
        },
        {
          category: "Agent Performance",
          insight: "Agent demonstrated excellent problem-solving skills and empathy.",
          action: "Consider this agent for mentoring new team members.",
          priority: "medium"
        }
      ]
    },
    intent_analysis: {
      primary_intent: "billing_inquiry",
      intent_scores: {
        billing_inquiry: { score: 8, confidence: 0.9, matches: ["billing", "charged", "refund"] },
        technical_support: { score: 1, confidence: 0.1, matches: ["trouble"] }
      },
      confidence: 0.9
    },
    conversation_metrics: {
      total_turns: 6,
      agent_turns: 3,
      customer_turns: 3,
      turn_ratio: 1.0,
      estimated_duration_minutes: 2.5,
      total_words: 156,
      agent_word_count: 78,
      customer_word_count: 78,
      average_words_per_turn: 26
    },
    quality_metrics: {
      quality_score: 0.89,
      positive_indicators: 12,
      negative_indicators: 2,
      call_outcome: "resolved",
      outcome_confidence: 0.95,
      escalation_risk: 0.1,
      politeness_score: 0.92
    },
    summary: {
      summary_points: [
        "Customer contacted regarding billing inquiry",
        "Overall conversation tone was positive",
        "Issue was resolved successfully"
      ],
      key_phrases: [
        "billing inquiry resolution",
        "duplicate charge identified", 
        "refund processed quickly",
        "customer satisfaction achieved",
        "agent problem-solving skills",
        "positive interaction outcome",
        "efficient service delivery"
      ],
      primary_topic: "Billing Inquiry",
      conversation_tone: "positive",
      brief_summary: "Customer contacted regarding billing inquiry. Overall conversation tone was positive. Issue was resolved successfully."
    }
  }
};

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analysis-tabpanel-${index}`}
      aria-labelledby={`analysis-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

// Audio Player Component
function AudioPlayer({ audioUrl, callId }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);

  const togglePlayPause = async () => {
    if (audioRef.current) {
      try {
        if (isPlaying) {
          audioRef.current.pause();
          setIsPlaying(false);
        } else {
          await audioRef.current.play();
          setIsPlaying(true);
        }
      } catch (error) {
        console.error('Audio playback error:', error);
        setIsPlaying(false);
        // You could show a user-friendly error message here
      }
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleAudioError = (error) => {
    console.error('Audio loading error:', error);
    setIsPlaying(false);
  };

  const handleSeek = (event, newValue) => {
    if (audioRef.current) {
      audioRef.current.currentTime = newValue;
      setCurrentTime(newValue);
    }
  };

  const handleVolumeChange = (event, newValue) => {
    const volumeValue = newValue / 100;
    setVolume(volumeValue);
    if (audioRef.current) {
      audioRef.current.volume = volumeValue;
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!audioUrl) {
    return (
      <Paper sx={{ p: 3, mb: 3, textAlign: 'center', backgroundColor: 'grey.50' }}>
        <Typography variant="body2" color="text.secondary">
          Audio file not available for playback
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <RecordVoiceOver sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Audio Playback
        </Typography>
        <Chip 
          label={`Call: ${callId}`} 
          size="small" 
          sx={{ ml: 2 }} 
        />
      </Box>

      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
        onError={handleAudioError}
        preload="metadata"
      >
        <source src={audioUrl} />
        Your browser does not support the audio element.
      </audio>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton 
          onClick={togglePlayPause} 
          size="large"
          sx={{ color: 'primary.main' }}
        >
          {isPlaying ? <Pause /> : <PlayArrow />}
        </IconButton>

        <Box sx={{ flex: 1 }}>
          <Slider
            value={currentTime}
            max={duration || 100}
            onChange={handleSeek}
            sx={{ mb: 1 }}
          />
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" color="text.secondary">
              {formatTime(currentTime)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {formatTime(duration)}
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 120 }}>
          <IconButton onClick={toggleMute} size="small">
            {isMuted ? <VolumeOff /> : <VolumeUp />}
          </IconButton>
          <Slider
            value={volume * 100}
            onChange={handleVolumeChange}
            sx={{ ml: 1 }}
            size="small"
          />
        </Box>
      </Box>
    </Paper>
  );
}

function ResultsViewer() {
  const [activeTab, setActiveTab] = useState(0);
  const location = useLocation();
  
  // Use real data if passed via navigation state, otherwise use mock data
  const result = location.state?.result || mockAnalysisResult;

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#10b981';
      case 'negative': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const formatScore = (score) => {
    return Math.round(score * 100);
  };

  // Chart data
  const sentimentData = [
    { name: 'Positive', value: formatScore(result.analytics.sentiment_analysis.overall_sentiment.scores.pos), color: '#10b981' },
    { name: 'Neutral', value: formatScore(result.analytics.sentiment_analysis.overall_sentiment.scores.neu), color: '#6b7280' },
    { name: 'Negative', value: formatScore(result.analytics.sentiment_analysis.overall_sentiment.scores.neg), color: '#ef4444' }
  ];

  const qualityData = [
    { name: 'Quality Score', value: formatScore(result.analytics.quality_metrics.quality_score) },
    { name: 'Politeness', value: formatScore(result.analytics.quality_metrics.politeness_score) },
    { name: 'Resolution', value: formatScore(result.analytics.quality_metrics.outcome_confidence) }
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 2, color: '#1f2937' }}>
          Analysis Results
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Chip label={`Call ID: ${result.call_id}`} color="primary" />
          <Chip label={`File: ${result.filename}`} variant="outlined" />
          <Chip 
            label={`Confidence: ${formatScore(result.transcription.confidence)}%`} 
            color="success" 
          />
          <Chip 
            label={`Duration: ${result.analytics.conversation_metrics.estimated_duration_minutes} min`} 
            variant="outlined" 
          />
        </Box>
      </Box>

      {/* Key Metrics Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <SentimentSatisfied sx={{ fontSize: 40, color: getSentimentColor(result.analytics.sentiment_analysis.overall_sentiment.polarity), mb: 1 }} />
              <Typography variant="h6" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                {result.analytics.sentiment_analysis.overall_sentiment.polarity}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Overall Sentiment
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={formatScore(result.analytics.sentiment_analysis.overall_sentiment.confidence)} 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Psychology sx={{ fontSize: 40, color: '#7c3aed', mb: 1 }} />
              <Typography variant="h6" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                {result.analytics.intent_analysis.primary_intent.replace('_', ' ')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Primary Intent
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={formatScore(result.analytics.intent_analysis.confidence)} 
                sx={{ mt: 1 }}
                color="secondary"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Star sx={{ fontSize: 40, color: '#f59e0b', mb: 1 }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {formatScore(result.analytics.quality_metrics.quality_score)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Quality Score
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={formatScore(result.analytics.quality_metrics.quality_score)} 
                sx={{ mt: 1 }}
                color="warning"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assessment sx={{ fontSize: 40, color: result.analytics.quality_metrics.call_outcome === 'resolved' ? '#10b981' : '#ef4444', mb: 1 }} />
              <Typography variant="h6" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                {result.analytics.quality_metrics.call_outcome}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Call Outcome
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={formatScore(result.analytics.quality_metrics.outcome_confidence)} 
                sx={{ mt: 1 }}
                color={result.analytics.quality_metrics.call_outcome === 'resolved' ? 'success' : 'error'}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Analysis Tabs */}
      <Paper sx={{ p: 0 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Transcript" icon={<RecordVoiceOver />} />
            <Tab label="Sentiment Analysis" icon={<SentimentSatisfied />} />
            <Tab label="Intent & Quality" icon={<Psychology />} />
            <Tab label="Summary & Insights" icon={<Summarize />} />
          </Tabs>
        </Box>

        {/* Transcript Tab */}
        <TabPanel value={activeTab} index={0}>
          {/* Audio Player */}
          <AudioPlayer audioUrl={result.audio_url} callId={result.call_id} />
          
          <Typography variant="h6" gutterBottom>
            Full Transcript
          </Typography>
          <Paper sx={{ p: 3, backgroundColor: 'grey.50', maxHeight: 500, overflow: 'auto' }}>
            {result.transcription?.transcript ? (
              <Typography variant="body1" sx={{ fontFamily: 'monospace', lineHeight: 1.8, whiteSpace: 'pre-line' }}>
                {result.transcription.transcript}
              </Typography>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Transcript Not Available
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {result.success === false ? 
                    `Transcription failed: ${result.error}` : 
                    'The transcript could not be generated for this audio file.'
                  }
                </Typography>
                {result.audio_url && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    You can still listen to the original audio recording above.
                  </Typography>
                )}
              </Box>
            )}
          </Paper>

          
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>Transcription Details</Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="Confidence Score" secondary={`${formatScore(result.transcription.confidence)}%`} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Language" secondary={result.transcription.language} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Processing Time" secondary={`${result.transcription.processing_time_seconds}s`} />
                </ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>Conversation Metrics</Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="Total Turns" secondary={result.analytics.conversation_metrics.total_turns} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Total Words" secondary={result.analytics.conversation_metrics.total_words} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Estimated Duration" secondary={`${result.analytics.conversation_metrics.estimated_duration_minutes} minutes`} />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Sentiment Analysis Tab */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Sentiment Distribution
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {sentimentData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Actionable Insights
              </Typography>
              <Box sx={{ maxHeight: 300, overflowY: 'auto' }}>
                {result.analytics.sentiment_analysis.actionable_insights && result.analytics.sentiment_analysis.actionable_insights.length > 0 ? (
                  result.analytics.sentiment_analysis.actionable_insights.map((insight, index) => (
                    <Alert 
                      key={index} 
                      severity={insight.priority === 'high' ? 'error' : insight.priority === 'medium' ? 'warning' : 'info'}
                      sx={{ mb: 1 }}
                    >
                      <AlertTitle sx={{ fontWeight: 'bold' }}>
                        {insight.category}
                      </AlertTitle>
                      {insight.insight}
                      {insight.action && (
                        <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                          <strong>Recommended Action:</strong> {insight.action}
                        </Typography>
                      )}
                    </Alert>
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                    No specific actionable insights identified for this conversation.
                  </Typography>
                )}
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Speaker-Specific Sentiment
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>Agent Sentiment</Typography>
                      <Chip 
                        label={result.analytics.sentiment_analysis.agent_sentiment?.polarity || 'N/A'} 
                        color={result.analytics.sentiment_analysis.agent_sentiment?.polarity === 'positive' ? 'success' : result.analytics.sentiment_analysis.agent_sentiment?.polarity === 'negative' ? 'error' : 'default'}
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        Confidence: {formatScore(result.analytics.sentiment_analysis.agent_sentiment?.confidence || 0)}%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>Customer Sentiment</Typography>
                      <Chip 
                        label={result.analytics.sentiment_analysis.customer_sentiment?.polarity || 'N/A'} 
                        color={result.analytics.sentiment_analysis.customer_sentiment?.polarity === 'positive' ? 'success' : result.analytics.sentiment_analysis.customer_sentiment?.polarity === 'negative' ? 'error' : 'default'}
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        Confidence: {formatScore(result.analytics.sentiment_analysis.customer_sentiment?.confidence || 0)}%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Intent & Quality Tab */}
        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Intent Analysis
              </Typography>
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>Primary Intent</Typography>
                  <Chip 
                    label={result.analytics.intent_analysis.primary_intent.replace('_', ' ')} 
                    color="primary" 
                    sx={{ mb: 2 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    Confidence: {formatScore(result.analytics.intent_analysis.confidence)}%
                  </Typography>
                </CardContent>
              </Card>

              <Typography variant="subtitle1" gutterBottom>All Intent Scores</Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Intent</TableCell>
                      <TableCell align="right">Score</TableCell>
                      <TableCell align="right">Confidence</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(result.analytics.intent_analysis.intent_scores).map(([intent, data]) => (
                      <TableRow key={intent}>
                        <TableCell>{intent.replace('_', ' ')}</TableCell>
                        <TableCell align="right">{data.score}</TableCell>
                        <TableCell align="right">{formatScore(data.confidence)}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Quality Metrics
              </Typography>
              <Box sx={{ height: 300, mb: 3 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={qualityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="value" fill="#4f46e5" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Positive Indicators</Typography>
                  <Typography variant="h6">{result.analytics.quality_metrics.positive_indicators}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Negative Indicators</Typography>
                  <Typography variant="h6">{result.analytics.quality_metrics.negative_indicators}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Escalation Risk</Typography>
                  <Typography variant="h6">{formatScore(result.analytics.quality_metrics.escalation_risk)}%</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Politeness Score</Typography>
                  <Typography variant="h6">{formatScore(result.analytics.quality_metrics.politeness_score)}%</Typography>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Summary & Insights Tab */}
        <TabPanel value={activeTab} index={3}>
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Call Summary
              </Typography>
              <Paper sx={{ p: 3, mb: 3, backgroundColor: 'grey.50' }}>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {result.analytics.summary.brief_summary}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>Key Points:</Typography>
                <List dense>
                  {result.analytics.summary.summary_points.map((point, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={`• ${point}`} />
                    </ListItem>
                  ))}
                </List>
              </Paper>

              <Typography variant="subtitle1" gutterBottom>
                Primary Topic
              </Typography>
              <Chip 
                label={result.analytics.summary.primary_topic} 
                color="secondary" 
                sx={{ mb: 2 }}
              />
              
              <Typography variant="subtitle1" gutterBottom>
                Conversation Tone
              </Typography>
              <Chip 
                label={result.analytics.summary.conversation_tone} 
                color={result.analytics.summary.conversation_tone === 'positive' ? 'success' : result.analytics.summary.conversation_tone === 'negative' ? 'error' : 'default'}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Key Phrases
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                {result.analytics.summary.key_phrases.map((phrase, index) => (
                  <Chip key={index} label={phrase} variant="outlined" size="small" />
                ))}
              </Box>

              <Typography variant="h6" gutterBottom>
                Conversation Statistics
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Agent Turns</TableCell>
                      <TableCell align="right">{result.analytics.conversation_metrics.agent_turns}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Customer Turns</TableCell>
                      <TableCell align="right">{result.analytics.conversation_metrics.customer_turns}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Agent Words</TableCell>
                      <TableCell align="right">{result.analytics.conversation_metrics.agent_word_count}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Customer Words</TableCell>
                      <TableCell align="right">{result.analytics.conversation_metrics.customer_word_count}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Average Words/Turn</TableCell>
                      <TableCell align="right">{Math.round(result.analytics.conversation_metrics.average_words_per_turn)}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>
    </Container>
  );
}

export default ResultsViewer; 