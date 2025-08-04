#!/usr/bin/env python3
"""
File utilities for Dataset Forge.

This module provides file operation utilities including path handling,
file type detection, and optimization functions.
"""

import os
import shutil
from typing import List, Optional, Callable

from dataset_forge.utils.printing import print_info, print_warning, print_error
from dataset_forge.utils.cache_utils import in_memory_cache

# Supported image file types
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".gif"}


def get_unique_filename(dest_dir, filename):
    """Generate a unique filename in the destination directory."""
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(dest_dir, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename


def perform_file_operation(src_path, dest_dir, operation, filename):
    """Perform file operation (copy, move, or in-place)."""
    dest_path = os.path.join(dest_dir, filename)
    
    if operation == "copy":
        shutil.copy2(src_path, dest_path)
    elif operation == "move":
        shutil.move(src_path, dest_path)
    elif operation == "inplace":
        return src_path  # No operation needed
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    return dest_path


@in_memory_cache(maxsize=512)  # Cache file type checks
def is_image_file(filename):
    """Check if a filename represents an image file."""
    return any(filename.lower().endswith(image_type) for image_type in IMAGE_TYPES)


def align_image_pairs_stub(hq_path, lq_path):
    # TODO: Implement image pair alignment logic
    return []


def get_output_path_stub(src_path, dest_dir, action):
    # TODO: Implement output path logic for copy/move/inplace
    return src_path


def run_oxipng_stub(image_path, level=4):
    # Replaced by real implementation below
    pass


def run_oxipng(image_path, level=4, strip=None, alpha=False):
    """Run oxipng on the given image_path with the specified options.
    Args:
        image_path (str): Path to the PNG image.
        level (int|str): Optimization level (0-6 or 'max').
        strip (str|None): Metadata to strip ('safe', 'all', or comma-separated list).
        alpha (bool): Whether to use --alpha for transparent pixel optimization.
    """
    import subprocess

    oxipng_bin = shutil.which("oxipng")
    if not oxipng_bin:
        print_warning(f"[Oxipng] Not found in PATH. Skipping optimization for {image_path}.")
        return
    level_arg = str(level) if isinstance(level, int) else level
    cmd = [oxipng_bin, "-o", str(level_arg)]
    if strip:
        cmd += ["--strip", strip]
    if alpha:
        cmd.append("--alpha")
    cmd.append(image_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print_info(f"[Oxipng] Optimized: {image_path}")
        else:
            print_error(f"[Oxipng] Error optimizing {image_path}: {result.stderr}")
    except Exception as e:
        print_error(f"[Oxipng] Exception: {e}")


def archive_folder(
    folder_path,
    out_name,
    archive_format="zip",
    compression_level=5,
    progress_callback=None,
):
    """
    Archive a folder to .zip, .tar, or .tar.gz.
    - folder_path: path to folder
    - out_name: output archive file path
    - archive_format: 'zip', 'tar', 'gztar'
    - compression_level: 1-9 (where supported)
    - progress_callback: function to call after each file (for progress bar)
    """
    import zipfile
    import tarfile

    file_list = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            file_list.append(os.path.join(root, f))
    if archive_format == "zip":
        compression = zipfile.ZIP_DEFLATED
        with zipfile.ZipFile(
            out_name, "w", compression, compresslevel=compression_level
        ) as zf:
            for file in file_list:
                arcname = os.path.relpath(file, folder_path)
                zf.write(file, arcname)
                if progress_callback:
                    progress_callback()
    elif archive_format == "gztar":
        with tarfile.open(out_name, "w:gz", compresslevel=compression_level) as tf:
            for file in file_list:
                arcname = os.path.relpath(file, folder_path)
                tf.add(file, arcname=arcname)
                if progress_callback:
                    progress_callback()
    elif archive_format == "tar":
        with tarfile.open(out_name, "w") as tf:
            for file in file_list:
                arcname = os.path.relpath(file, folder_path)
                tf.add(file, arcname=arcname)
                if progress_callback:
                    progress_callback()
    else:
        raise ValueError(f"Unsupported archive format: {archive_format}")
    return out_name
