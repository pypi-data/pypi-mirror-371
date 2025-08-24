"""CLI configuration and provider setup for FlexiStore."""

import os
from typing import Optional

from azure.core.exceptions import AzureError
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

from flexistore.backends.aws import AWSStorageManager, AWSStorageConfig
from flexistore.backends.azure import AzureStorageManager, AzureStorageConfig
from flexistore.core.base import StorageManager

# Load environment variables
load_dotenv()


def get_env_or_prompt(env_var: str, prompt_text: str) -> str:
    """Get environment variable or prompt user for input."""
    val = os.getenv(env_var)
    if not val:
        val = input(f"{prompt_text}: ").strip()
    return val


def get_default_provider() -> str:
    """Get the default provider from environment or return 'azure'."""
    return os.getenv("FLEXISTORE_PROVIDER", "azure")


def create_aws_manager(verify_ssl: bool = True) -> AWSStorageManager:
    """Create and configure AWS storage manager."""
    bucket = get_env_or_prompt("AWS_BUCKET", "S3 bucket name")
    region = get_env_or_prompt("AWS_REGION", "AWS region")
    access_key = get_env_or_prompt("AWS_ACCESS_KEY_ID", "AWS access key ID")
    secret_key = get_env_or_prompt("AWS_SECRET_ACCESS_KEY", "AWS secret access key")
    
    try:
        config = AWSStorageConfig(
            bucket_name=bucket,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            verify_ssl=verify_ssl,
        )
        return AWSStorageManager(config)
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"Unable to initialize AWSStorageManager: {e}")


def create_azure_manager(verify_ssl: bool = True) -> AzureStorageManager:
    """Create and configure Azure storage manager."""
    conn_str = get_env_or_prompt("AZURE_CONN_STRING", "Azure connection string")
    container = get_env_or_prompt("AZURE_CONTAINER", "Container name")
    
    try:
        config = AzureStorageConfig(
            connection_string=conn_str,
            container_name=container,
            verify_ssl=verify_ssl,
        )
        return AzureStorageManager(config)
    except AzureError as e:
        raise RuntimeError(f"Unable to initialize AzureStorageManager: {e}")


def create_storage_manager(provider: Optional[str] = None, verify_ssl: bool = True) -> StorageManager:
    """Create and return the appropriate storage manager."""
    if provider is None:
        provider = get_default_provider()
    
    if provider == "aws":
        return create_aws_manager(verify_ssl)
    elif provider == "azure":
        return create_azure_manager(verify_ssl)
    else:
        raise ValueError(f"Unknown provider '{provider}'. Please specify either 'azure' or 'aws'.")
