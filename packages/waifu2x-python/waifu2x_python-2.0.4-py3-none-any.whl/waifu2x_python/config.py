"""Configuration classes and constants for the waifu2x-python package.

This module defines configuration options, constants, and validation logic
for the waifu2x image upscaling functionality.
"""

import os
import sys
from typing import List, Dict, Any, Optional, Set, Type, TypeVar, Union
from pathlib import Path
from enum import Enum, auto
from dataclasses import dataclass, field

# Type variable for generic config classes
T = TypeVar('T')

class ModelType(Enum):
    """Enumeration of available waifu2x model types."""
    CUNET = "models-cunet"
    UPCONV_7_ANIME = "models-upconv_7_anime_style_art_rgb"
    UPCONV_7_PHOTO = "models-upconv_7_photo"

    @classmethod
    def all_models(cls) -> List[str]:
        """Get a list of all available model names."""
        return [model.value for model in cls]

    @classmethod
    def is_valid_model(cls, model: str) -> bool:
        """Check if a model name is valid."""
        try:
            cls(model)
            return True
        except ValueError:
            return False

class ScaleConfig:
    """Configuration for image scaling."""
    
    # Supported scale factors
    VALID_SCALES = {1, 2, 4, 8, 16, 32}
    
    @classmethod
    def is_valid_scale(cls, scale: int) -> bool:
        """Check if a scale factor is valid."""
        return scale in cls.VALID_SCALES
    
    @classmethod
    def validate_scale(cls, scale: int) -> int:
        """Validate and return a scale factor."""
        scale = int(scale)
        if not cls.is_valid_scale(scale):
            raise ValueError(f"Invalid scale factor: {scale}. Must be one of {sorted(cls.VALID_SCALES)}")
        return scale

class NoiseConfig:
    """Configuration for noise reduction."""
    
    # Valid noise reduction levels (-1 = no denoising, 0-3 = denoising strength)
    VALID_NOISE_LEVELS = {-1, 0, 1, 2, 3}
    
    @classmethod
    def is_valid_noise(cls, noise: int) -> bool:
        """Check if a noise reduction level is valid."""
        return noise in cls.VALID_NOISE_LEVELS
    
    @classmethod
    def validate_noise(cls, noise: int) -> int:
        """Validate and return a noise reduction level."""
        noise = int(noise)
        if not cls.is_valid_noise(noise):
            raise ValueError(f"Invalid noise level: {noise}. Must be one of {sorted(cls.VALID_NOISE_LEVELS)}")
        return noise

@dataclass
class ProcessingConfig:
    """Configuration for waifu2x processing parameters."""
    
    # Model configuration
    model: ModelType = ModelType.CUNET
    
    # Processing parameters
    scale: int = 2
    noise: int = 1
    gpu_id: int = 0
    tile_size: int = 0  # 0 = auto
    
    # Performance settings
    num_threads: int = 0  # 0 = auto
    
    # Timeout in seconds (None for no timeout)
    timeout: Optional[float] = None
    
    # Supported image formats
    supported_formats: Set[str] = field(
        default_factory=lambda: {
            ".png", ".jpg", ".jpeg", 
            ".bmp", ".tiff", ".tif", 
            ".webp"
        }
    )
    
    def validate(self) -> None:
        """Validate all configuration parameters."""
        if not ModelType.is_valid_model(self.model):
            raise ValueError(f"Invalid model: {self.model}")
        
        self.scale = ScaleConfig.validate_scale(self.scale)
        self.noise = NoiseConfig.validate_noise(self.noise)
        
        if self.gpu_id < -1:
            raise ValueError("GPU ID must be -1 (CPU-only) or >= 0 (GPU device ID)")
            
        if self.tile_size < 0:
            raise ValueError("Tile size must be >= 0")
            
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError("Timeout must be None or > 0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary."""
        return {
            "model": self.model,
            "scale": self.scale,
            "noise": self.noise,
            "gpu_id": self.gpu_id,
            "tile_size": self.tile_size,
            "num_threads": self.num_threads,
            "timeout": self.timeout,
            "supported_formats": sorted(self.supported_formats)
        }
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create configuration from a dictionary."""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.validate()
        return config

# Default configuration
DEFAULT_CONFIG = ProcessingConfig().to_dict()

# Environment variable names
ENV_WAIFU2X_PATH = "WAIFU2X_PATH"
ENV_WAIFU2X_GPU_ID = "WAIFU2X_GPU_ID"
ENV_WAIFU2X_THREADS = "WAIFU2X_THREADS"

# Default paths for different platforms
DEFAULT_PATHS = {
    "win32": {
        "executable": "waifu2x-ncnn-vulkan/waifu2x-ncnn-vulkan.exe"
    },
    "linux": {
        "executable": "waifu2x-ncnn-vulkan/waifu2x-ncnn-vulkan"
    },
    "darwin": {
        "executable": "waifu2x-ncnn-vulkan/waifu2x-ncnn-vulkan"
    }
}

def get_default_paths() -> Dict[str, str]:
    """Get default paths for the current platform."""
    system = sys.platform
    if system not in DEFAULT_PATHS:
        system = 'linux'  # Default to linux for unknown platforms
    return DEFAULT_PATHS[system]

def get_default_executable() -> str:
    """Get the default path to the waifu2x executable."""
    # Check environment variable first
    if ENV_WAIFU2X_PATH in os.environ:
        return os.environ[ENV_WAIFU2X_PATH]
    
    # Get platform-specific default path
    return get_default_paths()["executable"]