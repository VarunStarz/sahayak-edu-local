"""
Tests for configuration module
"""
import pytest
from pathlib import Path
from config import get_config, ensure_directories, PROJECT_ROOT


def test_get_config():
    """Test configuration retrieval"""
    config = get_config()
    
    assert "objectbox" in config
    assert "pocketflow" in config
    assert "mcp" in config
    assert "analytics" in config
    assert "google_calendar" in config
    assert "logging" in config


def test_ensure_directories():
    """Test directory creation"""
    ensure_directories()
    
    assert (PROJECT_ROOT / "data").exists()
    assert (PROJECT_ROOT / "logs").exists()
    assert (PROJECT_ROOT / "credentials").exists()


def test_objectbox_config():
    """Test ObjectBox configuration"""
    config = get_config()
    objectbox_config = config["objectbox"]
    
    assert "directory" in objectbox_config
    assert "max_db_size_in_kb" in objectbox_config
    assert "max_readers" in objectbox_config


def test_pocketflow_config():
    """Test PocketFlow configuration"""
    config = get_config()
    pocketflow_config = config["pocketflow"]
    
    assert "max_retries" in pocketflow_config
    assert "retry_delay" in pocketflow_config
    assert "shared_store_size" in pocketflow_config