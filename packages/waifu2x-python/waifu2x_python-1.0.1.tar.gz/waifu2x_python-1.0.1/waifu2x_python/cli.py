"""Command line interface"""

import argparse
import sys
from pathlib import Path
from .core import Waifu2x
from .config import ModelConfig, ScaleConfig

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Waifu2x Python CLI - Upscale images using waifu2x-ncnn-vulkan"
    )
    
    parser.add_argument(
        "input", 
        help="Input folder containing images"
    )
    parser.add_argument(
        "output",
        help="Output folder for upscaled images"
    )
    parser.add_argument(
        "-e", "--executable",
        required=True,
        help="Path to waifu2x-ncnn-vulkan executable"
    )
    parser.add_argument(
        "-s", "--scale",
        type=int,
        default=2,
        choices=ScaleConfig.VALID_SCALES,
        help="Scale factor (default: 2)"
    )
    parser.add_argument(
        "-n", "--noise", 
        type=int,
        default=1,
        choices=[-1, 0, 1, 2, 3],
        help="Noise reduction level (default: 1)"
    )
    parser.add_argument(
        "-m", "--model",
        default=ModelConfig.CUNET,
        choices=ModelConfig.all_models(),
        help="Model to use (default: models-cunet)"
    )
    parser.add_argument(
        "-g", "--gpu",
        type=int, 
        default=0,
        help="GPU ID (-1 for CPU, default: 0)"
    )
    parser.add_argument(
        "-t", "--tile-size",
        type=int,
        default=0,
        help="Tile size (0 for auto, default: 0)"
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