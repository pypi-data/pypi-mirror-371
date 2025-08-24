#!/usr/bin/env python3
"""
Advanced usage examples for waifu2x-python

This script demonstrates advanced usage of the waifu2x-python package,
including custom model paths, error handling, and performance optimization.
"""
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional

from waifu2x_python import Waifu2x, ProcessingConfig, ModelType, Waifu2xError, ProcessResult


def process_with_custom_model():
    """Example of using a custom model path."""
    print("\n=== Using Custom Model ===")
    
    # Point to a custom waifu2x-ncnn-vulkan executable and model directory
    config = ProcessingConfig(
        model=ModelType.CUNET,                           # Model type
        scale=2,
        noise=1,
        gpu_id=0                                        # -1 for CPU-only
    )
    
    try:
        waifu2x = Waifu2x(config=config)
        result = waifu2x.process("input.jpg", "output_custom_model.jpg")
        if result.success:
            print(f"Successfully processed with custom model: {result.output_path}")
    except Waifu2xError as e:
        print(f"Error: {e}")


def process_with_error_handling():
    """Example of robust error handling."""
    print("\n=== Error Handling ===")
    
    waifu2x = Waifu2x()
    
    # Non-existent file
    try:
        result = waifu2x.process("nonexistent.jpg", "output.jpg")
        print(f"Result: {result}")
    except FileNotFoundError as e:
        print(f"Expected error (file not found): {e}")
    
    # Invalid configuration
    try:
        invalid_config = ProcessingConfig(scale=3)  # Invalid scale
        waifu2x = Waifu2x(config=invalid_config)
    except ValueError as e:
        print(f"Expected error (invalid config): {e}")


def batch_process_with_parallelism(input_dir: str, output_dir: str, max_workers: int = 2):
    """
    Example of parallel processing with thread pool.
    
    Args:
        input_dir: Input directory containing images
        output_dir: Output directory for processed images
        max_workers: Maximum number of parallel workers
    """
    print(f"\n=== Parallel Processing (max_workers={max_workers}) ===")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get list of image files
    image_files = [f for f in Path(input_dir).glob("*") if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']]
    
    if not image_files:
        print("No image files found in input directory")
        return
    
    # Function to process a single image
    def process_image(input_path: Path) -> Optional[ProcessResult]:
        output_path = output_dir / input_path.name
        try:
            # Each thread gets its own Waifu2x instance to avoid thread-safety issues
            waifu2x = Waifu2x()
            return waifu2x.process(str(input_path), str(output_path))
        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            return None
    
    # Process images in parallel
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_image, image_files))
    
    # Calculate statistics
    success = sum(1 for r in results if r and r.success)
    elapsed = time.time() - start_time
    
    print(f"Processed {success}/{len(image_files)} images in {elapsed:.2f} seconds")
    print(f"Average time per image: {elapsed/len(image_files):.2f} seconds")


if __name__ == "__main__":
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    # Run examples if input files exist
    if os.path.exists("input.jpg"):
        process_with_custom_model()
        process_with_error_handling()
    else:
        print("Skipping examples that require input.jpg")
    
    # Run batch processing if input directory exists
    if os.path.isdir("input_images"):
        batch_process_with_parallelism("input_images", "output/parallel", max_workers=2)
    else:
        print("Skipping batch processing (input_images directory not found)")
