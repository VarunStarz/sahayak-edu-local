"""
ObjectBox database connection and store management.

This module provides:
- ObjectBox Store initialization and configuration
- Database connection utilities with transaction management
- Store lifecycle management (singleton pattern)
- Error handling for database operations
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from objectbox import Store

from .models import Student, Interaction, LearningProgress, CurriculumContent

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Configuration class for ObjectBox database settings."""
    
    def __init__(self, 
                 db_path: str = "data/objectbox",
                 max_db_size_in_kb: int = 1024 * 1024,  # 1GB
                 max_readers: int = 126,
                 debug_flags: int = 0):
        self.db_path = db_path
        self.max_db_size_in_kb = max_db_size_in_kb
        self.max_readers = max_readers
        self.debug_flags = debug_flags
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for ObjectBox Store options."""
        return {
            "directory": self.db_path,
            "max_db_size_in_kb": self.max_db_size_in_kb,
            "max_readers": self.max_readers,
            "debug_flags": self.debug_flags
        }


class ObjectBoxManager:
    """Singleton manager for ObjectBox Store instance."""
    
    _instance: Optional['ObjectBoxManager'] = None
    _store: Optional[Store] = None
    
    def __new__(cls) -> 'ObjectBoxManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._config: Optional[DatabaseConfig] = None
    
    def initialize(self, config: Optional[DatabaseConfig] = None) -> Store:
        """
        Initialize ObjectBox Store with configuration.
        
        Args:
            config: Database configuration. Uses default if None.
            
        Returns:
            ObjectBox Store instance
            
        Raises:
            RuntimeError: If initialization fails
        """
        if self._store is not None:
            logger.info("ObjectBox Store already initialized")
            return self._store
        
        try:
            self._config = config or DatabaseConfig()
            
            # Create database directory if it doesn't exist
            os.makedirs(self._config.db_path, exist_ok=True)
            
            # Create Store with configuration
            # ObjectBox automatically discovers entities with @Entity decorator
            self._store = Store(directory=self._config.db_path, model_classes=[Student, Interaction, LearningProgress, CurriculumContent])
            
            logger.info(f"ObjectBox Store initialized at {self._config.db_path}")
            return self._store
            
        except Exception as e:
            logger.error(f"Failed to initialize ObjectBox Store: {e}")
            raise RuntimeError(f"Database initialization failed: {e}")
    

    
    def get_store(self) -> Store:
        """
        Get the ObjectBox Store instance.
        
        Returns:
            ObjectBox Store instance
            
        Raises:
            RuntimeError: If Store is not initialized
        """
        if self._store is None:
            raise RuntimeError("ObjectBox Store not initialized. Call initialize() first.")
        return self._store
    
    def close(self):
        """Close the ObjectBox Store and cleanup resources."""
        if self._store is not None:
            try:
                self._store.close()
                logger.info("ObjectBox Store closed successfully")
            except Exception as e:
                logger.error(f"Error closing ObjectBox Store: {e}")
            finally:
                self._store = None
    
    def is_initialized(self) -> bool:
        """Check if the ObjectBox Store is initialized."""
        return self._store is not None
    
    def get_config(self) -> Optional[DatabaseConfig]:
        """Get the current database configuration."""
        return self._config


# Global instance
db_manager = ObjectBoxManager()


def initialize_database(config: Optional[DatabaseConfig] = None) -> Store:
    """
    Initialize the ObjectBox database with optional configuration.
    
    Args:
        config: Database configuration. Uses default if None.
        
    Returns:
        ObjectBox Store instance
    """
    return db_manager.initialize(config)


def get_database() -> Store:
    """
    Get the initialized ObjectBox Store instance.
    
    Returns:
        ObjectBox Store instance
        
    Raises:
        RuntimeError: If database is not initialized
    """
    return db_manager.get_store()


def close_database():
    """Close the ObjectBox database connection."""
    db_manager.close()


@contextmanager
def database_transaction():
    """
    Context manager for database transactions.
    
    Usage:
        with database_transaction():
            # Perform database operations
            pass
    """
    store = get_database()
    
    # ObjectBox handles transactions automatically for most operations
    # This context manager provides a consistent interface
    try:
        yield store
    except Exception as e:
        logger.error(f"Database transaction failed: {e}")
        raise


class DatabaseHealthCheck:
    """Utility class for database health monitoring."""
    
    @staticmethod
    def check_connection() -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            store = get_database()
            # Simple health check - try to access store info
            _ = store.size()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """
        Get database statistics and information.
        
        Returns:
            Dictionary with database statistics
        """
        try:
            store = get_database()
            config = db_manager.get_config()
            
            stats = {
                "is_initialized": db_manager.is_initialized(),
                "database_path": config.db_path if config else None,
                "database_size": store.size() if store else 0,
                "connection_healthy": DatabaseHealthCheck.check_connection()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {
                "is_initialized": False,
                "database_path": None,
                "database_size": 0,
                "connection_healthy": False,
                "error": str(e)
            }


# Utility functions for common database operations
def ensure_database_initialized(config: Optional[DatabaseConfig] = None):
    """
    Ensure database is initialized, initialize if not.
    
    Args:
        config: Database configuration to use if initializing
    """
    if not db_manager.is_initialized():
        initialize_database(config)


def reset_database(config: Optional[DatabaseConfig] = None):
    """
    Reset the database by closing and reinitializing.
    
    Args:
        config: New database configuration
    """
    close_database()
    initialize_database(config)