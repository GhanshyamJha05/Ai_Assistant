# YourDaddy Assistant - Modern Web Backend
"""
Modern Flask backend to serve the React frontend and provide real-time APIs
for YourDaddy Assistant's features.
"""
# print("Server Started ");
import warnings
warnings.simplefilter("ignore", category=FutureWarning)

# Initialize new session (must be first import)
import utils.session_init
from utils.session_activity_logger import (
    log_api_request,
    log_system_command,
    log_user_interaction,
    session_activity_logger
)

from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, 
    get_jwt_identity, verify_jwt_in_request
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import sys
import time
import threading
import json
from datetime import datetime, timedelta
from pathlib import Path
import re
import secrets
import logging

# Import secure secrets manager
try:
    from ai_assistant.core.secrets_manager import get_secrets_manager, SecretsValidationError
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False
# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    sys.stderr.reconfigure(encoding='utf-8') if hasattr(sys.stderr, 'reconfigure') else None

# Load environment variables
load_dotenv()

# Setup centralized logging
from utils.logging_config import get_logger, get_api_logger
from utils.user_data_logger import log_query, log_reply, log_action, log_module_usage
logger = get_logger('web_backend', log_category='backend')
api_logger = get_api_logger('api_requests')

logger.info("="*80)
logger.info("YourDaddy Assistant - Web Backend Starting")
logger.info("="*80)

# Add ai_assistant directory to sys.path to allow importing automation_tools_new and modules
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_assistant_dir = os.path.dirname(current_dir)
if ai_assistant_dir not in sys.path:
    sys.path.append(ai_assistant_dir)

# Import Multi-Agent System
try:
    from ai_assistant.core.chain_of_actions_manager import get_chain_manager, ChainOfActionsManager
    from ai_assistant.core.progress_tracker import get_progress_tracker
    MULTI_AGENT_AVAILABLE = True
except ImportError as e:
    MULTI_AGENT_AVAILABLE = False
    logger.warning(f"Multi-Agent System not available: {e}")

# Import automation tools
try:
    # Try importing from ai_assistant package first
    from ai_assistant.automation_tools_new import (
        write_a_note, open_application, search_google, search_youtube,
        close_application, speak, set_system_volume, get_app_path_from_name,
        setup_memory, save_to_memory, get_memory, search_memory,
        get_conversation_summary, save_knowledge, get_knowledge,
        discover_applications, smart_open_application, list_installed_apps,
        refresh_app_database, search_apps_by_name, get_app_usage_stats, get_apps_for_web,
        get_system_status, get_running_processes, cleanup_temp_files,
        get_network_info, get_upcoming_events, get_inbox_summary,
        get_spotify_status, spotify_play_pause, spotify_next_track,
        spotify_previous_track, search_and_play_spotify,
        get_weather_info, get_latest_news, get_stock_price,
        detect_taskbar_apps, can_see_taskbar
    )
    # Import app discovery scheduler functions
    from ai_assistant.modules.app_discovery import (
        start_auto_refresh_after_startup, start_periodic_refresh
    )
    AUTOMATION_AVAILABLE = True
    print("✅ Automation tools loaded successfully")
except ImportError as e:
    print(f"⚠️ Automation tools import failed: {e}")
    # Try fallback import from modules directly
    try:
        from ai_assistant.modules.app_discovery import (
            get_apps_for_web, refresh_app_database, 
            start_auto_refresh_after_startup, start_periodic_refresh
        )
        AUTOMATION_AVAILABLE = True
        print("✅ App discovery loaded from modules")
    except ImportError as e2:
        print(f"❌ App discovery also failed: {e2}")
        AUTOMATION_AVAILABLE = False

# Import Learning Router for automatic AI training
try:
    from auto_learning_router import LearningDataRouter
    learning_router = LearningDataRouter()
    LEARNING_ROUTER_AVAILABLE = True
    print("✅ Learning router initialized - AI will learn from all interactions")
except (ImportError, Exception) as e:
    print(f"⚠️ Learning router not available: {e}")
    learning_router = None
    LEARNING_ROUTER_AVAILABLE = False

# Import Smart Memory Retrieval for answering from past conversations
try:
    from smart_memory_retrieval import SmartMemoryRetrieval, enhance_response_with_memory
    memory_retriever = SmartMemoryRetrieval()
    SMART_MEMORY_AVAILABLE = True
    print("✅ Smart memory retrieval initialized - AI can answer from past conversations")
except ImportError as e:
    print(f"⚠️ Smart memory retrieval not available: {e}")
    memory_retriever = None
    SMART_MEMORY_AVAILABLE = False

# Import multimodal AI if available
try:
    from ai_assistant.multimodal import MultiModalAI
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False

# Import conversational AI if available
try:
    from ai_assistant.modules.conversational_ai import AdvancedConversationalAI
    CONVERSATIONAL_AI_AVAILABLE = True
except ImportError:
    CONVERSATIONAL_AI_AVAILABLE = False

# Import multilingual support if available
try:
    from ai_assistant.multilingual import MultilingualSupport, Language, LanguageContext
    MULTILINGUAL_AVAILABLE = True
    print("Multilingual support loaded in web backend")
except ImportError as e:
    MULTILINGUAL_AVAILABLE = False
    print("Multilingual support not available in web backend - dependency issue with googletrans/httpx")
except Exception as e:
    MULTILINGUAL_AVAILABLE = False
    print(f"Multilingual support not available in web backend: {e}")

# Import advanced chat system and LLM providers
try:
    from ai_assistant.modules.advanced_chat_system import AdvancedChatSystem
    ADVANCED_CHAT_AVAILABLE = True
    print("Advanced chat system loaded")
except ImportError as e:
    ADVANCED_CHAT_AVAILABLE = False
    print(f"Advanced chat system not available: {e}")

try:
    from ai_assistant.modules.llm_provider import UnifiedChatInterface, LLMFactory
    LLM_PROVIDER_AVAILABLE = True
    print("LLM providers loaded")
except ImportError as e:
    LLM_PROVIDER_AVAILABLE = False
    print(f"LLM providers not available: {e}")

# Import NEW ADVANCED FEATURES (lazy initialization)
try:
    from ai_assistant.core.enhanced_integration import get_enhanced_ai
    enhanced_ai = None  # Lazy load on first use
    ENHANCED_AI_AVAILABLE = True
    print("⚡ Enhanced AI available (will load on first use)")
except ImportError as e:
    ENHANCED_AI_AVAILABLE = False
    enhanced_ai = None
    print(f"⚠️ Enhanced AI not available: {e}")

def _get_enhanced_ai_lazy():
    """Lazy load enhanced AI on first use"""
    global enhanced_ai
    if enhanced_ai is None and ENHANCED_AI_AVAILABLE:
        enhanced_ai = get_enhanced_ai()
        logger.info("✅ Enhanced AI initialized (semantic cache, routing, streaming, emotion, verification)")
    return enhanced_ai

try:
    from ai_assistant.ai.usage_pattern_analyzer import UsagePatternAnalyzer
    usage_analyzer = None  # Lazy load on first use
    USAGE_ANALYZER_AVAILABLE = True
    print("⚡ Usage pattern analyzer available (will load on first use)")
except ImportError as e:
    USAGE_ANALYZER_AVAILABLE = False
    usage_analyzer = None
    print(f"⚠️ Usage analyzer not available: {e}")

def _get_usage_analyzer_lazy():
    """Lazy load usage analyzer on first use"""
    global usage_analyzer
    if usage_analyzer is None and USAGE_ANALYZER_AVAILABLE:
        usage_analyzer = UsagePatternAnalyzer()
        logger.info("✅ Usage pattern analyzer initialized")
    return usage_analyzer

# System monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Voice processing
try:
    import vosk
    import pvporcupine
    import pyaudio
    import speech_recognition as sr
    import pyttsx3
    import numpy as np
    import wave
    import base64
    import io
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# Import local AI manager
try:
    from ai_assistant.local_ai_manager import LocalAIManager
    LOCAL_AI_AVAILABLE = True
except ImportError:
    LOCAL_AI_AVAILABLE = False
    logger.warning("⚠️ Local AI not available. Install: pip install llama-cpp-python")

# Load environment variables
load_dotenv()

# Create Flask app
# Point to new web assets location
web_assets_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'web_assets'))
template_dir = os.path.join(web_assets_dir, 'templates')
static_dir = os.path.join(web_assets_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Security Configuration - Use secrets manager for secure key handling
if SECRETS_MANAGER_AVAILABLE:
    try:
        secrets_mgr = get_secrets_manager()
        app.config['SECRET_KEY'] = secrets_mgr.get_or_generate('SECRET_KEY', 32)
        app.config['JWT_SECRET_KEY'] = secrets_mgr.get_or_generate('JWT_SECRET_KEY', 32)
    except Exception as e:
        logger.warning(f"Secrets manager error: {e}. Using generated keys.")
        app.config['SECRET_KEY'] = secrets.token_hex(32)
        app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
else:
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') or secrets.token_hex(32)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize JWT
jwt = JWTManager(app)

# Initialize Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://"
)

# Secure CORS Configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5000,http://127.0.0.1:3000,http://127.0.0.1:5000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:15000,http://127.0.0.1:15000').split(',')
CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
    },
    r"/socket.io/*": {
        "origins": ALLOWED_ORIGINS,
        "supports_credentials": True
    }
})

# Initialize SocketIO for WebSocket support
socketio = SocketIO(
    app,
    cors_allowed_origins=ALLOWED_ORIGINS,
    async_mode='threading',
    logger=False,  # Disable verbose logging
    engineio_logger=False,  # Disable engine.io logging
    ping_timeout=60,
    ping_interval=25
)

# Configure logging levels for production - silence socketio spam
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('socketio.server').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('engineio.server').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

logger.info("✅ SocketIO initialized with CORS origins: %s", ALLOWED_ORIGINS)

# Voice Options for TTS
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

# Import voice API blueprint
try:
    from ai_assistant.services.voice_api import voice_bp, AVAILABLE_VOICES as VOICE_API_VOICES
    VOICE_API_AVAILABLE = True
    # Update AVAILABLE_VOICES if not already defined
    if 'AVAILABLE_VOICES' not in globals() or not AVAILABLE_VOICES:
        AVAILABLE_VOICES = VOICE_API_VOICES
except ImportError as e:
    logger.warning(f"Voice API blueprint not available: {e}")
    VOICE_API_AVAILABLE = False

# Import advanced voice processing modules
try:
    from ai_assistant.voice.voice_activity_detection import VoiceActivityDetector, VADConfig
    VAD_AVAILABLE = True
    logger.info("✅ Voice Activity Detection module loaded")
except ImportError as e:
    VAD_AVAILABLE = False
    logger.warning(f"⚠️ VAD module not available: {e}")

try:
    from ai_assistant.voice.noise_reduction import NoiseReductionSystem, NoiseReductionConfig
    NOISE_REDUCTION_AVAILABLE = True
    logger.info("✅ Noise Reduction module loaded")
except ImportError as e:
    NOISE_REDUCTION_AVAILABLE = False
    logger.warning(f"⚠️ Noise Reduction module not available: {e}")

try:
    from ai_assistant.voice.async_recognizer import (
        init_async_recognizer, recognize_async, get_recognition_stats
    )
    ASYNC_RECOGNIZER_AVAILABLE = True
    logger.info("✅ Async Voice Recognizer module loaded")
except ImportError as e:
    ASYNC_RECOGNIZER_AVAILABLE = False
    logger.warning(f"⚠️ Async Recognizer module not available: {e}")

# Import voice WebSocket handlers
try:
    from ai_assistant.services.voice_websocket_handlers import register_voice_handlers
    VOICE_WEBSOCKET_AVAILABLE = True
    logger.info("✅ Voice WebSocket handlers module loaded")
except ImportError as e:
    VOICE_WEBSOCKET_AVAILABLE = False
    logger.warning(f"⚠️ Voice WebSocket handlers not available: {e}")

# Import Vosk WebSocket handlers for offline recognition
try:
    from ai_assistant.services.vosk_websocket_handler import register_vosk_handlers, VOSK_AVAILABLE as VOSK_WS_AVAILABLE
    if VOSK_WS_AVAILABLE:
        logger.info("✅ Vosk WebSocket handler loaded (offline recognition ready)")
    else:
        logger.warning("⚠️ Vosk library not installed")
except ImportError as e:
    VOSK_WS_AVAILABLE = False
    logger.warning(f"⚠️ Vosk WebSocket handler not available: {e}")

# Import Google Speech Recognition WebSocket handlers
try:
    from ai_assistant.services.google_speech_websocket_handler import register_google_speech_handlers
    GOOGLE_SPEECH_WS_AVAILABLE = True
    logger.info("✅ Google Speech Recognition WebSocket handler loaded (online recognition ready)")
except ImportError as e:
    GOOGLE_SPEECH_WS_AVAILABLE = False
    logger.warning(f"⚠️ Google Speech WebSocket handler not available: {e}")


# =============================================================================
# STARTUP OPTIMIZATION - Feature Toggle Configuration
# =============================================================================
# These environment variables control which features are enabled at startup
# to optimize loading time. Set to 'false' to disable optional features.

ENABLE_VOICE = os.getenv('ENABLE_VOICE', 'true').lower() == 'true'
ENABLE_MULTIMODAL = os.getenv('ENABLE_MULTIMODAL', 'true').lower() == 'true'
ENABLE_CONVERSATIONAL_AI = os.getenv('ENABLE_CONVERSATIONAL_AI', 'true').lower() == 'true'
ENABLE_SYSTEM_MONITORING = os.getenv('ENABLE_SYSTEM_MONITORING', 'true').lower() == 'true'
LAZY_INIT = os.getenv('LAZY_INIT', 'true').lower() == 'true'  # Lazy load components on first use
BACKGROUND_INIT = os.getenv('BACKGROUND_INIT', 'true').lower() == 'true'  # Initialize in background

logger.info("🔧 Startup Configuration:")
logger.info(f"  - Lazy Initialization: {LAZY_INIT}")
logger.info(f"  - Background Initialization: {BACKGROUND_INIT}")
logger.info(f"  - Voice Features: {ENABLE_VOICE}")
logger.info(f"  - Multimodal AI: {ENABLE_MULTIMODAL}")
logger.info(f"  - Conversational AI: {ENABLE_CONVERSATIONAL_AI}")
logger.info(f"  - System Monitoring: {ENABLE_SYSTEM_MONITORING}")

# =============================================================================
# GLOBAL: Local AI Manager
# =============================================================================

local_ai_manager = None
local_ai_initialized = False

def initialize_local_ai():
    """Initialize local AI model in background"""
    global local_ai_manager, local_ai_initialized
    
    if not LOCAL_AI_AVAILABLE:
        logger.warning("Local AI not available")
        return
    
    try:
        logger.info("Initializing Local AI Manager (Ollama)...")
        local_ai_manager = LocalAIManager()
        
        # Check if Ollama is running
        if not local_ai_manager.is_ollama_running():
            logger.warning("Ollama service is not running. Start it with 'ollama serve'")
            return
        
        # Check for available models using auto-detection
        model_name = local_ai_manager.find_best_available_model()
        
        if model_name:
            logger.info(f"Loading Ollama model: {model_name}")
            if local_ai_manager.load_model(model_name):
                local_ai_initialized = True
                logger.info("Local AI ready!")
            else:
                logger.error(f"Failed to load model: {model_name}")
        else:
            logger.warning("No Ollama models found. Download with:")
            logger.warning("  ollama pull llama3.2")
    
    except Exception as e:
        logger.error(f"Local AI initialization failed: {e}")

# Initialize local AI in background thread
if BACKGROUND_INIT and LOCAL_AI_AVAILABLE:
    threading.Thread(target=initialize_local_ai, daemon=True).start()

# =============================================================================

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


