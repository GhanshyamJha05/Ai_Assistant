"""
Session Activity Logger - Import Redirect
=========================================

This module redirects to the main session_activity_logger in utils/
to prevent duplicate instances.

DO NOT MODIFY - import from utils.session_activity_logger directly instead.
"""

# Import from main utils to ensure singleton behavior
from utils.session_activity_logger import (
    SessionActivityLogger,
    session_activity_logger,
    get_session_activity_logger,
    log_voice_command,
    log_file_operation,
    log_system_command,
    log_api_request,
    log_user_interaction,
    log_music_control,
    log_email_operation,
    log_calendar_operation,
    log_web_scraping,
    log_multimodal_ai,
    log_automation,
    end_session
)

__all__ = [
    'SessionActivityLogger',
    'session_activity_logger',
    'get_session_activity_logger',
    'log_voice_command',
    'log_file_operation',
    'log_system_command',
    'log_api_request',
    'log_user_interaction',
    'log_music_control',
    'log_email_operation',
    'log_calendar_operation',
    'log_web_scraping',
    'log_multimodal_ai',
    'log_automation',
    'end_session'
]
