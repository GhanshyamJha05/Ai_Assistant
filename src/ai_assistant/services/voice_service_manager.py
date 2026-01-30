"""
Comprehensive Voice Service Manager
Integrates all professional voice features: wake word detection, neural TTS,
VAD, speaker recognition, and continuous listening
"""

import logging
import asyncio
import threading
import queue
from typing import Optional, Callable, Dict, Any
from pathlib import Path

# Import all voice modules
try:
    from ai_assistant.voice.wake_word_detector import get_wake_word_manager, WakeWordDetectionMode
    WAKE_WORD_AVAILABLE = True
except ImportError:
    WAKE_WORD_AVAILABLE = False
    logging.warning("Wake word detector not available")

try:
    from ai_assistant.voice.neural_voice_engine import get_neural_voice_engine, VoiceGender, SpeakingStyle
    NEURAL_TTS_AVAILABLE = True
except ImportError:
    NEURAL_TTS_AVAILABLE = False
    logging.warning("Neural TTS not available")

try:
    from ai_assistant.voice.voice_activity_detection import create_vad_detector, VADSensitivity
    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False
    logging.warning("VAD not available")

try:
    from ai_assistant.voice.advanced_voice import (
        VoiceProfileManager,
        ContinuousListeningManager,
        voice_command_registry
    )
    ADVANCED_VOICE_AVAILABLE = True
except ImportError:
    ADVANCED_VOICE_AVAILABLE = False
    logging.warning("Advanced voice features not available")

try:
    from ai_assistant.voice.advanced_speech_recognizer import AdvancedSpeechRecognizer
    ADVANCED_STT_AVAILABLE = True
except ImportError:
    ADVANCED_STT_AVAILABLE = False
    logging.warning("Advanced STT not available")


