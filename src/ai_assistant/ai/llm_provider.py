"""
Backward Compatibility Alias for llm_provider.py

This file was deprecated in favor of ai_assistant.modules.llm_provider.
It provides import aliases for backward compatibility.

DEPRECATED: Import from ai_assistant.modules.llm_provider instead.
This file will be removed in a future version.
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "ai_assistant.ai.llm_provider is deprecated. "
    "Import from ai_assistant.modules.llm_provider instead. "
    "This compatibility alias will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Import and re-export all public objects from the new location
from ai_assistant.modules.llm_provider import *
