"""CLI command implementations for FlexiStore."""

import os
from typing import List, Optional

from flexistore.core.base import StorageManager
from .utils import (
    confirm, get_input, validate_file_path, validate_directory_path,
    print_error, print_success, print_warning, print_info, format_file_size
)


class FileOperations:
    """File operation commands for the CLI."""
    
    def __init__(self, manager: StorageManager):
        self.manager = manager
    
    def upload_file(self) -> bool:
        """Handle file upload operation."""
        print("\n📤 Upload File")
        print("-" * 20)
        
        local_path = get_input("Local file path to upload")
        if not local_path or not validate_file_path(local_path):
            return False
        
        # Get file size for confirmation
        file_size = os.path.getsize(local_path)
        print_info(f"File size: {format_file_size(file_size)}")
        
        remote_path = get_input("Remote blob path")
        if not remote_path:
            return False
        
        if not confirm(f"Upload '{local_path}' → '{remote_path}'?"):
            print_info("Upload cancelled.")
            return False
        
        try:
            print_info("Uploading file...")
            self.manager.upload_file(local_path, remote_path)
            print_success(f"File uploaded successfully to '{remote_path}'")
            return True
        except Exception as e:
            print_error(f"Upload failed: {e}")
            return False
    
    def download_file(self) -> bool:
        """Handle file download operation."""
        print("\n📥 Download File")
        print("-" * 20)
        
        remote_path = get_input("Remote blob path to download")
        if not remote_path:
            return False
        
        # Check if file exists
        try:
            if not self.manager.file_exists(remote_path):
                print_error(f"File '{remote_path}' does not exist in storage.")
                return False
        except Exception as e:
            print_warning(f"Could not verify file existence: {e}")
        
        local_path = get_input("Local file path to save")
        if not local_path:
            return False
        
        # Validate local directory
        local_dir = os.path.dirname(local_path)
        if local_dir and not validate_directory_path(local_dir):
            return False
        
        # Check if local file already exists
        if os.path.exists(local_path):
            if not confirm(f"File '{local_path}' already exists. Overwrite?"):
                print_info("Download cancelled.")
                return False
        
        if not confirm(f"Download '{remote_path}' → '{local_path}'?"):
            print_info("Download cancelled.")
            return False
        
        try:
            print_info("Downloading file...")
            self.manager.download_file(remote_path, local_path)
            
            # Show downloaded file size
            if os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                print_success(f"File downloaded successfully ({format_file_size(file_size)})")
            else:
                print_success("File downloaded successfully")
            return True
        except Exception as e:
            print_error(f"Download failed: {e}")
            return False
    
    def list_files(self) -> bool:
        """Handle file listing operation."""
        print("\n📋 List Files")
        print("-" * 20)
        
        prefix = get_input("Path prefix (optional, press Enter for all files)", required=False)
        
        try:
            print_info("Retrieving file list...")
            files = self.manager.list_files(prefix or "")
            
            if not files:
                print_info("No files found.")
                return True
            
            print(f"\n📁 Found {len(files)} file(s):")
            print("-" * 60)
            
            for i, file_path in enumerate(files, 1):
                try:
                    # Try to get file info for size
                    file_info = self.manager.get_file_info(file_path)
                    if hasattr(file_info, 'size') and file_info.size is not None:
                        size_str = f" ({format_file_size(file_info.size)})"
                    else:
                        size_str = ""
                except Exception:
                    size_str = ""
                
                print(f"{i:3d}. {file_path}{size_str}")
            
            print("-" * 60)
            return True
        except Exception as e:
            print_error(f"Failed to list files: {e}")
            return False
    
    def delete_file(self) -> bool:
        """Handle file deletion operation."""
        print("\n🗑️  Delete File")
        print("-" * 20)
        
        remote_path = get_input("Remote blob path to delete")
        if not remote_path:
            return False
        
        # Check if file exists
        try:
            if not self.manager.file_exists(remote_path):
                print_error(f"File '{remote_path}' does not exist in storage.")
                return False
        except Exception as e:
            print_warning(f"Could not verify file existence: {e}")
        
        if not confirm(f"⚠️  Delete '{remote_path}' permanently?"):
            print_info("Deletion cancelled.")
            return False
        
        try:
            print_info("Deleting file...")
            self.manager.delete_file(remote_path)
            print_success(f"File '{remote_path}' deleted successfully")
            return True
        except Exception as e:
            print_error(f"Deletion failed: {e}")
            return False
    
    def download_folder(self) -> bool:
        """Handle folder download operation."""
        print("\n📥 Download Folder")
        print("-" * 20)
        
        remote_prefix = get_input("Remote folder prefix")
        if not remote_prefix:
            return False
        
        local_dir = get_input("Local directory to save files")
        if not local_dir or not validate_directory_path(local_dir):
            return False
        
        if not confirm(f"Download all files with prefix '{remote_prefix}' to '{local_dir}'?"):
            print_info("Download cancelled.")
            return False
        
        try:
            print_info("Downloading folder...")
            self.manager.download_folder(remote_prefix, local_dir)
            print_success(f"Folder downloaded successfully to '{local_dir}'")
            return True
        except Exception as e:
            print_error(f"Folder download failed: {e}")
            return False
