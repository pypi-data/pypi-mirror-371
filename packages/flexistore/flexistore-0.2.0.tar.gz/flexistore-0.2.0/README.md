
# FlexiStore

[![PyPI version](https://badge.fury.io/py/flexistore.svg)](https://badge.fury.io/py/flexistore)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/prakhara56/FlexiStore/workflows/Tests/badge.svg)](https://github.com/prakhara56/FlexiStore/actions)
[![Code Coverage](https://codecov.io/gh/prakhara56/FlexiStore/branch/main/graph/badge.svg)](https://codecov.io/gh/prakhara56/FlexiStore)

**FlexiStore** is a modern, cloud-agnostic Python storage abstraction library that provides a unified interface to common file operations across different cloud providers. It features enhanced architecture with async support, retry mechanisms, streaming operations, and a professional CLI interface.

## 🚀 Features

- **Unified API** for upload/download/list/delete operations across cloud providers
- **Async Support** with both async and sync interfaces for all operations
- **Enhanced Architecture** with modular design, retry mechanisms, and streaming
- **Professional CLI** with interactive menus and rich user experience
- **Multiple Backends** including Azure Blob Storage and AWS S3
- **Enterprise Features** like encryption, compression, validation, and error handling
- **Modern Python** with type hints, comprehensive testing, and CI/CD pipeline

## Features

- **Unified API** for upload/download/list/delete operations.
- **Pluggable backends**: Implement `StorageManager` to add new providers.
- **Minimal dependencies**: Only requires the SDK for the backend you use.
- **CLI tool**: Interactive command-line interface for common operations.

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install flexistore
```

### From GitHub (Development)

```bash
pip install git+https://github.com/prakhara56/FlexiStore.git@main
```

### With Development Dependencies

```bash
pip install flexistore[dev]
```

## 🚀 Quick Start

### As a Library

```python
from flexistore.backends.azure import AzureStorageManager, AzureStorageConfig
from flexistore.backends.aws import AWSStorageManager, AWSStorageConfig

# Azure Blob Storage
azure_config = AzureStorageConfig(
    connection_string="<AZURE_CONN_STRING>",
    container_name="my-container"
)
azure_mgr = AzureStorageManager(azure_config)

# AWS S3
aws_config = AWSStorageConfig(
    bucket_name="my-bucket",
    region_name="us-east-1",
    aws_access_key_id="<ACCESS_KEY>",
    aws_secret_access_key="<SECRET_KEY>"
)
aws_mgr = AWSStorageManager(aws_config)

# Upload a file
azure_mgr.upload_file("./data/report.csv", "backups/report.csv")

# List files
files = aws_mgr.list_files("backups/")

# Download a file
aws_mgr.download_file("backups/report.csv", "./downloads/report.csv")
```

### As a CLI

```bash
# Interactive CLI with Azure
flexistore --provider azure

# Interactive CLI with AWS
flexistore --provider aws

# With SSL verification disabled for AWS
flexistore --provider aws --no-verify-ssl

# Show help
flexistore --help

# Show version
flexistore --version
```

### Environment Variables

The CLI automatically detects credentials from environment variables or `.env` files:

#### Azure Backend
- `AZURE_CONN_STRING` - Azure Storage connection string
- `AZURE_CONTAINER` - Container name

#### AWS Backend
- `AWS_BUCKET` - S3 bucket name
- `AWS_REGION` - AWS region (e.g., us-east-1)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key

#### General
- `FLEXISTORE_PROVIDER` - Default provider (azure/aws)

### Example .env File

```bash
# Azure
AZURE_CONN_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_CONTAINER=my-container

# AWS
AWS_BUCKET=my-bucket
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

## 📚 API Reference

### Core Classes

- **`StorageManager`** - Abstract base class for all storage backends
- **`StorageConfig`** - Base configuration class with common options
- **`StorageMetadata`** - File metadata and properties
- **`StorageObject`** - File object representation

### Backend Implementations

#### `AzureStorageManager` & `AzureStorageConfig`
- Azure Blob Storage backend with async support
- Connection string and container-based configuration
- Built-in retry mechanisms and error handling

#### `AWSStorageManager` & `AWSStorageConfig`
- AWS S3 backend with async support
- Bucket, region, and credentials configuration
- SSL verification controls and connection pooling

### Key Methods

All storage managers implement these core methods:

```python
# Synchronous operations
manager.upload_file(local_path, remote_path)
manager.download_file(remote_path, local_path)
manager.list_files(prefix)
manager.delete_file(remote_path)
manager.download_folder(remote_prefix, local_dir)

# Asynchronous operations
await manager.aupload_file(local_path, remote_path)
await manager.adownload_file(remote_path, local_path)
await manager.alist_files(prefix)
await manager.adelete_file(remote_path)
await manager.adownload_folder(remote_prefix, local_dir)
```

## 🖥️ CLI Reference

The FlexiStore CLI provides an interactive interface for all storage operations:

### Commands

- **`flexistore`** - Main CLI command
- **`flexistore-cli`** - Alternative command name
- **`python -m flexistore`** - Run as Python module

### Options

- **`--provider {azure,aws}`** - Choose storage provider
- **`--verify-ssl`** - Enable SSL verification (AWS)
- **`--no-verify-ssl`** - Disable SSL verification (AWS)
- **`--help`** - Show help information
- **`--version`** - Show version information

### Interactive Menu

The CLI provides a user-friendly menu with these operations:

1. **📤 Upload a file** - Upload local files to cloud storage
2. **📋 List files** - Browse files and folders in storage
3. **📥 Download a file** - Download files from cloud storage
4. **🗑️ Delete a file** - Remove files from cloud storage
5. **📁 Download folder** - Download entire folders recursively
0. **🚪 Exit** - Clean exit with resource cleanup

## 🔧 Extending for Other Providers

FlexiStore is designed to be easily extensible. To add a new cloud provider:

1. **Create Configuration Class**
   ```python
   from flexistore.core.base import StorageConfig
   
   class MyProviderConfig(StorageConfig):
       def __init__(self, api_key: str, region: str, **kwargs):
           super().__init__(**kwargs)
           self.api_key = api_key
           self.region = region
   ```

2. **Implement Storage Manager**
   ```python
   from flexistore.core.base import StorageManager
   
   class MyProviderManager(StorageManager):
       def __init__(self, config: MyProviderConfig):
           self.config = config
           # Initialize your provider's client
   
       def upload_file(self, local_path, remote_path):
           # Implement upload logic
           pass
       
       # Implement other abstract methods...
   ```

3. **Add to Package**
   - Place in `flexistore/backends/myprovider.py`
   - Update `flexistore/backends/__init__.py`
   - Add CLI support in `flexistore/cli/config.py`

## 🏗️ Architecture

FlexiStore follows a modular, extensible architecture:

```
flexistore/
├── core/           # Abstract base classes and core functionality
├── backends/       # Cloud provider implementations
├── cli/           # Command-line interface modules
├── utils/         # Utility functions and helpers
└── __init__.py    # Package exports
```

### Key Design Principles

- **Separation of Concerns** - Clear boundaries between components
- **Dependency Injection** - Configuration-driven initialization
- **Async-First** - Native async support with sync wrappers
- **Error Handling** - Comprehensive exception hierarchy
- **Extensibility** - Easy to add new cloud providers

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/prakhara56/FlexiStore.git
cd FlexiStore
pip install -e '.[dev]'
pre-commit install
```

### Running Tests

```bash
pytest                    # Run all tests
pytest --cov=flexistore  # With coverage
tox                      # Multi-environment testing
```

## License

This project is licensed under the MIT License.