class VoiceServiceManager:
    """
    Comprehensive voice service manager
    Coordinates all voice features: wake word, TTS, VAD, speaker recognition
    """
    
    def __init__(self, 
                 enable_wake_word: bool = True,
                 enable_neural_tts: bool = True,
                 enable_vad: bool = True,
                 enable_speaker_recognition: bool = True):
        
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
        # Configuration
        self.enable_wake_word = enable_wake_word and WAKE_WORD_AVAILABLE
        self.enable_neural_tts = enable_neural_tts and NEURAL_TTS_AVAILABLE
        self.enable_vad = enable_vad and VAD_AVAILABLE
        self.enable_speaker_recognition = enable_speaker_recognition and ADVANCED_VOICE_AVAILABLE
        
        # Components
        self.wake_word_manager = None
        self.tts_engine = None
        self.vad_detector = None
        self.voice_profile_manager = None
        self.speech_recognizer = None
        self.continuous_listener = None
        
        # Callbacks
        self.on_wake_word_detected: Optional[Callable] = None
        self.on_command_recognized: Optional[Callable] = None
        self.on_speaker_identified: Optional[Callable] = None
        
        # State
        self.current_speaker: Optional[str] = None
        self.is_listening_for_command = False
        
        # Initialize components
        self._initialize_components()
        
        self.logger.info(f"✅ Voice Service Manager initialized")
        self.logger.info(f"   Wake Word: {self.enable_wake_word}")
        self.logger.info(f"   Neural TTS: {self.enable_neural_tts}")
        self.logger.info(f"   VAD: {self.enable_vad}")
        self.logger.info(f"   Speaker Recognition: {self.enable_speaker_recognition}")
    
    def _initialize_components(self):
        """Initialize all voice components"""
        
        # 1. Wake Word Detector (PocketSphinx)
        if self.enable_wake_word:
            try:
                self.wake_word_manager = get_wake_word_manager(
                    detection_mode=WakeWordDetectionMode.ALWAYS_ON
                )
                self.wake_word_manager.detector.on_wake_word_detected = self._handle_wake_word
                self.logger.info("✅ Wake word detector initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize wake word detector: {e}")
                self.enable_wake_word = False
        
        # 2. Neural TTS Engine (Edge-TTS + Coqui)
        if self.enable_neural_tts:
            try:
                self.tts_engine = get_neural_voice_engine()
                self.logger.info("✅ Neural TTS engine initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize TTS engine: {e}")
                self.enable_neural_tts = False
        
        # 3. Voice Activity Detector
        if self.enable_vad:
            try:
                self.vad_detector = create_vad_detector(
                    sensitivity=VADSensitivity.MEDIUM
                )
                self.logger.info("✅ VAD initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize VAD: {e}")
                self.enable_vad = False
        
        # 4. Speaker Recognition
        if self.enable_speaker_recognition:
            try:
                self.voice_profile_manager = VoiceProfileManager()
                self.logger.info("✅ Voice profile manager initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize voice profiles: {e}")
                self.enable_speaker_recognition = False
        
        # 5. Advanced Speech Recognizer
        if ADVANCED_STT_AVAILABLE:
            try:
                self.speech_recognizer = AdvancedSpeechRecognizer(
                    prefer_online=True,
                    noise_reduction=True
                )
                self.logger.info("✅ Advanced speech recognizer initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize speech recognizer: {e}")
    
    def start(self):
        """Start all voice services"""
        if self.is_running:
            self.logger.warning("Voice services already running")
            return
        
        self.is_running = True
        
        # Start wake word detection
        if self.enable_wake_word and self.wake_word_manager:
            try:
                self.wake_word_manager.start()
                self.logger.info("🎤 Wake word detection started")
            except Exception as e:
                self.logger.error(f"Failed to start wake word detection: {e}")
        
        # Start continuous listening if available
        if ADVANCED_VOICE_AVAILABLE and self.continuous_listener:
            try:
                self.continuous_listener.start_listening()
                self.logger.info("👂 Continuous listening started")
            except Exception as e:
                self.logger.error(f"Failed to start continuous listening: {e}")
        
        self.logger.info("✅ All voice services started")
    
    def stop(self):
        """Stop all voice services"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop wake word detection
        if self.wake_word_manager:
            try:
                self.wake_word_manager.stop()
                self.logger.info("Wake word detection stopped")
            except Exception as e:
                self.logger.error(f"Error stopping wake word: {e}")
        
        # Stop continuous listening
        if self.continuous_listener:
            try:
                self.continuous_listener.stop_listening()
                self.logger.info("Continuous listening stopped")
            except Exception as e:
                self.logger.error(f"Error stopping listener: {e}")
        
        self.logger.info("Voice services stopped")
    
    def _handle_wake_word(self, wake_word: str, confidence: float):
        """Handle wake word detection"""
        self.logger.info(f"🎯 Wake word detected: '{wake_word}' (confidence: {confidence:.2f})")
        
        self.is_listening_for_command = True
        
        # Callback to frontend
        if self.on_wake_word_detected:
            self.on_wake_word_detected(wake_word, confidence)
        
        # Speak greeting
        self.speak_greeting()
    
    def speak_greeting(self):
        """Speak a greeting after wake word"""
        greetings = [
            "Yes, I'm listening",
            "How can I help you?",
            "I'm ready",
            "At your service"
        ]
        
        import random
        greeting = random.choice(greetings)
        
        self.speak_text(greeting)
    
    def speak_text(self, text: str, language: str = 'en', gender: str = 'female'):
        """Speak text using neural TTS"""
        if not self.enable_neural_tts or not self.tts_engine:
            self.logger.warning("Neural TTS not available")
            return None
        
        try:
            # Map gender string to VoiceGender enum
            voice_gender = VoiceGender.FEMALE if gender == 'female' else VoiceGender.MALE
            
            # Synthesize speech
            audio_file = self.tts_engine.synthesize(
                text,
                language=language,
                gender=voice_gender,
                style=SpeakingStyle.FRIENDLY,
                prefer_online=True
            )
            
            self.logger.info(f"🔊 TTS: '{text}' → {audio_file}")
            return audio_file
            
        except Exception as e:
            self.logger.error(f"TTS failed: {e}")
            return None
    
    async def speak_text_async(self, text: str, language: str = 'en', gender: str = 'female'):
        """Async version of speak_text"""
        if not self.enable_neural_tts or not self.tts_engine:
            return None
        
        try:
            voice_gender = VoiceGender.FEMALE if gender == 'female' else VoiceGender.MALE
            
            # Use Edge-TTS async method
            audio_file = await self.tts_engine.synthesize_edge_tts(
                text,
                language=language,
                gender=voice_gender
            )
            
            return audio_file
        except Exception as e:
            self.logger.error(f"Async TTS failed: {e}")
            return None
    
    def identify_speaker(self, audio_data) -> Optional[str]:
        """Identify speaker from audio"""
        if not self.enable_speaker_recognition or not self.voice_profile_manager:
            return None
        
        try:
            speaker = self.voice_profile_manager.identify_speaker(audio_data)
            
            if speaker:
                self.current_speaker = speaker
                self.logger.info(f"👤 Speaker identified: {speaker}")
                
                if self.on_speaker_identified:
                    self.on_speaker_identified(speaker)
            
            return speaker
            
        except Exception as e:
            self.logger.error(f"Speaker identification failed: {e}")
            return None
    
    def train_speaker(self, speaker_name: str, audio_data):
        """Train voice profile for a speaker"""
        if not self.enable_speaker_recognition or not self.voice_profile_manager:
            return False
        
        try:
            self.voice_profile_manager.add_voice_sample(speaker_name, audio_data)
            self.logger.info(f"✅ Added voice sample for {speaker_name}")
            return True
        except Exception as e:
            self.logger.error(f"Speaker training failed: {e}")
            return False
    
    def detect_voice_activity(self, audio_data) -> bool:
        """Detect if audio contains speech"""
        if not self.enable_vad or not self.vad_detector:
            return True  # Assume speech if VAD not available
        
        try:
            result = self.vad_detector.detect_voice_activity(audio_data)
            return result.is_speech
        except Exception as e:
            self.logger.error(f"VAD failed: {e}")
            return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all voice services"""
        return {
            'running': self.is_running,
            'wake_word': {
                'enabled': self.enable_wake_word,
                'active': self.wake_word_manager is not None,
                'stats': self.wake_word_manager.get_stats() if self.wake_word_manager else {}
            },
            'tts': {
                'enabled': self.enable_neural_tts,
                'active': self.tts_engine is not None
            },
            'vad': {
                'enabled': self.enable_vad,
                'active': self.vad_detector is not None,
                'status': self.vad_detector.get_status() if self.vad_detector else {}
            },
            'speaker_recognition': {
                'enabled': self.enable_speaker_recognition,
                'active': self.voice_profile_manager is not None,
                'current_speaker': self.current_speaker,
                'profiles': len(self.voice_profile_manager.profiles) if self.voice_profile_manager else 0
            },
            'listening_for_command': self.is_listening_for_command
        }
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        if not self.enable_neural_tts or not self.tts_engine:
            return []
        
        # Return available voices from neural engine
        return [
            {'language': 'en', 'gender': 'female', 'name': 'Aria (US English Female)'},
            {'language': 'en', 'gender': 'male', 'name': 'Guy (US English Male)'},
            {'language': 'en-IN', 'gender': 'female', 'name': 'Neerja (Indian English Female)'},
            {'language': 'en-IN', 'gender': 'male', 'name': 'Prabhat (Indian English Male)'},
            {'language': 'hi', 'gender': 'female', 'name': 'Swara (Hindi Female)'},
            {'language': 'hi', 'gender': 'male', 'name': 'Madhur (Hindi Male)'},
        ]


