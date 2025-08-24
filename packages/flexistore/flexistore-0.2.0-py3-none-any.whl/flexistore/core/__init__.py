"""Core abstractions and base classes for FlexiStore."""

"""Core module for FlexiStore enhanced architecture."""

from .base import (
    StorageManager,
    StorageProvider,
    StorageConfig,
    StorageMetadata,
    StorageObject
)

from .manager import (
    StorageManager as LegacyStorageManager,
    StorageConfig as LegacyStorageConfig
)

from .exceptions import (
    StorageError,
    ConnectionError,
    AuthenticationError,
    ValidationError,
    OperationError,
    ConfigurationError,
    QuotaExceededError,
    FileNotFoundError,
    PermissionDeniedError,
    RateLimitError,
    TimeoutError,
    RetryableError,
    NonRetryableError,
    AzureStorageError,
    AWSStorageError,
    is_retryable_error,
    get_retry_delay,
    format_error_message
)

from .config import (
    ConfigManager,
    FlexiStoreConfig,
    get_config,
    get_storage_config,
    reload_config
)

__all__ = [
    # Base classes
    'StorageManager',
    'StorageProvider',
    'StorageConfig',
    'StorageMetadata',
    'StorageObject',
    
    # Legacy compatibility
    'LegacyStorageManager',
    'LegacyStorageConfig',
    
    # Exceptions
    'StorageError',
    'ConnectionError',
    'AuthenticationError',
    'ValidationError',
    'OperationError',
    'ConfigurationError',
    'QuotaExceededError',
    'FileNotFoundError',
    'PermissionDeniedError',
    'RateLimitError',
    'TimeoutError',
    'RetryableError',
    'NonRetryableError',
    'AzureStorageError',
    'AWSStorageError',
    'is_retryable_error',
    'get_retry_delay',
    'format_error_message',
    
    # Configuration
    'ConfigManager',
    'FlexiStoreConfig',
    'get_config',
    'get_storage_config',
    'reload_config',
]
