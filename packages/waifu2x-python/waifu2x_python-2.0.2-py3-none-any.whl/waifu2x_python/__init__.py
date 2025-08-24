"""
Waifu2x Python - Python wrapper for waifu2x-ncnn-vulkan

A simple and powerful interface for upscaling images and video frames
using waifu2x-ncnn-vulkan with enhanced features and better error handling.

Example:
    >>> from waifu2x_python import Waifu2x, ProcessingConfig
    >>> 
    >>> # Initialize with default settings
    >>> waifu2x = Waifu2x(executable_path="path/to/waifu2x-ncnn-vulkan")
    >>> 
    >>> # Or with custom configuration
    >>> config = ProcessingConfig(
    ...     model="models-cunet",
    ...     scale=2,
    ...     noise=1,
    ...     gpu_id=0,  # Use first GPU, or -1 for CPU-only mode
    ...     tile_size=0  # Auto
    ... )
    >>> waifu2x = Waifu2x(
    ...     executable_path="path/to/waifu2x-ncnn-vulkan",
    ...     config=config
    ... )
    >>> 
    >>> # Process an image
    >>> output_path = waifu2x.process("input.jpg", "output_2x.jpg")
    >>> print(f"Processed image saved to: {output_path}")
"""

__version__ = "2.0.2"
__author__ = "Gleidson Rodrigues Nunes"
__email__ = "gleidsonrnunes@gmail.com"

# Core functionality
from .core import Waifu2x

# Configuration
from .config import (
    ModelType,
    ScaleConfig,
    NoiseConfig,
    ProcessingConfig,
    get_default_executable,
    get_default_models_dir,
    get_default_paths,
    ENV_WAIFU2X_PATH,
    ENV_WAIFU2X_GPU_ID,
    ENV_WAIFU2X_THREADS,
)

# Exceptions
from .exceptions import (
    Waifu2xError,
    Waifu2xNotFoundError,
    Waifu2xProcessError,
    Waifu2xTimeoutError,
    Waifu2xConfigError,
    Waifu2xFileError,
    Waifu2xModelError,
)

__all__ = [
    # Main class
    "Waifu2x",
    
    # Configuration
    "ModelType",
    "ScaleConfig",
    "NoiseConfig",
    "ProcessingConfig",
    "get_default_executable",
    "get_default_models_dir",
    "get_default_paths",
    "ENV_WAIFU2X_PATH",
    "ENV_WAIFU2X_GPU_ID",
    "ENV_WAIFU2X_THREADS",
    
    # Exceptions
    "Waifu2xError",
    "Waifu2xNotFoundError",
    "Waifu2xProcessError",
    "Waifu2xTimeoutError",
    "Waifu2xConfigError",
    "Waifu2xFileError",
    "Waifu2xModelError",
]