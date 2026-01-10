"""
Backward Compatibility Alias for modern_web_backend.py

This file was deprecated in favor of ai_assistant.services.modern_web_backend.
It provides import aliases for backward compatibility.

DEPRECATED: Import from ai_assistant.services.modern_web_backend instead.
This file will be removed in a future version.
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "ai_assistant.apps.modern_web_backend is deprecated. "
    "Import from ai_assistant.services.modern_web_backend instead. "
    "This compatibility alias will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Import and re-export all public objects from the new location
from ai_assistant.services.modern_web_backend import *

__all__ = ['app', 'socketio', 'ModernAssistant', 'assistant']