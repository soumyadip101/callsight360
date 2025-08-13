import os
import tempfile
import logging
import time
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import webrtcvad
import librosa
import soundfile as sf
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor, as_completed
import torch

# Try to import faster-whisper, fallback to openai-whisper
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    try:
        import whisper  # type: ignore
        FASTER_WHISPER_AVAILABLE = False
    except ImportError:
        whisper = None  # type: ignore
        FASTER_WHISPER_AVAILABLE = False
    WhisperModel = None

logger = logging.getLogger(__name__)

@dataclass
class TranscriptionSegment:
    """Represents a transcription segment with speaker and timing info"""
    text: str
    speaker: str
    start_time: float
    end_time: float
    confidence: float
    speaker_confidence: float = 0.8

@dataclass
class AudioChunk:
    """Represents an audio chunk with metadata"""
    audio_data: np.ndarray
    start_time: float
    end_time: float
    sample_rate: int
    is_speech: bool = True

class AdvancedAudioTranscriber:
    """Advanced audio transcription with VAD, speaker diarization, and fast transcription"""
    
    def __init__(self):
        # Initialize VAD
        self.vad = webrtcvad.Vad(2)  # Reduced aggressiveness for speed (was 3)
        self.sample_rate = 16000  # Standard rate for VAD
        self.frame_duration_ms = 20  # Reduced from 30ms for faster processing
        
        # Initialize Whisper model (faster-whisper or openai-whisper)
        self.whisper_model = None
        self.use_faster_whisper = FASTER_WHISPER_AVAILABLE
        self._init_whisper_model()
        
        # Optimized processing parameters
        self.min_chunk_duration = 1.0  # Increased from 0.5s to reduce small chunks
        self.max_chunk_duration = 20.0  # Reduced from 30s for better parallelization
        self.silence_threshold = 0.3  # Reduced from 0.5s for faster grouping
        self.max_workers = min(6, os.cpu_count() or 1)  # Increased workers
        
        # VAD optimization parameters
        self.vad_buffer_size = 8192  # Process in larger buffers
        self.skip_normalization = False  # Option to skip expensive normalization
        
    def _init_whisper_model(self):
        """Initialize the Whisper model for transcription"""
        try:
            model_size = "base"  # Options: tiny, base, small, medium, large
            
            if FASTER_WHISPER_AVAILABLE and WhisperModel:
                # Use faster-whisper for better performance
                self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
                self.use_faster_whisper = True
                logger.info(f"Initialized faster-whisper model: {model_size}")
            elif whisper is not None:
                # Fallback to openai-whisper
                self.whisper_model = whisper.load_model(model_size)
                self.use_faster_whisper = False
                logger.info(f"Initialized OpenAI Whisper model: {model_size}")
            else:
                logger.error("No Whisper implementation available")
                self.whisper_model = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Whisper model: {e}")
            self.whisper_model = None
    
    def transcribe_audio(self, audio_data: bytes, filename: str = "audio") -> Dict:
        """
        Advanced audio transcription with optimized VAD chunking and speaker diarization
        
        Args:
            audio_data: Raw audio file bytes
            filename: Original filename for context
            
        Returns:
            Dict with comprehensive transcription results
        """
        start_time = time.time()
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=self._get_file_extension(filename)) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Step 1: Load and preprocess audio (optimized)
                logger.info(f"Loading audio file: {filename}")
                load_start = time.time()
                audio_array, original_sr = self._load_audio(temp_file_path)
                load_time = time.time() - load_start
                logger.info(f"Audio loading took {load_time:.2f}s")
                
                if audio_array is None:
                    return self._error_result("Failed to load audio file", time.time() - start_time)
                
                # Step 2: Perform optimized VAD-based chunking
                logger.info("Performing optimized VAD-based audio chunking")
                chunk_start = time.time()
                
                # For very large files (>5 minutes), use streaming processing
                audio_duration = len(audio_array) / original_sr
                if audio_duration > 300:  # 5 minutes
                    audio_chunks = self._stream_vad_chunking(audio_array, original_sr)
                else:
                    audio_chunks = self._vad_chunk_audio(audio_array, original_sr)
                
                chunk_time = time.time() - chunk_start
                logger.info(f"VAD chunking took {chunk_time:.2f}s")
                
                if not audio_chunks:
                    return self._error_result("No speech detected in audio", time.time() - start_time)
                
                logger.info(f"Created {len(audio_chunks)} audio chunks")
                
                # Step 3: Transcribe chunks in parallel (optimized)
                logger.info("Transcribing audio chunks")
                transcription_start = time.time()
                transcription_segments = self._transcribe_chunks_parallel(audio_chunks)
                transcription_time = time.time() - transcription_start
                logger.info(f"Transcription took {transcription_time:.2f}s")
                
                if not transcription_segments:
                    return self._error_result("Transcription failed for all chunks", time.time() - start_time)
                
                # Step 4: Perform speaker diarization
                logger.info("Performing speaker diarization")
                diarization_start = time.time()
                diarized_segments = self._perform_speaker_diarization(
                    temp_file_path, transcription_segments
                )
                diarization_time = time.time() - diarization_start
                logger.info(f"Speaker diarization took {diarization_time:.2f}s")
                
                # Step 5: Format transcript for conversation UI
                formatted_transcript = self._format_conversation_transcript(diarized_segments)
                conversation_flow = self._create_conversation_flow(diarized_segments)
                
                # Calculate overall metrics
                overall_confidence = float(np.mean([seg.confidence for seg in diarized_segments])) if diarized_segments else 0.0
                processing_time = time.time() - start_time
                
                logger.info(f"Total transcription completed in {processing_time:.2f}s for {filename}")
                
                return {
                    "success": True,
                    "transcript": formatted_transcript,
                    "conversation_flow": conversation_flow,
                    "confidence": overall_confidence,
                    "language": "en",
                    "filename": filename,
                    "processing_time": processing_time,
                    "segments": len(diarized_segments),
                    "speakers_detected": len(set(seg.speaker for seg in diarized_segments)),
                    "audio_duration": len(audio_array) / original_sr,
                    "chunks_processed": len(audio_chunks),
                    "diarization_method": "fallback",
                    "performance_metrics": {
                        "load_time": load_time,
                        "chunk_time": chunk_time,
                        "transcription_time": transcription_time,
                        "diarization_time": diarization_time
                    }
                }
                
            finally:
                # Cleanup temporary files
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Transcription error for {filename}: {str(e)}")
            return self._error_result(f"Transcription failed: {str(e)}", time.time() - start_time)
    
    def _load_audio(self, file_path: str) -> Tuple[Optional[np.ndarray], int]:
        """Load audio file and convert to appropriate format - optimized"""
        try:
            # Load audio using librosa with optimized parameters
            audio_array, sample_rate = librosa.load(
                file_path, 
                sr=self.sample_rate,  # Directly load at target sample rate
                mono=True,
                dtype=np.float32  # Use float32 instead of default float64
            )
            
            # Skip expensive normalization if not needed
            if not self.skip_normalization:
                # Fast normalization using numpy
                max_val = np.abs(audio_array).max()
                if max_val > 0:
                    audio_array = audio_array / max_val
            
            logger.info(f"Loaded audio: {len(audio_array)/sample_rate:.2f}s at {sample_rate}Hz")
            return audio_array, int(sample_rate)
            
        except Exception as e:
            logger.error(f"Error loading audio file: {e}")
            try:
                # Fallback to pydub - also optimized
                audio = AudioSegment.from_file(file_path)
                audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
                audio_array = np.array(audio.get_array_of_samples(), dtype=np.float32)
                
                # Fast normalization
                max_val = np.abs(audio_array).max()
                if max_val > 0:
                    audio_array = audio_array / max_val
                return audio_array, self.sample_rate
            except Exception as e2:
                logger.error(f"Fallback audio loading failed: {e2}")
                return None, 0
    
    def _vad_chunk_audio_optimized(self, audio_array: np.ndarray, sample_rate: int) -> List[AudioChunk]:
        """Highly optimized VAD-based audio chunking using vectorized operations"""
        try:
            # Skip resampling if already at correct rate
            if sample_rate != self.sample_rate:
                audio_array = librosa.resample(
                    audio_array, 
                    orig_sr=sample_rate, 
                    target_sr=self.sample_rate,
                    res_type='kaiser_fast'  # Faster resampling
                )
                sample_rate = self.sample_rate
            
            # Convert to 16-bit PCM for VAD - vectorized
            audio_int16 = (audio_array * 32767).astype(np.int16)
            
            # Calculate frame parameters
            frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
            hop_size = frame_size  # No overlap for speed
            
            # Vectorized frame processing
            num_frames = (len(audio_int16) - frame_size) // hop_size + 1
            if num_frames <= 0:
                return self._fallback_time_chunks(audio_array, sample_rate)
            
            # Pre-allocate arrays for speed
            speech_flags = np.zeros(num_frames, dtype=bool)
            frame_times = np.arange(num_frames) * hop_size / sample_rate
            
            # Process frames in batches for better performance
            batch_size = min(100, num_frames)  # Process 100 frames at a time
            
            for batch_start in range(0, num_frames, batch_size):
                batch_end = min(batch_start + batch_size, num_frames)
                
                for i in range(batch_start, batch_end):
                    frame_start = i * hop_size
                    frame_end = frame_start + frame_size
                    
                    if frame_end <= len(audio_int16):
                        frame = audio_int16[frame_start:frame_end]
                        try:
                            speech_flags[i] = self.vad.is_speech(frame.tobytes(), self.sample_rate)
                        except:
                            speech_flags[i] = False  # Handle VAD errors gracefully
            
            # Find speech segments using vectorized operations
            chunks = self._extract_speech_segments_vectorized(
                audio_array, speech_flags, frame_times, hop_size, sample_rate
            )
            
            if not chunks:
                logger.warning("No speech detected by optimized VAD, using fallback")
                return self._fallback_time_chunks(audio_array, sample_rate)
            
            logger.info(f"Optimized VAD created {len(chunks)} speech chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Optimized VAD chunking error: {e}")
            # Fallback to time-based chunking
            return self._fallback_time_chunks(audio_array, sample_rate)
    
    def _extract_speech_segments_vectorized(self, audio_array: np.ndarray, speech_flags: np.ndarray, 
                                          frame_times: np.ndarray, hop_size: int, sample_rate: int) -> List[AudioChunk]:
        """Extract speech segments using vectorized operations - much faster than loops"""
        
        # Find speech segment boundaries using numpy diff
        speech_changes = np.diff(np.concatenate(([False], speech_flags, [False])).astype(int))
        speech_starts = np.where(speech_changes == 1)[0]
        speech_ends = np.where(speech_changes == -1)[0]
        
        chunks = []
        min_samples = int(self.min_chunk_duration * sample_rate)
        
        for start_idx, end_idx in zip(speech_starts, speech_ends):
            if start_idx < len(frame_times) and end_idx <= len(frame_times):
                # Calculate time boundaries
                start_time = frame_times[start_idx]
                end_time = frame_times[min(end_idx - 1, len(frame_times) - 1)] + (hop_size / sample_rate)
                
                # Calculate sample boundaries
                start_sample = int(start_time * sample_rate)
                end_sample = int(end_time * sample_rate)
                
                # Ensure we don't exceed array bounds
                end_sample = min(end_sample, len(audio_array))
                
                # Check minimum duration
                if (end_sample - start_sample) >= min_samples:
                    chunk_audio = audio_array[start_sample:end_sample]
                    
                    chunks.append(AudioChunk(
                        audio_data=chunk_audio,
                        start_time=float(start_time),
                        end_time=float(end_time),
                        sample_rate=sample_rate,
                        is_speech=True
                    ))
        
        return chunks
    
    def _vad_chunk_audio(self, audio_array: np.ndarray, sample_rate: int) -> List[AudioChunk]:
        """Main VAD chunking method - now uses optimized version"""
        return self._vad_chunk_audio_optimized(audio_array, sample_rate)
    
    def _create_audio_chunk(self, audio_array: np.ndarray, start_time: float, 
                           end_time: float, sample_rate: int) -> AudioChunk:
        """Create an AudioChunk from audio array and time bounds"""
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        chunk_audio = audio_array[start_sample:end_sample]
        
        return AudioChunk(
            audio_data=chunk_audio,
            start_time=start_time,
            end_time=end_time,
            sample_rate=sample_rate,
            is_speech=True
        )
    
    def _optimize_chunks(self, chunks: List[AudioChunk], audio_array: np.ndarray, 
                        sample_rate: int) -> List[AudioChunk]:
        """Optimize chunks by merging small ones and splitting large ones"""
        if not chunks:
            return chunks
            
        optimized = []
        i = 0
        
        while i < len(chunks):
            current_chunk = chunks[i]
            chunk_duration = current_chunk.end_time - current_chunk.start_time
            
            # If chunk is too small, try to merge with next
            if chunk_duration < self.min_chunk_duration and i + 1 < len(chunks):
                next_chunk = chunks[i + 1]
                gap = next_chunk.start_time - current_chunk.end_time
                
                # Merge if gap is small
                if gap < self.silence_threshold:
                    merged_chunk = self._create_audio_chunk(
                        audio_array, current_chunk.start_time, next_chunk.end_time, sample_rate
                    )
                    optimized.append(merged_chunk)
                    i += 2  # Skip next chunk as it's merged
                    continue
            
            # If chunk is too large, split it
            if chunk_duration > self.max_chunk_duration:
                split_chunks = self._split_large_chunk(current_chunk, audio_array)
                optimized.extend(split_chunks)
            else:
                optimized.append(current_chunk)
            
            i += 1
        
        return optimized
    
    def _split_large_chunk(self, chunk: AudioChunk, audio_array: np.ndarray) -> List[AudioChunk]:
        """Split a large chunk into smaller ones"""
        chunks = []
        chunk_duration = chunk.end_time - chunk.start_time
        num_splits = int(np.ceil(chunk_duration / self.max_chunk_duration))
        split_duration = chunk_duration / num_splits
        
        for i in range(num_splits):
            split_start = chunk.start_time + i * split_duration
            split_end = min(chunk.start_time + (i + 1) * split_duration, chunk.end_time)
            
            split_chunk = self._create_audio_chunk(
                audio_array, float(split_start), float(split_end), chunk.sample_rate
            )
            chunks.append(split_chunk)
        
        return chunks
    
    def _fallback_time_chunks(self, audio_array: np.ndarray, sample_rate: int) -> List[AudioChunk]:
        """Optimized fallback to simple time-based chunking"""
        chunks = []
        duration = len(audio_array) / sample_rate
        chunk_duration = 15.0  # Optimized chunk size (was 10s)
        
        # Use numpy arange for better performance
        chunk_starts = np.arange(0, duration, chunk_duration)
        
        for start in chunk_starts:
            end = float(min(float(start + chunk_duration), duration))
            
            # Skip very short chunks
            if (end - start) < 2.0:  # Skip chunks shorter than 2 seconds
                continue
                
            start_sample = int(start * sample_rate)
            end_sample = int(end * sample_rate)
            chunk_audio = audio_array[start_sample:end_sample]
            
            chunks.append(AudioChunk(
                audio_data=chunk_audio,
                start_time=float(start),
                end_time=end,
                sample_rate=sample_rate,
                is_speech=True
            ))
        
        logger.info(f"Optimized fallback chunking created {len(chunks)} chunks")
        return chunks
    
    def _transcribe_chunks_parallel(self, chunks: List[AudioChunk]) -> List[TranscriptionSegment]:
        """Transcribe audio chunks in parallel using faster-whisper or openai-whisper"""
        if not self.whisper_model:
            logger.error("Whisper model not available")
            return []
        
        segments = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit transcription tasks
            future_to_chunk = {
                executor.submit(self._transcribe_single_chunk, chunk, i): (chunk, i)
                for i, chunk in enumerate(chunks)
            }
            
            # Collect results
            for future in as_completed(future_to_chunk):
                chunk, chunk_idx = future_to_chunk[future]
                try:
                    result = future.result(timeout=60)  # 60 second timeout
                    if result:
                        segments.append(result)
                except Exception as e:
                    logger.error(f"Chunk {chunk_idx} transcription failed: {e}")
        
        # Sort segments by start time
        segments.sort(key=lambda x: x.start_time)
        return segments
    
    def _transcribe_single_chunk(self, chunk: AudioChunk, chunk_idx: int) -> Optional[TranscriptionSegment]:
        """Transcribe a single audio chunk"""
        if not self.whisper_model:
            return None
            
        try:
            # Save chunk to temporary file for Whisper
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                sf.write(temp_file.name, chunk.audio_data, chunk.sample_rate)
                temp_path = temp_file.name
            
            try:
                if self.use_faster_whisper:
                    # Use faster-whisper
                    segments, info = self.whisper_model.transcribe(
                        temp_path,
                        language="en",
                        vad_filter=True,
                        vad_parameters=dict(min_silence_duration_ms=500),
                        word_timestamps=True
                    )
                    
                    # Combine all segments into one text
                    text_parts = []
                    confidences = []
                    
                    for segment in segments:
                        text_parts.append(segment.text.strip())
                        confidences.append(segment.avg_logprob)
                    
                    if not text_parts:
                        return None
                    
                    combined_text = " ".join(text_parts)
                    avg_confidence = float(np.mean(confidences)) if confidences else 0.0
                    
                    # Convert confidence from log probability to 0-1 scale
                    confidence = float(min(1.0, max(0.0, (avg_confidence + 1.0) / 2.0)))
                    
                else:
                    # Use openai-whisper
                    result = self.whisper_model.transcribe(temp_path)
                    combined_text = str(result.get("text", "")).strip() if isinstance(result, dict) else ""
                    confidence = 0.8  # Default confidence for openai-whisper
                
                if not combined_text:
                    return None
                
                return TranscriptionSegment(
                    text=combined_text,
                    speaker="Unknown",  # Will be determined by diarization
                    start_time=chunk.start_time,
                    end_time=chunk.end_time,
                    confidence=confidence
                )
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error transcribing chunk {chunk_idx}: {e}")
            return None
    
    def _perform_speaker_diarization(self, audio_file_path: str, 
                                   segments: List[TranscriptionSegment]) -> List[TranscriptionSegment]:
        """Perform speaker diarization on transcribed segments"""
        # This method is no longer needed as pyannote.audio is removed
        return self._fallback_speaker_detection(segments)
    
    def _fallback_speaker_detection(self, segments: List[TranscriptionSegment]) -> List[TranscriptionSegment]:
        """Fallback speaker detection using text analysis and timing patterns"""
        if not segments:
            return segments
        
        # Simple alternating speaker pattern with text analysis
        diarized_segments = []
        current_speaker = "Agent"  # Start with agent
        
        for i, segment in enumerate(segments):
            # Analyze text content for speaker indicators
            text_lower = segment.text.lower()
            
            # Agent indicators
            agent_phrases = [
                'thank you for calling', 'how may I help', 'how can I assist',
                'let me check', 'according to our records', 'I understand',
                'I apologize', 'company policy', 'I can help you'
            ]
            
            # Customer indicators  
            customer_phrases = [
                'I need', 'I want', 'my account', 'I have a problem',
                'can you help me', 'I would like', 'my bill', 'I paid'
            ]
            
            agent_score = sum(1 for phrase in agent_phrases if phrase in text_lower)
            customer_score = sum(1 for phrase in customer_phrases if phrase in text_lower)
            
            # Determine speaker based on content and alternation
            if agent_score > customer_score:
                speaker = "Agent"
            elif customer_score > agent_score:
                speaker = "Customer"
            else:
                # Use alternation pattern
                if i > 0:
                    prev_speaker = diarized_segments[-1].speaker
                    speaker = "Customer" if prev_speaker == "Agent" else "Agent"
                else:
                    speaker = current_speaker
            
            diarized_segment = TranscriptionSegment(
                text=segment.text,
                speaker=speaker,
                start_time=segment.start_time,
                end_time=segment.end_time,
                confidence=segment.confidence,
                speaker_confidence=0.7  # Moderate confidence for fallback method
            )
            diarized_segments.append(diarized_segment)
        
        logger.info("Completed fallback speaker detection")
        return diarized_segments
    
    def _format_conversation_transcript(self, segments: List[TranscriptionSegment]) -> str:
        """Format transcript as a readable conversation"""
        if not segments:
            return ""
        
        formatted_lines = []
        current_speaker = None
        
        for segment in segments:
            timestamp = f"[{segment.start_time:.1f}s]"
            
            # Group consecutive segments from same speaker
            if segment.speaker != current_speaker:
                formatted_lines.append(f"\n{segment.speaker} {timestamp}: {segment.text}")
                current_speaker = segment.speaker
            else:
                # Continue same speaker's text
                formatted_lines.append(f" {segment.text}")
        
        return "".join(formatted_lines).strip()
    
    def _create_conversation_flow(self, segments: List[TranscriptionSegment]) -> List[Dict]:
        """Create conversation flow data structure for frontend UI"""
        conversation = []
        current_message = None
        
        for segment in segments:
            if current_message is None or current_message["speaker"] != segment.speaker:
                # New message from different speaker
                if current_message:
                    conversation.append(current_message)
                
                current_message = {
                    "speaker": segment.speaker,
                    "text": segment.text,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "confidence": segment.confidence,
                    "speaker_confidence": segment.speaker_confidence,
                    "segments": [segment.__dict__]
                }
            else:
                # Continue current speaker's message
                current_message["text"] += " " + segment.text
                current_message["end_time"] = segment.end_time
                current_message["segments"].append(segment.__dict__)
                
                # Update average confidence
                confidences = [seg.confidence for seg in segments if seg.speaker == segment.speaker]
                current_message["confidence"] = float(np.mean(confidences))
        
        # Add final message
        if current_message:
            conversation.append(current_message)
        
        return conversation
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        if '.' in filename:
            return '.' + filename.split('.')[-1].lower()
        return '.wav'
    
    def _error_result(self, error_message: str, processing_time: float) -> Dict:
        """Create error result dictionary"""
        return {
            "success": False,
            "error": error_message,
            "transcript": "",
            "conversation_flow": [],
            "confidence": 0.0,
            "processing_time": processing_time
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac', '.aiff', '.au', '.wma']
    
    def validate_audio_file(self, filename: str, max_size_mb: int = 100) -> Dict:
        """Validate if audio file is supported"""
        file_ext = self._get_file_extension(filename).lower()
        supported_formats = self.get_supported_formats()
        
        if file_ext not in supported_formats:
            return {
                "valid": False,
                "error": f"Unsupported format {file_ext}. Supported: {', '.join(supported_formats)}"
            }
        
        return {"valid": True, "error": None}

    def _stream_vad_chunking(self, audio_array: np.ndarray, sample_rate: int) -> List[AudioChunk]:
        """Stream-based VAD chunking for very large audio files"""
        logger.info("Using streaming VAD for large audio file")
        
        # Process audio in 60-second windows with overlap
        window_duration = 60.0  # seconds
        overlap_duration = 5.0   # seconds
        
        window_samples = int(window_duration * sample_rate)
        overlap_samples = int(overlap_duration * sample_rate)
        
        all_chunks = []
        
        for window_start in range(0, len(audio_array), window_samples - overlap_samples):
            window_end = min(window_start + window_samples, len(audio_array))
            window_audio = audio_array[window_start:window_end]
            
            # Process this window
            window_chunks = self._vad_chunk_audio_optimized(window_audio, sample_rate)
            
            # Adjust chunk timestamps to global timeline
            time_offset = window_start / sample_rate
            for chunk in window_chunks:
                chunk.start_time += time_offset
                chunk.end_time += time_offset
                all_chunks.append(chunk)
        
        # Remove overlapping chunks
        all_chunks = self._remove_overlapping_chunks(all_chunks)
        
        logger.info(f"Streaming VAD created {len(all_chunks)} chunks")
        return all_chunks
    
    def _remove_overlapping_chunks(self, chunks: List[AudioChunk]) -> List[AudioChunk]:
        """Remove overlapping chunks from streaming processing"""
        if not chunks:
            return chunks
        
        # Sort by start time
        chunks.sort(key=lambda x: x.start_time)
        
        # Remove overlaps
        filtered_chunks = [chunks[0]]
        
        for chunk in chunks[1:]:
            last_chunk = filtered_chunks[-1]
            
            # If chunks overlap significantly, skip the later one
            if chunk.start_time < last_chunk.end_time - 1.0:  # 1 second overlap tolerance
                continue
            
            filtered_chunks.append(chunk)
        
        return filtered_chunks

# For backward compatibility, alias the new class
AudioTranscriber = AdvancedAudioTranscriber 