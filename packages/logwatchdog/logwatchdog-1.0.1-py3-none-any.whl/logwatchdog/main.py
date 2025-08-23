"""
LogWatchdog - Main Entry Point
==============================

This module serves as the main entry point for the LogWatchdog application.
It initializes the log monitoring system and starts monitoring for exceptions
in specified log files.

The application provides real-time monitoring of log files with automatic
alerting via email and system tray notifications when exceptions are detected.
"""

from .log_monitor import monitor_log

if __name__ == "__main__":
    # Display startup message to indicate monitoring has begun
    print("[START] Monitoring logs for exceptions...")
    print("[INFO] Press Ctrl+C to stop monitoring")
    
    # Start the continuous log monitoring process
    # This function runs indefinitely until interrupted
    monitor_log()
