"""Validation utilities for FlexiStore."""

import re
import os
from pathlib import Path, PurePath
from typing import Union, Optional, List, Dict, Any
from urllib.parse import urlparse, urljoin

from ..core.exceptions import ValidationError


class PathValidator:
    """Validates and sanitizes file paths."""
    
    # Common dangerous patterns
    DANGEROUS_PATTERNS = [
        r'\.\.',  # Directory traversal
        r'//+',   # Multiple slashes
        r'\\+',   # Multiple backslashes
        r'[<>:"|?*]',  # Invalid characters
        r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$',  # Reserved names (Windows)
    ]
    
    # Maximum path length (conservative)
    MAX_PATH_LENGTH = 1024
    
    # Allowed file extensions (configurable)
    ALLOWED_EXTENSIONS = {
        '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.tar', '.gz', '.rar', '.7z',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
        '.log', '.tmp', '.bak', '.old'
    }
    
    def __init__(self, allowed_extensions: Optional[set] = None):
        self.allowed_extensions = allowed_extensions or self.ALLOWED_EXTENSIONS
    
    def validate_path(self, path: Union[str, Path]) -> Path:
        """Validate and return a sanitized Path object."""
        path_str = str(path)
        
        # Check length
        if len(path_str) > self.MAX_PATH_LENGTH:
            raise ValidationError(
                f"Path too long: {len(path_str)} characters (max: {self.MAX_PATH_LENGTH})",
                field="path_length",
                value=len(path_str)
            )
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, path_str, re.IGNORECASE):
                raise ValidationError(
                    f"Path contains dangerous pattern: {pattern}",
                    field="path_pattern",
                    value=path_str
                )
        
        # Convert to Path and resolve
        path_obj = Path(path_str)
        
        # Check for absolute paths (optional security measure)
        if path_obj.is_absolute():
            raise ValidationError(
                "Absolute paths are not allowed for security reasons",
                field="path_type",
                value=str(path_obj)
            )
        
        return path_obj
    
    def sanitize_path(self, path: Union[str, Path]) -> str:
        """Sanitize a path string by removing dangerous characters."""
        path_str = str(path)
        
        # Remove dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            path_str = re.sub(pattern, '', path_str, flags=re.IGNORECASE)
        
        # Normalize separators
        path_str = path_str.replace('\\', '/')
        path_str = re.sub(r'//+', '/', path_str)
        
        # Remove leading/trailing separators
        path_str = path_str.strip('/')
        
        return path_str
    
    def validate_file_extension(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        ext = Path(filename).suffix.lower()
        return ext in self.allowed_extensions
    
    def is_safe_filename(self, filename: str) -> bool:
        """Check if filename is safe."""
        if not filename or len(filename) > 255:
            return False
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                return False
        
        return True


class URLValidator:
    """Validates and sanitizes URLs."""
    
    # Allowed schemes
    ALLOWED_SCHEMES = {'http', 'https', 'ftp', 's3', 'gs', 'azure'}
    
    # Maximum URL length
    MAX_URL_LENGTH = 2048
    
    def __init__(self, allowed_schemes: Optional[set] = None):
        self.allowed_schemes = allowed_schemes or self.ALLOWED_SCHEMES
    
    def validate_url(self, url: str) -> str:
        """Validate and return a sanitized URL."""
        if not url or len(url) > self.MAX_URL_LENGTH:
            raise ValidationError(
                f"URL too long: {len(url)} characters (max: {self.MAX_URL_LENGTH})",
                field="url_length",
                value=len(url)
            )
        
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(
                f"Invalid URL format: {e}",
                field="url_format",
                value=url
            )
        
        # Check scheme
        if parsed.scheme and parsed.scheme.lower() not in self.allowed_schemes:
            raise ValidationError(
                f"URL scheme not allowed: {parsed.scheme}",
                field="url_scheme",
                value=parsed.scheme
            )
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'javascript:',  # JavaScript injection
            r'data:',        # Data URLs
            r'file:',        # File URLs
            r'vbscript:',    # VBScript injection
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                raise ValidationError(
                    f"URL contains dangerous pattern: {pattern}",
                    field="url_pattern",
                    value=url
                )
        
        return url
    
    def is_secure_url(self, url: str) -> bool:
        """Check if URL uses secure protocol."""
        try:
            parsed = urlparse(url)
            return parsed.scheme.lower() in {'https', 's3', 'gs', 'azure'}
        except:
            return False


class StorageValidator:
    """Validates storage-related inputs."""
    
    def __init__(self):
        self.path_validator = PathValidator()
        self.url_validator = URLValidator()
    
    def validate_storage_path(self, path: Union[str, Path]) -> str:
        """Validate storage path (remote path in cloud storage)."""
        path_str = str(path)
        
        # Storage paths should not contain absolute path indicators
        if path_str.startswith('/') or path_str.startswith('\\'):
            raise ValidationError(
                "Storage paths should be relative",
                field="storage_path",
                value=path_str
            )
        
        # Sanitize the path
        sanitized = self.path_validator.sanitize_path(path_str)
        
        # Ensure it's not empty
        if not sanitized:
            raise ValidationError(
                "Storage path cannot be empty",
                field="storage_path",
                value=path_str
            )
        
        return sanitized
    
    def validate_local_path(self, path: Union[str, Path]) -> Path:
        """Validate local file path."""
        return self.path_validator.validate_path(path)
    
    def validate_file_size(self, size: int, max_size: Optional[int] = None) -> int:
        """Validate file size."""
        if size < 0:
            raise ValidationError(
                "File size cannot be negative",
                field="file_size",
                value=size
            )
        
        if max_size is not None and size > max_size:
            raise ValidationError(
                f"File size {size} exceeds maximum allowed size {max_size}",
                field="file_size",
                value=size
            )
        
        return size
    
    def validate_metadata(self, metadata: Dict[str, str]) -> Dict[str, str]:
        """Validate storage metadata."""
        if not isinstance(metadata, dict):
            raise ValidationError(
                "Metadata must be a dictionary",
                field="metadata_type",
                value=type(metadata)
            )
        
        validated = {}
        for key, value in metadata.items():
            # Validate key
            if not isinstance(key, str) or len(key) > 128:
                raise ValidationError(
                    f"Invalid metadata key: {key}",
                    field="metadata_key",
                    value=key
                )
            
            # Validate value
            if not isinstance(value, str) or len(value) > 256:
                raise ValidationError(
                    f"Invalid metadata value for key {key}",
                    field="metadata_value",
                    value=value
                )
            
            # Check for dangerous patterns in key/value
            dangerous_patterns = [r'[<>"&]', r'javascript:', r'vbscript:']
            for pattern in dangerous_patterns:
                if re.search(pattern, key + value, re.IGNORECASE):
                    raise ValidationError(
                        f"Metadata contains dangerous pattern: {pattern}",
                        field="metadata_content",
                        value=f"{key}: {value}"
                    )
            
            validated[key] = value
        
        return validated


class SecurityValidator:
    """Validates security-related inputs."""
    
    def __init__(self):
        self.path_validator = PathValidator()
    
    def validate_credentials(self, credentials: Dict[str, str]) -> Dict[str, str]:
        """Validate credential dictionary."""
        if not isinstance(credentials, dict):
            raise ValidationError(
                "Credentials must be a dictionary",
                field="credentials_type",
                value=type(credentials)
            )
        
        required_fields = ['access_key', 'secret_key']
        for field in required_fields:
            if field not in credentials:
                raise ValidationError(
                    f"Missing required credential field: {field}",
                    field="credentials_missing",
                    value=field
                )
        
        # Validate credential values
        for key, value in credentials.items():
            if not isinstance(value, str) or len(value) < 8:
                raise ValidationError(
                    f"Invalid credential value for {key}",
                    field="credential_value",
                    value=key
                )
        
        return credentials
    
    def validate_permissions(self, permissions: List[str]) -> List[str]:
        """Validate permission list."""
        if not isinstance(permissions, list):
            raise ValidationError(
                "Permissions must be a list",
                field="permissions_type",
                value=type(permissions)
            )
        
        valid_permissions = {
            'read', 'write', 'delete', 'list', 'admin', 'public'
        }
        
        validated = []
        for permission in permissions:
            if not isinstance(permission, str):
                raise ValidationError(
                    f"Permission must be a string: {permission}",
                    field="permission_type",
                    value=permission
                )
            
            if permission not in valid_permissions:
                raise ValidationError(
                    f"Invalid permission: {permission}",
                    field="permission_value",
                    value=permission
                )
            
            validated.append(permission)
        
        return validated


# Global validator instances
path_validator = PathValidator()
url_validator = URLValidator()
storage_validator = StorageValidator()
security_validator = SecurityValidator()


# Convenience functions
def validate_path(path: Union[str, Path]) -> Path:
    """Validate a file path."""
    return path_validator.validate_path(path)


def validate_storage_path(path: Union[str, Path]) -> str:
    """Validate a storage path."""
    return storage_validator.validate_storage_path(path)


def validate_url(url: str) -> str:
    """Validate a URL."""
    return url_validator.validate_url(url)


def validate_metadata(metadata: Dict[str, str]) -> Dict[str, str]:
    """Validate storage metadata."""
    return storage_validator.validate_metadata(metadata)


def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe."""
    return path_validator.is_safe_filename(filename)


def is_secure_url(url: str) -> bool:
    """Check if URL uses secure protocol."""
    return url_validator.is_secure_url(url)
