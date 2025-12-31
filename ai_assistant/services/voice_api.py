# Voice endpoints added by AI assistant
# Location: f:\bn\assitant\ai_assistant\services\voice_api.py

from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
import hashlib
import time
from functools import lru_cache
from typing import Dict, Optional

voice_bp = Blueprint('voice', __name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"]
)

# Check if voice synthesis is available
try:
    import edge_tts
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logging.warning("Edge-TTS not available. Voice preview will not work.")

# Available Voice Options for TTS
AVAILABLE_VOICES = [
    {"id": "en-US-AriaNeural", "name": "Aria", "gender": "female", "accent": "US", "language": "en-US", "description": "Warm and friendly", "personality": "Friendly and conversational"},
    {"id": "en-US-JennyNeural", "name": "Jenny", "gender": "female", "accent": "US", "language": "en-US", "description": "Professional and clear", "personality": "Professional and articulate"},
    {"id": "en-US-GuyNeural", "name": "Guy", "gender": "male", "accent": "US", "language": "en-US", "description": "Confident and professional", "personality": "Confident and authoritative"},
    {"id": "en-US-DavisNeural", "name": "Davis", "gender": "male", "accent": "US", "language": "en-US", "description": "Warm and conversational", "personality": "Warm and approachable"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia", "gender": "female", "accent": "UK", "language": "en-GB", "description": "British elegance", "personality": "Elegant and refined"},
    {"id": "en-GB-RyanNeural", "name": "Ryan", "gender": "male", "accent": "UK", "language": "en-GB", "description": "British sophistication", "personality": "Sophisticated and clear"},
    {"id": "en-IN-NeerjaNeural", "name": "Neerja", "gender": "female", "accent": "Indian", "language": "en-IN", "description": "Indian warmth", "personality": "Warm and expressive"},
    {"id": "en-IN-PrabhatNeural", "name": "Prabhat", "gender": "male", "accent": "Indian", "language": "en-IN", "description": "Indian clarity", "personality": "Clear and professional"},
    {"id": "en-US-AnaNeural", "name": "Ana", "gender": "female", "accent": "US", "language": "en-US", "description": "Energetic and cheerful", "personality": "Cheerful and enthusiastic"},
    {"id": "en-US-ChristopherNeural", "name": "Christopher", "gender": "male", "accent": "US", "language": "en-US", "description": "Deep and reassuring", "personality": "Calm and reassuring"},
    {"id": "en-GB-LibbyNeural", "name": "Libby", "gender": "female", "accent": "UK", "language": "en-GB", "description": "Young and friendly British", "personality": "Youthful and energetic"},
    {"id": "en-US-EricNeural", "name": "Eric", "gender": "male", "accent": "US", "language": "en-US", "description": "Natural and friendly", "personality": "Casual and friendly"}
]

# Default preview text
DEFAULT_PREVIEW_TEXT = "Hello! This is a sample of my voice. I'm here to assist you with anything you need."

# ============================================================================
# CACHING SYSTEM for Voice Previews
# ============================================================================

class VoicePreviewCache:
    """In-memory LRU cache for voice previews with expiration"""
    
    def __init__(self, max_size: int = 50, expiry_seconds: int = 3600):
        self.cache: Dict[str, dict] = {}
        self.max_size = max_size
        self.expiry_seconds = expiry_seconds
        self.hits = 0
        self.misses = 0
    
    def get_cache_key(self, voice_id: str, text: str) -> str:
        """Generate cache key from voice_id and text"""
        content = f"{voice_id}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[dict]:
        """Get cached preview if exists and not expired"""
        if key in self.cache:
            cached = self.cache[key]
            if time.time() - cached['timestamp'] < self.expiry_seconds:
                self.hits += 1
                return cached['data']
            else:
                # Expired, remove
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, data: dict):
        """Cache preview data with LRU eviction"""
        # If cache is full, remove oldest entry
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }

# Global cache instance
preview_cache = VoicePreviewCache()

def generate_voice_preview(voice_id: str, text: str) -> dict:
    """Generate voice preview audio (internal function)"""
    import tempfile
    import asyncio
    import base64
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    output_path = temp_file.name
    temp_file.close()
    
    # Generate audio asynchronously
    async def generate():
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(output_path)
    
    # Run async function
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(generate())
    
    # Read and encode as base64
    with open(output_path, 'rb') as f:
        audio_data = f.read()
    
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Clean up temp file
    try:
        os.unlink(output_path)
    except Exception as cleanup_error:
        logging.warning(f"Failed to clean up temp file: {cleanup_error}")
    
    return f"data:audio/mp3;base64,{audio_base64}"