# Global instance
_voice_service_manager: Optional[VoiceServiceManager] = None


def get_voice_service_manager(
    enable_wake_word: bool = True,
    enable_neural_tts: bool = True,
    enable_vad: bool = True,
    enable_speaker_recognition: bool = True
) -> VoiceServiceManager:
    """Get or create voice service manager instance"""
    global _voice_service_manager
    
    if _voice_service_manager is None:
        _voice_service_manager = VoiceServiceManager(
            enable_wake_word=enable_wake_word,
            enable_neural_tts=enable_neural_tts,
            enable_vad=enable_vad,
            enable_speaker_recognition=enable_speaker_recognition
        )
    
    return _voice_service_manager


# Example usage
if __name__ == "__main__":
    # Initialize voice services
    voice_manager = get_voice_service_manager()
    
    # Set up callbacks
    def on_wake_word(word, confidence):
        print(f"🎯 Wake word: {word} ({confidence:.2f})")
    
    def on_speaker(speaker):
        print(f"👤 Speaker: {speaker}")
    
    voice_manager.on_wake_word_detected = on_wake_word
    voice_manager.on_speaker_identified = on_speaker
    
    # Start services
    voice_manager.start()
    
    print("Voice services running. Press Ctrl+C to stop...")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        voice_manager.stop()
        print("Stopped")
