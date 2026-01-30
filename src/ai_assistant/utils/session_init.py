"""
Session Initialization Module - Import Redirect
===============================================

DEPRECATED: This file redirects to utils/session_init
DO NOT modify - import from utils.session_init directly instead
"""

# Re-export everything from main session_init to maintain compatibility
from utils.session_init import *

# Explicitly re-export key items
from utils.session_init import (
    session_id,
    SESSION_START_TIME,
    CURRENT_SESSION_ID,
    get_session_info,
    log_module_initialization
)