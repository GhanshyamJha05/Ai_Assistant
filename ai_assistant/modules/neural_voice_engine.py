"""
Backward Compatibility Alias for neural_voice_engine.py

This file was deprecated in favor of ai_assistant.voice.neural_voice_engine.
It provides import aliases for backward compatibility.

DEPRECATED: Import from ai_assistant.voice.neural_voice_engine instead.
This file will be removed in a future version.
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "ai_assistant.modules.neural_voice_engine is deprecated. "
    "Import from ai_assistant.voice.neural_voice_engine instead. "
    "This compatibility alias will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Import and re-export all public objects from the new location
from ai_assistant.voice.neural_voice_engine import *
