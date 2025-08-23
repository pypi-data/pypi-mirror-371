"""
LogWatchdog CLI Main Entry Point
================================

This module provides the command-line interface for LogWatchdog.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import from logwatchdog
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from logwatchdog.log_monitor import monitor_log

def main():
    """Main CLI entry point."""
    try:
        print("[START] LogWatchdog - Windows Log Monitoring Solution")
        print("[INFO] Starting log monitoring...")
        print("[INFO] Press Ctrl+C to stop monitoring")
        monitor_log()
    except KeyboardInterrupt:
        print("\n[INFO] LogWatchdog stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] LogWatchdog failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
