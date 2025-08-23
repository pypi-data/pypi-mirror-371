"""
Log Monitor Module
==================

This module provides continuous monitoring of log files for exception detection.
It watches for specific keywords that indicate errors, exceptions, or issues
and triggers alerts via email and system tray notifications.

The monitor runs continuously, checking for new log entries and analyzing
them for exception-related keywords. When detected, it immediately sends
alerts to configured recipients.

Features:
- Real-time log file monitoring (single file, multiple files, or folder)
- Configurable exception keywords
- Automatic email alerts
- System tray notifications
- INI file-based configuration
- Support for multiple log file extensions
- Folder monitoring with file filtering
"""

import os
import time
import glob
import configparser
from pathlib import Path
from typing import List, Dict, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from .email_service import send_email
from .notifier import show_popup

def load_config():
    """Load configuration from log_config.ini file and environment variables for sensitive data."""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent.parent / "log_config.ini"
    
    if not config_path.exists():
        print(f"[WARNING] Configuration file not found: {config_path}")
        print("[INFO] Using default configuration values")
        return get_default_config()
    
    try:
        config.read(config_path)
        return config
    except Exception as e:
        print(f"[ERROR] Failed to read configuration file: {e}")
        print("[INFO] Using default configuration values")
        return get_default_config()

