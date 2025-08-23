"""Configuration classes and constants"""

from typing import List
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Available waifu2x models"""
    CUNET = "models-cunet"
    UPCONV_7_ANIME = "models-upconv_7_anime_style_art_rgb"
    UPCONV_7_PHOTO = "models-upconv_7_photo"
    
    @classmethod
    def all_models(cls) -> List[str]:
        return [cls.CUNET, cls.UPCONV_7_ANIME, cls.UPCONV_7_PHOTO]

@dataclass 
class ScaleConfig:
    """Available scale factors"""
    VALID_SCALES = [1, 2, 4, 8, 16, 32]
    
    @classmethod
    def is_valid_scale(cls, scale: int) -> bool:
        return scale in cls.VALID_SCALES

@dataclass
class NoiseConfig:
    """Available noise reduction levels"""
    VALID_NOISE_LEVELS = [-1, 0, 1, 2, 3]
    
    @classmethod
    def is_valid_noise(cls, noise: int) -> bool:
        return noise in cls.VALID_NOISE_LEVELS

# Default configurations
DEFAULT_CONFIG = {
    "scale": 2,
    "noise": 1, 
    "model": ModelConfig.CUNET,
    "gpu_id": 0,
    "tile_size": 0,
    "timeout": None,
    "supported_formats": [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]
}