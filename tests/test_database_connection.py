"""
Unit tests for ObjectBox database connection and store management.

Tests cover:
- Database configuration
- ObjectBox Store initialization and management
- Connection health checks and statistics
- Transaction management
- Error handling and recovery
"""

import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.database.connection import (
    DatabaseConfig, ObjectBoxManager, initialize_database, get_database,
    close_database, database_transaction, DatabaseHealthCheck,
    ensure_database_initialized, reset_database, db_manager
)


class TestDatabaseConfig:
    """Test cases for DatabaseConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DatabaseConfig()
        
        assert config.db_path == "data/objectbox"
        assert config.max_db_size_in_kb == 1024 * 1024  # 1GB
        assert config.max_readers == 126
        assert config.debug_flags == 0
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = DatabaseConfig(
            db_path="/tmp/test_db",
            max_db_size_in_kb=512 * 1024,  # 512MB
            max_readers=64,
            debug_flags=1
        )
        
        assert config.db_path == "/tmp/test_db"
        assert config.max_db_size_in_kb == 512 * 1024
        assert config.max_readers == 64
        assert config.debug_flags == 1
    
    def test_to_dict(self):
        """Test configuration conversion to dictionary."""
        config = DatabaseConfig(
            db_path="/tmp/test",
            max_db_size_in_kb=1024,
            max_readers=32,
            debug_flags=2
        )
        
        config_dict = config.to_dict()
        expected = {
            "directory": "/tmp/test",
            "max_db_size_in_kb": 1024,
            "max_readers": 32,
            "debug_flags": 2
        }
        
        assert config_dict == expected


class TestObjectBoxManager:
    """Test cases for ObjectBoxManager singleton."""
    
    def setup_method(self):
        """Reset manager state before each test."""
        # Reset singleton state
        ObjectBoxManager._instance = None
        ObjectBoxManager._store = None
        ObjectBoxManager._model = None
    
    def teardown_method(self):
        """Cleanup after each test."""
        try:
            db_manager.close()
        except:
            pass
        ObjectBoxManager._instance = None
        ObjectBoxManager._store = None
        ObjectBoxManager._model = None
    
    def test_singleton_pattern(self):
        """Test that ObjectBoxManager follows singleton pattern."""
        manager1 = ObjectBoxManager()
        manager2 = ObjectBoxManager()
        
        assert manager1 is manager2
        assert id(manager1) == id(manager2)
    
    @patch('src.database.connection.Store')
    @patch('src.database.connection.Builder')
    @patch('os.makedirs')
    def test_initialize_success(self, mock_makedirs, mock_builder, mock_store):
        """Test successful database initialization."""
        # Setup mocks
        mock_model = MagicMock()
        mock_builder_instance = MagicMock()
        mock_builder_instance.model.return_value = mock_model
        mock_builder.return_value = mock_builder_instance
        
        mock_store_instance = MagicMock()
        mock_store.return_value = mock_store_instance
        
        # Test initialization
        manager = ObjectBoxManager()
        config = DatabaseConfig(db_path="/tmp/test_db")
        
        store = manager.initialize(config)
        
        # Verify calls
        mock_makedirs.assert_called_once_with("/tmp/test_db", exist_ok=True)
        mock_builder.assert_called_once()
        mock_store.assert_called_once()
        
        assert store == mock_store_instance
        assert manager.is_initialized()
        assert manager.get_config() == config
    
    @patch('src.database.connection.Store')
    @patch('src.database.connection.Builder')
    def test_initialize_failure(self, mock_builder, mock_store):
        """Test database initialization failure."""
        # Setup mock to raise exception
        mock_store.side_effect = Exception("Store creation failed")
        
        manager = ObjectBoxManager()
        
        with pytest.raises(RuntimeError, match="Database initialization failed"):
            manager.initialize()
        
        assert not manager.is_initialized()
    
    @patch('src.database.connection.Store')
    @patch('src.database.connection.Builder')
    @patch('os.makedirs')
    def test_get_store_success(self, mock_makedirs, mock_builder, mock_store):
        """Test getting initialized store."""
        mock_store_instance = MagicMock()
        mock_store.return_value = mock_store_instance
        
        manager = ObjectBoxManager()
        manager.initialize()
        
        store = manager.get_store()
        assert store == mock_store_instance
    
    def test_get_store_not_initialized(self):
        """Test getting store when not initialized."""
        manager = ObjectBoxManager()
        
        with pytest.raises(RuntimeError, match="ObjectBox Store not initialized"):
            manager.get_store()
    
    @patch('src.database.connection.Store')
    @patch('src.database.connection.Builder')
    @patch('os.makedirs')
    def test_close_store(self, mock_makedirs, mock_builder, mock_store):
        """Test closing the store."""
        mock_store_instance = MagicMock()
        mock_store.return_value = mock_store_instance
        
        manager = ObjectBoxManager()
        manager.initialize()
        
        assert manager.is_initialized()
        
        manager.close()
        
        mock_store_instance.close.assert_called_once()
        assert not manager.is_initialized()
    
    @patch('src.database.connection.Store')
    @patch('src.database.connection.Builder')
    @patch('os.makedirs')
    def test_close_store_with_error(self, mock_makedirs, mock_builder, mock_store):
        """Test closing store with error."""
        mock_store_instance = MagicMock()
        mock_store_instance.close.side_effect = Exception("Close failed")
        mock_store.return_value = mock_store_instance
        
        manager = ObjectBoxManager()
        manager.initialize()
        
        # Should not raise exception
        manager.close()
        
        assert not manager.is_initialized()


class TestDatabaseFunctions:
    """Test cases for database utility functions."""
    
    def setup_method(self):
        """Reset state before each test."""
        ObjectBoxManager._instance = None
        ObjectBoxManager._store = None
        ObjectBoxManager._model = None
    
    def teardown_method(self):
        """Cleanup after each test."""
        try:
            close_database()
        except:
            pass
        ObjectBoxManager._instance = None
        ObjectBoxManager._store = None
        ObjectBoxManager._model = None
    
    @patch('src.database.connection.ObjectBoxManager.initialize')
    def test_initialize_database(self, mock_initialize):
        """Test initialize_database function."""
        mock_store = MagicMock()
        mock_initialize.return_value = mock_store
        
        config = DatabaseConfig()
        result = initialize_database(config)
        
        mock_initialize.assert_called_once_with(config)
        assert result == mock_store
    
    @patch('src.database.connection.ObjectBoxManager.get_store')
    def test_get_database(self, mock_get_store):
        """Test get_database function."""
        mock_store = MagicMock()
        mock_get_store.return_value = mock_store
        
        result = get_database()
        
        mock_get_store.assert_called_once()
        assert result == mock_store
    
    @patch('src.database.connection.ObjectBoxManager.close')
    def test_close_database(self, mock_close):
        """Test close_database function."""
        close_database()
        mock_close.assert_called_once()
    
    @patch('src.database.connection.get_database')
    def test_database_transaction_success(self, mock_get_database):
        """Test successful database transaction."""
        mock_store = MagicMock()
        mock_get_database.return_value = mock_store
        
        with database_transaction() as store:
            assert store == mock_store
            # Simulate some operation
            store.some_operation()
        
        mock_store.some_operation.assert_called_once()
    
    @patch('src.database.connection.get_database')
    def test_database_transaction_failure(self, mock_get_database):
        """Test database transaction with exception."""
        mock_store = MagicMock()
        mock_get_database.return_value = mock_store
        
        with pytest.raises(ValueError, match="Test error"):
            with database_transaction():
                raise ValueError("Test error")
    
    @patch('src.database.connection.ObjectBoxManager.is_initialized')
    @patch('src.database.connection.initialize_database')
    def test_ensure_database_initialized_not_initialized(self, mock_initialize, mock_is_initialized):
        """Test ensure_database_initialized when not initialized."""
        mock_is_initialized.return_value = False
        
        config = DatabaseConfig()
        ensure_database_initialized(config)
        
        mock_initialize.assert_called_once_with(config)
    
    @patch('src.database.connection.ObjectBoxManager.is_initialized')
    @patch('src.database.connection.initialize_database')
    def test_ensure_database_initialized_already_initialized(self, mock_initialize, mock_is_initialized):
        """Test ensure_database_initialized when already initialized."""
        mock_is_initialized.return_value = True
        
        ensure_database_initialized()
        
        mock_initialize.assert_not_called()
    
    @patch('src.database.connection.close_database')
    @patch('src.database.connection.initialize_database')
    def test_reset_database(self, mock_initialize, mock_close):
        """Test reset_database function."""
        config = DatabaseConfig()
        reset_database(config)
        
        mock_close.assert_called_once()
        mock_initialize.assert_called_once_with(config)


class TestDatabaseHealthCheck:
    """Test cases for DatabaseHealthCheck utility."""
    
    @patch('src.database.connection.get_database')
    def test_check_connection_healthy(self, mock_get_database):
        """Test healthy database connection check."""
        mock_store = MagicMock()
        mock_store.size.return_value = 100
        mock_get_database.return_value = mock_store
        
        result = DatabaseHealthCheck.check_connection()
        
        assert result is True
        mock_store.size.assert_called_once()
    
    @patch('src.database.connection.get_database')
    def test_check_connection_unhealthy(self, mock_get_database):
        """Test unhealthy database connection check."""
        mock_get_database.side_effect = Exception("Connection failed")
        
        result = DatabaseHealthCheck.check_connection()
        
        assert result is False
    
    @patch('src.database.connection.get_database')
    @patch('src.database.connection.db_manager')
    def test_get_database_stats_success(self, mock_manager, mock_get_database):
        """Test successful database stats retrieval."""
        mock_store = MagicMock()
        mock_store.size.return_value = 150
        mock_get_database.return_value = mock_store
        
        mock_config = DatabaseConfig(db_path="/tmp/test")
        mock_manager.is_initialized.return_value = True
        mock_manager.get_config.return_value = mock_config
        
        with patch.object(DatabaseHealthCheck, 'check_connection', return_value=True):
            stats = DatabaseHealthCheck.get_database_stats()
        
        expected = {
            "is_initialized": True,
            "database_path": "/tmp/test",
            "database_size": 150,
            "connection_healthy": True
        }
        
        assert stats == expected
    
    @patch('src.database.connection.get_database')
    def test_get_database_stats_failure(self, mock_get_database):
        """Test database stats retrieval with error."""
        mock_get_database.side_effect = Exception("Stats error")
        
        stats = DatabaseHealthCheck.get_database_stats()
        
        assert stats["is_initialized"] is False
        assert stats["connection_healthy"] is False
        assert "error" in stats
        assert stats["error"] == "Stats error"