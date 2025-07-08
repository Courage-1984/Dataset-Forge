import os
import shutil
from PIL import Image
from typing import List, Tuple, Dict, Optional
from tqdm import tqdm


def get_image_orientation(image_path: str) -> Optional[str]:
    """Return 'landscape', 'portrait', or 'square' for the given image, or None if not an image."""
    try:
        with Image.open(image_path) as img:
            w, h = img.size
            if w > h:
                return "landscape"
            elif h > w:
                return "portrait"
            elif w == h:
                return "square"
    except Exception:
        return None
    return None


def scan_folder_for_orientations(
    folder: str,
    extensions: Tuple[str, ...] = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"),
) -> Dict[str, List[str]]:
    """Scan a folder and return a dict with keys 'landscape', 'portrait', 'square' mapping to lists of file paths."""
    result = {"landscape": [], "portrait": [], "square": []}
    files = [
        fname for fname in os.listdir(folder) if fname.lower().endswith(extensions)
    ]
    for fname in tqdm(files, desc="Checking image orientations"):
        fpath = os.path.join(folder, fname)
        orientation = get_image_orientation(fpath)
        if orientation:
            result[orientation].append(fpath)
    return result


def organize_images_by_orientation(
    input_folder: str,
    output_folder: str,
    orientations: List[str],
    operation: str = "copy",
    extensions: Tuple[str, ...] = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"),
) -> Dict[str, List[str]]:
    """Copy or move images of specified orientations from input_folder to output_folder/orientation/. Returns dict of moved/copied files."""
    os.makedirs(output_folder, exist_ok=True)
    found = scan_folder_for_orientations(input_folder, extensions)
    result = {o: [] for o in orientations}
    for orientation in orientations:
        out_dir = os.path.join(output_folder, orientation)
        os.makedirs(out_dir, exist_ok=True)
        files = found.get(orientation, [])
        for fpath in tqdm(files, desc=f"{operation.title()}ing {orientation} images"):
            dest = os.path.join(out_dir, os.path.basename(fpath))
            if operation == "move":
                shutil.move(fpath, dest)
            else:
                shutil.copy2(fpath, dest)
            result[orientation].append(dest)
    return result


def organize_hq_lq_by_orientation(
    hq_folder: str,
    lq_folder: str,
    output_hq_folder: str,
    output_lq_folder: str,
    orientations: List[str],
    operation: str = "copy",
    extensions: Tuple[str, ...] = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"),
) -> Dict[str, List[Tuple[str, str]]]:
    """Copy or move HQ/LQ image pairs of specified orientations, keeping alignment. Returns dict of (hq, lq) pairs."""
    os.makedirs(output_hq_folder, exist_ok=True)
    os.makedirs(output_lq_folder, exist_ok=True)
    hq_files = {
        os.path.splitext(f)[0]: f
        for f in os.listdir(hq_folder)
        if f.lower().endswith(extensions)
    }
    lq_files = {
        os.path.splitext(f)[0]: f
        for f in os.listdir(lq_folder)
        if f.lower().endswith(extensions)
    }
    common_keys = set(hq_files.keys()) & set(lq_files.keys())
    result = {o: [] for o in orientations}
    for key in common_keys:
        hq_path = os.path.join(hq_folder, hq_files[key])
        lq_path = os.path.join(lq_folder, lq_files[key])
        orientation = get_image_orientation(hq_path)
        if orientation in orientations:
            out_hq_dir = os.path.join(output_hq_folder, orientation)
            out_lq_dir = os.path.join(output_lq_folder, orientation)
            os.makedirs(out_hq_dir, exist_ok=True)
            os.makedirs(out_lq_dir, exist_ok=True)
            dest_hq = os.path.join(out_hq_dir, os.path.basename(hq_path))
            dest_lq = os.path.join(out_lq_dir, os.path.basename(lq_path))
            if operation == "move":
                shutil.move(hq_path, dest_hq)
                shutil.move(lq_path, dest_lq)
            else:
                shutil.copy2(hq_path, dest_hq)
                shutil.copy2(lq_path, dest_lq)
            result[orientation].append((dest_hq, dest_lq))
    return result
