"""FlexiStore Storage Manager - Enhanced Architecture with Backward Compatibility."""

from .base import StorageManager as EnhancedStorageManager
from .config import StorageConfig as EnhancedStorageConfig
from .exceptions import StorageError, ConnectionError, ValidationError

# Re-export the enhanced classes for backward compatibility
__all__ = [
    'StorageManager',
    'StorageConfig', 
    'StorageError',
    'ConnectionError',
    'ValidationError'
]

# Alias the enhanced classes to maintain backward compatibility
StorageManager = EnhancedStorageManager
StorageConfig = EnhancedStorageConfig

# Legacy compatibility - these will be removed in future versions
class LegacyStorageManager(EnhancedStorageManager):
    """Legacy storage manager for backward compatibility."""
    
    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn(
            "LegacyStorageManager is deprecated. Use StorageManager from flexistore.core.base instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

# For very old code that might import from here
__all__.extend(['LegacyStorageManager'])
