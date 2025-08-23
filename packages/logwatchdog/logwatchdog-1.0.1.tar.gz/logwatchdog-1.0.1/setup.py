#!/usr/bin/env python3
"""
LogWatchdog - Windows Log Monitoring Solution
Setup script for package installation and distribution
"""

import os
import sys
from setuptools import setup, find_packages, find_namespace_packages
from pathlib import Path

# Read the README file for long description
def read_readme():
    """Read README.md file for long description."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "LogWatchdog - Windows Log Monitoring Solution"

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    requirements_path = Path(__file__).parent / "requirements.txt"
    if requirements_path.exists():
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

# Project metadata
PROJECT_NAME = "logwatchdog"
PROJECT_DESCRIPTION = "Comprehensive Windows log monitoring and management solution"
PROJECT_LONG_DESCRIPTION = read_readme()
PROJECT_AUTHOR = "Pandiyaraj Karuppasamy"
PROJECT_AUTHOR_EMAIL = "pandiyarajk@live.com"
PROJECT_URL = "https://github.com/pandiyarajk/logwatchdog"
PROJECT_DOWNLOAD_URL = "https://github.com/pandiyarajk/logwatchdog/releases"
PROJECT_LICENSE = "MIT"
PROJECT_CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Intended Audience :: Information Technology",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "Operating System :: Microsoft :: Windows :: Windows 11",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: System :: Logging",
    "Topic :: System :: Monitoring",
    "Topic :: System :: Networking :: Monitoring",
    "Topic :: Utilities",
    "Topic :: System :: Systems Administration",
    "Topic :: Security",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
]

# Package requirements
INSTALL_REQUIRES = read_requirements()
PYTHON_REQUIRES = ">=3.7"

# Development requirements
DEV_REQUIRES = [
    "pytest>=6.0.0",
    "pytest-cov>=2.10.0",
    "black>=21.0.0",
    "flake8>=3.8.0",
    "mypy>=0.800",
    "pre-commit>=2.15.0",
    "tox>=3.20.0",
    "sphinx>=4.0.0",
    "sphinx-rtd-theme>=0.5.0",
]

# Setup configuration
setup(
    name=PROJECT_NAME,
    version="1.0.1",
    description=PROJECT_DESCRIPTION,
    long_description=PROJECT_LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=PROJECT_AUTHOR,
    author_email=PROJECT_AUTHOR_EMAIL,
    url=PROJECT_URL,
    download_url=PROJECT_DOWNLOAD_URL,
    license=PROJECT_LICENSE,
    classifiers=PROJECT_CLASSIFIERS,
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "dev": DEV_REQUIRES,
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    packages=find_packages(include=["logwatchdog", "logwatchdog.*"]),
    include_package_data=True,
    package_data={
        "logwatchdog": [
            "*.ini",
            "*.yml",
            "*.yaml",
            "*.json",
            "*.txt",
            "*.md",
        ],
    },
    entry_points={
        "console_scripts": [
            "logwatchdog=logwatchdog.cli.main:main",
            "lwd=logwatchdog.cli.main:main",
        ],
    },
    keywords=[
        "log",
        "monitoring",
        "windows",
        "notifications",
        "alerts",
        "system-administration",
        "security",
        "auditing",
        "real-time",
        "watchdog",
        "monitoring-tool",
        "log-analysis",
        "event-logging",
        "system-monitoring",
    ],
    project_urls={
        "Bug Reports": f"{PROJECT_URL}/issues",
        "Source": PROJECT_URL,
        "Documentation": f"{PROJECT_URL}/blob/main/README.md",
        "Changelog": f"{PROJECT_URL}/blob/main/CHANGELOG.md",
        "Download": PROJECT_DOWNLOAD_URL,
    },
    zip_safe=False,
    platforms=["win32", "win_amd64"],
    requires_python=">=3.7",
)

if __name__ == "__main__":
    print(f"Setting up {PROJECT_NAME}...")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Requirements: {len(INSTALL_REQUIRES)} packages")
    
    # Check if running on Windows
    if not sys.platform.startswith("win"):
        print("Warning: This package is primarily designed for Windows systems.")
        print("Some features may not work correctly on other platforms.")
    
    print("Setup complete!")
