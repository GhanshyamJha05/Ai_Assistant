"""
Backward Compatibility Alias for advanced_voice.py

This file was deprecated in favor of ai_assistant.voice.advanced_voice.
It provides import aliases for backward compatibility.

DEPRECATED: Import from ai_assistant.voice.advanced_voice instead.
This file will be removed in a future version.
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "ai_assistant.modules.advanced_voice is deprecated. "
    "Import from ai_assistant.voice.advanced_voice instead. "
    "This compatibility alias will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Import and re-export all public objects from the new location
from ai_assistant.voice.advanced_voice import *