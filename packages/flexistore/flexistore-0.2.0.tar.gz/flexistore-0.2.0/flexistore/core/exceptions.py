"""Custom exception hierarchy for FlexiStore."""

from typing import Optional, Any, Dict


class StorageError(Exception):
    """Base exception for all storage operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConnectionError(StorageError):
    """Network/connection related errors."""
    
    def __init__(self, message: str, retry_after: Optional[float] = None, **kwargs):
        super().__init__(message, kwargs)
        self.retry_after = retry_after


class AuthenticationError(StorageError):
    """Authentication/authorization errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(message, kwargs)
        self.provider = provider


class ValidationError(StorageError):
    """Input validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs):
        super().__init__(message, kwargs)
        self.field = field
        self.value = value


class OperationError(StorageError):
    """Storage operation errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, resource: Optional[str] = None, **kwargs):
        super().__init__(message, kwargs)
        self.operation = operation
        self.resource = resource


class ConfigurationError(StorageError):
    """Configuration related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, kwargs)
        self.config_key = config_key


class QuotaExceededError(StorageError):
    """Storage quota exceeded errors."""
    
    def __init__(self, message: str, current_usage: Optional[int] = None, limit: Optional[int] = None, **kwargs):
        super().__init__(message, kwargs)
        self.current_usage = current_usage
        self.limit = limit


class FileNotFoundError(StorageError):
    """File not found errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(message, kwargs)
        self.file_path = file_path


class NotFoundError(StorageError):
    """Resource not found errors (generic)."""
    
    def __init__(self, message: str, resource_path: Optional[str] = None, **kwargs):
        super().__init__(message, kwargs)
        self.resource_path = resource_path


class AlreadyExistsError(StorageError):
    """Resource already exists errors."""
    
    def __init__(self, message: str, resource_path: Optional[str] = None, **kwargs):
        super().__init__(message, kwargs)
        self.resource_path = resource_path


class PermissionDeniedError(StorageError):
    """Permission denied errors."""
    
    def __init__(self, message: str, required_permissions: Optional[list] = None, **kwargs):
        super().__init__(message, kwargs)
        self.required_permissions = required_permissions or []


class RateLimitError(StorageError):
    """Rate limiting errors."""
    
    def __init__(self, message: str, retry_after: Optional[float] = None, limit: Optional[int] = None, **kwargs):
        super().__init__(message, kwargs)
        self.retry_after = retry_after
        self.limit = limit


class TimeoutError(StorageError):
    """Operation timeout errors."""
    
    def __init__(self, message: str, timeout_value: Optional[float] = None, **kwargs):
        super().__init__(message, kwargs)
        self.timeout_value = timeout_value


class RetryableError(StorageError):
    """Errors that can be retried."""
    
    def __init__(self, message: str, max_retries: Optional[int] = None, **kwargs):
        super().__init__(message, kwargs)
        self.max_retries = max_retries


class NonRetryableError(StorageError):
    """Errors that should not be retried."""
    pass


# Provider-specific exceptions
class AzureStorageError(StorageError):
    """Azure-specific storage errors."""
    
    def __init__(self, message: str, azure_error_code: Optional[str] = None, **kwargs):
        super().__init__(message, kwargs)
        self.azure_error_code = azure_error_code


class AWSStorageError(StorageError):
    """AWS-specific storage errors."""
    
    def __init__(self, message: str, aws_error_code: Optional[str] = None, **kwargs):
        super().__init__(message, kwargs)
        self.aws_error_code = aws_error_code


# Utility functions for error handling
def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable."""
    if isinstance(error, RetryableError):
        return True
    if isinstance(error, (ConnectionError, TimeoutError, RateLimitError)):
        return True
    return False


def get_retry_delay(error: Exception, base_delay: float = 1.0) -> float:
    """Get retry delay for an error."""
    if hasattr(error, 'retry_after') and error.retry_after:
        return error.retry_after
    if isinstance(error, RateLimitError):
        return base_delay * 2
    if isinstance(error, ConnectionError):
        return base_delay
    return base_delay


def format_error_message(error: Exception) -> str:
    """Format error message for user display."""
    if isinstance(error, StorageError):
        return str(error)
    
    # Handle built-in exceptions
    if isinstance(error, FileNotFoundError):
        return f"File not found: {error}"
    if isinstance(error, PermissionError):
        return f"Permission denied: {error}"
    if isinstance(error, TimeoutError):
        return f"Operation timed out: {error}"
    
    return str(error)

# Export all exceptions
__all__ = [
    'StorageError',
    'ConnectionError', 
    'AuthenticationError',
    'ValidationError',
    'OperationError',
    'ConfigurationError',
    'QuotaExceededError',
    'FileNotFoundError',
    'NotFoundError',
    'AlreadyExistsError',
    'PermissionDeniedError',
    'RateLimitError',
    'TimeoutError',
    'RetryableError',
    'NonRetryableError',
    'AzureStorageError',
    'AWSStorageError',
    'is_retryable_error',
    'get_retry_delay',
    'format_error_message'
]
