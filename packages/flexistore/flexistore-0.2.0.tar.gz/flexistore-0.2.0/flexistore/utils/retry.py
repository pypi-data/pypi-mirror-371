"""Retry mechanisms with exponential backoff for FlexiStore."""

import asyncio
import time
from typing import Callable, TypeVar, Optional, Union, Any
from functools import wraps

from ..core.exceptions import StorageError, RetryableError, NonRetryableError, is_retryable_error

T = TypeVar('T')


class RetryPolicy:
    """Configurable retry policy for operations."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (RetryableError,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a specific attempt."""
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add some randomness to prevent thundering herd
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = None
):
    """Decorator for retrying functions with exponential backoff."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Use default retryable exceptions if none specified
            if retryable_exceptions is None:
                from ..core.exceptions import RetryableError, ConnectionError, TimeoutError, RateLimitError
                default_retryable = (RetryableError, ConnectionError, TimeoutError, RateLimitError)
            else:
                default_retryable = retryable_exceptions
            
            policy = RetryPolicy(
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                jitter=jitter,
                retryable_exceptions=default_retryable
            )
            
            last_exception = None
            
            for attempt in range(1, policy.max_retries + 1):  # +1 because we start at 1
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on last attempt
                    if attempt >= policy.max_retries:
                        break
                    
                    # Check if exception is in retryable list (this takes priority)
                    if not any(isinstance(e, exc_type) for exc_type in policy.retryable_exceptions):
                        break
                    
                    # If we have explicit retryable_exceptions, we don't need the fallback check
                    # The fallback check is only needed when using default retryable_exceptions
                    
                    # Calculate delay and wait
                    delay = policy.get_delay(attempt)
                    time.sleep(delay)
            
            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            else:
                raise StorageError("Operation failed after all retries")
        
        return wrapper
    
    return decorator


def aretry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = None
):
    """Decorator for retrying async functions with exponential backoff."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Use default retryable exceptions if none specified
            if retryable_exceptions is None:
                from ..core.exceptions import RetryableError, ConnectionError, TimeoutError, RateLimitError
                default_retryable = (RetryableError, ConnectionError, TimeoutError, RateLimitError)
            else:
                default_retryable = retryable_exceptions
            
            policy = RetryPolicy(
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                jitter=jitter,
                retryable_exceptions=default_retryable
            )
            
            last_exception = None
            
            for attempt in range(1, policy.max_retries + 1):  # +1 because we start at 1
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on last attempt
                    if attempt >= policy.max_retries:
                        break
                    
                    # Check if exception is in retryable list (this takes priority)
                    if not any(isinstance(e, exc_type) for exc_type in policy.retryable_exceptions):
                        break
                    
                    # If we have explicit retryable_exceptions, we don't need the fallback check
                    # The fallback check is only needed when using default retryable_exceptions
                    
                    # Calculate delay and wait
                    delay = policy.get_delay(attempt)
                    await asyncio.sleep(delay)
            
            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            else:
                raise StorageError("Operation failed after all retries")
        
        return wrapper
    
    return decorator


def retry_on_condition(
    condition: Callable[[Exception], bool],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
):
    """Decorator for retrying functions based on a custom condition."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on last attempt
                    if attempt >= max_retries:
                        break
                    
                    # Check custom condition
                    if not condition(e):
                        break
                    
                    # Calculate delay and wait
                    delay = min(base_delay * (backoff_factor ** (attempt - 1)), max_delay)
                    time.sleep(delay)
            
            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            else:
                raise StorageError("Operation failed after all retries")
        
        return wrapper
    
    return decorator


async def aretry_on_condition(
    condition: Callable[[Exception], bool],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
):
    """Decorator for retrying async functions based on a custom condition."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on last attempt
                    if attempt >= max_retries:
                        break
                    
                    # Check custom condition
                    if not condition(e):
                        break
                    
                    # Calculate delay and wait
                    delay = min(base_delay * (backoff_factor ** (attempt - 1)), max_delay)
                    await asyncio.sleep(delay)
            
            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            else:
                raise StorageError("Operation failed after all retries")
        
        return wrapper
    
    return decorator


# Convenience functions for common retry scenarios
def retry_on_connection_error(max_retries: int = 3):
    """Retry on connection-related errors."""
    return retry_with_backoff(
        max_retries=max_retries,
        retryable_exceptions=(ConnectionError, TimeoutError)
    )


def retry_on_rate_limit(max_retries: int = 5):
    """Retry on rate limiting errors with longer delays."""
    return retry_with_backoff(
        max_retries=max_retries,
        base_delay=2.0,
        max_delay=120.0,
        backoff_factor=3.0
    )


async def aretry_on_connection_error(max_retries: int = 3):
    """Async retry on connection-related errors."""
    return aretry_with_backoff(
        max_retries=max_retries,
        retryable_exceptions=(ConnectionError, TimeoutError)
    )


async def aretry_on_rate_limit(max_retries: int = 5):
    """Async retry on rate limiting errors with longer delays."""
    return aretry_with_backoff(
        max_retries=max_retries,
        base_delay=2.0,
        max_delay=120.0,
        backoff_factor=3.0
    )
