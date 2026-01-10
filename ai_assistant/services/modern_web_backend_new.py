"""
YourDaddy AI Assistant - Streamlined Backend Entry Point

This replaces the monolithic modern_web_backend.py with a clean
entry point that uses the modular backend structure.

All business logic has been extracted to:
- backend/app.py - Flask app factory
- backend/routes.py - API routes
- backend/websocket.py - WebSocket handlers  
- backend/middleware.py - Auth, rate limiting
- backend/services/ - Business logic (to be created)
"""

import os
import sys
import logging
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    sys.stderr.reconfigure(encoding='utf-8') if hasattr(sys.stderr, 'reconfigure') else None

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = Path(current_dir).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Setup logging
from utils.logging_config import get_logger
logger = get_logger('backend_main', log_category='backend')

# Import modular backend
from ai_assistant.services.backend import create_app, initialize_components
from ai_assistant.services.backend import routes, websocket

def main():
    """Main entry point for the backend server"""
    
    logger.info("=" * 80)
    logger.info("YourDaddy AI Assistant - Starting Modular Backend")
    logger.info("=" * 80)
    
    # Create Flask app and SocketIO
    app, socketio = create_app()
    
    # Initialize components (AI, automation, etc.)
    components = initialize_components()
    
    # Register API routes
    routes.register_routes(app, components)
    logger.info("✅ API routes registered")
    
    # Register WebSocket handlers
    websocket.register_handlers(socketio, components)
    logger.info("✅ WebSocket handlers registered")
    
    # Import voice API blueprint if available
    try:
        from ai_assistant.services.voice_api import voice_bp
        app.register_blueprint(voice_bp, url_prefix='/api/voice')
        logger.info("✅ Voice API blueprint registered")
    except ImportError as e:
        logger.warning(f"Voice API not available: {e}")
    
    # Get port from environment
    port = int(os.getenv('BACKEND_PORT', 8000))
    host = os.getenv('BACKEND_HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info("=" * 80)
    logger.info(f"🚀 Server starting on {host}:{port}")
    logger.info(f"🌐 Access at: http://localhost:{port}")
    logger.info("=" * 80)
    
    # Run the server
    socketio.run(app, debug=debug, host=host, port=port)


# For backward compatibility - export app and socketio
app, socketio = create_app()
components = initialize_components()
routes.register_routes(app, components)
websocket.register_handlers(socketio, components)

# Export ModernAssistant for backward compatibility
try:
    # Import the assistant class if it exists elsewhere
    from ai_assistant.core.assistant import ModernAssistant
    assistant = ModernAssistant()
except ImportError:
    # If not, we'll need to create a simple placeholder
    logger.warning("ModernAssistant class not found - using minimal placeholder")
    class ModernAssistant:
        """Placeholder for backward compatibility"""
        pass
    assistant = ModernAssistant()


if __name__ == '__main__':
    main()
