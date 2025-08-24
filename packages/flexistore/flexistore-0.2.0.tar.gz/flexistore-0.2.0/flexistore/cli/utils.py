"""CLI utility functions for FlexiStore."""

import os
from typing import Optional


def confirm(prompt: str) -> bool:
    """Ask user for confirmation."""
    response = input(f"{prompt} (y/N): ").strip().lower()
    return response in ("y", "yes")


def get_input(prompt: str, required: bool = True) -> Optional[str]:
    """Get user input with optional validation."""
    while True:
        value = input(f"{prompt}: ").strip()
        if value or not required:
            return value if value else None
        print("This field is required. Please enter a value.")


def validate_file_path(file_path: str) -> bool:
    """Validate that a file path exists and is readable."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return False
    
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a file.")
        return False
    
    if not os.access(file_path, os.R_OK):
        print(f"Error: File '{file_path}' is not readable.")
        return False
    
    return True


def validate_directory_path(dir_path: str) -> bool:
    """Validate that a directory path exists and is writable."""
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")
        except OSError as e:
            print(f"Error: Cannot create directory '{dir_path}': {e}")
            return False
    
    if not os.path.isdir(dir_path):
        print(f"Error: '{dir_path}' is not a directory.")
        return False
    
    if not os.access(dir_path, os.W_OK):
        print(f"Error: Directory '{dir_path}' is not writable.")
        return False
    
    return True


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def print_error(message: str) -> None:
    """Print an error message with formatting."""
    print(f"❌ Error: {message}")


def print_success(message: str) -> None:
    """Print a success message with formatting."""
    print(f"✅ {message}")


def print_warning(message: str) -> None:
    """Print a warning message with formatting."""
    print(f"⚠️  Warning: {message}")


def print_info(message: str) -> None:
    """Print an info message with formatting."""
    print(f"ℹ️  {message}")
