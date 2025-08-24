"""
Core functionality for background removal.
"""

import os
import sys
from pathlib import Path


def get_vendored_imports():
    """Get vendored dependencies with absolute isolation."""
    vendor_path = Path(__file__).parent / "vendor"
    
    if not vendor_path.exists():
        raise ImportError(f"Vendor directory not found: {vendor_path}")
    
    # Store original state to restore later
    original_path = sys.path[:]
    original_cwd = os.getcwd()
    
    # Store modules that might conflict
    conflicting_modules = {}
    module_prefixes = ['numpy', 'rembg', 'PIL', 'onnx']
    
    for mod_name in list(sys.modules.keys()):
        if any(prefix in mod_name for prefix in module_prefixes):
            conflicting_modules[mod_name] = sys.modules.pop(mod_name, None)
    
    try:
        # Change to a different directory (away from source)
        temp_dir = Path.home() / '.remove_the_bg_temp'
        temp_dir.mkdir(exist_ok=True)
        os.chdir(temp_dir)
        
        # Set up completely clean sys.path
        sys.path.clear()
        sys.path.append(str(vendor_path))  # Vendor first
        
        # Add only essential Python paths
        import sys as system
        python_dir = Path(system.executable).parent
        essential_paths = [
            str(python_dir / 'Lib'),
            str(python_dir / 'DLLs'),
            str(python_dir / 'lib'),
            str(python_dir.parent / 'Lib' / 'site-packages'),
        ]
        
        for path in essential_paths:
            if Path(path).exists():
                sys.path.append(path)
        
        # Set environment to prevent numpy from detecting source directory
        env_backup = {}
        env_vars = {
            'PYTHONWARNINGS': 'ignore',
            'NUMPY_DISABLE_SOURCE_DETECTION': '1',
            'PYTHONDONTWRITEBYTECODE': '1',
            'NUMPY_EXPERIMENTAL_DTYPE_API': '1'
        }
        
        for var, value in env_vars.items():
            env_backup[var] = os.environ.get(var)
            os.environ[var] = value
        
        try:
            # Suppress warnings during import
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # Import packages in specific order
                import numpy
                import rembg  
                from PIL import Image
                
                return numpy, rembg, Image
                
        finally:
            # Restore environment
            for var, old_value in env_backup.items():
                if old_value is not None:
                    os.environ[var] = old_value
                else:
                    os.environ.pop(var, None)
    
    except Exception as e:
        # If import failed, restore conflicting modules
        sys.modules.update(conflicting_modules)
        raise ImportError(f"Failed to import vendored packages: {e}")
    
    finally:
        # Always restore original state
        os.chdir(original_cwd)
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
