"""Enhanced Azure Blob Storage Manager with async support and advanced features."""

import asyncio
import os
from pathlib import Path
from typing import List, Optional, Union

from azure.core.exceptions import AzureError, ResourceNotFoundError, ResourceExistsError
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
from azure.storage.blob.aio import ContainerClient as AsyncContainerClient

from ..core.base import StorageManager, StorageConfig, StorageMetadata, StorageObject
from ..core.exceptions import (
    StorageError, ConnectionError, ValidationError, NotFoundError, 
    AlreadyExistsError, RetryableError
)
from ..utils.retry import retry_with_backoff, aretry_with_backoff
from ..utils.validation import validate_path, validate_url
from ..utils.streaming import StreamingUploader, StreamingDownloader


class AzureStorageConfig(StorageConfig):
    """Azure-specific storage configuration."""
    
    def __init__(
        self,
        connection_string: str,
        container_name: str,
        *,
        verify_ssl: bool = True,
        timeout: int = 60,
        max_retries: int = 3,
        chunk_size: int = 16 * 1024 * 1024,  # 16MB
        enable_compression: bool = False,
        enable_encryption: bool = False,
        **kwargs
    ):
        super().__init__(
            verify_ssl=verify_ssl,
            timeout=timeout,
            max_retries=max_retries,
            chunk_size=chunk_size,
            enable_compression=enable_compression,
            enable_encryption=enable_encryption,
            **kwargs
        )
        self.connection_string = connection_string
        self.container_name = container_name


