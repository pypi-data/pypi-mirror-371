#!/usr/bin/env python3
"""
Setup script for remove-the-bg package.
A self-contained background removal tool with vendored dependencies.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "A self-contained background removal tool"

setup(
    name="remove-the-bg",
    version="1.0.3",
    author="Your Name",
    author_email="your.email@example.com",
    description="A self-contained background removal tool with no external dependencies",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/remove-the-bg",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "rem=remove_the_bg.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "remove_the_bg": ["vendor/**/*", "models/*"],
    },
    # No external dependencies - everything is vendored
    install_requires=[],
)
