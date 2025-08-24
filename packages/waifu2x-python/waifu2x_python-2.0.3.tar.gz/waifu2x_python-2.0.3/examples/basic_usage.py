#!/usr/bin/env python3
"""
Basic usage examples for waifu2x-python

This script demonstrates how to use the waifu2x-python package
for image upscaling with various configurations.
"""
import os
from pathlib import Path
from waifu2x_python import Waifu2x, ProcessingConfig, ModelType

def process_single_image():
    """Example of processing a single image."""
    # Initialize with default settings (auto-downloads waifu2x-ncnn-vulkan if needed)
    waifu2x = Waifu2x()
    
    # Process a single image
    result = waifu2x.process("input.jpg", "output_2x.jpg")
    print(f"Processed image saved to: {result.output_path}")
    print(f"Processing time: {result.metadata.get('processing_time', 0):.2f} seconds")

def process_with_custom_config():
    """Example of processing with custom configuration."""
    # Create a custom configuration
    config = ProcessingConfig(
        model=ModelType.UPCONV_7_ANIME,  # Use anime model
        scale=2,                         # 2x upscaling
        noise=1,                         # Medium noise reduction
        gpu_id=0,                        # Use first GPU (-1 for CPU-only)
        tile_size=0,                     # Auto-detect tile size
        num_threads=4                   # Number of CPU threads to use
    )
    
    waifu2x = Waifu2x(config=config)
    
    # Process a folder of images
    results = waifu2x.process_folder("input_folder", "output_folder")
    
    # Print summary
    success = sum(1 for r in results if r.success)
    print(f"Successfully processed {success}/{len(results)} images")

def process_with_callback():
    """Example of processing with progress callback."""
    def progress_callback(input_path: str, output_path: str, current: int, total: int):
        print(f"Processing {current}/{total}: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
    
    waifu2x = Waifu2x()
    waifu2x.process_folder("input_folder", "output_folder", progress_callback=progress_callback)

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    Path("output_folder").mkdir(exist_ok=True)
    
    print("=== Single Image Processing ===")
    if os.path.exists("input.jpg"):
        process_single_image()
    else:
        print("Skipping single image example (input.jpg not found)")
    
    print("\n=== Batch Processing ===")
    if os.path.isdir("input_folder"):
        process_with_custom_config()
    else:
        print("Skipping batch processing (input_folder not found)")
    
    print("\n=== Processing with Callback ===")
    if os.path.isdir("input_folder"):
        process_with_callback()
    else:
        print("Skipping callback example (input_folder not found)")