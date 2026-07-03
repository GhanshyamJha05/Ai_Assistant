import sys
import os
import threading
import logging
import time
from pathlib import Path

try:
    import webview
except ImportError:
    print("pywebview is required. Please 'pip install pywebview'")
    sys.exit(1)

# Ensure path is correct
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent.parent.parent.parent
    return base_path / relative_path

project_root = get_resource_path("")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from ai_assistant.services.modern_web_backend import app, socketio

def start_backend():
    print("Starting backend on port 5000 for Desktop App...")
    
    try:
        from ai_assistant.services.backend.system_monitor import start_system_monitor
        start_system_monitor(socketio)
    except Exception as e:
        pass
        
    try:
        from ai_assistant.services.modern_web_backend import GOOGLE_SPEECH_WS_AVAILABLE, register_google_speech_handlers
        if GOOGLE_SPEECH_WS_AVAILABLE:
            register_google_speech_handlers(socketio)
    except Exception as e:
        pass
        
    try:
        import ai_assistant.services.chat_voice_handlers_new as chat_handlers
        from ai_assistant.services.modern_web_backend import learning_router
        chat_handlers.set_socketio(socketio)
        chat_handlers.set_learning_router(learning_router)
    except Exception as e:
        print(f"⚠️ Could not register command handlers: {e}")

    # React app expects port 5000 based on its hardcoded fetches
    # allow_unsafe_werkzeug might be needed if running in a thread with certain configurations
    socketio.run(app, host='127.0.0.1', port=5000, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)

def main():
    # Start the Flask backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for the backend to initialize
    time.sleep(2)

    # Path to the compiled React app
    dist_path = get_resource_path("src/web_assets")
    
    if not dist_path.exists():
        print(f"Error: React build not found at {dist_path}")
        print("Please run 'npm install && npm run build' in src/project first.")
        url = "http://localhost:5173"
        print(f"Falling back to dev server: {url}")
        webview.create_window('YourDaddy AI Assistant', url, width=1280, height=800, min_size=(800, 600))
        webview.start()
    else:
        # We now serve the frontend via Flask on port 5000
        print(f"Serving UI from Flask on port 5000 (from {dist_path})")
        webview.create_window('YourDaddy AI Assistant', 'http://127.0.0.1:5000', width=1280, height=800, min_size=(800, 600))
        webview.start()

if __name__ == '__main__':
    main()
