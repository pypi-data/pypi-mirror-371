"""Enhanced abstract base classes for FlexiStore with async support."""

from abc import ABC, abstractmethod
from typing import Protocol, Dict, Any, Optional, AsyncIterator, List, Union
from dataclasses import dataclass, field
from pathlib import Path
import asyncio


@dataclass
class StorageConfig:
    """Configuration for storage operations."""
    verify_ssl: bool = True
    timeout: int = 30
    max_retries: int = 3
    chunk_size: int = 8 * 1024 * 1024  # 8MB
    connection_pool_size: int = 10
    enable_compression: bool = False
    enable_encryption: bool = False
    retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    backoff_factor: float = 2.0


@dataclass
class StorageMetadata:
    """Metadata for storage objects."""
    content_type: Optional[str] = None
    content_encoding: Optional[str] = None
    content_disposition: Optional[str] = None
    cache_control: Optional[str] = None
    custom_metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class StorageObject:
    """Represents a storage object with metadata."""
    name: str
    size: int
    last_modified: Optional[str] = None
    etag: Optional[str] = None
    metadata: StorageMetadata = field(default_factory=StorageMetadata)
    is_directory: bool = False


class StorageManager(ABC):
    """Enhanced abstract storage manager with async support."""
    
    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig()
        self._initialized = False
    
    @abstractmethod
    async def ainitialize(self) -> None:
        """Initialize async connections and resources."""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize synchronous connections and resources."""
        pass
    
    @abstractmethod
    async def aupload_file(
        self, 
        local_path: Union[str, Path], 
        remote_path: str, 
        metadata: Optional[StorageMetadata] = None
    ) -> None:
        """Upload a file asynchronously."""
        pass
    
    @abstractmethod
    async def adownload_file(
        self, 
        remote_path: str, 
        local_path: Union[str, Path]
    ) -> None:
        """Download a file asynchronously."""
        pass
    
    @abstractmethod
    async def alist_files(
        self, 
        remote_prefix: str = "", 
        recursive: bool = True
    ) -> AsyncIterator[StorageObject]:
        """List files asynchronously."""
        pass
    
    @abstractmethod
    async def adownload_folder(
        self, 
        remote_prefix: str, 
        local_dir: Union[str, Path]
    ) -> None:
        """Download a folder asynchronously."""
        pass
    
    @abstractmethod
    async def adelete_file(self, remote_path: str) -> None:
        """Delete a file asynchronously."""
        pass
    
    @abstractmethod
    async def adelete_folder(self, remote_path: str) -> None:
        """Delete a folder asynchronously."""
        pass
    
    @abstractmethod
    async def afile_exists(self, remote_path: str) -> bool:
        """Check if a file exists asynchronously."""
        pass
    
    @abstractmethod
    async def aget_file_info(self, remote_path: str) -> StorageObject:
        """Get file information asynchronously."""
        pass
    
    # Synchronous wrappers for backward compatibility
    def upload_file(
        self, 
        local_path: Union[str, Path], 
        remote_path: str, 
        metadata: Optional[StorageMetadata] = None
    ) -> None:
        """Synchronous wrapper for async upload."""
        return asyncio.run(self.aupload_file(local_path, remote_path, metadata))
    
    def download_file(
        self, 
        remote_path: str, 
        local_path: Union[str, Path]
    ) -> None:
        """Synchronous wrapper for async download."""
        return asyncio.run(self.adownload_file(remote_path, local_path))
    
    def list_files(
        self, 
        remote_prefix: str = "", 
        recursive: bool = True
    ) -> List[str]:
        """Synchronous wrapper for async list."""
        async def _list():
            files = []
            async for obj in self.alist_files(remote_prefix, recursive):
                files.append(obj.name)
            return files
        return asyncio.run(_list())
    
    def download_folder(
        self, 
        remote_prefix: str, 
        local_dir: Union[str, Path]
    ) -> None:
        """Synchronous wrapper for async folder download."""
        return asyncio.run(self.adownload_folder(remote_prefix, local_dir))
    
    def delete_file(self, remote_path: str) -> None:
        """Synchronous wrapper for async delete."""
        return asyncio.run(self.adelete_file(remote_path))
    
    def delete_folder(self, remote_prefix: str) -> None:
        """Synchronous wrapper for async folder delete."""
        return asyncio.run(self.adelete_folder(remote_prefix))
    
    def file_exists(self, remote_path: str) -> bool:
        """Synchronous wrapper for async file existence check."""
        return asyncio.run(self.afile_exists(remote_path))
    
    def get_file_info(self, remote_path: str) -> StorageObject:
        """Synchronous wrapper for async file info."""
        return asyncio.run(self.aget_file_info(remote_path))
    
    async def aclose(self) -> None:
        """Close async connections and cleanup resources."""
        pass
    
    def close(self) -> None:
        """Close synchronous connections and cleanup resources."""
        pass
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.ainitialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()


class StorageProvider(Protocol):
    """Protocol for storage providers."""
    
    async def upload(self, local_path: Union[str, Path], remote_path: str, 
                    metadata: Optional[StorageMetadata] = None) -> None:
        """Upload a file."""
        ...
    
    async def download(self, remote_path: str, local_path: Union[str, Path]) -> None:
        """Download a file."""
        ...
    
    async def list(self, prefix: str = "", recursive: bool = True) -> AsyncIterator[StorageObject]:
        """List files."""
        ...
    
    async def delete(self, remote_path: str) -> None:
        """Delete a file."""
        ...
    
    async def exists(self, remote_path: str) -> bool:
        """Check if file exists."""
        ...
