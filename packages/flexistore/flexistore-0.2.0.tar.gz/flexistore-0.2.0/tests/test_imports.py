"""Test that all FlexiStore modules can be imported correctly."""

import pytest


def test_import_flexistore_package():
    """Test that the main flexistore package can be imported."""
    import flexistore

    assert flexistore is not None
    assert hasattr(flexistore, "__version__")
    assert flexistore.__version__ == "0.2.0"


def test_import_storage_manager():
    """Test that StorageManager can be imported."""
    from flexistore.manager import StorageManager

    assert StorageManager is not None


def test_import_azure_manager():
    """Test that AzureStorageManager can be imported."""
    from flexistore.azure import AzureStorageManager

    assert AzureStorageManager is not None


def test_import_aws_manager():
    """Test that AWSStorageManager can be imported."""
    from flexistore.aws import AWSStorageManager

    assert AWSStorageManager is not None


def test_import_cli():
    """Test that CLI module can be imported."""
    from flexistore.cli import main

    assert main is not None
    assert callable(main)


def test_import_all():
    """Test that __all__ exports work correctly."""
    from flexistore import __all__

    expected_exports = [
        "StorageManager",
        "AzureStorageManager",
        "AWSStorageManager",
        "cli_main",
        "__version__",
        "__author__",
        "__email__",
    ]

    for export in expected_exports:
        assert export in __all__, f"Expected {export} to be in __all__"


def test_version_functions():
    """Test that version helper functions work."""
    from flexistore import get_author, get_email, get_version

    assert get_version() == "0.2.0"
    assert get_author() == "Prakhar Agarwal"
    assert get_email() == "prakhara56@gmail.com"


def test_cli_function_exists():
    """Test that CLI main function exists and is callable."""
    from flexistore.cli import main

    assert main is not None
    assert callable(main)


def test_azure_imports():
    """Test that Azure module imports work."""
    from flexistore.azure import AzureStorageManager

    assert AzureStorageManager is not None

    # Test that it inherits from StorageManager
    from flexistore.manager import StorageManager

    assert issubclass(AzureStorageManager, StorageManager)


def test_aws_imports():
    """Test that AWS module imports work."""
    from flexistore.aws import AWSStorageManager

    assert AWSStorageManager is not None

    # Test that it inherits from StorageManager
    from flexistore.manager import StorageManager

    assert issubclass(AWSStorageManager, StorageManager)


def test_manager_abstract_methods():
    """Test that StorageManager has the expected abstract methods."""
    from abc import ABC

    from flexistore.manager import StorageManager

    assert issubclass(StorageManager, ABC)

    expected_methods = [
        "upload_file",
        "download_file",
        "list_files",
        "download_folder",
        "delete_file",
    ]

    for method in expected_methods:
        assert hasattr(StorageManager, method), f"Expected {method} method"
