"""Utility functions"""

import os
import glob
from typing import List, Optional
from pathlib import Path
from .config import DEFAULT_CONFIG

def get_frame_list(folder: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    Get sorted list of image files from folder
    
    Args:
        folder: Path to folder containing frames
        extensions: List of file extensions to include
        
    Returns:
        Sorted list of file paths
    """
    if extensions is None:
        extensions = DEFAULT_CONFIG["supported_formats"]
    
    frame_files = []
    folder_path = Path(folder)
    
    if not folder_path.exists():
        return []
    
    for ext in extensions:
        # Check both lowercase and uppercase
        pattern = folder_path / f"*{ext}"
        frame_files.extend(folder_path.glob(f"*{ext}"))
        frame_files.extend(folder_path.glob(f"*{ext.upper()}"))
    
    # Remove duplicates and sort
    frame_files = list(set(str(f) for f in frame_files))
    frame_files.sort()
    
    return frame_files

def validate_waifu2x_path(executable_path: str) -> bool:
    """
    Validate that waifu2x executable exists and is executable
    
    Args:
        executable_path: Path to waifu2x-ncnn-vulkan executable
        
    Returns:
        True if valid, False otherwise
    """
    if not os.path.exists(executable_path):
        return False
    
    # Check if it's executable (Unix-like systems)
    if hasattr(os, 'access'):
        return os.access(executable_path, os.X_OK)
    
    # Windows - just check if file exists
    return os.path.isfile(executable_path)

def ensure_folder_exists(folder_path: str) -> str:
    """
    Ensure folder exists, create if it doesn't
    
    Args:
        folder_path: Path to folder
        
    Returns:
        Absolute path to folder
    """
    abs_path = os.path.abspath(folder_path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)
    return 0.0