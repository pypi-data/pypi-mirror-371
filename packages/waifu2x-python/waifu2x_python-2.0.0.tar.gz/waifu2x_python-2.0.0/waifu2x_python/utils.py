"""Utility functions for the waifu2x-python package.

This module provides various utility functions for file operations, path handling,
and other common tasks used throughout the package.
"""

import os
import sys
import shutil
import logging
import tempfile
import platform
from typing import List, Optional, Union, Tuple, Set, Dict, Any, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import mimetypes

from .exceptions import Waifu2xFileError
from .config import DEFAULT_CONFIG

# Configure logging
logger = logging.getLogger(__name__)

# Add more image formats to the default mimetypes
mimetypes.add_type('image/webp', '.webp')

def get_frame_list(
    folder: Union[str, Path], 
    extensions: Optional[List[str]] = None,
    recursive: bool = False
) -> List[str]:
    """
    Get sorted list of image files from a folder with optional recursion.
    
    Args:
        folder: Path to folder containing image files
        extensions: List of file extensions to include (with leading dot).
                   If None, uses DEFAULT_CONFIG["supported_formats"]
        recursive: If True, search for files recursively in subdirectories
        
    Returns:
        Sorted list of absolute file paths
        
    Raises:
        Waifu2xFileError: If the folder doesn't exist or is not accessible
    """
    if extensions is None:
        extensions = DEFAULT_CONFIG["supported_formats"]
    
    folder_path = Path(folder).resolve()
    
    if not folder_path.exists():
        raise Waifu2xFileError("Folder does not exist", str(folder_path))
    if not folder_path.is_dir():
        raise Waifu2xFileError("Path is not a directory", str(folder_path))
    
    # Create a set of extensions for faster lookups (case-insensitive)
    ext_set = {ext.lower() for ext in extensions}
    ext_set.update(ext.upper() for ext in extensions)
    
    # Find all matching files
    frame_files = []
    glob_pattern = "**/*" if recursive else "*"
    
    for file_path in folder_path.glob(glob_pattern):
        if file_path.is_file() and file_path.suffix.lower() in ext_set:
            frame_files.append(str(file_path.absolute()))
    
    # Sort files naturally
    frame_files.sort()
    
    if not frame_files:
        logger.warning(f"No image files found in {folder_path} with extensions: {', '.join(extensions)}")
    
    return frame_files

def validate_waifu2x_path(executable_path: Union[str, Path]) -> bool:
    """
    Validate that waifu2x executable exists and is executable.
    
    Args:
        executable_path: Path to waifu2x-ncnn-vulkan executable
        
    Returns:
        bool: True if the executable is valid and accessible, False otherwise
    """
    try:
        exec_path = Path(executable_path).resolve()
        
        # Check if file exists
        if not exec_path.exists():
            logger.error(f"waifu2x executable not found at: {exec_path}")
            return False
            
        # Check if it's a file
        if not exec_path.is_file():
            logger.error(f"Path is not a file: {exec_path}")
            return False
            
        # Check if it's executable
        if not os.access(exec_path, os.X_OK):
            # On Windows, we can't reliably check execute permission
            if platform.system() != 'Windows':
                logger.error(f"File is not executable: {exec_path}")
                return False
                
        return True
        
    except (TypeError, ValueError, OSError) as e:
        logger.error(f"Error validating waifu2x path: {e}")
        return False

def ensure_folder_exists(folder_path: Union[str, Path]) -> str:
    """
    Ensure folder exists, create if it doesn't.
    
    Args:
        folder_path: Path to the folder
        
    Returns:
        str: Absolute path to the folder
        
    Raises:
        Waifu2xFileError: If folder cannot be created or is not writable
    """
    try:
        folder = Path(folder_path).resolve()
        folder.mkdir(parents=True, exist_ok=True)
        
        # Verify write permission
        test_file = folder / ".waifu2x_test"
        try:
            test_file.touch(exist_ok=True)
            test_file.unlink(missing_ok=True)
        except (IOError, OSError) as e:
            raise Waifu2xFileError("Cannot write to directory", str(folder)) from e
            
        return str(folder)
    except Exception as e:
        raise Waifu2xFileError(f"Failed to create directory: {e}", str(folder_path)) from e

def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in megabytes (MB).
    
    Args:
        file_path: Path to the file
        
    Returns:
        float: File size in MB
        
    Raises:
        Waifu2xFileError: If file doesn't exist or is not accessible
    """
    try:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise Waifu2xFileError("File does not exist", str(file_path))
        return file_path.stat().st_size / (1024 * 1024)
    except (OSError, AttributeError) as e:
        raise Waifu2xFileError(f"Cannot get file size: {e}", str(file_path)) from e

def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
    """
    Calculate the hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: 'sha256')
        chunk_size: Size of chunks to read at a time (default: 8KB)
        
    Returns:
        str: Hexadecimal digest of the file
        
    Raises:
        Waifu2xFileError: If file cannot be read
        ValueError: If the hash algorithm is not available
    """
    file_path = Path(file_path).resolve()
    
    if not file_path.is_file():
        raise Waifu2xFileError("Path is not a file", str(file_path))
    
    hash_func = getattr(hashlib, algorithm, None)
    if hash_func is None:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    try:
        hasher = hash_func()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError) as e:
        raise Waifu2xFileError(f"Cannot read file for hashing: {e}", str(file_path)) from e

def get_temp_dir(prefix: str = 'waifu2x_') -> str:
    """
    Create and return a temporary directory with the given prefix.
    
    Args:
        prefix: Prefix for the temporary directory name
        
    Returns:
        str: Path to the created temporary directory
        
    Raises:
        Waifu2xFileError: If temporary directory cannot be created
    """
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        return str(temp_dir)
    except Exception as e:
        raise Waifu2xFileError(f"Cannot create temporary directory: {e}") from e

def cleanup_temp_dir(temp_dir: Union[str, Path]) -> None:
    """
    Safely remove a temporary directory and its contents.
    
    Args:
        temp_dir: Path to the temporary directory
        
    Raises:
        Waifu2xFileError: If cleanup fails
    """
    try:
        temp_path = Path(temp_dir)
        if temp_path.exists() and temp_path.is_dir():
            shutil.rmtree(temp_path, ignore_errors=True)
    except Exception as e:
        logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")

def is_image_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is an image based on its extension and MIME type.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if the file is an image, False otherwise
    """
    try:
        file_path = Path(file_path)
        if not file_path.is_file():
            return False
            
        # First check by extension
        ext = file_path.suffix.lower()
        if ext in {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}:
            return True
            
        # Fall back to MIME type detection
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type is not None and mime_type.startswith('image/')
    except Exception:
        return False

def parallel_process(
    items: list,
    process_func: Callable,
    max_workers: Optional[int] = None,
    **kwargs
) -> list:
    """
    Process items in parallel using a thread pool.
    
    Args:
        items: List of items to process
        process_func: Function to apply to each item
        max_workers: Maximum number of worker threads
        **kwargs: Additional arguments to pass to process_func
        
    Returns:
        list: List of results in the same order as input items
    """
    if not items:
        return []
        
    results = [None] * len(items)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Start the load operations and mark each future with its index
        future_to_index = {
            executor.submit(process_func, item, **kwargs): i 
            for i, item in enumerate(items)
        }
        
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as e:
                logger.error(f"Error processing item at index {index}: {e}")
                results[index] = e
    
    return results