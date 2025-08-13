from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Dict, List, Optional
import logging
import time
from datetime import datetime
import os
import uuid
import shutil

from ..services.audio_transcriber import AudioTranscriber
from ..services.lightweight_analytics import LightweightAnalytics

logger = logging.getLogger(__name__)

router = APIRouter()

# Audio storage directory
AUDIO_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "../../../uploads/audio")
os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)

# Initialize services
try:
    audio_transcriber = AudioTranscriber()
    logger.info("Audio transcriber initialized successfully")
except Exception as e:
    logger.error(f"Audio transcriber initialization failed: {e}")
    audio_transcriber = None

try:
    analytics_service = LightweightAnalytics()
    logger.info("Analytics service initialized successfully")
except Exception as e:
    logger.error(f"Analytics service initialization failed: {e}")
    analytics_service = None

@router.post("/upload-and-analyze")
async def upload_and_analyze_audio(
    file: UploadFile = File(...),
    call_id: Optional[str] = Form(None)
):
    """
    Complete workflow: Upload audio file, transcribe it, and perform analytics
    
    This is the main endpoint that implements the full pipeline:
    1. Upload audio file
    2. Transcribe audio to text
    3. Perform conversation analytics
    4. Return comprehensive results
    """
    if not audio_transcriber:
        raise HTTPException(status_code=503, detail="Audio transcription service not available")
    
    if not analytics_service:
        raise HTTPException(status_code=503, detail="Analytics service not available")
    
    try:
        start_time = time.time()
        
        # Generate call ID if not provided
        if not call_id:
            call_id = f"call_{uuid.uuid4().hex[:8]}"
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file format
        validation = audio_transcriber.validate_audio_file(file.filename)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        logger.info(f"Processing audio file: {file.filename} for call {call_id}")
        
        # Read audio data
        audio_data = await file.read()
        
        # Save audio file for playback
        audio_file_path = None
        try:
            file_extension = os.path.splitext(file.filename)[1] or '.wav'
            audio_filename = f"{call_id}{file_extension}"
            audio_file_path = os.path.join(AUDIO_STORAGE_DIR, audio_filename)
            
            with open(audio_file_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"Audio file saved: {audio_file_path}")
        except Exception as e:
            logger.warning(f"Failed to save audio file: {str(e)}")
        
        # Step 1: Transcribe audio
        logger.info(f"Starting transcription for call {call_id}")
        transcription_start = time.time()
        transcription_result = audio_transcriber.transcribe_audio(audio_data, file.filename)
        transcription_time = time.time() - transcription_start
        
        if not transcription_result["success"]:
            logger.error(f"Transcription failed for call {call_id}: {transcription_result['error']}")
            return {
                "call_id": call_id,
                "success": False,
                "error": transcription_result["error"],
                "step_failed": "transcription",
                "audio_url": f"/api/v1/audio/{call_id}" if audio_file_path and os.path.exists(audio_file_path) else None,
                "processing_time_seconds": round(time.time() - start_time, 2)
            }
        
        transcript = transcription_result["transcript"]
        logger.info(f"Transcription completed for call {call_id} in {transcription_time:.2f} seconds")
        
        # Step 2: Perform analytics
        logger.info(f"Starting analytics for call {call_id}")
        analytics_start = time.time()
        analytics_result = analytics_service.analyze_conversation(transcript)
        analytics_time = time.time() - analytics_start
        
        if not analytics_result["success"]:
            return {
                "call_id": call_id,
                "success": False,
                "error": analytics_result["error"],
                "step_failed": "analytics",
                "transcription_result": transcription_result,
                "processing_time_seconds": round(time.time() - start_time, 2)
            }
        
        logger.info(f"Analytics completed for call {call_id} in {analytics_time:.2f} seconds")
        
        # Combine results
        total_time = time.time() - start_time
        
        return {
            "call_id": call_id,
            "success": True,
            "filename": file.filename,
            "audio_url": f"/api/v1/audio/{call_id}" if audio_file_path and os.path.exists(audio_file_path) else None,
            "transcription": {
                "transcript": transcript,
                "confidence": transcription_result["confidence"],
                "language": transcription_result["language"],
                "processing_time_seconds": round(transcription_time, 2)
            },
            "analytics": analytics_result,
            "processing_times": {
                "transcription_seconds": round(transcription_time, 2),
                "analytics_seconds": round(analytics_time, 2),
                "total_seconds": round(total_time, 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/transcribe")
async def transcribe_audio_only(file: UploadFile = File(...)):
    """
    Transcribe audio file to text only (without analytics)
    """
    if not audio_transcriber:
        raise HTTPException(status_code=503, detail="Audio transcription service not available")
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
            
        validation = audio_transcriber.validate_audio_file(file.filename)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Read and transcribe
        audio_data = await file.read()
        result = audio_transcriber.transcribe_audio(audio_data, file.filename)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "filename": file.filename,
            "transcript": result["transcript"],
            "confidence": result["confidence"],
            "language": result["language"],
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error for {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/analyze-transcript")
async def analyze_transcript_only(transcript_data: Dict):
    """
    Analyze a text transcript (without audio transcription)
    
    Expected input format:
    {
        "transcript": "Agent: Hello, how can I help you? Customer: I have a billing issue...",
        "call_id": "optional_call_id"
    }
    """
    if not analytics_service:
        raise HTTPException(status_code=503, detail="Analytics service not available")
    
    try:
        transcript = transcript_data.get("transcript", "")
        call_id = transcript_data.get("call_id", f"analysis_{uuid.uuid4().hex[:8]}")
        
        if not transcript.strip():
            raise HTTPException(status_code=400, detail="Transcript text is required")
        
        logger.info(f"Analyzing transcript for call {call_id}")
        start_time = time.time()
        
        result = analytics_service.analyze_conversation(transcript)
        processing_time = time.time() - start_time
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "call_id": call_id,
            "success": True,
            "analytics": result,
            "processing_time_seconds": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/batch-analyze")
async def batch_analyze_files(files: List[UploadFile] = File(...)):
    """
    Batch process multiple audio files
    """
    if not audio_transcriber or not analytics_service:
        raise HTTPException(status_code=503, detail="Required services not available")
    
    try:
        results = []
        start_time = time.time()
        
        logger.info(f"Starting batch processing of {len(files)} files")
        
        for i, file in enumerate(files):
            try:
                call_id = f"batch_{uuid.uuid4().hex[:8]}_{i+1}"
                
                # Validate file has filename
                filename = file.filename
                if not filename:
                    results.append({
                        "call_id": call_id,
                        "filename": "unknown",
                        "success": False,
                        "error": "No filename provided",
                        "step_failed": "validation"
                    })
                    continue
                
                # Process each file
                audio_data = await file.read()
                
                # Save audio file for playback
                audio_file_path = None
                try:
                    file_extension = os.path.splitext(filename)[1] or '.wav'
                    audio_filename = f"{call_id}{file_extension}"
                    audio_file_path = os.path.join(AUDIO_STORAGE_DIR, audio_filename)
                    
                    with open(audio_file_path, 'wb') as f:
                        f.write(audio_data)
                    
                    logger.info(f"Audio file saved: {audio_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to save audio file: {str(e)}")
                
                # Transcribe
                transcription_result = audio_transcriber.transcribe_audio(audio_data, filename)
                
                if transcription_result["success"]:
                    # Analyze
                    analytics_result = analytics_service.analyze_conversation(transcription_result["transcript"])
                    
                    results.append({
                        "call_id": call_id,
                        "filename": filename,
                        "success": True,
                        "audio_url": f"/api/v1/audio/{call_id}" if audio_file_path and os.path.exists(audio_file_path) else None,
                        "transcription": transcription_result,
                        "analytics": analytics_result if analytics_result["success"] else {"error": analytics_result["error"]}
                    })
                else:
                    results.append({
                        "call_id": call_id,
                        "filename": filename,
                        "success": False,
                        "error": transcription_result["error"],
                        "step_failed": "transcription"
                    })
                    
            except Exception as e:
                results.append({
                    "call_id": f"batch_error_{i+1}",
                    "filename": file.filename if file else "unknown",
                    "success": False,
                    "error": str(e)
                })
        
        total_time = time.time() - start_time
        successful = len([r for r in results if r.get("success", False)])
        
        return {
            "batch_summary": {
                "total_files": len(files),
                "successful": successful,
                "failed": len(files) - successful,
                "total_processing_time_seconds": round(total_time, 2),
                "average_time_per_file": round(total_time / len(files), 2) if files else 0
            },
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@router.get("/audio/{call_id}")
async def get_audio_file(call_id: str):
    """Serve audio file for playback"""
    try:
        # Look for audio file with any supported extension
        supported_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac']
        
        for ext in supported_extensions:
            audio_path = os.path.join(AUDIO_STORAGE_DIR, f"{call_id}{ext}")
            if os.path.exists(audio_path):
                # Determine media type based on extension
                media_types = {
                    '.wav': 'audio/wav',
                    '.mp3': 'audio/mpeg',
                    '.m4a': 'audio/mp4',
                    '.flac': 'audio/flac',
                    '.ogg': 'audio/ogg',
                    '.aac': 'audio/aac'
                }
                
                media_type = media_types.get(ext, 'audio/wav')
                return FileResponse(
                    path=audio_path,
                    media_type=media_type,
                    filename=f"{call_id}{ext}"
                )
        
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    except Exception as e:
        logger.error(f"Error serving audio file for call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve audio file")

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported audio formats"""
    if not audio_transcriber:
        return {"formats": [], "error": "Transcription service not available"}
    
    return {
        "supported_formats": audio_transcriber.get_supported_formats(),
        "transcription_engines": ["Google Speech Recognition", "Sphinx (offline)"],
        "max_file_size_mb": 100
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "audio_transcriber": "active" if audio_transcriber else "unavailable",
            "analytics_service": "active" if analytics_service else "unavailable",
        },
        "capabilities": {
            "audio_transcription": audio_transcriber is not None,
            "conversation_analytics": analytics_service is not None,
            "batch_processing": audio_transcriber is not None and analytics_service is not None
        }
    }

@router.get("/stats")
async def get_system_stats():
    """Get system statistics and capabilities"""
    stats = {
        "system_info": {
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "type": "lightweight_local"
        },
        "capabilities": {
            "transcription": {
                "available": audio_transcriber is not None,
                "engines": ["Google Speech Recognition", "Sphinx (offline)"],
                "supported_formats": audio_transcriber.get_supported_formats() if audio_transcriber else []
            },
            "analytics": {
                "available": analytics_service is not None,
                "features": [
                    "Sentiment Analysis (VADER)",
                    "Intent Detection (Rule-based)",
                    "Conversation Metrics",
                    "Quality Assessment",
                    "Call Summarization"
                ] if analytics_service else []
            }
        }
    }
    
    return stats 