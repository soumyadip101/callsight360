# Audio Analysis Pipeline

A lightweight, local audio processing and conversation analytics tool that transforms audio files into actionable insights without requiring external APIs or cloud services.

## 🎯 Features

- **🎵 Audio Transcription**: Convert audio files to text using Faster-Whisper AI model
- **🎭 Sentiment Analysis**: VADER-powered emotion detection and satisfaction analysis
- **🎯 Intent Detection**: Rule-based pattern matching for conversation categorization
- **📈 Conversation Metrics**: Turn analysis, speaking patterns, and interaction quality
- **⭐ Quality Assessment**: Call quality scoring, politeness metrics, and outcome prediction
- **📝 Smart Summarization**: Key phrase extraction and conversation insights
- **🔄 Batch Processing**: Simultaneous analysis of multiple audio files

## 🔒 Privacy & Security

- **100% Local Processing**: All audio and data processing happens on your machine
- **No External APIs**: No data sent to third-party services
- **Offline Capable**: Works completely without internet connection
- **Lightweight**: Minimal memory footprint and fast processing

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **FFmpeg** (for audio processing)
- **Docker & Docker Compose** (optional, for containerized deployment)

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd audio-analysis-pipeline
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg portaudio19-dev python3-dev
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg portaudio
   ```
   
   **Windows:**
   - Download FFmpeg from https://ffmpeg.org/download.html
   - Add FFmpeg to your system PATH
   - Install Microsoft Visual C++ Build Tools

5. **Start the backend server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## 📋 Usage Guide

### Single File Analysis

1. Navigate to the **Upload Audio** page
2. Drag & drop an audio file or click to browse
3. Optionally enter a Call ID for tracking
4. Click **Analyze Audio**
5. View real-time processing progress
6. Review comprehensive results including:
   - Full transcript with confidence scores
   - Sentiment analysis (overall, agent, customer)
   - Intent detection and categorization
   - Quality metrics and call outcome
   - Key phrases and conversation summary

### Batch Processing

1. Navigate to the **Batch Process** page
2. Upload multiple audio files simultaneously
3. Monitor processing progress for all files
4. Review batch summary statistics
5. Examine individual file results
6. Export results for further analysis

### API Usage

The application provides a RESTful API for programmatic access:

```bash
# Upload and analyze single file
curl -X POST "http://localhost:8000/api/v1/upload-and-analyze" \
     -F "file=@your_audio.wav" \
     -F "call_id=test_001"

# Transcribe only
curl -X POST "http://localhost:8000/api/v1/transcribe" \
     -F "file=@your_audio.wav"

# Analyze existing transcript
curl -X POST "http://localhost:8000/api/v1/analyze-transcript" \
     -H "Content-Type: application/json" \
     -d '{"transcript": "Agent: Hello, how can I help? Customer: I have an issue..."}'

# Batch processing
curl -X POST "http://localhost:8000/api/v1/batch-analyze" \
     -F "files=@file1.wav" \
     -F "files=@file2.wav"
```

## 🎵 Supported Audio Formats

- **WAV** (recommended for best quality)
- **MP3**
- **M4A**
- **FLAC**
- **OGG**
- **AAC**

**File Size Limit**: 100MB per file  
**Quality Recommendations**: 16kHz+ sample rate for optimal transcription accuracy

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Audio Processing
MAX_FILE_SIZE_MB=100
SUPPORTED_FORMATS=wav,mp3,m4a,flac,ogg,aac

# Transcription Settings
DEFAULT_LANGUAGE=en-US
TRANSCRIPTION_TIMEOUT=300

# Analytics Configuration
SENTIMENT_THRESHOLD=0.05
QUALITY_SCORE_WEIGHTS=sentiment:0.3,intent:0.2,politeness:0.3,outcome:0.2
```

### Advanced Configuration

For production deployments, consider:

- **Resource Limits**: Adjust Docker memory/CPU limits based on usage
- **Load Balancing**: Use nginx for multiple backend instances
- **Storage**: Configure persistent volumes for large-scale processing
- **Monitoring**: Add health checks and logging integrations

## 🏗️ Architecture

### Backend Components

- **FastAPI**: Modern Python web framework
- **SpeechRecognition**: Local audio-to-text conversion using faster-whisper
- **VADER Sentiment**: Lexicon-based sentiment analysis
- **Librosa and Pydub**: Audio format conversion and processing
- **TextStat**: Readability and text statistics

### Frontend Components

- **React 18**: Modern UI framework
- **Material-UI**: Professional component library
- **Recharts**: Data visualization
- **React-Dropzone**: File upload interface
- **React-Query**: State management and caching

### Processing Pipeline

1. **Audio Upload**: Secure file handling with format validation
2. **Format Conversion**: Automatic conversion to WAV using FFmpeg
3. **Speech Recognition**: Local transcription with Whisper AI
4. **Text Analytics**: Parallel processing of multiple analysis types
5. **Result Generation**: Comprehensive insights and metrics
6. **Response Delivery**: Structured JSON with detailed results

## 🔍 Analysis Features

### Sentiment Analysis
- **Overall conversation sentiment** with confidence scores
- **Speaker-specific sentiment** (agent vs. customer)
- **Sentiment trend analysis** throughout the conversation
- **VADER lexicon-based** approach for consistent results

### Intent Detection
- **Rule-based pattern matching** for reliable categorization
- **Multiple intent categories**: billing, technical support, complaints, etc.
- **Confidence scoring** for each detected intent
- **Keyword extraction** and matching details

### Quality Metrics
- **Call quality scoring** based on multiple factors
- **Politeness assessment** using linguistic markers
- **Outcome prediction** (resolved, unresolved, in-progress)
- **Escalation risk analysis** for proactive management

### Conversation Analytics
- **Turn-by-turn analysis** of speaker interactions
- **Speaking time distribution** between participants
- **Word count statistics** and conversation flow
- **Duration estimation** based on speech patterns

## 🚨 Troubleshooting

### Common Issues

**1. Audio Transcription Fails**
- Ensure FFmpeg is installed and in PATH
- Check audio file format and quality
- Verify file size is under 100MB limit

**2. Poor Transcription Quality**
- Use higher quality audio files (16kHz+ sample rate)
- Ensure clear audio without excessive background noise
- Consider preprocessing audio for noise reduction

**3. Installation Issues**
- Install system dependencies (portaudio, ffmpeg)
- Use Python 3.11+ for best compatibility
- Check virtual environment activation

**4. Docker Issues**
- Ensure Docker and Docker Compose are installed
- Check port availability (3000, 8000, 6379)
- Verify sufficient disk space for containers

### Performance Optimization

- **CPU Usage**: Transcription is CPU-intensive; consider dedicated processing time
- **Memory**: Large audio files require more RAM; monitor system resources
- **Batch Size**: Process files in smaller batches for better performance
- **Storage**: Ensure sufficient disk space for temporary file processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review existing [GitHub Issues](issues)
3. Create a new issue with detailed information
4. Include system information and error logs

## 🎯 Roadmap

- [ ] **Enhanced Transcription**: Additional speech recognition engines
- [ ] **Multi-language Support**: Transcription and analysis in multiple languages
- [ ] **Custom Models**: Support for domain-specific analysis models
- [ ] **Advanced Analytics**: Machine learning-based insights
- [ ] **Integration APIs**: Webhooks and third-party service integrations
- [ ] **Performance Monitoring**: Built-in analytics and performance metrics

---

**Audio Analysis Pipeline v2.0.0** - Lightweight, Local, and Privacy-Focused 
