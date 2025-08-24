"""Streaming operations for efficient file handling in FlexiStore."""

import asyncio
import aiofiles
from pathlib import Path
from typing import AsyncIterator, Optional, Union, Callable
from contextlib import asynccontextmanager

from ..core.base import StorageMetadata
from ..core.exceptions import StorageError, ValidationError


class StreamingUploader:
    """Handles streaming uploads for large files."""
    
    def __init__(self, chunk_size: int = 8 * 1024 * 1024):  # 8MB default
        self.chunk_size = chunk_size
    
    async def upload_in_chunks(
        self,
        local_path: Union[str, Path],
        upload_chunk: Callable[[bytes, int, bool], None],
        metadata: Optional[StorageMetadata] = None
    ) -> None:
        """Upload a file in chunks using a callback function."""
        local_path = Path(local_path)
        
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        file_size = local_path.stat().st_size
        total_chunks = (file_size + self.chunk_size - 1) // self.chunk_size
        
        async with aiofiles.open(local_path, 'rb') as file:
            chunk_number = 0
            
            while True:
                chunk = await file.read(self.chunk_size)
                if not chunk:
                    break
                
                is_last_chunk = chunk_number == total_chunks - 1
                await upload_chunk(chunk, chunk_number, is_last_chunk)
                chunk_number += 1
    
    async def upload_with_progress(
        self,
        local_path: Union[str, Path],
        upload_chunk: Callable[[bytes, int, bool], None],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """Upload with progress tracking."""
        local_path = Path(local_path)
        file_size = local_path.stat().st_size
        uploaded_bytes = 0
        
        async def progress_upload(chunk: bytes, chunk_number: int, is_last_chunk: bool):
            nonlocal uploaded_bytes
            await upload_chunk(chunk, chunk_number, is_last_chunk)
            uploaded_bytes += len(chunk)
            
            if progress_callback:
                progress_callback(uploaded_bytes, file_size)
        
        await self.upload_in_chunks(local_path, progress_upload)


class StreamingDownloader:
    """Handles streaming downloads for large files."""
    
    def __init__(self, chunk_size: int = 8 * 1024 * 1024):  # 8MB default
        self.chunk_size = chunk_size
    
    async def download_in_chunks(
        self,
        download_chunk: Callable[[int], bytes],
        local_path: Union[str, Path],
        total_size: int
    ) -> None:
        """Download a file in chunks using a callback function."""
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        total_chunks = (total_size + self.chunk_size - 1) // self.chunk_size
        
        async with aiofiles.open(local_path, 'wb') as file:
            for chunk_number in range(total_chunks):
                chunk = await download_chunk(chunk_number)
                await file.write(chunk)
    
    async def download_with_progress(
        self,
        download_chunk: Callable[[int], bytes],
        local_path: Union[str, Path],
        total_size: int,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """Download with progress tracking."""
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        total_chunks = (total_size + self.chunk_size - 1) // self.chunk_size
        downloaded_bytes = 0
        
        async with aiofiles.open(local_path, 'wb') as file:
            for chunk_number in range(total_chunks):
                chunk = await download_chunk(chunk_number)
                await file.write(chunk)
                downloaded_bytes += len(chunk)
                
                if progress_callback:
                    progress_callback(downloaded_bytes, total_size)


class MemoryEfficientProcessor:
    """Processes large files with minimal memory usage."""
    
    def __init__(self, buffer_size: int = 1024 * 1024):  # 1MB buffer
        self.buffer_size = buffer_size
    
    async def process_file_by_line(
        self,
        file_path: Union[str, Path],
        processor: Callable[[str], str],
        output_path: Optional[Union[str, Path]] = None
    ) -> None:
        """Process a file line by line to minimize memory usage."""
        file_path = Path(file_path)
        
        if output_path is None:
            output_path = file_path.with_suffix('.processed' + file_path.suffix)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'r') as infile, aiofiles.open(output_path, 'w') as outfile:
            async for line in infile:
                processed_line = processor(line)
                await outfile.write(processed_line)
    
    async def process_file_by_chunk(
        self,
        file_path: Union[str, Path],
        processor: Callable[[bytes], bytes],
        output_path: Optional[Union[str, Path]] = None
    ) -> None:
        """Process a file in chunks to minimize memory usage."""
        file_path = Path(file_path)
        
        if output_path is None:
            output_path = file_path.with_suffix('.processed' + file_path.suffix)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'rb') as infile, aiofiles.open(output_path, 'wb') as outfile:
            while True:
                chunk = await infile.read(self.buffer_size)
                if not chunk:
                    break
                
                processed_chunk = processor(chunk)
                await outfile.write(processed_chunk)


