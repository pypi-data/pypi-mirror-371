"""
Main Waifu2x class implementation for the waifu2x-python package.

This module provides the core Waifu2x class that handles the interaction with
the waifu2x-ncnn-vulkan executable, including process management, error handling,
and file operations.
"""

import os
import sys
import time
import signal
import shutil
import asyncio
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import (
    List, Optional, Dict, Any, Union, 
    Callable, Tuple, Set, TypeVar, Type, 
    AsyncGenerator, BinaryIO, TextIO
)
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party imports
import numpy as np
from PIL import Image, ImageOps, ImageFile

# Local imports
from .exceptions import (
    Waifu2xError,
    Waifu2xNotFoundError,
    Waifu2xProcessError,
    Waifu2xTimeoutError,
    Waifu2xConfigError,
    Waifu2xFileError,
    Waifu2xModelError
)

from .config import (
    ProcessingConfig,
    ModelType,
    ScaleConfig,
    NoiseConfig,
    get_default_executable,
    ENV_WAIFU2X_PATH,
    ENV_WAIFU2X_GPU_ID,
    ENV_WAIFU2X_THREADS
)

from .utils import (
    get_frame_list,
    validate_waifu2x_path,
    ensure_folder_exists,
    get_file_size_mb,
    calculate_file_hash,
    get_temp_dir,
    cleanup_temp_dir,
    is_image_file,
    parallel_process
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Type aliases
PathLike = Union[str, os.PathLike]
ProcessCallback = Callable[[str, str, int, int], None]

@dataclass
class ProcessResult:
    """Result of a waifu2x processing operation."""
    input_path: str
    output_path: str
    success: bool
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class Waifu2x:
    """
    Main Waifu2x wrapper class providing high-level interface for image upscaling.
    
    This class handles the interaction with the waifu2x-ncnn-vulkan executable,
    including process management, error handling, and file operations.
    
    Example:
        >>> from waifu2x_python import Waifu2x, ProcessingConfig
        >>> 
        >>> # Initialize with default settings
        >>> waifu2x = Waifu2x(executable_path="path/to/waifu2x-ncnn-vulkan")
        >>> 
        >>> # Process a single image
        >>> result = waifu2x.process("input.jpg", "output_2x.jpg")
        >>> print(f"Processed image saved to: {result.output_path}")
        >>> 
        >>> # Process all images in a folder
        >>> results = waifu2x.process_folder("input_folder", "output_folder")
        >>> print(f"Processed {len(results)} images")
        >>> 
        >>> # Process with custom settings
        >>> config = ProcessingConfig(
        ...     model=ModelType.UPCONV_7_ANIME,
        ...     scale=2,
        ...     noise=1,
        ...     gpu_id=0,  # Use first GPU, or -1 for CPU-only mode
        ...     tile_size=0  # Auto
        ... )
        >>> waifu2x = Waifu2x(
        ...     executable_path="path/to/waifu2x-ncnn-vulkan",
        ...     config=config
        ... )
    """
    
    def __init__(
        self,
        executable_path: Optional[PathLike] = None,
        config: Optional[ProcessingConfig] = None,
        **kwargs
    ):
        """
        Initialize the Waifu2x processor.
        
        Args:
            executable_path: Path to the waifu2x-ncnn-vulkan executable.
                           If not provided, will try to find it in the default locations.
            config: Processing configuration. If not provided, default settings will be used.
            **kwargs: Additional keyword arguments to override config settings.
        """
        # Initialize configuration
        self.config = config if config is not None else ProcessingConfig()
        
        # Apply any overrides from kwargs
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Set executable path
        if executable_path is None:
            self.executable_path = get_default_executable()
        else:
            self.executable_path = str(Path(executable_path).expanduser().resolve())
        
        # Validate configuration and paths
        self._validate()
        
        # Initialize thread pool for parallel processing
        self._executor = ThreadPoolExecutor(
            max_workers=self.config.num_threads or None
        )
        
        logger.debug(f"Initialized Waifu2x with config: {self.config}")
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)
    
    def _validate(self) -> None:
        """Validate configuration and executable."""
        # Validate executable
        if not validate_waifu2x_path(self.executable_path):
            raise Waifu2xNotFoundError(self.executable_path)
        
        # Validate configuration
        try:
            self.config.validate()
        except ValueError as e:
            raise Waifu2xConfigError(str(e)) from e
    
    def _build_command(
        self, 
        input_path: PathLike, 
        output_path: PathLike,
        **overrides
    ) -> List[str]:
        """
        Build the command line arguments for waifu2x-ncnn-vulkan.
        
        Args:
            input_path: Path to the input file.
            output_path: Path to save the output file.
            **overrides: Configuration overrides for this operation.
            
        Returns:
            List of command line arguments.
        """
        # Use overrides if provided, otherwise use instance config
        config = {}
        for key in ['model', 'scale', 'noise', 'gpu_id', 'tile_size']:
            config[key] = overrides.get(key, getattr(self.config, key, None))
        
        # Build the base command
        cmd = [
            str(self.executable_path),
            '-i', str(input_path),
            '-o', str(output_path),
            '-n', str(config['noise']),
            '-s', str(config['scale']),
            '-m', str(config['model']),
            '-g', str(config['gpu_id']),
            '-t', str(config['tile_size'] or 0),  # 0 = auto
            '-j', '1:1:1'  # Use 1 thread for each step
        ]
        
        return cmd
    
    def process(
        self, 
        input_path: PathLike, 
        output_path: PathLike,
        **overrides
    ) -> ProcessResult:
        """
        Process a single image file.
        
        Args:
            input_path: Path to the input image file.
            output_path: Path to save the processed image.
            **overrides: Configuration overrides for this operation.
            
        Returns:
            ProcessResult: Result of the processing operation.
            
        Raises:
            Waifu2xFileError: If the input file doesn't exist or is not accessible.
            Waifu2xProcessError: If the waifu2x process fails.
            Waifu2xTimeoutError: If the process times out.
        """
        input_path = Path(input_path).expanduser().resolve()
        output_path = Path(output_path).expanduser().resolve()
        
        # Validate input file
        if not input_path.is_file():
            raise Waifu2xFileError("Input file not found", str(input_path))
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build command
        cmd = self._build_command(input_path, output_path, **overrides)
        
        # Run the command
        return self._run_command(cmd, str(input_path), str(output_path))
    
    def process_folder(
        self,
        input_dir: PathLike,
        output_dir: PathLike,
        recursive: bool = False,
        progress_callback: Optional[ProcessCallback] = None,
        **overrides
    ) -> List[ProcessResult]:
        """
        Process all images in a folder.
        
        Args:
            input_dir: Path to the input directory.
            output_dir: Path to save processed images.
            recursive: If True, process images in subdirectories recursively.
            progress_callback: Optional callback function that will be called after
                             each image is processed. The function should accept
                             (input_path, output_path, current, total) as arguments.
            **overrides: Configuration overrides for this operation.
            
        Returns:
            List of ProcessResult objects for each processed file.
        """
        input_dir = Path(input_dir).expanduser().resolve()
        output_dir = Path(output_dir).expanduser().resolve()
        
        # Validate input directory
        if not input_dir.is_dir():
            raise Waifu2xFileError("Input directory not found", str(input_dir))
        
        # Get list of image files
        image_files = get_frame_list(str(input_dir), recursive=recursive)
        
        if not image_files:
            logger.warning(f"No image files found in {input_dir}")
            return []
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        total = len(image_files)
        
        for i, img_path in enumerate(image_files, 1):
            try:
                # Create relative path for output
                rel_path = Path(img_path).relative_to(input_dir)
                out_path = output_dir / rel_path
                
                # Create output directory if it doesn't exist
                out_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Process the image
                result = self.process(img_path, out_path, **overrides)
                results.append(result)
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(img_path, str(out_path), i, total)
                
            except Exception as e:
                logger.error(f"Error processing {img_path}: {str(e)}")
                results.append(ProcessResult(
                    input_path=img_path,
                    output_path=str(out_path) if 'out_path' in locals() else '',
                    success=False,
                    error=e,
                    metadata={"index": i, "total": total}
                ))
        
        return results
    
    def process_batch(
        self,
        input_paths: List[PathLike],
        output_dir: PathLike,
        max_workers: Optional[int] = None,
        **overrides
    ) -> List[ProcessResult]:
        """
        Process multiple images in parallel.
        
        Args:
            input_paths: List of input file paths.
            output_dir: Directory to save processed images.
            max_workers: Maximum number of parallel processes. If None, uses the
                       system's default (number of CPUs).
            **overrides: Configuration overrides for this operation.
            
        Returns:
            List of ProcessResult objects for each processed file.
        """
        output_dir = Path(output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not input_paths:
            return []
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for input_path in input_paths:
                input_path = Path(input_path).expanduser().resolve()
                output_path = output_dir / input_path.name
                
                # Submit task to thread pool
                future = executor.submit(
                    self.process,
                    input_path=input_path,
                    output_path=output_path,
                    **overrides
                )
                futures.append(future)
            
            # Gather results
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error in batch processing: {str(e)}")
                    results.append(ProcessResult(
                        input_path="",
                        output_path="",
                        success=False,
                        error=e
                    ))
            
            return results
    
    async def process_async(
        self,
        input_path: PathLike,
        output_path: PathLike,
        **overrides
    ) -> ProcessResult:
        """
        Process an image file asynchronously.
        
        Args:
            input_path: Path to the input image file.
            output_path: Path to save the processed image.
            **overrides: Configuration overrides for this operation.
            
        Returns:
            ProcessResult: Result of the processing operation.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self.process(input_path, output_path, **overrides)
        )
    
    async def process_folder_async(
        self,
        input_dir: PathLike,
        output_dir: PathLike,
        recursive: bool = False,
        max_concurrent: int = 4,
        **overrides
    ) -> List[ProcessResult]:
        """
        Process all images in a folder asynchronously with limited concurrency.
        
        Args:
            input_dir: Path to the input directory.
            output_dir: Directory to save processed images.
            recursive: If True, process images in subdirectories recursively.
            max_concurrent: Maximum number of concurrent processes.
            **overrides: Configuration overrides for this operation.
            
        Returns:
            List of ProcessResult objects for each processed file.
        """
        input_dir = Path(input_dir).expanduser().resolve()
        output_dir = Path(output_dir).expanduser().resolve()
        
        # Get list of image files
        image_files = get_frame_list(str(input_dir), recursive=recursive)
        
        if not image_files:
            return []
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process files with limited concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_one(img_path: str) -> ProcessResult:
            async with semaphore:
                try:
                    # Create relative path for output
                    rel_path = Path(img_path).relative_to(input_dir)
                    out_path = output_dir / rel_path
                    
                    # Create output directory if it doesn't exist
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Process the image asynchronously
                    return await self.process_async(img_path, out_path, **overrides)
                    
                except Exception as e:
                    logger.error(f"Error processing {img_path}: {str(e)}")
                    return ProcessResult(
                        input_path=img_path,
                        output_path=str(out_path) if 'out_path' in locals() else '',
                        success=False,
                        error=e
                    )
        
        # Process all images concurrently
        tasks = [process_one(img_path) for img_path in image_files]
        return await asyncio.gather(*tasks)
    
    def _run_command(
        self,
        cmd: List[str],
        input_path: str,
        output_path: str,
        timeout: Optional[float] = None
    ) -> ProcessResult:
        """
        Run the waifu2x command and handle the result.
        
        Args:
            cmd: Command to execute as a list of strings.
            input_path: Path to the input file (for error reporting).
            output_path: Path to the output file (for error reporting).
            timeout: Timeout in seconds. If None, uses the instance timeout.
            
        Returns:
            ProcessResult: Result of the processing operation.
            
        Raises:
            Waifu2xProcessError: If the process fails.
            Waifu2xTimeoutError: If the process times out.
        """
        if timeout is None:
            timeout = self.config.timeout
        
        start_time = time.time()
        
        try:
            # Run the command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Wait for the process to complete with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Try to terminate the process gracefully
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate
                    process.kill()
                    process.wait()
                
                raise Waifu2xTimeoutError(timeout or 0)
            
            # Check the return code
            if process.returncode != 0:
                raise Waifu2xProcessError(
                    f"waifu2x-ncnn-vulkan failed with return code {process.returncode}",
                    process.returncode,
                    stderr,
                    " ".join(f'"{x}"' if ' ' in str(x) else str(x) for x in cmd)
                )
            
            # Verify output file was created
            if not os.path.exists(output_path):
                raise Waifu2xProcessError(
                    "Output file was not created",
                    process.returncode,
                    stderr,
                    " ".join(f'"{x}"' if ' ' in str(x) else str(x) for x in cmd)
                )
            
            # Log success
            duration = time.time() - start_time
            logger.debug(
                f"Processed {input_path} -> {output_path} "
                f"in {duration:.2f} seconds"
            )
            
            return ProcessResult(
                input_path=input_path,
                output_path=output_path,
                success=True,
                metadata={
                    "duration": duration,
                    "command": cmd,
                    "return_code": process.returncode,
                    "stderr": stderr,
                    "stdout": stdout
                }
            )
            
        except subprocess.CalledProcessError as e:
            raise Waifu2xProcessError(
                f"waifu2x-ncnn-vulkan process failed: {str(e)}",
                e.returncode,
                e.stderr,
                " ".join(f'"{x}"' if ' ' in str(x) else str(x) for x in e.cmd)
            ) from e
            
        except Exception as e:
            raise Waifu2xError(f"Unexpected error: {str(e)}") from e
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the Waifu2x instance.
        
        Returns:
            Dictionary containing status information.
        """
        return {
            "executable": self.executable_path,
            "config": self.config.to_dict(),
            "thread_pool": {
                "max_workers": self._executor._max_workers if hasattr(self, '_executor') else None,
                "active_threads": len(self._executor._threads) if hasattr(self, '_executor') and hasattr(self._executor, '_threads') else 0
            }
        }
    
    def upscale_file_list(
        self,
        file_paths: List[str],
        output_folder: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[str]:
        """
        Upscale specific list of files
        
        Args:
            file_paths: List of input file paths
            output_folder: Output folder for upscaled images
            progress_callback: Optional callback function(current, total)
            
        Returns:
            List of processed file paths
        """
        
        if not file_paths:
            return []
        
        # Create temporary input folder
        with tempfile.TemporaryDirectory(prefix="waifu2x_input_") as temp_input:
            # Copy files to temp folder
            temp_files = []
            for i, file_path in enumerate(file_paths):
                if not os.path.exists(file_path):
                    logger.warning(f"Input file not found: {file_path}")
                    continue
                
                filename = f"frame_{i:06d}{os.path.splitext(file_path)[1]}"
                temp_path = os.path.join(temp_input, filename)
                shutil.copy2(file_path, temp_path)
                temp_files.append((temp_path, os.path.basename(file_path)))
            
            if not temp_files:
                logger.error("No valid input files to process")
                return []
            
            # Process folder
            result_files = self.upscale_folder(
                temp_input, 
                output_folder,
                progress_callback=progress_callback
            )
            
            # Rename to original names
            final_files = []
            for (temp_path, original_name), result_path in zip(temp_files, result_files):
                if os.path.exists(result_path):
                    final_path = os.path.join(output_folder, original_name)
                    if result_path != final_path:
                        shutil.move(result_path, final_path)
                    final_files.append(final_path)
            
            return final_files
    
    def get_info(self) -> Dict[str, Any]:
        """Get current configuration info"""
        return {
            "executable_path": self.executable_path,
            "model": self.model,
            "scale": self.scale,
            "noise": self.noise,
            "gpu_id": self.gpu_id,
            "tile_size": self.tile_size,
            "timeout": self.timeout,
            "version": "1.0.0"
        }
    
    def __str__(self) -> str:
        return f"Waifu2x(model={self.model}, scale={self.scale}x, noise={self.noise})"
    
    def __repr__(self) -> str:
        return (f"Waifu2x(executable_path='{self.executable_path}', "
                f"model='{self.model}', scale={self.scale}, noise={self.noise})")