"""
System Blueprint

Handles system status, monitoring, and diagnostics endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime

def create_blueprint(assistant):
    """Create and configure the system blueprint"""
    bp = Blueprint('system', __name__, url_prefix='/api')
    
    # Import feature flags
    from ai_assistant.services.modern_web_backend import (
        AUTOMATION_AVAILABLE, MULTIMODAL_AVAILABLE,
        CONVERSATIONAL_AI_AVAILABLE, VOICE_AVAILABLE,
        PSUTIL_AVAILABLE
    )
    
    @bp.route('/status')
    def status():
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
                "learning_systems": learning_systems_available
            }
        })
    
    @bp.route('/status/initialization', methods=['GET'])
    def initialization_status():
        """Get assistant initialization status"""
        try:
            status = assistant.get_init_status()
            return jsonify({
                "status": status,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @bp.route('/startup/sequence', methods=['GET'])
    def startup_sequence():
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
            return jsonify({
                "success": False,
                "error": "Failed to generate startup sequence",
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @bp.route('/startup/diagnostics', methods=['GET'])
    def startup_diagnostics():
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
            return jsonify({
                "success": False,
                "error": "Failed to get system diagnostics",
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @bp.route('/startup/briefing', methods=['GET'])
    def startup_briefing():
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
            return jsonify({
                "success": False,
                "error": "Failed to get contextual briefing",
                "timestamp": datetime.now().isoformat()
            }), 500
    
    return bp
