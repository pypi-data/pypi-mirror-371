"""
Core functionality for background removal.
"""

import os
import sys
import subprocess
from pathlib import Path


def _auto_install_packages(packages):
    """Automatically install missing packages using pip."""
    all_success = True
    try:
        # Use the same Python executable that's running this script
        python_executable = sys.executable
        
        for package in packages:
            print(f"    Installing {package}...")
            result = subprocess.run(
                [python_executable, "-m", "pip", "install", package, "--quiet"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"    ⚠️  Warning: Failed to install {package}")
                print(f"    Error: {result.stderr}")
                all_success = False
            else:
                print(f"    ✅ Successfully installed {package}")
                
    except subprocess.TimeoutExpired:
        print("    ⚠️  Installation timed out")
        all_success = False
    except Exception as e:
        print(f"    ⚠️  Installation error: {e}")
        all_success = False
    
    return all_success


def get_system_imports():
    """Get system-installed dependencies with fallback to vendored rembg."""
    vendor_path = Path(__file__).parent / "vendor"
    
    # Check system dependencies and auto-install if needed
    missing_packages = []
    numpy_compatible = False
    pil_available = False
    
    # Check numpy
    try:
        import numpy
        # Check version compatibility
        numpy_version = tuple(map(int, numpy.__version__.split('.')[:2]))
        if numpy_version >= (2, 0):
            print(f"  ⚠️  System numpy {numpy.__version__} >= 2.0.0, need <2.0.0")
            missing_packages.append("numpy>=1.21.0,<2.0.0")
        else:
            print(f"  ✅ Using system numpy {numpy.__version__}")
            numpy_compatible = True
    except ImportError:
        missing_packages.append("numpy>=1.21.0,<2.0.0")
    
    # Check PIL
    try:
        from PIL import Image
        print("  ✅ Using system PIL")
        pil_available = True
    except ImportError:
        missing_packages.append("Pillow>=8.0.0")
    
    # Auto-install missing packages
    if missing_packages:
        print(f"  📦 Installing missing packages: {', '.join(missing_packages)}")
        success = _auto_install_packages(missing_packages)
        
        if success:
            # Re-import after installation
            try:
                import numpy
                from PIL import Image
                print("  ✅ Successfully installed and imported dependencies")
                numpy_compatible = True
                pil_available = True
            except ImportError as retry_error:
                raise ImportError(f"Failed to import after installation: {retry_error}")
        else:
            print(f"  ❌ Failed to install packages. Please install manually: pip install {' '.join(missing_packages)}")
            return None
    
    # Now handle rembg (always after numpy/PIL are sorted)
    if numpy_compatible and pil_available:
        # Try to import rembg from system first
        try:
            import rembg
            print("  ✅ Using system rembg")
        except ImportError:
            # Fall back to vendored rembg
            if vendor_path.exists():
                original_path = sys.path[:]
                try:
                    if str(vendor_path) not in sys.path:
                        sys.path.insert(0, str(vendor_path))
                    import rembg
                    print("  ✅ Using vendored rembg (system not available)")
                finally:
                    sys.path[:] = original_path
            else:
                raise ImportError("rembg not found in system or vendor directory")
        
        return numpy, rembg, Image
    else:
        raise ImportError("Failed to ensure numpy and PIL compatibility")


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
    imports = get_system_imports()
    if imports is None:
        raise ImportError("Failed to get required dependencies")
    
    numpy, rembg, Image = imports
    
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
