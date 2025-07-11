#!/usr/bin/env python3
"""
Test script for pepeline library to identify problematic files.
"""

import os
import sys
from pathlib import Path


def test_pepeline_reading(folder_path, max_files=10):
    """Test pepeline library's read function on files in the folder."""
    print(f"Testing pepeline library on folder: {folder_path}")

    try:
        from pepeline import read, ImgFormat

        print("✅ Successfully imported pepeline library")
    except ImportError as e:
        print(f"❌ Failed to import pepeline: {e}")
        return False

    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        return False

    try:
        files = os.listdir(folder_path)
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
        image_files = [f for f in files if Path(f).suffix.lower() in image_extensions]

        if not image_files:
            print("⚠️  No image files found in folder")
            return False

        print(f"Found {len(image_files)} image files")
        print(f"Testing first {min(max_files, len(image_files))} files...")

        success_count = 0
        error_count = 0

        for i, filename in enumerate(image_files[:max_files]):
            filepath = os.path.join(folder_path, filename)
            try:
                # Test pepeline read function
                image = read(filepath, format=ImgFormat.F32)
                print(
                    f"✅ {filename} - pepeline read successful (shape: {image.shape})"
                )
                success_count += 1
            except Exception as e:
                print(f"❌ {filename} - pepeline read failed: {e}")
                error_count += 1

        print(f"\nResults: {success_count} successful, {error_count} failed")

        if error_count > 0:
            print("\nSome files failed to read with pepeline. This could be due to:")
            print("1. Corrupted image files")
            print("2. Unsupported image formats")
            print("3. File permission issues")
            print("4. Memory constraints")
            return False
        else:
            print("\n✅ All tested files read successfully with pepeline!")
            return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False


def main():
    """Main test function."""
    print("=== Pepeline Library Test Script ===\n")

    # Get folder path from user
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = input("Enter the folder path to test: ").strip()

    if not folder_path:
        print("No folder path provided. Exiting.")
        return

    # Test pepeline reading
    if test_pepeline_reading(folder_path):
        print("\n✅ Pepeline library test passed!")
        print("The BHI filtering should work with the improved error handling.")
    else:
        print("\n❌ Pepeline library test failed!")
        print("The improved BHI filtering will skip problematic files and continue.")


if __name__ == "__main__":
    main()
