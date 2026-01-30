"""
YourDaddy AI Assistant - Complete Modular Backend

Main entry point for the modular backend system.
Replaces the monolithic modern_web_backend.py

Usage:
    python -m ai_assistant.services.backend.main
    
Or set as default backend by updating references in your startup scripts.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ai_assistant.services.backend.app import create_app, initialize_components
from ai_assistant.services.backend import routes, websocket

# Setup logging
from utils.logging_config import get_logger
logger = get_logger('backend_main', log_category='backend')


def main():
    """Main entry point"""
    try:
        logger.info("="*80)
        logger.info("🚀 YourDaddy AI Assistant - Complete Modular Backend")
        logger.info("="*80)
        
        # Create Flask app and SocketIO
        app, socketio = create_app()
        
        # Initialize components
        logger.info("🔧 Initializing components...")
        components = initialize_components()
        
        # =====================================================================
        # REGISTER EXISTING API BLUEPRINTS
        # =====================================================================
        logger.info("📡 Registering existing API blueprints...")
        
        # Voice API Blueprint (already well-organized)
        try:
            from ai_assistant.services.voice_api import voice_bp
            app.register_blueprint(voice_bp, url_prefix='/api/voice')
            logger.info("  ✅ Voice API blueprint registered")
        except ImportError as e:
            logger.warning(f"  ⚠️  Voice API blueprint not available: {e}")
        
        # App Integration API Blueprint  
        try:
            from ai_assistant.services.app_integration_api import create_app as create_integration_app
            # The app_integration_api creates its own app, we need to extract routes
            # For now, we'll note this needs integration
            logger.info("  ℹ️  App Integration API noted (needs route extraction)")
        except ImportError as e:
            logger.warning(f"  ⚠️  App Integration API not available: {e}")
        
        # Learning API Blueprint
        try:
            from ai_assistant.services.learning_api import learning_bp
            app.register_blueprint(learning_bp, url_prefix='/api/learning')
            logger.info("  ✅ Learning API blueprint registered")
        except ImportError as e:
            logger.warning(f"  ⚠️  Learning API blueprint not available: {e}")

        # Preferences / Settings API Blueprint
        try:
            from ai_assistant.services.backend.blueprints.preferences import create_blueprint as create_prefs_bp
            prefs_bp = create_prefs_bp()
            app.register_blueprint(prefs_bp)
            logger.info("  ✅ Preferences API blueprint registered")
        except ImportError as e:
            logger.warning(f"  ⚠️  Preferences API blueprint not available: {e}")
        
        # =====================================================================
        # REGISTER CORE ROUTES from modular backend
        # =====================================================================
        logger.info("📡 Registering core API routes...")
        routes.register_routes(app, components)
        
        # =====================================================================
        # REGISTER WEBSOCKET HANDLERS
        # =====================================================================
        logger.info("🔌 Registering WebSocket handlers...")
        websocket.register_handlers(socketio, components)
        
        # Try to register voice WebSocket handlers if available
        try:
            from ai_assistant.services.voice_websocket_handlers import register_voice_handlers
            register_voice_handlers(socketio)
            logger.info("  ✅ Voice WebSocket handlers registered")
        except ImportError:
            logger.info("  ℹ️  Voice WebSocket handlers not available (optional)")
        
        # Try to register chat/voice handlers
        try:
            from ai_assistant.services.chat_voice_handlers import register_chat_voice_handlers
            register_chat_voice_handlers(app, socketio, None)  # assistant will be initialized
            logger.info("  ✅ Chat/Voice handlers registered")
        except ImportError:
            logger.info("  ℹ️  Chat/Voice handlers not available (optional)")
        
        # =====================================================================
        # SECURITY & MIDDLEWARE
        # =====================================================================
        from ai_assistant.services.backend.middleware import add_security_headers
        
        @app.after_request
        def after_request(response):
            return add_security_headers(response)
        
        logger.info("🔒 Security headers middleware registered")
        
        # =====================================================================
        # CONFIGURATION & STARTUP
        # =====================================================================
        try:
            from ai_assistant.core.config_loader import get_config
            config = get_config()
            port = config.get('BACKEND_PORT', 5000)
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
            port = int(os.getenv('BACKEND_PORT', 5000))
        
        # =====================================================================
        # START BACKGROUND TASKS
        # =====================================================================
        try:
            from ai_assistant.services.backend.system_monitor import start_system_monitor
            start_system_monitor(socketio)
            logger.info("  📊 System monitoring task started")
        except ImportError as e:
            logger.warning(f"  ⚠️  Could not start system monitoring: {e}")
        
        # Start server
        logger.info("="*80)
        logger.info(f"✅ Backend initialization complete")
        logger.info(f"📊 Features loaded:")
        logger.info(f"   - Core routes: ✅")
        logger.info(f"   - Voice API: {'✅' if 'voice_bp' in locals() else '⚠️'}")
        logger.info(f"   - Learning API: {'✅' if 'learning_bp' in locals() else '⚠️'}")
        logger.info(f"   - WebSocket: ✅")
        logger.info(f"🌐 Starting server on http://0.0.0.0:{port}")
        logger.info("="*80)
        
        socketio.run(
            app,
            debug=False,
            host='0.0.0.0',
            port=port,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)



if __name__ == "__main__":
    main()
