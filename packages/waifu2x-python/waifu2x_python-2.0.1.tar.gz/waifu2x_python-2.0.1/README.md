# Waifu2x Python

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/waifu2x-python.svg)](https://badge.fury.io/py/waifu2x-python)

Python wrapper for waifu2x-ncnn-vulkan with a simple and powerful interface for image and video frame upscaling.

## Features

- High-performance image upscaling using waifu2x-ncnn-vulkan
- Support for multiple image formats (PNG, JPG, WEBP, etc.)
- Multiple models including anime and photo styles
- GPU acceleration with fallback to CPU
- Batch processing of multiple images
- Progress tracking and error handling

## Installation

```bash
pip install waifu2x-python
```

### Dependencies

- waifu2x-ncnn-vulkan
- Python 3.8+
- OpenCV
- NumPy
- Pillow

## Usage

### Basic Example

```python
from waifu2x_python import Waifu2x, ProcessingConfig

# Initialize with default settings
waifu2x = Waifu2x()

# Process a single image
result = waifu2x.process("input.jpg", "output_2x.jpg")
print(f"Processed image saved to: {result.output_path}")
```

### Advanced Configuration

```python
from waifu2x_python import Waifu2x, ProcessingConfig, ModelType

# Custom configuration
config = ProcessingConfig(
    model=ModelType.UPCONV_7_ANIME,  # or ModelType.CUNET, ModelType.UP_PHOTO, etc.
    scale=2,                         # 1, 2, 4, 8, 16, 32
    noise=1,                         # -1 to 3 (-1 = no effect, 0 = no noise reduction, 1-3 = noise reduction level)
    gpu_id=0,                        # -1 for CPU-only, 0 for first GPU, 1 for second GPU, etc.
    tile_size=0,                     # 0 for auto
    num_threads=4,                   # Number of CPU threads to use
    verbose=True                     # Enable verbose output
)

waifu2x = Waifu2x(config=config)

# Process all images in a folder
results = waifu2x.process_folder("input_folder", "output_folder")
print(f"Processed {len([r for r in results if r.success])}/{len(results)} images successfully")
```

### Command Line Interface

```bash
# Basic usage
waifu2x -i input.jpg -o output.png

# Process folder recursively
waifu2x -i input_folder -o output_folder -r

# Custom settings
waifu2x -i input.jpg -o output.png -m models-upconv_7_anime_style_art_rgb -s 2 -n 1 -g 0 -t 200

# CPU-only mode
waifu2x -i input.jpg -o output.png -g -1
```

## Available Models

- `models-cunet` - High quality denoising and upscaling (default)
- `models-upconv_7_anime_style_art_rgb` - For anime-style art
- `models-upconv_7_photo` - For photos
- `models-upconv_7_anime_style_art_rgb_noise0` - For clean anime-style art
- `models-upconv_7_anime_style_art_rgb_noise1` - For slightly noisy anime-style art
- `models-upconv_7_anime_style_art_rgb_noise2` - For noisy anime-style art
- `models-upconv_7_anime_style_art_rgb_noise3` - For very noisy anime-style art

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [waifu2x-ncnn-vulkan](https://github.com/nihui/waifu2x-ncnn-vulkan) - The underlying engine
- [ncnn](https://github.com/Tencent/ncnn) - High-performance neural network inference framework
- [Vulkan](https://www.vulkan.org/) - Cross-platform 3D graphics and compute API