import os
import shutil
import logging

IMAGE_TYPES = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".tiff", ".webp"]


def get_unique_filename(dest_dir, filename):
    """Return a unique filename in dest_dir by appending a counter if needed."""
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_name = filename
    while os.path.exists(os.path.join(dest_dir, unique_name)):
        unique_name = f"{base}_{counter}{ext}"
        counter += 1
    return unique_name


def perform_file_operation(src_path, dest_dir, operation, filename):
    """Performs file operations (copy, move, inplace save). Returns the path to the resulting file if successful, None otherwise."""
    try:
        if operation == "inplace":
            return src_path
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, get_unique_filename(dest_dir, filename))
        if operation == "copy":
            shutil.copy2(src_path, dest_path)
        elif operation == "move":
            shutil.move(src_path, dest_path)
        return dest_path
    except Exception as e:
        logging.error(f"Error performing {operation} on {src_path} to {dest_dir}: {e}")
        return None


def is_image_file(filename):
    """Checks if a file is an image based on its extension."""
    return any(filename.lower().endswith(image_type) for image_type in IMAGE_TYPES)
