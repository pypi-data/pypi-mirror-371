"""
Core functionality for background removal.
"""

import os
import sys
from pathlib import Path

def setup_vendor_imports():
    """Setup imports for vendored dependencies."""
    vendor_path = Path(__file__).parent / "vendor"
    
    # Add vendor directory to beginning of path if not already there
    vendor_str = str(vendor_path)
    if vendor_str not in sys.path:
        sys.path.insert(0, vendor_str)
    
    # Also add numpy path specifically to avoid import issues
    numpy_path = vendor_path / "numpy"
    if numpy_path.exists() and str(numpy_path) not in sys.path:
        sys.path.insert(0, str(numpy_path))

# Setup vendored imports
setup_vendor_imports()

try:
    # Import vendored dependencies
    import rembg
    from rembg import remove as rembg_remove
    import PIL
    from PIL import Image
except ImportError as e:
    # Fallback message if vendored dependencies aren't available yet
    print(f"❌ Vendored dependencies not found: {e}")
    print("Please ensure all dependencies are properly vendored")
    sys.exit(1)


def remove_background(input_path, output_path=None):
    """
    Remove background from an image.
    
    Args:
        input_path (str): Path to input image
        output_path (str, optional): Path for output image. If None, adds '_no_bg' suffix
    
    Returns:
        str: Path to the output image
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not input_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_no_bg.png"
    else:
        output_path = Path(output_path)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Open and process the image
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()
        
        # Remove background using rembg
        output_data = rembg_remove(input_data)
        
        # Save the result
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
        
        print(f"✅ Background removed: {input_path.name} → {output_path.name}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error processing {input_path.name}: {e}")
        raise
