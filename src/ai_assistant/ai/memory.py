"""
Backward Compatibility Alias for memory.py

This file was deprecated in favor of ai_assistant.modules.memory.
It provides import aliases for backward compatibility.

DEPRECATED: Import from ai_assistant.modules.memory instead.
This file will be removed in a future version.
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "ai_assistant.ai.memory is deprecated. "
    "Import from ai_assistant.modules.memory instead. "
    "This compatibility alias will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Import and re-export all public objects from the new location
from ai_assistant.modules.memory import *