# ============================================================================
# API ENDPOINTS
# ============================================================================

@voice_bp.route('/list', methods=['GET'])
def api_list_voices():
    """Get list of available AI voices"""
    try:
        return jsonify({
            "success": True,
            "voices": AVAILABLE_VOICES,
            "default": "en-US-AriaNeural",
            "total": len(AVAILABLE_VOICES)
        }), 200
    except Exception as e:
        logging.error(f"Error fetching voice list: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch voices"
        }), 500

@voice_bp.route('/preview', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limiting
def api_preview_voice():
    """Generate preview audio for a voice (with caching)"""
    
    # Check if voice synthesis is available
    if not VOICE_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Voice synthesis not available. Edge-TTS is not installed."
        }), 503
    
    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        voice_id = data.get('voice_id')
        if not voice_id:
            return jsonify({
                "success": False,
                "error": "voice_id is required"
            }), 400
        
        # Validate voice_id exists
        voice_info = next((v for v in AVAILABLE_VOICES if v['id'] == voice_id), None)
        if not voice_info:
            return jsonify({
                "success": False,
                "error": f"Invalid voice_id: {voice_id}. Use /api/voice/list to get valid voices."
            }), 404
        
        # Get sample text (with length limit for safety)
        sample_text = data.get('text', DEFAULT_PREVIEW_TEXT)
        if len(sample_text) > 500:
            return jsonify({
                "success": False,
                "error": "Text too long. Maximum 500 characters allowed."
            }), 400
        
        # Check cache first
        cache_key = preview_cache.get_cache_key(voice_id, sample_text)
        cached_audio = preview_cache.get(cache_key)
        
        if cached_audio:
            # Return from cache (fast!)
            return jsonify({
                "success": True,
                "voice_id": voice_id,
                "voice_name": voice_info['name'],
                "audio_data": cached_audio,
                "text": sample_text,
                "cached": True
            }), 200
        
        # Generate audio using Edge-TTS
        try:
            audio_data_base64 = generate_voice_preview(voice_id, sample_text)
            
            # Cache the result
            preview_cache.set(cache_key, audio_data_base64)
            
            return jsonify({
                "success": True,
                "voice_id": voice_id,
                "voice_name": voice_info['name'],
                "audio_data": audio_data_base64,
                "text": sample_text,
                "cached": False
            }), 200
            
        except ImportError as ie:
            logging.error(f"Import error in preview generation: {ie}")
            return jsonify({
                "success": False,
                "error": "Required library not available"
            }), 503
        except asyncio.TimeoutError:
            logging.error("Edge-TTS timeout")
            return jsonify({
                "success": False,
                "error": "Voice generation timed out. Please try again."
            }), 504
        except Exception as e:
            logging.error(f"Edge-TTS preview failed: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Preview generation failed: {str(e)}"
            }), 500
            
    except Exception as e:
        logging.error(f"Voice preview error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to generate preview"
        }), 500

@voice_bp.route('/cache/stats', methods=['GET'])
def api_cache_stats():
    """Get cache statistics (for monitoring)"""
    try:
        stats = preview_cache.get_stats()
        return jsonify({
            "success": True,
            "cache_stats": stats
        }), 200
    except Exception as e:
        logging.error(f"Error getting cache stats: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get cache stats"
        }), 500

# ============================================================================
# CACHE PRE-WARMING (Optional - can be called at startup)
# ============================================================================

def prewarm_voice_cache():
    """Pre-generate previews for all voices with default text"""
    if not VOICE_AVAILABLE:
        logging.warning("Cannot prewarm cache: Edge-TTS not available")
        return
    
    logging.info("🔄 Pre-warming voice preview cache...")
    success_count = 0
    
    for voice in AVAILABLE_VOICES:
        try:
            voice_id = voice['id']
            audio_data = generate_voice_preview(voice_id, DEFAULT_PREVIEW_TEXT)
            cache_key = preview_cache.get_cache_key(voice_id, DEFAULT_PREVIEW_TEXT)
            preview_cache.set(cache_key, audio_data)
            success_count += 1
            logging.info(f"   ✅ Cached preview for {voice['name']}")
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to cache {voice['name']}: {e}")
    
    logging.info(f"✅ Cache pre-warming complete: {success_count}/{len(AVAILABLE_VOICES)} voices cached")

