"""
Configuration settings for the Multi-Agent Educational Platform
"""
import os
from pathlib import Path
from typing import Dict, Any

# Base paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Database configuration
OBJECTBOX_CONFIG = {
    "directory": str(DATA_DIR / "objectbox"),
    "max_db_size_in_kb": 1024 * 1024,  # 1GB
    "max_readers": 126,
}

# PocketFlow configuration
POCKETFLOW_CONFIG = {
    "max_retries": 3,
    "retry_delay": 1.0,
    "shared_store_size": 1024 * 1024,  # 1MB
}

# MCP configuration
MCP_CONFIG = {
    "timeout": 30.0,
    "max_connections": 10,
    "auth_providers": {},
}

# Analytics configuration
ANALYTICS_CONFIG = {
    "dashboard_refresh_interval": 5.0,  # seconds
    "vector_dimension": 384,
    "batch_size": 100,
}

# External API configuration
GOOGLE_CALENDAR_CONFIG = {
    "scopes": ["https://www.googleapis.com/auth/calendar"],
    "credentials_file": str(PROJECT_ROOT / "credentials" / "google_credentials.json"),
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "platform.log"),
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary"""
    return {
        "objectbox": OBJECTBOX_CONFIG,
        "pocketflow": POCKETFLOW_CONFIG,
        "mcp": MCP_CONFIG,
        "analytics": ANALYTICS_CONFIG,
        "google_calendar": GOOGLE_CALENDAR_CONFIG,
        "logging": LOGGING_CONFIG,
    }

def ensure_directories():
    """Ensure required directories exist"""
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    (PROJECT_ROOT / "credentials").mkdir(exist_ok=True)