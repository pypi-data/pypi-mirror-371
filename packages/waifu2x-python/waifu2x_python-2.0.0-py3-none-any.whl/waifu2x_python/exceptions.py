"""Custom exceptions for the waifu2x-python package.

This module defines custom exceptions used throughout the waifu2x-python package
to provide more detailed error information to the users.
"""
from typing import Optional, Any, Dict

class Waifu2xError(Exception):
    """Base exception for all waifu2x related errors.
    
    This exception should be used as the base class for all custom exceptions
    in the waifu2x-python package.
    """
    def __init__(self, message: str = "An error occurred in waifu2x-python"):
        self.message = message
        super().__init__(self.message)

class Waifu2xNotFoundError(FileNotFoundError, Waifu2xError):
    """Raised when the waifu2x-ncnn-vulkan executable is not found.
    
    Attributes:
        path: The path where the executable was expected to be found.
    """
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"waifu2x-ncnn-vulkan executable not found at: {path}")

class Waifu2xProcessError(Waifu2xError):
    """Raised when the waifu2x-ncnn-vulkan process fails.
    
    Attributes:
        returncode: The exit code returned by the process.
        stderr: The error output from the process, if any.
        command: The command that was executed, if available.
    """
    def __init__(
        self, 
        message: str, 
        returncode: int, 
        stderr: Optional[str] = None,
        command: Optional[str] = None
    ):
        self.returncode = returncode
        self.stderr = stderr
        self.command = command
        details = f"Return code: {returncode}"
        if stderr:
            details += f"\nError: {stderr}"
        if command:
            details += f"\nCommand: {command}"
        super().__init__(f"{message}. {details}")

class Waifu2xTimeoutError(TimeoutError, Waifu2xError):
    """Raised when a waifu2x operation times out.
    
    Attributes:
        timeout: The timeout value in seconds that was exceeded.
    """
    def __init__(self, timeout: int):
        self.timeout = timeout
        super().__init__(f"Operation timed out after {timeout} seconds")

class Waifu2xConfigError(ValueError, Waifu2xError):
    """Raised when there is an invalid configuration.
    
    This could be due to invalid model paths, unsupported parameters,
    or other configuration issues.
    """
    def __init__(self, message: str, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        super().__init__(f"Configuration error: {message}")

class Waifu2xFileError(IOError, Waifu2xError):
    """Raised when there is an error with input/output files.
    
    This includes file not found, permission errors, and other file-related issues.
    """
    def __init__(self, message: str, path: Optional[str] = None):
        self.path = path
        if path:
            message = f"{message}: {path}"
        super().__init__(message)

class Waifu2xModelError(Waifu2xError):
    """Raised when there is an error with the model.
    
    This could be due to an invalid model file, unsupported model type,
    or other model-related issues.
    """
    def __init__(self, message: str, model: Optional[str] = None):
        self.model = model
        if model:
            message = f"{message} (model: {model})"
        super().__init__(message)