def load_env_credentials():
    """Load sensitive email credentials from environment file."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Read sensitive email credentials from environment
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    
    if not email_user or not email_password:
        print("[WARNING] Email credentials not found in environment file")
        print("[INFO] Please create a .env file with EMAIL_USER and EMAIL_PASSWORD")
        return "", ""
    
    return email_user, email_password

def get_default_config():
    """Return default configuration values."""
    config = configparser.ConfigParser()
    
    # Set default values
    config['monitoring'] = {
        'monitor_mode': 'single',
        'log_file_path': 'C:\\logs\\application.log',
        'log_files': 'C:\\logs\\app.log,C:\\logs\\application.log',
        'log_folder_path': 'C:\\logs',
        'log_file_extensions': '*.log,*.txt,*.evtx',
        'file_discovery_interval': '30',
        'empty_monitor_delay': '10'
    }
    
    config['notifications'] = {
        'email_enabled': 'true',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': '587',
        'receiver_group': 'admin@company.com,ops@company.com',
        'system_tray_notifications': 'true'
    }
    
    config['alerts'] = {
        'exception_keywords': 'Exception,Error,Failure,Fail,Fatal,Issue,Crash,Close,Cannot,Wrong,unsupported,not found,retry,terminated,disconnected'
    }
    
    return config

# Load configuration
config = load_config()

# Load sensitive email credentials from environment
EMAIL_USER, EMAIL_PASSWORD = load_env_credentials()

# Configuration constants loaded from INI file
MONITOR_MODE = config.get('monitoring', 'monitor_mode', fallback='single')
LOG_FILE_PATH = config.get('monitoring', 'log_file_path', fallback='')
LOG_FOLDER_PATH = config.get('monitoring', 'log_folder_path', fallback='')
LOG_FILE_EXTENSIONS = config.get('monitoring', 'log_file_extensions', fallback='*.log,*.txt,*.evtx').split(',')

# File discovery settings
FILE_DISCOVERY_INTERVAL = int(config.get('monitoring', 'file_discovery_interval', fallback='30'))
EMPTY_MONITOR_DELAY = int(config.get('monitoring', 'empty_monitor_delay', fallback='10'))

# Notification settings
EMAIL_ENABLED = config.get('notifications', 'email_enabled', fallback='true').lower() == 'true'
SMTP_SERVER = config.get('notifications', 'smtp_server', fallback='smtp.gmail.com')
SMTP_PORT = int(config.get('notifications', 'smtp_port', fallback='587'))
RECEIVER_GROUP = config.get('notifications', 'receiver_group', fallback='')
SYSTEM_TRAY_NOTIFICATIONS = config.get('notifications', 'system_tray_notifications', fallback='true').lower() == 'true'

# Comprehensive list of keywords that indicate exceptions, errors, or issues
# These keywords are case-insensitive and will trigger alerts when found in logs
EXCEPTION_KEYWORDS = config.get('alerts', 'exception_keywords', fallback='Exception,Error,Failure,Fail,Fatal,Issue,Crash,Close,Cannot,Wrong,unsupported,not found,retry,terminated,disconnected').split(',')

class LogFileHandler(FileSystemEventHandler):
    """
    File system event handler for monitoring log files in a folder.
    
    This class handles file creation, modification, and deletion events
    to automatically start/stop monitoring new log files.
    """
    
    def __init__(self, monitor_files: Dict[str, dict]):
        self.monitor_files = monitor_files
        self.observer = Observer()
        
    def on_created(self, event):
        """Handle new file creation events."""
        if not event.is_directory and self._is_log_file(event.src_path):
            self._add_file_to_monitoring(event.src_path)
            
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and event.src_path in self.monitor_files:
            # File was modified, this is handled by the file reader
            pass
            
    def on_deleted(self, event):
        """Handle file deletion events."""
        if event.src_path in self.monitor_files:
            self._remove_file_from_monitoring(event.src_path)
            
    def _is_log_file(self, file_path: str) -> bool:
        """Check if a file has a supported log extension."""
        return any(file_path.lower().endswith(ext.strip().lower()) for ext in LOG_FILE_EXTENSIONS)
        
    def _add_file_to_monitoring(self, file_path: str):
        """Add a new file to the monitoring list."""
        if file_path not in self.monitor_files:
            self.monitor_files[file_path] = {
                'position': 0,
                'last_modified': os.path.getmtime(file_path),
                'size': os.path.getsize(file_path)
            }
            print(f"[INFO] Added new log file to monitoring: {file_path}")
            
    def _remove_file_from_monitoring(self, file_path: str):
        """Remove a file from the monitoring list."""
        if file_path in self.monitor_files:
            del self.monitor_files[file_path]
            print(f"[INFO] Removed log file from monitoring: {file_path}")

def get_log_files() -> List[str]:
    """
    Get list of log files to monitor based on configuration.
    
    Returns:
        List of file paths to monitor
    """
    files = []
    
    if MONITOR_MODE == "single" and LOG_FILE_PATH:
        if os.path.exists(LOG_FILE_PATH):
            files.append(LOG_FILE_PATH)
        else:
            print(f"[WARNING] Single log file not found: {LOG_FILE_PATH}")
            
    elif MONITOR_MODE == "multiple" and LOG_FILE_PATH:
        # Support comma-separated list of files
        file_list = [f.strip() for f in LOG_FILE_PATH.split(",")]
        for file_path in file_list:
            if os.path.exists(file_path):
                files.append(file_path)
            else:
                print(f"[WARNING] Log file not found: {file_path}")
                
    elif MONITOR_MODE == "folder" and LOG_FOLDER_PATH:
        if os.path.exists(LOG_FOLDER_PATH) and os.path.isdir(LOG_FOLDER_PATH):
            # Find all files with supported extensions in the folder
            for extension in LOG_FILE_EXTENSIONS:
                pattern = os.path.join(LOG_FOLDER_PATH, extension.strip())
                files.extend(glob.glob(pattern))
            # Remove duplicates and sort
            files = sorted(list(set(files)))
        elif LOG_FILE_PATH == "":
            print("[WARNING] Log file not specified")
        elif LOG_FOLDER_PATH == "":
            print("[WARNING] Log folder not specified")
        else:
            print(f"[WARNING] Log folder not found: {LOG_FOLDER_PATH}")
            
    return files

def monitor_log():
    """
    Monitor log files for exceptions and send alerts.
    
    This function supports three monitoring modes:
    1. Single file monitoring (MONITOR_MODE=single)
    2. Multiple file monitoring (MONITOR_MODE=multiple)
    3. Folder monitoring (MONITOR_MODE=folder)
    
    When exceptions are detected, it triggers:
    1. Email alerts to configured recipients
    2. System tray popup notifications
    
    The function runs indefinitely until interrupted (Ctrl+C) and uses
    efficient file tailing to monitor only new log entries.
    
    Returns:
        None
        
    Raises:
        FileNotFoundError: If specified log files don't exist
        PermissionError: If log files cannot be read
        KeyboardInterrupt: When user stops the monitoring (Ctrl+C)
    """
    # Get list of files to monitor
    log_files = get_log_files()
    
    if not log_files:
        print("[ERROR] No log files found to monitor")
        print("[ERROR] Please check your configuration:")
        print(f"  - MONITOR_MODE: {MONITOR_MODE}")
        print(f"  - LOG_FILE_PATH: {LOG_FILE_PATH}")
        print(f"  - LOG_FOLDER_PATH: {LOG_FOLDER_PATH}")
        print(f"  - LOG_FILE_EXTENSIONS: {LOG_FILE_EXTENSIONS}")
        return

    print(f"[INFO] Monitoring mode: {MONITOR_MODE}")
    print(f"[INFO] Found {len(log_files)} log file(s) to monitor:")
    for file_path in log_files:
        print(f"  - {file_path}")
    print(f"[INFO] Watching for keywords: {', '.join(EXCEPTION_KEYWORDS)}")
    print(f"[DEBUG] Exception keywords (lowercase): {[kw.lower() for kw in EXCEPTION_KEYWORDS]}")

    # Initialize file monitoring state
    monitor_files = {}
    for file_path in log_files:
        try:
            monitor_files[file_path] = {
                'position': os.path.getsize(file_path),
                'last_modified': os.path.getmtime(file_path),
                'size': os.path.getsize(file_path)
            }
        except (OSError, PermissionError) as e:
            print(f"[WARNING] Cannot access file {file_path}: {e}")
            continue

    # Set up folder monitoring if in folder mode
    observer = None
    if MONITOR_MODE == "folder" and LOG_FOLDER_PATH:
        try:
            event_handler = LogFileHandler(monitor_files)
            observer = Observer()
            observer.schedule(event_handler, LOG_FOLDER_PATH, recursive=False)
            observer.start()
            print(f"[INFO] Started folder monitoring: {LOG_FOLDER_PATH}")
            print(f"[INFO] Watching for files with extensions: {', '.join(LOG_FILE_EXTENSIONS)}")
        except Exception as e:
            print(f"[WARNING] Could not start folder monitoring: {e}")
            print(f"[INFO] Will use periodic file discovery instead")

    try:
        # Continuous monitoring loop
        while True:
            if len(monitor_files) == 0:
                print("[INFO] No log files found to monitor")
                print(f"[INFO] Waiting {EMPTY_MONITOR_DELAY} seconds before checking for new files...")
                
                # Wait longer when no files are found, then check for new files
                time.sleep(EMPTY_MONITOR_DELAY)
                
                # Try to find new log files
                new_log_files = get_log_files()
                if new_log_files:
                    print(f"[INFO] Found {len(new_log_files)} new log file(s) to monitor")
                    # Initialize monitoring for new files
                    for file_path in new_log_files:
                        if file_path not in monitor_files:
                            try:
                                monitor_files[file_path] = {
                                    'position': os.path.getsize(file_path),
                                    'last_modified': os.path.getmtime(file_path),
                                    'size': os.path.getsize(file_path)
                                }
                                print(f"[INFO] Started monitoring new file: {file_path}")
                            except (OSError, PermissionError) as e:
                                print(f"[WARNING] Cannot access new file {file_path}: {e}")
                                continue
                else:
                    print("[INFO] Still no log files found, continuing to wait...")
                    continue
            
            # Check each monitored file for new content
            for file_path in list(monitor_files.keys()):
                try:
                    if not os.path.exists(file_path):
                        print(f"[WARNING] Log file no longer exists: {file_path}")
                        del monitor_files[file_path]
                        continue
                        
                    current_size = os.path.getsize(file_path)
                    current_modified = os.path.getmtime(file_path)
                    
                    # Debug: Log file size changes
                    if current_size != monitor_files[file_path]['size']:
                        print(f"[DEBUG] File {os.path.basename(file_path)} size changed: {monitor_files[file_path]['size']} -> {current_size}")
                    
                    # Check if file has new content
                    if current_size > monitor_files[file_path]['size']:
                        try:
                            # Read new content from the file
                            with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                                f.seek(monitor_files[file_path]['size'])
                                new_content = f.read()
                                
                            print(f"[DEBUG] Read {len(new_content)} bytes of new content from {os.path.basename(file_path)}")
                            
                            # Process new lines
                            new_lines = new_content.splitlines()
                            for line in new_lines:
                                if line.strip():  # Skip empty lines
                                    # Check for exception keywords (case-insensitive)
                                    line_lower = line.lower()
                                    for keyword in EXCEPTION_KEYWORDS:
                                        if keyword.lower() in line_lower:
                                            # Exception detected - log the alert
                                            print(f"[ALERT] Exception detected in {os.path.basename(file_path)}: {line.strip()}")
                                            print(f"[ALERT] File: {file_path}")
                                            print(f"[ALERT] Line content: {line.strip()}")
                                            print(f"[ALERT] Keyword matched: {keyword}")

                                            # Show system tray popup notification
                                            show_popup(
                                                f"Exception Alert - {os.path.basename(file_path)}", 
                                                line.strip()
                                            )

                                            # Send email alert to configured recipients
                                            if EMAIL_ENABLED:
                                                send_email(
                                                    subject=f"Exception Alert - {os.path.basename(file_path)}",
                                                    body=f"An exception was detected in log file {file_path}:\n\n{line}",
                                                    smtp_server=SMTP_SERVER,
                                                    smtp_port=SMTP_PORT,
                                                    email_user=EMAIL_USER,
                                                    email_password=EMAIL_PASSWORD,
                                                    receiver_group=RECEIVER_GROUP
                                                )
                                            break  # Only alert once per line
                            
                            # Update file monitoring state
                            monitor_files[file_path]['size'] = current_size
                            monitor_files[file_path]['last_modified'] = current_modified
                            
                        except Exception as e:
                            print(f"[ERROR] Error reading file {file_path}: {e}")
                            continue
                        
                except (OSError, PermissionError) as e:
                    print(f"[WARNING] Error accessing file {file_path}: {e}")
                    continue
                except Exception as e:
                    print(f"[ERROR] Unexpected error monitoring {file_path}: {e}")
                    continue
            
            # Brief pause between monitoring cycles
            time.sleep(1)
            
            # Periodically check for new files
            # This is especially useful for folder monitoring
            if time.time() % FILE_DISCOVERY_INTERVAL < 1:  # Check every FILE_DISCOVERY_INTERVAL seconds
                try:
                    new_log_files = get_log_files()
                    for file_path in new_log_files:
                        if file_path not in monitor_files:
                            try:
                                monitor_files[file_path] = {
                                    'position': os.path.getsize(file_path),
                                    'last_modified': os.path.getmtime(file_path),
                                    'size': os.path.getsize(file_path)
                                }
                                print(f"[INFO] Started monitoring new file: {file_path}")
                            except (OSError, PermissionError) as e:
                                print(f"[WARNING] Cannot access new file {file_path}: {e}")
                                continue
                except Exception as e:
                    print(f"[WARNING] Error checking for new files: {e}")
            
    except KeyboardInterrupt:
        # Handle graceful shutdown when user presses Ctrl+C
        print("\n[INFO] Monitoring stopped by user")
    except Exception as e:
        # Log any unexpected errors during monitoring
        print(f"[ERROR] Unexpected error during monitoring: {e}")
    finally:
        # Clean up folder monitoring
        if observer:
            observer.stop()
            observer.join()
            print("[INFO] Folder monitoring stopped")

def monitor_single_file(file_path: str):
    """
    Monitor a single log file (legacy function for backward compatibility).
    
    Args:
        file_path: Path to the log file to monitor
        
    Returns:
        None
    """
    global LOG_FILE_PATH
    original_path = LOG_FILE_PATH
    LOG_FILE_PATH = file_path
    monitor_log()
    LOG_FILE_PATH = original_path

if __name__ == "__main__":
    # Run the monitor when script is executed directly
    monitor_log()
