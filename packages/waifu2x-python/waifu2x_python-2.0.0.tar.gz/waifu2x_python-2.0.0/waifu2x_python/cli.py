"""
Command line interface for waifu2x-python.

This module provides a command-line interface for the waifu2x-python package,
allowing users to upscale images using waifu2x-ncnn-vulkan from the command line.
"""

import os
import sys
import time
import logging
import argparse
import platform
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable

# Local imports
from . import (
    Waifu2x,
    ModelType,
    ScaleConfig,
    NoiseConfig,
    ProcessingConfig,
    get_default_executable,
    get_default_models_dir,
    Waifu2xError,
    Waifu2xNotFoundError,
    Waifu2xProcessError,
    Waifu2xTimeoutError,
    Waifu2xConfigError,
    Waifu2xFileError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args(args: List[str] = None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: List of command line arguments. If None, uses sys.argv[1:].
        
    Returns:
        Parsed arguments as a Namespace object.
    """
    parser = argparse.ArgumentParser(
        description="""
        Waifu2x Python - Command line interface for waifu2x-ncnn-vulkan
        
        This tool allows you to upscale images using waifu2x-ncnn-vulkan
        with various configuration options for quality and performance.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
          # Basic usage
          waifu2x -i input.jpg -o output.png
          
          # Process all images in a folder
          waifu2x -i input_folder -o output_folder -r
          
          # Use specific model and scale
          waifu2x -i input.jpg -o output.png -m models-upconv_7_anime_style_art_rgb -s 2
          
          # Process with noise reduction
          waifu2x -i input.jpg -o output.png -n 2
          
          # Use specific GPU and tile size
          waifu2x -i input.jpg -o output.png -g 0 -t 200
        """
    )
    
    # Input/output arguments
    io_group = parser.add_argument_group('Input/Output')
    io_group.add_argument(
        '-i', '--input',
        required=True,
        help="Input file or directory"
    )
    io_group.add_argument(
        '-o', '--output',
        required=True,
        help="Output file or directory"
    )
    io_group.add_argument(
        '-r', '--recursive',
        action='store_true',
        help="Process directories recursively"
    )
    io_group.add_argument(
        '--overwrite',
        action='store_true',
        help="Overwrite existing files without prompting"
    )
    
    # Processing parameters
    proc_group = parser.add_argument_group('Processing Parameters')
    proc_group.add_argument(
        '-m', '--model',
        default=ModelType.CUNET.value,
        choices=ModelType.all_models(),
        help=f"Model to use (default: {ModelType.CUNET.value})"
    )
    proc_group.add_argument(
        '-s', '--scale',
        type=int,
        default=2,
        choices=sorted(ScaleConfig.VALID_SCALES),
        help="Scale factor (default: 2)"
    )
    proc_group.add_argument(
        '-n', '--noise',
        type=int,
        default=1,
        choices=sorted(NoiseConfig.VALID_NOISE_LEVELS),
        help="Noise reduction level (-1 to 3, default: 1)"
    )
    proc_group.add_argument(
        '--tile-size',
        type=int,
        default=0,
        help="Tile size (0 for auto, default: 0)"
    )
    proc_group.add_argument(
        '-g', '--gpu',
        type=int,
        default=0,
        help="GPU device to use (-1 for CPU-only, 0 for first GPU, etc., default: 0)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Waifu2x
        upscaler = Waifu2x(
            executable_path=args.executable,
            model=args.model,
            scale=args.scale,
            noise=args.noise,
            gpu_id=args.gpu,
            tile_size=args.tile_size,
            verbose=args.verbose
        )
        
        # Progress callback
        def progress(current, total):
            percent = (current / total) * 100
            print(f"\rProgress: {current}/{total} ({percent:.1f}%)", end="", flush=True)
        
        # Process folder
        result_files = upscaler.upscale_folder(
            args.input,
            args.output,
            progress_callback=progress if args.verbose else None
        )
        
        print(f"\n✅ Successfully processed {len(result_files)} files")
        print(f"Output saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()