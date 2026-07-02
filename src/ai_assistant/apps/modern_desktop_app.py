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
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from ai_assistant.services.modern_web_backend import app, socketio

def start_backend():
    print("Starting backend on port 5000 for Desktop App...")
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
    dist_path = project_root / "src" / "project" / "dist"
    
    if not dist_path.exists():
        print(f"Error: React build not found at {dist_path}")
        print("Please run 'npm install && npm run build' in src/project first.")
        url = "http://localhost:5173"
        print(f"Falling back to dev server: {url}")
        webview.create_window('YourDaddy AI Assistant', url, width=1280, height=800, min_size=(800, 600))
        webview.start()
    else:
        # pywebview can serve a local directory using its own HTTP server
        print(f"Serving UI from: {dist_path}")
        index_html = str(dist_path / "index.html")
        webview.create_window('YourDaddy AI Assistant', str(dist_path), width=1280, height=800, min_size=(800, 600))
        webview.start(http_server=True)

if __name__ == '__main__':
    main()
