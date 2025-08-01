#!/usr/bin/env python3
"""
Test script for BHI filtering to diagnose file access issues.
"""

import os
import sys
from pathlib import Path


def folder_access(folder_path):
    """Test basic folder and file access."""
    print(f"Testing access to folder: {folder_path}")

    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        return False

    if not os.path.isdir(folder_path):
        print(f"❌ Path is not a directory: {folder_path}")
        return False

    try:
        files = os.listdir(folder_path)
        print(f"✅ Successfully listed {len(files)} files in folder")

        # Test reading first few image files
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
        image_files = [f for f in files if Path(f).suffix.lower() in image_extensions]

        if not image_files:
            print("⚠️  No image files found in folder")
            return True

        print(f"Found {len(image_files)} image files")

        # Test access to first 5 image files
        for i, filename in enumerate(image_files[:5]):
            filepath = os.path.join(folder_path, filename)
            try:
                # Test if file is readable
                with open(filepath, "rb") as f:
                    f.read(1024)  # Read first 1KB
                print(f"✅ {filename} - accessible")
            except PermissionError:
                print(f"❌ {filename} - Permission denied")
            except Exception as e:
                print(f"❌ {filename} - Error: {e}")

        return True

    except PermissionError:
        print(f"❌ Permission denied accessing folder: {folder_path}")
        return False
    except Exception as e:
        print(f"❌ Error accessing folder: {e}")
        return False


if __name__ == "__main__":
    """Main test function."""
    print("=== BHI Filtering Test Script ===\n")

    # Get folder path from user
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = input("Enter the folder path to test: ").strip()

    if not folder_path:
        print("No folder path provided. Exiting.")
        sys.exit(0)

    # Test folder access
    if not folder_access(folder_path):
        print("\n❌ Folder access test failed. Please check:")
        print("1. Folder path is correct")
        print("2. You have read permissions for the folder")
        print("3. The folder contains image files")
    else:
        print("\n✅ Folder access test passed!")
        print("\nIf you're still having issues with BHI filtering:")
        print("1. Try running the script as administrator")
        print("2. Check if any files are locked by other applications")
        print("3. Try copying the folder to a different location")
        print("4. Use the 'report' action first to see what would be filtered")
