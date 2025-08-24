#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Read the README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() 
        for line in fh 
        if line.strip() and not line.startswith("#")
    ]

def get_version() -> str:
    """Get the current version from the package's __init__ file."""
    version_file = Path("waifu2x_python/__init__.py").read_text(encoding="utf-8")
    version_match = re.search(
        r'^__version__ = [\'"]([^\'"]*)[\'"]', 
        version_file, 
        re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Get package metadata
version = get_version()

# Main setup configuration
setup(
    name="waifu2x-python",
    version=version,
    author="Gleidson Rodrigues Nunes",
    author_email="gleidsonrnunes@gmail.com",
    maintainer="Gleidson Rodrigues Nunes",
    maintainer_email="gleidsonrnunes@gmail.com",
    description="A high-performance Python wrapper for waifu2x-ncnn-vulkan with async support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gleidsonnunes/waifu2x-python",
    project_urls={
        "Bug Tracker": "https://github.com/gleidsonnunes/waifu2x-python/issues",
        "Documentation": "https://github.com/gleidsonnunes/waifu2x-python#readme",
        "Source Code": "https://github.com/gleidsonnunes/waifu2x-python",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    py_modules=[],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.12b0",
            "isort>=5.10.1",
            "mypy>=0.930",
            "pylint>=2.12.0",
            "types-PyYAML>=6.0.0",
            "types-requests>=2.27.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-mock>=3.7.0",
            "pytest-asyncio>=0.15.1",
        ],
        "docs": [
            "sphinx>=4.2.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.15.0",
            "myst-parser>=0.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "waifu2x=waifu2x_python.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    keywords=[
        "waifu2x",
        "super-resolution",
        "image-processing",
        "computer-vision",
        "deep-learning",
        "ncnn",
        "vulkan",
        "upscaling",
        "denoising",
    ],
    license="MIT",
    platforms="any",
)