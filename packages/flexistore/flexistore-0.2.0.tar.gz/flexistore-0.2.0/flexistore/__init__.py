"""FlexiStore - Cloud-agnostic storage interface with enhanced features."""

__version__ = "0.2.0"
__author__ = "Prakhar Agarwal"
__email__ = "prakhara56@gmail.com"

# Import core components first
from .core.base import StorageManager

# Import backend managers
from .backends.aws import AWSStorageManager
from .backends.azure import AzureStorageManager
from .cli import main as cli_main

# Maintain backward compatibility
__all__ = [
    "StorageManager",
    "AzureStorageManager",
    "AWSStorageManager",
    "cli_main",
    "__version__",
    "__author__",
    "__email__",
]


# Version info
def get_version() -> str:
    """Get the current version of FlexiStore."""
    return __version__


def get_author() -> str:
    """Get the author information."""
    return __author__


def get_email() -> str:
    """Get the contact email."""
    return __email__
