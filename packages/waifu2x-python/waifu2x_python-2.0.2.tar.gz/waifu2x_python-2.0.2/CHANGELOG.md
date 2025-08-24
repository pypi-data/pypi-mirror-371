# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2] - 2025-08-23

### Added
- Added support for CPU-only mode with `gpu_id = -1`
- Added comprehensive type hints throughout the codebase
- Added detailed error messages and input validation
- Added support for multiple GPU selection
- Added progress callbacks for batch processing
- Added more detailed logging

### Changed
- Updated minimum Python version to 3.8+
- Updated all dependencies to their latest stable versions
- Improved error handling and user feedback
- Refactored configuration system for better maintainability
- Improved documentation with better examples
- Enhanced CLI interface with more options and better help text

### Fixed
- Fixed memory leaks in image processing pipeline
- Fixed issues with non-ASCII file paths
- Fixed race conditions in parallel processing
- Fixed compatibility with latest waifu2x-ncnn-vulkan

### Removed
- Dropped support for Python 3.7 and below
- Removed deprecated functions and parameters

## [1.0.2] - 2025-01-15

### Added
- Initial release of waifu2x-python
- Basic image upscaling functionality
- Support for multiple models
- Command-line interface
- Basic documentation
