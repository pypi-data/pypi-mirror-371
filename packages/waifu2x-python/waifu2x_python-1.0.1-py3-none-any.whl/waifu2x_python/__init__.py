"""
Waifu2x Python - Python wrapper for waifu2x-ncnn-vulkan

A simple and powerful interface for upscaling images and video frames
using waifu2x-ncnn-vulkan.
"""

__version__ = "1.0.0"
__author__ = "Gleidson Rodrigues Nunes"
__email__ = "gleidsonrnunes@gmail.com"

from .core import Waifu2x
from .exceptions import (
    Waifu2xError,
    Waifu2xNotFoundError,
    Waifu2xProcessError,
    Waifu2xTimeoutError
)
from .config import ModelConfig, ScaleConfig

__all__ = [
    "Waifu2x",
    "Waifu2xError", 
    "Waifu2xNotFoundError",
    "Waifu2xProcessError", 
    "Waifu2xTimeoutError",
    "ModelConfig",
    "ScaleConfig"
]