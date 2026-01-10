"""
Services Package for ModernAssistant

Contains extracted service classes for better modularity:
- CommandProcessor: Command processing and multilingual support
- MonitoringService: System monitoring and statistics
"""

__all__ = ['CommandProcessor', 'MonitoringService']

try:
    from .command_processor import CommandProcessor
except ImportError:
    CommandProcessor = None

try:
    from .monitoring_service import MonitoringService
except ImportError:
    MonitoringService = None
