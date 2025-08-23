"""Main Waifu2x class implementation"""

import subprocess
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
import logging

from .exceptions import (
    Waifu2xNotFoundError, 
    Waifu2xProcessError, 
    Waifu2xTimeoutError,
    Waifu2xConfigError
)
from .utils import get_frame_list, validate_waifu2x_path, ensure_folder_exists
from .config import DEFAULT_CONFIG, ModelConfig, ScaleConfig, NoiseConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Waifu2x:
    """
    Main Waifu2x wrapper class
    
    Provides a simple interface for upscaling images and video frames
    using waifu2x-ncnn-vulkan.
    """
    
    def __init__(
        self,
        executable_path: str,
        model: str = DEFAULT_CONFIG["model"],
        scale: int = DEFAULT_CONFIG["scale"],
        noise: int = DEFAULT_CONFIG["noise"], 
        gpu_id: int = DEFAULT_CONFIG["gpu_id"],
        tile_size: int = DEFAULT_CONFIG["tile_size"],
        timeout: Optional[int] = DEFAULT_CONFIG["timeout"],
        verbose: bool = False
    ):
        """
        Initialize Waifu2x wrapper
        
        Args:
            executable_path: Path to waifu2x-ncnn-vulkan executable
            model: Model to use (see ModelConfig)
            scale: Scale factor (1, 2, 4, 8, 16, 32)
            noise: Noise reduction level (-1 to 3)
            gpu_id: GPU ID (-1 for CPU, 0+ for specific GPU)
            tile_size: Tile size (0 for auto, 32-512 for manual)
            timeout: Process timeout in seconds (None for no timeout)
            verbose: Enable verbose logging
            
        Raises:
            Waifu2xNotFoundError: If executable not found
            Waifu2xConfigError: If configuration is invalid
        """
        
        # Validate executable
        if not validate_waifu2x_path(executable_path):
            raise Waifu2xNotFoundError(f"waifu2x executable not found: {executable_path}")
        
        # Validate configuration
        if not ScaleConfig.is_valid_scale(scale):
            raise Waifu2xConfigError(f"Invalid scale factor: {scale}. Valid: {ScaleConfig.VALID_SCALES}")
        
        if not NoiseConfig.is_valid_noise(noise):
            raise Waifu2xConfigError(f"Invalid noise level: {noise}. Valid: {NoiseConfig.VALID_NOISE_LEVELS}")
        
        if model not in ModelConfig.all_models():
            raise Waifu2xConfigError(f"Invalid model: {model}. Valid: {ModelConfig.all_models()}")
        
        # Store configuration
        self.executable_path = executable_path
        self.model = model
        self.scale = scale
        self.noise = noise
        self.gpu_id = gpu_id
        self.tile_size = tile_size
        self.timeout = timeout
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        logger.info(f"Initialized Waifu2x with model={model}, scale={scale}x, noise={noise}")
    
    def _build_command(self, input_path: str, output_path: str) -> List[str]:
        """Build waifu2x command"""
        cmd = [
            self.executable_path,
            "-i", input_path,
            "-o", output_path,
            "-s", str(self.scale),
            "-n", str(self.noise),
            "-m", self.model,
            "-g", str(self.gpu_id)
        ]
        
        if self.tile_size > 0:
            cmd.extend(["-t", str(self.tile_size)])
        
        return cmd
    
    def _run_waifu2x(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Run waifu2x process
        
        Returns:
            Dict with process information
        """
        cmd = self._build_command(input_path, output_path)
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                error_msg = f"waifu2x failed with code {result.returncode}: {result.stderr}"
                logger.error(error_msg)
                raise Waifu2xProcessError(error_msg)
            
            if self.verbose and result.stdout:
                logger.info(f"waifu2x output: {result.stdout}")
            
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": cmd
            }
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"waifu2x process timed out after {self.timeout} seconds"
            logger.error(error_msg)
            raise Waifu2xTimeoutError(error_msg) from e
    
    def upscale_folder(
        self, 
        input_folder: str,
        output_folder: str, 
        file_pattern: str = "*",
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[str]:
        """
        Upscale all images in a folder
        
        Args:
            input_folder: Input folder containing images
            output_folder: Output folder for upscaled images
            file_pattern: File pattern to match (default: all files)
            progress_callback: Optional callback function(current, total)
            
        Returns:
            List of processed file paths
            
        Raises:
            Waifu2xProcessError: If processing fails
        """
        
        # Validate input folder
        if not os.path.exists(input_folder):
            raise Waifu2xProcessError(f"Input folder not found: {input_folder}")
        
        # Get file list
        input_files = get_frame_list(input_folder)
        if not input_files:
            logger.warning(f"No image files found in {input_folder}")
            return []
        
        # Create output folder
        output_folder = ensure_folder_exists(output_folder)
        
        logger.info(f"Processing {len(input_files)} files from {input_folder}")
                
        # Verify output files
        output_files = []
        for i, input_file in enumerate(input_files):
            filename = os.path.basename(input_file)
            output_file = os.path.join(output_folder, filename)

            # Process with waifu2x
            self._run_waifu2x(input_file, output_file)

            if os.path.exists(output_file):
                output_files.append(output_file)
            else:
                logger.warning(f"Output file not created: {filename}")
            
            # Progress callback
            if progress_callback:
                progress_callback(i + 1, len(input_files))
        
        logger.info(f"Successfully processed {len(output_files)}/{len(input_files)} files")
        return output_files
    
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