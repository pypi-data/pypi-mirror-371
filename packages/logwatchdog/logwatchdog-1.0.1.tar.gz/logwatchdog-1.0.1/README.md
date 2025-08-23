# LogWatchdog

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/logwatchdog.svg)](https://pypi.org/project/logwatchdog/)
[![GitHub](https://img.shields.io/badge/github-logwatchdog-green.svg)](https://github.com/pandiyarajk/logwatchdog)
[![Build Log Watchdog Executable](https://github.com/Pandiyarajk/logwatchdog/actions/workflows/build-exe.yml/badge.svg)](https://github.com/Pandiyarajk/logwatchdog/actions/workflows/build-exe.yml)

**LogWatchdog** is a production-ready Windows log monitoring solution that provides real-time monitoring, notifications, and automated log management capabilities.

## 🚀 Features

- **Real-time Log Monitoring**: Monitor single files, multiple files, or entire folders
- **Smart Notifications**: Email alerts and system tray notifications for critical events
- **Configurable Alerts**: Customizable exception keywords and notification rules
- **File Discovery**: Automatic detection of new log files
- **Windows Native**: Designed specifically for Windows 10/11 systems

## 📋 Requirements

- **Python 3.7+**
- **Windows 10/11** (primary target)

## 🛠️ Installation

### From PyPI (Recommended)

```bash
pip install logwatchdog
```

### From Source

```bash
git clone https://github.com/pandiyarajk/logwatchdog.git
cd logwatchdog
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Configuration Files

Create `log_config.ini` for monitoring settings:

```ini
[monitoring]
monitor_mode = folder                    # single, multiple, or folder
log_folder_path = C:\logs               # Folder to monitor
log_file_extensions = *.log,*.txt       # File extensions to monitor
file_discovery_interval = 30            # Check for new files every 30 seconds
empty_monitor_delay = 10                # Delay when no files found

[notifications]
email_enabled = true
smtp_server = smtp.gmail.com
smtp_port = 587
receiver_group = admin@company.com
system_tray_notifications = true

[alerts]
exception_keywords = Exception,Error,Failure,Fail,Fatal,Issue,Crash
```

### 2. Email Credentials

Create `.env` file for email authentication:

```bash
# Copy env_example.txt to .env and fill in your credentials
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

**Security Note**: Never commit the `.env` file to version control.

### 3. Start Monitoring

```bash
# Start monitoring with default settings
logwatchdog

# Or use the short command
lwd
```

## 📁 Monitoring Modes

- **Single File**: Monitor one specific log file
- **Multiple Files**: Monitor multiple specific log files simultaneously  
- **Folder**: Monitor all log files in a folder with automatic file detection

## 🔧 Configuration

### Main Settings (`log_config.ini`)

- Monitoring mode and file paths
- SMTP server configuration
- Alert keywords and notification settings
- File discovery intervals

### Email Credentials (`.env`)

- `EMAIL_USER`: Your email address
- `EMAIL_PASSWORD`: Your email password or app password

## 📚 Documentation

- **User Guide**: See the code comments and configuration examples
- **Issues**: [GitHub Issues](https://github.com/pandiyarajk/logwatchdog/issues)
- **Support**: pandiyarajk@live.com

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](https://github.com/pandiyarajk/logwatchdog/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/pandiyarajk/logwatchdog/blob/main/LICENSE) file for details.

## 🔄 Changelog

See [CHANGELOG.md](https://github.com/pandiyarajk/logwatchdog/blob/main/CHANGELOG.md) for version history.

---

**Made with ❤️ by [Pandiyaraj Karuppasamy](https://github.com/pandiyarajk)**

*LogWatchdog - Your Windows Log Monitoring Companion*
