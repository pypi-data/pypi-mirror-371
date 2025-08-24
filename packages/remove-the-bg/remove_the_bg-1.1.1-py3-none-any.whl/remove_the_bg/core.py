"""
Core functionality for background removal.
"""

import os
import sys
from pathlib import Path


def get_system_imports():
    """Get system-installed dependencies with fallback to vendored rembg."""
    vendor_path = Path(__file__).parent / "vendor"
    
    try:
        # First try to import numpy and PIL from system
        import numpy
        from PIL import Image
        print("  ✅ Using system numpy and PIL")
        
        # Try to import rembg from system first
        try:
            import rembg
            print("  ✅ Using system rembg")
        except ImportError:
            # Fall back to vendored rembg if system doesn't have it
            if vendor_path.exists():
                original_path = sys.path[:]
                try:
                    # Add vendor path for rembg only
                    rembg_path = str(vendor_path / "rembg")
                    if rembg_path not in sys.path:
                        sys.path.insert(0, str(vendor_path))
                    
                    # Import vendored rembg
                    import rembg
                    print("  ✅ Using vendored rembg (system not available)")
                    
                finally:
                    # Restore original path
                    sys.path[:] = original_path
            else:
                raise ImportError("rembg not found in system or vendor directory")
        
        return numpy, rembg, Image
        
    except ImportError as e:
        # If system packages are missing, provide helpful error
        missing_packages = []
        
        try:
            import numpy
        except ImportError:
            missing_packages.append("numpy")
        
        try:
            from PIL import Image
        except ImportError:
            missing_packages.append("Pillow")
            
        if missing_packages:
            raise ImportError(
                f"Required packages not found: {', '.join(missing_packages)}. "
                f"Please install them with: pip install {' '.join(missing_packages)}"
            )
        else:
            raise ImportError(f"Failed to import dependencies: {e}")


def remove_background(input_path, output_path=None):
    """
    Remove background from an image.
    
    Args:
        input_path (str): Path to input image
        output_path (str, optional): Path for output image. If None, adds '_nobg' suffix
    
    Returns:
        str: Path to the output image
    """
    # Get imports from system/vendor
    numpy, rembg, Image = get_system_imports()
    
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