class AzureStorageManager(StorageManager):
    """Enhanced Azure Blob Storage Manager with async support."""
    
    def __init__(self, config: AzureStorageConfig):
        self.config = config
        self._sync_client: Optional[BlobServiceClient] = None
        self._sync_container: Optional[ContainerClient] = None
        self._async_client: Optional[AsyncBlobServiceClient] = None
        self._async_container: Optional[AsyncContainerClient] = None
        self._initialized = False
        
    def _get_sync_client(self) -> BlobServiceClient:
        """Get or create synchronous Azure client."""
        if self._sync_client is None:
            transport = RequestsTransport(connection_verify=self.config.verify_ssl)
            self._sync_client = BlobServiceClient.from_connection_string(
                self.config.connection_string,
                transport=transport
            )
        return self._sync_client
    
    def _get_sync_container(self) -> ContainerClient:
        """Get or create synchronous container client."""
        if self._sync_container is None:
            client = self._get_sync_client()
            self._sync_container = client.get_container_client(self.config.container_name)
        return self._sync_container
    
    async def _get_async_client(self) -> AsyncBlobServiceClient:
        """Get or create asynchronous Azure client."""
        if self._async_client is None:
            self._async_client = AsyncBlobServiceClient.from_connection_string(
                self.config.connection_string
            )
        return self._async_client
    
    async def _get_async_container(self) -> AsyncContainerClient:
        """Get or create asynchronous container client."""
        if self._async_container is None:
            client = await self._get_async_client()
            self._async_container = client.get_container_client(self.config.container_name)
        return self._async_container
    
    @retry_with_backoff(max_retries=3)
    def initialize(self) -> None:
        """Initialize synchronous connections and verify container exists."""
        try:
            container = self._get_sync_container()
            # Verify container exists by checking container properties
            container.get_container_properties()
            self._initialized = True
            print(f"✅ Connected to Azure container '{self.config.container_name}' successfully.")
        except ResourceNotFoundError:
            raise NotFoundError(f"Container '{self.config.container_name}' not found")
        except AzureError as e:
            raise ConnectionError(f"Failed to connect to Azure: {e}")
    
    async def ainitialize(self) -> None:
        """Initialize async connections and verify container exists."""
        try:
            container = await self._get_async_container()
            # Verify container exists by checking container properties
            await container.get_container_properties()
            self._initialized = True
            print(f"✅ Connected to Azure container '{self.config.container_name}' successfully.")
        except ResourceNotFoundError:
            raise NotFoundError(f"Container '{self.config.container_name}' not found")
        except AzureError as e:
            raise ConnectionError(f"Failed to connect to Azure: {e}")
    
    def close(self) -> None:
        """Close synchronous connections."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        if self._sync_container:
            self._sync_container = None
        self._initialized = False
    
    async def aclose(self) -> None:
        """Close async connections."""
        if self._async_client:
            await self._async_client.close()
            self._async_client = None
        if self._async_container:
            await self._async_container.aclose()
            self._async_container = None
        self._initialized = False
    
    @retry_with_backoff(max_retries=3)
    def upload_file(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        metadata: Optional[StorageMetadata] = None
    ) -> None:
        """Upload a file with retry mechanism and metadata support."""
        if not self._initialized:
            self.initialize()
        
        local_path = Path(local_path)
        validate_path(str(local_path))
        
        if not local_path.exists():
            raise NotFoundError(f"Local file not found: {local_path}")
        
        try:
            container = self._get_sync_container()
            blob_client = container.get_blob_client(remote_path)
            
            # Convert metadata to Azure format
            azure_metadata = {}
            if metadata:
                azure_metadata = {
                    k: str(v) for k, v in metadata.to_dict().items()
                    if k not in ['content_type', 'content_encoding', 'cache_control']
                }
            
            # Set content type if available
            content_settings = None
            if metadata and metadata.content_type:
                from azure.storage.blob import ContentSettings
                content_settings = ContentSettings(content_type=metadata.content_type)
            
            with open(local_path, "rb") as f:
                blob_client.upload_blob(
                    f,
                    overwrite=True,
                    metadata=azure_metadata,
                    content_settings=content_settings
                )
            
            print(f"✅ Upload succeeded: '{local_path}' → '{remote_path}'")
            
        except ResourceExistsError as e:
            raise AlreadyExistsError(f"Blob already exists: {remote_path}") from e
        except AzureError as e:
            raise StorageError(f"Upload failed: {e}") from e
    
    @aretry_with_backoff(max_retries=3)
    async def aupload_file(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        metadata: Optional[StorageMetadata] = None
    ) -> None:
        """Async upload with retry mechanism and metadata support."""
        if not self._initialized:
            await self.ainitialize()
        
        local_path = Path(local_path)
        validate_path(str(local_path))
        
        if not local_path.exists():
            raise NotFoundError(f"Local file not found: {local_path}")
        
        try:
            container = await self._get_async_container()
            blob_client = container.get_blob_client(remote_path)
            
            # Convert metadata to Azure format
            azure_metadata = {}
            if metadata:
                azure_metadata = {
                    k: str(v) for k, v in metadata.to_dict().items()
                    if k not in ['content_type', 'content_encoding', 'cache_control']
                }
            
            # Set content type if available
            content_settings = None
            if metadata and metadata.content_type:
                from azure.storage.blob import ContentSettings
                content_settings = ContentSettings(content_type=metadata.content_type)
            
            async with open(local_path, "rb") as f:
                await blob_client.upload_blob(
                    f,
                    overwrite=True,
                    metadata=azure_metadata,
                    content_settings=content_settings
                )
            
            print(f"✅ Upload succeeded: '{local_path}' → '{remote_path}'")
            
        except ResourceExistsError as e:
            raise AlreadyExistsError(f"Blob already exists: {remote_path}") from e
        except AzureError as e:
            raise StorageError(f"Upload failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def download_file(
        self,
        remote_path: str,
        local_path: Union[str, Path],
        metadata: Optional[StorageMetadata] = None
    ) -> None:
        """Download a file with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        local_path = Path(local_path)
        validate_path(str(local_path))
        
        try:
            container = self._get_sync_container()
            blob_client = container.get_blob_client(remote_path)
            
            # Ensure local directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with streaming for large files
            if self.config.chunk_size > 0:
                with StreamingDownloader(blob_client, self.config.chunk_size) as downloader:
                    with open(local_path, "wb") as f:
                        for chunk in downloader:
                            f.write(chunk)
            else:
                # Simple download for small files
                with open(local_path, "wb") as f:
                    blob_data = blob_client.download_blob()
                    f.write(blob_data.readall())
            
            print(f"✅ Download succeeded: '{remote_path}' → '{local_path}'")
            
        except ResourceNotFoundError:
            raise NotFoundError(f"Blob not found: {remote_path}")
        except AzureError as e:
            raise StorageError(f"Download failed: {e}") from e
    
    @aretry_with_backoff(max_retries=3)
    async def adownload_file(
        self,
        remote_path: str,
        local_path: Union[str, Path],
        metadata: Optional[StorageMetadata] = None
    ) -> None:
        """Async download with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        local_path = Path(local_path)
        validate_path(str(local_path))
        
        try:
            container = await self._get_async_container()
            blob_client = container.get_blob_client(remote_path)
            
            # Ensure local directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with streaming for large files
            if self.config.chunk_size > 0:
                async with StreamingDownloader(blob_client, self.config.chunk_size) as downloader:
                    async with open(local_path, "wb") as f:
                        async for chunk in downloader:
                            f.write(chunk)
            else:
                # Simple download for small files
                async with open(local_path, "wb") as f:
                    blob_data = await blob_client.download_blob()
                    f.write(await blob_data.readall())
            
            print(f"✅ Download succeeded: '{remote_path}' → '{local_path}'")
            
        except ResourceNotFoundError:
            raise NotFoundError(f"Blob not found: {remote_path}")
        except AzureError as e:
            raise StorageError(f"Download failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def list_files(self, remote_prefix: str = "") -> List[str]:
        """List files with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            container = self._get_sync_container()
            blobs = [
                blob.name for blob in container.list_blobs(name_starts_with=remote_prefix)
            ]
            print(f"📋 Listed {len(blobs)} blobs under prefix '{remote_prefix}'")
            return blobs
        except AzureError as e:
            raise StorageError(f"List operation failed: {e}") from e
    
    async def alist_files(self, remote_prefix: str = "") -> List[str]:
        """Async list files with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            container = await self._get_async_container()
            blobs = []
            async for blob in container.list_blobs(name_starts_with=remote_prefix):
                blobs.append(blob.name)
            print(f"📋 Listed {len(blobs)} blobs under prefix '{remote_prefix}'")
            return blobs
        except AzureError as e:
            raise StorageError(f"List operation failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def download_folder(
        self,
        remote_prefix: str,
        local_dir: Union[str, Path]
    ) -> None:
        """Download entire folder with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        local_dir = Path(local_dir)
        validate_path(str(local_dir))
        
        try:
            blobs = self.list_files(remote_prefix)
            if not blobs:
                print(f"⚠️  No files found under prefix '{remote_prefix}'")
                return
            
            local_dir.mkdir(parents=True, exist_ok=True)
            
            for blob_name in blobs:
                # Calculate relative path from prefix
                if remote_prefix and blob_name.startswith(remote_prefix):
                    relative_path = blob_name[len(remote_prefix):].lstrip('/')
                else:
                    relative_path = blob_name
                
                if relative_path:  # Skip if it's the prefix itself
                    dest_path = local_dir / relative_path
                    self.download_file(blob_name, dest_path)
            
            print(f"✅ Folder download succeeded: '{remote_prefix}' → '{local_dir}'")
            
        except Exception as e:
            raise StorageError(f"Folder download failed: {e}") from e
    
    async def adownload_folder(
        self,
        remote_prefix: str,
        local_dir: Union[str, Path]
    ) -> None:
        """Async download entire folder with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        local_dir = Path(local_dir)
        validate_path(str(local_dir))
        
        try:
            blobs = await self.alist_files(remote_prefix)
            if not blobs:
                print(f"⚠️  No files found under prefix '{remote_prefix}'")
                return
            
            local_dir.mkdir(parents=True, exist_ok=True)
            
            for blob_name in blobs:
                # Calculate relative path from prefix
                if remote_prefix and blob_name.startswith(remote_prefix):
                    relative_path = blob_name[len(remote_prefix):].lstrip('/')
                else:
                    relative_path = blob_name
                
                if relative_path:  # Skip if it's the prefix itself
                    dest_path = local_dir / relative_path
                    await self.adownload_file(blob_name, dest_path)
            
            print(f"✅ Folder download succeeded: '{remote_prefix}' → '{local_dir}'")
            
        except Exception as e:
            raise StorageError(f"Folder download failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def delete_file(self, remote_path: str) -> None:
        """Delete a file with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            container = self._get_sync_container()
            container.delete_blob(remote_path)
            print(f"🗑️  Deletion succeeded: '{remote_path}'")
        except ResourceNotFoundError:
            raise NotFoundError(f"Blob not found: {remote_path}")
        except AzureError as e:
            raise StorageError(f"Deletion failed: {e}") from e
    
    async def adelete_file(self, remote_path: str) -> None:
        """Async delete a file with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            container = await self._get_async_container()
            await container.delete_blob(remote_path)
            print(f"🗑️  Deletion succeeded: '{remote_path}'")
        except ResourceNotFoundError:
            raise NotFoundError(f"Blob not found: {remote_path}")
        except AzureError as e:
            raise StorageError(f"Deletion failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def delete_folder(self, remote_prefix: str) -> None:
        """Delete entire folder with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            blobs = self.list_files(remote_prefix)
            if not blobs:
                print(f"⚠️  No files found under prefix '{remote_prefix}'")
                return
            
            container = self._get_sync_container()
            for blob_name in blobs:
                container.delete_blob(blob_name)
            
            print(f"🗑️  Folder deletion succeeded: '{remote_prefix}' ({len(blobs)} files)")
            
        except Exception as e:
            raise StorageError(f"Folder deletion failed: {e}") from e
    
    async def adelete_folder(self, remote_prefix: str) -> None:
        """Async delete entire folder with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            blobs = await self.alist_files(remote_prefix)
            if not blobs:
                print(f"⚠️  No files found under prefix '{remote_prefix}'")
                return
            
            container = await self._get_async_container()
            for blob_name in blobs:
                await container.delete_blob(blob_name)
            
            print(f"🗑️  Folder deletion succeeded: '{remote_prefix}' ({len(blobs)} files)")
            
        except Exception as e:
            raise StorageError(f"Folder deletion failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            container = self._get_sync_container()
            blob_client = container.get_blob_client(remote_path)
            blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
        except AzureError as e:
            raise StorageError(f"File existence check failed: {e}") from e
    
    async def afile_exists(self, remote_path: str) -> bool:
        """Async check if file exists with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            container = await self._get_async_container()
            blob_client = container.get_blob_client(remote_path)
            await blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
        except AzureError as e:
            raise StorageError(f"File existence check failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def get_file_info(self, remote_path: str) -> StorageObject:
        """Get file information with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            container = self._get_sync_container()
            blob_client = container.get_blob_client(remote_path)
            properties = blob_client.get_blob_properties()
            
            # Convert Azure properties to StorageObject
            metadata = StorageMetadata(
                content_type=properties.content_settings.content_type,
                content_encoding=properties.content_settings.content_encoding,
                cache_control=properties.cache_control,
                custom_metadata=properties.metadata or {}
            )
            
            return StorageObject(
                name=properties.name,
                size=properties.size,
                last_modified=properties.last_modified.isoformat(),
                etag=properties.etag,
                is_directory=False,
                metadata=metadata
            )
            
        except ResourceNotFoundError:
            raise NotFoundError(f"Blob not found: {remote_path}")
        except AzureError as e:
            raise StorageError(f"File info retrieval failed: {e}") from e
    
    async def aget_file_info(self, remote_path: str) -> StorageObject:
        """Async get file information with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            container = await self._get_async_container()
            blob_client = container.get_blob_client(remote_path)
            properties = await blob_client.get_blob_properties()
            
            # Convert Azure properties to StorageObject
            metadata = StorageMetadata(
                content_type=properties.content_settings.content_type,
                content_encoding=properties.content_settings.content_encoding,
                cache_control=properties.cache_control,
                custom_metadata=properties.metadata or {}
            )
            
            return StorageObject(
                name=properties.name,
                size=properties.size,
                last_modified=properties.last_modified.isoformat(),
                etag=properties.etag,
                is_directory=False,
                metadata=metadata
            )
            
        except ResourceNotFoundError:
            raise NotFoundError(f"Blob not found: {remote_path}")
        except AzureError as e:
            raise StorageError(f"File info retrieval failed: {e}") from e
