"""
Remove The BG - A self-contained background removal tool.

This package provides background removal functionality with auto-installing
system dependencies and vendored rembg/onnxruntime for seamless operation.
"""

__version__ = "1.1.2"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import remove_background

__all__ = ["remove_background"]
