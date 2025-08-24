"""
Core functionality for background removal.
"""

import os
import sys
from pathlib import Path


def setup_vendor_imports():
    """Setup imports for vendored dependencies with complete isolation."""
    vendor_path = Path(__file__).parent / "vendor"
    vendor_str = str(vendor_path)
    
    # Aggressively clear ALL related modules and their submodules
    modules_to_clear = []
    for mod_name in list(sys.modules.keys()):
        if any(mod_name.startswith(pkg) or pkg in mod_name 
               for pkg in ['numpy', 'rembg', 'PIL', 'onnxruntime', 'cv2', 'skimage']):
            modules_to_clear.append(mod_name)
    
    for mod in modules_to_clear:
        if mod in sys.modules:
            del sys.modules[mod]
    
    # Create completely isolated path with ONLY our vendor directory
    original_path = sys.path[:]
    
    # Keep only essential Python paths (stdlib, etc.) and our vendor
    essential_paths = []
    for path in original_path:
        path_lower = path.lower()
        if (not path or  # current directory
            'python' in path_lower and ('lib' in path_lower or 'dll' in path_lower) or  # stdlib
            path.endswith('.zip')):  # zip imports
            essential_paths.append(path)
    
    # Set minimal path with vendor first
    sys.path.clear()
    sys.path.append(vendor_str)
    sys.path.extend(essential_paths)
    
    # Force environment variables
    os.environ['PYTHONPATH'] = vendor_str
    if 'NUMPY_PATH' in os.environ:
        del os.environ['NUMPY_PATH']


def get_vendored_imports():
    """Get vendored dependencies with complete numpy source detection bypass."""
    try:
        # Setup vendor paths and clear conflicts
        setup_vendor_imports()
        
        # Special handling for numpy source directory detection bypass
        vendor_path_str = str(Path(__file__).parent / "vendor")
        
        # Temporarily disable numpy's source directory checks
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning, module="numpy")
        
        # Force import numpy from vendor by manipulating its detection mechanism
        numpy_path = Path(vendor_path_str) / "numpy"
        
        # Import numpy with special handling to bypass source directory detection
        import importlib.util
        import types
        
        # Load numpy module manually to bypass source directory checks
        numpy_init_path = numpy_path / "__init__.py"
        if numpy_init_path.exists():
            spec = importlib.util.spec_from_file_location("numpy", numpy_init_path)
            numpy_module = importlib.util.module_from_spec(spec)
            
            # Override numpy's source directory detection before loading
            original_path = sys.path[:]
            try:
                # Clear sys.path to contain only vendor and essential paths
                sys.path = [vendor_path_str] + [p for p in original_path if 'numpy' not in p.lower()]
                
                # Execute the module
                spec.loader.exec_module(numpy_module)
                sys.modules['numpy'] = numpy_module
                
            finally:
                # Restore minimal path
                sys.path = [vendor_path_str] + [p for p in original_path if not any(
                    exclude in p.lower() for exclude in ['site-packages', 'dist-packages']) or p == vendor_path_str]
        
        # Now import other packages normally
        import rembg
        # Verify we're using vendored version
        if not rembg.__file__.startswith(vendor_path_str):
            raise ImportError(f"Using system rembg instead of vendored: {rembg.__file__}")
            
        from rembg import remove as rembg_remove
        import PIL
        from PIL import Image
        
        return rembg_remove, Image
        
    except ImportError as e:
        # More detailed error message
        vendor_path = Path(__file__).parent / "vendor"
        error_msg = f"""
❌ Vendored dependencies not found: {e}

This usually means:
1. The package wasn't built correctly with vendored dependencies
2. There's a conflict with system-installed packages
3. The installation is corrupted

Solutions:
1. Reinstall: pip uninstall remove-the-bg && pip install remove-the-bg --no-cache-dir
2. Clear Python cache: python -Bc "import sys; [sys.modules.pop(m, None) for m in list(sys.modules) if 'numpy' in m or 'rembg' in m]"
3. Check vendor directory: {vendor_path}

Please ensure all dependencies are properly vendored"""
        
        print(error_msg)
        raise RuntimeError("Failed to load vendored dependencies") from e


def remove_background(input_path, output_path=None):
    """
    Remove background from an image.
    
    Args:
        input_path (str): Path to input image
        output_path (str, optional): Path for output image. If None, adds '_no_bg' suffix
    
    Returns:
        str: Path to the output image
    """
    # Get imports dynamically
    rembg_remove, Image = get_vendored_imports()
    
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not input_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_no_bg.png"
    else:
        output_path = Path(output_path)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"  Processing: {input_path.name}")
        
        # Open and process the image
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()
        
        # Remove background using rembg
        output_data = rembg_remove(input_data)
        
        # Save the result
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
        
        print(f"  ✅ Saved: {output_path.name}")
        return str(output_path)
        
    except Exception as e:
        error_msg = f"Error processing {input_path.name}: {e}"
        print(f"  ❌ {error_msg}")
        raise Exception(error_msg)
