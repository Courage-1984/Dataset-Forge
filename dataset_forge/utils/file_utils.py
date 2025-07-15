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
    import shutil

    oxipng_bin = shutil.which("oxipng")
    if not oxipng_bin:
        print(f"[Oxipng] Not found in PATH. Skipping optimization for {image_path}.")
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
            print(f"[Oxipng] Optimized: {image_path}")
        else:
            print(f"[Oxipng] Error optimizing {image_path}: {result.stderr}")
    except Exception as e:
        print(f"[Oxipng] Exception: {e}")


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
