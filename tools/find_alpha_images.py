#!/usr/bin/env python3
"""
Find Images with Alpha Channels
A utility script to scan directories for images that contain alpha channels.

Usage:
    python tools/find_alpha_images.py <folder_path>
    python tools/find_alpha_images.py <folder_path> --count-only
    python tools/find_alpha_images.py <folder_path> --summary
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict

# Add the project root to the path so we can import dataset_forge modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataset_forge.utils.printing import print_info, print_success, print_warning, print_error
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.progress_utils import tqdm


def has_alpha_channel(image_path: str) -> bool:
    """Check if an image has an alpha channel.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if the image has an alpha channel, False otherwise
    """
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            return img.mode.endswith("A")
    except Exception as e:
        print_warning(f"Error checking alpha channel for {image_path}: {e}")
        return False


def find_images_with_alpha(folder_path: str, recursive: bool = True) -> List[str]:
    """Find all images with alpha channels in a folder.
    
    Args:
        folder_path: Path to the folder to search
        recursive: Whether to search subdirectories recursively
        
    Returns:
        List of image paths that have alpha channels
    """
    images_with_alpha = []
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print_error(f"Folder does not exist: {folder_path}")
        return images_with_alpha
    
    if not folder_path.is_dir():
        print_error(f"Path is not a directory: {folder_path}")
        return images_with_alpha
    
    # Supported image formats that can have alpha channels
    image_extensions = {'.png', '.tiff', '.tif', '.bmp', '.gif', '.webp'}
    
    if recursive:
        # Search recursively - first collect all image files
        image_files = [
            image_path for image_path in folder_path.rglob('*')
            if image_path.is_file() and image_path.suffix.lower() in image_extensions
        ]
        
        if not image_files:
            return images_with_alpha
            
        # Scan with progress bar
        for image_path in tqdm(image_files, desc="Scanning for alpha channels (recursive)"):
            if has_alpha_channel(str(image_path)):
                images_with_alpha.append(str(image_path))
    else:
        # Search only in the specified directory - first collect all image files
        image_files = [
            image_path for image_path in folder_path.iterdir()
            if image_path.is_file() and image_path.suffix.lower() in image_extensions
        ]
        
        if not image_files:
            return images_with_alpha
            
        # Scan with progress bar
        for image_path in tqdm(image_files, desc="Scanning for alpha channels"):
            if has_alpha_channel(str(image_path)):
                images_with_alpha.append(str(image_path))
    
    return images_with_alpha


def get_summary_stats(images_with_alpha: List[str]) -> Dict:
    """Get summary statistics about images with alpha channels.
    
    Args:
        images_with_alpha: List of image paths with alpha channels
        
    Returns:
        Dictionary with summary statistics
    """
    if not images_with_alpha:
        return {
            'total_images': 0,
            'formats': {},
            'total_size_mb': 0
        }
    
    formats = {}
    total_size = 0
    
    for image_path in images_with_alpha:
        path = Path(image_path)
        ext = path.suffix.lower()
        formats[ext] = formats.get(ext, 0) + 1
        
        try:
            total_size += path.stat().st_size
        except OSError:
            pass
    
    return {
        'total_images': len(images_with_alpha),
        'formats': formats,
        'total_size_mb': total_size / (1024 * 1024)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Find images with alpha channels in a directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/find_alpha_images.py /path/to/images
  python tools/find_alpha_images.py /path/to/images --count-only
  python tools/find_alpha_images.py /path/to/images --summary --no-recursive
        """
    )
    
    parser.add_argument(
        'folder_path',
        help='Path to the folder to search for images with alpha channels'
    )
    
    parser.add_argument(
        '--count-only',
        action='store_true',
        help='Only show the count of images with alpha channels'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary statistics'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subdirectories recursively'
    )
    
    args = parser.parse_args()
    
    print_info(f"🔍 Scanning for images with alpha channels in: {args.folder_path}")
    
    # Find images with alpha channels
    images_with_alpha = find_images_with_alpha(
        args.folder_path, 
        recursive=not args.no_recursive
    )
    
    if not images_with_alpha:
        print_success("✓ No images with alpha channels found.")
        return
    
    # Show results based on options
    if args.count_only:
        print_success(f"✓ Found {len(images_with_alpha)} images with alpha channels")
        return
    
    if args.summary:
        stats = get_summary_stats(images_with_alpha)
        print_success(f"✓ Found {stats['total_images']} images with alpha channels")
        print_info(f"📊 Total size: {stats['total_size_mb']:.2f} MB")
        print_info("📋 Format breakdown:")
        for ext, count in stats['formats'].items():
            print_info(f"  • {ext}: {count} images")
        return
    
    # Show full list
    print_success(f"✓ Found {len(images_with_alpha)} images with alpha channels:")
    for i, image_path in enumerate(images_with_alpha, 1):
        rel_path = os.path.relpath(image_path, args.folder_path)
        print_info(f"  {i:3d}. {rel_path}")


if __name__ == "__main__":
    main() 