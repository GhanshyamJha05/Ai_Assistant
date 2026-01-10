"""
Apps Blueprint

Handles application control, discovery, and automation endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_blueprint(assistant):
    """Create and configure the apps blueprint"""
    bp = Blueprint('apps', __name__, url_prefix='/api/apps')
    
    # Import automation functions
    try:
        from automation_tools_new import (
            open_application, close_application,
            smart_open_application
        )
        AUTOMATION_AVAILABLE = True
    except ImportError:
        AUTOMATION_AVAILABLE = False
        open_application = lambda x: f"Would open: {x}"
        close_application = lambda x: f"Would close: {x}"
        smart_open_application = lambda x: f"Would open: {x}"
    
    try:
        from ai_assistant.modules.app_discovery import get_installed_apps, refresh_app_list
        APP_DISCOVERY_AVAILABLE = True
    except ImportError:
        APP_DISCOVERY_AVAILABLE = False
        get_installed_apps = lambda: []
        refresh_app_list = lambda: []
    
    @bp.route('', methods=['GET'])
    def list_apps():
        """List all installed applications"""
        try:
            if not APP_DISCOVERY_AVAILABLE:
                return jsonify({
                    "apps": [],
                    "message": "App discovery not available"
                })
            
            apps = get_installed_apps()
            return jsonify({
                "apps": apps,
                "count": len(apps),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"List apps error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @bp.route('/refresh', methods=['POST'])
    def refresh_apps():
        """Refresh application list"""
        try:
            if not APP_DISCOVERY_AVAILABLE:
                return jsonify({"error": "App discovery not available"}), 503
            
            apps = refresh_app_list()
            return jsonify({
                "success": True,
                "apps": apps,
                "count": len(apps),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Refresh apps error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @bp.route('/launch', methods=['POST'])
    def launch_app():
        """Launch an application"""
        try:
            data = request.get_json()
            app_name = data.get('app_name', '')
            
            if not app_name:
                return jsonify({"error": "No app name provided"}), 400
            
            if not AUTOMATION_AVAILABLE:
                return jsonify({"error": "Automation not available"}), 503
            
            result = smart_open_application(app_name)
            
            return jsonify({
                "success": True,
                "app": app_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Launch app error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @bp.route('/close', methods=['POST'])
    def close_app():
        """Close an application"""
        try:
            data = request.get_json()
            app_name = data.get('app_name', '')
            
            if not app_name:
                return jsonify({"error": "No app name provided"}), 400
            
            if not AUTOMATION_AVAILABLE:
                return jsonify({"error": "Automation not available"}), 503
            
            result = close_application(app_name)
            
            return jsonify({
                "success": True,
                "app": app_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Close app error: {e}")
            return jsonify({"error": str(e)}), 500
    
    return bp
