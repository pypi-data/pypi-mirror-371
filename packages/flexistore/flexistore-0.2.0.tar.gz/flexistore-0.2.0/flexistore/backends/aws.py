"""Enhanced AWS S3 Storage Manager with async support and advanced features."""

import asyncio
import os
from pathlib import Path
from typing import List, Optional, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from botocore.config import Config
from boto3.session import Session
from boto3.resources.base import ServiceResource

from ..core.base import StorageManager, StorageConfig, StorageMetadata, StorageObject
from ..core.exceptions import (
    StorageError, ConnectionError, ValidationError, NotFoundError, 
    AlreadyExistsError, RetryableError
)
from ..utils.retry import retry_with_backoff, aretry_with_backoff
from ..utils.validation import validate_path, validate_url
from ..utils.streaming import StreamingUploader, StreamingDownloader


class AWSStorageConfig(StorageConfig):
    """AWS-specific storage configuration."""
    
    def __init__(
        self,
        bucket_name: str,
        region_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
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
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key


class AWSStorageManager(StorageManager):
    """Enhanced AWS S3 Storage Manager with async support."""
    
    def __init__(self, config: AWSStorageConfig):
        self.config = config
        self._sync_session: Optional[Session] = None
        self._sync_s3: Optional[ServiceResource] = None
        self._sync_bucket = None
        self._async_session: Optional[Session] = None
        self._async_s3: Optional[ServiceResource] = None
        self._async_bucket = None
        self._initialized = False
        
    def _get_sync_session(self) -> Session:
        """Get or create synchronous AWS session."""
        if self._sync_session is None:
            self._sync_session = Session(
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
                region_name=self.config.region_name
            )
        return self._sync_session
    
    def _get_sync_s3(self) -> ServiceResource:
        """Get or create synchronous S3 resource."""
        if self._sync_s3 is None:
            session = self._get_sync_session()
            self._sync_s3 = session.resource(
                's3',
                verify=self.config.verify_ssl,
                config=Config(
                    connect_timeout=self.config.timeout,
                    read_timeout=self.config.timeout,
                    retries={'max_attempts': self.config.max_retries}
                )
            )
        return self._sync_s3
    
    def _get_sync_bucket(self):
        """Get or create synchronous bucket resource."""
        if self._sync_bucket is None:
            s3 = self._get_sync_s3()
            self._sync_bucket = s3.Bucket(self.config.bucket_name)
        return self._sync_bucket
    
    def _get_async_session(self) -> Session:
        """Get or create asynchronous AWS session."""
        if self._async_session is None:
            self._async_session = Session(
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
                region_name=self.config.region_name
            )
        return self._async_session
    
    def _get_async_s3(self) -> ServiceResource:
        """Get or create asynchronous S3 resource."""
        if self._async_s3 is None:
            session = self._get_async_session()
            self._async_s3 = session.resource(
                's3',
                verify=self.config.verify_ssl,
                config=Config(
                    connect_timeout=self.config.timeout,
                    read_timeout=self.config.timeout,
                    retries={'max_attempts': self.config.max_retries}
                )
            )
        return self._async_s3
    
    def _get_async_bucket(self):
        """Get or create asynchronous bucket resource."""
        if self._async_bucket is None:
            s3 = self._get_async_s3()
            self._async_bucket = s3.Bucket(self.config.bucket_name)
        return self._async_bucket
    
    @retry_with_backoff(max_retries=3)
    def initialize(self) -> None:
        """Initialize synchronous connections and verify bucket exists."""
        try:
            s3 = self._get_sync_s3()
            # Verify bucket exists by checking its location
            s3.meta.client.head_bucket(Bucket=self.config.bucket_name)
            self._initialized = True
            print(f"✅ Connected to AWS bucket '{self.config.bucket_name}' successfully.")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket '{self.config.bucket_name}' not found")
            else:
                raise ConnectionError(f"Failed to connect to AWS: {e}")
    
    async def ainitialize(self) -> None:
        """Initialize async connections and verify bucket exists."""
        try:
            s3 = self._get_async_s3()
            # Verify bucket exists by checking its location
            await asyncio.get_event_loop().run_in_executor(
                None, 
                s3.meta.client.head_bucket, 
                Bucket=self.config.bucket_name
            )
            self._initialized = True
            print(f"✅ Connected to AWS bucket '{self.config.bucket_name}' successfully.")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket '{self.config.bucket_name}' not found")
            else:
                raise ConnectionError(f"Failed to connect to AWS: {e}")
    
    def close(self) -> None:
        """Close synchronous connections."""
        if self._sync_s3:
            # boto3 resources don't have explicit close methods
            self._sync_s3 = None
        if self._sync_session:
            self._sync_session = None
        if self._sync_bucket:
            self._sync_bucket = None
        self._initialized = False
    
    async def aclose(self) -> None:
        """Close async connections."""
        if self._async_s3:
            # boto3 resources don't have explicit close methods
            self._async_s3 = None
        if self._async_session:
            self._async_session = None
        if self._async_bucket:
            self._async_bucket = None
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
            bucket = self._get_sync_bucket()
            
            # Convert metadata to S3 format
            extra_args = {}
            if metadata:
                if metadata.content_type:
                    extra_args['ContentType'] = metadata.content_type
                if metadata.content_encoding:
                    extra_args['ContentEncoding'] = metadata.content_encoding
                if metadata.cache_control:
                    extra_args['CacheControl'] = metadata.cache_control
                if metadata.custom_metadata:
                    extra_args['Metadata'] = {
                        k: str(v) for k, v in metadata.custom_metadata.items()
                    }
            
            bucket.upload_file(
                str(local_path),
                remote_path,
                ExtraArgs=extra_args
            )
            
            print(f"✅ Upload succeeded: '{local_path}' → '{remote_path}'")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"Upload failed: {e}")
        except Exception as e:
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
            bucket = self._get_async_bucket()
            
            # Convert metadata to S3 format
            extra_args = {}
            if metadata:
                if metadata.content_type:
                    extra_args['ContentType'] = metadata.content_type
                if metadata.content_encoding:
                    extra_args['ContentEncoding'] = metadata.content_encoding
                if metadata.cache_control:
                    extra_args['CacheControl'] = metadata.cache_control
                if metadata.custom_metadata:
                    extra_args['Metadata'] = {
                        k: str(v) for k, v in metadata.custom_metadata.items()
                    }
            
            # Run upload in executor since boto3 doesn't have async upload
            await asyncio.get_event_loop().run_in_executor(
                None,
                bucket.upload_file,
                str(local_path),
                remote_path,
                extra_args
            )
            
            print(f"✅ Upload succeeded: '{local_path}' → '{remote_path}'")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"Upload failed: {e}")
        except Exception as e:
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
            bucket = self._get_sync_bucket()
            
            # Ensure local directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with streaming for large files
            if self.config.chunk_size > 0:
                # For now, use simple download since boto3 streaming is complex
                bucket.download_file(remote_path, str(local_path))
            else:
                bucket.download_file(remote_path, str(local_path))
            
            print(f"✅ Download succeeded: '{remote_path}' → '{local_path}'")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise NotFoundError(f"Object not found: {remote_path}")
            elif error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"Download failed: {e}")
        except Exception as e:
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
            bucket = self._get_async_bucket()
            
            # Ensure local directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Run download in executor since boto3 doesn't have async download
            await asyncio.get_event_loop().run_in_executor(
                None,
                bucket.download_file,
                remote_path,
                str(local_path)
            )
            
            print(f"✅ Download succeeded: '{remote_path}' → '{local_path}'")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise NotFoundError(f"Object not found: {remote_path}")
            elif error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"Download failed: {e}")
        except Exception as e:
            raise StorageError(f"Download failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def list_files(self, remote_prefix: str = "") -> List[str]:
        """List files with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            bucket = self._get_sync_bucket()
            objects = [obj.key for obj in bucket.objects.filter(Prefix=remote_prefix)]
            print(f"📋 Listed {len(objects)} objects under prefix '{remote_prefix}'")
            return objects
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"List operation failed: {e}")
        except Exception as e:
            raise StorageError(f"List operation failed: {e}") from e
    
    async def alist_files(self, remote_prefix: str = "") -> List[str]:
        """Async list files with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            bucket = self._get_async_bucket()
            # Run list operation in executor
            objects = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: [obj.key for obj in bucket.objects.filter(Prefix=remote_prefix)]
            )
            print(f"📋 Listed {len(objects)} objects under prefix '{remote_prefix}'")
            return objects
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"List operation failed: {e}")
        except Exception as e:
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
            objects = self.list_files(remote_prefix)
            if not objects:
                print(f"⚠️  No objects found under prefix '{remote_prefix}'")
                return
            
            local_dir.mkdir(parents=True, exist_ok=True)
            
            for obj_key in objects:
                # Calculate relative path from prefix
                if remote_prefix and obj_key.startswith(remote_prefix):
                    relative_path = obj_key[len(remote_prefix):].lstrip('/')
                else:
                    relative_path = obj_key
                
                if relative_path:  # Skip if it's the prefix itself
                    dest_path = local_dir / relative_path
                    self.download_file(obj_key, dest_path)
            
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
            objects = await self.alist_files(remote_prefix)
            if not objects:
                print(f"⚠️  No objects found under prefix '{remote_prefix}'")
                return
            
            local_dir.mkdir(parents=True, exist_ok=True)
            
            for obj_key in objects:
                # Calculate relative path from prefix
                if remote_prefix and obj_key.startswith(remote_prefix):
                    relative_path = obj_key[len(remote_prefix):].lstrip('/')
                else:
                    relative_path = obj_key
                
                if relative_path:  # Skip if it's the prefix itself
                    dest_path = local_dir / relative_path
                    await self.adownload_file(obj_key, dest_path)
            
            print(f"✅ Folder download succeeded: '{remote_prefix}' → '{local_dir}'")
            
        except Exception as e:
            raise StorageError(f"Folder download failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def delete_file(self, remote_path: str) -> None:
        """Delete a file with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            bucket = self._get_sync_bucket()
            bucket.Object(remote_path).delete()
            print(f"🗑️  Deletion succeeded: '{remote_path}'")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise NotFoundError(f"Object not found: {remote_path}")
            elif error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"Deletion failed: {e}")
        except Exception as e:
            raise StorageError(f"Deletion failed: {e}") from e
    
    async def adelete_file(self, remote_path: str) -> None:
        """Async delete a file with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            bucket = self._get_async_bucket()
            # Run delete operation in executor
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: bucket.Object(remote_path).delete()
            )
            print(f"🗑️  Deletion succeeded: '{remote_path}'")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise NotFoundError(f"Object not found: {remote_path}")
            elif error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"Deletion failed: {e}")
        except Exception as e:
            raise StorageError(f"Deletion failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def delete_folder(self, remote_prefix: str) -> None:
        """Delete entire folder with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            objects = self.list_files(remote_prefix)
            if not objects:
                print(f"⚠️  No objects found under prefix '{remote_prefix}'")
                return
            
            bucket = self._get_sync_bucket()
            # Delete all objects in the folder
            bucket.objects.filter(Prefix=remote_prefix).delete()
            
            print(f"🗑️  Folder deletion succeeded: '{remote_prefix}' ({len(objects)} objects)")
            
        except Exception as e:
            raise StorageError(f"Folder deletion failed: {e}") from e
    
    async def adelete_folder(self, remote_prefix: str) -> None:
        """Async delete entire folder with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            objects = await self.alist_files(remote_prefix)
            if not objects:
                print(f"⚠️  No objects found under prefix '{remote_prefix}'")
                return
            
            bucket = self._get_async_bucket()
            # Run delete operation in executor
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: bucket.objects.filter(Prefix=remote_prefix).delete()
            )
            
            print(f"🗑️  Folder deletion succeeded: '{remote_prefix}' ({len(objects)} objects)")
            
        except Exception as e:
            raise StorageError(f"Folder deletion failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            bucket = self._get_sync_bucket()
            bucket.Object(remote_path).load()
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                return False
            elif error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"File existence check failed: {e}")
        except Exception as e:
            raise StorageError(f"File existence check failed: {e}") from e
    
    async def afile_exists(self, remote_path: str) -> bool:
        """Async check if file exists with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            bucket = self._get_async_bucket()
            # Run existence check in executor
            return await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.file_exists(remote_path)
            )
        except Exception as e:
            raise StorageError(f"File existence check failed: {e}") from e
    
    @retry_with_backoff(max_retries=3)
    def get_file_info(self, remote_path: str) -> StorageObject:
        """Get file information with retry mechanism."""
        if not self._initialized:
            self.initialize()
        
        try:
            bucket = self._get_sync_bucket()
            obj = bucket.Object(remote_path)
            obj.load()  # Load object metadata
            
            # Convert S3 object info to StorageObject
            metadata = StorageMetadata(
                content_type=obj.content_type,
                content_encoding=obj.content_encoding,
                cache_control=obj.cache_control,
                custom_metadata=obj.metadata or {}
            )
            
            return StorageObject(
                name=obj.key,
                size=obj.content_length,
                last_modified=obj.last_modified.isoformat(),
                etag=obj.e_tag.strip('"'),  # Remove quotes from ETag
                is_directory=False,
                metadata=metadata
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise NotFoundError(f"Object not found: {remote_path}")
            elif error_code == 'NoSuchBucket':
                raise NotFoundError(f"Bucket not found: {self.config.bucket_name}")
            elif error_code == 'AccessDenied':
                raise StorageError(f"Access denied: {e}")
            else:
                raise StorageError(f"File info retrieval failed: {e}")
        except Exception as e:
            raise StorageError(f"File info retrieval failed: {e}") from e
    
    async def aget_file_info(self, remote_path: str) -> StorageObject:
        """Async get file information with retry mechanism."""
        if not self._initialized:
            await self.ainitialize()
        
        try:
            # Run info retrieval in executor
            return await asyncio.get_event_loop().run_in_executor(
                None,
                self.get_file_info,
                remote_path
            )
        except Exception as e:
            raise StorageError(f"File info retrieval failed: {e}") from e
