"""Custom exceptions for waifu2x-python"""

class Waifu2xError(Exception):
    """Base exception for waifu2x-python"""
    pass

class Waifu2xNotFoundError(Waifu2xError):
    """Raised when waifu2x-ncnn-vulkan executable is not found"""
    pass

class Waifu2xProcessError(Waifu2xError):
    """Raised when waifu2x process fails"""
    pass

class Waifu2xTimeoutError(Waifu2xError):
    """Raised when waifu2x process times out"""
    pass

class Waifu2xConfigError(Waifu2xError):
    """Raised when configuration is invalid"""
    pass