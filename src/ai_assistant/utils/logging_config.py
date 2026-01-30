"""
Logging Configuration - Import Redirect
=======================================

This module redirects to the main logging_config in utils/
to prevent duplicate instances and session conflicts.

DO NOT MODIFY - import from utils.logging_config directly instead.
"""

# Import everything from main utils logging_config
from utils.logging_config import *

__all__ = [
    'SessionManager',
    'LoggingConfig', 
    'get_logger',
    'get_api_logger'
]
