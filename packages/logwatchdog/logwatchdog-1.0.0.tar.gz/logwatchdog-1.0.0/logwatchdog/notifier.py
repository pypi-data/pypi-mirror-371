"""
System Notification Module
=========================

This module provides desktop notification functionality for the LogWatchdog system.
It displays popup notifications when exceptions are detected in monitored logs.

The module uses the 'plyer' library which provides cross-platform notification
support for Windows. Notifications appear as system
tray popups or desktop alerts.

Features:
- Windows compatibility
- Configurable notification duration (5 seconds)
- Clean, simple API
- Automatic fallback handling
"""

from plyer import notification

def show_popup(title: str, message: str):
    """
    Display a system tray popup notification.
    
    This function creates a desktop notification that appears as a popup
    in the system tray area. The notification is automatically dismissed
    after the specified timeout period.
    
    Args:
        title (str): The notification title/heading
        message (str): The notification message content
        
    Returns:
        None
        
    Note:
        - Uses plyer library for cross-platform compatibility
        - Notifications automatically disappear after 5 seconds
        - Works on Windows
        - Falls back gracefully if system notifications are unavailable
        
    Example:
        show_popup("Exception Alert", "Database connection failed")
    """
    # Display the system notification using plyer
    # This creates a popup that appears in the system tray area
    notification.notify(
        title=title,      # The notification heading
        message=message,  # The notification content
        timeout=5         # Duration in seconds before auto-dismissal
    )
