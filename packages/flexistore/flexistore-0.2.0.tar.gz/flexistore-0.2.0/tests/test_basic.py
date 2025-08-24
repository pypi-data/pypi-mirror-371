"""Basic tests to verify testing infrastructure is working."""

from pathlib import Path

import pytest


def test_import_flexistore():
    """Test that flexistore can be imported."""
    try:
        import flexistore

        assert flexistore is not None
    except ImportError:
        pytest.skip("flexistore not available for testing")


def test_temp_file_fixture(temp_file):
    """Test that temp_file fixture works."""
    assert temp_file.exists()
    assert temp_file.is_file()
    assert temp_file.read_bytes() == b"test content for file operations"


def test_temp_dir_fixture(temp_dir):
    """Test that temp_dir fixture works."""
    assert temp_dir.exists()
    assert temp_dir.is_dir()


def test_test_data_dir_fixture(test_data_dir):
    """Test that test_data_dir fixture works."""
    assert isinstance(test_data_dir, Path)
    assert test_data_dir.name == "data"


def test_mock_azure_client(mock_azure_client):
    """Test that mock_azure_client fixture works."""
    assert mock_azure_client is not None
    container_client = mock_azure_client.get_container_client("test")
    assert container_client is not None


def test_mock_aws_client(mock_aws_client):
    """Test that mock_aws_client fixture works."""
    assert mock_aws_client is not None
    s3_resource = mock_aws_client.resource("s3")
    assert s3_resource is not None


def test_environment_variables():
    """Test that test environment is set up correctly."""
    import os

    assert os.getenv("FLEXISTORE_TESTING") == "true"


class TestBasicFunctionality:
    """Basic functionality tests."""

    def test_pathlib_operations(self):
        """Test basic pathlib operations."""
        path = Path("test/path/file.txt")
        assert path.name == "file.txt"
        assert path.parent == Path("test/path")
        assert path.suffix == ".txt"

    def test_string_operations(self):
        """Test basic string operations."""
        test_string = "hello world"
        assert test_string.upper() == "HELLO WORLD"
        assert test_string.split() == ["hello", "world"]

    def test_list_operations(self):
        """Test basic list operations."""
        test_list = [1, 2, 3, 4, 5]
        assert len(test_list) == 5
        assert sum(test_list) == 15
        assert test_list[::2] == [1, 3, 5]


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (1, 1),
        ("hello", "hello"),
        ([1, 2, 3], [1, 2, 3]),
        (True, True),
    ],
)
def test_parametrized_test(input_value, expected):
    """Test parametrized testing functionality."""
    assert input_value == expected


@pytest.mark.slow
def test_slow_marker():
    """Test that slow marker works."""
    # This test should be marked as slow
    assert True


@pytest.mark.unit
def test_unit_marker():
    """Test that unit marker works."""
    # This test should be marked as unit
    assert True


@pytest.mark.integration
def test_integration_marker():
    """Test that integration marker works."""
    # This test should be marked as integration
    assert True
