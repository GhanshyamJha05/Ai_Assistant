#!/usr/bin/env python3
"""
Proxy launcher to run the web backend from the repository root.
This allows running `python modern_web_backend.py` as before,
even though the source code has been moved to `src/`.
"""
import runpy
import sys
import os

# Add src directory to path to allow importing ai_assistant
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

if __name__ == "__main__":
    print("🚀 Starting YourDaddy AI Assistant Web Backend...")
    try:
        # Run the module as a script
        runpy.run_module('ai_assistant.services.modern_web_backend', run_name='__main__')
    except ImportError as e:
        print(f"❌ Error starting backend: {e}")
        print(f"Title: Dependency Issue")
        print("Please ensure you have installed the requirements:")
        print("  pip install -r config/requirements/requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
