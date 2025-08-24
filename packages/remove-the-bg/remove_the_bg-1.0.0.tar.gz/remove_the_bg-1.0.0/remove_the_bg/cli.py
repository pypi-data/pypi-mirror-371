#!/usr/bin/env python3
"""
Command Line Interface for remove-the-bg package.
"""

import argparse
import os
import sys
from pathlib import Path
from .core import remove_background


def process_single_file(file_path):
    """Process a single image file."""
    try:
        remove_background(file_path)
        return True
    except Exception as e:
        print(f"❌ Failed to process {file_path}: {e}")
        return False


def process_folder(folder_path):
    """Process all images in a folder."""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return False
    
    if not folder.is_dir():
        print(f"❌ Not a directory: {folder_path}")
        return False
    
    # Find all image files
    image_extensions = ['.png', '.jpg', '.jpeg']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(folder.glob(f"*{ext}"))
        image_files.extend(folder.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"❌ No image files found in {folder_path}")
        return False
    
    print(f"🔍 Found {len(image_files)} image(s) to process...")
    
    success_count = 0
    for image_file in image_files:
        if process_single_file(image_file):
            success_count += 1
    
    print(f"✅ Successfully processed {success_count}/{len(image_files)} images")
    return success_count > 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Remove backgrounds from images",
        prog="rem"
    )
    
    parser.add_argument(
        "path",
        help="Path to image file or folder containing images"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output path (for single files only)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="remove-the-bg 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Check if path exists
    path = Path(args.path)
    if not path.exists():
        print(f"❌ Path not found: {args.path}")
        sys.exit(1)
    
    try:
        if path.is_file():
            # Process single file
            if args.output:
                remove_background(args.path, args.output)
            else:
                remove_background(args.path)
        elif path.is_dir():
            # Process folder
            if args.output:
                print("⚠️  Output path ignored when processing folders")
            process_folder(args.path)
        else:
            print(f"❌ Invalid path: {args.path}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
