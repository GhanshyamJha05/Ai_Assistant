"""
Real-time Google Speech Recognition via WebSocket
Provides online speech recognition using Google's Speech Recognition API
No C++ dependencies required - pure Python implementation
"""

import json
import logging
import base64
from flask_socketio import emit
from io import BytesIO
import wave

try:
    import speech_recognition as sr
    GOOGLE_SR_AVAILABLE = True
except ImportError:
    GOOGLE_SR_AVAILABLE = False

# Initialize logger
try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Global recognizer instances per client
google_recognizers = {}
google_audio_buffers = {}

def register_google_speech_handlers(socketio):
    """Register Google Speech Recognition WebSocket event handlers"""
    
    if not GOOGLE_SR_AVAILABLE:
        logger.warning("⚠️ speech_recognition not available - install with: pip install SpeechRecognition")
        return False
    
    @socketio.on('google_start_recognition')
    def handle_start_google(data):
        """Start Google Speech Recognition session"""
        try:
            from flask import request
            client_id = request.sid
            language = data.get('language', 'en-US')
            sample_rate = data.get('sampleRate', 16000)
            
            # Create recognizer for this client
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300  # Adjust for ambient noise
            recognizer.dynamic_energy_threshold = True
            
            google_recognizers[client_id] = {
                'recognizer': recognizer,
                'language': language,
                'sample_rate': sample_rate
            }
            google_audio_buffers[client_id] = bytearray()
            
            logger.info(f"🎤 Google Speech Recognition started for client {client_id} (lang: {language}, rate: {sample_rate}Hz)")
            emit('google_ready', {'language': language, 'mode': 'online'})
            
        except Exception as e:
            logger.error(f"❌ Failed to start Google Speech: {e}", exc_info=True)
            emit('google_error', {'error': str(e)})
    
    @socketio.on('google_audio_chunk')
    def handle_google_audio(data):
        """Process audio chunk with Google Speech Recognition"""
        try:
            from flask import request
            client_id = request.sid
            
            if client_id not in google_recognizers:
                emit('google_error', {'error': 'Recognition not started'})
                return
            
            recognizer_data = google_recognizers[client_id]
            recognizer = recognizer_data['recognizer']
            language = recognizer_data['language']
            sample_rate = recognizer_data['sample_rate']
            
            audio_data = data.get('audio')
            
            # Decode audio if base64
            if isinstance(audio_data, str):
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = bytes(audio_data)
            
            # Accumulate audio in buffer
            google_audio_buffers[client_id].extend(audio_bytes)
            
            # Process every ~2 seconds of audio (configurable)
            buffer_size_threshold = sample_rate * 2 * 2  # 2 seconds, 16-bit (2 bytes per sample)
            
            if len(google_audio_buffers[client_id]) >= buffer_size_threshold:
                # Convert buffer to AudioData
                audio_buffer = bytes(google_audio_buffers[client_id])
                
                # Create WAV file in memory
                wav_buffer = BytesIO()
                with wave.open(wav_buffer, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_buffer)
                
                wav_buffer.seek(0)
                
                # Create AudioData object
                with sr.AudioFile(wav_buffer) as source:
                    audio = recognizer.record(source)
                
                # Recognize speech
                try:
                    # Try Google Speech Recognition (free tier)
                    text = recognizer.recognize_google(audio, language=language, show_all=False)
                    
                    if text:
                        logger.info(f"📝 Google recognized: {text}")
                        emit('google_transcript', {
                            'text': text,
                            'isFinal': True,
                            'confidence': 0.9,  # Google doesn't provide confidence in free tier
                            'mode': 'online'
                        })
                        
                        # Clear buffer after successful recognition
                        google_audio_buffers[client_id] = bytearray()
                
                except sr.UnknownValueError:
                    # Speech unintelligible - not an error, just send partial empty
                    emit('google_transcript', {
                        'text': '',
                        'isFinal': False,
                        'mode': 'online'
                    })
                except sr.RequestError as e:
                    logger.error(f"❌ Google Speech API error: {e}")
                    emit('google_error', {'error': f'API request failed: {e}'})
                except Exception as e:
                    logger.error(f"❌ Recognition error: {e}", exc_info=True)
                    emit('google_error', {'error': str(e)})
        
        except Exception as e:
            logger.error(f"❌ Google audio processing error: {e}", exc_info=True)
            emit('google_error', {'error': str(e)})
    
    @socketio.on('google_stop_recognition')
    def handle_stop_google():
        """Stop Google Speech Recognition session"""
        try:
            from flask import request
            client_id = request.sid
            
            if client_id in google_recognizers:
                # Process any remaining audio in buffer
                if client_id in google_audio_buffers and len(google_audio_buffers[client_id]) > 0:
                    recognizer_data = google_recognizers[client_id]
                    recognizer = recognizer_data['recognizer']
                    language = recognizer_data['language']
                    sample_rate = recognizer_data['sample_rate']
                    
                    audio_buffer = bytes(google_audio_buffers[client_id])
                    
                    try:
                        # Create WAV file in memory
                        wav_buffer = BytesIO()
                        with wave.open(wav_buffer, 'wb') as wav_file:
                            wav_file.setnchannels(1)
                            wav_file.setsampwidth(2)
                            wav_file.setframerate(sample_rate)
                            wav_file.writeframes(audio_buffer)
                        
                        wav_buffer.seek(0)
                        
                        with sr.AudioFile(wav_buffer) as source:
                            audio = recognizer.record(source)
                        
                        final_text = recognizer.recognize_google(audio, language=language)
                    except:
                        final_text = ''
                else:
                    final_text = ''
                
                # Clean up
                del google_recognizers[client_id]
                if client_id in google_audio_buffers:
                    del google_audio_buffers[client_id]
                
                logger.info(f"🛑 Google Speech Recognition stopped for client {client_id}")
                emit('google_stopped', {'finalText': final_text})
        
        except Exception as e:
            logger.error(f"❌ Failed to stop Google Speech: {e}", exc_info=True)
            emit('google_error', {'error': str(e)})
    
    logger.info("✅ Google Speech Recognition WebSocket handlers registered")
    return True