@asynccontextmanager
async def streaming_context():
    """Context manager for streaming operations."""
    try:
        yield
    except Exception as e:
        raise StorageError(f"Streaming operation failed: {e}")


class ChunkedFileReader:
    """Reads files in configurable chunks."""
    
    def __init__(self, chunk_size: int = 8 * 1024 * 1024):
        self.chunk_size = chunk_size
    
    async def read_chunks(self, file_path: Union[str, Path]) -> AsyncIterator[bytes]:
        """Read a file in chunks."""
        file_path = Path(file_path)
        
        async with aiofiles.open(file_path, 'rb') as file:
            while True:
                chunk = await file.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
    
    async def read_chunks_with_metadata(
        self, 
        file_path: Union[str, Path]
    ) -> AsyncIterator[tuple[bytes, int, int]]:
        """Read a file in chunks with metadata (chunk_data, chunk_number, total_chunks)."""
        file_path = Path(file_path)
        file_size = file_path.stat().st_size
        total_chunks = (file_size + self.chunk_size - 1) // self.chunk_size
        
        async with aiofiles.open(file_path, 'rb') as file:
            chunk_number = 0
            while True:
                chunk = await file.read(self.chunk_size)
                if not chunk:
                    break
                
                yield chunk, chunk_number, total_chunks
                chunk_number += 1


class ChunkedFileWriter:
    """Writes files in configurable chunks."""
    
    def __init__(self, chunk_size: int = 8 * 1024 * 1024):
        self.chunk_size = chunk_size
    
    async def write_chunks(
        self, 
        file_path: Union[str, Path], 
        chunks: AsyncIterator[bytes]
    ) -> None:
        """Write chunks to a file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as file:
            async for chunk in chunks:
                await file.write(chunk)
    
    async def write_chunks_with_validation(
        self, 
        file_path: Union[str, Path], 
        chunks: AsyncIterator[bytes],
        expected_size: Optional[int] = None
    ) -> None:
        """Write chunks with size validation."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        written_size = 0
        
        async with aiofiles.open(file_path, 'wb') as file:
            async for chunk in chunks:
                await file.write(chunk)
                written_size += len(chunk)
        
        if expected_size is not None and written_size != expected_size:
            raise ValidationError(
                f"File size mismatch: expected {expected_size}, got {written_size}",
                field="file_size",
                value=written_size
            )


# Utility functions for common streaming operations
async def copy_file_streaming(
    source_path: Union[str, Path],
    dest_path: Union[str, Path],
    chunk_size: int = 8 * 1024 * 1024
) -> None:
    """Copy a file using streaming to minimize memory usage."""
    reader = ChunkedFileReader(chunk_size)
    writer = ChunkedFileWriter(chunk_size)
    
    chunks = reader.read_chunks(source_path)
    await writer.write_chunks(dest_path, chunks)


async def copy_file_with_progress(
    source_path: Union[str, Path],
    dest_path: Union[str, Path],
    chunk_size: int = 8 * 1024 * 1024,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> None:
    """Copy a file with progress tracking."""
    source_path = Path(source_path)
    file_size = source_path.stat().st_size
    
    reader = ChunkedFileReader(chunk_size)
    writer = ChunkedFileWriter(chunk_size)
    
    copied_bytes = 0
    
    async def progress_chunks():
        nonlocal copied_bytes
        async for chunk in reader.read_chunks(source_path):
            copied_bytes += len(chunk)
            if progress_callback:
                progress_callback(copied_bytes, file_size)
            yield chunk
    
    await writer.write_chunks(dest_path, progress_chunks())
