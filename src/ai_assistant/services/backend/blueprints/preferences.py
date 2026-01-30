"""
User Preferences Blueprint

Handles user preferences and settings management.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

# In-memory storage (should use database in production)
user_preferences = {}

def create_blueprint(assistant):
    """Create and configure the user preferences blueprint"""
    bp = Blueprint('preferences', __name__, url_prefix='/api/user')
    
    @bp.route('/preferences', methods=['GET'])
    @jwt_required(optional=True)
    def get_preferences():
        """Get user preferences"""
        try:
            current_user = get_jwt_identity() or "default"
            prefs = user_preferences.get(current_user, {
                "theme": "dark",
                "language": "en",
                "voice_enabled": True,
                "notifications": True,
                "auto_listen": False
            })
            
            return jsonify({
                "preferences": prefs,
                "user": current_user,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Get preferences error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @bp.route('/preferences', methods=['POST'])
    @jwt_required(optional=True)
    def update_preferences():
        """Update user preferences"""
        try:
            current_user = get_jwt_identity() or "default"
            data = request.get_json()
            
            # Validate preferences
            valid_keys = ['theme', 'language', 'voice_enabled', 'notifications', 'auto_listen']
            preferences = {k: v for k, v in data.items() if k in valid_keys}
            
            # Store preferences
            if current_user not in user_preferences:
                user_preferences[current_user] = {}
            
            user_preferences[current_user].update(preferences)
            
            return jsonify({
                "success": True,
                "preferences": user_preferences[current_user],
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Update preferences error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @bp.route('/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        """Get user profile"""
        try:
            current_user = get_jwt_identity()
            profile = {
                "username": current_user,
                "role": "user",
                "created_at": "2024-01-01",
                "last_login": datetime.now().isoformat()
            }
            return jsonify(profile)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return bp
