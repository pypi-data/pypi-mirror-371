"""
Core functionality for background removal.
"""

import os
import sys
from pathlib import Path


def get_vendored_imports():
    """Get vendored dependencies using environment isolation."""
    vendor_path = Path(__file__).parent / "vendor"
    
    if not vendor_path.exists():
        raise ImportError(f"Vendor directory not found: {vendor_path}")
    
    # Use environment isolation to bypass numpy source directory detection
    import subprocess
    import tempfile
    import json
    
    # Create an isolated import script
    script_content = f'''
import sys
import os

# Clear existing modules to avoid conflicts
for mod in list(sys.modules.keys()):
    if any(pkg in mod for pkg in ["numpy", "rembg", "PIL"]):
        del sys.modules[mod]

# Set up isolated environment
vendor_path = r"{vendor_path}"
sys.path.insert(0, vendor_path)

# Suppress numpy warnings about source directories
os.environ["PYTHONWARNINGS"] = "ignore::UserWarning"

try:
    # Import and test vendored packages
    import numpy
    import rembg
    from PIL import Image
    
    print("SUCCESS")
    
except Exception as e:
    print(f"FAILED: {{e}}")
    sys.exit(1)
'''
    
    # Create temporary script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    
    try:
        # Test imports in subprocess
        result = subprocess.run(
            [sys.executable, script_path], 
            capture_output=True, 
            text=True, 
            timeout=30,
            env={**os.environ, "PYTHONWARNINGS": "ignore"}
        )
        
        if result.returncode != 0 or "FAILED" in result.stdout:
            raise ImportError(f"Vendor import test failed: {result.stdout} {result.stderr}")
        
        # If subprocess succeeded, do actual import
        return do_vendor_import()
        
    finally:
        try:
            os.unlink(script_path)
        except:
            pass


def do_vendor_import():
    """Perform the actual vendor import after verification."""
    vendor_path = Path(__file__).parent / "vendor"
    
    # Clear any existing conflicting modules
    modules_to_clear = [mod for mod in sys.modules.keys() 
                       if any(pkg in mod for pkg in ["numpy", "rembg", "PIL"])]
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    # Backup original path
    original_path = sys.path[:]
    original_warnings = os.environ.get("PYTHONWARNINGS", "")
    
    try:
        # Set up clean import environment
        sys.path.insert(0, str(vendor_path))
        os.environ["PYTHONWARNINGS"] = "ignore::UserWarning"
        
        # Import packages
        import numpy
        import rembg
        from PIL import Image
        
        # Verify we got vendored versions
        if not numpy.__file__.startswith(str(vendor_path)):
            raise ImportError(f"Not using vendored numpy: {numpy.__file__}")
        
        return numpy, rembg, Image
        
    finally:
        # Restore environment
        sys.path[:] = original_path
        if original_warnings:
            os.environ["PYTHONWARNINGS"] = original_warnings
        else:
            os.environ.pop("PYTHONWARNINGS", None)


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
