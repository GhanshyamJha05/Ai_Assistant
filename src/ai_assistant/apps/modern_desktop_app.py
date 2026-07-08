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

def start_backend():
    print("Starting backend on port 5000 for Desktop App...")
    
    # LAZY IMPORT: Move heavy imports here so they don't block the UI window from opening!
    from ai_assistant.services.modern_web_backend import app, socketio, start_ai_background_thread
    
    # Fire off the background thread to load AI models while Flask starts serving the UI instantly
    start_ai_background_thread()
    
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
    loading_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loading YourDaddy AI...</title>
        <style>
            body { background: #16181D; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; font-family: sans-serif; }
            .loader { border: 4px solid rgba(255,255,255,0.1); border-left-color: #3B82F6; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 20px; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="loader"></div>
        <h2>Starting Web Server...</h2>
        <p style="color: #9CA3AF;">UI will appear instantly, AI modules will load in background.</p>
        <script>
            function checkServer() {
                fetch('http://127.0.0.1:5000/')
                    .then(r => {
                        if(r.ok) window.location.href = 'http://127.0.0.1:5000/';
                        else setTimeout(checkServer, 200);
                    })
                    .catch(e => setTimeout(checkServer, 200));
            }
            setTimeout(checkServer, 200);
        </script>
    </body>
    </html>
    """

    # We now serve the frontend via Flask on port 5000
    print("Opening native window with loading screen...")
    webview.create_window('YourDaddy AI Assistant', html=loading_html, width=1280, height=800, min_size=(800, 600))
    
    # Start the webview GUI loop FIRST, then run start_backend in a background thread.
    # This guarantees the window appears instantly (0 seconds) before heavy AI models block the GIL.
    webview.start(start_backend)

if __name__ == '__main__':
    main()
