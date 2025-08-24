"""
Core functionality for background removal.
"""

import os
import sys
from pathlib import Path


def get_vendored_imports():
    """Get vendored dependencies using direct sys.path manipulation."""
    vendor_path = Path(__file__).parent / "vendor"
    
    if not vendor_path.exists():
        raise ImportError(f"Vendor directory not found: {vendor_path}")
    
    # Store original environment
    original_path = sys.path[:]
    original_modules = set(sys.modules.keys())
    
    try:
        # Clear potentially problematic modules
        problematic_modules = [mod for mod in sys.modules.keys() 
                             if any(pkg in mod for pkg in ['numpy', 'rembg', 'PIL', 'onnx'])]
        for mod in problematic_modules:
            sys.modules.pop(mod, None)
        
        # Set up clean import path with only vendor directory first
        sys.path.clear()
        sys.path.append(str(vendor_path))
        
        # Add minimal required Python paths (stdlib only)
        import platform
        python_dir = Path(platform.executable).parent
        
        # Add essential Python paths
        for essential_path in [
            str(python_dir / 'Lib'),
            str(python_dir / 'DLLs'),
            str(python_dir / 'lib' / 'python3.dll'),
        ]:
            if Path(essential_path).exists():
                sys.path.append(essential_path)
        
        # Suppress all warnings during import
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Set environment variables to disable numpy source detection
            import os
            old_pythonwarnings = os.environ.get('PYTHONWARNINGS', '')
            old_pythonpath = os.environ.get('PYTHONPATH', '')
            
            os.environ['PYTHONWARNINGS'] = 'ignore'
            os.environ['NUMPY_DISABLE_SOURCE_DETECTION'] = '1'
            
            try:
                # Import numpy first
                import numpy
                
                # Import other packages
                import rembg
                from PIL import Image
                
                return numpy, rembg, Image
                
            finally:
                # Restore environment
                if old_pythonwarnings:
                    os.environ['PYTHONWARNINGS'] = old_pythonwarnings
                else:
                    os.environ.pop('PYTHONWARNINGS', None)
                    
                if old_pythonpath:
                    os.environ['PYTHONPATH'] = old_pythonpath
                else:
                    os.environ.pop('PYTHONPATH', None)
                    
                os.environ.pop('NUMPY_DISABLE_SOURCE_DETECTION', None)
    
    finally:
        # Always restore original path
        sys.path[:] = original_path


def remove_background(input_path, output_path=None):
    """
    Remove background from an image.
    
    Args:
        input_path (str): Path to input image
        output_path (str, optional): Path for output image. If None, adds '_nobg' suffix
    
    Returns:
        str: Path to the output image
    """
    # Get imports dynamically
    numpy, rembg, Image = get_vendored_imports()
    
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not input_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_nobg.png"
    else:
        output_path = Path(output_path)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"  Processing: {input_path.name}")
        
        # Open and process the image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Remove background
            output = rembg.remove(img)
            
            # Save result
            output.save(output_path)
        
        print(f"  ✅ Saved: {output_path.name}")
        return str(output_path)
        
    except Exception as e:
        error_msg = f"Error processing {input_path.name}: {e}"
        print(f"  ❌ {error_msg}")
        raise Exception(error_msg)


def process_images(paths):
    """Process multiple images or directories."""
    from pathlib import Path
    import glob
    
    results = []
    errors = []
    
    for path_str in paths:
        path = Path(path_str)
        
        if path.is_file():
            # Single file
            try:
                if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    output_path = remove_background(str(path))
                    results.append((str(path), output_path))
                else:
                    errors.append(f"Unsupported format: {path}")
            except Exception as e:
                errors.append(f"Error processing {path}: {e}")
                
        elif path.is_dir():
            # Directory - find all image files
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
            for ext in image_extensions:
                for img_path in path.glob(ext):
                    try:
                        output_path = remove_background(str(img_path))
                        results.append((str(img_path), output_path))
                    except Exception as e:
                        errors.append(f"Error processing {img_path}: {e}")
                        
        else:
            # Glob pattern
            for img_path in glob.glob(path_str):
                try:
                    if Path(img_path).suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                        output_path = remove_background(img_path)
                        results.append((img_path, output_path))
                except Exception as e:
                    errors.append(f"Error processing {img_path}: {e}")
    
    return results, errors
