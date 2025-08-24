# Vendor Directory

This directory contains vendored (bundled) versions of external dependencies to make the package self-contained.

## Dependencies to Vendor

1. **rembg** - The core background removal library
2. **Pillow (PIL)** - Image processing library
3. **numpy** - Required by rembg
4. **onnxruntime** - Required by rembg for model inference

## How to Vendor Dependencies

### Method 1: Manual Vendoring (Recommended for control)

1. Install dependencies in a temporary environment:
   ```bash
   pip install rembg pillow numpy onnxruntime
   ```

2. Find the installed packages:
   ```bash
   python -c "import rembg; print(rembg.__file__)"
   python -c "import PIL; print(PIL.__file__)"
   ```

3. Copy the package directories to this vendor folder:
   - Copy `rembg/` → `remove_the_bg/vendor/rembg/`
   - Copy `PIL/` → `remove_the_bg/vendor/PIL/`
   - Copy `numpy/` → `remove_the_bg/vendor/numpy/`
   - Copy `onnxruntime/` → `remove_the_bg/vendor/onnxruntime/`

### Method 2: Automated Vendoring Script

Run the provided `vendor_deps.py` script which will automatically download and vendor all required dependencies.

## Structure After Vendoring

```
vendor/
├── __init__.py
├── rembg/
│   ├── __init__.py
│   ├── models/
│   └── ... (all rembg files)
├── PIL/
│   ├── __init__.py
│   └── ... (all Pillow files)
├── numpy/
│   ├── __init__.py
│   └── ... (all numpy files)
└── onnxruntime/
    ├── __init__.py
    └── ... (all onnxruntime files)
```

## Important Notes

- Make sure to include all model files from rembg
- Preserve the original directory structure
- Test thoroughly after vendoring
- The total size will be significant (50-100MB+)
