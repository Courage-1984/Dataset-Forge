#!/usr/bin/env python3
"""
Test script for pepeline library to identify problematic files.
"""

import os
import sys
from pathlib import Path

from dataset_forge.utils.printing import print_info, print_success, print_warning, print_error


def pepeline_reading(folder_path, max_files=10):
    """Test pepeline library's read function on files in the folder."""
    print_info(f"Testing pepeline library on folder: {folder_path}")

    try:
        from pepeline import read, ImgFormat

        print_success("Successfully imported pepeline library")
    except ImportError as e:
        print_error(f"Failed to import pepeline: {e}")
        return False

    if not os.path.exists(folder_path):
        print_error(f"Folder does not exist: {folder_path}")
        return False

    try:
        files = os.listdir(folder_path)
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
        image_files = [f for f in files if Path(f).suffix.lower() in image_extensions]

        if not image_files:
            print_warning("No image files found in folder")
            return False

        print_info(f"Found {len(image_files)} image files")
        print_info(f"Testing first {min(max_files, len(image_files))} files...")

        success_count = 0
        error_count = 0

        for i, filename in enumerate(image_files[:max_files]):
            filepath = os.path.join(folder_path, filename)
            try:
                # Test pepeline read function
                image = read(filepath, format=ImgFormat.F32)
                print_success(
                    f"{filename} - pepeline read successful (shape: {image.shape})"
                )
                success_count += 1
            except Exception as e:
                print_error(f"{filename} - pepeline read failed: {e}")
                error_count += 1

        print_info(f"\nResults: {success_count} successful, {error_count} failed")

        if error_count > 0:
            print_warning("\nSome files failed to read with pepeline. This could be due to:")
            print_info("1. Corrupted image files")
            print_info("2. Unsupported image formats")
            print_info("3. File permission issues")
            print_info("4. Memory constraints")
            return False
        else:
            print_success("\nAll tested files read successfully with pepeline!")
            return True

    except Exception as e:
        print_error(f"Error during testing: {e}")
        return False


if __name__ == "__main__":
    print_info("=== Pepeline Library Test Script ===\n")

    # Get folder path from user
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = input("Enter the folder path to test: ").strip()

    if not folder_path:
        print_error("No folder path provided. Exiting.")
        sys.exit(0)
    else:
        # Test pepeline reading
        if pepeline_reading(folder_path):
            print_success("\nPepeline library test passed!")
            print_info("The BHI filtering should work with the improved error handling.")
        else:
            print_error("\nPepeline library test failed!")
            print_info(
                "The improved BHI filtering will skip problematic files and continue."
            )
