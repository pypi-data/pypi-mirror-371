"""Configuration management for FlexiStore."""

import os
import configparser
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field

from .exceptions import ConfigurationError, ValidationError
from .base import StorageConfig


@dataclass
class FlexiStoreConfig:
    """Main configuration for FlexiStore."""
    
    # Default storage provider
    default_provider: str = "azure"
    
    # Global storage configuration
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CLI configuration
    cli_timeout: int = 300
    cli_confirm_actions: bool = True
    cli_show_progress: bool = True
    
    # Cache configuration
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 1000
    
    # Security configuration
    enable_ssl_verification: bool = True
    allow_insecure_connections: bool = False
    
    # Performance configuration
    max_concurrent_operations: int = 10
    connection_timeout: int = 30
    read_timeout: int = 60


class ConfigManager:
    """Manages FlexiStore configuration from multiple sources."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _get_default_config_path(self) -> Path:
        """Get the default configuration file path."""
        config_dir = Path.home() / ".flexistore"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.ini"
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from file if it exists
        if self.config_path.exists():
            try:
                self.config.read(self.config_path)
            except configparser.Error as e:
                raise ConfigurationError(f"Failed to parse config file: {e}")
        
        # Set defaults
        self._set_defaults()
        
        # Override with environment variables
        self._load_from_env()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        # Note: 'DEFAULT' section is special in configparser and can't be added manually
        
        if not self.config.has_section('general'):
            self.config.add_section('general')
        
        if not self.config.has_section('storage'):
            self.config.add_section('storage')
        
        if not self.config.has_section('cli'):
            self.config.add_section('cli')
        
        if not self.config.has_section('logging'):
            self.config.add_section('logging')
        
        if not self.config.has_section('security'):
            self.config.add_section('security')
        
        if not self.config.has_section('performance'):
            self.config.add_section('performance')
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'FLEXISTORE_DEFAULT_PROVIDER': ('general', 'default_provider'),
            'FLEXISTORE_LOG_LEVEL': ('logging', 'log_level'),
            'FLEXISTORE_CLI_TIMEOUT': ('cli', 'cli_timeout'),
            'FLEXISTORE_CLI_CONFIRM_ACTIONS': ('cli', 'cli_confirm_actions'),
            'FLEXISTORE_CLI_SHOW_PROGRESS': ('cli', 'cli_show_progress'),
            'FLEXISTORE_STORAGE_TIMEOUT': ('storage', 'timeout'),
            'FLEXISTORE_STORAGE_MAX_RETRIES': ('storage', 'max_retries'),
            'FLEXISTORE_STORAGE_CHUNK_SIZE': ('storage', 'chunk_size'),
            'FLEXISTORE_STORAGE_VERIFY_SSL': ('storage', 'verify_ssl'),
            'FLEXISTORE_SECURITY_ENABLE_SSL_VERIFICATION': ('security', 'enable_ssl_verification'),
            'FLEXISTORE_PERFORMANCE_MAX_CONCURRENT': ('performance', 'max_concurrent_operations'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if key in ['cli_timeout', 'storage_timeout', 'storage_max_retries', 
                          'storage_chunk_size', 'max_concurrent_operations']:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif key in ['cli_confirm_actions', 'cli_show_progress', 'storage_verify_ssl', 
                           'enable_ssl_verification']:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                self.config.set(section, key, str(value))
    
    def get(self, section: str, key: str, fallback: Optional[Any] = None) -> Any:
        """Get a configuration value."""
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getint(self, section: str, key: str, fallback: Optional[int] = None) -> Optional[int]:
        """Get an integer configuration value."""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getboolean(self, section: str, key: str, fallback: Optional[bool] = None) -> Optional[bool]:
        """Get a boolean configuration value."""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set a configuration value."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                self.config.write(f)
        except (OSError, IOError) as e:
            raise ConfigurationError(f"Failed to save config file: {e}")
    
    def get_storage_config(self) -> StorageConfig:
        """Get storage configuration as StorageConfig object."""
        return StorageConfig(
            verify_ssl=self.getboolean('storage', 'verify_ssl', True),
            timeout=self.getint('storage', 'timeout', 30),
            max_retries=self.getint('storage', 'max_retries', 3),
            chunk_size=self.getint('storage', 'chunk_size', 8 * 1024 * 1024),
            connection_pool_size=self.getint('storage', 'connection_pool_size', 10),
            enable_compression=self.getboolean('storage', 'enable_compression', False),
            enable_encryption=self.getboolean('storage', 'enable_encryption', False),
            retry_delay=float(self.get('storage', 'retry_delay', 1.0)),
            max_retry_delay=float(self.get('storage', 'max_retry_delay', 60.0)),
            backoff_factor=float(self.get('storage', 'backoff_factor', 2.0))
        )
    
    def get_flexistore_config(self) -> FlexiStoreConfig:
        """Get complete FlexiStore configuration."""
        return FlexiStoreConfig(
            default_provider=self.get('general', 'default_provider', 'azure'),
            storage=self.get_storage_config(),
            log_level=self.get('logging', 'log_level', 'INFO'),
            log_format=self.get('logging', 'log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            cli_timeout=self.getint('cli', 'cli_timeout', 300),
            cli_confirm_actions=self.getboolean('cli', 'cli_confirm_actions', True),
            cli_show_progress=self.getboolean('cli', 'cli_show_progress', True),
            cache_enabled=self.getboolean('cli', 'cache_enabled', True),
            cache_ttl=self.getint('cli', 'cache_ttl', 3600),
            cache_max_size=self.getint('cli', 'cache_max_size', 1000),
            enable_ssl_verification=self.getboolean('security', 'enable_ssl_verification', True),
            allow_insecure_connections=self.getboolean('security', 'allow_insecure_connections', False),
            max_concurrent_operations=self.getint('performance', 'max_concurrent_operations', 10),
            connection_timeout=self.getint('performance', 'connection_timeout', 30),
            read_timeout=self.getint('performance', 'read_timeout', 60)
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        errors = []
        
        # Validate storage configuration
        storage_config = self.get_storage_config()
        if storage_config.timeout <= 0:
            errors.append("Storage timeout must be positive")
        if storage_config.max_retries < 0:
            errors.append("Storage max retries must be non-negative")
        if storage_config.chunk_size <= 0:
            errors.append("Storage chunk size must be positive")
        
        # Validate CLI configuration
        cli_timeout = self.getint('cli', 'cli_timeout', 300)
        if cli_timeout <= 0:
            errors.append("CLI timeout must be positive")
        
        # Validate performance configuration
        max_concurrent = self.getint('performance', 'max_concurrent_operations', 10)
        if max_concurrent <= 0:
            errors.append("Max concurrent operations must be positive")
        
        if errors:
            raise ValidationError("Configuration validation failed", details={'errors': errors})


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> FlexiStoreConfig:
    """Get the global FlexiStore configuration."""
    return config_manager.get_flexistore_config()


def get_storage_config() -> StorageConfig:
    """Get the global storage configuration."""
    return config_manager.get_storage_config()


def reload_config() -> None:
    """Reload configuration from file and environment."""
    config_manager._load_config()
    config_manager.validate()
