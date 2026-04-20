# YourDaddy Assistant Modules Package
"""
Modular architecture for YourDaddy AI Assistant

This package contains specialized modules for different functionality:
- core: Basic Windows automation and file operations
- memory: Enhanced memory and knowledge management
- system: System monitoring and maintenance
- calendar: Google Calendar integration
- email: Email management (future)
- media: Music/media control (future)
- web: Web scraping and online services (future)
- vision: Computer vision and OCR (future)
"""

from __future__ import annotations

import importlib
from typing import Any

__version__ = "3.0.0"
__author__ = "YourDaddy AI Assistant"

# NOTE:
# Keep this package init lightweight. Eager wildcard imports here can trigger
# heavy optional dependencies (music/web integrations) and break unrelated
# offline automation modules at import time.

_LAZY_ATTR_MODULES = {
    # Core automation helpers
    "open_application": "ai_assistant.modules.core",
    "close_application": "ai_assistant.modules.core",
    "search_google": "ai_assistant.modules.core",
    "search_youtube": "ai_assistant.modules.core",
    "open_settings_page": "ai_assistant.modules.core",
    "speak": "ai_assistant.modules.core",
    "set_system_volume": "ai_assistant.modules.core",
    "get_system_volume": "ai_assistant.modules.core",
    "volume_up": "ai_assistant.modules.core",
    "volume_down": "ai_assistant.modules.core",
    "mute_volume": "ai_assistant.modules.core",
    "unmute_volume": "ai_assistant.modules.core",

    # System helpers
    "get_system_status": "ai_assistant.modules.system",
    "get_running_processes": "ai_assistant.modules.system",
    "cleanup_temp_files": "ai_assistant.modules.system",
    "get_network_info": "ai_assistant.modules.system",
    "monitor_system_alerts": "ai_assistant.modules.system",
    "get_system_info": "ai_assistant.modules.system",
    "get_battery_status": "ai_assistant.modules.system",

    # File/web helpers used by automation workflows
    "organize_files_by_type": "ai_assistant.modules.file_ops",
    "get_weather_info": "ai_assistant.modules.web_scraping",
    "get_latest_news": "ai_assistant.modules.web_scraping",
}

_LAZY_SUBMODULES = {
    "core",
    "memory",
    "system",
    "google_calendar",
    "email_handler",
    "music",
    "file_ops",
    "web_scraping",
    "whatsapp",
    "offline_mode",
    "offline_llm_provider",
}


def __getattr__(name: str) -> Any:
    module_name = _LAZY_ATTR_MODULES.get(name)
    if module_name:
        module = importlib.import_module(module_name)
        value = getattr(module, name)
        globals()[name] = value
        return value

    if name in _LAZY_SUBMODULES:
        module = importlib.import_module(f"ai_assistant.modules.{name}")
        globals()[name] = module
        return module

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = sorted(list(_LAZY_ATTR_MODULES.keys()) + list(_LAZY_SUBMODULES))