@app.route('/api/user/preferences', methods=['GET'])
@limiter.limit("20 per minute")
def get_user_preferences():
    """Get user preferences"""
    try:
        from ai_assistant.services.user_preferences import get_preferences_manager
        
        # Get user from auth token or use 'default'
        user_id = request.args.get('user_id', 'default')
        
        prefs_manager = get_preferences_manager()
        preferences = prefs_manager.get_preferences(user_id)
        
        return jsonify({
            "success": True,
            "preferences": preferences
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/user/profile/status', methods=['GET'])
def get_user_profile_status():
    """Check if the user profile is set up."""
    try:
        from ai_assistant.database_config import get_db_path
        import sqlite3
        import json
        
        db_path = get_db_path('personal_knowledge')
        if not db_path.exists():
            return jsonify({"setup_complete": False, "exists": False})
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_nodes'")
            if not cursor.fetchone():
                return jsonify({"setup_complete": False, "exists": True, "reason": "no_tables"})
                
            cursor.execute("SELECT content, metadata FROM knowledge_nodes WHERE node_type='person'")
            rows = cursor.fetchall()
            
            for content, meta_json in rows:
                meta = json.loads(meta_json) if meta_json else {}
                if meta.get('is_primary_user'):
                    return jsonify({
                        "setup_complete": True, 
                        "name": content,
                        "role": meta.get('role'),
                        "has_deep_profile": meta.get('full_profile_complete', False)
                    })
                    
            # Fallback
            if rows:
                return jsonify({"setup_complete": True, "name": rows[0][0], "message": "basic_profile_only"})
                
        except Exception as e:
            logger.error(f"DB Error checking profile: {e}")
            return jsonify({"setup_complete": False, "error": str(e)})
        finally:
            conn.close()
            
        return jsonify({"setup_complete": False})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/user/profile/setup', methods=['POST'])
def setup_user_profile():
    """Setup or update the user profile."""
    try:
        from ai_assistant.ai.enhanced_learning import PersonalKnowledgeGraph
        from ai_assistant.database_config import get_db_path
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        name = data.get('name')
        if not name:
             return jsonify({"success": False, "error": "Name is required"}), 400
             
        # Extract fields
        role = data.get('role', 'User')
        location = data.get('location')
        style = data.get('communication_style', 'Concise')
        interests = data.get('interests', [])
        skills = data.get('skills', [])
        goals = data.get('goals', [])
        work_pattern = data.get('work_pattern')
        
        # Init DB
        db_path = get_db_path('personal_knowledge')
        
        # Ensure tables exist
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS knowledge_nodes (node_id TEXT PRIMARY KEY, content TEXT NOT NULL, node_type TEXT NOT NULL, metadata TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP, importance_score REAL DEFAULT 0.5)")
        cursor.execute("CREATE TABLE IF NOT EXISTS knowledge_edges (edge_id TEXT PRIMARY KEY, source_node TEXT NOT NULL, target_node TEXT NOT NULL, relationship_type TEXT NOT NULL, strength REAL DEFAULT 1.0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (source_node) REFERENCES knowledge_nodes (node_id), FOREIGN KEY (target_node) REFERENCES knowledge_nodes (node_id))")
        conn.commit()
        conn.close()
        
        try:
            kg = PersonalKnowledgeGraph(str(db_path))
        except:
             # Fallback if init fails (shouldn't happen if tables exist)
             pass

        # Use direct KG methods if available, else manual DB insert
        # Re-import to be safe
        from ai_assistant.ai.enhanced_learning import PersonalKnowledgeGraph
        kg = PersonalKnowledgeGraph(str(db_path))
        
        # Add User Node
        user_metadata = {
            "role": role,
            "is_primary_user": True,
            "interests": interests,
            "location": location,
            "communication_style": style,
            "skills": skills,
            "goals": goals,
            "work_pattern": work_pattern,
            "full_profile_complete": True
        }
        
        user_node_id = kg.add_knowledge_node(name, "person", user_metadata)
        
        # Add basic relations
        role_node_id = kg.add_knowledge_node(role, "role", {})
        kg.add_relationship(user_node_id, role_node_id, "has_role", strength=1.0)
        
        for interest in interests:
            if interest:
                i_node = kg.add_knowledge_node(interest, "topic", {})
                kg.add_relationship(user_node_id, i_node, "interested_in", strength=0.8)
                
        for skill in skills:
            if skill:
                s_node = kg.add_knowledge_node(skill, "skill", {})
                kg.add_relationship(user_node_id, s_node, "has_skill", strength=0.9)
                
        logger.info(f"✅ Created/Updated profile for {name}")
        
        return jsonify({"success": True, "message": "Profile setup complete"})
        
    except Exception as e:
        logger.error(f"Profile setup failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/user/preferences', methods=['POST'])
@limiter.limit("10 per minute")
def save_user_preferences():
    """Save user preferences"""
    try:
        from ai_assistant.services.user_preferences import get_preferences_manager
        
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        preferences = data.get('preferences', {})
        
        prefs_manager = get_preferences_manager()
        success = prefs_manager.save_preferences(user_id, preferences)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Preferences saved successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save preferences"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Initialization Status Endpoint
@app.route('/api/status/initialization', methods=['GET'])
@limiter.limit("30 per minute")
def get_initialization_status():
    """Get initialization status of all components"""
    try:
        if hasattr(assistant, 'get_init_status'):
            status = assistant.get_init_status()
            
            # Calculate overall readiness
            ready_count = sum(1 for v in status.values() if v == 'ready')
            total_count = len(status)
            overall_ready = (ready_count == total_count)
            
            return jsonify({
                "success": True,
                "overall_ready": overall_ready,
                "ready_percentage": int((ready_count / total_count) * 100),
                "components": status,
                "config": {
                    "lazy_init": LAZY_INIT,
                    "background_init": BACKGROUND_INIT,
                    "voice_enabled": ENABLE_VOICE,
                    "multimodal_enabled": ENABLE_MULTIMODAL,
                    "conversational_ai_enabled": ENABLE_CONVERSATIONAL_AI,
                    "system_monitoring_enabled": ENABLE_SYSTEM_MONITORING
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "Assistant does not support init status tracking"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Initialize SocketIO with secure origins
socketio = SocketIO(
    app, 
    cors_allowed_origins=ALLOWED_ORIGINS,
    async_mode='threading',
    engineio_logger=False,
    logger=False,
    ping_timeout=60,
    ping_interval=25
)

# ============================================================
# PROFESSIONAL VOICE SYSTEM INITIALIZATION
# ============================================================
try:
    from ai_assistant.services.voice_api import voice_bp, init_professional_voice_services
    
    # Register voice API blueprint
    app.register_blueprint(voice_bp, url_prefix='/api/voice')
    logger.info("✅ Voice API blueprint registered at /api/voice")
    
    # Initialize professional voice services with WebSocket support
    voice_initialized = init_professional_voice_services(socketio)
    
    if voice_initialized:
        logger.info("=" * 60)
        logger.info("🎤 PROFESSIONAL VOICE SYSTEM ACTIVATED")
        logger.info("=" * 60)
        logger.info("✅ SmartWakeWordDetector - PocketSphinx (Offline)")
        logger.info("✅ NeuralVoiceEngine - Edge-TTS + Coqui")
        logger.info("✅ VoiceActivityDetector - WebRTC VAD")
        logger.info("✅ Speaker Recognition - Enabled")
        logger.info("✅ Advanced STT - Whisper + Google + Vosk")
        logger.info("✅ Noise Reduction - Active")
        logger.info("=" * 60)
    else:
        logger.warning("⚠️  Voice system running in limited mode")
        
except ImportError as e:
    logger.warning(f"⚠️  Professional voice system not available: {e}")
    logger.info("💡 Basic voice features still available via assistant")
except Exception as e:
    logger.error(f"❌ Voice system initialization failed: {e}")
    logger.info("💡 Server will continue without professional voice features")


# User Management (Simple in-memory store - replace with database in production)
# WARNING: Admin password MUST be set via environment variable for security
_admin_password = os.getenv('ADMIN_PASSWORD')
if not _admin_password:
    logger.warning(
        "⚠️  ADMIN_PASSWORD not set! Using temporary generated password. "
        "Set ADMIN_PASSWORD in your environment for production use."
    )
    _admin_password = secrets.token_urlsafe(16)
    logger.info(f"Temporary admin password: {_admin_password}")

USERS_DB = {
    "admin": {
        "password_hash": generate_password_hash(_admin_password),
        "role": "admin"
    }
}

# Clear the password from memory
del _admin_password

# Input Validation Patterns
VALIDATION_PATTERNS = {
    'command': re.compile(r'^[\w\s\-.,!?@#$%()+=:;"\']+$'),
    'app_name': re.compile(r'^[\w\s\-.]+$'),
    'username': re.compile(r'^[a-zA-Z0-9_]{3,20}$'),
}

def validate_input(data, field, pattern_name):
    """Validate input data against pattern"""
    if not data or field not in data:
        return False, f"{field} is required"
    
    value = data[field]
    if not isinstance(value, str):
        return False, f"{field} must be a string"
    
    if len(value) > 1000:
        return False, f"{field} is too long (max 1000 characters)"
    
    pattern = VALIDATION_PATTERNS.get(pattern_name)
    if pattern and not pattern.match(value):
        return False, f"{field} contains invalid characters"
    
    return True, None

def sanitize_command(command):
    """Sanitize command input to prevent injection"""
    # Remove potentially dangerous characters
    dangerous_chars = ['|', '&', ';', '`', '$', '(', ')', '<', '>', '\n', '\r']
    for char in dangerous_chars:
        command = command.replace(char, '')
    return command.strip()[:500]  # Limit length

# =============================================================================
# IMPORT MODERN ASSISTANT CLASS (Extracted for Modularity)
# =============================================================================
# ModernAssistant has been extracted to ai_assistant/core/assistant.py
# This reduces this file from 4946 lines to ~3700 lines while maintaining
# all functionality. The class can now be reused by other modules.

from ai_assistant.core.assistant import ModernAssistant, set_socketio

# Inject SocketIO instance into the assistant module for system monitoring
set_socketio(socketio)


# Global assistant instance - protected initialization
try:
    print("ðŸ”§ Initializing YourDaddy Assistant...")
    assistant = ModernAssistant()
    print("âœ… Assistant initialized successfully")
except Exception as e:
    print(f"âŒ CRITICAL: Assistant initialization failed: {e}")
    print("âš ï¸  Server will start in limited mode without some features")
    # Create a minimal assistant instance
    class MinimalAssistant:
        def __init__(self):
            self.multimodal_ai = None
            self.conversational_ai = None
            self.multilingual = None
            self.voice_listening = False
        
        def process_command(self, command):
            return f"I understand you said: '{command}'. However, some features are currently unavailable due to initialization errors. Please check the server logs."
        
        def get_real_time_system_stats(self):
            return {"timestamp": datetime.now().isoformat(), "cpu_usage": 0, "memory_usage": 0, "disk_usage": 0, "network_mbps": 0, "active_tasks": 0, "temperature": "N/A"}
        
        def get_init_status(self):
            return {
                'multimodal_ai': 'failed',
                'conversational_ai': 'failed',
                'multilingual': 'failed',
                'llm_chat': 'failed',
                'voice_system': 'failed',
                'memory': 'failed',
                'system_monitoring': 'failed'
            }
        
        def analyze_screen(self, prompt): return "Screen analysis unavailable"
        def answer_visual_question(self, question): return "Visual Q&A unavailable"
        def start_voice_listening(self): return {"error": "Voice features unavailable"}
        def stop_voice_listening(self): return {"error": "Voice features unavailable"}
        def speak_text(self, text): return False
        def process_voice_audio(self, audio_data): return {"error": "Audio processing unavailable"}
    
    assistant = MinimalAssistant()

# =============================================================================
# REGISTER BLUEPRINTS - Modular Route Organization
# =============================================================================
print("📋 Registering blueprints...")
try:
    from ai_assistant.services.backend.blueprints import register_all_blueprints
    register_all_blueprints(app, assistant)
    print("✅ All blueprints registered")
except Exception as e:
    print(f"⚠️ Blueprint registration failed: {e}")
    import traceback
    traceback.print_exc()

@app.route('/')
def index():
    """Serve Bolt.ai React app build"""
    try:
        print("Serving Bolt.ai React app from project/dist")
        return send_from_directory('project/dist', 'index.html')
    except Exception as e:
        print(f"React app serving error: {e}")
        return f"<h1>React App Error</h1><p>Error: {e}</p><p>Please ensure the React app is built in project/dist/</p>"

# ============================================================
# LEGACY ROUTES (keep for old template compatibility)
# ============================================================


@app.route('/<path:path>')
def serve_static_or_react(path):
    """Serve static files or fallback to React app"""
    # CRITICAL: Skip API routes - let them be handled by their specific handlers
    if path.startswith('api/'):
        # This will be handled by Flask's routing system
        # Return 404 only if no API route matches (Flask will handle this)
        from flask import abort
        abort(404)
    
    # Handle old static files for backward compatibility
    if path.startswith('static/'):
        try:
            return send_from_directory('static', path[7:])
        except:
            pass
    
    # Handle common files
    elif path in ['favicon.ico', 'robots.txt', 'vite.svg']:
        try:
            return send_from_directory('project/dist', path)
        except:
            try:
                return send_from_directory('static', path)
            except:
                return "File not found", 404
    
    # For any other path, serve React app (SPA routing)
    try:
        return send_from_directory('project/dist', 'index.html')
    except Exception as e:
        print(f"React app fallback error: {e}")
        return f"<h1>App Error</h1><p>Could not serve React app: {e}</p>", 404

@app.route('/enhanced-chat')
def enhanced_chat():
    """Serve enhanced chat interface"""
    from flask import render_template
    try:
        print("Attempting to render enhanced_chat.html")
        return render_template('enhanced_chat.html')
    except Exception as e:
        print(f"Enhanced chat template error: {e}")
        return f"<h1>Enhanced Chat Template Error</h1><p>Error: {e}</p><p><a href='/'>Go back to main page</a></p>"

@app.route('/download')
def download_page():
    """Serve Windows app download page"""
    from flask import render_template
    try:
        return render_template('download.html')
    except Exception as e:
        logger.error(f"Download page error: {e}")
        return f"<h1>Download Page Error</h1><p>Error: {e}</p>"

@app.route('/download/windows-app')
def download_windows_app():
    """Download the Windows desktop app"""
    from flask import send_file
    import os
    
    zip_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            'dist', 'AI-Assistant-Windows.zip')
    
    if os.path.exists(zip_path):
        logger.info(f"Serving Windows app from: {zip_path}")
        return send_file(
            zip_path,
            as_attachment=True,
            download_name='AI-Assistant-Windows.zip',
            mimetype='application/zip'
        )
    else:
        logger.error(f"Windows app not found at: {zip_path}")
        return f"""
        <h1>Download Not Available</h1>
        <p>The Windows app package has not been built yet.</p>
        <p>Please run <code>build_for_website.bat</code> first to create the distributable package.</p>
        <p><a href='/download'>Go back</a></p>
        """, 404

@app.route('/test')
def test_page():
    """Simple test page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YourDaddy Assistant - Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .test-btn { display: block; margin: 10px 0; padding: 15px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; text-align: center; }
            .test-btn:hover { background: #0056b3; }
            .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ðŸ¤– YourDaddy Assistant - Test Page</h1>
            <div class="status success">âœ… Backend is operational and all features are enabled!</div>
            
            <h2>Test Enhanced Chat Features:</h2>
            <a href="/enhanced-chat" class="test-btn">ðŸ’¬ Open Enhanced Chat Interface</a>
            <a href="/api/features" class="test-btn">ðŸ”§ Check Available Features</a>
            <a href="/api/apps" class="test-btn">ðŸ“± List Installed Applications</a>
            <a href="/api/weather" class="test-btn">ðŸŒ¤ï¸ Get Weather Information</a>
            
            <h2>Quick API Tests:</h2>
            <div style="font-family: monospace; background: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 12px;">
                <strong>Test Enhanced Chat:</strong><br>
                POST /api/chat<br>
                {"message": "Hello! What can you do?"}<br><br>
                
                <strong>Test Features:</strong><br>
                GET /api/features<br><br>
                
                <strong>Test Apps:</strong><br>
                GET /api/apps<br><br>
                
                <strong>Test Screen Analysis:</strong><br>
                POST /api/screen/analyze<br>
                {"prompt": "What's on the screen?"}
            </div>
        </div>
    </body>
    </html>
    """

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("3 per hour")  # Prevent abuse
def api_register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_input(data, 'username', 'username')
        if not is_valid:
            return jsonify({"error": error}), 400
        
        if 'password' not in data:
            return jsonify({"error": "Password is required"}), 400
        
        username = data['username']
        password = data['password']
        
        # Check password strength
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Check if user already exists
        if username in USERS_DB:
            return jsonify({"error": "Username already exists"}), 409
        
        # Create new user
        USERS_DB[username] = {
            "password_hash": generate_password_hash(password),
            "role": "user"
        }
        
        # Create tokens
        access_token = create_access_token(
            identity=username,
            additional_claims={"role": "user"}
        )
        
        return jsonify({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 86400,
            "user": {
                "username": username,
                "role": "user"
            },
            "message": "Registration successful"
        }), 201
        
    except Exception as e:
        return jsonify({"error": "Registration failed"}), 500


@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Prevent brute force
def api_login():
    """Authenticate user with PIN and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate PIN input
        if 'pin' not in data:
            return jsonify({"error": "PIN is required"}), 400
        
        pin = str(data['pin']).strip()
        
        # Validate PIN format
        if not pin:
            return jsonify({"error": "PIN cannot be empty"}), 400
            
        if len(pin) < 4:
            return jsonify({"error": "PIN must be at least 4 digits"}), 400
            
        if not pin.isdigit():
            return jsonify({"error": "PIN must contain only numbers"}), 400
        
        # Check PIN against environment variable or default
        valid_pin = os.getenv('ADMIN_PIN', '1234')
        
        if pin != valid_pin:
            return jsonify({"error": "Invalid PIN"}), 401
        
        # Create JWT token for authenticated user
        access_token = create_access_token(
            identity="assistant_user",
            additional_claims={"role": "user"}
        )
        
        return jsonify({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 86400,  # 24 hours
            "user": {
                "username": "assistant_user",
                "role": "user"
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def api_verify_token():
    """Verify JWT token is valid"""
    current_user = get_jwt_identity()
    user = USERS_DB.get(current_user)
    
    return jsonify({
        "valid": True,
        "user": {
            "username": current_user,
            "role": user['role'] if user else "user"
        }
    }), 200

# API Routes
@app.route('/api/status')
def api_status():
    """API status endpoint - Public"""
    authenticated = False
    try:
        verify_jwt_in_request(optional=True)
        authenticated = bool(get_jwt_identity())
    except:
        pass
    
    # Check learning systems availability
    learning_systems_available = False
    try:
        from ai_assistant.services.learning_integration import LEARNING_SYSTEMS_AVAILABLE
        learning_systems_available = LEARNING_SYSTEMS_AVAILABLE
    except:
        pass
    
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "authenticated": authenticated,
        "services": {
            "automation": AUTOMATION_AVAILABLE,
            "multimodal": MULTIMODAL_AVAILABLE,
            "conversational_ai": CONVERSATIONAL_AI_AVAILABLE,
            "voice": VOICE_AVAILABLE,
            "system_monitoring": PSUTIL_AVAILABLE,
            "learning_systems": learning_systems_available,
            # NEW ADVANCED FEATURES
            "enhanced_ai": ENHANCED_AI_AVAILABLE,
            "usage_analyzer": USAGE_ANALYZER_AVAILABLE,
            "semantic_cache": ENHANCED_AI_AVAILABLE and enhanced_ai and enhanced_ai.cache is not None,
            "model_router": ENHANCED_AI_AVAILABLE and enhanced_ai and enhanced_ai.router is not None,
            "streaming": ENHANCED_AI_AVAILABLE and enhanced_ai and enhanced_ai.streaming is not None,
            "emotion_detection": ENHANCED_AI_AVAILABLE and enhanced_ai and enhanced_ai.emotion_detector is not None,
            "visual_verification": ENHANCED_AI_AVAILABLE and enhanced_ai and enhanced_ai.verifier is not None
        }
    })

@app.route('/api/learning/stats')
@jwt_required(optional=True)
def api_learning_stats():
    """Get stats from all learning systems"""
    try:
        from ai_assistant.services.learning_integration import get_learning_stats, LEARNING_SYSTEMS_AVAILABLE
        
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        stats = get_learning_stats()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Learning stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def learning_dashboard():
    """Serve the learning systems dashboard"""
    static_dir = Path(__file__).parent.parent.parent / "static"
    return send_from_directory(static_dir, 'learning_dashboard.html')

# ==================== LEARNING SYSTEMS ENDPOINTS ====================
# Comprehensive API for all 27 learning systems

# Import Learning Dashboard API
try:
    from learning_dashboard_api import LearningDashboardAPI
    dashboard_api = LearningDashboardAPI()
    DASHBOARD_API_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Dashboard API not available: {e}")
    dashboard_api = None
    DASHBOARD_API_AVAILABLE = False

@app.route('/api/learning/dashboard')
@jwt_required(optional=True)
def api_learning_dashboard():
    """Get complete learning dashboard data"""
    try:
        if not DASHBOARD_API_AVAILABLE or not dashboard_api:
            return jsonify({"error": "Dashboard API not available"}), 503
        
        data = dashboard_api.get_dashboard_data()
        return jsonify({
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Dashboard API error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/databases')
@jwt_required(optional=True)
def api_learning_databases():
    """Get list of all learning databases with stats"""
    try:
        if not DASHBOARD_API_AVAILABLE or not dashboard_api:
            return jsonify({"error": "Dashboard API not available"}), 503
        
        databases = dashboard_api.get_database_stats()
        return jsonify({
            "success": True,
            "databases": databases,
            "total": len(databases)
        })
    except Exception as e:
        logger.error(f"Databases API error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/database/<db_name>/<table_name>')
@jwt_required(optional=True)
def api_database_content(db_name, table_name):
    """Get content from a specific database table"""
    try:
        if not DASHBOARD_API_AVAILABLE or not dashboard_api:
            return jsonify({"error": "Dashboard API not available"}), 503
        
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        content = dashboard_api.get_database_content(db_name, table_name, limit, offset)
        return jsonify({
            "success": True,
            "database": db_name,
            "table": table_name,
            "content": content
        })
    except Exception as e:
        logger.error(f"Database content error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/memory/search')
@jwt_required(optional=True)
def api_memory_search():
    """Search memory database"""
    try:
        if not DASHBOARD_API_AVAILABLE or not dashboard_api:
            return jsonify({"error": "Dashboard API not available"}), 503
        
        query = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({"error": "Query parameter 'q' required"}), 400
        
        results = dashboard_api.search_memory(query, limit)
        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        logger.error(f"Memory search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/documentation')
@jwt_required(optional=True)
def api_learning_documentation():
    """Serve HOW_AI_LEARNS.md documentation"""
    try:
        doc_path = Path(__file__).parent.parent.parent / 'HOW_AI_LEARNS.md'
        
        if not doc_path.exists():
            return jsonify({"error": "Documentation not found"}), 404
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "success": True,
            "content": content,
            "format": "markdown"
        })
    except Exception as e:
        logger.error(f"Documentation API error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs/recent')
@jwt_required(optional=True)
def api_logs_recent():
    """Get recent log entries"""
    try:
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        
        # Get most recent log file
        log_files = list(log_dir.glob('**/*.log'))
        if not log_files:
            return jsonify({"error": "No log files found"}), 404
        
        # Sort by modification time
        latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
        
        # Read last N lines
        limit = request.args.get('limit', 100, type=int)
        
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            recent_lines = lines[-limit:]
        
        return jsonify({
            "success": True,
            "log_file": latest_log.name,
            "lines": recent_lines,
            "total_lines": len(lines)
        })
    except Exception as e:
        logger.error(f"Logs API error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/stats/all')
@jwt_required(optional=True)
def api_all_learning_stats():
    """Get stats from all 27 learning systems"""
    try:
        from ai_assistant.services.learning_integration import get_learning_stats, LEARNING_SYSTEMS_AVAILABLE
        
        if not LEARNING_SYSTEMS_AVAILABLE:
            logger.warning("Learning systems not available")
            return jsonify({
                "success": False,
                "error": "Learning systems not available",
                "systems": {},
                "total_systems": 0
            }), 200  # Return 200 with error flag instead of 503
        
        stats = get_learning_stats()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "systems": stats,
            "total_systems": len(stats)
        })
    except ImportError as e:
        logger.error(f"Learning stats import error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Learning module not found",
            "systems": {},
            "total_systems": 0
        }), 200
    except Exception as e:
        logger.error(f"Learning stats error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "systems": {},
            "total_systems": 0
        }), 200

@app.route('/api/learning/smart-commands/predict', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("120 per minute")
def api_smart_command_predict():
    """Predict next command based on context"""
    try:
        from ai_assistant.services.learning_integration import LEARNING_SYSTEMS_AVAILABLE
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        from ai_assistant.ai.smart_command_prediction import SmartCommandPredictor
        predictor = SmartCommandPredictor()
        
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        context = data.get('context', {})
        recent_commands = data.get('recent_commands', [])
        recent_outputs = data.get('recent_outputs', [])
        
        prediction = predictor.predict_command(user_id, context, recent_commands, recent_outputs)
        
        return jsonify({
            "success": True,
            "prediction": prediction
        })
    except Exception as e:
        logger.error(f"Smart command prediction error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/context/generate', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("120 per minute")
def api_context_generate():
    """Generate context-aware response"""
    try:
        from ai_assistant.services.learning_integration import LEARNING_SYSTEMS_AVAILABLE
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        from ai_assistant.ai.context_aware_response import ContextAwareResponseGenerator
        generator = ContextAwareResponseGenerator()
        
        data = request.get_json()
        query = data.get('query', '')
        conversation_history = data.get('conversation_history', [])
        user_profile = data.get('user_profile', {})
        
        response = generator.generate_response(query, conversation_history, user_profile)
        
        return jsonify({
            "success": True,
            "response": response
        })
    except Exception as e:
        logger.error(f"Context generation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/workflow/recommend', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("60 per minute")
def api_workflow_recommend():
    """Get workflow recommendations"""
    try:
        from ai_assistant.services.learning_integration import LEARNING_SYSTEMS_AVAILABLE
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        from ai_assistant.ai.workflow_recommender import WorkflowRecommender
        recommender = WorkflowRecommender()
        
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        current_task = data.get('current_task', '')
        context = data.get('context', {})
        
        recommendations = recommender.recommend_workflows(user_id, current_task, context)
        
        return jsonify({
            "success": True,
            "recommendations": recommendations
        })
    except Exception as e:
        logger.error(f"Workflow recommendation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/anomaly/detect', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("120 per minute")
def api_anomaly_detect():
    """Detect anomalies in system behavior"""
    try:
        from ai_assistant.services.learning_integration import LEARNING_SYSTEMS_AVAILABLE
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        from ai_assistant.ai.anomaly_detection import AnomalyDetector
        detector = AnomalyDetector()
        
        data = request.get_json()
        features = data.get('features', [])
        
        result = detector.detect(features)
        
        return jsonify({
            "success": True,
            "is_anomaly": result['is_anomaly'],
            "anomaly_score": result.get('anomaly_score', 0)
        })
    except Exception as e:
        logger.error(f"Anomaly detection error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/causal/query', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("60 per minute")
def api_causal_query():
    """Query causal relationships"""
    try:
        from ai_assistant.services.learning_integration import LEARNING_SYSTEMS_AVAILABLE
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        from ai_assistant.ai.causal_inference import CausalInference
        causal = CausalInference()
        
        data = request.get_json()
        action = data.get('action', '')
        target = data.get('target', '')
        
        # Add edge if both provided
        if action and target:
            causal.add_edge(action, target, strength=data.get('strength', 0.5))
        
        stats = causal.get_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Causal query error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/knowledge-graph/query', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("120 per minute")
def api_knowledge_graph_query():
    """Query personal knowledge graph"""
    try:
        from ai_assistant.services.learning_integration import LEARNING_SYSTEMS_AVAILABLE
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        from ai_assistant.ai.enhanced_learning import PersonalKnowledgeGraph
        kg = PersonalKnowledgeGraph(db_path="data/knowledge_graph.db")
        
        data = request.get_json()
        query_type = data.get('type', 'stats')
        
        if query_type == 'stats':
            result = kg.get_stats()
        elif query_type == 'export':
            result = kg.export_graph_data()
        else:
            result = {"error": "Unknown query type"}
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        logger.error(f"Knowledge graph query error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/adaptive-voice/log', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("200 per minute")
def api_adaptive_voice_log():
    """Log voice recognition for adaptation"""
    try:
        from ai_assistant.services.learning_integration import LEARNING_SYSTEMS_AVAILABLE
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        from ai_assistant.ai.adaptive_voice import AdaptiveVoiceRecognition
        voice = AdaptiveVoiceRecognition()
        
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        transcription = data.get('transcription', '')
        intended_text = data.get('intended_text', None)
        confidence = data.get('confidence', 1.0)
        
        voice.log_recognition(user_id, transcription, intended_text, confidence)
        
        return jsonify({
            "success": True,
            "message": "Recognition logged"
        })
    except Exception as e:
        logger.error(f"Adaptive voice log error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/rl/action', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("120 per minute")
def api_rl_select_action():
    """Select action using reinforcement learning"""
    try:
        from ai_assistant.services.learning_integration import LEARNING_SYSTEMS_AVAILABLE
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        from ai_assistant.ai.full_rl_system import PPOAgent
        agent = PPOAgent(state_dim=10, action_dim=5)
        
        data = request.get_json()
        state = data.get('state', [0] * 10)
        
        action = agent.select_action(state)
        
        return jsonify({
            "success": True,
            "action": int(action),
            "state": state
        })
    except Exception as e:
        logger.error(f"RL action selection error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning/system/<system_name>/stats')
@jwt_required(optional=True)
def api_single_system_stats(system_name):
    """Get stats for a single learning system"""
    try:
        from ai_assistant.services.learning_integration import get_learning_stats, LEARNING_SYSTEMS_AVAILABLE
        
        if not LEARNING_SYSTEMS_AVAILABLE:
            return jsonify({"error": "Learning systems not available"}), 503
        
        all_stats = get_learning_stats()
        
        if system_name not in all_stats:
            return jsonify({"error": f"System '{system_name}' not found"}), 404
        
        return jsonify({
            "success": True,
            "system": system_name,
            "stats": all_stats[system_name]
        })
    except Exception as e:
        logger.error(f"Single system stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/local-ai/status', methods=['GET'])
@limiter.limit("10 per minute")
def api_local_ai_status():
    """Get local AI initialization status for debugging"""
    try:
        return jsonify({
            "success": True,
            "local_ai_available": LOCAL_AI_AVAILABLE,
            "local_ai_initialized": local_ai_initialized,
            "local_ai_manager_loaded": local_ai_manager is not None,
            "current_model": local_ai_manager.current_model if local_ai_manager else None,
            "background_init_enabled": BACKGROUND_INIT,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/chat', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("60 per minute")
def api_chat():
    """Enhanced chat endpoint with full AI integration and learning"""
    start_time = time.time()
    try:
        current_user = get_jwt_identity() or "anonymous"
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_input(data, 'message', 'command')
        if not is_valid:
            return jsonify({"error": error}), 400
        
        message = sanitize_command(data['message'])
        context = data.get('context', {})
        image_data = data.get('image', None)
        
        if not message and not image_data:
            return jsonify({"error": "No message or image provided"}), 400
        
        # === NEW: Multi-step Task Chain Orchestration ===
        try:
            from ai_assistant.integrations.orchestrator_integration import should_use_orchestrator, process_with_orchestrator
            
            if should_use_orchestrator(message):
                logger.info(f"🔗 Multi-step command detected: {message}")
                orch_result = process_with_orchestrator(message, context)
                
                if orch_result['success']:
                    return jsonify({
                        "message": message,
                        "response": orch_result['response'],
                        "orchestrated": True,
                        "steps_completed": orch_result['steps_completed'],
                        "total_steps": orch_result['total_steps'],
                        "features_used": ["multi_step_orchestration"],
                        "user": current_user,
                        "timestamp": datetime.now().isoformat()
                    })
                elif not orch_result.get('fallback'):
                    # Hard error, don't fallback
                    return jsonify({
                        "error": orch_result.get('error', 'Multi-step execution failed'),
                        "orchestrated": True,
                        "timestamp": datetime.now().isoformat()
                    }), 500
                else:
                    logger.warning("Orchestrator unavailable/failed, using fallback")
                    # Continue to normal processing below
        except Exception as orch_error:
            logger.warning(f"Orchestrator error, falling back: {orch_error}")
            # Continue to normal processing
        # === END: Multi-step Orchestration ===
        
        # Check if user wants to use local AI
        use_local_ai = data.get('use_local_ai', False) or data.get('offline_mode', False)
        
        if use_local_ai and local_ai_initialized and local_ai_manager:
            # Use local Ollama model
            try:
                logger.info(f"Using local AI for: {message[:50]}...")
                local_response = local_ai_manager.chat(message, max_tokens=512)
                
                return jsonify({
                    "message": message,
                    "response": local_response,
                    "features_used": ["local_ai", "ollama"],
                    "model": local_ai_manager.current_model,
                    "suggestions": [],
                    "mood": "neutral",
                    "user": current_user,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as local_error:
                logger.error(f"Local AI error: {local_error}, falling back to cloud")
                # Fall through to cloud AI below
        
        # Apply learning-enhanced response generation
        try:
            from ai_assistant.integrations.learning_integration import get_learning_assistant
            learning_assistant = get_learning_assistant(current_user)
            if learning_assistant.systems_active:
                # Enhance message with context-aware generation
                message = learning_assistant.generate_intelligent_response(message, context)
                logger.info("Applied learning-enhanced response generation")
        except Exception as e:
            logger.warning(f"Learning enhancement skipped: {e}")
        
        # Try cloud AI (Gemini) first, fallback to local if it fails
        try:
            # Process with full AI capabilities (Gemini)
            response = assistant.process_enhanced_chat(message, context, image_data)
            
            return jsonify({
                "message": message,
                "response": response["response"],
                "features_used": response["features_used"],
                "suggestions": response.get("suggestions", []),
                "mood": response.get("mood", "neutral"),
                "context_id": response.get("context_id"),
                "user": current_user,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as cloud_error:
            # If Gemini fails (quota, network, etc.) and local AI is available, use it
            if local_ai_initialized and local_ai_manager:
                logger.warning(f"Cloud AI failed ({str(cloud_error)[:100]}), using local AI fallback")
                try:
                    local_response = local_ai_manager.chat(message, max_tokens=512)
                    
                    return jsonify({
                        "message": message,
                        "response": local_response,
                        "features_used": ["local_ai_fallback", "ollama"],
                        "model": local_ai_manager.current_model,
                        "suggestions": [],
                        "mood": "neutral",
                        "fallback": True,
                        "user": current_user,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as local_error:
                    logger.error(f"Local AI fallback also failed: {local_error}")
                    # Re-raise original cloud error
                    raise cloud_error
            else:
                # No local AI available, re-raise original error
                raise cloud_error
                
    except Exception as e:
        logging.error(f"Chat API error: {str(e)}")
        return jsonify({"error": f"Chat processing failed: {str(e)[:200]}"}), 500

@app.route('/api/command', methods=['POST'])
@limiter.limit("30 per minute")
def api_command():
    """Process text command - NO AUTH REQUIRED"""
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_input(data, 'command', 'command')
        if not is_valid:
            return jsonify({"error": error}), 400
        
        command = sanitize_command(data['command'])
        
        if not command:
            return jsonify({"error": "No command provided"}), 400
        
        # === NEW: Multi-step Task Chain Orchestration ===
        try:
            from ai_assistant.integrations.orchestrator_integration import should_use_orchestrator, process_with_orchestrator
            
            if should_use_orchestrator(command):
                logger.info(f"🔗 Multi-step command detected: {command}")
                orch_result = process_with_orchestrator(command, {})
                
                if orch_result['success']:
                    return jsonify({
                        "success": True,
                        "command": command,
                        "response": orch_result['response'],
                        "orchestrated": True,
                        "steps_completed": orch_result['steps_completed'],
                        "total_steps": orch_result['total_steps'],
                        "timestamp": datetime.now().isoformat()
                    })
                elif not orch_result.get('fallback'):
                    # Hard error, don't fallback
                    return jsonify({
                        "success": False,
                        "error": orch_result.get('error', 'Multi-step execution failed'),
                        "orchestrated": True,
                        "command": command,
                        "timestamp": datetime.now().isoformat()
                    }), 500
                else:
                    logger.warning("Orchestrator unavailable/failed, using fallback")
                    # Continue to normal processing below
        except Exception as orch_error:
            logger.warning(f"Orchestrator error, falling back: {orch_error}")
            # Continue to normal processing
        # === END: Multi-step Orchestration ===
        
        # Check if user wants to use local AI
        use_local_ai = data.get('use_local_ai', False) or data.get('offline_mode', False)
        
        if use_local_ai and local_ai_initialized and local_ai_manager:
            # Use local Ollama model
            try:
                logger.info(f"Using local AI for command: {command[:50]}...")
                local_response = local_ai_manager.chat(command, max_tokens=512)
                
                return jsonify({
                    "success": True,
                    "command": command,
                    "response": local_response,
                    "model": local_ai_manager.current_model,
                    "offline_mode": True,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as local_error:
                logger.error(f"Local AI error: {local_error}, falling back to cloud")
                # Fall through to cloud AI below
        
        # Process command with cloud AI (default)
        try:
            response = assistant.process_command(command)
            
            return jsonify({
                "success": True,
                "command": command,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as cmd_error:
            # If cloud fails and local AI is available, try local fallback
            if local_ai_initialized and local_ai_manager:
                logger.warning(f"Cloud AI failed ({str(cmd_error)[:100]}), using local AI fallback")
                try:
                    local_response = local_ai_manager.chat(command, max_tokens=512)
                    
                    return jsonify({
                        "success": True,
                        "command": command,
                        "response": local_response,
                        "model": local_ai_manager.current_model,
                        "offline_mode": True,
                        "fallback": True,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as local_error:
                    logger.error(f"Local AI fallback also failed: {local_error}")
                    # Re-raise original cloud error
                    raise cmd_error
            else:
                # No local AI available, return error
                raise cmd_error
                
        except Exception as cmd_error:
            return jsonify({
                "success": False,
                "error": f"Command processing failed: {str(cmd_error)}",
                "command": command,
                "timestamp": datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        api_logger.error(f"Command API error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# JARVIS-Style Startup Sequence API Endpoints
# ============================================================================

@app.route('/api/startup/sequence', methods=['GET'])
@limiter.limit("10 per minute")
def api_startup_sequence():
    """Get complete startup sequence data (JARVIS-style)"""
    try:
        from ai_assistant.services.startup_sequence import get_startup_sequence
        
        startup = get_startup_sequence()
        data = startup.get_startup_sequence_data()
        
        return jsonify({
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Startup sequence error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to generate startup sequence",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/startup/diagnostics', methods=['GET'])
@limiter.limit("20 per minute")
def api_startup_diagnostics():
    """Get system diagnostics for startup sequence"""
    try:
        from ai_assistant.services.startup_sequence import get_startup_sequence
        
        startup = get_startup_sequence()
        diagnostics = startup.get_system_diagnostics()
        
        return jsonify({
            "success": True,
            "diagnostics": diagnostics,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Startup diagnostics error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get system diagnostics",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/startup/briefing', methods=['GET'])
@limiter.limit("20 per minute")
def api_startup_briefing():
    """Get contextual briefing for startup sequence"""
    try:
        from ai_assistant.services.startup_sequence import get_startup_sequence
        
        startup = get_startup_sequence()
        briefing = startup.get_contextual_briefing()
        
        return jsonify({
            "success": True,
            "briefing": briefing,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Startup briefing error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get briefing",
            "timestamp": datetime.now().isoformat()
        }), 500

# ============================================================================
# End of Startup Sequence API Endpoints
# ============================================================================

# ============================================================================
# ADVANCED FEATURES API ENDPOINTS
# ============================================================================

@app.route('/api/enhanced/chat', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("60 per minute")
async def api_enhanced_chat():
    """Enhanced chat with all advanced features: caching, routing, streaming, emotion detection"""
    try:
        if not ENHANCED_AI_AVAILABLE:
            return jsonify({
                "error": "Enhanced AI not available. Run: pip install diskcache sentence-transformers",
                "fallback": True
            }), 503
        
        current_user = get_jwt_identity() or "anonymous"
        data = request.get_json()
        
        message = data.get('message', '')
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Optional parameters
        enable_cache = data.get('enable_cache', True)
        enable_streaming = data.get('enable_streaming', False)
        audio_path = data.get('audio_path', None)  # For emotion detection
        context = data.get('context', {})
        
        # Process with enhanced AI
        result = await enhanced_ai.process_query(
            query=message,
            context=context,
            enable_cache=enable_cache,
            enable_streaming=enable_streaming,
            audio_path=audio_path
        )
        
        # Log for learning
        if LEARNING_ROUTER_AVAILABLE and learning_router:
            learning_router.route_conversation(message, result['text'], current_user)
        
        return jsonify({
            "success": True,
            "message": message,
            "response": result['text'],
            "metadata": {
                "model": result['model'],
                "cached": result['cached'],
                "emotion": result.get('emotion'),
                "complexity": result.get('complexity', 0),
                "time_ms": result['time_ms'],
                "tokens": result.get('tokens', 0),
                "cost_usd": result.get('cost_usd', 0)
            },
            "features_used": ["enhanced_ai", "semantic_cache", "model_routing"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Enhanced chat error: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

@app.route('/api/enhanced/stats', methods=['GET'])
@limiter.limit("30 per minute")
def api_enhanced_stats():
    """Get comprehensive stats for all advanced features"""
    try:
        if not ENHANCED_AI_AVAILABLE:
            return jsonify({"error": "Enhanced AI not available"}), 503
        
        stats = enhanced_ai.get_stats()
        
        return jsonify({
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Enhanced stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/enhanced/cache/clear', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def api_clear_cache():
    """Clear the semantic response cache"""
    try:
        if not ENHANCED_AI_AVAILABLE:
            return jsonify({"error": "Enhanced AI not available"}), 503
        
        if enhanced_ai.cache:
            enhanced_ai.cache.invalidate()  # Clear all cache
            
            return jsonify({
                "success": True,
                "message": "Cache cleared successfully",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Cache not available"}), 503
        
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/usage-analysis', methods=['GET'])
@jwt_required(optional=True)
@limiter.limit("10 per minute")
def api_usage_analysis():
    """Get usage pattern analysis and training data"""
    try:
        if not USAGE_ANALYZER_AVAILABLE:
            return jsonify({"error": "Usage analyzer not available"}), 503
        
        days_back = int(request.args.get('days', 30))
        
        # Run analysis
        results = usage_analyzer.analyze_all(days_back=days_back)
        
        return jsonify({
            "success": True,
            "analysis": {
                "common_commands": results.get('common_commands', [])[:10],
                "frequent_topics": results.get('frequent_topics', [])[:10],
                "time_patterns": results.get('time_patterns', {}),
                "app_usage": results.get('app_usage', {}),
                "command_sequences": results.get('command_sequences', [])[:5],
                "preferences": results.get('preferences', {}),
                "training_data_count": len(results.get('training_data', []))
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Usage analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/usage-analysis/export', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def api_export_training_data():
    """Export training data for fine-tuning"""
    try:
        if not USAGE_ANALYZER_AVAILABLE:
            return jsonify({"error": "Usage analyzer not available"}), 503
        
        data = request.get_json()
        format_type = data.get('format', 'openai')  # 'openai' or 'huggingface'
        days_back = data.get('days', 30)
        
        # Analyze
        results = usage_analyzer.analyze_all(days_back=days_back)
        
        # Export
        output_path = f"data/training/finetuning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        exported_file = usage_analyzer.export_for_finetuning(output_path, format=format_type)
        
        return jsonify({
            "success": True,
            "file_path": exported_file,
            "examples_count": len(results.get('training_data', [])),
            "format": format_type,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Export training data error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/automation/verify', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("30 per minute")
async def api_verify_automation():
    """Verify automation action using visual verification"""
    try:
        if not ENHANCED_AI_AVAILABLE:
            return jsonify({"error": "Visual verification not available"}), 503
        
        data = request.get_json()
        action_name = data.get('action_name', 'automation')
        app_name = data.get('app_name', None)
        
        # Verify automation
        result = await enhanced_ai.verify_automation(action_name, app_name)
        
        return jsonify({
            "success": result['success'],
            "verification": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Automation verification error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# End of Advanced Features API Endpoints
# ============================================================================


# Chat Streaming Session Management
chat_sessions = {}
chat_session_lock = threading.Lock()

@app.route('/api/chat/stream', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("30 per minute")
def api_chat_stream():
    """
    Stream chat response token-by-token via Server-Sent Events.
    Provides real-time response generation with response count tracking.
    """
    try:
        current_user = get_jwt_identity() or "anonymous"
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_input(data, 'message', 'command')
        if not is_valid:
            return jsonify({"error": error}), 400
        
        message = sanitize_command(data['message'])
        session_id = data.get('session_id', f"{current_user}_{int(time.time())}")
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        logger.info(f"ðŸ”„ Streaming chat for user: {current_user}, session: {session_id}")
        
        def generate_stream():
            """Generate streaming response tokens"""
            try:
                # Get or create chat session
                with chat_session_lock:
                    if session_id not in chat_sessions:
                        if LLM_PROVIDER_AVAILABLE:
                            chat_sessions[session_id] = UnifiedChatInterface()
                            chat_sessions[session_id].add_system_message(
                                "You are a helpful AI assistant. Respond concisely and accurately."
                            )
                        else:
                            # Fallback if LLM not available
                            yield f"data: {json.dumps({'error': 'LLM provider not available'})}\n\n"
                            return
                    
                    chat = chat_sessions[session_id]
                
                # Stream the response
                start_time = time.time()
                tokens = 0
                full_response = ""
                
                logger.debug(f"Starting stream for message: {message[:50]}...")
                
                try:
                    # Get streaming response
                    for token in chat.chat(message, stream=True):
                        tokens += 1
                        full_response += token
                        
                        # Emit token with count
                        token_data = json.dumps({
                            'token': token,
                            'count': tokens,
                            'partial': full_response
                        })
                        yield f"data: {token_data}\n\n"
                        
                        # Small delay to prevent overwhelming client
                        time.sleep(0.001)
                except Exception as stream_error:
                    logger.error(f"Streaming error: {stream_error}")
                    error_data = json.dumps({'error': f'Streaming failed: {str(stream_error)}'})
                    yield f"data: {error_data}\n\n"
                    return
                
                # Send completion stats
                duration = time.time() - start_time
                completion_data = json.dumps({
                    'done': True,
                    'tokens': tokens,
                    'duration': round(duration, 2),
                    'tokens_per_second': round(tokens / duration, 2) if duration > 0 else 0,
                    'full_response': full_response,
                    'user': current_user,
                    'timestamp': datetime.now().isoformat()
                })
                yield f"data: {completion_data}\n\n"
                
                logger.info(f"âœ… Stream complete: {tokens} tokens in {duration:.2f}s ({tokens/duration:.1f} tok/s)")
                
            except Exception as e:
                logger.error(f"Stream generation error: {e}")
                error_msg = json.dumps({'error': str(e)})
                yield f"data: {error_msg}\n\n"
        
        return Response(generate_stream(), mimetype='text/event-stream')
    
    except Exception as e:
        logger.error(f"Chat stream endpoint error: {str(e)}")
        return jsonify({"error": f"Chat streaming failed: {str(e)}"}), 500

@app.route('/api/chat/sessions/<session_id>', methods=['GET'])
@jwt_required(optional=True)
def api_get_session(session_id):
    """Get information about a chat session"""
    try:
        if session_id not in chat_sessions:
            return jsonify({"error": "Session not found"}), 404
        
        chat = chat_sessions[session_id]
        stats = {
            "session_id": session_id,
            "messages": len(chat.conversation_history),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/sessions/<session_id>', methods=['DELETE'])
@jwt_required(optional=True)
def api_delete_session(session_id):
    """Delete a chat session"""
    try:
        with chat_session_lock:
            if session_id in chat_sessions:
                del chat_sessions[session_id]
                return jsonify({"success": True, "message": "Session deleted"})
        
        return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/stats')
@jwt_required()
@limiter.limit("60 per minute")
def api_system_stats():
    """Get real-time system statistics - PROTECTED"""
    try:
        stats = assistant.get_real_time_system_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": "Failed to retrieve system stats"}), 500

@app.route('/api/weather')
@jwt_required()
@limiter.limit("20 per minute")
def api_weather():
    """Get weather information - PROTECTED"""
    try:
        if AUTOMATION_AVAILABLE:
            weather = get_weather_info()
        else:
            weather = {
                "temperature": "72Â°F",
                "description": "Sunny and Clear",
                "humidity": "45%",
                "wind_speed": "12 mph",
                "icon": "â˜€ï¸"
            }
        return jsonify(weather)
    except Exception as e:
        return jsonify({"error": "Failed to retrieve weather"}), 500

# Enhanced Feature Endpoints for Full AI Integration
@app.route('/api/features', methods=['GET'])
def api_features():
    """Get list of all available features and their status"""
    features = {
        "conversational_ai": CONVERSATIONAL_AI_AVAILABLE,
        "multimodal_ai": MULTIMODAL_AVAILABLE,
        "multilingual": MULTILINGUAL_AVAILABLE,
        "automation": AUTOMATION_AVAILABLE,
        "voice_recognition": VOICE_AVAILABLE,
        "modules": {
            "smart_automation": True,
            "enhanced_learning": True,
            "advanced_integration": True,
            "file_operations": True,
            "web_scraping": True,
            "music_control": True,
            "email_handler": True,
            "calendar_integration": True,
            "document_ocr": True,
            "memory_system": True,
            "system_monitoring": True,
            "taskbar_detection": True
        }
    }
    return jsonify(features)

@app.route('/api/chat/context', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("20 per minute")
def api_create_context():
    """Create new conversation context"""
    try:
        if not assistant.conversational_ai:
            return jsonify({"error": "Conversational AI not available"}), 503
        
        data = request.get_json()
        name = data.get('name', 'New Conversation')
        topic = data.get('topic', 'General Chat')
        initial_message = data.get('initial_message', '')
        
        context_id = assistant.conversational_ai.create_context(name, topic, initial_message)
        
        return jsonify({
            "context_id": context_id,
            "name": name,
            "topic": topic,
            "created_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to create context: {str(e)}"}), 500

@app.route('/api/chat/suggestions', methods=['GET'])
@jwt_required(optional=True)
@limiter.limit("30 per minute")
def api_get_suggestions():
    """Get AI-powered suggestions for next actions"""
    try:
        if not assistant.conversational_ai:
            return jsonify({"suggestions": []})
        
        suggestions = assistant.conversational_ai.suggest_next_actions()
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        return jsonify({"error": f"Failed to get suggestions: {str(e)}"}), 500

@app.route('/api/multimodal/analyze', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("10 per minute")
def api_multimodal_analyze():
    """Analyze image with AI"""
    try:
        if not assistant.multimodal_ai:
            return jsonify({"error": "Multimodal AI not available"}), 503
        
        data = request.get_json()
        image_data = data.get('image')
        prompt = data.get('prompt', 'What do you see in this image?')
        
        if not image_data:
            return jsonify({"error": "No image provided"}), 400
        
        analysis = assistant.multimodal_ai.analyze_image_from_base64(image_data, prompt)
        
        return jsonify({
            "analysis": analysis,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Image analysis failed: {str(e)}"}), 500

@app.route('/api/screen/analyze', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("5 per minute")
def api_analyze_screen():
    """Analyze current screen using multimodal AI"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'What is on the screen?')
        
        analysis = assistant.analyze_screen(prompt)
        
        return jsonify({
            "analysis": analysis,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Screen analysis failed: {str(e)}"}), 500

@app.route('/api/automation/workflows', methods=['GET'])
@jwt_required(optional=True)
@limiter.limit("20 per minute")
def api_get_workflows():
    """Get available automation workflows"""
    try:
        if not AUTOMATION_AVAILABLE:
            return jsonify({"workflows": []})
        
        from ai_assistant.modules.smart_automation import SmartAutomationEngine
        automation_engine = SmartAutomationEngine()
        workflows = automation_engine.get_available_workflows()
        
        return jsonify({"workflows": workflows})
    except Exception as e:
        return jsonify({"error": f"Failed to get workflows: {str(e)}"}), 500

@app.route('/api/automation/execute', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("10 per minute")
def api_execute_workflow():
    """Execute automation workflow"""
    try:
        if not AUTOMATION_AVAILABLE:
            return jsonify({"error": "Automation not available"}), 503
        
        data = request.get_json()
        workflow_name = data.get('workflow_name')
        
        if not workflow_name:
            return jsonify({"error": "Workflow name required"}), 400
        
        from ai_assistant.modules.smart_automation import SmartAutomationEngine
        automation_engine = SmartAutomationEngine()
        result = automation_engine.execute_workflow_by_name(workflow_name)
        
        return jsonify({
            "result": result,
            "workflow_name": workflow_name,
            "executed_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Workflow execution failed: {str(e)}"}), 500

@app.route('/api/memory/save', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("30 per minute")
def api_save_memory():
    """Save information to memory system"""
    try:
        if not AUTOMATION_AVAILABLE:
            return jsonify({"error": "Memory system not available"}), 503
        
        data = request.get_json()
        category = data.get('category', 'user')
        content = data.get('content')
        
        if not content:
            return jsonify({"error": "Content required"}), 400
        
        result = save_to_memory(category, content)
        
        return jsonify({
            "result": result,
            "category": category,
            "saved_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to save memory: {str(e)}"}), 500

@app.route('/api/memory/search', methods=['GET'])
@jwt_required(optional=True)
@limiter.limit("30 per minute")
def api_search_memory():
    """Search memory system"""
    try:
        if not AUTOMATION_AVAILABLE:
            return jsonify({"results": []})
        
        query = request.args.get('query', '')
        if not query:
            return jsonify({"error": "Search query required"}), 400
        
        results = search_memory(query)
        
        return jsonify({
            "results": results,
            "query": query,
            "searched_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Memory search failed: {str(e)}"}), 500

@app.route('/api/language/detect', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("30 per minute")
def api_detect_language():
    """Detect language of text"""
    try:
        if not assistant.multilingual:
            return jsonify({"error": "Multilingual support not available"}), 503
        
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({"error": "Text required"}), 400
        
        language_context = assistant.multilingual.detect_language(text)
        
        return jsonify({
            "detected_language": language_context.detected_language.value,
            "confidence": language_context.confidence,
            "original_text": text,
            "detected_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Language detection failed: {str(e)}"}), 500

@app.route('/api/language/translate', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("20 per minute")
def api_translate_text():
    """Translate text to target language"""
    try:
        if not assistant.multilingual:
            return jsonify({"error": "Multilingual support not available"}), 503
        
        data = request.get_json()
        text = data.get('text')
        target_language = data.get('target_language', 'en')
        
        if not text:
            return jsonify({"error": "Text required"}), 400
        
        from ai_assistant.multilingual import Language
        translated = assistant.multilingual.translate_text(text, Language(target_language))
        
        return jsonify({
            "original_text": text,
            "translated_text": translated,
            "target_language": target_language,
            "translated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

@app.route('/api/apps')
# Removed @jwt_required() to fix HTTP 401 error - public endpoint for app grid
@limiter.limit("30 per minute")
def api_apps():
    """Get list of installed applications - PUBLIC"""
    try:
        if AUTOMATION_AVAILABLE:
            apps = get_apps_for_web()
            # Ensure it's always a list
            if not isinstance(apps, list):
                apps = []
        else:
            # Fallback app list - MUST be an array, not object
            apps = [
                {"name": "Chrome", "path": "chrome.exe", "category": "Browser", "usage": 89, "description": "Google Chrome web browser"},
                {"name": "Mail", "path": "mail.exe", "category": "Communication", "usage": 76, "description": "Email application"},
                {"name": "Documents", "path": "word.exe", "category": "Productivity", "usage": 65, "description": "Document editor"},
                {"name": "Photos", "path": "photos.exe", "category": "Media", "usage": 52, "description": "Photo viewer"},
                {"name": "Videos", "path": "vlc.exe", "category": "Media", "usage": 43, "description": "Video player"},
                {"name": "Code", "path": "code.exe", "category": "Development", "usage": 92, "description": "Code editor"},
                {"name": "Database", "path": "pgadmin.exe", "category": "Development", "usage": 67, "description": "Database administration"},
                {"name": "Terminal", "path": "cmd.exe", "category": "System Tools", "usage": 78, "description": "Command line interface"},
                {"name": "Calculator", "path": "calc.exe", "category": "System Tools", "usage": 45, "description": "Windows calculator"},
                {"name": "Notepad", "path": "notepad.exe", "category": "System Tools", "usage": 30, "description": "Simple text editor"},
                {"name": "Paint", "path": "mspaint.exe", "category": "System Tools", "usage": 25, "description": "Image editor"},
                {"name": "Control Panel", "path": "control.exe", "category": "System Tools", "usage": 20, "description": "System settings"},
                {"name": "Task Manager", "path": "taskmgr.exe", "category": "System Tools", "usage": 35, "description": "Process manager"}
            ]
        
        # Always return array directly
        return jsonify(apps)
    except Exception as e:
        logger.error(f"Failed to get apps: {e}")
        # Return empty array on error, not error object
        return jsonify([]), 500

@app.route('/api/apps/refresh', methods=['POST'])
@limiter.limit("5 per minute")
def api_refresh_apps():
    """Refresh/rescan installed applications"""
    try:
        if AUTOMATION_AVAILABLE:
            result = refresh_app_database()
            apps = get_apps_for_web()
            return jsonify({
                "success": True,
                "message": result,
                "total": len(apps),
                "apps": apps
            })
        else:
            return jsonify({"success": False, "message": "App discovery not available"}), 503
    except Exception as e:
        logger.error(f"Failed to refresh apps: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/apps/launch', methods=['POST'])
@jwt_required(optional=True)  # Optional authentication for demo purposes
@limiter.limit("20 per minute")
def api_launch_app():
    """Launch an application - DEMO MODE"""
    try:
        current_user = get_jwt_identity() or "demo_user"
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_input(data, 'app_name', 'app_name')
        if not is_valid:
            return jsonify({"error": error}), 400
        
        app_name = data['app_name']
        
        try:
            if AUTOMATION_AVAILABLE:
                result = smart_open_application(app_name)
                if "Error" in result or "not found" in result.lower():
                    # Try alternative approaches for common apps
                    if "youtube music" in app_name.lower():
                        # Try opening YouTube Music via web
                        import webbrowser
                        webbrowser.open('https://music.youtube.com')
                        result = "Opened YouTube Music in web browser"
                    elif "spotify" in app_name.lower():
                        # Try opening Spotify via web
                        import webbrowser
                        webbrowser.open('https://open.spotify.com')
                        result = "Opened Spotify in web browser"
                    else:
                        result = f"Attempted to launch {app_name} (result: {result})"
            else:
                result = f"Launched {app_name} (simulation mode)"
        except Exception as launch_error:
            # Fallback for common applications
            if "youtube music" in app_name.lower():
                import webbrowser
                webbrowser.open('https://music.youtube.com')
                result = "Opened YouTube Music in web browser"
            elif "spotify" in app_name.lower():
                import webbrowser
                webbrowser.open('https://open.spotify.com')
                result = "Opened Spotify in web browser"
            else:
                result = f"Could not launch {app_name} directly, but command was received"
        
        return jsonify({
            "success": True,
            "message": result,
            "app_name": app_name,
            "user": current_user
        })
    except Exception as e:
        logger.error(f"Launch error: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to launch {data.get('app_name', 'application')}: {str(e)}"
        }), 500

@app.route('/api/spotify/status')
@jwt_required()
@limiter.limit("30 per minute")
def api_spotify_status():
    """Get Spotify status - PROTECTED"""
    try:
        if AUTOMATION_AVAILABLE:
            status = get_spotify_status()
        else:
            status = {
                "is_playing": True,
                "track_name": "Midnight Dreams",
                "artist_name": "Synthwave Collective",
                "progress": 65,
                "duration": 240
            }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": "Failed to retrieve Spotify status"}), 500

@app.route('/api/spotify/control', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def api_spotify_control():
    """Control Spotify playback - PROTECTED"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        action = data.get('action', '')
        
        if not action:
            return jsonify({"error": "No action provided"}), 400
        
        if AUTOMATION_AVAILABLE:
            if action == 'play_pause':
                result = spotify_play_pause()
            elif action == 'next':
                result = spotify_next_track()
            elif action == 'previous':
                result = spotify_previous_track()
            else:
                return jsonify({"error": "Unknown action"}), 400
        else:
            result = f"Spotify {action} executed (simulation mode)"
        
        return jsonify({
            "success": True,
            "message": result,
            "action": action,
            "user": current_user
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to control Spotify"
        }), 500

@app.route('/api/visual/question', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def api_visual_question():
    """Answer visual questions about screen content - PROTECTED"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_input(data, 'question', 'command')
        if not is_valid:
            return jsonify({"error": error}), 400
        
        question = data['question']
        
        answer = assistant.answer_visual_question(question)
        return jsonify({
            "question": question,
            "answer": answer,
            "user": current_user,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": "Failed to answer visual question"}), 500

# Activity feed endpoint
@app.route('/api/activity')
@jwt_required()
def api_activity():
    """Get recent activity feed - PROTECTED"""
    activities = [
        {"time": "2 min ago", "action": "Launched Spotify", "status": "success"},
        {"time": "15 min ago", "action": "Weather update received", "status": "info"},
        {"time": "1 hour ago", "action": "Calendar sync completed", "status": "success"},
        {"time": "3 hours ago", "action": "System optimization", "status": "info"}
    ]
    return jsonify(activities)

# Voice command history
@app.route('/api/voice/history')
@jwt_required()
def api_voice_history():
    """Get voice command history - PROTECTED"""
    history = [
        "Play my favorite playlist",
        "What's the weather like today?",
        "Schedule a meeting for 3 PM",
        "Open Chrome browser"
    ]
    return jsonify(history)

@app.route('/api/voice/status')
def api_voice_status():
    """Get voice system status - PUBLIC"""
    try:
        voice_available = VOICE_AVAILABLE and assistant.voice_recognizer is not None
        return jsonify({
            "connected": True,
            "voice_available": voice_available,
            "features": {
                "speech_recognition": assistant.voice_recognizer is not None,
                "text_to_speech": assistant.tts_engine is not None,
                "wake_word_detection": assistant.wake_word_detector is not None
            },
            "listening": getattr(assistant, 'voice_listening', False),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/voice/start', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def api_start_voice():
    """Start voice listening - PROTECTED"""
    try:
        result = assistant.start_voice_listening()
        if "error" in result:
            return jsonify(result), 500
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "Failed to start voice listening"}), 500

@app.route('/api/voice/stop', methods=['POST'])
@jwt_required()
def api_stop_voice():
    """Stop voice listening - PROTECTED"""
    try:
        result = assistant.stop_voice_listening()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "Failed to stop voice listening"}), 500

@app.route('/api/voice/speak', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def api_speak():
    """Convert text to speech - PROTECTED"""
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_input(data, 'text', 'command')
        if not is_valid:
            return jsonify({"error": error}), 400
        
        text = data['text']
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        success = assistant.speak_text(text)
        return jsonify({"success": success, "text": text})
    except Exception as e:
        logging.error(f"Error in api_speak: {str(e)}")
        return jsonify({"error": "Failed to process text-to-speech"}), 500

@app.route('/api/voice/list', methods=['GET'])
def api_list_voices():
    """Get list of available AI voices"""
    try:
        return jsonify({
            "success": True,
            "voices": AVAILABLE_VOICES,
            "default": "en-US-AriaNeural"
        })
    except Exception as e:
        logging.error(f"Error fetching voice list: {str(e)}")
        return jsonify({"error": "Failed to fetch voices"}), 500

@app.route('/api/voice/preview', methods=['POST'])
@limiter.limit("10 per minute")
def api_preview_voice():
    """Generate preview audio for a voice"""
    try:
        data = request.get_json()
        voice_id = data.get('voice_id', 'en-US-AriaNeural')
        sample_text = data.get('text', "Hello! This is a sample of my voice. I'm here to assist you with anything you need.")
        
        # Find voice info
        voice_info = next((v for v in AVAILABLE_VOICES if v['id'] == voice_id), None)
        if not voice_info:
            return jsonify({"error": "Voice not found"}), 404
        
        # Generate audio using Edge-TTS
        if VOICE_AVAILABLE:
            try:
                import edge_tts
                import tempfile
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                output_path = temp_file.name
                temp_file.close()
                
                # Generate audio
                async def generate():
                    communicate = edge_tts.Communicate(sample_text, voice_id)
                    await communicate.save(output_path)
                
                # Run async function
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                loop.run_until_complete(generate())
                
                # Read and encode as base64
                with open(output_path, 'rb') as f:
                    audio_data = f.read()
                
                import base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Clean up
                os.unlink(output_path)
                
                return jsonify({
                    "success": True,
                    "voice_id": voice_id,
                    "voice_name": voice_info['name'],
                    "audio_data": f"data:audio/mp3;base64,{audio_base64}"
                })
                
            except Exception as e:
                logging.error(f"Edge-TTS preview failed: {str(e)}")
                return jsonify({"error": f"Preview generation failed: {str(e)}"}), 500
        else:
            return jsonify({"error": "Voice synthesis not available"}), 503
            
    except Exception as e:
        logging.error(f"Voice preview error: {str(e)}")
        return jsonify({"error": "Failed to generate preview"}), 500

@app.route('/api/voice/process', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def api_process_voice():
    """Process voice audio data - PROTECTED"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        audio_data = data.get('audio_data', '')
        
        if not audio_data:
            return jsonify({"error": "No audio data provided"}), 400
        
        result = assistant.process_voice_audio(audio_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "Failed to process voice"}), 500

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {
        'message': 'Connected to YourDaddy Assistant',
        'timestamp': datetime.now().isoformat()
    })
    
    # Send voice server status
    voice_available = VOICE_AVAILABLE and assistant.voice_recognizer is not None
    emit('voice_server_status', {
        'connected': True,
        'voice_available': voice_available,
        'features': {
            'speech_recognition': assistant.voice_recognizer is not None,
            'text_to_speech': assistant.tts_engine is not None,
            'wake_word_detection': assistant.wake_word_detector is not None
        }
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('command')
def handle_command(data):
    """Handle real-time command"""
    try:
        command = data.get('command', '')
        message = data.get('message', command)  # Support both 'command' and 'message'
        model = data.get('model')  # Get model preference
        
        if command or message:
            # Use the actual command/message
            user_input = command or message
            
            # Process command with proper error handling
            response = assistant.process_command(user_input, model_preference=model)
            
            # Enhanced response format
            emit('command_response', {
                'command': user_input,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'type': 'text'
            })
            
            # Log the interaction
            print(f"âœ… Command processed: {user_input[:50]}...")
            
        else:
            emit('command_response', {
                'error': 'No command provided',
                'timestamp': datetime.now().isoformat(),
                'success': False
            })
            
    except Exception as e:
        print(f"âŒ Command processing error: {str(e)}")
        emit('command_response', {
            'error': f'Sorry, I encountered an error: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'success': False
        })

# Enhanced Chat SocketIO Events
@socketio.on('enhanced_chat')
def handle_enhanced_chat(data):
    """Handle enhanced chat with full AI integration"""
    try:
        message = data.get('message', '')
        context = data.get('context', {})
        image_data = data.get('image', None)
        model = data.get('model')  # Get model preference
        
        if message or image_data:
            response = assistant.process_enhanced_chat(message, context, image_data, model_preference=model)
            emit('enhanced_chat_response', {
                'message': message,
                'response': response['response'],
                'features_used': response['features_used'],
                'suggestions': response.get('suggestions', []),
                'mood': response.get('mood', 'neutral'),
                'context_id': response.get('context_id'),
                'detected_language': response.get('detected_language', 'english'),
                'message_type': response.get('message_type', 'general_chat'),
                'timestamp': datetime.now().isoformat()
            })
        else:
            emit('enhanced_chat_error', {'error': 'No message or image provided'})
    except Exception as e:
        emit('enhanced_chat_error', {'error': f'Chat processing failed: {str(e)}'})

@socketio.on('chat_stream')
def handle_chat_stream(data):
    """
    Handle real-time streaming chat via WebSocket.
    Streams response tokens as they are generated.
    """
    try:
        message = data.get('message', '')
        session_id = data.get('session_id', request.sid)
        
        if not message:
            emit('chat_stream_error', {'error': 'No message provided'})
            return
        
        logger.info(f"ðŸ“¡ WebSocket chat stream started: {session_id}")
        
        # Get or create chat session
        with chat_session_lock:
            if session_id not in chat_sessions:
                if LLM_PROVIDER_AVAILABLE:
                    chat_sessions[session_id] = UnifiedChatInterface()
                    chat_sessions[session_id].add_system_message(
                        "You are a helpful AI assistant. Respond concisely and accurately."
                    )
                else:
                    emit('chat_stream_error', {'error': 'LLM provider not available'})
                    return
            
            chat = chat_sessions[session_id]
        
        # Stream the response
        start_time = time.time()
        tokens = 0
        full_response = ""
        
        try:
            # Stream tokens
            for token in chat.chat(message, stream=True):
                tokens += 1
                full_response += token
                
                # Emit token to client
                emit('chat_token', {
                    'token': token,
                    'count': tokens,
                    'partial': full_response
                }, skip_sid=False)  # Send to current client
        
        except Exception as stream_error:
            logger.error(f"WebSocket streaming error: {stream_error}")
            emit('chat_stream_error', {'error': f'Streaming failed: {str(stream_error)}'})
            return
        
        # Send completion signal with stats
        duration = time.time() - start_time
        emit('chat_complete', {
            'tokens': tokens,
            'duration': round(duration, 2),
            'tokens_per_second': round(tokens / duration, 2) if duration > 0 else 0,
            'full_response': full_response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"âœ… WebSocket stream complete: {tokens} tokens in {duration:.2f}s")
        
    except Exception as e:
        logger.error(f"WebSocket chat stream error: {e}")
        emit('chat_stream_error', {'error': f'Chat stream failed: {str(e)}'})

@socketio.on('analyze_image')
def handle_analyze_image(data):
    """Handle image analysis request"""
    try:
        image_data = data.get('image')
        prompt = data.get('prompt', 'What do you see in this image?')
        
        if not image_data:
            emit('image_analysis_error', {'error': 'No image provided'})
            return
        
        if assistant.multimodal_ai:
            analysis = assistant.multimodal_ai.analyze_image_from_base64(image_data, prompt)
            emit('image_analysis_response', {
                'analysis': analysis,
                'prompt': prompt,
                'timestamp': datetime.now().isoformat()
            })
        else:
            emit('image_analysis_error', {'error': 'Multimodal AI not available'})
    except Exception as e:
        emit('image_analysis_error', {'error': f'Image analysis failed: {str(e)}'})

@socketio.on('analyze_screen')
def handle_analyze_screen(data):
    """Handle screen analysis request"""
    try:
        prompt = data.get('prompt', 'What is on the screen?')
        
        analysis = assistant.analyze_screen(prompt)
        emit('screen_analysis_response', {
            'analysis': analysis,
            'prompt': prompt,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        emit('screen_analysis_error', {'error': f'Screen analysis failed: {str(e)}'})

@socketio.on('get_suggestions')
def handle_get_suggestions():
    """Handle AI suggestions request"""
    try:
        if assistant.conversational_ai:
            suggestions = assistant.conversational_ai.suggest_next_actions()
            emit('suggestions_response', {
                'suggestions': suggestions,
                'timestamp': datetime.now().isoformat()
            })
        else:
            emit('suggestions_response', {'suggestions': []})
    except Exception as e:
        emit('suggestions_error', {'error': f'Failed to get suggestions: {str(e)}'})

@socketio.on('execute_workflow')
def handle_execute_workflow(data):
    """Handle workflow execution request"""
    try:
        workflow_name = data.get('workflow_name')
        
        if not workflow_name:
            emit('workflow_error', {'error': 'Workflow name required'})
            return
        
        if AUTOMATION_AVAILABLE:
            from ai_assistant.modules.smart_automation import SmartAutomationEngine
            automation_engine = SmartAutomationEngine()
            result = automation_engine.execute_workflow_by_name(workflow_name)
            
            emit('workflow_response', {
                'result': result,
                'workflow_name': workflow_name,
                'executed_at': datetime.now().isoformat()
            })
        else:
            emit('workflow_error', {'error': 'Automation not available'})
    except Exception as e:
        emit('workflow_error', {'error': f'Workflow execution failed: {str(e)}'})

@socketio.on('mood_detection')
def handle_mood_detection(data):
    """Handle mood detection request"""
    try:
        text = data.get('text', '')
        
        if not text:
            emit('mood_detection_error', {'error': 'Text required'})
            return
        
        if assistant.conversational_ai:
            mood = assistant.conversational_ai.detect_mood(text)
            emit('mood_detection_response', {
                'text': text,
                'mood': mood.value,
                'timestamp': datetime.now().isoformat()
            })
        else:
            emit('mood_detection_error', {'error': 'Conversational AI not available'})
    except Exception as e:
        emit('mood_detection_error', {'error': f'Mood detection failed: {str(e)}'})

@socketio.on('request_system_stats')
def handle_system_stats_request():
    """Handle system stats request"""
    stats = assistant.get_real_time_system_stats()
    emit('system_stats', stats)

@socketio.on('start_voice_listening')
def handle_start_voice():
    """Start voice listening"""
    result = assistant.start_voice_listening()
    emit('voice_start_response', result)

@socketio.on('stop_voice_listening')
def handle_stop_voice():
    """Stop voice listening"""
    result = assistant.stop_voice_listening()
    emit('voice_stop_response', result)

@socketio.on('voice_audio_data')
def handle_voice_audio(data):
    """Handle voice audio data from client"""
    audio_data = data.get('audio_data', '')
    if audio_data:
        result = assistant.process_voice_audio(audio_data)
        
        # Emit transcript if recognized
        if result.get('success') and result.get('transcript'):
            emit('voice_transcript', {
                'text': result['transcript'],
                'confidence': 0.9
            })
            
            # Also emit the response if available
            if result.get('response'):
                emit('voice_response', {
                    'response': result['response']
                })
        else:
            emit('voice_audio_response', result)

@socketio.on('voice_command')
def handle_voice_command(data):
    """Process voice command from transcript text"""
    try:
        text = data.get('text', '')
        language = data.get('language', 'en-US')
        
        if not text:
            emit('voice_response', {'response': 'No command received', 'error': True})
            return
        
        print(f"🎤 Processing voice command: {text}")
        print(f"   Language: {language}")
        
        # Log the voice interaction
        log_query(text)
        log_module_usage('voice', 'voice_command')
        
        # Process the command with full AI capabilities
        response = assistant.process_command(text)
        
        # Log the response
        log_reply(response)
        
        # Emit the response for talkback
        emit('voice_response', {
            'response': response,
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'command': text
        })
        
        print(f"✅ Voice command processed successfully")
        print(f"   Response: {response[:100]}...")
        print(f"🔊 Emitted voice_response event for talkback")
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Voice command error: {str(e)}")
        print(f"   Traceback: {error_trace}")
        
        error_msg = f'Sorry, I encountered an error: {str(e)}'
        log_action('voice_command_error', {'error': str(e), 'command': text})
        
        emit('voice_response', {
            'response': error_msg,
            'error': True,
            'success': False
        })

@socketio.on('request_tts')
def handle_tts_request(data):
    """Handle text-to-speech request with multilingual support"""
    text = data.get('text', '')
    language = data.get('language', 'auto')
    
    if text:
        if assistant.multilingual:
            # Use multilingual TTS
            result = assistant.multilingual.speak_multilingual(
                text, 
                Language(language) if language != 'auto' else Language.AUTO_DETECT
            )
            emit('tts_response', {'success': True, 'text': text, 'result': result})
        else:
            # Fallback to regular TTS
            success = assistant.speak_text(text)
            emit('tts_response', {'success': success, 'text': text})

# Multilingual API Routes
@app.route('/api/language/detect', methods=['POST'])
def detect_language():
    """Detect language of input text"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    if assistant.multilingual:
        context = assistant.multilingual.detect_language(text)
        return jsonify({
            'detected_language': context.detected_language.value,
            'confidence': context.confidence,
            'is_mixed': context.is_mixed,
            'hindi_percentage': context.hindi_percentage,
            'english_percentage': context.english_percentage
        })
    else:
        return jsonify({"error": "Multilingual support not available"}), 503

@app.route('/api/language/translate', methods=['POST'])
def translate_text():
    """Translate text between languages"""
    data = request.json
    text = data.get('text', '')
    target_language = data.get('target_language', 'en')
    source_language = data.get('source_language')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    if assistant.multilingual:
        try:
            target_lang = Language(target_language)
            source_lang = Language(source_language) if source_language else None
            
            result = assistant.multilingual.translate_text(text, target_lang, source_lang)
            return jsonify({
                'translated_text': result,
                'source_language': source_language,
                'target_language': target_language
            })
        except ValueError as e:
            return jsonify({"error": f"Invalid language code: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Translation failed: {str(e)}"}), 500
    else:
        return jsonify({"error": "Multilingual support not available"}), 503

@app.route('/api/language/hinglish', methods=['POST'])
def process_hinglish():
    """Process Hinglish commands"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    if assistant.multilingual:
        result = assistant.multilingual.process_hinglish_command(text)
        return jsonify(result)
    else:
        return jsonify({"error": "Multilingual support not available"}), 503

@app.route('/api/language/preference', methods=['POST'])
def set_language_preference():
    """Set user language preference"""
    data = request.json
    language = data.get('language', 'hinglish')
    tts_language = data.get('tts_language', language)
    user_id = data.get('user_id', 'web_user')
    
    if assistant.multilingual:
        try:
            lang = Language(language)
            tts_lang = Language(tts_language)
            assistant.multilingual.set_language_preference(user_id, lang, tts_lang)
            assistant.current_language = language
            return jsonify({
                'message': f'Language preference set to {language}',
                'user_id': user_id
            })
        except ValueError as e:
            return jsonify({"error": f"Invalid language: {str(e)}"}), 400
    else:
        return jsonify({"error": "Multilingual support not available"}), 503

@app.route('/api/language/preference', methods=['GET'])
def get_language_preference():
    """Get current language preference"""
    user_id = request.args.get('user_id', 'web_user')
    
    if assistant.multilingual:
        lang, tts_lang = assistant.multilingual.get_language_preference(user_id)
        return jsonify({
            'language': lang.value,
            'tts_language': tts_lang.value,
            'user_id': user_id
        })
    else:
        return jsonify({
            'language': 'en',
            'tts_language': 'en',
            'user_id': user_id
        })

# Multilingual SocketIO Events
@socketio.on('language_command')
def handle_multilingual_command(data):
    """Handle multilingual command"""
    command = data.get('command', '')
    language = data.get('language', 'auto')
    
    if command:
        log_query(command)
        if assistant.multilingual:
            response = assistant.process_multilingual_command(command)
        else:
            response = assistant.process_command(command)
        
        log_reply(response)
        emit('language_command_response', {
            'command': command,
            'response': response,
            'language': language,
            'timestamp': datetime.now().isoformat()
        })

# Duplicate handler removed - see handle_voice_audio above

# Error logging endpoint
@app.route('/api/error/log', methods=['POST'])
def api_log_error():
    """Log frontend errors for monitoring"""
    try:
        error_data = request.get_json()
        
        # Log to proper logger instead of print
        logger.error(f"Frontend Error: {error_data.get('message', 'Unknown error')}")
        logger.error(f"URL: {error_data.get('url', 'Unknown')}")
        logger.error(f"Time: {error_data.get('timestamp', 'Unknown')}")
        
        # Create error log entry
        error_log = {
            'timestamp': error_data.get('timestamp', datetime.now().isoformat()),
            'message': error_data.get('message', ''),
            'stack': error_data.get('stack', ''),
            'component_stack': error_data.get('componentStack', ''),
            'user_agent': error_data.get('userAgent', ''),
            'url': error_data.get('url', ''),
        }
        
        # Save to proper error log file in logs directory
        log_file = Path('logs/errors/frontend_errors.json')
        try:
            if log_file.exists() and log_file.stat().st_size > 0:
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
            else:
                logs = []
            
            logs.append(error_log)
            
            # Keep only last 100 errors
            if len(logs) > 100:
                logs = logs[-100:]
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save error log: {e}")
        
        return jsonify({"success": True, "logged": True})
    
    except Exception as e:
        logger.error(f"Error logging endpoint failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/save', methods=['POST'])
def api_save_settings():
    """Save user settings"""
    try:
        settings_data = request.get_json()
        
        # Save settings to a file (in production, use a database)
        settings_file = Path(__file__).parent / 'user_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(settings_data, f, indent=2)
        
        return jsonify({"success": True, "message": "Settings saved successfully"})
    
    except Exception as e:
        print(f"Failed to save settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/load')
def api_load_settings():
    """Load user settings"""
    try:
        settings_file = Path(__file__).parent / 'user_settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            return jsonify(settings)
        else:
            return jsonify({"settings": None})
    
    except Exception as e:
        print(f"Failed to load settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/all', methods=['GET'])
def api_get_all_settings():
    """Get all comprehensive settings"""
    try:
        settings_file = Path(__file__).parent.parent.parent / 'data' / 'user_preferences' / 'settings.json'
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        else:
            # Default settings
            settings = {
                "appearance": {
                    "theme": "dark",
                    "accentColor": "blue",
                    "fontSize": "medium",
                    "language": "en-US"
                },
                "notifications": {
                    "pushNotifications": True,
                    "soundAlerts": True,
                    "emailNotifications": False,
                    "desktopNotifications": True
                },
                "privacy": {
                    "dataCollection": "minimal",
                    "encryption": True,
                    "autoLock": "5 minutes",
                    "twoFactorAuth": False
                },
                "voice": {
                    "engine": "edge_tts",
                    "voice": "en-US-AriaNeural",
                    "speed": 1.0,
                    "volume": 0.9,
                    "wakeWord": "assistant",
                    "continuousListening": False
                },
                "ai": {
                    "preferredModel": "gemini-2.0-flash-exp",
                    "autoRoute": True,
                    "contextMemory": True,
                    "learningEnabled": True
                },
                "automation": {
                    "autoUpdate": True,
                    "backgroundTasks": True,
                    "autoBackup": "daily"
                }
            }
        
        return jsonify({"success": True, "settings": settings})
    
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/update', methods=['POST'])
def api_update_settings():
    """Update specific settings"""
    try:
        data = request.get_json()
        category = data.get('category')
        settings_data = data.get('settings')
        
        if not category or not settings_data:
            return jsonify({"success": False, "error": "Category and settings required"}), 400
        
        settings_file = Path(__file__).parent.parent.parent / 'data' / 'user_preferences' / 'settings.json'
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing settings
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                all_settings = json.load(f)
        else:
            all_settings = {}
        
        # Update category
        all_settings[category] = settings_data
        
        # Save
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(all_settings, f, indent=2)
        
        return jsonify({
            "success": True,
            "message": f"{category.capitalize()} settings updated",
            "settings": all_settings
        })
    
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/reset', methods=['POST'])
def api_reset_settings():
    """Reset settings to default"""
    try:
        data = request.get_json()
        category = data.get('category')  # Optional: reset specific category
        
        settings_file = Path(__file__).parent.parent.parent / 'data' / 'user_preferences' / 'settings.json'
        
        if category:
            # Reset specific category
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
            else:
                all_settings = {}
            
            # Remove category
            if category in all_settings:
                del all_settings[category]
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(all_settings, f, indent=2)
            
            return jsonify({"success": True, "message": f"{category.capitalize()} settings reset"})
        else:
            # Reset all settings
            if settings_file.exists():
                settings_file.unlink()
            
            return jsonify({"success": True, "message": "All settings reset to default"})
    
    except Exception as e:
        logger.error(f"Failed to reset settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/export', methods=['GET'])
def api_export_settings():
    """Export settings as JSON"""
    try:
        settings_file = Path(__file__).parent.parent.parent / 'data' / 'user_preferences' / 'settings.json'
        
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        else:
            settings = {}
        
        return jsonify({
            "success": True,
            "data": settings,
            "exportedAt": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Failed to export settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/import', methods=['POST'])
def api_import_settings():
    """Import settings from JSON"""
    try:
        data = request.get_json()
        imported_settings = data.get('settings')
        
        if not imported_settings:
            return jsonify({"success": False, "error": "No settings data provided"}), 400
        
        settings_file = Path(__file__).parent.parent.parent / 'data' / 'user_preferences' / 'settings.json'
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(imported_settings, f, indent=2)
        
        return jsonify({
            "success": True,
            "message": "Settings imported successfully",
            "settings": imported_settings
        })
    
    except Exception as e:
        logger.error(f"Failed to import settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# MODEL SELECTION & PREFERENCES API ENDPOINTS
# ============================================================

@app.route('/api/models/available', methods=['GET'])
@limiter.limit("30 per minute")
def api_get_available_models():
    """Get list of all available models with their providers"""
    try:
        models_list = []
        
        # Get models from router if available
        if ENHANCED_AI_AVAILABLE and enhanced_ai and enhanced_ai.router:
            router_models = enhanced_ai.router.models
            for model in router_models:
                models_list.append({
                    'id': model.name,
                    'name': model.name,
                    'provider': model.tier.value,
                    'tier': model.tier.value,
                    'max_tokens': model.max_tokens,
                    'cost_per_1k_tokens': model.cost_per_1k_tokens,
                    'avg_latency_ms': model.avg_latency_ms,
                    'capabilities': model.capabilities,
                    'priority': model.priority
                })
        else:
            # Fallback: provide default model list
            models_list = [
                {
                    'id': 'gemini-2.0-flash-exp',
                    'name': 'Gemini 2.0 Flash',
                    'provider': 'Google',
                    'tier': 'fast',
                    'max_tokens': 8192,
                    'cost_per_1k_tokens': 0.0001,
                    'avg_latency_ms': 500,
                    'capabilities': ['general', 'multimodal', 'coding'],
                    'priority': 10,
                    'description': 'Fast, cost-effective model for general queries'
                },
                {
                    'id': 'gpt-3.5-turbo',
                    'name': 'GPT-3.5 Turbo',
                    'provider': 'OpenAI',
                    'tier': 'standard',
                    'max_tokens': 4096,
                    'cost_per_1k_tokens': 0.002,
                    'avg_latency_ms': 1000,
                    'capabilities': ['general', 'coding', 'reasoning'],
                    'priority': 5,
                    'description': 'Balanced model for medium complexity tasks'
                },
                {
                    'id': 'gpt-4-turbo',
                    'name': 'GPT-4 Turbo',
                    'provider': 'OpenAI',
                    'tier': 'advanced',
                    'max_tokens': 8192,
                    'cost_per_1k_tokens': 0.03,
                    'avg_latency_ms': 3000,
                    'capabilities': ['general', 'coding', 'reasoning', 'creativity', 'math'],
                    'priority': 1,
                    'description': 'Most capable model for complex tasks'
                },
                {
                    'id': 'gemini-2.0-pro',
                    'name': 'Gemini 2.0 Pro',
                    'provider': 'Google',
                    'tier': 'advanced',
                    'max_tokens': 32768,
                    'cost_per_1k_tokens': 0.0025,
                    'avg_latency_ms': 2000,
                    'capabilities': ['general', 'multimodal', 'reasoning', 'coding'],
                    'priority': 2,
                    'description': 'Advanced multimodal model with large context'
                },
                {
                    'id': 'claude-3-sonnet',
                    'name': 'Claude 3 Sonnet',
                    'provider': 'Anthropic',
                    'tier': 'standard',
                    'max_tokens': 4096,
                    'cost_per_1k_tokens': 0.015,
                    'avg_latency_ms': 1500,
                    'capabilities': ['general', 'reasoning', 'coding'],
                    'priority': 4,
                    'description': 'Balanced Claude model'
                }
            ]
        
        # Group by provider
        by_provider = {}
        for model in models_list:
            provider = model.get('provider', 'Unknown')
            if provider not in by_provider:
                by_provider[provider] = []
            by_provider[provider].append(model)
        
        return jsonify({
            'success': True,
            'models': models_list,
            'by_provider': by_provider,
            'total_models': len(models_list),
            'providers': list(by_provider.keys()),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Get available models error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/preference', methods=['GET'])
@jwt_required(optional=True)
def api_get_model_preference():
    """Get user's preferred model"""
    try:
        current_user = get_jwt_identity() or "anonymous"
        
        # Load preferences from file
        prefs_file = Path('data') / 'user_preferences' / f'{current_user}_model_pref.json'
        
        if prefs_file.exists():
            with open(prefs_file, 'r') as f:
                preference = json.load(f)
        else:
            # Default preference
            preference = {
                'preferred_model': 'gemini-2.0-flash-exp',
                'auto_route': True,
                'fallback_model': 'gpt-3.5-turbo',
                'max_cost_per_query': 0.01
            }
        
        return jsonify({
            'success': True,
            'preference': preference,
            'user': current_user,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Get model preference error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/preference', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("30 per minute")
def api_set_model_preference():
    """Set user's preferred model"""
    try:
        current_user = get_jwt_identity() or "anonymous"
        data = request.get_json()
        
        preferred_model = data.get('preferred_model')
        auto_route = data.get('auto_route', True)
        fallback_model = data.get('fallback_model')
        max_cost_per_query = data.get('max_cost_per_query', 0.01)
        
        if not preferred_model:
            return jsonify({'success': False, 'error': 'preferred_model is required'}), 400
        
        # Save preference
        preference = {
            'preferred_model': preferred_model,
            'auto_route': auto_route,
            'fallback_model': fallback_model or 'gpt-3.5-turbo',
            'max_cost_per_query': max_cost_per_query,
            'updated_at': datetime.now().isoformat()
        }
        
        prefs_dir = Path('data') / 'user_preferences'
        prefs_dir.mkdir(parents=True, exist_ok=True)
        
        prefs_file = prefs_dir / f'{current_user}_model_pref.json'
        with open(prefs_file, 'w') as f:
            json.dump(preference, f, indent=2)
        
        logger.info(f"User {current_user} set preferred model to {preferred_model}")
        
        return jsonify({
            'success': True,
            'preference': preference,
            'message': f'Model preference saved: {preferred_model}',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Set model preference error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/stats', methods=['GET'])
@jwt_required(optional=True)
@limiter.limit("30 per minute")
def api_get_model_stats():
    """Get usage statistics for each model"""
    try:
        current_user = get_jwt_identity() or "anonymous"
        
        stats = {}
        
        # Get stats from router if available
        if ENHANCED_AI_AVAILABLE and enhanced_ai and enhanced_ai.router:
            router_stats = enhanced_ai.router.get_stats()
            stats['routing'] = router_stats
        
        # Get stats from enhanced AI
        if ENHANCED_AI_AVAILABLE and enhanced_ai:
            ai_stats = enhanced_ai.get_stats()
            stats['enhanced_ai'] = ai_stats
        
        return jsonify({
            'success': True,
            'stats': stats,
            'user': current_user,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Get model stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/compare', methods=['POST'])
@limiter.limit("20 per minute")
def api_compare_models():
    """Compare multiple models side by side"""
    try:
        data = request.get_json()
        model_ids = data.get('model_ids', [])
        
        if not model_ids or len(model_ids) < 2:
            return jsonify({'success': False, 'error': 'At least 2 model IDs required'}), 400
        
        # Get model details
        comparison = []
        
        if ENHANCED_AI_AVAILABLE and enhanced_ai and enhanced_ai.router:
            for model_id in model_ids:
                model = next((m for m in enhanced_ai.router.models if m.name == model_id), None)
                if model:
                    comparison.append({
                        'id': model.name,
                        'name': model.name,
                        'tier': model.tier.value,
                        'cost_per_1k_tokens': model.cost_per_1k_tokens,
                        'max_tokens': model.max_tokens,
                        'avg_latency_ms': model.avg_latency_ms,
                        'capabilities': model.capabilities
                    })
        
        return jsonify({
            'success': True,
            'comparison': comparison,
            'model_count': len(comparison),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Compare models error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/providers', methods=['GET'])
@limiter.limit("30 per minute")
def api_get_providers():
    """Get list of all available LLM providers"""
    try:
        providers = [
            {
                'id': 'google',
                'name': 'Google',
                'description': 'Google Gemini models',
                'models': ['gemini-2.0-flash-exp', 'gemini-2.0-pro', 'gemini-1.5-pro'],
                'features': ['multimodal', 'fast', 'cost-effective'],
                'api_key_required': True,
                'status': 'active'
            },
            {
                'id': 'openai',
                'name': 'OpenAI',
                'description': 'GPT models from OpenAI',
                'models': ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o'],
                'features': ['versatile', 'powerful', 'coding'],
                'api_key_required': True,
                'status': 'active'
            },
            {
                'id': 'anthropic',
                'name': 'Anthropic',
                'description': 'Claude models',
                'models': ['claude-3-sonnet', 'claude-3-opus', 'claude-3-haiku'],
                'features': ['safe', 'reasoning', 'long-context'],
                'api_key_required': True,
                'status': 'active'
            }
        ]
        
        return jsonify({
            'success': True,
            'providers': providers,
            'total_providers': len(providers),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Get providers error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# LOCAL AI API ENDPOINTS
# ============================================================

@app.route('/api/local_ai/status', methods=['GET'])
@limiter.limit("30 per minute")
def local_ai_status():
    """Get local AI status and info"""
    try:
        if not LOCAL_AI_AVAILABLE:
            return jsonify({
                'success': True,
                'available': False,
                'message': 'Local AI not installed. Run: pip install llama-cpp-python'
            })
        
        status = {
            'success': True,
            'available': True,
            'initialized': local_ai_initialized,
            'model_loaded': local_ai_manager is not None and local_ai_manager.current_model is not None
        }
        
        if local_ai_initialized and local_ai_manager:
            status['model_info'] = {
                'name': local_ai_manager.model_config.name if local_ai_manager.model_config else None,
                'context_length': local_ai_manager.model_config.context_length if local_ai_manager.model_config else None,
                'threads': local_ai_manager.model_config.threads if local_ai_manager.model_config else None
            }
            status['stats'] = local_ai_manager.get_stats()
        else:
            status['message'] = 'No model loaded. Download TinyLlama or Qwen2 model.'
        
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Local AI status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/local_ai/chat', methods=['POST'])
@limiter.limit("20 per minute")
def local_ai_chat():
    """Chat with local AI model"""
    try:
        if not local_ai_initialized or not local_ai_manager:
            return jsonify({
                'success': False,
                'error': 'Local AI not initialized. Check /api/local_ai/status'
            }), 503
        
        data = request.json
        message = data.get('message', '')
        max_tokens = data.get('max_tokens', 512)
        temperature = data.get('temperature', 0.7)
        use_history = data.get('use_history', True)
        
        if not message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
        
        # Log request
        log_api_request(
            endpoint='/api/local_ai/chat',
            method='POST',
            user_id='default',
            request_data={'message_length': len(message)}
        )
        
        # Generate response
        start_time = time.time()
        
        if use_history:
            response = local_ai_manager.chat(message, max_tokens=max_tokens)
        else:
            response = local_ai_manager.generate(
                message,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
        
        elapsed = time.time() - start_time
        
        return jsonify({
            'success': True,
            'response': response,
            'stats': {
                'elapsed_time': round(elapsed, 2),
                'avg_tokens_per_sec': local_ai_manager.stats.get('avg_tokens_per_sec', 0),
                'total_queries': local_ai_manager.stats.get('total_queries', 0)
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Local AI chat error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/local_ai/reset', methods=['POST'])
@limiter.limit("10 per minute")
def local_ai_reset():
    """Reset local AI conversation history"""
    try:
        if not local_ai_initialized or not local_ai_manager:
            return jsonify({
                'success': False,
                'error': 'Local AI not initialized'
            }), 503
        
        local_ai_manager.clear_history()
        
        return jsonify({
            'success': True,
            'message': 'Conversation history cleared'
        })
    
    except Exception as e:
        logger.error(f"Local AI reset error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/local_ai/stats', methods=['GET'])
@limiter.limit("30 per minute")
def local_ai_stats():
    """Get local AI performance statistics"""
    try:
        if not local_ai_initialized or not local_ai_manager:
            return jsonify({
                'success': False,
                'error': 'Local AI not initialized'
            }), 503
        
        stats = local_ai_manager.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Local AI stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/local_ai/load_model', methods=['POST'])
@limiter.limit("5 per minute")
def local_ai_load_model():
    """Load a specific local model"""
    global local_ai_manager, local_ai_initialized
    
    try:
        if not LOCAL_AI_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Local AI not available. Install llama-cpp-python'
            }), 503
        
        data = request.json
        model_name = data.get('model_name', 'tinyllama')
        threads = data.get('threads', 4)
        
        if not local_ai_manager:
            local_ai_manager = LocalAIManager()
        
        # Map model names to file paths
        model_paths = {
            'tinyllama': 'model/local_models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
            'qwen2': 'model/local_models/qwen2-0_5b-instruct-q4_k_m.gguf'
        }
        
        model_path = model_paths.get(model_name)
        if not model_path:
            return jsonify({
                'success': False,
                'error': f'Unknown model: {model_name}. Choose from: {list(model_paths.keys())}'
            }), 400
        
        if not Path(model_path).exists():
            return jsonify({
                'success': False,
                'error': f'Model file not found: {model_path}',
                'download_instructions': 'Run: huggingface-cli download TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --local-dir model/local_models'
            }), 404
        
        # Load model
        if local_ai_manager.load_model(str(model_path), threads=threads):
            local_ai_initialized = True
            return jsonify({
                'success': True,
                'message': f'Model {model_name} loaded successfully',
                'model_info': {
                    'name': local_ai_manager.model_config.name,
                    'path': local_ai_manager.model_config.path,
                    'threads': local_ai_manager.model_config.threads
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to load model'
            }), 500
    
    except Exception as e:
        logger.error(f"Local AI load model error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/local_ai/unload', methods=['POST'])
@limiter.limit("10 per minute")
def local_ai_unload():
    """Unload local AI model from memory"""
    global local_ai_initialized
    
    try:
        if local_ai_manager:
            local_ai_manager.unload_model()
            local_ai_initialized = False
            
            return jsonify({
                'success': True,
                'message': 'Model unloaded from memory'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No model loaded'
            }), 400
    
    except Exception as e:
        logger.error(f"Local AI unload error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# FILE OPERATIONS API ENDPOINTS
# ============================================================

@app.route('/api/files/organize', methods=['POST'])
@jwt_required()
def api_organize_files():
    """Organize files by type in a directory"""
    try:
        from ai_assistant.modules.file_ops import organize_files_by_type
        
        data = request.get_json()
        directory = data.get('directory')
        create_subfolders = data.get('create_subfolders', True)
        
        if not directory:
            return jsonify({"success": False, "error": "Directory path required"}), 400
        
        # Security: Basic path validation
        if not os.path.exists(directory):
            return jsonify({"success": False, "error": "Directory not found"}), 404
        
        result = organize_files_by_type(directory, create_subfolders)
        
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"File organization error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/files/find-duplicates', methods=['POST'])
@jwt_required()
def api_find_duplicates():
    """Find duplicate files in a directory"""
    try:
        from ai_assistant.modules.file_ops import find_duplicate_files
        
        data = request.get_json()
        directory = data.get('directory')
        include_subdirs = data.get('include_subdirs', True)
        
        if not directory:
            return jsonify({"success": False, "error": "Directory path required"}), 400
        
        result = find_duplicate_files(directory, include_subdirs)
        
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Duplicate file detection error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/files/search', methods=['POST'])
@jwt_required()
def api_search_files():
    """Search for files with advanced filtering"""
    try:
        from ai_assistant.modules.file_ops import smart_file_search
        
        data = request.get_json()
        directory = data.get('directory')
        pattern = data.get('pattern')
        search_content = data.get('search_content', False)
        file_types = data.get('file_types')
        
        if not directory or not pattern:
            return jsonify({"success": False, "error": "Directory and pattern required"}), 400
        
        result = smart_file_search(directory, pattern, search_content, file_types)
        
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"File search error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/files/batch-rename', methods=['POST'])
@jwt_required()
def api_batch_rename():
    """Batch rename files using patterns"""
    try:
        from ai_assistant.modules.file_ops import batch_rename_files
        
        data = request.get_json()
        directory = data.get('directory')
        pattern = data.get('pattern')
        replacement = data.get('replacement')
        preview = data.get('preview', True)
        
        if not all([directory, pattern, replacement]):
            return jsonify({"success": False, "error": "Directory, pattern, and replacement required"}), 400
        
        result = batch_rename_files(directory, pattern, replacement, preview)
        
        return jsonify({
            "success": True,
            "result": result,
            "preview": preview,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Batch rename error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/files/analyze-directory', methods=['POST'])
@jwt_required()
def api_analyze_directory():
    """Analyze directory structure and contents"""
    try:
        from ai_assistant.modules.file_ops import analyze_directory_structure
        
        data = request.get_json()
        directory = data.get('directory')
        max_depth = data.get('max_depth', 3)
        
        if not directory:
            return jsonify({"success": False, "error": "Directory path required"}), 400
        
        result = analyze_directory_structure(directory, max_depth)
        
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Directory analysis error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# DOCUMENT OCR API ENDPOINTS
# ============================================================

@app.route('/api/ocr/check-dependencies', methods=['GET'])
def api_ocr_check_dependencies():
    """Check OCR dependencies status"""
    try:
        from ai_assistant.modules.document_ocr import check_ocr_dependencies
        
        result = check_ocr_dependencies()
        
        return jsonify({
            "success": True,
            "dependencies_status": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"OCR dependency check error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ocr/extract-image', methods=['POST'])
@jwt_required()
def api_extract_text_image():
    """Extract text from image using OCR"""
    try:
        from ai_assistant.modules.document_ocr import extract_text_from_image
        
        data = request.get_json()
        image_path = data.get('image_path')
        language = data.get('language', 'eng')
        enhance = data.get('enhance', True)
        
        if not image_path:
            return jsonify({"success": False, "error": "Image path required"}), 400
        
        result = extract_text_from_image(image_path, language, enhance)
        
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Image OCR error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ocr/extract-pdf', methods=['POST'])
@jwt_required()
def api_extract_text_pdf():
    """Extract text from PDF document"""
    try:
        from ai_assistant.modules.document_ocr import extract_text_from_pdf
        
        data = request.get_json()
        pdf_path = data.get('pdf_path')
        page_range = data.get('page_range')
        
        if not pdf_path:
            return jsonify({"success": False, "error": "PDF path required"}), 400
        
        result = extract_text_from_pdf(pdf_path, page_range)
        
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ocr/analyze-document', methods=['POST'])
@jwt_required()
def api_analyze_document():
    """Analyze document structure and metadata"""
    try:
        from ai_assistant.modules.document_ocr import analyze_document_structure
        
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({"success": False, "error": "File path required"}), 400
        
        result = analyze_document_structure(file_path)
        
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Document analysis error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ocr/extract-info', methods=['POST'])
@jwt_required()
def api_extract_key_information():
    """Extract key information from text"""
    try:
        from ai_assistant.modules.document_ocr import extract_key_information
        
        data = request.get_json()
        text = data.get('text')
        info_type = data.get('info_type', 'general')
        
        if not text:
            return jsonify({"success": False, "error": "Text required"}), 400
        
        result = extract_key_information(text, info_type)
        
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Information extraction error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# WEB SCRAPING API ENDPOINTS
# ============================================================

@app.route('/api/web/weather', methods=['GET'])
def api_get_weather():
    """Get weather information for a location"""
    try:
        from ai_assistant.modules.web_scraping import get_weather_info
        
        location = request.args.get('location', 'New York')
        api_key = request.args.get('api_key')
        
        result = get_weather_info(location, api_key)
        
        return jsonify({
            "success": True,
            "weather": result,
            "location": location,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/web/news', methods=['GET'])
def api_get_news():
    """Get latest news headlines"""
    try:
        from ai_assistant.modules.web_scraping import get_latest_news
        
        category = request.args.get('category', 'general')
        country = request.args.get('country', 'us')
        max_articles = int(request.args.get('max_articles', 5))
        
        result = get_latest_news(category, country, max_articles)
        
        return jsonify({
            "success": True,
            "news": result,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"News API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/web/stock', methods=['GET'])
def api_get_stock():
    """Get stock price information"""
    try:
        from ai_assistant.modules.web_scraping import get_stock_price
        
        symbol = request.args.get('symbol', 'AAPL')
        
        result = get_stock_price(symbol)
        
        return jsonify({
            "success": True,
            "stock_info": result,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Stock API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/web/crypto', methods=['GET'])
def api_get_crypto():
    """Get cryptocurrency price information"""
    try:
        from ai_assistant.modules.web_scraping import get_crypto_price
        
        symbol = request.args.get('symbol', 'bitcoin')
        
        result = get_crypto_price(symbol)
        
        return jsonify({
            "success": True,
            "crypto_info": result,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Crypto API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/web/scrape', methods=['POST'])
@jwt_required()
def api_scrape_website():
    """Scrape website content"""
    try:
        from ai_assistant.modules.web_scraping import scrape_website_content
        
        data = request.get_json()
        url = data.get('url')
        extract_text = data.get('extract_text', True)
        max_length = data.get('max_length', 1000)
        
        if not url:
            return jsonify({"success": False, "error": "URL required"}), 400
        
        result = scrape_website_content(url, extract_text, max_length)
        
        return jsonify({
            "success": True,
            "content": result,
            "url": url,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Web scraping error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/web/trending', methods=['GET'])
def api_get_trending():
    """Get trending topics from various platforms"""
    try:
        from ai_assistant.modules.web_scraping import get_trending_topics
        
        platform = request.args.get('platform', 'general')
        
        result = get_trending_topics(platform)
        
        return jsonify({
            "success": True,
            "trending": result,
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Trending topics error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# TASKBAR DETECTION API ENDPOINTS
# ============================================================

@app.route('/api/taskbar/detect', methods=['GET'])
@jwt_required()
def api_detect_taskbar():
    """Detect and analyze taskbar applications"""
    try:
        from ai_assistant.modules.taskbar_detection import detect_taskbar_apps
        
        result = detect_taskbar_apps()
        
        return jsonify({
            "success": True,
            "taskbar_analysis": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Taskbar detection error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/taskbar/capabilities', methods=['GET'])
def api_taskbar_capabilities():
    """Check taskbar detection capabilities"""
    try:
        from ai_assistant.modules.taskbar_detection import can_see_taskbar
        
        result = can_see_taskbar()
        
        return jsonify({
            "success": True,
            "capabilities": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Taskbar capabilities check error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/taskbar/find-app', methods=['POST'])
@jwt_required()
def api_find_app_in_taskbar():
    """Find a specific application in taskbar"""
    try:
        from ai_assistant.modules.taskbar_detection import TaskbarDetector
        
        data = request.get_json()
        app_name = data.get('app_name')
        
        if not app_name:
            return jsonify({"success": False, "error": "App name required"}), 400
        
        detector = TaskbarDetector()
        result = detector.find_specific_app_in_taskbar(app_name)
        
        return jsonify({
            "success": True,
            "app_search_result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"App search error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/taskbar/running-apps', methods=['GET'])
@jwt_required()
def api_get_running_apps():
    """Get list of running applications"""
    try:
        from ai_assistant.modules.taskbar_detection import TaskbarDetector
        
        detector = TaskbarDetector()
        result = detector.get_running_applications()
        
        return jsonify({
            "success": True,
            "running_apps": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Running apps detection error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Enhanced Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "Not found",
        "message": "The requested resource was not found",
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    print(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred on the server",
        "timestamp": datetime.now().isoformat()
    }), 500

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({
        "error": "Bad request",
        "message": "The request was invalid or malformed",
        "timestamp": datetime.now().isoformat()
    }), 400

@app.errorhandler(503)
def service_unavailable_error(error):
    return jsonify({
        "error": "Service unavailable",
        "message": "The service is temporarily unavailable",
        "timestamp": datetime.now().isoformat()
    }), 503

# Define fallback functions for when automation tools are not available
if not AUTOMATION_AVAILABLE:
    def write_a_note(*args, **kwargs): return "Note taking not available"
    def open_application(app_name, *args, **kwargs): 
        try:
            # Try to use Intent Recognizer for app name normalization
            try:
                import sys
                import os
                # Add ai_assistant to path if not already there
                ai_assistant_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if ai_assistant_dir not in sys.path:
                    sys.path.insert(0, ai_assistant_dir)
                
                from ai_assistant.ai.intent_recognizer import IntentRecognizer
                recognizer = IntentRecognizer()
                
                # Normalize the app name to handle variations like "whats app" -> "whatsapp"
                normalized_app = recognizer.normalize_app_name(app_name)
                print(f"[Intent Recognizer] Normalized '{app_name}' -> '{normalized_app}'")
                app_name = normalized_app
            except Exception as intent_error:
                # If intent recognizer fails, continue with original app name
                print(f"[Intent Recognizer] Not available: {intent_error}")
            
            # Try subprocess first
            subprocess.Popen(app_name, shell=True)
            return f"Opened {app_name}"
        except Exception as e:
            # Fallback: Try Start menu automation with pyautogui
            try:
                import pyautogui
                import time
                pyautogui.hotkey('win', 'd')
                time.sleep(0.5)
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.write(app_name, interval=0.05)
                time.sleep(1)
                pyautogui.press('enter')
                return f"Tried to open '{app_name}' via Start menu."
            except Exception as e2:
                return f"Could not find '{app_name}' on your system. Try saying the full application name or check if it's installed."
    def search_google(*args, **kwargs): return "Google search not available"
    def search_youtube(*args, **kwargs): return "YouTube search not available"
    def close_application(*args, **kwargs): return "App closing not available"
    def speak(*args, **kwargs): return "Text-to-speech not available"
    def set_system_volume(*args, **kwargs): return "Volume control not available"
    def get_app_path_from_name(*args, **kwargs): return None
    def setup_memory(*args, **kwargs): return True
    def save_to_memory(*args, **kwargs): return True
    def get_memory(*args, **kwargs): return "Memory not available"
    def search_memory(*args, **kwargs): return "Memory search not available"
    def get_conversation_summary(*args, **kwargs): return "Conversation history not available"
    def save_knowledge(*args, **kwargs): return "Knowledge saving not available"
    def get_knowledge(*args, **kwargs): return "Knowledge retrieval not available"
    def discover_applications(*args, **kwargs): return "App discovery completed (fallback)"
    def smart_open_application(app_name, *args, **kwargs): return open_application(app_name)
    def list_installed_apps(*args, **kwargs): 
        return [
            {"name": "Notepad", "path": "notepad.exe"},
            {"name": "Calculator", "path": "calc.exe"},
            {"name": "Paint", "path": "mspaint.exe"}
        ]
    
    def get_apps_for_web(*args, **kwargs):
        return [
            {"name": "Chrome", "path": "chrome.exe", "category": "Browser", "usage": 89, "description": "Google Chrome web browser"},
            {"name": "Mail", "path": "mail.exe", "category": "Communication", "usage": 76, "description": "Email application"},
            {"name": "Documents", "path": "word.exe", "category": "Productivity", "usage": 65, "description": "Document editor"},
            {"name": "Photos", "path": "photos.exe", "category": "Media", "usage": 52, "description": "Photo viewer"},
            {"name": "Videos", "path": "vlc.exe", "category": "Media", "usage": 43, "description": "Video player"},
            {"name": "Code", "path": "code.exe", "category": "Development", "usage": 92, "description": "Code editor"},
            {"name": "Database", "path": "pgadmin.exe", "category": "Development", "usage": 67, "description": "Database administration"},
            {"name": "Terminal", "path": "cmd.exe", "category": "System Tools", "usage": 78, "description": "Command line interface"},
            {"name": "Calculator", "path": "calc.exe", "category": "System Tools", "usage": 45, "description": "Windows calculator"},
            {"name": "Notepad", "path": "notepad.exe", "category": "System Tools", "usage": 30, "description": "Simple text editor"},
            {"name": "Paint", "path": "mspaint.exe", "category": "System Tools", "usage": 25, "description": "Image editor"},
            {"name": "Control Panel", "path": "control.exe", "category": "System Tools", "usage": 20, "description": "System settings"},
            {"name": "Task Manager", "path": "taskmgr.exe", "category": "System Tools", "usage": 35, "description": "Process manager"}
        ]
    def get_system_status(*args, **kwargs): 
        if PSUTIL_AVAILABLE:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('C:\\' if os.name == 'nt' else '/').percent
            }
        return {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0}
    def get_running_processes(*args, **kwargs): return []
    def cleanup_temp_files(*args, **kwargs): return "Cleanup not available"
    def get_network_info(*args, **kwargs): return {"status": "unavailable"}
    def get_upcoming_events(*args, **kwargs): return []
    def get_inbox_summary(*args, **kwargs): return {"count": 0}
    def get_spotify_status(*args, **kwargs): return {"is_playing": False, "track_name": "Spotify not available", "artist_name": "N/A"}
    def spotify_play_pause(*args, **kwargs): return "Spotify control not available"
    def spotify_next_track(*args, **kwargs): return "Spotify control not available"
    def spotify_previous_track(*args, **kwargs): return "Spotify control not available"
    def search_and_play_spotify(*args, **kwargs): return "Spotify search not available"
    def get_weather_info(*args, **kwargs): return {"temperature": "22Â°C", "description": "Weather service not configured"}
    def get_latest_news(*args, **kwargs): return []
    def get_stock_price(*args, **kwargs): return "N/A"
    def detect_taskbar_apps(*args, **kwargs): return []
    def can_see_taskbar(*args, **kwargs): return False

# Initialize advanced voice processing systems
vad_detector = None
noise_reducer = None

if VAD_AVAILABLE:
    try:
        vad_detector = VoiceActivityDetector()
        logger.info("✅ Voice Activity Detector initialized")
    except Exception as e:
        logger.error(f"Failed to initialize VAD: {e}")

if NOISE_REDUCTION_AVAILABLE:
    try:
        noise_reducer = NoiseReductionSystem()
        logger.info("✅ Noise Reduction System initialized")
    except Exception as e:
        logger.error(f"Failed to initialize noise reduction: {e}")

# Register voice API blueprint if available (skip if already registered above)
if VOICE_API_AVAILABLE and 'voice_bp' in globals():
    try:
        # Check if already registered to avoid duplicate error
        if not any(bp.name == 'voice' for bp in app.blueprints.values()):
            app.register_blueprint(voice_bp, url_prefix='/api/voice')
            logger.info("✅ Voice API blueprint registered at /api/voice")
            logger.info(f"   - GET /api/voice/list (12 voices available)")
            logger.info(f"   - POST /api/voice/preview (voice preview generation)")
            logger.info(f"   - GET /api/voice/cache/stats (cache monitoring)")
        else:
            logger.info("✅ Voice API blueprint already registered (skipping duplicate)")
    except Exception as e:
        logger.error(f"Failed to register voice API blueprint: {e}")
else:
    if not VOICE_API_AVAILABLE:
        logger.warning("⚠️ Voice API blueprint not available")

# Register voice WebSocket handlers
if VOICE_WEBSOCKET_AVAILABLE:
    try:
        register_voice_handlers(socketio, assistant)
        logger.info("✅ Voice WebSocket handlers registered")
    except Exception as e:
        logger.error(f"Failed to register voice WebSocket handlers: {e}")
else:
    logger.warning("⚠️ Voice WebSocket handlers not available")

# ============================================================
# CHAT & VOICE INTEGRATION
# ============================================================

# Import and register Socket.IO handlers for chat and voice
try:
    # Define Socket.IO event handlers inline
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f'✅ Client connected: {request.sid}')
        socketio.emit('connection_established', {
            'status': 'connected',
            'sid': request.sid,
            'timestamp': datetime.now().isoformat()
        }, room=request.sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f'❌ Client disconnected: {request.sid}')

    @socketio.on('command')
    def handle_command(data):
        """Handle command from voice or chat input"""
        try:
            from ai_assistant.core.assistant import ModernAssistant
            
            command_text = data.get('command') or data.get('message', '')
            source = data.get('source', 'chat')
            
            if not command_text:
                emit('command_response', {
                    'success': False,
                    'error': 'No command provided',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            print(f'📨 Command received ({source}): {command_text}')
            print(f'   Using assistant: {type(handle_command.assistant).__name__ if hasattr(handle_command, "assistant") else "Not created yet"}')
            
            # Process command through assistant
            try:
                # Create assistant instance if needed
                if not hasattr(handle_command, 'assistant'):
                    handle_command.assistant = ModernAssistant()
                
                # Process the query
                response_text = handle_command.assistant.process_query(command_text)
                
                # Emit response
                emit('command_response', {
                    'success': True,
                    'response': response_text,
                    'command': command_text,
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f'✅ Response sent: {response_text[:100]}...')
                
                # Emit log update
                emit('log_update', {
                    'type': 'info',
                    'message': f'Processed {source} command: {command_text[:50]}...',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                
            except Exception as process_error:
                print(f'❌ Processing error: {process_error}')
                import traceback
                print(traceback.format_exc())
                
                # Fallback: Simple greeting responses
                cmd_lower = command_text.lower()
                if any(word in cmd_lower for word in ['hello', 'hi', 'hey']):
                    fallback_response = "👋 Hello! I'm your assistant. I can help you open apps, search the web, play music, and much more. What would you like me to do?"
                elif any(word in cmd_lower for word in ['how are you']):
                    fallback_response = "I'm doing great, thank you for asking! 😊 How can I help you today?"
                else:
                    fallback_response = f'I received: "{command_text}". Let me help you with that!'
                
                emit('command_response', {
                    'success': True,
                    'response': fallback_response,
                    'command': command_text,
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f'✅ Fallback response sent: {fallback_response[:100]}...')
                
        except Exception as e:
            print(f'❌ Command error: {e}')
            emit('command_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })

    # System stats broadcaster with caching
    _stats_cache = {'data': None, 'timestamp': 0}
    STATS_CACHE_DURATION = 2  # Cache for 2 seconds
    BROADCAST_INTERVAL = 3  # Broadcast every 3 seconds
    
    def get_cached_stats():
        """Get system stats with caching to reduce CPU usage"""
        current_time = time.time()
        if _stats_cache['data'] and (current_time - _stats_cache['timestamp']) < STATS_CACHE_DURATION:
            return _stats_cache['data']
        
        try:
            if PSUTIL_AVAILABLE:
                stats = assistant.get_real_time_system_stats()
                _stats_cache['data'] = stats
                _stats_cache['timestamp'] = current_time
                return stats
        except Exception as e:
            logger.error(f'Stats collection error: {e}', exc_info=True)
        return None
    
    def broadcast_system_stats():
        """Broadcast system statistics every 3 seconds with caching"""
        while True:
            try:
                stats = get_cached_stats()
                if stats:
                    # Only broadcast essential stats to reduce bandwidth
                    broadcast_stats = {
                        'cpu_usage': stats.get('cpu_usage', 0),
                        'memory_usage': stats.get('memory_usage', 0),
                        'disk_usage': stats.get('disk_usage', 0),
                        'network_speed': stats.get('network_mbps', 0)
                    }
                    socketio.emit('system_stats_update', broadcast_stats)
            except Exception as e:
                logger.error(f'Stats broadcast error: {e}')
            time.sleep(BROADCAST_INTERVAL)

    # Start stats broadcaster
    stats_thread = threading.Thread(target=broadcast_system_stats, daemon=True)
    stats_thread.start()
    
    # Register Vosk WebSocket handlers for offline recognition
    if VOSK_WS_AVAILABLE:
        try:
            register_vosk_handlers(socketio)
            logger.info("✅ Vosk WebSocket handlers registered (offline recognition enabled)")
        except Exception as e:
            logger.error(f"Failed to register Vosk handlers: {e}")
    
    logger.info("✅ Chat & Voice Socket.IO handlers registered")
    
except Exception as e:
    logger.error(f"Failed to register chat/voice handlers: {e}")


# ============================================================
# MULTI-AGENT ACTION CHAIN ROUTES
# ============================================================

@app.route('/api/chains/create', methods=['POST'])
@jwt_required()
def create_chain():
    """Create a new action chain from command"""
    if not MULTI_AGENT_AVAILABLE:
        return jsonify({"error": "Multi-Agent System not available"}), 503
        
    data = request.get_json()
    command = data.get("command")
    
    if not command:
        return jsonify({"error": "Command is required"}), 400
        
    try:
        import asyncio
        manager = get_chain_manager()
        
        # 1. Create Chain Synchronously (well, effectively) to get ID
        # We need to run the async create_chain method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        chain = loop.run_until_complete(manager.create_chain(command))
        
        # 2. Run execution in background
        def run_chain_background(chain_obj):
            async def _run():
                # Continue with Steps 2-7
                # Subscribe to progress
                manager.subscribe_progress(chain_obj.id, _broadcast_chain_progress)
                
                # Step 2: Process & Breakdown
                await manager.decompose_command(chain_obj)
                
                # Step 3: Identify
                await manager.identify_executors(chain_obj)
                
                # Step 4: Assign & Execute + Step 5: Track Progress
                report = await manager.execute_chain(chain_obj.id)
                
                # Step 7: Notify
                await manager.notify_completion(report)
                
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(_run())
            new_loop.close()
            
        thread = threading.Thread(target=run_chain_background, args=(chain,))
        thread.start()
        
        return jsonify({
            "status": "started", 
            "message": "Chain execution started",
            "chain_id": chain.id,
            "command": command
        })
        
    except Exception as e:
        logger.error(f"Chain creation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chains/<chain_id>/resume', methods=['POST'])
@jwt_required()
def resume_chain(chain_id):
    """Resume a paused chain with user input/confirmation"""
    if not MULTI_AGENT_AVAILABLE:
        return jsonify({"error": "Multi-Agent System not available"}), 503
        
    data = request.get_json()
    user_input = data.get("input")
    action = data.get("action", "proceed") # proceed, cancel, retry
    
    # Placeholder for resume logic
    # In future: manager.resume_chain(chain_id, action, user_input)
    return jsonify({"status": "resumed", "message": "Resume signal sent (Not fully implemented)"})


@app.route('/api/chains/<chain_id>', methods=['GET'])
@jwt_required()
def get_chain_status(chain_id):
    """Get status of an action chain"""
    if not MULTI_AGENT_AVAILABLE:
        return jsonify({"error": "Multi-Agent System not available"}), 503
        
    try:
        manager = get_chain_manager()
        chain = manager.get_chain(chain_id)
        
        if not chain:
            return jsonify({"error": "Chain not found"}), 404
            
        return jsonify(chain.to_dict())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chains/history', methods=['GET'])
@jwt_required()
def get_chain_history():
    """Get history of action chains"""
    if not MULTI_AGENT_AVAILABLE:
        return jsonify({"error": "Multi-Agent System not available"}), 503
        
    try:
        tracker = get_progress_tracker()
        history = tracker.get_recent_chains(limit=20)
        return jsonify({"chains": history})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# WebSocket Broadcaster for Chain Progress
def _broadcast_chain_progress(progress):
    """Broadcast chain progress via WebSocket"""
    try:
        socketio.emit(
            'chain_progress',
            progress.to_dict(),
            namespace='/'
        )
    except Exception as e:
        logger.error(f"WebSocket broadcast error: {e}")


@socketio.on('subscribe_chain')
def handle_chain_subscribe(data):
    """Subscribe to chain updates"""
    chain_id = data.get('chain_id')
    # In a full implementation, we would join a room specific to this chain
    # For now, progress is broadcast globally or we could filter
    emit('subscribed', {'chain_id': chain_id})


# ============================================================
# UNIFIED DASHBOARD ROUTES
# ============================================================

@app.route('/unified')
@app.route('/unified-dashboard')
def serve_unified_dashboard():
    """Serve the unified dashboard interface"""
    from flask import send_from_directory
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
    return send_from_directory(templates_dir, 'unified_dashboard.html')


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 YourDaddy Assistant - Modern Web Backend")
    print("=" * 60)
    print("🌐 Server starting on: http://localhost:5000")
    print("⚛️  Bolt.ai React UI (Monochrome Steel Design)")
    print("⚡ Real-time features enabled via WebSockets")
    print("🔧 API endpoints available at /api/*")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Bind to localhost only for security
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', 5000))
        
        print(f"ðŸ”’ Security: JWT authentication enabled")
        print(f"ðŸ”’ Security: Rate limiting enabled")
        print(f"ðŸ”’ Security: CORS restricted to: {', '.join(ALLOWED_ORIGINS)}")
        print(f"ðŸ”’ Security: Host binding: {host}")
        print("")
        print(f"âš ï¸  Default credentials: username='admin', password='{os.getenv('ADMIN_PASSWORD', 'changeme123')}'")
        print("âš ï¸  CHANGE THE PASSWORD in .env file before production!")
        print("")
        
        # Start app discovery schedulers (non-blocking)
        if AUTOMATION_AVAILABLE:
            # Start delayed refresh 30 seconds after server starts
            start_auto_refresh_after_startup(delay_seconds=30)
            # Start weekly periodic refresh
            start_periodic_refresh(interval_hours=168)  # 168 hours = 1 week
        
        # Start robust system monitoring
        try:
            from ai_assistant.services.backend.system_monitor import start_system_monitor
            start_system_monitor(socketio)
            print("✅ System monitoring started")
        except ImportError as e:
            print(f"⚠️ Could not start system monitoring: {e}")
        
        # Register Google Speech Recognition WebSocket handlers
        if GOOGLE_SPEECH_WS_AVAILABLE:
            try:
                register_google_speech_handlers(socketio)
                print("✅ Google Speech Recognition WebSocket handlers registered")
            except Exception as e:
                print(f"⚠️ Could not register Google Speech handlers: {e}")
        

        socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"âŒ Server failed to start: {e}")
        sys.exit(1)
