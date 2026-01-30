"""
Advanced Speech Recognition Engine - Google Assistant Quality ASR
Uses OpenAI Whisper API for accuracy, with offline fallback options
Implements noise handling, accent robustness, and context-aware recognition
"""

import logging
import threading
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from enum import Enum
import time
import numpy as np

try:
    import openai
    WHISPER_API_AVAILABLE = True
except ImportError:
    WHISPER_API_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    # Create a dummy sr module for type hints
    class sr:
        class AudioSource:
            pass

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Import privacy consent manager
try:
    from ai_assistant.core.privacy_consent import get_consent_manager, ConsentType
    CONSENT_MANAGER_AVAILABLE = True
except ImportError:
    CONSENT_MANAGER_AVAILABLE = False
    logger.warning("Privacy consent manager not available. External APIs will be used without consent checks!")


class RecognitionModel(Enum):
    """Available recognition models"""
    WHISPER_API = "whisper_api"  # Best accuracy (online)
    GOOGLE_CLOUD = "google_cloud"  # Very good (online)
    SPEECH_RECOGNITION = "speech_recognition"  # Good (online)
    VOSK = "vosk"  # Offline, instant
    OFFLINE_WHISPER = "offline_whisper"  # Whisper local


class AdvancedSpeechRecognizer:
    """
    Advanced speech recognition engine matching Google Assistant accuracy
    Multi-model approach with automatic fallback
    """
    
    def __init__(
        self,
        whisper_api_key: Optional[str] = None,
        google_cloud_key: Optional[str] = None,
        prefer_online: bool = True,
        noise_reduction: bool = True,
        cache_dir: str = "data/recognition_cache",
        user_id: str = "default_user",
        require_consent: bool = True
    ):
        """
        Initialize the advanced speech recognizer
        
        Args:
            whisper_api_key: OpenAI API key for Whisper
            google_cloud_key: Google Cloud API key
            prefer_online: Try online models first
            noise_reduction: Apply noise reduction to audio
            cache_dir: Directory for caching recognition results
            user_id: User identifier for consent management
            require_consent: Whether to check consent before using external APIs
        """
        self.whisper_api_key = whisper_api_key
        self.google_cloud_key = google_cloud_key
        self.prefer_online = prefer_online
        self.noise_reduction = noise_reduction
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.user_id = user_id
        self.require_consent = require_consent and CONSENT_MANAGER_AVAILABLE
        
        # Initialize consent manager
        if self.require_consent:
            self.consent_manager = get_consent_manager()
            logger.info("✅ Privacy consent manager enabled for speech recognition")
        else:
            self.consent_manager = None
            if require_consent:
                logger.warning("⚠️ Consent requested but not available!")
        
        # Initialize recognizers
        self.sr_recognizer = None
        self.vosk_models = {}
        self.google_recognizer = None
        
        # Performance tracking
        self.recognition_history = []
        self.confidence_scores = []
        
        # Initialize Advanced Noise Reduction
        self.noise_reducer = None
        if self.noise_reduction:
            try:
                from ai_assistant.voice.noise_reduction import NoiseReductionSystem, NoiseReductionConfig, NoiseReductionMethod
                self.noise_reducer = NoiseReductionSystem(
                    NoiseReductionConfig(
                        method=NoiseReductionMethod.HYBRID,
                        adaptive_parameters=True,
                        enable_vad_gating=True
                    )
                )
                logger.info("✅ Advanced Noise Reduction System initialized")
            except ImportError as e:
                logger.warning(f"⚠️ Advanced noise reduction not available: {e}. Using legacy noise gate.")
        
        self._initialize_recognizers()
    
    def _initialize_recognizers(self):
        """Initialize all available recognition engines"""
        # Speech Recognition library
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.sr_recognizer = sr.Recognizer()
                self.sr_recognizer.energy_threshold = 3000  # Noise threshold
                self.sr_recognizer.dynamic_energy_threshold = True
                self.sr_recognizer.pause_threshold = 0.8
                self.sr_recognizer.phrase_threshold = 0.3
                logger.info("✅ Speech Recognition library initialized")
            except Exception as e:
                logger.warning(f"⚠️ Speech Recognition failed: {e}")
        
        # Vosk (offline, instant) - Use singleton manager to prevent duplicate loading
        if VOSK_AVAILABLE:
            try:
                from ai_assistant.voice.vosk_model_manager import get_vosk_manager
                self.vosk_manager = get_vosk_manager()
                # Models will load on-demand when first used
                logger.info("✅ Vosk model manager connected (models load on-demand)")
            except ImportError:
                # Fallback to old behavior if manager not available
                logger.warning("⚠️ VoskModelManager not available, using legacy loading")
                self.vosk_manager = None
                self._legacy_vosk_init()
        
        # Whisper API
        if WHISPER_API_AVAILABLE and self.whisper_api_key:
            try:
                openai.api_key = self.whisper_api_key
                logger.info("✅ Whisper API configured")
            except Exception as e:
                logger.warning(f"⚠️ Whisper API setup failed: {e}")
    
    def _legacy_vosk_init(self):
        """Legacy Vosk initialization (fallback if manager unavailable)"""
        # Load English model
        en_model_path = Path("model/vosk-model-small-en-us-0.15")
        if en_model_path.exists():
            try:
                model = Model(str(en_model_path))
                self.vosk_models['en'] = model
                logger.info(f"✅ Vosk English model loaded (offline/private)")
            except Exception as e:
                logger.error(f"❌ Failed to load English model: {e}")
        else:
            logger.warning(f"⚠️ Vosk English model not found at {en_model_path}")
        
        # Load Hindi model (optional)
        hi_model_path = Path("model/vosk-model-small-hi-0.22")
        if hi_model_path.exists():
            try:
                model = Model(str(hi_model_path))
                self.vosk_models['hi'] = model
                logger.info(f"✅ Vosk Hindi model loaded (offline/private)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load Hindi model: {e}")
        else:
            logger.info("ℹ️ Vosk Hindi model not needed (optional)")
    
    def reduce_noise(self, audio_data, sr: int = 16000) -> np.ndarray:
        """
        Apply noise reduction to audio data
        Uses Advanced Noise Reduction System if available, otherwise simple gate
        
        Args:
            audio_data: Audio data as numpy array
            sr: Sample rate
        
        Returns:
            Noise-reduced audio array
        """
        if not self.noise_reduction:
            return audio_data
            
        # Use Advanced Noise Reduction if available
        if self.noise_reducer:
            try:
                return self.noise_reducer.reduce_noise(audio_data)
            except Exception as e:
                logger.error(f"Advanced noise reduction failed: {e}. Falling back to simple gate.")
        
        try:
            # Fallback: Simple noise gate (remove very low amplitude)
            noise_threshold = np.mean(np.abs(audio_data)) * 0.1
            reduced = np.copy(audio_data)
            reduced[np.abs(reduced) < noise_threshold] = 0
            
            # Normalize after noise reduction
            max_val = np.max(np.abs(reduced))
            if max_val > 0:
                reduced = (reduced / max_val) * 32767
            
            return reduced
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return audio_data
    
    async def recognize_whisper_api(
        self,
        audio_file: str,
        language: str = "en",
        prompt: Optional[str] = None
    ) -> Tuple[Optional[str], float]:
        """
        Recognize speech using OpenAI Whisper API
        Best accuracy, handles diverse accents and background noise
        
        PRIVACY: Sends audio to OpenAI servers. Requires user consent.
        
        Args:
            audio_file: Path to audio file
            language: Language code (en, hi, or auto for Hinglish)
            prompt: Optional context prompt to improve recognition
        
        Returns:
            Tuple of (recognized_text, confidence_score)
        """
        # Check consent
        if self.require_consent and not self.consent_manager.has_consent(self.user_id, ConsentType.EXTERNAL_STT):
            logger.warning(f"🚫 Whisper API blocked - user {self.user_id} has not consented to external STT")
            return None, 0.0
        
        if not WHISPER_API_AVAILABLE or not self.whisper_api_key:
            return None, 0.0
        
        try:
            # Map language codes for Whisper
            whisper_lang = None  # None = auto-detect
            context_prompt = prompt
            
            if language in ["en", "en-US", "en-IN", "en-GB"]:
                whisper_lang = "en"
                if not context_prompt:
                    context_prompt = "English speech with possible Indian accent."
            elif language in ["hi", "hi-IN"]:
                whisper_lang = "hi"
                if not context_prompt:
                    context_prompt = "Hindi speech, may contain some English words."
            elif language in ["auto", "hinglish"]:
                # Auto-detect for Hinglish (code-switching)
                whisper_lang = None
                if not context_prompt:
                    context_prompt = "Mixed Hindi and English speech (Hinglish). Contains both languages."
            else:
                whisper_lang = None  # Let Whisper auto-detect
            
            logger.info(f"🎤 Whisper API: language={whisper_lang or 'auto-detect'}, prompt='{context_prompt}'")
            
            with open(audio_file, 'rb') as f:
                # Prepare Whisper API call parameters
                api_params = {
                    'model': 'whisper-1',
                    'file': f,
                }
                
                # Add language if specified (omit for auto-detection)
                if whisper_lang:
                    api_params['language'] = whisper_lang
                
                # Add context prompt if provided
                if context_prompt:
                    api_params['prompt'] = context_prompt
                
                transcript = openai.Audio.transcribe(**api_params)
            
            text = transcript.get('text', '').strip()
            detected_lang = transcript.get('language', whisper_lang or 'unknown')
            
            logger.info(f"✅ Whisper recognized [{detected_lang}]: {text}")
            
            # Higher confidence for Whisper due to its robustness
            confidence = 0.95 if text else 0.0
            
            return text, confidence
            
        except Exception as e:
            logger.error(f"❌ Whisper API failed: {e}")
            return None, 0.0
    
    def recognize_google_cloud_speech(
        self,
        audio_file: str,
        language: str = "en-US"
    ) -> Tuple[Optional[str], float]:
        """
        Recognize speech using Google Cloud Speech-to-Text
        Very good accuracy, less latency than Whisper
        
        PRIVACY: Sends audio to Google servers. Requires user consent.
        
        Args:
            audio_file: Path to audio file
            language: Language code
        
        Returns:
            Tuple of (recognized_text, confidence_score)
        """
        # Check consent
        if self.require_consent and not self.consent_manager.has_consent(self.user_id, ConsentType.EXTERNAL_STT):
            logger.warning(f"🚫 Google Cloud Speech blocked - user {self.user_id} has not consented to external STT")
            return None, 0.0
        
        try:
            from google.cloud import speech_v1
            
            client = speech_v1.SpeechClient()
            
            with open(audio_file, 'rb') as f:
                audio = speech_v1.RecognitionAudio(content=f.read())
            
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language,
                enable_automatic_punctuation=True,
                model="latest_long",
            )
            
            response = client.recognize(config=config, audio=audio)
            
            if response.results:
                text = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                logger.info(f"✅ Google Cloud recognized: {text} (confidence: {confidence})")
                return text, confidence
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"❌ Google Cloud Speech failed: {e}")
            return None, 0.0
    
    def recognize_speech_recognition(
        self,
        audio_source: sr.AudioSource,
        language: str = "en-US"
    ) -> Tuple[Optional[str], float]:
        """
        Recognize speech using speech_recognition library (Google Speech-to-Text backend)
        Good accuracy, no API key needed
        
        Args:
            audio_source: Audio source from speech_recognition
            language: Language code
        
        Returns:
            Tuple of (recognized_text, confidence_score)
        """
        if not self.sr_recognizer:
            return None, 0.0
        
        try:
            # Adjust for ambient noise
            self.sr_recognizer.adjust_for_ambient_noise(audio_source, duration=0.1)
            
            # Listen
            audio = self.sr_recognizer.listen(
                audio_source,
                timeout=10.0,
                phrase_time_limit=15.0
            )
            
            # Recognize
            text = self.sr_recognizer.recognize_google(audio, language=language)
            logger.info(f"✅ Speech Recognition recognized: {text}")
            
            return text, 0.85  # Estimated confidence
            
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None, 0.0
        except sr.RequestError as e:
            logger.error(f"Speech Recognition API error: {e}")
            return None, 0.0
        except Exception as e:
            logger.error(f"Recognition failed: {e}")
            return None, 0.0
    
    def recognize_vosk(
        self,
        audio_data,
        language: str = "en"
    ) -> Tuple[Optional[str], float]:
        """
        Recognize speech using Vosk (offline, instant)
        Lower accuracy but works without internet
        
        Args:
            audio_data: Audio data
            language: Language code
        
        Returns:
            Tuple of (recognized_text, confidence_score)
        """
        # Get model from manager (lazy loads if needed) or use cached models
        model = None
        if hasattr(self, 'vosk_manager') and self.vosk_manager:
            model = self.vosk_manager.get_model(language)
        elif language in self.vosk_models:
            model = self.vosk_models[language]
        
        if model is None:
            return None, 0.0
        
        try:
            recognizer = KaldiRecognizer(model, 16000)
            recognizer.AcceptWaveform(audio_data)
            
            result = recognizer.Result()
            logger.info(f"✅ Vosk recognized: {result}")
            
            # Parse JSON result
            import json
            result_dict = json.loads(result)
            
            if 'result' in result_dict and result_dict['result']:
                text = ' '.join([item['word'] for item in result_dict['result']])
                return text, 0.75  # Estimated confidence
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Vosk recognition failed: {e}")
            return None, 0.0
    
    def recognize(
        self,
        audio_input,
        language: str = "en",
        context: Optional[str] = None
    ) -> Tuple[Optional[str], float, str]:
        """
        Recognize speech with automatic model selection and fallback
        
        Args:
            audio_input: Audio file path or audio source
            language: Language code (en, hi, en-IN, hi-IN, auto, hinglish)
            context: Optional context prompt for better accuracy
        
        Returns:
            Tuple of (recognized_text, confidence, model_used)
        """
        # Normalize language code for better compatibility
        normalized_lang = language.lower()
        
        # Map common variations - DEFAULT TO ENGLISH for best performance
        if normalized_lang in ["en", "en-us", "en-in", "en-gb", "english", "auto"]:
            whisper_lang = "en"
            google_lang = "en-US"  # US English as default
            vosk_lang = "en"
        elif normalized_lang in ["hinglish"]:
            whisper_lang = "auto"  # Let Whisper detect
            google_lang = "en-IN"  # Indian English for hinglish
            vosk_lang = "en"  # Use English model for hinglish
        elif normalized_lang in ["hi", "hi-in", "hindi"]:
            whisper_lang = "hi"
            google_lang = "hi-IN"
            vosk_lang = "hi" if "hi" in self.vosk_models else "en"  # Fallback to English if Hindi not available
        else:
            # Unknown language - default to English
            whisper_lang = "en"
            google_lang = "en-US"
            vosk_lang = "en"
        
        logger.info(f"🌐 Language mapping: input='{language}' -> whisper='{whisper_lang}', google='{google_lang}'")
        
        models_to_try = []
        
        if self.prefer_online:
            if self.whisper_api_key:
                models_to_try.append(("whisper_api", audio_input, whisper_lang))
            if self.google_cloud_key:
                models_to_try.append(("google_cloud", audio_input, google_lang))
            models_to_try.append(("speech_recognition", audio_input, google_lang))
        
        models_to_try.append(("vosk", audio_input, vosk_lang))
        
        for model_info in models_to_try:
            model_name = model_info[0]
            audio = model_info[1]
            lang_code = model_info[2] if len(model_info) > 2 else language
            
            try:
                if model_name == "whisper_api":
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    text, conf = loop.run_until_complete(
                        self.recognize_whisper_api(audio, lang_code, context)
                    )
                elif model_name == "google_cloud":
                    text, conf = self.recognize_google_cloud_speech(audio, lang_code)
                elif model_name == "speech_recognition" and self.sr_recognizer:
                    text, conf = self.recognize_speech_recognition(audio, lang_code)
                elif model_name == "vosk":
                    # Extract base language code for Vosk (en or hi)
                    vosk_base_lang = "hi" if "hi" in lang_code.lower() else "en"
                    text, conf = self.recognize_vosk(audio, vosk_base_lang)
                else:
                    continue
                
                if text and conf > 0.5:
                    logger.info(f"✅ Recognition successful with {model_name}: {text} (conf: {conf:.2f})")
                    self.recognition_history.append({"text": text, "model": model_name, "confidence": conf})
                    return text, conf, model_name
                    
            except Exception as e:
                logger.warning(f"Model {model_name} failed: {e}")
                continue
        
        logger.error("❌ All recognition models failed")
        return None, 0.0, "none"
    
    def get_recognition_stats(self) -> Dict:
        """Get recognition performance statistics"""
        if not self.recognition_history:
            return {}
        
        return {
            "total_recognitions": len(self.recognition_history),
            "average_confidence": np.mean([r["confidence"] for r in self.recognition_history]),
            "models_used": list(set([r["model"] for r in self.recognition_history])),
            "success_rate": len([r for r in self.recognition_history if r["confidence"] > 0.5]) / len(self.recognition_history)
        }


# Global instance
_recognizer_instance = None


def get_advanced_speech_recognizer(
    whisper_api_key: Optional[str] = None,
    google_cloud_key: Optional[str] = None
) -> AdvancedSpeechRecognizer:
    """Get or create the advanced speech recognizer instance"""
    global _recognizer_instance
    if _recognizer_instance is None:
        _recognizer_instance = AdvancedSpeechRecognizer(
            whisper_api_key=whisper_api_key,
            google_cloud_key=google_cloud_key
        )
    return _recognizer_instance


# Example usage
if __name__ == "__main__":
    recognizer = get_advanced_speech_recognizer()
    print("✅ Advanced Speech Recognizer initialized")
