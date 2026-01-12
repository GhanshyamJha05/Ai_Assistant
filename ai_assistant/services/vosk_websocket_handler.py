"""
Real-time Vosk Speech Recognition via WebSocket
Provides 100% offline/private speech recognition
"""

import json
import logging
from pathlib import Path
from flask_socketio import emit

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

# Initialize logger
try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Global recognizer instances per client
vosk_recognizers = {}
vosk_models = {}

def load_vosk_models():
    """Load Vosk models on startup"""
    if not VOSK_AVAILABLE:
        logger.warning("⚠️ Vosk not available - install with: pip install vosk")
        return False
    
    # Load English model
    en_model_path = Path("model/vosk-model-small-en-us-0.15")
    if en_model_path.exists():
        try:
            vosk_models['en'] = Model(str(en_model_path))
            logger.info(f"✅ Vosk English model loaded for WebSocket streaming")
        except Exception as e:
            logger.error(f"❌ Failed to load English model: {e}")
            return False
    else:
        logger.error(f"❌ Vosk model not found at {en_model_path}")
        return False
    
    # Load Hindi model (optional)
    hi_model_path = Path("model/vosk-model-small-hi-0.22")
    if hi_model_path.exists():
        try:
            vosk_models['hi'] = Model(str(hi_model_path))
            logger.info(f"✅ Vosk Hindi model loaded for WebSocket streaming")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load Hindi model: {e}")
    
    return True

def register_vosk_handlers(socketio):
    """Register Vosk WebSocket event handlers"""
    
    @socketio.on('vosk_start_recognition')
    def handle_start_vosk(data):
        """Start Vosk recognition session"""
        if not VOSK_AVAILABLE or not vosk_models:
            emit('vosk_error', {'error': 'Vosk models not loaded'})
            return
        
        try:
            from flask import request
            client_id = request.sid
            language = data.get('language', 'en')
            sample_rate = data.get('sampleRate', 16000)
            
            # Get model for language
            lang_key = 'hi' if 'hi' in language.lower() else 'en'
            if lang_key not in vosk_models:
                lang_key = 'en'  # Fallback to English
            
            # Create recognizer for this client
            recognizer = KaldiRecognizer(vosk_models[lang_key], sample_rate)
            recognizer.SetWords(True)  # Enable word-level timestamps
            vosk_recognizers[client_id] = recognizer
            
            logger.info(f"🎤 Vosk recognition started for client {client_id} (lang: {lang_key}, rate: {sample_rate}Hz)")
            emit('vosk_ready', {'language': lang_key, 'mode': 'offline'})
            
        except Exception as e:
            logger.error(f"❌ Failed to start Vosk: {e}", exc_info=True)
            emit('vosk_error', {'error': str(e)})
    
    @socketio.on('vosk_audio_chunk')
    def handle_vosk_audio(data):
        """Process audio chunk with Vosk"""
        try:
            from flask import request
            client_id = request.sid
            
            if client_id not in vosk_recognizers:
                emit('vosk_error', {'error': 'Recognition not started'})
                return
            
            recognizer = vosk_recognizers[client_id]
            audio_data = data.get('audio')  # Base64 or binary
            
            if isinstance(audio_data, str):
                # Decode base64 if needed
                import base64
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = bytes(audio_data)
            
            # Process audio chunk
            if recognizer.AcceptWaveform(audio_bytes):
                # Final result
                result = json.loads(recognizer.Result())
                if result.get('text'):
                    logger.info(f"📝 Vosk final: {result['text']}")
                    emit('vosk_transcript', {
                        'text': result['text'],
                        'isFinal': True,
                        'confidence': 1.0,
                        'mode': 'offline'
                    })
            else:
                # Partial result
                partial = json.loads(recognizer.PartialResult())
                if partial.get('partial'):
                    emit('vosk_transcript', {
                        'text': partial['partial'],
                        'isFinal': False,
                        'mode': 'offline'
                    })
        
        except Exception as e:
            logger.error(f"❌ Vosk audio processing error: {e}", exc_info=True)
            emit('vosk_error', {'error': str(e)})
    
    @socketio.on('vosk_stop_recognition')
    def handle_stop_vosk():
        """Stop Vosk recognition session"""
        try:
            from flask import request
            client_id = request.sid
            
            if client_id in vosk_recognizers:
                # Get final result
                recognizer = vosk_recognizers[client_id]
                final_result = json.loads(recognizer.FinalResult())
                
                # Clean up
                del vosk_recognizers[client_id]
                
                logger.info(f"🛑 Vosk recognition stopped for client {client_id}")
                emit('vosk_stopped', {'finalText': final_result.get('text', '')})
            
        except Exception as e:
            logger.error(f"❌ Failed to stop Vosk: {e}", exc_info=True)
            emit('vosk_error', {'error': str(e)})
    
    logger.info("✅ Vosk WebSocket handlers registered")

# Initialize models on module load
if VOSK_AVAILABLE:
    load_vosk_models()
