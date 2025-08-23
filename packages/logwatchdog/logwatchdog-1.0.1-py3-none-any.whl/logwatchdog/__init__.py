"""
LogWatchdog - Windows Log Monitoring Solution
============================================

A comprehensive Windows log monitoring and management solution that provides
real-time monitoring, notifications, and automated log management capabilities.

Version: 1.0.1
Author: Pandiyaraj Karuppasamy
License: MIT
"""

__version__ = "1.0.1"
__author__ = "Pandiyaraj Karuppasamy"
__email__ = "pandiyarajk@live.com"
__license__ = "MIT"

# Import main components
from .log_monitor import monitor_log, monitor_single_file
from .email_service import send_email
from .notifier import show_popup
from .tray_notifier import show_notification

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "monitor_log",
    "monitor_single_file", 
    "send_email",
    "show_popup",
    "show_notification",
]
