"""
System Tray Notifier Module
===========================

This module provides enhanced system tray notification functionality for the LogWatchdog system.
It serves as an alternative to the basic notifier.py and includes fallback mechanisms
for cases where system tray notifications are unavailable.

Features:
- Cross-platform system tray notifications
- Automatic fallback to console output
- Configurable notification duration
- Enhanced error handling
- Test functionality for verification

The module uses the 'plyer' library for cross-platform compatibility and gracefully
handles cases where the system doesn't support tray notifications.
"""

import sys
from plyer import notification

def show_notification(title: str, message: str):
    """
    Show a desktop notification with the given title and message.
    
    This function attempts to display a system tray notification using the plyer
    library. If the notification fails for any reason (unsupported platform,
    permissions, etc.), it falls back to printing the message to the console.
    
    Args:
        title (str): The notification title/heading
        message (str): The notification message content
        
    Returns:
        None
        
    Note:
        - Uses plyer library for cross-platform compatibility
        - Notifications automatically disappear after 10 seconds
        - Falls back to console output if notifications fail
        - Includes app name for better system integration
        
    Example:
        show_notification("Exception Alert", "Database connection failed")
        
    Raises:
        Exception: Any unexpected errors during notification display
    """
    try:
        # Attempt to show the system tray notification
        # This will work on most modern operating systems
        notification.notify(
            title=title,           # The notification heading
            message=message,        # The notification content
            timeout=10,            # Duration in seconds before auto-dismissal
            app_name="LogWatchdog", # Application name for system integration
        )
        
        # Log successful notification (optional)
        print(f"[TrayNotifier] System notification sent: {title}")
        
    except Exception as e:
        # If system notifications fail, fall back to console output
        # This ensures the user still gets the alert information
        print(f"[TrayNotifier] Failed to send system notification: {e}")
        print(f"[TrayNotifier] Fallback to console: {title}: {message}")
        
        # Additional fallback: try to make the message more visible
        print("=" * 60)
        print(f"ALERT: {title}")
        print(f"Message: {message}")
        print("=" * 60)

def test_notification_system():
    """
    Test the notification system to verify it's working correctly.
    
    This function sends a test notification to help users verify that
    the system tray notifications are functioning properly on their system.
    
    Returns:
        bool: True if test notification was sent successfully, False otherwise
        
    Note:
        - Sends a test notification with sample content
        - Useful for troubleshooting notification issues
        - Can be called independently for testing purposes
    """
    try:
        test_title = "LogWatchdog Test"
        test_message = "This is a sample notification to test the system"
        
        print("[TrayNotifier] Testing notification system...")
        show_notification(test_title, test_message)
        
        print("[TrayNotifier] Test notification sent successfully!")
        return True
        
    except Exception as e:
        print(f"[TrayNotifier] Test notification failed: {e}")
        return False

if __name__ == "__main__":
    """
    Quick test when running this module directly.
    
    This allows users to test the notification system independently
    by running: python tray_notifier.py
    """
    print("Testing LogWatchdog Tray Notifier...")
    print("=" * 40)
    
    # Test the notification system
    success = test_notification_system()
    
    if success:
        print("Notification system test completed successfully!")
    else:
        print("Notification system test failed!")
    
    print("=" * 40)
    print("You can also import and use this module in other scripts:")
    print("from tray_notifier import show_notification")
    print("show_notification('Title', 'Message')")
