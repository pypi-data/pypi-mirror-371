"""
Remove The BG - A self-contained background removal tool.

This package provides background removal functionality with all dependencies
vendored to ensure zero external dependencies for users.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import remove_background

__all__ = ["remove_background"]
