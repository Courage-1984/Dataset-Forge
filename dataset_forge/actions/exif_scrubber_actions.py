import os
import subprocess
from typing import List, Tuple, Optional
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound

SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp")


def is_image_file(filename: str) -> bool:
    return filename.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)


def scrub_exif_single_folder(
    folder: str, dry_run: bool = False
) -> Tuple[int, List[str]]:
    """
    Scrub EXIF metadata from all images in a single folder using exiftool.
    Returns (num_processed, list_of_failed_files)
    """
    if not os.path.isdir(folder):
        raise ValueError(f"Input folder does not exist: {folder}")
    files = [f for f in os.listdir(folder) if is_image_file(f)]
    failed = []
    count = 0
    for fname in files:
        fpath = os.path.join(folder, fname)
        try:
            if not dry_run:
                # -overwrite_original ensures no backup files
                subprocess.run(
                    ["exiftool", "-all=", "-overwrite_original", fpath],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            count += 1
            log_operation("exif_scrub", f"Scrubbed EXIF from {fpath}")
        except Exception as e:
            failed.append(fname)
    return count, failed


def scrub_exif_hq_lq_folders(
    hq_folder: str, lq_folder: str, dry_run: bool = False
) -> Tuple[int, List[Tuple[str, str]]]:
    """
    Scrub EXIF metadata from paired HQ/LQ folders, preserving alignment by filename.
    Returns (num_pairs_processed, list_of_failed_pairs)
    """
    if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
        raise ValueError("Both HQ and LQ folders must exist.")
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    common_files = hq_files & lq_files
    failed = []
    count = 0
    for fname in sorted(common_files):
        hq_path = os.path.join(hq_folder, fname)
        lq_path = os.path.join(lq_folder, fname)
        try:
            if not dry_run:
                subprocess.run(
                    ["exiftool", "-all=", "-overwrite_original", hq_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                subprocess.run(
                    ["exiftool", "-all=", "-overwrite_original", lq_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            count += 1
        except Exception as e:
            failed.append((fname, str(e)))
    return count, failed


def has_exiftool() -> bool:
    """Check if exiftool is available in PATH."""
    try:
        subprocess.run(
            ["exiftool", "-ver"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except Exception:
        return False
