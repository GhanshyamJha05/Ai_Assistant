"""
YourDaddy AI Assistant - Standalone Backup Backend

A simplified, working backend that can be used while refactoring the main one.
This avoids the duplicate endpoint error and provides a clean starting point.

Usage:
    python -m ai_assistant.services.backend_simple
"""

import os
import sys
import secrets
import logging
from pathlib import Path
from datetime import timedelta
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Load environment
load_dotenv()

# Add ai_assistant to path
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_assistant_dir = os.path.dirname(current_dir)
if ai_assistant_dir not in sys.path:
    sys.path.append(ai_assistant_dir)

# Setup logging
from utils.logging_config import get_logger
logger = get_logger('backend_simple', log_category='backend')

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)

# CORS
allowed_origins = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:5000,http://127.0.0.1:3000,'
    'http://127.0.0.1:5000,http://localhost:5173,http://127.0.0.1:5173'
).split(',')

CORS(app, resources={
    r"/api/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://"
)

# SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins=allowed_origins,
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)

logger.info("="*80)
logger.info("YourDaddy Assistant - Simple Backend")
logger.info("="*80)

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/ping', methods=['GET'])
def ping():
    """Health check"""
    return jsonify({"status": "ok", "message": "Backend is running"})


@app.route('/api/status', methods=['GET'])
def status():
    """System status"""
    return jsonify({
        "success": True,
        "backend": "simple",
        "version": "1.0.0"
    })


# PIN Authentication Routes
@app.route('/api/auth/verify-pin', methods=['POST'])
@limiter.limit("10 per minute")
def verify_pin():
    """Verify PIN"""
    try:
        from ai_assistant.auth.pin_auth import PINAuth
        
        data = request.get_json()
        pin = data.get('pin', '')
        
        auth = PINAuth()
        if auth.verify_pin(pin):
            return jsonify({"success": True, "message": "PIN verified"})
        else:
            return jsonify({"success": False, "error": "Invalid PIN"}), 401
            
    except Exception as e:
        logger.error(f"PIN verification error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/auth/setup-pin', methods=['POST'])
@limiter.limit("5 per hour")
def setup_pin():
    """Setup PIN"""
    try:
        from ai_assistant.auth.pin_auth import PINAuth
        
        data = request.get_json()
        pin = data.get('pin', '')
        
        if len(pin) < 4:
            return jsonify({"success": False, "error": "PIN must be at least 4 characters"}), 400
        
        auth = PINAuth()
        if auth.setup_pin(pin):
            return jsonify({"success": True, "message": "PIN setup successful"})
        else:
            return jsonify({"success": False, "error": "PIN setup failed"}), 500
            
    except Exception as e:
        logger.error(f"PIN setup error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/auth/is-configured', methods=['GET'])
def is_pin_configured():
    """Check if PIN is configured"""
    try:
        from ai_assistant.auth.pin_auth import PINAuth
        
        auth = PINAuth()
        configured = auth.is_pin_configured()
        
        return jsonify({"success": True, "configured": configured})
        
    except Exception as e:
        logger.error(f"PIN check error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Chat / Conversation Route
@app.route('/api/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    """Process chat message"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400
        
        # Simple echo response for now
        # TODO: Integrate actual AI processing
        response = f"Received: {message}"
        
        return jsonify({
            "success": True,
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Apps Routes
@app.route('/api/apps/list', methods=['GET'])
@limiter.limit("20 per minute")
def list_apps():
    """List installed applications"""
    try:
        from automation_tools_new import list_installed_apps
        
        apps = list_installed_apps()
        return jsonify({"success": True, "apps": apps})
        
    except Exception as e:
        logger.error(f"List apps error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/apps/launch', methods=['POST'])
@limiter.limit("10 per minute")
def launch_app():
    """Launch an application"""
    try:
        from automation_tools_new import smart_open_application
        
        data = request.get_json()
        app_name = data.get('name', '')
        
        if not app_name:
            return jsonify({"success": False, "error": "App name is required"}), 400
        
        result = smart_open_application(app_name)
        
        return jsonify({
            "success": True,
            "message": result
        })
        
    except Exception as e:
        logger.error(f"Launch app error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Voice Routes
@app.route('/api/voice/available', methods=['GET'])
def voice_available():
    """Check if voice is available"""
    try:
        import speech_recognition as sr
        return jsonify({"success": True, "available": True})
    except ImportError:
        return jsonify({"success": True, "available": False})


# ============================================================================
# WEBSOCKET HANDLERS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'ok'})


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat message via WebSocket"""
    try:
        message = data.get('message', '')
        logger.info(f"Chat message: {message}")
        
        # Echo response
        emit('chat_response', {
            'response': f"Received: {message}",
            'timestamp': str(timedelta())
        })
        
    except Exception as e:
        logger.error(f"WebSocket chat error: {e}")
        emit('error', {'error': str(e)})


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv('BACKEND_PORT', 5001))  # Different port to avoid conflict
    
    logger.info(f"🚀 Starting simple backend on port {port}")
    logger.info(f"📡 CORS allowed origins: {allowed_origins}")
    logger.info("="*80)
    
    socketio.run(
        app,
        debug=False,
        host='0.0.0.0',
        port=port,
        allow_unsafe_werkzeug=True
    )
