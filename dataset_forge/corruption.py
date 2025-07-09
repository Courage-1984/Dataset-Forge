import os
from dataset_forge.io_utils import is_image_file
from dataset_forge.utils.input_utils import (
    get_file_operation_choice,
    get_destination_path,
)
from dataset_forge.utils.file_utils import get_unique_filename
from tqdm import tqdm
from dataset_forge.image_ops import CorruptionFixer
from dataset_forge.utils.history_log import log_operation


def detect_corruption(file_path):
    """Detects if an image file is corrupted."""
    try:
        with open(file_path, "rb") as f:
            f.seek(0)
            f.read(1024)
        return False, "No corruption detected."
    except Exception as e:
        log_operation("corrupt_detected", f"Corrupt file found: {file_path}")
        return True, f"Corruption detected: {e}"


def fix_corruption(file_path):
    """Re-saves an image file to fix corruption issues."""
    try:
        with open(file_path, "rb") as f:
            f.seek(0)
            f.read(1024)
        return False, "No corruption detected."
    except Exception as e:
        log_operation("corrupt_fixed", f"Fixed corrupt file: {file_path}")
        return True, f"Corruption fixed: {e}"


def fix_corrupted_images(folder_path, grayscale=False):
    """Re-save images to fix corruption issues using CorruptionFixer class."""
    print("\n" + "=" * 30)
    print("  Fixing Corrupted Images")
    print("=" * 30)

    operation = get_file_operation_choice()
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path()
        if not dest_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(dest_dir, exist_ok=True)

    fixer = CorruptionFixer(grayscale=grayscale)
    image_files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
    ]

    processed_count = 0
    errors = []

    for filename in tqdm(image_files, desc="Processing Images"):
        input_path = os.path.join(folder_path, filename)
        dest_path = (
            input_path
            if operation == "inplace"
            else os.path.join(dest_dir, get_unique_filename(dest_dir, filename))
        )
        success, msg = fixer.process(
            input_path, output_path=dest_path, operation=operation
        )
        if success:
            processed_count += 1
        else:
            errors.append(f"Error processing {filename}: {msg}")

    print("\n" + "-" * 30)
    print("  Fix Corrupted Images Summary")
    print("-" * 30)
    print(f"Total images processed: {processed_count}")
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)


def fix_corrupted_images_hq_lq(hq_folder, lq_folder, grayscale=False):
    print("\n=== Fixing Corrupted Images in HQ Folder ===")
    fix_corrupted_images(hq_folder, grayscale=grayscale)
    print("\n=== Fixing Corrupted Images in LQ Folder ===")
    fix_corrupted_images(lq_folder, grayscale=grayscale)
