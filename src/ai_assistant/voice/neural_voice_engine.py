"""
Neural Voice Engine for YourDaddy AI Assistant
Provides high-quality neural voice synthesis using KittenTTS (primary, offline) and Edge-TTS (fallback, online).
"""
import asyncio
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from enum import Enum
import threading
import time

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import kittentts
    KITTEN_AVAILABLE = True
except ImportError:
    KITTEN_AVAILABLE = False

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class VoiceGender(Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class SpeakingStyle(Enum):
    """Speaking style options for natural conversation"""
    NORMAL = "normal"
    EXCITED = "excited"
    CALM = "calm"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CHEERFUL = "cheerful"


class NeuralVoiceEngine:
    """
    High-quality neural voice synthesis engine
    """
    
    def __init__(self, cache_dir: str = "data/voice_cache", gpu: bool = False):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.gpu = gpu
        
        # Voice configurations for edge-tts
        self.edge_voices = {
            'en': {
                'female': 'en-US-AriaNeural',
                'male': 'en-US-GuyNeural',
                'neutral': 'en-US-AriaNeural'
            },
            'hi': {
                'female': 'hi-IN-SwaraNeural',
                'male': 'hi-IN-MadhurNeural',
                'neutral': 'hi-IN-SwaraNeural'
            }
        }
        
        # Initialize engines
        self.edge_tts_available = EDGE_TTS_AVAILABLE
        self.kitten_tts = None
        self.kitten_available = KITTEN_AVAILABLE
        
        self._initialize_engines()
        
    def _initialize_engines(self):
        """Initialize all available TTS engines"""
        if self.kitten_available:
             logger.info("✅ KittenTTS available (Primary Offline Voice Engine)")
        else:
             logger.warning("⚠️ KittenTTS not available. Install: pip install kittentts")
             
        if self.edge_tts_available:
            logger.info("✅ Edge-TTS available (Fallback Online Voice Engine)")
        else:
            logger.warning("⚠️ Edge-TTS not available. Install: pip install edge-tts")

    def synthesize_kitten_tts(
        self,
        text: str,
        voice: str = "Jasper",
        speed: float = 1.0,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """Synthesize speech using KittenTTS (offline, ultra-lightweight)"""
        if not self.kitten_available or not text:
            return None
            
        try:
            logger.info(f"⏳ Synthesizing with KittenTTS: {text[:50]}...")
            
            # Lazy load the model
            if self.kitten_tts is None:
                from kittentts import KittenTTS
                self.kitten_tts = KittenTTS("KittenML/kitten-tts-mini-0.8")
                
            if voice not in self.kitten_tts.available_voices:
                voice = "Jasper" # Default fallback
                
            # Cache key
            cache_key = f"kitten_{text[:30].replace(' ', '_')}_{voice}.wav"
            cache_file = self.cache_dir / cache_key
            
            output_file = output_file or str(cache_file)
            if Path(output_file).exists():
                return output_file
                
            # Generate audio
            self.kitten_tts.tts_to_file(text, output_file, voice=voice, speed=speed)
            logger.info(f"✅ KittenTTS Synthesized -> {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ KittenTTS synthesis failed: {e}")
            return None

    async def synthesize_edge_tts(
        self,
        text: str,
        language: str = 'en',
        gender: VoiceGender = VoiceGender.FEMALE,
        rate: float = 0.0,
        pitch: float = 0.0,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """Synthesize speech using Edge-TTS (fallback)"""
        if not self.edge_tts_available or not text:
            return None
        
        try:
            voice_key = gender.value if gender.value != 'neutral' else 'female'
            voice = self.edge_voices.get(language, self.edge_voices['en']).get(
                voice_key, 'en-US-AriaNeural'
            )
            
            cache_key = f"edge_{text[:30].replace(' ', '_')}_{language}_{gender.value}.mp3"
            cache_file = self.cache_dir / cache_key
            
            if cache_file.exists():
                return str(cache_file)
            
            output_file = output_file or str(cache_file)
            
            rate_str = f"+{int(rate)}%" if rate >= 0 else f"{int(rate)}%"
            pitch_str = f"+{int(pitch)}Hz" if pitch >= 0 else f"{int(pitch)}Hz"
            
            communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
            await communicate.save(output_file)
            logger.info(f"✅ Edge-TTS Synthesized -> {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Edge-TTS synthesis failed: {e}")
            return None
    
    def synthesize_edge_tts_sync(
        self,
        text: str,
        language: str = 'en',
        gender: VoiceGender = VoiceGender.FEMALE,
        rate: float = 0.0,
        pitch: float = 0.0,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """Synchronous wrapper for Edge-TTS"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.synthesize_edge_tts(text, language, gender, rate, pitch, output_file)
        )

    def speak(
        self, 
        text: str, 
        language: str = 'en',
        style: SpeakingStyle = SpeakingStyle.NORMAL,
        gender: VoiceGender = VoiceGender.FEMALE,
        output_file: Optional[str] = None,
        force_engine: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate audio using KittenTTS, falling back to Edge-TTS.
        Returns the path to the audio file.
        """
        if not text:
            return None
            
        logger.info(f"🎤 Synthesizing speech: {text[:50]}...")
        result_file = None
        
        # Primary Engine: KittenTTS
        if self.kitten_available and force_engine in [None, 'kittentts']:
            # Map gender to kitten voices roughly
            kitten_voice = "Jasper" if gender == VoiceGender.MALE else "Bella"
            result_file = self.synthesize_kitten_tts(text, voice=kitten_voice, output_file=output_file)
            
        # Fallback Engine: Edge-TTS
        if not result_file and self.edge_tts_available and force_engine in [None, 'edge_tts']:
            result_file = self.synthesize_edge_tts_sync(text, language, gender, output_file=output_file)
            
        if not result_file:
            logger.error("❌ All TTS engines failed or are unavailable.")
            
        return result_file

# Singleton instance
_engine_instance = None

def get_neural_voice_engine(cache_dir: str = "data/voice_cache", gpu: bool = False) -> NeuralVoiceEngine:
    """Get or create the neural voice engine singleton"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = NeuralVoiceEngine(cache_dir=cache_dir, gpu=gpu)
    return _engine_instance
