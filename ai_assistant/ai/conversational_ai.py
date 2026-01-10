"""
Backward Compatibility Alias for conversational_ai.py

This file was deprecated in favor of ai_assistant.modules.conversational_ai.
It provides import aliases for backward compatibility.

DEPRECATED: Import from ai_assistant.modules.conversational_ai instead.
This file will be removed in a future version.
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "ai_assistant.ai.conversational_ai is deprecated. "
    "Import from ai_assistant.modules.conversational_ai instead. "
    "This compatibility alias will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Import and re-export all public objects from the new location
from ai_assistant.modules.conversational_ai import *
