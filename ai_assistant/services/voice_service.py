"""
Voice Service Module - Complete Voice System Integration
Provides unified interface for TTS, STT, Wake Word Detection, and Voice Processing
"""

import asyncio
import os
import sys
import json
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime

# Import voice engines
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Import voice modules
try:
    from ai_assistant.voice.neural_voice_engine import NeuralVoiceEngine
    from ai_assistant.voice.advanced_speech_recognizer import AdvancedSpeechRecognizer
    from ai_assistant.voice.wake_word_detector import WakeWordDetector
    from ai_assistant.voice.voice_activity_detection import VoiceActivityDetector
    VOICE_MODULES_AVAILABLE = True
except ImportError:
    VOICE_MODULES_AVAILABLE = False

# Logging
try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class VoiceService:
    """
    Unified Voice Service - Integrates all voice functionality
    - Text-to-Speech (TTS) with multiple engines
    - Speech-to-Text (STT) with fallback support
    - Wake Word Detection
    - Voice Activity Detection
    - Audio caching and optimization
    """
    
    def __init__(self, config_path: str = "config/voice_config.json"):
        """Initialize Voice Service with configuration"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Voice engines
        self.tts_engine = None
        self.stt_engine = None
        self.wake_word_detector = None
        self.vad_detector = None
        
        # State
        self.is_listening = False
        self.is_speaking = False
        self.wake_word_active = False
        
        # History and cache
        self.voice_history = []
        self.audio_cache = {}
        
        # Initialize engines
        self._initialize_engines()
        
        logger.info("✅ Voice Service initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load voice configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded voice config from {self.config_path}")
                return config
            else:
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading voice config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default voice configuration"""
        return {
            "tts": {
                "default_engine": "edge_tts",
                "default_voice": "en-US-AriaNeural",
                "speed": 1.0,
                "volume": 0.9
            },
            "stt": {
                "default_engine": "whisper_api",
                "language": "en-US",
                "continuous": True
            },
            "wake_word": {
                "enabled": True,
                "phrases": ["hey daddy", "ok daddy"],
                "sensitivity": 0.5
            }
        }
    
    def _initialize_engines(self):
        """Initialize all voice engines"""
        logger.info("Initializing voice engines...")
        
        # Initialize TTS
        self._initialize_tts()
        
        # Initialize STT
        self._initialize_stt()
        
        # Initialize Wake Word Detection
        self._initialize_wake_word()
        
        # Initialize VAD
        self._initialize_vad()
    
    def _initialize_tts(self):
        """Initialize Text-to-Speech engine"""
        try:
            if VOICE_MODULES_AVAILABLE:
                self.tts_engine = NeuralVoiceEngine()
                logger.info("✅ Neural Voice Engine (Edge-TTS) initialized")
            elif PYTTSX3_AVAILABLE:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.9)
                logger.info("✅ pyttsx3 TTS initialized")
            else:
                logger.warning("⚠️ No TTS engine available")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
    
    def _initialize_stt(self):
        """Initialize Speech-to-Text engine"""
        try:
            if SPEECH_RECOGNITION_AVAILABLE:
                self.stt_engine = sr.Recognizer()
                # Configure recognition settings
                self.stt_engine.energy_threshold = self.config.get('stt', {}).get('energy_threshold', 4000)
                self.stt_engine.dynamic_energy_threshold = True
                self.stt_engine.pause_threshold = 0.8
                logger.info("✅ Speech Recognition engine initialized")
            else:
                logger.warning("⚠️ Speech Recognition not available")
        except Exception as e:
            logger.error(f"Failed to initialize STT: {e}")
    
    def _initialize_wake_word(self):
        """Initialize Wake Word Detection"""
        try:
            wake_config = self.config.get('wake_word', {})
            if wake_config.get('enabled', False) and VOICE_MODULES_AVAILABLE:
                self.wake_word_detector = WakeWordDetector(
                    wake_words=wake_config.get('phrases', ['hey daddy']),
                    sensitivity=wake_config.get('sensitivity', 0.5)
                )
                logger.info("✅ Wake Word Detector initialized")
            else:
                logger.info("Wake Word Detection disabled or unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize Wake Word Detector: {e}")
    
    def _initialize_vad(self):
        """Initialize Voice Activity Detection"""
        try:
            if VOICE_MODULES_AVAILABLE:
                self.vad_detector = VoiceActivityDetector()
                logger.info("✅ Voice Activity Detector initialized")
        except Exception as e:
            logger.warning(f"VAD not available: {e}")
    
    # ============================================
    # Text-to-Speech Methods
    # ============================================
    
    async def speak_async(self, text: str, voice: Optional[str] = None, **kwargs) -> bool:
        """Speak text asynchronously using Edge-TTS"""
        try:
            if not EDGE_TTS_AVAILABLE:
                logger.error("Edge-TTS not available")
                return False
            
            self.is_speaking = True
            
            # Get voice from config
            voice_id = voice or self.config['tts']['default_voice']
            
            # Generate audio
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
            
            # Create communication
            communicate = edge_tts.Communicate(text, voice_id)
            await communicate.save(output_path)
            
            # Play audio
            self._play_audio_file(output_path)
            
            # Cleanup
            os.unlink(output_path)
            
            self.is_speaking = False
            return True
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            self.is_speaking = False
            return False
    
    def speak(self, text: str, voice: Optional[str] = None, **kwargs) -> bool:
        """Speak text synchronously"""
        try:
            # Try async Edge-TTS first
            if EDGE_TTS_AVAILABLE:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                return loop.run_until_complete(self.speak_async(text, voice, **kwargs))
            
            # Fallback to pyttsx3
            elif PYTTSX3_AVAILABLE and self.tts_engine:
                self.is_speaking = True
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                self.is_speaking = False
                return True
            
            # Fallback to gTTS
            elif GTTS_AVAILABLE:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                tts = gTTS(text=text, lang='en')
                tts.save(temp_file.name)
                self._play_audio_file(temp_file.name)
                os.unlink(temp_file.name)
                return True
            
            else:
                logger.error("No TTS engine available")
                return False
                
        except Exception as e:
            logger.error(f"Speak error: {e}")
            self.is_speaking = False
            return False
    
    def _play_audio_file(self, file_path: str):
        """Play audio file using pygame or system player"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except:
            # Fallback to system player
            if sys.platform == 'win32':
                os.system(f'start {file_path}')
            elif sys.platform == 'darwin':
                os.system(f'afplay {file_path}')
            else:
                os.system(f'mpg123 {file_path}')
    
    # ============================================
    # Speech-to-Text Methods
    # ============================================
    
    def listen(self, timeout: Optional[int] = None, phrase_time_limit: Optional[int] = None) -> Optional[str]:
        """Listen for speech and return transcribed text"""
        if not SPEECH_RECOGNITION_AVAILABLE or not self.stt_engine:
            logger.error("Speech recognition not available")
            return None
        
        try:
            self.is_listening = True
            
            with sr.Microphone() as source:
                logger.info("🎤 Listening...")
                
                # Adjust for ambient noise
                self.stt_engine.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.stt_engine.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                logger.info("🔄 Processing speech...")
                
                # Try multiple recognition engines
                text = self._recognize_speech(audio)
                
                self.is_listening = False
                
                if text:
                    logger.info(f"✅ Recognized: {text}")
                    self._add_to_history(text)
                    return text
                else:
                    logger.warning("No speech recognized")
                    return None
                
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout")
            self.is_listening = False
            return None
        except Exception as e:
            logger.error(f"Listen error: {e}")
            self.is_listening = False
            return None
    
    def _recognize_speech(self, audio) -> Optional[str]:
        """Try multiple recognition engines in order of priority"""
        engines = [
            ('google', lambda: self.stt_engine.recognize_google(audio)),
            ('whisper_api', lambda: self._recognize_whisper(audio)),
            ('sphinx', lambda: self.stt_engine.recognize_sphinx(audio))
        ]
        
        for engine_name, recognize_func in engines:
            try:
                text = recognize_func()
                if text:
                    logger.info(f"Recognition successful using {engine_name}")
                    return text
            except Exception as e:
                logger.debug(f"{engine_name} recognition failed: {e}")
                continue
        
        return None
    
    def _recognize_whisper(self, audio) -> Optional[str]:
        """Recognize speech using OpenAI Whisper API"""
        try:
            # This requires OpenAI API key
            import openai
            # Convert audio to file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                with open(f.name, 'wb') as audio_file:
                    audio_file.write(audio.get_wav_data())
                
                with open(f.name, 'rb') as audio_file:
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)
                    os.unlink(f.name)
                    return transcript.text
        except Exception as e:
            logger.debug(f"Whisper API error: {e}")
            return None
    
    # ============================================
    # Wake Word Detection
    # ============================================
    
    def start_wake_word_detection(self, callback: Callable):
        """Start listening for wake word"""
        if not self.wake_word_detector:
            logger.warning("Wake word detector not available")
            return
        
        self.wake_word_active = True
        
        def detection_thread():
            while self.wake_word_active:
                try:
                    detected = self.wake_word_detector.detect()
                    if detected:
                        logger.info("🎙️ Wake word detected!")
                        callback()
                    time.sleep(0.1)
                except Exception as e:
                    logger.error(f"Wake word detection error: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=detection_thread, daemon=True)
        thread.start()
    
    def stop_wake_word_detection(self):
        """Stop wake word detection"""
        self.wake_word_active = False
    
    # ============================================
    # Utility Methods
    # ============================================
    
    def _add_to_history(self, text: str):
        """Add recognized text to history"""
        self.voice_history.append({
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'type': 'recognized'
        })
        
        # Keep only last 100 items
        if len(self.voice_history) > 100:
            self.voice_history = self.voice_history[-100:]
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get voice command history"""
        return self.voice_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice service status"""
        return {
            'tts_available': self.tts_engine is not None,
            'stt_available': self.stt_engine is not None,
            'wake_word_available': self.wake_word_detector is not None,
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'wake_word_active': self.wake_word_active,
            'engines': {
                'edge_tts': EDGE_TTS_AVAILABLE,
                'pyttsx3': PYTTSX3_AVAILABLE,
                'gtts': GTTS_AVAILABLE,
                'speech_recognition': SPEECH_RECOGNITION_AVAILABLE
            }
        }
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available TTS voices"""
        voices = []
        
        # Edge-TTS voices
        if EDGE_TTS_AVAILABLE:
            voices.extend([
                {'id': 'en-US-AriaNeural', 'name': 'Aria (US Female)', 'language': 'en-US', 'gender': 'female'},
                {'id': 'en-US-GuyNeural', 'name': 'Guy (US Male)', 'language': 'en-US', 'gender': 'male'},
                {'id': 'en-GB-SoniaNeural', 'name': 'Sonia (UK Female)', 'language': 'en-GB', 'gender': 'female'},
                {'id': 'hi-IN-SwaraNeural', 'name': 'Swara (Hindi Female)', 'language': 'hi-IN', 'gender': 'female'},
                {'id': 'hi-IN-MadhurNeural', 'name': 'Madhur (Hindi Male)', 'language': 'hi-IN', 'gender': 'male'},
            ])
        
        return voices


# Global instance
_voice_service_instance = None

def get_voice_service(config_path: str = "config/voice_config.json") -> VoiceService:
    """Get or create voice service singleton"""
    global _voice_service_instance
    if _voice_service_instance is None:
        _voice_service_instance = VoiceService(config_path)
    return _voice_service_instance


if __name__ == "__main__":
    # Test voice service
    service = get_voice_service()
    print("Voice Service Status:", service.get_status())
    
    # Test TTS
    print("\nTesting TTS...")
    service.speak("Hello! Voice service is working perfectly.")
    
    # Test STT
    print("\nTesting STT... Please speak something:")
    text = service.listen(timeout=5)
    if text:
        print(f"You said: {text}")
