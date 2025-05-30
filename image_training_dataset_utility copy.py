import os
import random
import shutil
from PIL import Image, ImageEnhance, UnidentifiedImageError, ImageFont, ImageDraw
from collections import Counter, defaultdict
from tqdm import tqdm
import cv2
import numpy as np
import concurrent.futures
import logging
import sys
import traceback
import imageio
import torch

# Setup logging for better error reporting in background tasks
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = "".join(traceback.format_tb(tb))
    print(f"Uncaught exception:\n{text}\n{ex_cls.__name__}: {ex}")
    logging.critical(f"Uncaught exception:\n{text}\n{ex_cls.__name__}: {ex}")


sys.excepthook = log_uncaught_exceptions


def get_folder_path(prompt):
    while True:
        path = input(prompt).strip()
        if os.path.isdir(path):
            return path
        else:
            print("Error: Invalid path. Please enter a valid directory.")


def get_file_operation_choice():
    while True:
        choice = input("Enter operation choice (copy/move/inplace): ").strip().lower()
        if choice in ["copy", "move", "inplace"]:
            return choice
        else:
            print("Invalid choice. Please enter 'copy', 'move', or 'inplace'.")


def get_destination_path(is_optional=False):
    while True:
        path = input(
            "Enter the destination directory path (leave blank if not moving/copying to a new location): "
        ).strip()
        if is_optional and not path:
            return ""
        # Check if the parent directory exists. If not, offer to create.
        parent_dir = os.path.dirname(path) or "."
        if not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir)
                print(f"Created parent directory: {parent_dir}")
                return path
            except OSError as e:
                print(f"Error creating parent directory {parent_dir}: {e}")
                print("Please enter a valid path.")
        else:
            return path


# Helper to avoid filename collisions (Adapted from combine_folders.py)
def get_unique_filename(dest_dir, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(dest_dir, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename


def get_pairs_to_process(matching_files, operation_name="process"):
    """
    Prompts the user for how many pairs to process (all, specific number, percentage, or random)
    and returns a randomly ordered list of selected file names.
    """
    if not matching_files:
        print(f"No matching pairs found to {operation_name}.")
        return []

    num_available = len(matching_files)
    print(f"\nFound {num_available} matching pairs.")

    while True:
        choice_prompt = (
            f"How many pairs do you want to {operation_name}?\n"
            f"  - Enter 'all' to {operation_name} all {num_available} pairs.\n"
            f"  - Enter a specific number (e.g., 100).\n"
            f"  - Enter a percentage (e.g., 10% of {num_available}).\n"
            f"  - Enter 'random' for a random number of pairs (1 to {num_available}).\n"
            f"Your choice: "
        )
        choice = input(choice_prompt).strip().lower()

        num_to_process = 0

        if choice == "all":
            num_to_process = num_available
            break
        elif choice == "random":
            if num_available == 0:
                num_to_process = 0
            else:
                num_to_process = random.randint(1, num_available)
            print(f"Selected random amount: {num_to_process} pairs.")
            break
        elif choice.endswith("%"):
            try:
                percentage = float(choice[:-1])
                if 0 <= percentage <= 100:
                    num_to_process = int(num_available * (percentage / 100))
                    break
                else:
                    print("Percentage must be between 0 and 100.")
            except ValueError:
                print("Invalid percentage format. Example: '10%'")
        else:
            try:
                num = int(choice)
                if 0 <= num <= num_available:
                    num_to_process = num
                    break
                else:
                    print(f"Number of pairs must be between 0 and {num_available}.")
            except ValueError:
                print(
                    "Invalid input. Please enter 'all', a number, a percentage (e.g., '10%'), or 'random'."
                )

    if num_to_process == 0:
        print(f"No pairs selected to {operation_name}. Exiting this operation.")
        return []

    print(
        f"\nWill {operation_name} {num_to_process} pairs out of {num_available} available pairs."
    )
    selected_files = random.sample(matching_files, num_to_process)
    random.shuffle(selected_files)  # Ensure processing in random order
    return selected_files


# Supported image types for verification
IMAGE_TYPES = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".tiff", ".webp"]


def is_image_file(filename):
    """Checks if a file is an image based on its extension."""
    return any(filename.lower().endswith(image_type) for image_type in IMAGE_TYPES)


def check_image_integrity(file_path, in_depth):
    """Checks if an image file is corrupted."""
    try:
        with Image.open(file_path) as img:
            if in_depth:
                img.load()  # Fully load the image data
            else:
                img.verify()  # Quick check
        return True
    except (IOError, SyntaxError, UnidentifiedImageError, Exception) as e:
        # Catch a broader Exception for other potential issues during loading/verification
        # print(f"Error verifying {file_path}: {e}") # Avoid verbose output during check
        return False


def perform_file_operation(src_path, dest_dir, operation, filename):
    """
    Performs file operations (copy, move, inplace save).
    Returns the path to the resulting file if successful, None otherwise.
    """
    try:
        if operation == "inplace":
            # For inplace operations, the dest_dir is not used for creating a new path.
            # The file is modified and saved back to src_path.
            # This function currently only handles moving/copying.
            # Inplace modifications will be handled directly in the functions that modify images.
            return (
                src_path  # Return original path if inplace, as no new file is created.
            )

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


# --- Function from hq_lq_scale.py ---
def find_hq_lq_scale(hq_folder, lq_folder, verbose=True):
    if verbose:
        print("\n" + "=" * 30)
        print("   Finding HQ/LQ Scale")
        print("=" * 30)

    hq_files = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )

    scales = []
    inconsistent_scales = []
    missing_lq = []
    missing_hq = []

    if verbose:
        print(f"Processing {len(hq_files)} HQ files and {len(lq_files)} LQ files...")

    for hq_file in tqdm(hq_files, desc="Finding Scale", disable=not verbose):
        if hq_file in lq_files:
            hq_path = os.path.join(hq_folder, hq_file)
            lq_path = os.path.join(
                lq_folder, hq_file
            )  # Assuming same filename in LQ folder

            try:
                with Image.open(hq_path) as hq_img:
                    hq_width, hq_height = hq_img.size
                with Image.open(lq_path) as lq_img:
                    lq_width, lq_height = lq_img.size

                if lq_width == 0 or lq_height == 0:
                    inconsistent_scales.append(
                        f"{hq_file}: Division by zero in LQ dimension"
                    )
                    continue

                width_scale = hq_width / lq_width
                height_scale = hq_height / lq_height

                if abs(width_scale - height_scale) < 1e-9:
                    scales.append(
                        round(width_scale, 2)
                    )  # Round for consistent grouping
                else:
                    inconsistent_scales.append(
                        f"{hq_file}: Inconsistent Scale: Width {width_scale:.2f}, Height {height_scale:.2f}"
                    )

            except Exception as e:
                inconsistent_scales.append(f"Could not process file {hq_file}: {e}")
        else:
            missing_lq.append(hq_file)

    for lq_file in lq_files:
        if lq_file not in hq_files:
            missing_hq.append(lq_file)

    if verbose:
        print("\n" + "-" * 30)
        print("  Scale Analysis Summary")
        print("-" * 30)
        print(f"Total HQ files found: {len(hq_files)}")
        print(f"Total LQ files found: {len(lq_files)}")
        print(f"Processed image pairs: {len(scales) + len(inconsistent_scales)}")

        if scales:
            scale_counts = Counter(scales)
            most_common_scale = scale_counts.most_common(1)[0]
            print(
                f"Most common consistent scale found: {most_common_scale[0]:.2f} (occurred {most_common_scale[1]} times)"
            )
            if len(scale_counts) > 1:
                print("Other consistent scales found:")
                for scale, count in scale_counts.most_common(
                    min(len(scale_counts) - 1, 5)
                )[
                    1:
                ]:  # Start from the second item
                    if (
                        count > 0
                    ):  # ensure we don't print if most_common was the only one
                        print(f"  - {scale:.2f} ({count} times)")
                if (
                    len(scale_counts) - 1 > 5
                ):  # Adjust for the already printed most common
                    print(
                        f"  ... and {len(scale_counts) - 1 - 5} more unique scales."
                    )  # -1 for most_common, -5 for printed
        else:
            print("No consistent scales found among processed pairs.")

        if inconsistent_scales:
            print(
                f"\nFiles with inconsistent width/height scales or processing errors: {len(inconsistent_scales)}"
            )
            for i, item in enumerate(inconsistent_scales[:5]):
                print(f"  - {item}")
            if len(inconsistent_scales) > 5:
                print(f"  ... and {len(inconsistent_scales) - 5} more files.")

        if missing_lq:
            print(
                f"\nFiles in HQ folder with no corresponding file in LQ folder: {len(missing_lq)}"
            )
            for item in missing_lq[:5]:
                print(f"  - {item}")
            if len(missing_lq) > 5:
                print(f"  ... and {len(missing_lq) - 5} more files.")

        if missing_hq:
            print(
                f"\nFiles in LQ folder with no corresponding file in HQ folder: {len(missing_hq)}"
            )
            for item in missing_hq[:5]:
                print(f"  - {item}")
            if len(missing_hq) > 5:
                print(f"  ... and {len(missing_hq) - 5} more files.")
        print("-" * 30)
        print("=" * 30)

    return {
        "total_hq_files": len(hq_files),
        "total_lq_files": len(lq_files),
        "processed_pairs": len(scales) + len(inconsistent_scales),
        "scales": scales,
        "inconsistent_scales": inconsistent_scales,
        "missing_lq": missing_lq,
        "missing_hq": missing_hq,
    }


# --- Function from hq_lq_scale.py ---
def test_hq_lq_scale(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("   Testing HQ/LQ Scale")
    print("=" * 30)

    while True:
        try:
            test_scale = float(input("Enter the scale to test (e.g., 2.0 for 2x): "))
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    hq_files = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )

    tolerance = 1e-9  # Small tolerance for floating point comparison

    matches = []
    mismatches = []  # Includes processing errors and division by zero
    missing_lq = []
    missing_hq = []

    print(f"Processing {len(hq_files)} HQ files and {len(lq_files)} LQ files...")

    for hq_file in tqdm(hq_files, desc="Testing Scale"):
        if hq_file in lq_files:
            hq_path = os.path.join(hq_folder, hq_file)
            lq_path = os.path.join(
                lq_folder, hq_file
            )  # Assuming same filename in LQ folder

            try:
                with Image.open(hq_path) as hq_img:
                    hq_width, hq_height = hq_img.size
                with Image.open(lq_path) as lq_img:
                    lq_width, lq_height = lq_img.size

                if lq_width == 0 or lq_height == 0:
                    mismatches.append(f"{hq_file}: Division by zero in LQ dimension")
                    continue

                width_scale = hq_width / lq_width
                height_scale = hq_height / lq_height

                if (
                    abs(width_scale - test_scale) < tolerance
                    and abs(height_scale - test_scale) < tolerance
                ):
                    matches.append(hq_file)
                else:
                    mismatches.append(
                        f"{hq_file}: Expected {test_scale:.2f}, Got Width {width_scale:.2f}, Height {height_scale:.2f}"
                    )

            except Exception as e:
                mismatches.append(f"Could not process file {hq_file}: {e}")
        else:
            missing_lq.append(hq_file)

    for lq_file in lq_files:
        if lq_file not in hq_files:
            missing_hq.append(lq_file)

    print("\n" + "-" * 30)
    print("  Scale Test Summary")
    print("-" * 30)
    print(f"Total HQ files found: {len(hq_files)}")
    print(f"Total LQ files found: {len(lq_files)}")
    print(f"Test Scale: {test_scale:.2f}")
    print(f"Files matching test scale: {len(matches)}")

    if mismatches:
        print(f"\nFiles not matching test scale or with errors: {len(mismatches)}")
        for i, item in enumerate(mismatches[: min(len(mismatches), 5)]):
            print(f"  - {item}")
        if len(mismatches) > 5:
            print(f"  ... and {len(mismatches) - 5} more files.")

    if missing_lq:
        print(
            f"\nFiles in HQ folder with no corresponding file in LQ folder: {len(missing_lq)}"
        )
        for item in missing_lq[: min(len(missing_lq), 5)]:
            print(f"  - {item}")
        if len(missing_lq) > 5:
            print(f"  ... and {len(missing_lq) - 5} more files.")

    if missing_hq:
        print(
            f"\nFiles in LQ folder with no corresponding file in HQ folder: {len(missing_hq)}"
        )
        for item in missing_hq[: min(len(missing_hq), 5)]:
            print(f"  - {item}")
        if len(missing_hq) > 5:
            print(f"  ... and {len(missing_hq) - 5} more files.")
    print("-" * 30)
    print("=" * 30)


# --- Function from check_image_consistency.py ---
def check_consistency(folder_path, folder_name, verbose=True):
    if verbose:
        print("\n" + "=" * 30)
        print(f"  Checking Consistency in {folder_name} Folder")
        print("=" * 30)

    files = sorted(
        [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
        ]
    )

    formats = defaultdict(list)
    modes = defaultdict(list)
    errors = []

    if verbose:
        print(f"Processing {len(files)} files...")

    for file in tqdm(files, desc=f"Checking {folder_name}", disable=not verbose):
        file_path = os.path.join(folder_path, file)
        try:
            with Image.open(file_path) as img:
                formats[img.format].append(file)
                modes[img.mode].append(file)
        except Exception as e:
            errors.append(f"{file}: {e}")

    if verbose:
        print(f"Total files found: {len(files)}")

        if formats:
            print("\nFile Format Distribution:")
            for fmt, file_list in formats.items():
                print(f"  - {fmt}: {len(file_list)} files")
            if len(formats) > 1:
                print("\nWarning: Multiple file formats found in this folder.")

        if modes:
            print("\nColor Mode Distribution:")
            for mode, file_list in modes.items():
                print(f"  - {mode}: {len(file_list)} files")
            if len(modes) > 1:
                print("\nWarning: Multiple color modes found in this folder.")

        if errors:
            print(f"\nFiles with processing errors: {len(errors)}")
            for i, error in enumerate(errors[: min(len(errors), 5)]):
                print(f"  - {error}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more files.")
        print("-" * 30)
        print("=" * 30)

    return {
        "total_files": len(files),
        "formats": formats,
        "modes": modes,
        "errors": errors,
    }


# --- Function from report_image_dimensions.py ---
def report_dimensions(folder_path, folder_name, verbose=True):
    if verbose:
        print("\n" + "=" * 30)
        print(f"  Reporting Dimensions for {folder_name} Folder")
        print("=" * 30)

    files = sorted(
        [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
        ]
    )

    dimensions = []
    errors = []

    if verbose:
        print(f"Processing {len(files)} files...")

    for file in tqdm(
        files, desc=f"Reporting Dimensions for {folder_name}", disable=not verbose
    ):
        file_path = os.path.join(folder_path, file)
        try:
            with Image.open(file_path) as img:
                dimensions.append(img.size)
        except Exception as e:
            errors.append(f"{file}: {e}")

    if verbose:
        print(f"Total files found: {len(files)}")
        print(f"Successfully processed images: {len(dimensions)}")

        if dimensions:
            widths = [dim[0] for dim in dimensions]
            heights = [dim[1] for dim in dimensions]

            min_width = min(widths)
            max_width = max(widths)
            avg_width = sum(widths) / len(widths)

            min_height = min(heights)
            max_height = max(heights)
            avg_height = sum(heights) / len(heights)

            print("\nDimension Statistics:")
            print(f"  - Width: Min={min_width}, Max={max_width}, Avg={avg_width:.2f}")
            print(
                f"  - Height: Min={min_height}, Max={max_height}, Avg={avg_height:.2f}"
            )

            unique_dimensions = sorted(list(set(dimensions)))
            if len(unique_dimensions) < 10 and len(unique_dimensions) > 0:
                print("\nUnique Dimensions Found:")
                for dim in unique_dimensions:
                    print(f"  - {dim[0]}x{dim[1]}")
            elif len(unique_dimensions) >= 10:
                print(
                    f"\nFound {len(unique_dimensions)} unique dimensions (listing first 5):"
                )
                for dim in unique_dimensions[:5]:
                    print(f"  - {dim[0]}x{dim[1]}")
                print(f"  ...")

        if errors:
            print(f"\nFiles with processing errors: {len(errors)}")
            for i, error in enumerate(errors[: min(len(errors), 5)]):
                print(f"  - {error}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more files.")
        print("-" * 30)
        print("=" * 30)

    return {
        "total_files": len(files),
        "successfully_processed": len(dimensions),
        "dimensions": dimensions,
        "errors": errors,
    }


# --- Function from report_extreme_dimensions.py ---
def find_extreme_dimensions(folder_path, folder_name, verbose=True):
    if verbose:
        print("\n" + "=" * 30)
        print(f"  Reporting Extreme Dimensions for {folder_name} Folder")
        print("=" * 30)

    files = sorted(
        [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
        ]
    )

    biggest_dim = (0, 0)
    biggest_files = []
    smallest_dim = (float("inf"), float("inf"))
    smallest_files = []
    processed_count = 0
    errors = []

    if verbose:
        print(f"Processing {len(files)} files...")

    for file in tqdm(
        files, desc=f"Finding Extreme Dimensions for {folder_name}", disable=not verbose
    ):
        file_path = os.path.join(folder_path, file)
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                processed_count += 1

                # Check for biggest dimension (consider total pixels)
                if width * height > biggest_dim[0] * biggest_dim[1]:
                    biggest_dim = (width, height)
                    biggest_files = [file]
                elif width * height == biggest_dim[0] * biggest_dim[1]:
                    # if (width, height) not in biggest_files: # This was wrong, should be file not dimension tuple
                    if file not in biggest_files:  # Store file name not dimension tuple
                        biggest_files.append(file)

                # Check for smallest dimension (consider total pixels)
                if width * height < smallest_dim[0] * smallest_dim[1]:
                    smallest_dim = (width, height)
                    smallest_files = [file]
                elif width * height == smallest_dim[0] * smallest_dim[1]:
                    # if (width, height) not in smallest_files: # This was wrong
                    if file not in smallest_files:  # Store file name
                        smallest_files.append(file)

        except Exception as e:
            errors.append(f"{file}: {e}")

    if verbose:
        print(f"Total files found: {len(files)}")
        print(f"Successfully processed images: {processed_count}")

        if processed_count > 0:
            print("\nExtreme Dimensions:")
            print(f"  - Biggest Dimension: {biggest_dim[0]}x{biggest_dim[1]}")
            if biggest_files:
                print(
                    f"    Files with this dimension: {', '.join(biggest_files[:5])}{'...' if len(biggest_files) > 5 else ''}"
                )
            print(f"  - Smallest Dimension: {smallest_dim[0]}x{smallest_dim[1]}")
            if smallest_files:
                print(
                    f"    Files with this dimension: {', '.join(smallest_files[:5])}{'...' if len(smallest_files) > 5 else ''}"
                )
        elif len(files) > 0:
            print("No images were successfully processed to determine dimensions.")

        if errors:
            print(f"\nFiles with processing errors: {len(errors)}")
            for i, error in enumerate(errors[: min(len(errors), 5)]):
                print(f"  - {error}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more files.")
        print("-" * 30)
        print("=" * 30)

    return {
        "total_files": len(files),
        "successfully_processed": processed_count,
        "biggest_dimension": biggest_dim,
        "biggest_files": biggest_files,
        "smallest_dimension": smallest_dim,
        "smallest_files": smallest_files,
        "errors": errors,
    }


# --- Function from remove_small_pairs.py ---
def is_small(img_path, min_size):
    try:
        with Image.open(img_path) as img:
            w, h = img.size
            return w < min_size or h < min_size
    except Exception as e:
        # print(f"Error reading {img_path}: {e}") # Avoid verbose error during check
        return True  # treat unreadable images as "too small"


def remove_small_image_pairs(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Removing Small Image Pairs")
    print("=" * 30)

    while True:
        try:
            min_size = int(input("Enter the minimum allowed dimension (e.g., 80): "))
            if min_size >= 0:
                break
            else:
                print("Please enter a non-negative integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    operation = get_file_operation_choice()
    destination = ""
    if operation == "move":
        destination = get_destination_path()
        if not destination:
            print("Operation aborted as no destination path was provided for move.")
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)
    elif operation == "copy":
        destination = get_destination_path()
        if not destination:
            print("Operation aborted as no destination path was provided for copy.")
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)

    removed_count = 0
    checked_count = 0
    errors = []

    lq_files = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    # Filter to only include pairs that exist in both folders
    hq_files_set = set(os.listdir(hq_folder))
    matching_files = [f for f in lq_files if f in hq_files_set and is_image_file(f)]

    print(f"Checking {len(matching_files)} HQ/LQ pairs...")

    for filename in tqdm(matching_files, desc="Processing Small Pairs"):
        lq_path = os.path.join(lq_folder, filename)
        hq_path = os.path.join(hq_folder, filename)

        # This check is redundant due to pre-filtering, but kept for safety.
        if not os.path.isfile(hq_path):
            # errors.append(f"Skipping {filename}: HQ pair not found.") # Should not happen with matching_files
            continue

        checked_count += 1

        lq_is_small = is_small(lq_path, min_size)
        hq_is_small = is_small(hq_path, min_size)

        if lq_is_small or hq_is_small:
            try:
                if operation == "inplace":
                    # For remove, inplace means direct deletion
                    os.remove(lq_path)
                    os.remove(hq_path)
                    # logging.info(f"Removed (inplace) small pair: {filename}")
                else:  # copy or move
                    hq_dest_folder = os.path.join(destination, "hq")
                    lq_dest_folder = os.path.join(destination, "lq")
                    hq_dest_path = os.path.join(
                        hq_dest_folder,
                        get_unique_filename(hq_dest_folder, filename),
                    )
                    lq_dest_path = os.path.join(
                        lq_dest_folder,
                        get_unique_filename(lq_dest_folder, filename),
                    )

                    if operation == "copy":
                        shutil.copy2(hq_path, hq_dest_path)
                        shutil.copy2(lq_path, lq_dest_path)
                        # logging.info(f"Copied small pair {filename} to {destination}")
                    elif operation == "move":
                        shutil.move(hq_path, hq_dest_path)
                        shutil.move(lq_path, lq_dest_path)
                        # logging.info(f"Moved small pair {filename} to {destination}")
                removed_count += 1
            except Exception as e:
                errors.append(f"Error {operation}ing {filename}: {e}")
                logging.error(f"Error {operation}ing small pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove Small Pairs Summary")
    print("-" * 30)
    print(f"Checked {checked_count} pairs.")
    print(
        f"Processed ({operation}ed) {removed_count} image pairs where either dimension was smaller than {min_size}."
    )
    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    print("-" * 30)
    print("=" * 30)


# --- Function from extract_val_random.py ---
def extract_random_pairs(input_hq_folder, input_lq_folder):
    print("\n" + "=" * 30)
    print("  Extracting Random Image Pairs")
    print("=" * 30)

    operation = get_file_operation_choice()

    output_base_dir = ""
    if operation != "inplace":
        output_base_dir = get_destination_path()
        if not output_base_dir:
            print(
                "Operation aborted as no destination path was provided for copy/move."
            )
            return

    while True:
        try:
            num_pairs_str = input(
                "Enter the number of random pairs to extract (default is 15 if left blank): "
            ).strip()
            num_pairs = int(num_pairs_str) if num_pairs_str else 15
            if num_pairs > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    hq_files = [
        f
        for f in os.listdir(input_hq_folder)
        if os.path.isfile(os.path.join(input_hq_folder, f)) and is_image_file(f)
    ]
    lq_files = [
        f
        for f in os.listdir(input_lq_folder)
        if os.path.isfile(os.path.join(input_lq_folder, f)) and is_image_file(f)
    ]

    available_pairs = [f for f in hq_files if f in lq_files]

    if len(available_pairs) < num_pairs:
        print(
            f"Warning: Only {len(available_pairs)} matching HQ/LQ pairs found, which is less than the requested {num_pairs} pairs. Extracting {len(available_pairs)} pairs instead."
        )
        num_pairs = len(available_pairs)

    if num_pairs == 0:
        print("No pairs to process. Exiting.")
        return

    selected_files = random.sample(available_pairs, num_pairs)

    if operation != "inplace":
        output_hq_dir = os.path.join(output_base_dir, "hq")
        output_lq_dir = os.path.join(output_base_dir, "lq")
        os.makedirs(output_hq_dir, exist_ok=True)
        os.makedirs(output_lq_dir, exist_ok=True)
        print(
            f"Processing {num_pairs} random pairs to {output_base_dir} using {operation}..."
        )
    else:
        print(
            f"Selected {num_pairs} random pairs. 'Inplace' operation means no files will be moved or copied."
        )

    processed_count = 0
    errors = []
    for filename in tqdm(selected_files, desc=f"{operation.capitalize()}ing Pairs"):
        hq_src_path = os.path.join(input_hq_folder, filename)
        lq_src_path = os.path.join(input_lq_folder, filename)

        try:
            if operation == "copy":
                hq_dest_path = os.path.join(
                    output_hq_dir, get_unique_filename(output_hq_dir, filename)
                )
                lq_dest_path = os.path.join(
                    output_lq_dir, get_unique_filename(output_lq_dir, filename)
                )
                shutil.copy2(hq_src_path, hq_dest_path)
                shutil.copy2(lq_src_path, lq_dest_path)
                processed_count += 1
            elif operation == "move":
                hq_dest_path = os.path.join(
                    output_hq_dir, get_unique_filename(output_hq_dir, filename)
                )
                lq_dest_path = os.path.join(
                    output_lq_dir, get_unique_filename(output_lq_dir, filename)
                )
                shutil.move(hq_src_path, hq_dest_path)
                shutil.move(lq_src_path, lq_dest_path)
                processed_count += 1
            elif operation == "inplace":
                # For extraction, "inplace" means no file operation, only selection.
                # The files are already "selected" in the `selected_files` list.
                # We count them as "processed" in terms of selection.
                processed_count += 1  # Count as selected
                continue
        except Exception as e:
            errors.append(f"Error {operation}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Extract Random Pairs Summary")
    print("-" * 30)
    print(f"Requested pairs for extraction: {num_pairs}")
    if operation != "inplace":
        print(f"Successfully {operation}d: {processed_count} pairs.")
    else:
        print(
            f"Successfully selected: {processed_count} pairs (no files moved/copied due to 'inplace')."
        )

    if errors:
        print(f"Errors encountered during file operations: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more issues.")
    if operation == "inplace":
        print(
            "Note: 'Inplace' operation for extraction means no files were moved or copied, only selected."
        )
    print("-" * 30)
    print("=" * 30)


# --- New Split/Adjust Functions ---


def split_dataset_in_half(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Splitting Dataset in Half")
    print("=" * 30)

    hq_files = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )

    # Find matching pairs
    matching_files = [f for f in hq_files if f in lq_files]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_pairs = len(matching_files)
    split_point = num_pairs // 2

    # Shuffle before splitting to ensure random distribution if desired,
    # or keep sorted if alphabetical split is intended.
    # For a true random half, shuffle:
    # random.shuffle(matching_files)

    first_half_files = matching_files[:split_point]
    second_half_files = matching_files[split_point:]

    print(
        f"Found {num_pairs} matching pairs. Splitting into {len(first_half_files)} for first half and {len(second_half_files)} for second half."
    )

    operation = get_file_operation_choice()

    output_base_dir = ""
    if operation != "inplace":
        output_base_dir = get_destination_path()  # Get base output path
        if not output_base_dir:
            print(
                "Operation aborted as no destination path was provided for copy/move."
            )
            return

        output_dir_1_hq = os.path.join(output_base_dir, "split_1", "hq")
        output_dir_1_lq = os.path.join(output_base_dir, "split_1", "lq")
        output_dir_2_hq = os.path.join(output_base_dir, "split_2", "hq")
        output_dir_2_lq = os.path.join(output_base_dir, "split_2", "lq")

        for d in [output_dir_1_hq, output_dir_1_lq, output_dir_2_hq, output_dir_2_lq]:
            os.makedirs(d, exist_ok=True)
    else:
        print(
            "Performing inplace split. This means no files will be moved or copied; the split is conceptual."
        )
        print("If you intended to move files, please choose 'copy' or 'move'.")

    # Process first half
    print(
        f"\nProcessing first half ({len(first_half_files)} pairs) using {operation}..."
    )
    processed_first_half = 0
    errors_first_half = []
    if operation != "inplace":
        for filename in tqdm(
            first_half_files, desc=f"{operation.capitalize()}ing First Half"
        ):
            hq_src = os.path.join(hq_folder, filename)
            lq_src = os.path.join(lq_folder, filename)

            try:
                hq_dest = os.path.join(
                    output_dir_1_hq, get_unique_filename(output_dir_1_hq, filename)
                )
                lq_dest = os.path.join(
                    output_dir_1_lq, get_unique_filename(output_dir_1_lq, filename)
                )
                if operation == "copy":
                    shutil.copy2(hq_src, hq_dest)
                    shutil.copy2(lq_src, lq_dest)
                elif operation == "move":
                    shutil.move(hq_src, hq_dest)
                    shutil.move(lq_src, lq_dest)
                processed_first_half += 1
            except Exception as e:
                errors_first_half.append(
                    f"Error {operation}ing pair {filename} to split_1: {e}"
                )
    else:  # Inplace, just count
        processed_first_half = len(first_half_files)

    # Process second half
    print(
        f"\nProcessing second half ({len(second_half_files)} pairs) using {operation}..."
    )
    processed_second_half = 0
    errors_second_half = []
    if operation != "inplace":
        for filename in tqdm(
            second_half_files, desc=f"{operation.capitalize()}ing Second Half"
        ):
            hq_src = os.path.join(hq_folder, filename)
            lq_src = os.path.join(lq_folder, filename)

            try:
                hq_dest = os.path.join(
                    output_dir_2_hq, get_unique_filename(output_dir_2_hq, filename)
                )
                lq_dest = os.path.join(
                    output_dir_2_lq, get_unique_filename(output_dir_2_lq, filename)
                )
                if operation == "copy":
                    shutil.copy2(hq_src, hq_dest)
                    shutil.copy2(lq_src, lq_dest)
                elif operation == "move":
                    # Important: If moving, source files for second half might have been moved
                    # if they were also part of the first_half_files source during the 'move' operation.
                    # This logic assumes source folders (hq_folder, lq_folder) are not modified by the first half's 'move'.
                    # If 'move' is from original, ensure files are still there.
                    # However, typical use of 'move' here is to move *from* original *to* new split folders.
                    if os.path.exists(hq_src) and os.path.exists(lq_src):
                        shutil.move(hq_src, hq_dest)
                        shutil.move(lq_src, lq_dest)
                    else:
                        errors_second_half.append(
                            f"Source file {filename} already moved or missing for second half."
                        )
                        continue  # Skip if source is gone
                processed_second_half += 1
            except Exception as e:
                errors_second_half.append(
                    f"Error {operation}ing pair {filename} to split_2: {e}"
                )
    else:  # Inplace, just count
        processed_second_half = len(second_half_files)

    print("\nSplit in half operation complete.")
    if operation == "inplace":
        print(
            f"Note: 'Inplace' operation for splitting means {processed_first_half} pairs identified for first half, {processed_second_half} for second. No files were moved or copied."
        )
    else:
        print(
            f"Total processed into first half: {processed_first_half}, into second half: {processed_second_half}"
        )
        if errors_first_half or errors_second_half:
            print("Errors encountered during split:")
            for e in errors_first_half:
                print(f"  - {e}")
            for e in errors_second_half:
                print(f"  - {e}")

    print("=" * 30)


def remove_pairs_by_count_percentage(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Remove Pairs by Count/Percentage")
    print("=" * 30)

    hq_files_list = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files_list = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_available = len(matching_files)
    print(f"Found {num_available} matching pairs.")

    while True:
        amount_str = input(
            f"Enter amount to remove (e.g., 100 or 10% of {num_available} pairs): "
        ).strip()
        num_to_remove = 0
        if amount_str.endswith("%"):
            try:
                percentage = float(amount_str[:-1])
                if 0 <= percentage <= 100:
                    num_to_remove = int(num_available * (percentage / 100))
                    break
                else:
                    print("Percentage must be between 0 and 100.")
            except ValueError:
                print("Invalid percentage format.")
        else:
            try:
                num = int(amount_str)
                if 0 <= num <= num_available:
                    num_to_remove = num
                    break
                else:
                    print(
                        f"Number of pairs to remove must be between 0 and {num_available}."
                    )
            except ValueError:
                print("Invalid number format.")

    if num_to_remove == 0:
        print("No pairs to remove. Exiting operation.")
        print("=" * 30)
        return

    print(f"Will identify {num_to_remove} pairs for removal.")

    operation = (
        get_file_operation_choice()
    )  # This will be "remove", "copy to remove", "move to remove"
    action_verb = "remove"
    if operation == "copy":
        action_verb = "copy (as removal)"
    if operation == "move":
        action_verb = "move (as removal)"

    destination = None
    dest_hq_folder = None
    dest_lq_folder = None

    if operation == "move" or operation == "copy":
        destination_prompt = (
            "Enter the destination directory path to move/copy the 'removed' pairs:"
        )
        destination = (
            get_destination_path(prompt=destination_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )  # a bit of a hack for older signature
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        dest_hq_folder = os.path.join(
            destination, "removed_hq" if operation == "move" else "copied_removed_hq"
        )
        dest_lq_folder = os.path.join(
            destination, "removed_lq" if operation == "move" else "copied_removed_lq"
        )
        os.makedirs(dest_hq_folder, exist_ok=True)
        os.makedirs(dest_lq_folder, exist_ok=True)
        print(f"Pairs designated for 'removal' will be {operation}d to {destination}")

    pairs_to_remove_names = random.sample(matching_files, num_to_remove)

    print(
        f"\nPerforming '{action_verb}' operation on {len(pairs_to_remove_names)} pairs..."
    )

    processed_count = 0
    errors = []

    for filename in tqdm(
        pairs_to_remove_names, desc=f"{action_verb.capitalize()}ing Pairs"
    ):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            if operation == "move":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.move(hq_path, hq_dest)
                shutil.move(lq_path, lq_dest)
            elif operation == "copy":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.copy2(hq_path, hq_dest)
                shutil.copy2(lq_path, lq_dest)
            elif operation == "inplace":  # This means actual deletion
                os.remove(hq_path)
                os.remove(lq_path)
            processed_count += 1
        except Exception as e:
            errors.append(f"Error {action_verb}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove by Count/Percentage Summary")
    print("-" * 30)
    print(f"Requested to {action_verb}: {num_to_remove} pairs.")
    print(f"Successfully {action_verb}d: {processed_count} pairs.")
    if operation == "inplace":
        print("  (Files were deleted from the source folders).")
    elif operation in ["copy", "move"]:
        print(f"  (Files were {operation}d to {destination}).")

    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    print("-" * 30)
    print("=" * 30)


def remove_pairs_by_size(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Remove Pairs by File Size")
    print("=" * 30)

    hq_files_list = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files_list = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_available = len(matching_files)
    print(f"Found {num_available} matching pairs.")

    while True:
        try:
            size_threshold_str = (
                input("Enter size threshold (e.g., 100KB, 2MB, 500B for bytes): ")
                .strip()
                .upper()
            )
            multiplier = 1
            if size_threshold_str.endswith("KB"):
                multiplier = 1024
                size_threshold_str = size_threshold_str[:-2]
            elif size_threshold_str.endswith("MB"):
                multiplier = 1024 * 1024
                size_threshold_str = size_threshold_str[:-2]
            elif size_threshold_str.endswith("B"):
                size_threshold_str = size_threshold_str[:-1]

            size_threshold = float(size_threshold_str) * multiplier
            if size_threshold >= 0:
                break
            else:
                print("Size threshold must be non-negative.")
        except ValueError:
            print(
                "Invalid input. Please enter a number, optionally followed by KB, MB, or B."
            )

    while True:
        criteria = (
            input(
                f"Remove pairs where EITHER image's size is (above/below) {size_threshold / multiplier:.2f}{('KB' if multiplier==1024 else ('MB' if multiplier==1024*1024 else 'B'))}? "
            )
            .strip()
            .lower()
        )
        if criteria in ["above", "below"]:
            break
        else:
            print("Invalid criteria. Please enter 'above' or 'below'.")

    operation = get_file_operation_choice()
    action_verb = "remove"
    if operation == "copy":
        action_verb = "copy (as removal)"
    if operation == "move":
        action_verb = "move (as removal)"

    destination = None
    dest_hq_folder = None
    dest_lq_folder = None

    if operation == "move" or operation == "copy":
        destination_prompt = (
            "Enter destination directory for pairs meeting size criteria:"
        )
        destination = (
            get_destination_path(prompt=destination_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        dest_hq_folder = os.path.join(destination, "size_criteria_hq")
        dest_lq_folder = os.path.join(destination, "size_criteria_lq")
        os.makedirs(dest_hq_folder, exist_ok=True)
        os.makedirs(dest_lq_folder, exist_ok=True)
        print(f"Pairs matching criteria will be {operation}d to {destination}")

    pairs_to_process_names = []
    skipped_due_error = []
    for filename in tqdm(matching_files, desc="Checking File Sizes"):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            hq_size = os.path.getsize(hq_path)
            lq_size = os.path.getsize(lq_path)
            process_pair = False
            if criteria == "above" and (
                hq_size > size_threshold or lq_size > size_threshold
            ):
                process_pair = True
            elif criteria == "below" and (
                hq_size < size_threshold or lq_size < size_threshold
            ):
                process_pair = True

            if process_pair:
                pairs_to_process_names.append(filename)
        except Exception as e:
            # print(f"Error getting size for pair {filename}: {e}")
            skipped_due_error.append(f"{filename}: {e}")

    if not pairs_to_process_names:
        print(
            f"No pairs found matching the criteria: size {criteria} {size_threshold / multiplier:.2f}{('KB' if multiplier==1024 else ('MB' if multiplier==1024*1024 else 'B'))}. Exiting."
        )
        if skipped_due_error:
            print(
                f"Skipped {len(skipped_due_error)} pairs due to errors during size check."
            )
        print("=" * 30)
        return

    print(
        f"\nWill {action_verb} {len(pairs_to_process_names)} pairs matching: size {criteria} {size_threshold / multiplier:.2f}{('KB' if multiplier==1024 else ('MB' if multiplier==1024*1024 else 'B'))}."
    )
    if skipped_due_error:
        print(
            f"Note: Skipped {len(skipped_due_error)} pairs due to errors during size check (e.g., file not found)."
        )

    processed_count = 0
    errors = []

    for filename in tqdm(
        pairs_to_process_names, desc=f"{action_verb.capitalize()}ing Pairs by Size"
    ):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            if operation == "move":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.move(hq_path, hq_dest)
                shutil.move(lq_path, lq_dest)
            elif operation == "copy":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.copy2(hq_path, hq_dest)
                shutil.copy2(lq_path, lq_dest)
            elif operation == "inplace":  # Actual deletion
                os.remove(hq_path)
                os.remove(lq_path)
            processed_count += 1
        except Exception as e:
            errors.append(f"Error {action_verb}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove by File Size Summary")
    print("-" * 30)
    print(
        f"Criteria: Size {criteria} {size_threshold / multiplier:.2f}{('KB' if multiplier==1024 else ('MB' if multiplier==1024*1024 else 'B'))}."
    )
    print(f"Successfully {action_verb}d: {processed_count} pairs.")
    if operation == "inplace":
        print("  (Files were deleted from the source folders).")
    elif operation in ["copy", "move"]:
        print(f"  (Files were {operation}d to {destination}).")

    if errors:
        print(f"Errors encountered during {action_verb} operation: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    if skipped_due_error:
        print(
            f"Pairs skipped due to read errors during initial check: {len(skipped_due_error)}"
        )
        for i, error in enumerate(skipped_due_error[: min(len(skipped_due_error), 2)]):
            print(f"  - {error}")
        if len(skipped_due_error) > 2:
            print(f"  ... and {len(skipped_due_error) - 2} more skipped.")
    print("-" * 30)
    print("=" * 30)


def remove_pairs_by_dimensions(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Remove Pairs by Dimensions")
    print("=" * 30)

    hq_files_list = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files_list = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_available = len(matching_files)
    print(f"Found {num_available} matching pairs.")

    while True:
        # Clarify if criteria applies to HQ, LQ, or BOTH images in a pair
        target_image = (
            input(
                "Apply dimension criteria to (hq/lq/both_must_match_criteria) images in a pair? "
            )
            .strip()
            .lower()
        )
        if target_image in ["hq", "lq", "both_must_match_criteria"]:
            break
        else:
            print(
                "Invalid input. Please enter 'hq', 'lq', or 'both_must_match_criteria'."
            )

    while True:
        dim_type = (
            input(
                "Filter by (width/height/area/any_dimension)? 'area' is width*height. 'any_dimension' checks width OR height. "
            )
            .strip()
            .lower()
        )
        if dim_type in ["width", "height", "area", "any_dimension"]:
            break
        else:
            print(
                "Invalid input. Please enter 'width', 'height', 'area', or 'any_dimension'."
            )

    min_val = -1.0  # Use float for area
    max_val = float("inf")

    while True:
        try:
            min_val_str = input(
                f"Enter MINIMUM {dim_type} (pixels/pixels^2 for area). Leave blank for no minimum: "
            ).strip()
            min_val = float(min_val_str) if min_val_str else -1.0
            if min_val != -1.0 and min_val < 0:
                print("Minimum value cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    while True:
        try:
            max_val_str = input(
                f"Enter MAXIMUM {dim_type} (pixels/pixels^2 for area). Leave blank for no maximum: "
            ).strip()
            max_val = float(max_val_str) if max_val_str else float("inf")
            if max_val != float("inf") and max_val < 0:  # max_val can be 0
                print("Maximum value cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    if min_val != -1.0 and max_val != float("inf") and min_val > max_val:
        print("Minimum value cannot be greater than maximum value. Aborting.")
        return

    # Ask if the user wants to remove pairs *within* this range or *outside* this range.
    while True:
        removal_logic = (
            input(
                f"Remove pairs with {dim_type} (within/outside) this range [{min_val if min_val != -1.0 else 'any'} - {max_val if max_val != float('inf') else 'any'}]? "
            )
            .strip()
            .lower()
        )
        if removal_logic in ["within", "outside"]:
            break
        else:
            print("Invalid choice. Please enter 'within' or 'outside'.")

    operation = get_file_operation_choice()
    action_verb = "remove"
    if operation == "copy":
        action_verb = "copy (as removal)"
    if operation == "move":
        action_verb = "move (as removal)"

    destination = None
    dest_hq_folder = None
    dest_lq_folder = None

    if operation == "move" or operation == "copy":
        destination_prompt = (
            "Enter destination directory for pairs matching dimension criteria:"
        )
        destination = (
            get_destination_path(prompt=destination_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        dest_hq_folder = os.path.join(destination, "dimension_criteria_hq")
        dest_lq_folder = os.path.join(destination, "dimension_criteria_lq")
        os.makedirs(dest_hq_folder, exist_ok=True)
        os.makedirs(dest_lq_folder, exist_ok=True)
        print(f"Pairs matching criteria will be {operation}d to {destination}")

    pairs_to_process_names = []
    skipped_due_error = []

    for filename in tqdm(matching_files, desc="Checking Dimensions"):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            with Image.open(hq_path) as hq_img, Image.open(lq_path) as lq_img:
                hq_w, hq_h = hq_img.size
                lq_w, lq_h = lq_img.size

                def check_dim(w, h, dim_type, min_v, max_v):
                    val_to_check = 0
                    if dim_type == "width":
                        val_to_check = w
                    elif dim_type == "height":
                        val_to_check = h
                    elif dim_type == "area":
                        val_to_check = w * h
                    elif dim_type == "any_dimension":
                        # For 'any_dimension', it's within range if EITHER width OR height is in range
                        in_range_w = (min_v == -1.0 or w >= min_v) and (
                            max_v == float("inf") or w <= max_v
                        )
                        in_range_h = (min_v == -1.0 or h >= min_v) and (
                            max_v == float("inf") or h <= max_v
                        )
                        return in_range_w or in_range_h

                    return (min_v == -1.0 or val_to_check >= min_v) and (
                        max_v == float("inf") or val_to_check <= max_v
                    )

                hq_matches_range = check_dim(hq_w, hq_h, dim_type, min_val, max_val)
                lq_matches_range = check_dim(lq_w, lq_h, dim_type, min_val, max_val)

                pair_is_within_range = False
                if target_image == "hq":
                    pair_is_within_range = hq_matches_range
                elif target_image == "lq":
                    pair_is_within_range = lq_matches_range
                elif (
                    target_image == "both_must_match_criteria"
                ):  # Both HQ and LQ images must individually satisfy the range
                    pair_is_within_range = hq_matches_range and lq_matches_range

                # Determine if the pair should be processed based on removal_logic
                process_pair = False
                if removal_logic == "within" and pair_is_within_range:
                    process_pair = True
                elif removal_logic == "outside" and not pair_is_within_range:
                    process_pair = True

                if process_pair:
                    pairs_to_process_names.append(filename)
        except Exception as e:
            # print(f"Error processing dimensions for pair {filename}: {e}")
            skipped_due_error.append(f"{filename}: {e}")

    if not pairs_to_process_names:
        print(f"No pairs found matching the dimension criteria. Exiting operation.")
        if skipped_due_error:
            print(
                f"Skipped {len(skipped_due_error)} pairs due to errors reading images."
            )
        print("=" * 30)
        return

    print(
        f"\nWill {action_verb} {len(pairs_to_process_names)} pairs. Criteria: Target '{target_image}', Dim '{dim_type}', Range [{min_val if min_val != -1.0 else 'any'}-{max_val if max_val != float('inf') else 'any'}], Logic '{removal_logic}'."
    )
    if skipped_due_error:
        print(
            f"Note: Skipped {len(skipped_due_error)} pairs due to errors reading image dimensions."
        )

    processed_count = 0
    errors = []

    for filename in tqdm(
        pairs_to_process_names, desc=f"{action_verb.capitalize()}ing Pairs by Dimension"
    ):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            if operation == "move":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.move(hq_path, hq_dest)
                shutil.move(lq_path, lq_dest)
            elif operation == "copy":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.copy2(hq_path, hq_dest)
                shutil.copy2(lq_path, lq_dest)
            elif operation == "inplace":  # Actual deletion
                os.remove(hq_path)
                os.remove(lq_path)
            processed_count += 1
        except Exception as e:
            errors.append(f"Error {action_verb}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove by Dimensions Summary")
    print("-" * 30)
    print(
        f"Criteria: Target '{target_image}', Dim '{dim_type}', Range [{min_val if min_val != -1.0 else 'any'} - {max_val if max_val != float('inf') else 'any'}], Logic '{removal_logic}'."
    )
    print(f"Successfully {action_verb}d: {processed_count} pairs.")
    if operation == "inplace":
        print("  (Files were deleted from the source folders).")
    elif operation in ["copy", "move"]:
        print(f"  (Files were {operation}d to {destination}).")

    if errors:
        print(f"Errors encountered during {action_verb} operation: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    if skipped_due_error:
        print(
            f"Pairs skipped due to read errors during initial check: {len(skipped_due_error)}"
        )
    print("-" * 30)
    print("=" * 30)


def remove_pairs_by_file_type(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print(" Remove Pairs by File Type")
    print("=" * 30)

    hq_files_list = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files_list = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_available = len(matching_files)
    print(f"Found {num_available} matching pairs.")

    print("\nSupported image types:")
    for i, img_type in enumerate(IMAGE_TYPES):
        print(f"  {i+1}. {img_type.lstrip('.')}")

    while True:
        file_type_input = (
            input("Enter file type to target for removal (e.g., 'png' or 'jpg'): ")
            .strip()
            .lower()
        )
        if not file_type_input.startswith("."):
            file_type_to_remove_normalized = "." + file_type_input
        else:
            file_type_to_remove_normalized = file_type_input

        if file_type_to_remove_normalized in IMAGE_TYPES:
            break
        else:
            print(
                f"Invalid file type '{file_type_input}'. Please enter a supported image type (e.g., png, jpg, webp)."
            )

    # Ask if we are removing pairs IF HQ is type, IF LQ is type, or IF BOTH are type.
    while True:
        target_choice = (
            input(
                f"Remove pair if (hq/lq/both/either) is of type '{file_type_to_remove_normalized}'? "
            )
            .strip()
            .lower()
        )
        if target_choice in ["hq", "lq", "both", "either"]:
            break
        else:
            print("Invalid choice. Please enter 'hq', 'lq', 'both', or 'either'.")

    operation = get_file_operation_choice()
    action_verb = "remove"
    if operation == "copy":
        action_verb = "copy (as removal)"
    if operation == "move":
        action_verb = "move (as removal)"

    destination = None
    dest_hq_folder = None
    dest_lq_folder = None

    if operation == "move" or operation == "copy":
        destination_prompt = f"Enter destination directory for pairs where {target_choice} is type '{file_type_to_remove_normalized}':"
        destination = (
            get_destination_path(prompt=destination_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        dest_hq_folder = os.path.join(destination, "filetype_criteria_hq")
        dest_lq_folder = os.path.join(destination, "filetype_criteria_lq")
        os.makedirs(dest_hq_folder, exist_ok=True)
        os.makedirs(dest_lq_folder, exist_ok=True)
        print(f"Pairs matching criteria will be {operation}d to {destination}")

    pairs_to_process_names = []
    for filename in matching_files:
        hq_is_target_type = filename.lower().endswith(file_type_to_remove_normalized)
        lq_is_target_type = filename.lower().endswith(
            file_type_to_remove_normalized
        )  # Assuming LQ has same name and thus same original type logic

        process_pair = False
        if target_choice == "hq" and hq_is_target_type:
            process_pair = True
        elif (
            target_choice == "lq" and lq_is_target_type
        ):  # This is often same as HQ due to naming
            process_pair = True
        elif target_choice == "both" and (hq_is_target_type and lq_is_target_type):
            process_pair = True
        elif target_choice == "either" and (hq_is_target_type or lq_is_target_type):
            process_pair = True

        if process_pair:
            pairs_to_process_names.append(filename)

    if not pairs_to_process_names:
        print(
            f"No pairs found matching criteria: {target_choice} is type '{file_type_to_remove_normalized}'. Exiting."
        )
        print("=" * 30)
        return

    print(
        f"\nWill {action_verb} {len(pairs_to_process_names)} pairs where {target_choice} is of type '{file_type_to_remove_normalized}'."
    )

    processed_count = 0
    errors = []

    for filename in tqdm(
        pairs_to_process_names, desc=f"{action_verb.capitalize()}ing Pairs by File Type"
    ):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            if operation == "move":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.move(hq_path, hq_dest)
                shutil.move(lq_path, lq_dest)
            elif operation == "copy":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.copy2(hq_path, hq_dest)
                shutil.copy2(lq_path, lq_dest)
            elif operation == "inplace":  # Actual deletion
                os.remove(hq_path)
                os.remove(lq_path)
            processed_count += 1
        except Exception as e:
            errors.append(f"Error {action_verb}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print(" Remove by File Type Summary")
    print("-" * 30)
    print(
        f"Criteria: {target_choice.capitalize()} image file type is '{file_type_to_remove_normalized}'."
    )
    print(f"Successfully {action_verb}d: {processed_count} pairs.")
    if operation == "inplace":
        print("  (Files were deleted from the source folders).")
    elif operation in ["copy", "move"]:
        print(f"  (Files were {operation}d to {destination}).")

    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    print("-" * 30)
    print("=" * 30)


# --- Functions from verify_images.py ---
def verify_images(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Verifying Image Integrity")
    print("=" * 30)

    all_files_to_check = []
    if hq_folder and os.path.isdir(hq_folder):
        for f in os.listdir(hq_folder):
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f):
                all_files_to_check.append((os.path.join(hq_folder, f), f"HQ/{f}"))
    else:
        print(
            f"Warning: HQ folder '{hq_folder}' not found or not a directory. Skipping HQ verification."
        )

    if lq_folder and os.path.isdir(lq_folder):
        for f in os.listdir(lq_folder):
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f):
                all_files_to_check.append((os.path.join(lq_folder, f), f"LQ/{f}"))
    else:
        print(
            f"Warning: LQ folder '{lq_folder}' not found or not a directory. Skipping LQ verification."
        )

    if not all_files_to_check:
        print("No image files found in the specified and accessible HQ/LQ folders.")
        print("=" * 30)
        return

    while True:
        depth_choice = (
            input("Perform in-depth check (slower but more thorough)? (y/n): ")
            .strip()
            .lower()
        )
        if depth_choice in ["y", "n"]:
            in_depth = depth_choice == "y"
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    corrupted_images_details = []  # Store path and display name
    print(f"Checking integrity of {len(all_files_to_check)} images...")

    # Use a ProcessPoolExecutor for CPU-bound tasks like image loading/verification
    # if Pillow's GIL release allows, otherwise ThreadPoolExecutor is fine for I/O bound parts.
    # Sticking to ThreadPoolExecutor as it's generally safer with libraries not explicitly releasing GIL.
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_details = {
            executor.submit(check_image_integrity, path, in_depth): (path, display_name)
            for path, display_name in all_files_to_check
        }
        for future in tqdm(
            concurrent.futures.as_completed(future_to_details),
            total=len(all_files_to_check),
            desc="Verifying Images",
        ):
            original_path, display_name = future_to_details[future]
            try:
                if not future.result():
                    corrupted_images_details.append(
                        {"path": original_path, "display_name": display_name}
                    )
            except Exception as exc:
                logging.error(
                    f"Image verification generated an exception for {display_name} ({original_path}): {exc}"
                )
                corrupted_images_details.append(
                    {
                        "path": original_path,
                        "display_name": f"{display_name} (Error during check: {exc})",
                    }
                )

    print("\n" + "-" * 30)
    print("  Image Integrity Verification Summary")
    print("-" * 30)
    print(f"Total images checked: {len(all_files_to_check)}")
    if corrupted_images_details:
        print(
            f"\nFound {len(corrupted_images_details)} corrupted, unreadable images, or images that caused errors during check:"
        )
        for i, img_detail in enumerate(
            corrupted_images_details[: min(len(corrupted_images_details), 10)]
        ):
            print(f"  - {img_detail['display_name']}")
        if len(corrupted_images_details) > 10:
            print(f"  ... and {len(corrupted_images_details) - 10} more.")
    else:
        print("\nNo corrupted or unreadable images found. All good!")
    print("-" * 30)
    print("=" * 30)

    # Offer to remove corrupted files
    if corrupted_images_details:
        while True:
            remove_choice_prompt = "Do you want to perform an operation (delete, move, copy) on these corrupted/problematic images? (y/n): "
            remove_choice = input(remove_choice_prompt).strip().lower()

            if remove_choice == "y":
                print("\nChoose operation for corrupted/problematic files:")
                print("  'inplace' = permanently delete from original location")
                print(
                    "  'move'    = move to a 'corrupted_files' subfolder in a new destination"
                )
                print(
                    "  'copy'    = copy to a 'corrupted_files' subfolder in a new destination"
                )
                operation = get_file_operation_choice()  # copy/move/inplace

                dest_corrupted_dir = ""
                if operation == "move" or operation == "copy":
                    dest_base = get_destination_path(
                        prompt="Enter destination directory for these files: "
                    )
                    if not dest_base:
                        print("Operation aborted as no destination path was provided.")
                        return  # Abort removal
                    dest_corrupted_dir = os.path.join(
                        dest_base, "corrupted_or_error_files"
                    )
                    os.makedirs(dest_corrupted_dir, exist_ok=True)
                    print(f"Files will be {operation}d to: {dest_corrupted_dir}")

                processed_count = 0
                op_errors = []
                action_verb = "deleted" if operation == "inplace" else operation + "ed"

                print(
                    f"\nAttempting to {action_verb} {len(corrupted_images_details)} files..."
                )
                for img_detail in tqdm(
                    corrupted_images_details,
                    desc=f"{operation.capitalize()}ing Problematic Files",
                ):
                    original_path = img_detail["path"]
                    base_filename = os.path.basename(original_path)

                    try:
                        if os.path.exists(original_path):  # Re-check existence
                            if operation == "inplace":
                                os.remove(original_path)
                            elif operation == "move":
                                dest_file_path = os.path.join(
                                    dest_corrupted_dir,
                                    get_unique_filename(
                                        dest_corrupted_dir, base_filename
                                    ),
                                )
                                shutil.move(original_path, dest_file_path)
                            elif operation == "copy":
                                dest_file_path = os.path.join(
                                    dest_corrupted_dir,
                                    get_unique_filename(
                                        dest_corrupted_dir, base_filename
                                    ),
                                )
                                shutil.copy2(original_path, dest_file_path)
                            processed_count += 1
                        else:
                            op_errors.append(
                                f"File {original_path} no longer exists. Skipped."
                            )
                    except Exception as e:
                        op_errors.append(f"Error {action_verb} {original_path}: {e}")

                print(f"\nSuccessfully {action_verb} {processed_count} files.")
                if op_errors:
                    print("Errors during file operation:")
                    for err_idx, err_msg in enumerate(op_errors[:5]):
                        print(f"  - {err_msg}")
                    if len(op_errors) > 5:
                        print(f"  ... and {len(op_errors) - 5} more errors.")
                break  # Exit y/n loop for removal
            elif remove_choice == "n":
                print("No action taken on corrupted/problematic files.")
                break  # Exit y/n loop
            else:
                print("Invalid input. Please enter 'y' or 'n'.")


# --- Improved Find Misaligned Images Function ---
def find_misaligned_images(hq_folder, lq_folder):
    # import logging # Already imported globally
    # import cv2 # Already imported globally
    # import numpy as np # Already imported globally
    # import concurrent.futures # Already imported globally
    # from PIL import Image # Already imported globally
    # import os # Already imported globally
    # import shutil # Already imported globally

    print("\n" + "=" * 30)
    print("  Finding Misaligned Image Pairs (Phase Correlation)")
    print("=" * 30)

    # Ask user for threshold
    while True:
        try:
            threshold = float(
                input(
                    "Enter alignment score threshold (default 0.1, lower is stricter, higher is more tolerant): "
                ).strip()
                or 0.1  # Default to 0.1 if empty
            )
            if threshold >= 0:
                break
            else:
                print("Threshold must be non-negative.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Ask user if they want to move/copy misaligned pairs or just report
    while True:
        action = (
            input("Action for misaligned pairs? (report/move/copy): ").strip().lower()
        )
        if action in ["report", "move", "copy"]:
            break
        else:
            print("Invalid choice. Please enter 'report', 'move', or 'copy'.")

    dest_folder_base = None
    dest_hq_misaligned = None
    dest_lq_misaligned = None
    dest_overlays_misaligned = None

    if action in ["move", "copy"]:
        dest_folder_base = get_destination_path(
            prompt="Enter base destination directory for misaligned pairs & overlays: "
        )
        if not dest_folder_base:
            print("Operation aborted as no destination path was provided.")
            return

        # Define subfolder names clearly
        misaligned_subfolder = "misaligned_pairs"
        hq_sub = "hq"
        lq_sub = "lq"
        overlays_sub = "overlays_for_misaligned"

        dest_hq_misaligned = os.path.join(
            dest_folder_base, misaligned_subfolder, hq_sub
        )
        dest_lq_misaligned = os.path.join(
            dest_folder_base, misaligned_subfolder, lq_sub
        )
        dest_overlays_misaligned = os.path.join(
            dest_folder_base, misaligned_subfolder, overlays_sub
        )

        os.makedirs(dest_hq_misaligned, exist_ok=True)
        os.makedirs(dest_lq_misaligned, exist_ok=True)
        os.makedirs(dest_overlays_misaligned, exist_ok=True)
        print(f"Misaligned HQ pairs will be {action}d to: {dest_hq_misaligned}")
        print(f"Misaligned LQ pairs will be {action}d to: {dest_lq_misaligned}")
        print(
            f"Visual overlays for misaligned pairs will be saved to: {dest_overlays_misaligned}"
        )

    # Set up logging to a file within the destination or source folder
    log_dir = dest_folder_base if dest_folder_base else (hq_folder or lq_folder or ".")
    log_file_path = os.path.join(log_dir, "misalignment_check.log")

    # Remove existing handlers to avoid duplicate logging if function is called multiple times
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure new handlers
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",  # More detailed format for file log
        handlers=[
            logging.FileHandler(log_file_path, mode="w"),  # Overwrite log file each run
            logging.StreamHandler(),  # Keep console output as is (controlled by print)
        ],
    )
    # For this function, we'll primarily use print for user feedback and specific logging.info for file log.
    # The global logging config might interfere if not managed carefully per function.
    # Re-establish basic console logging for this function if needed, or rely on print.
    # The above setup will make logging.info go to the file and console.

    # Gather all image pairs (supporting subfolders by using relpath)
    hq_files_map = {}  # rel_path -> abs_path
    for root, _, files in os.walk(hq_folder):
        for file in files:
            if is_image_file(file):
                rel_path = os.path.relpath(os.path.join(root, file), hq_folder)
                hq_files_map[rel_path] = os.path.join(root, file)

    lq_files_map = {}  # rel_path -> abs_path
    for root, _, files in os.walk(lq_folder):
        for file in files:
            if is_image_file(file):
                rel_path = os.path.relpath(os.path.join(root, file), lq_folder)
                lq_files_map[rel_path] = os.path.join(root, file)

    common_rel_paths = sorted(list(set(hq_files_map.keys()) & set(lq_files_map.keys())))

    print(
        f"Found {len(common_rel_paths)} common relative paths for HQ/LQ pairs to check."
    )
    if not common_rel_paths:
        print(
            "No common image pairs found based on relative paths. Ensure folder structures correspond."
        )
        logging.info("No common image pairs found.")
        print("=" * 30)
        return

    def load_image_gray_cv(image_path):
        try:
            # Read with OpenCV, which is generally faster for this type of processing
            cv_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if cv_img is None:
                # Try with PIL if OpenCV fails, as PIL might support more formats or handle corruption differently
                pil_img = Image.open(image_path).convert("L")
                cv_img = np.array(pil_img)

            if cv_img is None:  # If still None
                logging.error(
                    f"Failed to load image {image_path} with both OpenCV and PIL."
                )
                return None

            # Ensure uint8
            if cv_img.dtype != np.uint8:
                cv_img = cv2.normalize(cv_img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            return cv_img
        except Exception as e:
            logging.error(f"Exception loading image {image_path}: {e}")
            return None

    def compare_pair_phase_correlation(rel_path_tuple):
        # Expects tuple: (rel_path, abs_hq_path, abs_lq_path)
        rel_path, hq_abs_path, lq_abs_path = rel_path_tuple

        img1_gray = load_image_gray_cv(hq_abs_path)
        img2_gray = load_image_gray_cv(lq_abs_path)

        if img1_gray is None or img2_gray is None:
            return (rel_path, None, "error_loading_image")

        # Resize LQ to HQ size for comparison if different. Use area interpolation for downscaling.
        if img1_gray.shape != img2_gray.shape:
            h, w = img1_gray.shape
            try:
                interp_method = (
                    cv2.INTER_AREA
                    if (img2_gray.shape[0] > h or img2_gray.shape[1] > w)
                    else cv2.INTER_CUBIC
                )
                img2_gray_resized = cv2.resize(
                    img2_gray, (w, h), interpolation=interp_method
                )
            except cv2.error as e:
                logging.error(f"cv2.resize error for {lq_abs_path} to ({w},{h}): {e}")
                return (rel_path, None, "error_resizing_lq")
            img2_gray = img2_gray_resized

        img1_float = np.float32(img1_gray)
        img2_float = np.float32(img2_gray)

        if img1_float.size == 0 or img2_float.size == 0:
            logging.warning(f"Zero-size float image array for {rel_path}")
            return (rel_path, None, "error_zero_size_array")

        try:
            # Phase correlation returns (dx, dy), peak_response
            # We are interested in the shift (dx, dy)
            shift, _ = cv2.phaseCorrelate(img1_float, img2_float)
            # Calculate Euclidean distance of the shift vector from (0,0)
            # A larger score means a larger shift, hence more misalignment.
            alignment_score = np.linalg.norm(shift)
            return (rel_path, alignment_score, "ok")
        except cv2.error as cv2_e:  # Catch specific OpenCV errors
            logging.error(
                f"OpenCV error comparing {hq_abs_path} and {lq_abs_path}: {cv2_e}"
            )
            return (rel_path, None, f"error_phase_correlate_cv2: {cv2_e}")
        except Exception as e:  # Catch other errors
            logging.error(
                f"Generic error comparing {hq_abs_path} and {lq_abs_path}: {e}"
            )
            return (rel_path, None, f"error_phase_correlate_generic: {e}")

    misaligned_pairs_details = []  # Store (rel_path, score)
    aligned_pairs_details = []  # Store (rel_path, score)
    error_pairs_details = []  # Store (rel_path, status_message)

    # Prepare list of tuples for executor.map
    paths_to_compare = []
    for rp in common_rel_paths:
        paths_to_compare.append((rp, hq_files_map[rp], lq_files_map[rp]))

    # Using ThreadPoolExecutor as phaseCorrelate might not release GIL efficiently for true parallelism with threads.
    # For CPU-bound tasks like this, ProcessPoolExecutor is often better if GIL is an issue.
    # However, OpenCV functions can sometimes release GIL. Sticking with ThreadPool for now.
    # max_workers can be os.cpu_count()
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max(1, os.cpu_count() // 2 if os.cpu_count() else 1)
    ) as executor:

        # Using executor.map preserves order of common_rel_paths if needed later,
        # but tqdm won't show progress for map directly as easily as for as_completed.
        # Future objects are better for tqdm.
        future_to_relpath = {
            executor.submit(compare_pair_phase_correlation, path_tuple): path_tuple[0]
            for path_tuple in paths_to_compare
        }

        for future in tqdm(
            concurrent.futures.as_completed(future_to_relpath),
            total=len(paths_to_compare),
            desc="Comparing Image Pairs",
        ):
            rel_path_processed = future_to_relpath[future]
            try:
                _, score, status = future.result()
                if status == "ok":
                    if score is not None:  # Should always be not None if status is ok
                        if score > threshold:
                            misaligned_pairs_details.append(
                                {
                                    "rel_path": rel_path_processed,
                                    "score": score,
                                    "hq_path": hq_files_map[rel_path_processed],
                                    "lq_path": lq_files_map[rel_path_processed],
                                }
                            )
                        else:
                            aligned_pairs_details.append(
                                {"rel_path": rel_path_processed, "score": score}
                            )
                else:  # An error occurred
                    error_pairs_details.append(
                        {
                            "rel_path": rel_path_processed,
                            "status": status,
                            "hq_path": hq_files_map[rel_path_processed],
                            "lq_path": lq_files_map[rel_path_processed],
                        }
                    )
            except Exception as exc:
                logging.critical(
                    f"Critical error processing future for {rel_path_processed}: {exc}"
                )
                error_pairs_details.append(
                    {
                        "rel_path": rel_path_processed,
                        "status": f"exception_in_future_result: {exc}",
                        "hq_path": hq_files_map[rel_path_processed],
                        "lq_path": lq_files_map[rel_path_processed],
                    }
                )

    print("\n" + "-" * 30)
    print("  Misalignment Report (Phase Correlation)")
    print("-" * 30)
    logging.info("--- Misalignment Report (Phase Correlation) ---")

    total_checked = len(common_rel_paths)
    print(f"Total pairs checked: {total_checked}")
    logging.info(f"Total pairs checked: {total_checked}")

    num_aligned = len(aligned_pairs_details)
    print(f"Aligned pairs (score <= {threshold:.4f}): {num_aligned}")
    logging.info(f"Aligned pairs (score <= {threshold:.4f}): {num_aligned}")

    num_misaligned = len(misaligned_pairs_details)
    print(f"Misaligned pairs (score > {threshold:.4f}): {num_misaligned}")
    logging.info(f"Misaligned pairs (score > {threshold:.4f}): {num_misaligned}")

    num_errors = len(error_pairs_details)
    print(f"Pairs with errors during comparison: {num_errors}")
    logging.info(f"Pairs with errors during comparison: {num_errors}")

    if misaligned_pairs_details:
        print("\nTop Misaligned pairs (higher score = more misaligned):")
        logging.info("\nMisaligned pairs (rel_path, score, hq_abs_path, lq_abs_path):")
        # Sort by score descending
        sorted_misaligned = sorted(
            misaligned_pairs_details, key=lambda x: x["score"], reverse=True
        )
        for i, detail in enumerate(sorted_misaligned[:10]):  # Show top 10
            print(f"  - {detail['rel_path']} (Score: {detail['score']:.4f})")
            logging.info(
                f"  - MISALIGNED: {detail['rel_path']}, Score: {detail['score']:.4f}, HQ: {detail['hq_path']}, LQ: {detail['lq_path']}"
            )
        if num_misaligned > 10:
            print(f"  ... and {num_misaligned - 10} more misaligned pairs.")
            # Log all misaligned pairs if many
            if num_misaligned > 10:
                for i, detail in enumerate(sorted_misaligned[10:]):
                    logging.info(
                        f"  - MISALIGNED (cont.): {detail['rel_path']}, Score: {detail['score']:.4f}, HQ: {detail['hq_path']}, LQ: {detail['lq_path']}"
                    )
    else:
        print("\nNo misaligned pairs found exceeding the threshold.")
        logging.info("No misaligned pairs found exceeding the threshold.")

    if error_pairs_details:
        print("\nPairs with errors during comparison:")
        logging.warning(
            "\nPairs with errors during comparison (rel_path, status, hq_abs_path, lq_abs_path):"
        )
        for i, detail in enumerate(error_pairs_details[:5]):  # Show first 5
            print(f"  - {detail['rel_path']} (Status: {detail['status']})")
            logging.warning(
                f"  - ERROR: {detail['rel_path']}, Status: {detail['status']}, HQ: {detail['hq_path']}, LQ: {detail['lq_path']}"
            )
        if num_errors > 5:
            print(f"  ... and {num_errors - 5} more errors.")
            # Log all errors if many
            if num_errors > 5:
                for i, detail in enumerate(error_pairs_details[5:]):
                    logging.warning(
                        f"  - ERROR (cont.): {detail['rel_path']}, Status: {detail['status']}, HQ: {detail['hq_path']}, LQ: {detail['lq_path']}"
                    )

    # Optionally move/copy misaligned pairs and create overlays
    if action in ["move", "copy"] and misaligned_pairs_details:
        print(
            f"\nPerforming '{action}' operation for {num_misaligned} misaligned pairs..."
        )
        processed_op_count = 0
        op_errors = 0

        for detail in tqdm(
            misaligned_pairs_details, desc=f"{action.capitalize()}ing Misaligned Pairs"
        ):
            rel_path = detail["rel_path"]
            score = detail["score"]
            hq_src_abs = detail["hq_path"]
            lq_src_abs = detail["lq_path"]

            # Create unique filenames for destination, preserving relative path structure
            # The rel_path might contain subdirectories, e.g., "subdir/image.png"

            # Destination for HQ image
            hq_dest_abs = os.path.join(dest_hq_misaligned, rel_path)
            os.makedirs(
                os.path.dirname(hq_dest_abs), exist_ok=True
            )  # Ensure subdir exists
            hq_dest_abs = get_unique_filename(
                os.path.dirname(hq_dest_abs), os.path.basename(rel_path)
            )  # Get unique name in specific subdir
            hq_final_dest_path = os.path.join(
                os.path.dirname(os.path.join(dest_hq_misaligned, rel_path)), hq_dest_abs
            )

            # Destination for LQ image
            lq_dest_abs = os.path.join(dest_lq_misaligned, rel_path)
            os.makedirs(os.path.dirname(lq_dest_abs), exist_ok=True)
            lq_dest_abs = get_unique_filename(
                os.path.dirname(lq_dest_abs), os.path.basename(rel_path)
            )
            lq_final_dest_path = os.path.join(
                os.path.dirname(os.path.join(dest_lq_misaligned, rel_path)), lq_dest_abs
            )

            # Destination for Overlay image (use .jpg for overlay)
            overlay_filename_base = (
                os.path.splitext(os.path.basename(rel_path))[0]
                + f"_overlay_score{score:.2f}.jpg"
            )
            overlay_dest_abs = os.path.join(
                dest_overlays_misaligned,
                os.path.dirname(rel_path),
                overlay_filename_base,
            )  # Keep subdir for overlay too
            os.makedirs(os.path.dirname(overlay_dest_abs), exist_ok=True)
            # No need for get_unique_filename for overlay if score makes it unique enough, or just overwrite.
            # For safety, can use it:
            # overlay_dest_abs = get_unique_filename(os.path.dirname(overlay_dest_abs), os.path.basename(overlay_dest_abs))
            # overlay_final_dest_path = os.path.join(os.path.dirname(os.path.join(dest_overlays_misaligned, rel_path)), overlay_dest_abs)

            try:
                if action == "move":
                    if os.path.exists(hq_src_abs):
                        shutil.move(hq_src_abs, hq_final_dest_path)
                    if os.path.exists(lq_src_abs):
                        shutil.move(lq_src_abs, lq_final_dest_path)
                elif action == "copy":
                    if os.path.exists(hq_src_abs):
                        shutil.copy2(hq_src_abs, hq_final_dest_path)
                    if os.path.exists(lq_src_abs):
                        shutil.copy2(lq_src_abs, lq_final_dest_path)

                # Create and save overlay for visual inspection using the (potentially new) destination paths
                img1_color = cv2.imread(
                    hq_final_dest_path if action != "report" else hq_src_abs,
                    cv2.IMREAD_COLOR,
                )
                img2_color = cv2.imread(
                    lq_final_dest_path if action != "report" else lq_src_abs,
                    cv2.IMREAD_COLOR,
                )

                if img1_color is not None and img2_color is not None:
                    if img1_color.shape != img2_color.shape:
                        interp_method_ov = (
                            cv2.INTER_AREA
                            if (
                                img2_color.shape[0] > img1_color.shape[0]
                                or img2_color.shape[1] > img1_color.shape[1]
                            )
                            else cv2.INTER_CUBIC
                        )
                        img2_color_resized_ov = cv2.resize(
                            img2_color,
                            (img1_color.shape[1], img1_color.shape[0]),
                            interpolation=interp_method_ov,
                        )
                        img2_color = img2_color_resized_ov

                    overlay_img = cv2.addWeighted(img1_color, 0.5, img2_color, 0.5, 0)
                    cv2.imwrite(
                        overlay_dest_abs, overlay_img, [cv2.IMWRITE_JPEG_QUALITY, 90]
                    )
                    logging.info(
                        f"{action.capitalize()}d misaligned pair: {rel_path} (Score: {score:.4f}) to respective folders. Overlay at {overlay_dest_abs}"
                    )
                else:
                    logging.warning(
                        f"Could not read one or both images for overlay: HQ='{hq_final_dest_path}', LQ='{lq_final_dest_path}' for rel_path '{rel_path}'"
                    )

                processed_op_count += 1
            except Exception as e_op:
                op_errors += 1
                logging.error(
                    f"Error during {action} or overlay for pair {rel_path}: {e_op}"
                )

        print(f"\nFinished {action} operation: {processed_op_count} pairs processed.")
        if op_errors > 0:
            print(
                f"Encountered {op_errors} errors during file operations/overlay creation. Check log."
            )
        logging.info(
            f"Finished {action} operation: {processed_op_count} pairs processed. Errors: {op_errors}"
        )

    print("-" * 30)
    print("= " * 15)  # Visual separator
    print(f"Misalignment check log file: {log_file_path}")
    logging.info(f"--- Misalignment Check Complete ---")
    # Important: remove the file handler for this specific log so global logging isn't affected.
    for handler in logging.root.handlers[:]:
        if (
            isinstance(handler, logging.FileHandler)
            and handler.baseFilename == log_file_path
        ):
            handler.close()
            logging.root.removeHandler(handler)
    # Re-setup global basicConfig if it was cleared or if other functions rely on it
    # This is tricky. Better to use named loggers. For now, assume main script might re-init.
    # logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") # Restore global


# --- Functions from shuffle_images.py ---
def shuffle_image_pairs(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Shuffling Image Pairs (with Renaming)")
    print("=" * 30)

    hq_files_list = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files_list = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )

    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found to shuffle.")
        print("=" * 30)
        return

    print(f"Found {len(matching_files)} matching pairs to shuffle and rename.")

    operation = get_file_operation_choice()  # copy, move, inplace

    # For inplace, files are renamed in original folders.
    # For copy/move, files are copied/moved to new folders and then renamed within those new folders.

    output_hq_dir = hq_folder
    output_lq_dir = lq_folder

    if operation != "inplace":
        output_base_dir_prompt = (
            "Enter base destination directory for shuffled & renamed pairs: "
        )
        output_base_dir = (
            get_destination_path(prompt=output_base_dir_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )

        if not output_base_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return

        # Create subfolders like "shuffled_hq" and "shuffled_lq"
        # Or just "hq" and "lq" if the user intends the base_dir to be the new dataset root.
        # Let's assume user provides a new dataset root.
        output_hq_dir = os.path.join(output_base_dir, "hq")  # Standardized output
        output_lq_dir = os.path.join(output_base_dir, "lq")
        os.makedirs(output_hq_dir, exist_ok=True)
        os.makedirs(output_lq_dir, exist_ok=True)
        print(
            f"Shuffled pairs will be {operation}d and renamed in: {output_hq_dir} and {output_lq_dir}"
        )
    else:
        print("Shuffling and renaming files in-place within original folders.")

    # Create pairs: (original_filename, extension)
    # This ensures that if we shuffle, the extension is tied to the original file.
    original_pairs_info = []
    for fname in matching_files:
        original_pairs_info.append(
            {"original_name": fname, "ext": os.path.splitext(fname)[1]}
        )

    random.shuffle(original_pairs_info)  # Shuffle the list of dicts

    # Generate new sequential names (e.g., 00001.ext, 00002.ext)
    # The new name will use the original extension of the file it's being assigned to after shuffle.

    processed_count = 0
    errors = []

    # Temporary renaming for inplace shuffle to avoid collisions
    # (e.g. a.jpg -> 00001.jpg, b.jpg -> a.jpg - this would fail without temp)
    temp_suffix = "_shuffletemp_" + str(
        random.randint(10000, 99999)
    )  # Unique temp suffix

    # --- Stage 1: Copy or Move to destination (if not inplace), or rename to temp (if inplace) ---
    # This list will hold info about files in their (potentially new) locations before final renaming.
    files_in_final_location_for_renaming = []

    print(f"\nStage 1: Preparing files for shuffling ({operation})...")
    if operation == "inplace":
        # Rename to temporary names in source folders
        for idx, pair_info in enumerate(
            tqdm(original_pairs_info, desc="Renaming to Temp (Inplace)")
        ):
            orig_name = pair_info["original_name"]
            ext = pair_info["ext"]

            hq_src_path = os.path.join(hq_folder, orig_name)
            lq_src_path = os.path.join(lq_folder, orig_name)

            # Create a unique temporary name that's unlikely to already exist or be a target name
            temp_name_base = f"{idx:05d}{temp_suffix}"
            hq_temp_path = os.path.join(hq_folder, temp_name_base + ext)
            lq_temp_path = os.path.join(lq_folder, temp_name_base + ext)

            try:
                if os.path.exists(hq_src_path):
                    os.rename(hq_src_path, hq_temp_path)
                else:
                    errors.append(f"Inplace-Temp: HQ Source {hq_src_path} not found.")
                    continue
                if os.path.exists(lq_src_path):
                    os.rename(lq_src_path, lq_temp_path)
                else:  # Rollback HQ rename if LQ fails
                    os.rename(hq_temp_path, hq_src_path)
                    errors.append(
                        f"Inplace-Temp: LQ Source {lq_src_path} not found. HQ rename for {orig_name} rolled back."
                    )
                    continue

                files_in_final_location_for_renaming.append(
                    {
                        "current_hq_path": hq_temp_path,
                        "current_lq_path": lq_temp_path,
                        "original_ext": ext,  # This is the extension of the file that will eventually get this slot's new name.
                        # No, this should be the extension of THIS file.
                        # The `original_pairs_info` is shuffled.
                        # The new name (00001, 00002) will take *this* file's extension.
                    }
                )
            except Exception as e:
                errors.append(f"Error renaming {orig_name} to temporary: {e}")
    else:  # "copy" or "move"
        for pair_info in tqdm(
            original_pairs_info, desc=f"{operation.capitalize()}ing to Destination"
        ):
            orig_name = pair_info["original_name"]
            ext = pair_info["ext"]

            hq_src_path = os.path.join(hq_folder, orig_name)
            lq_src_path = os.path.join(lq_folder, orig_name)

            # Destination files will initially keep their original names in the new location
            # get_unique_filename is important if multiple source datasets could have same names.
            # Here, `orig_name` is already unique within its source, so unique check is for destination.

            # For shuffle, the crucial part is that the *pairing* based on original names is maintained
            # during copy/move, and *then* they are renamed according to the shuffle order.
            # The `original_pairs_info` is ALREADY shuffled.
            # So, `pair_info` is for the file that will end up at a certain position in the shuffle.

            # Let's re-think. `original_pairs_info` is a shuffled list of what *was* in the source.
            # We need to copy/move these files using their original names, then rename them
            # based on their new position in the `original_pairs_info` list.

            # No, the current `pair_info` from `original_pairs_info` (which is shuffled) IS the file
            # that should receive the (idx+1)th name.

            # If copying/moving, the file `orig_name` is processed. Its new name will be based on its
            # position in the shuffled list `original_pairs_info`.

            # Correct approach for copy/move:
            # Iterate 0 to N-1 for new names. `original_pairs_info[i]` is the original file that gets new name `i`.
            # This is what the original script was closer to for copy/move.

            # Let's stick to: `original_pairs_info` is shuffled. Iterate through it.
            # Each item `pair_info` represents an original file.
            # This file will be given a new name corresponding to its current index in the shuffled list.

            hq_dest_path_initial = os.path.join(
                output_hq_dir, get_unique_filename(output_hq_dir, orig_name)
            )
            lq_dest_path_initial = os.path.join(
                output_lq_dir, get_unique_filename(output_lq_dir, orig_name)
            )

            try:
                if operation == "copy":
                    if os.path.exists(hq_src_path):
                        shutil.copy2(hq_src_path, hq_dest_path_initial)
                    else:
                        errors.append(f"Copy: HQ Source {hq_src_path} not found.")
                        continue
                    if os.path.exists(lq_src_path):
                        shutil.copy2(lq_src_path, lq_dest_path_initial)
                    else:
                        errors.append(f"Copy: LQ Source {lq_src_path} not found.")
                        os.remove(hq_dest_path_initial)
                        continue  # Clean up copied HQ
                elif operation == "move":
                    if os.path.exists(hq_src_path):
                        shutil.move(hq_src_path, hq_dest_path_initial)
                    else:
                        errors.append(f"Move: HQ Source {hq_src_path} not found.")
                        continue
                    if os.path.exists(lq_src_path):
                        shutil.move(lq_src_path, lq_dest_path_initial)
                    else:  # This case is tricky for move, as HQ is already gone. Log error.
                        errors.append(
                            f"Move: LQ Source {lq_src_path} not found after HQ was moved. HQ is at {hq_dest_path_initial}."
                        )
                        continue

                files_in_final_location_for_renaming.append(
                    {
                        "current_hq_path": hq_dest_path_initial,  # Path in the *new* directory
                        "current_lq_path": lq_dest_path_initial,  # Path in the *new* directory
                        "original_ext": ext,  # The extension of this specific file.
                    }
                )
            except Exception as e:
                errors.append(
                    f"Error {operation}ing file {orig_name} to destination: {e}"
                )

    # --- Stage 2: Rename files (which are now in their final folders) to new sequential shuffled names ---
    print(f"\nStage 2: Renaming files to final shuffled order...")
    # `files_in_final_location_for_renaming` now contains paths to files that are
    # either temp-named (inplace) or copied/moved to destination with original-ish names.
    # The order of this list corresponds to the shuffled order.

    for idx, file_detail in enumerate(
        tqdm(files_in_final_location_for_renaming, desc="Final Renaming")
    ):
        # The new name is based on the index 'idx' in the shuffled list.
        # The extension comes from the file itself (which was stored in 'original_ext' or can be derived).
        current_hq_path = file_detail["current_hq_path"]
        current_lq_path = file_detail["current_lq_path"]
        # Get extension from current path, as original_ext might be from a different context if logic was mixed.
        # Safest is to get ext from current_hq_path (assuming hq/lq share it)
        ext_for_new_name = os.path.splitext(current_hq_path)[1]

        new_name_base = f"{idx+1:05d}"  # e.g., 00001, 00002
        final_hq_name = new_name_base + ext_for_new_name
        final_lq_name = new_name_base + ext_for_new_name

        # The directory for renaming is the directory of the current_path
        final_hq_path = os.path.join(os.path.dirname(current_hq_path), final_hq_name)
        final_lq_path = os.path.join(os.path.dirname(current_lq_path), final_lq_name)

        try:
            # Avoid renaming to itself if names collide due to prior unique naming, though unlikely with sequential.
            if current_hq_path != final_hq_path:
                # Ensure final path doesn't exist if we are not careful with get_unique_filename logic before.
                # However, for sequential renaming, this should be fine.
                if os.path.exists(final_hq_path):
                    errors.append(
                        f"Final Renaming: Target HQ path {final_hq_path} unexpectedly exists before rename."
                    )
                    continue
                os.rename(current_hq_path, final_hq_path)

            if current_lq_path != final_lq_path:
                if os.path.exists(final_lq_path):
                    errors.append(
                        f"Final Renaming: Target LQ path {final_lq_path} unexpectedly exists before rename."
                    )
                    os.rename(final_hq_path, current_hq_path)
                    continue  # Rollback HQ
                os.rename(current_lq_path, final_lq_path)

            processed_count += 1
        except Exception as e:
            errors.append(
                f"Error during final rename of '{os.path.basename(current_hq_path)}' to '{final_hq_name}': {e}"
            )

    # Cleanup: Remove original files if operation was 'move' and it was done in stages (not directly relevant here as move is to new name)
    # The current logic for 'move' already puts it in the final place with a temp/original name.

    print("\n" + "-" * 30)
    print("  Shuffle Image Pairs Summary")
    print("-" * 30)
    print(f"Total matching pairs considered: {len(matching_files)}")
    print(f"Successfully processed (shuffled & renamed): {processed_count} pairs.")
    if operation == "inplace":
        print(f"  Files were renamed in-place in {hq_folder} and {lq_folder}.")
    else:
        print(
            f"  Files were {operation}d and renamed in {output_hq_dir} and {output_lq_dir}."
        )

    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error_msg in enumerate(
            errors[: min(len(errors), 10)]
        ):  # Show more errors if many
            print(f"  - {error_msg}")
        if len(errors) > 10:
            print(
                f"  ... and {len(errors) - 10} more issues (check log if detailed logging was added)."
            )
    print("-" * 30)
    print("=" * 30)


# --- Functions from transform_dataset.py ---
def apply_transformation_to_image(
    image_path, transform_type, value, operation, dest_path=None, quality=95
):
    try:
        with Image.open(image_path) as img:
            original_format = img.format  # Preserve original format if possible
            output_img = None

            if transform_type == "brightness":
                enhancer = ImageEnhance.Brightness(img)
                output_img = enhancer.enhance(value)
            elif transform_type == "contrast":
                enhancer = ImageEnhance.Contrast(img)
                output_img = enhancer.enhance(value)
            elif transform_type == "saturation":  # PIL's Color is for saturation
                if (
                    img.mode == "L"
                ):  # Grayscale image, saturation has no effect or can cause error
                    output_img = img.copy()  # Keep as is
                    # logging.info(f"Saturation no-op for grayscale image: {image_path}")
                else:
                    enhancer = ImageEnhance.Color(img)
                    output_img = enhancer.enhance(value)
            elif transform_type == "sharpness":
                enhancer = ImageEnhance.Sharpness(img)
                output_img = enhancer.enhance(value)
            elif transform_type == "rotate":
                # Ensure expand=True for rotate to prevent cropping, fillcolor for background if needed
                output_img = img.rotate(
                    value, expand=True, fillcolor=None
                )  # None usually means black or white depending on mode
            elif transform_type == "flip_horizontal":
                output_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif transform_type == "flip_vertical":
                output_img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif transform_type == "grayscale":
                if img.mode != "L":  # Only convert if not already grayscale
                    output_img = img.convert("L")
                else:
                    output_img = img.copy()  # Already grayscale, just copy
            else:
                logging.error(
                    f"Unknown transform_type: {transform_type} for {image_path}"
                )
                return False

            if (
                output_img is None
            ):  # Should not happen if all branches assign output_img
                logging.error(
                    f"Output image is None after transform {transform_type} for {image_path}"
                )
                return False

            save_params = {}
            if original_format and original_format.upper() in ["JPEG", "JPG"]:
                save_params["quality"] = quality
                # save_params['subsampling'] = 0 # Optional: Keep original subsampling if known, 0 for best quality
                # save_params['icc_profile'] = img.info.get('icc_profile') # Preserve color profile

            if operation == "inplace":
                output_img.save(image_path, format=original_format, **save_params)
            elif operation in ["copy", "move"]:
                if dest_path is None:
                    logging.error(
                        f"Destination path is None for {operation} on {image_path}"
                    )
                    return False
                output_img.save(dest_path, format=original_format, **save_params)
                if operation == "move":
                    if os.path.exists(image_path):  # Ensure it exists before removing
                        os.remove(image_path)
            return True

    except UnidentifiedImageError:
        logging.error(
            f"UnidentifiedImageError: Cannot open or read image file {image_path}. It may be corrupted or not a supported format."
        )
        return False
    except IOError as ioe:
        logging.error(
            f"IOError processing image {image_path} for {transform_type}: {ioe}"
        )
        return False
    except Exception as e:
        logging.error(
            f"Unexpected error applying {transform_type} to {image_path}: {e}"
        )
        return False


def transform_dataset(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Transforming Dataset")
    print("=" * 30)

    BATCH_SIZE = 1000  # Process this many pairs at a time

    hq_files_list = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files_list = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found for transformation.")
        print("=" * 30)
        return

    # Get subset of pairs to process
    files_to_process = get_pairs_to_process(matching_files, operation_name="transform")
    if not files_to_process:
        print("=" * 30)
        return

    num_selected_for_transform = len(files_to_process)

    transform_options = {
        "1": "brightness",
        "2": "contrast",
        "3": "saturation",
        "4": "sharpness",
        "5": "rotate",
        "6": "flip_horizontal",
        "7": "flip_vertical",
        "8": "grayscale",
    }

    print("\nSelect a transformation:")
    for key, value in transform_options.items():
        print(f"  {key}. {value.replace('_', ' ').capitalize()}")

    while True:
        transform_choice = input("Enter the number of your choice: ").strip()
        if transform_choice in transform_options:
            selected_transform = transform_options[transform_choice]
            break
        else:
            print("Invalid choice. Please enter a valid number.")

    value = (
        None  # For transforms like flip/grayscale, value is not directly used from user
    )
    if selected_transform in ["brightness", "contrast", "saturation", "sharpness"]:
        while True:
            try:
                val_str = input(
                    f"Enter {selected_transform} factor (e.g., 0.5 for half, 1.0 for original, 1.5 for 50% more): "
                ).strip()
                value = float(val_str)
                if value >= 0:  # Allow 0 for some factors, e.g., brightness to black
                    break
                else:
                    print("Factor must be non-negative.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    elif selected_transform == "rotate":
        while True:
            try:
                val_str = input(
                    "Enter rotation angle in degrees (e.g., 90, -90, 180). Positive = counter-clockwise: "
                ).strip()
                value = float(val_str)  # Allow float angles
                break
            except ValueError:
                print("Invalid input. Please enter a number for angle.")

    operation = get_file_operation_choice()

    destination_hq_folder = ""
    destination_lq_folder = ""
    if operation != "inplace":
        output_base_dir_prompt = (
            f"Enter base destination directory for {operation}ed transformed pairs: "
        )
        output_base_dir = (
            get_destination_path(prompt=output_base_dir_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not output_base_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        # Sanitize transform name for folder
        sane_transform_name = selected_transform.replace("_", "-")
        destination_hq_folder = os.path.join(
            output_base_dir, f"transformed_{sane_transform_name}_hq"
        )
        destination_lq_folder = os.path.join(
            output_base_dir, f"transformed_{sane_transform_name}_lq"
        )
        os.makedirs(destination_hq_folder, exist_ok=True)
        os.makedirs(destination_lq_folder, exist_ok=True)
        print(
            f"Transformed pairs will be {operation}d to respective subfolders in {output_base_dir}"
        )
    else:
        print(
            f"Performing '{selected_transform}' transformation in-place on {num_selected_for_transform} selected pairs."
        )

    processed_count = 0
    errors = []

    print(
        f"\nApplying transformation ({selected_transform}) to {num_selected_for_transform} randomly selected and ordered pairs..."
    )

    # Batching loop
    for batch_start in range(0, len(files_to_process), BATCH_SIZE):
        batch = files_to_process[batch_start : batch_start + BATCH_SIZE]
        print(f"Processing batch {batch_start//BATCH_SIZE+1} ({len(batch)} pairs)...")
        for filename in tqdm(
            batch,
            desc=f"Transforming Pairs ({selected_transform}) [Batch {batch_start//BATCH_SIZE+1}]",
        ):
            hq_src_path = os.path.join(hq_folder, filename)
            lq_src_path = os.path.join(lq_folder, filename)

            hq_dest_path_for_apply = None
            lq_dest_path_for_apply = None

            if operation != "inplace":
                hq_dest_path_for_apply = os.path.join(
                    destination_hq_folder,
                    get_unique_filename(destination_hq_folder, filename),
                )
                lq_dest_path_for_apply = os.path.join(
                    destination_lq_folder,
                    get_unique_filename(destination_lq_folder, filename),
                )
            else:  # inplace
                hq_dest_path_for_apply = hq_src_path  # For inplace, apply_transformation saves to source path
                lq_dest_path_for_apply = lq_src_path

            hq_success = apply_transformation_to_image(
                hq_src_path,
                selected_transform,
                value,
                operation,
                hq_dest_path_for_apply,
            )
            lq_success = False  # Initialize
            if (
                hq_success or operation != "move"
            ):  # If HQ failed on move, LQ source might still be there to try
                # If HQ succeeded on move, LQ source is gone unless it's a different file (not a pair)
                # This logic assumes paired operations. If HQ move failed, LQ src is still there.
                # If HQ move succeeded, LQ src should also be moved from original.
                # For 'move', apply_transformation_to_image handles removal of src_path *after* saving to dest_path.
                # So, lq_src_path should still be original path.
                lq_success = apply_transformation_to_image(
                    lq_src_path,
                    selected_transform,
                    value,
                    operation,
                    lq_dest_path_for_apply,
                )

            if hq_success and lq_success:
                processed_count += 1
            else:
                # Construct more detailed error
                err_msg = f"Pair {filename}: "
                if not hq_success:
                    err_msg += f"HQ failed. "
                if not lq_success:
                    err_msg += f"LQ failed."
                errors.append(err_msg)
                logging.warning(
                    f"Failed to fully transform pair {filename}. HQ status: {hq_success}, LQ status: {lq_success}"
                )

    print("\n" + "-" * 30)
    print("  Transform Dataset Summary")
    print("-" * 30)
    print(
        f"Transformation: {selected_transform} (Value: {value if value is not None else 'N/A'})"
    )
    print(f"Operation: {operation.capitalize()}")
    print(f"Total matching pairs in source: {len(matching_files)}")
    print(f"Number of pairs selected for transformation: {num_selected_for_transform}")
    print(f"Successfully transformed: {processed_count} pairs.")
    if errors:
        print(f"Errors or partial failures encountered for {len(errors)} pairs:")
        for i, error_msg in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error_msg}")
        if len(errors) > 5:
            print(
                f"  ... and {len(errors) - 5} more issues (check console/log for details)."
            )
    print("-" * 30)
    print("=" * 30)


# --- Functions from dataset_color_adjustment.py ---
def adjust_image_color(
    image_path, adjustment_type, factor, operation, dest_path=None, quality=95
):
    # This function is very similar to apply_transformation_to_image,
    # could be merged or use a common core if PIL Enhance objects are handled generically.
    # For now, keeping separate as per original structure.
    try:
        if adjustment_type == "hue":
            # Use OpenCV for hue adjustment
            import cv2
            import numpy as np

            img_bgr = cv2.imread(image_path)
            if img_bgr is None:
                logging.error(f"Could not read image for hue adjustment: {image_path}")
                return False
            img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            # factor is now degrees (0-179)
            try:
                hue_shift = int(factor)
            except Exception:
                hue_shift = 0
            img_hsv[..., 0] = (img_hsv[..., 0].astype(int) + hue_shift) % 180
            img_bgr_shifted = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
            # Save result
            save_path = image_path if operation == "inplace" else dest_path
            if save_path is None:
                logging.error(
                    f"Destination path is None for hue adjustment on {image_path}"
                )
                return False
            # Use cv2.imwrite for BGR images
            result = cv2.imwrite(save_path, img_bgr_shifted)
            if not result:
                logging.error(f"cv2.imwrite failed for {save_path}")
                return False
            if (
                operation == "move"
                and os.path.exists(image_path)
                and save_path != image_path
            ):
                os.remove(image_path)
            return True
        # ... existing code ...
        with Image.open(image_path) as img:
            original_format = img.format
            output_img = None
            enhancer = None

            if adjustment_type == "brightness":
                enhancer = ImageEnhance.Brightness(img)
            elif adjustment_type == "contrast":
                enhancer = ImageEnhance.Contrast(img)
            elif adjustment_type == "color":  # This is saturation in PIL's terminology
                if img.mode == "L":  # Grayscale image
                    output_img = img.copy()  # No change
                else:
                    enhancer = ImageEnhance.Color(img)
            elif adjustment_type == "sharpness":
                enhancer = ImageEnhance.Sharpness(img)
            else:
                logging.error(
                    f"Unknown adjustment_type: {adjustment_type} for {image_path}"
                )
                return False

            if enhancer:  # If not grayscale 'color'
                output_img = enhancer.enhance(factor)
            elif output_img is None:  # Grayscale 'color' case, output_img was set
                logging.error(
                    f"Output image is None after adjustment {adjustment_type} for {image_path} - logic error."
                )
                return False

            save_params = {}
            if original_format and original_format.upper() in ["JPEG", "JPG"]:
                save_params["quality"] = quality
                # save_params['icc_profile'] = img.info.get('icc_profile')

            if operation == "inplace":
                output_img.save(image_path, format=original_format, **save_params)
            elif operation in ["copy", "move"]:
                if dest_path is None:
                    logging.error(
                        f"Destination path is None for {operation} on {image_path} (color adjust)"
                    )
                    return False
                output_img.save(dest_path, format=original_format, **save_params)
                if operation == "move":
                    if os.path.exists(image_path):
                        os.remove(image_path)
            return True

    except UnidentifiedImageError:
        logging.error(
            f"UnidentifiedImageError: Cannot open or read image file {image_path} for color adjustment."
        )
        return False
    except IOError as ioe:
        logging.error(
            f"IOError during color adjustment for {image_path} ({adjustment_type}): {ioe}"
        )
        return False
    except Exception as e:
        logging.error(
            f"Unexpected error adjusting {adjustment_type} for {image_path}: {e}"
        )
        return False


def dataset_colour_adjustment(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Dataset Color Adjustment")
    print("=" * 30)

    BATCH_SIZE = 1000  # Process this many pairs at a time

    hq_files_list = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files_list = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found for color adjustment.")
        print("=" * 30)
        return

    files_to_process = get_pairs_to_process(
        matching_files, operation_name="apply color adjustment to"
    )
    if not files_to_process:
        print("=" * 30)
        return
    num_selected_for_adjust = len(files_to_process)

    adjustment_options = {
        "1": "brightness",
        "2": "contrast",
        "3": "saturation",
        "4": "sharpness",
        "5": "grayscale",
        "6": "hue",
    }

    print("\nSelect an adjustment type:")
    for key, value in adjustment_options.items():
        print(f"  {key}. {value.capitalize()}")

    while True:
        adj_choice = input("Enter the number of your choice: ").strip()
        if adj_choice in adjustment_options:
            selected_adjustment = adjustment_options[adj_choice]
            break
        else:
            print("Invalid choice. Please enter a valid number.")

    # HUE: Accept degrees and allow random per-pair
    if selected_adjustment == "hue":
        while True:
            hue_input = (
                input(
                    "Enter hue shift in degrees (0-179), or 'random' for random shift per pair: "
                )
                .strip()
                .lower()
            )
            if hue_input == "random":
                hue_shift_value = "random"
                break
            try:
                hue_shift_value = int(hue_input)
                if 0 <= hue_shift_value <= 179:
                    break
                else:
                    print("Hue shift must be between 0 and 179.")
            except ValueError:
                print("Invalid input. Enter a number (0-179) or 'random'.")
    else:
        while True:
            try:
                factor_str = input(
                    f"Enter adjustment factor for {selected_adjustment} (e.g., 0.5 for less, 1.0 for original, 1.5 for 50% more): "
                ).strip()
                factor = float(factor_str)
                if factor >= 0:  # Allow 0, e.g. brightness to black
                    break
                else:
                    print("Factor must be non-negative.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    operation = get_file_operation_choice()

    destination_hq_folder = ""
    destination_lq_folder = ""
    if operation != "inplace":
        output_base_dir_prompt = (
            f"Enter base destination directory for {operation}ed color-adjusted pairs: "
        )
        output_base_dir = (
            get_destination_path(prompt=output_base_dir_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not output_base_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return

        sane_adjust_name = selected_adjustment.replace("_", "-")
        destination_hq_folder = os.path.join(
            output_base_dir, f"adjusted_{sane_adjust_name}_hq"
        )
        destination_lq_folder = os.path.join(
            output_base_dir, f"adjusted_{sane_adjust_name}_lq"
        )
        os.makedirs(destination_hq_folder, exist_ok=True)
        os.makedirs(destination_lq_folder, exist_ok=True)
        print(
            f"Adjusted pairs will be {operation}d to respective subfolders in {output_base_dir}"
        )
    else:
        print(
            f"Performing '{selected_adjustment}' adjustment in-place on {num_selected_for_adjust} selected pairs."
        )

    processed_count = 0
    errors = []

    print(
        f"\nApplying {selected_adjustment} adjustment to {num_selected_for_adjust} randomly selected and ordered pairs..."
    )

    # Batching loop
    for batch_start in range(0, len(files_to_process), BATCH_SIZE):
        batch = files_to_process[batch_start : batch_start + BATCH_SIZE]
        print(f"Processing batch {batch_start//BATCH_SIZE+1} ({len(batch)} pairs)...")
        for filename in tqdm(
            batch,
            desc=f"Adjusting Pairs ({selected_adjustment}) [Batch {batch_start//BATCH_SIZE+1}]",
        ):
            hq_src_path = os.path.join(hq_folder, filename)
            lq_src_path = os.path.join(lq_folder, filename)

            hq_dest_path_for_apply = None
            lq_dest_path_for_apply = None
            if operation != "inplace":
                hq_dest_path_for_apply = os.path.join(
                    destination_hq_folder,
                    get_unique_filename(destination_hq_folder, filename),
                )
                lq_dest_path_for_apply = os.path.join(
                    destination_lq_folder,
                    get_unique_filename(destination_lq_folder, filename),
                )
            else:
                hq_dest_path_for_apply = hq_src_path
                lq_dest_path_for_apply = lq_src_path

            # HUE: handle random per-pair and pass degrees
            if selected_adjustment == "hue":
                if hue_shift_value == "random":
                    hue_deg = random.randint(0, 179)
                else:
                    hue_deg = int(hue_shift_value)  # Ensure always int for both HQ/LQ
                hq_success = adjust_image_color(
                    hq_src_path,
                    selected_adjustment,
                    hue_deg,
                    operation,
                    hq_dest_path_for_apply,
                )
                lq_success = adjust_image_color(
                    lq_src_path,
                    selected_adjustment,
                    hue_deg,
                    operation,
                    lq_dest_path_for_apply,
                )
            else:
                hq_success = adjust_image_color(
                    hq_src_path,
                    selected_adjustment,
                    factor,
                    operation,
                    hq_dest_path_for_apply,
                )
                lq_success = False
                if hq_success or operation != "move":
                    lq_success = adjust_image_color(
                        lq_src_path,
                        selected_adjustment,
                        factor,
                        operation,
                        lq_dest_path_for_apply,
                    )

            if hq_success and lq_success:
                processed_count += 1
            else:
                err_msg = f"Pair {filename}: "
                if not hq_success:
                    err_msg += f"HQ failed adjustment. "
                if not lq_success:
                    err_msg += f"LQ failed adjustment."
                errors.append(err_msg)
                logging.warning(
                    f"Failed to fully adjust pair {filename}. HQ status: {hq_success}, LQ status: {lq_success}"
                )

    print("\n" + "-" * 30)
    print("  Dataset Color Adjustment Summary")
    print("-" * 30)
    if selected_adjustment == "hue":
        print(
            f"Adjustment Type: hue (Degrees: {'random per pair' if hue_shift_value == 'random' else hue_shift_value})"
        )
    else:
        print(f"Adjustment Type: {selected_adjustment} (Factor: {factor})")
    print(f"Operation: {operation.capitalize()}")
    print(f"Total matching pairs in source: {len(matching_files)}")
    print(f"Number of pairs selected for adjustment: {num_selected_for_adjust}")
    print(f"Successfully adjusted: {processed_count} pairs.")
    if errors:
        print(f"Errors or partial failures encountered for {len(errors)} pairs:")
        for i, error_msg in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error_msg}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more issues.")
    print("-" * 30)
    print("=" * 30)


# --- New Function: Grayscale Conversion ---
def grayscale_conversion(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Grayscale Conversion")
    print("=" * 30)

    hq_files_list = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files_list = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found for grayscale conversion.")
        print("=" * 30)
        return

    files_to_process = get_pairs_to_process(
        matching_files, operation_name="convert to grayscale"
    )
    if not files_to_process:
        print("=" * 30)
        return
    num_selected_for_grayscale = len(files_to_process)

    operation = get_file_operation_choice()

    destination_hq_folder = ""
    destination_lq_folder = ""
    if operation != "inplace":
        output_base_dir_prompt = (
            f"Enter base destination directory for {operation}ed grayscale pairs: "
        )
        output_base_dir = (
            get_destination_path(prompt=output_base_dir_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not output_base_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        destination_hq_folder = os.path.join(output_base_dir, "grayscale_hq")
        destination_lq_folder = os.path.join(output_base_dir, "grayscale_lq")
        os.makedirs(destination_hq_folder, exist_ok=True)
        os.makedirs(destination_lq_folder, exist_ok=True)
        print(
            f"Grayscale pairs will be {operation}d to respective subfolders in {output_base_dir}"
        )
    else:
        print(
            f"Performing grayscale conversion in-place on {num_selected_for_grayscale} selected pairs."
        )

    processed_count = 0
    errors = []

    print(
        f"\nConverting {num_selected_for_grayscale} randomly selected and ordered pairs to grayscale (Operation: {operation})..."
    )

    for filename in tqdm(files_to_process, desc="Converting to Grayscale"):
        hq_src_path = os.path.join(hq_folder, filename)
        lq_src_path = os.path.join(lq_folder, filename)

        hq_dest_path_for_apply = None
        lq_dest_path_for_apply = None
        if operation != "inplace":
            hq_dest_path_for_apply = os.path.join(
                destination_hq_folder,
                get_unique_filename(destination_hq_folder, filename),
            )
            lq_dest_path_for_apply = os.path.join(
                destination_lq_folder,
                get_unique_filename(destination_lq_folder, filename),
            )
        else:
            hq_dest_path_for_apply = hq_src_path
            lq_dest_path_for_apply = lq_src_path

        # "grayscale" is a transform type in apply_transformation_to_image, value is not used.
        hq_success = apply_transformation_to_image(
            hq_src_path, "grayscale", None, operation, hq_dest_path_for_apply
        )
        lq_success = False
        if hq_success or operation != "move":
            lq_success = apply_transformation_to_image(
                lq_src_path, "grayscale", None, operation, lq_dest_path_for_apply
            )

        if hq_success and lq_success:
            processed_count += 1
        else:
            err_msg = f"Pair {filename}: "
            if not hq_success:
                err_msg += f"HQ failed grayscale. "
            if not lq_success:
                err_msg += f"LQ failed grayscale."
            errors.append(err_msg)
            logging.warning(
                f"Failed to fully convert pair {filename} to grayscale. HQ: {hq_success}, LQ: {lq_success}"
            )

    print("\n" + "-" * 30)
    print("  Grayscale Conversion Summary")
    print("-" * 30)
    print(f"Operation: {operation.capitalize()}")
    print(f"Total matching pairs in source: {len(matching_files)}")
    print(
        f"Number of pairs selected for grayscale conversion: {num_selected_for_grayscale}"
    )
    print(f"Successfully converted to grayscale: {processed_count} pairs.")
    if errors:
        print(f"Errors or partial failures encountered for {len(errors)} pairs:")
        for i, error_msg in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error_msg}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more issues.")
    print("-" * 30)
    print("=" * 30)


# --- New Function: HQ/LQ Dataset Report ---
def generate_hq_lq_dataset_report(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("   HQ/LQ DATASET REPORT")
    print("=" * 30)

    print("\n--- Overall Dataset Information ---")
    try:
        hq_files_list = sorted(
            [
                f
                for f in os.listdir(hq_folder)
                if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
            ]
        )
        lq_files_list = sorted(
            [
                f
                for f in os.listdir(lq_folder)
                if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
            ]
        )
    except FileNotFoundError as fnf_e:
        print(f"Error: One of the dataset folders not found: {fnf_e}")
        print("Please ensure HQ and LQ folders are correctly set.")
        print("=" * 30)
        return

    matching_pairs_list = [
        f for f in hq_files_list if f in lq_files_list
    ]  # Ensure it's a list for len

    print(f"HQ Folder: {hq_folder}")
    print(f"LQ Folder: {lq_folder}")
    print(f"Total HQ Images (root): {len(hq_files_list)}")
    print(f"Total LQ Images (root): {len(lq_files_list)}")
    print(f"Matching HQ/LQ Pairs (based on root filenames): {len(matching_pairs_list)}")

    hq_unique_files = [f for f in hq_files_list if f not in lq_files_list]
    lq_unique_files = [f for f in lq_files_list if f not in hq_files_list]
    print(f"Images unique to HQ folder (root): {len(hq_unique_files)}")
    if hq_unique_files and len(hq_unique_files) <= 5:
        print(f"  ({', '.join(hq_unique_files)})")
    elif hq_unique_files:
        print(f"  (e.g., {', '.join(hq_unique_files[:3])} ...)")

    print(f"Images unique to LQ folder (root): {len(lq_unique_files)}")
    if lq_unique_files and len(lq_unique_files) <= 5:
        print(f"  ({', '.join(lq_unique_files)})")
    elif lq_unique_files:
        print(f"  (e.g., {', '.join(lq_unique_files[:3])} ...)")

    print("\n--- Scale Analysis (based on root filenames) ---")
    scale_results = find_hq_lq_scale(
        hq_folder, lq_folder, verbose=False
    )  # verbose=False for report summary
    if scale_results["scales"]:
        scale_counts = Counter(scale_results["scales"])
        most_common_scale = scale_counts.most_common(1)[0]
        print(
            f"Most common consistent scale: {most_common_scale[0]:.2f} (occurred {most_common_scale[1]} times out of {scale_results['processed_pairs']} pairs)"
        )
        other_scales = scale_counts.most_common()[1:6]  # Show up to 5 other scales
        if other_scales:
            print("Other consistent scales found:")
            for s, c in other_scales:
                print(f"  - {s:.2f} ({c} times)")
    else:
        print("No consistent scales found among processed pairs.")
    if scale_results["inconsistent_scales"]:
        print(
            f"Pairs with inconsistent width/height scales or processing errors: {len(scale_results['inconsistent_scales'])}"
        )
        # for item in scale_results['inconsistent_scales'][:2]: print(f"  - e.g., {item}")
    if scale_results["missing_lq"]:
        print(
            f"HQ files missing corresponding LQ file: {len(scale_results['missing_lq'])}"
        )
    if scale_results["missing_hq"]:
        print(
            f"LQ files missing corresponding HQ file: {len(scale_results['missing_hq'])}"
        )

    print("\n--- Consistency Check (HQ) ---")
    hq_consistency = check_consistency(hq_folder, "HQ", verbose=False)
    if hq_consistency["formats"]:
        print(
            f"HQ File Formats: { {k: len(v) for k, v in hq_consistency['formats'].items()} }"
        )
    else:
        print("HQ File Formats: No image files found or processed.")
    if hq_consistency["modes"]:
        print(
            f"HQ Color Modes: { {k: len(v) for k, v in hq_consistency['modes'].items()} }"
        )
    else:
        print("HQ Color Modes: No image files found or processed.")
    if hq_consistency["errors"]:
        print(f"HQ files with processing errors: {len(hq_consistency['errors'])}")

    print("\n--- Consistency Check (LQ) ---")
    lq_consistency = check_consistency(lq_folder, "LQ", verbose=False)
    if lq_consistency["formats"]:
        print(
            f"LQ File Formats: { {k: len(v) for k, v in lq_consistency['formats'].items()} }"
        )
    else:
        print("LQ File Formats: No image files found or processed.")
    if lq_consistency["modes"]:
        print(
            f"LQ Color Modes: { {k: len(v) for k, v in lq_consistency['modes'].items()} }"
        )
    else:
        print("LQ Color Modes: No image files found or processed.")
    if lq_consistency["errors"]:
        print(f"LQ files with processing errors: {len(lq_consistency['errors'])}")

    print("\n--- Dimension Report (HQ) ---")
    hq_dimensions_report = report_dimensions(
        hq_folder, "HQ", verbose=False
    )  # Corrected variable name
    if hq_dimensions_report["dimensions"]:  # Check if list is not empty
        hq_widths = [dim[0] for dim in hq_dimensions_report["dimensions"]]
        hq_heights = [dim[1] for dim in hq_dimensions_report["dimensions"]]
        print(
            f"HQ Width (processed {len(hq_widths)} images): Min={min(hq_widths)}, Max={max(hq_widths)}, Avg={sum(hq_widths)/len(hq_widths):.2f}"
        )
        print(
            f"HQ Height (processed {len(hq_heights)} images): Min={min(hq_heights)}, Max={max(hq_heights)}, Avg={sum(hq_heights)/len(hq_heights):.2f}"
        )
        unique_dims_hq = sorted(list(set(hq_dimensions_report["dimensions"])))
        print(
            f"HQ Unique Dimensions (WxH): {len(unique_dims_hq)}. Examples: {unique_dims_hq[:min(3, len(unique_dims_hq))]}"
        )

    else:
        print("HQ Dimensions: No images successfully processed for dimensions.")
    if hq_dimensions_report["errors"]:
        print(f"HQ dimension processing errors: {len(hq_dimensions_report['errors'])}")

    print("\n--- Dimension Report (LQ) ---")
    lq_dimensions_report = report_dimensions(
        lq_folder, "LQ", verbose=False
    )  # Corrected variable name
    if lq_dimensions_report["dimensions"]:  # Check if list is not empty
        lq_widths = [dim[0] for dim in lq_dimensions_report["dimensions"]]
        lq_heights = [dim[1] for dim in lq_dimensions_report["dimensions"]]
        print(
            f"LQ Width (processed {len(lq_widths)} images): Min={min(lq_widths)}, Max={max(lq_widths)}, Avg={sum(lq_widths)/len(lq_widths):.2f}"
        )
        print(
            f"LQ Height (processed {len(lq_heights)} images): Min={min(lq_heights)}, Max={max(lq_heights)}, Avg={sum(lq_heights)/len(lq_heights):.2f}"
        )
        unique_dims_lq = sorted(list(set(lq_dimensions_report["dimensions"])))
        print(
            f"LQ Unique Dimensions (WxH): {len(unique_dims_lq)}. Examples: {unique_dims_lq[:min(3, len(unique_dims_lq))]}"
        )

    else:
        print("LQ Dimensions: No images successfully processed for dimensions.")
    if lq_dimensions_report["errors"]:
        print(f"LQ dimension processing errors: {len(lq_dimensions_report['errors'])}")

    print("\n--- Extreme Dimensions (HQ) ---")
    hq_extreme_dims = find_extreme_dimensions(hq_folder, "HQ", verbose=False)
    if hq_extreme_dims["successfully_processed"] > 0:
        bd_hq = hq_extreme_dims["biggest_dimension"]
        sd_hq = hq_extreme_dims["smallest_dimension"]
        bf_hq = hq_extreme_dims["biggest_files"]
        sf_hq = hq_extreme_dims["smallest_files"]
        print(
            f"HQ Biggest Dimension (pixels): {bd_hq[0]}x{bd_hq[1]} (Area: {bd_hq[0]*bd_hq[1]})"
        )
        if bf_hq:
            print(f"  Files: {', '.join(bf_hq[:2])}{'...' if len(bf_hq) > 2 else ''}")
        print(
            f"HQ Smallest Dimension (pixels): {sd_hq[0]}x{sd_hq[1]} (Area: {sd_hq[0]*sd_hq[1]})"
        )
        if sf_hq:
            print(f"  Files: {', '.join(sf_hq[:2])}{'...' if len(sf_hq) > 2 else ''}")
    else:
        print("HQ Extreme Dimensions: No images successfully processed.")
    if hq_extreme_dims["errors"]:
        print(
            f"HQ extreme dimension processing errors: {len(hq_extreme_dims['errors'])}"
        )

    print("\n--- Extreme Dimensions (LQ) ---")
    lq_extreme_dims = find_extreme_dimensions(lq_folder, "LQ", verbose=False)
    if lq_extreme_dims["successfully_processed"] > 0:
        bd_lq = lq_extreme_dims["biggest_dimension"]
        sd_lq = lq_extreme_dims["smallest_dimension"]
        bf_lq = lq_extreme_dims["biggest_files"]
        sf_lq = lq_extreme_dims["smallest_files"]
        print(
            f"LQ Biggest Dimension (pixels): {bd_lq[0]}x{bd_lq[1]} (Area: {bd_lq[0]*bd_lq[1]})"
        )
        if bf_lq:
            print(f"  Files: {', '.join(bf_lq[:2])}{'...' if len(bf_lq) > 2 else ''}")
        print(
            f"LQ Smallest Dimension (pixels): {sd_lq[0]}x{sd_lq[1]} (Area: {sd_lq[0]*sd_lq[1]})"
        )
        if sf_lq:
            print(f"  Files: {', '.join(sf_lq[:2])}{'...' if len(sf_lq) > 2 else ''}")
    else:
        print("LQ Extreme Dimensions: No images successfully processed.")
    if lq_extreme_dims["errors"]:
        print(
            f"LQ extreme dimension processing errors: {len(lq_extreme_dims['errors'])}"
        )

    print("\n" + "=" * 30)
    print("   REPORT COMPLETE")
    print("=" * 30)


# --- Other existing functions from combine_folders.py etc. that need modification ---
# Will add these in the final script, ensuring they use the new operation choices.


    def combine_datasets():
        print("\n" + "=" * 30)
        print("  Combine Multiple Datasets (Pairwise HQ/LQ)")
        print("=" * 30)

        sources = []
        print(
            "Enter paths to SOURCE dataset ROOTS. Each root must contain 'hq' and 'lq' subfolders."
        )
        print(
            "These 'hq' and 'lq' subfolders will be combined into a NEW destination's 'hq' and 'lq'."
        )
        print("Enter a blank path when you are finished adding sources.")

        while True:
            src_root_path = input(
                f"Source dataset root #{len(sources) + 1} (or blank to finish): "
            ).strip()
            if not src_root_path:
                if not sources:  # No sources added yet
                    print("No sources added. Aborting combine operation.")
                    return
                break  # Finished adding sources

            if not os.path.isdir(src_root_path):
                print(
                    f"  Error: '{src_root_path}' is not a valid directory. Please try again."
                )
                continue

            src_hq_path = os.path.join(src_root_path, "hq")
            src_lq_path = os.path.join(src_root_path, "lq")

            if not (os.path.isdir(src_hq_path) and os.path.isdir(src_lq_path)):
                print(
                    f"  Error: '{src_root_path}' must contain both 'hq' and 'lq' subfolders."
                )
                print(f"    Checked for: '{src_hq_path}' and '{src_lq_path}'")
                continue

            sources.append({"root": src_root_path, "hq": src_hq_path, "lq": src_lq_path})
            print(f"  Added source: {src_root_path}")

        if not sources:  # Should be caught earlier, but as a safeguard
            print("No valid sources provided. Aborting combine operation.")
            return

        # Get operation: copy or move
        while True:
            operation = input("Operation for combining files (copy/move): ").strip().lower()
            if operation in ["copy", "move"]:
                break
            print("Invalid operation. Please enter 'copy' or 'move'.")

        # Get destination root for the NEW combined dataset
        dest_root_prompt = "Enter path for the NEW combined dataset root directory: "
        dest_root = (
            get_destination_path(prompt=dest_root_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )

        if not dest_root:  # User left it blank or path creation failed
            print("No valid destination root provided. Aborting combine operation.")
            return

        # Create 'hq' and 'lq' subfolders in the destination root
        dest_combined_hq = os.path.join(dest_root, "hq")
        dest_combined_lq = os.path.join(dest_root, "lq")
        try:
            os.makedirs(dest_combined_hq, exist_ok=True)
            os.makedirs(dest_combined_lq, exist_ok=True)
        except OSError as e:
            print(f"Error creating destination subfolders in '{dest_root}': {e}")
            return

        print(f"Combined HQ files will go to: {dest_combined_hq}")
        print(f"Combined LQ files will go to: {dest_combined_lq}")

        total_pairs_processed = 0
        total_errors = 0

        print(
            f"\nStarting to {operation} files from {len(sources)} sources to {dest_root}..."
        )

        for src_info in sources:
            src_name = os.path.basename(src_info["root"])  # For progress bar
            print(f"\nProcessing source: {src_info['root']} ({src_name})")

            try:
                src_hq_files = set(
                    f
                    for f in os.listdir(src_info["hq"])
                    if os.path.isfile(os.path.join(src_info["hq"], f)) and is_image_file(f)
                )
                src_lq_files = set(
                    f
                    for f in os.listdir(src_info["lq"])
                    if os.path.isfile(os.path.join(src_info["lq"], f)) and is_image_file(f)
                )
            except FileNotFoundError:
                print(
                    f"  Error: Could not list files in hq/lq for source {src_info['root']}. Skipping this source."
                )
                total_errors += 1  # Count as a major error for the source
                continue

            common_files_in_src = sorted(list(src_hq_files & src_lq_files))

            if not common_files_in_src:
                print(
                    f"  No common HQ/LQ image pairs found in {src_info['root']}. Skipping."
                )
                continue

            print(
                f"  Found {len(common_files_in_src)} HQ/LQ pairs to {operation} from this source."
            )

            current_source_errors = 0
            for fname in tqdm(
                common_files_in_src, desc=f"{operation.capitalize()}ing from '{src_name}'"
            ):
                src_hq_filepath = os.path.join(src_info["hq"], fname)
                src_lq_filepath = os.path.join(src_info["lq"], fname)

                # Get unique filename for destination to avoid overwrites from different sources
                # or if a file with same name already exists in dest_combined_hq/lq
                unique_dest_fname_hq = get_unique_filename(dest_combined_hq, fname)
                unique_dest_fname_lq = get_unique_filename(
                    dest_combined_lq, fname
                )  # LQ should also be unique, usually same as HQ's unique

                dest_hq_filepath = os.path.join(dest_combined_hq, unique_dest_fname_hq)
                dest_lq_filepath = os.path.join(
                    dest_combined_lq, unique_dest_fname_lq
                )  # Use unique LQ name for LQ path

                try:
                    if operation == "copy":
                        shutil.copy2(src_hq_filepath, dest_hq_filepath)
                        shutil.copy2(src_lq_filepath, dest_lq_filepath)
                    elif operation == "move":
                        shutil.move(src_hq_filepath, dest_hq_filepath)
                        shutil.move(src_lq_filepath, dest_lq_filepath)
                    total_pairs_processed += 1
                except Exception as e_file_op:
                    logging.error(
                        f"Error {operation}ing pair '{fname}' from '{src_info['root']}': {e_file_op}"
                    )
                    current_source_errors += 1
                    total_errors += 1

            if current_source_errors > 0:
                print(
                    f"  Encountered {current_source_errors} errors while processing files from {src_info['root']}."
                )

        print("\n" + "-" * 30)
        print(f"  Combine Datasets Summary")
        print("-" * 30)
        print(f"Total source locations processed: {len(sources)}")
        print(f"Total HQ/LQ pairs successfully {operation}d: {total_pairs_processed}")
        print(f"Total errors during file operations: {total_errors}")
        if total_errors > 0:
            print("  Please check the console output or log for details on errors.")
        print(f"Combined dataset is located in: {dest_root}")
        print("-" * 30)
        print("=" * 30)


def split_adjust_dataset(hq_folder, lq_folder):
    print("\nSplit/Adjust Dataset Options:")
    print(
        "  1. Split dataset in half (moves/copies to subfolders 'split_1', 'split_2')"
    )
    print(
        "  2. Remove pairs by count or percentage (deletes or moves/copies to 'removed')"
    )
    print("  3. Remove pairs by file size (deletes or moves/copies to 'size_criteria')")
    print(
        "  4. Remove pairs by dimensions (deletes or moves/copies to 'dimension_criteria')"
    )
    print(
        "  5. Remove pairs by file type (deletes or moves/copies to 'filetype_criteria')"
    )
    print("  6. Back to main menu")

    while True:
        choice = input("Enter your choice for Split/Adjust: ").strip()
        if choice == "1":
            split_dataset_in_half(hq_folder, lq_folder)
        elif choice == "2":
            remove_pairs_by_count_percentage(hq_folder, lq_folder)
        elif choice == "3":
            remove_pairs_by_size(hq_folder, lq_folder)
        elif choice == "4":
            remove_pairs_by_dimensions(hq_folder, lq_folder)
        elif choice == "5":
            remove_pairs_by_file_type(hq_folder, lq_folder)
        elif choice == "6":
            break
        else:
            print("Invalid choice for Split/Adjust. Please try again.")
        # After an operation, re-display split/adjust menu or break to main?
        # Current: re-displays split/adjust menu. User must select 6 to go back.


def find_alpha_channels(hq_folder, lq_folder):
    """Find images with alpha channels in HQ/LQ folders."""
    print("\n" + "=" * 30)
    print("  Finding Images with Alpha Channels")
    print("=" * 30)

    def check_alpha_in_folder(folder_path, folder_name):
        images_with_alpha = []
        errors = []

        image_files = [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
        ]

        for filename in tqdm(image_files, desc=f"Checking {folder_name}"):
            file_path = os.path.join(folder_path, filename)
            try:
                with Image.open(file_path) as img:
                    if img.mode in ("RGBA", "LA") or (
                        img.mode == "P" and "transparency" in img.info
                    ):
                        images_with_alpha.append(filename)
            except Exception as e:
                errors.append((filename, str(e)))

        return images_with_alpha, errors

    hq_alpha_images, hq_errors = check_alpha_in_folder(hq_folder, "HQ")
    lq_alpha_images, lq_errors = check_alpha_in_folder(lq_folder, "LQ")

    print("\n" + "-" * 30)
    print("  Alpha Channel Analysis Summary")
    print("-" * 30)

    print(f"\nHQ Folder Results:")
    print(f"Found {len(hq_alpha_images)} images with alpha channels")
    if hq_alpha_images:
        print("\nExample HQ files with alpha:")
        for f in hq_alpha_images[:5]:
            print(f"  - {f}")
        if len(hq_alpha_images) > 5:
            print(f"  ... and {len(hq_alpha_images) - 5} more")

    print(f"\nLQ Folder Results:")
    print(f"Found {len(lq_alpha_images)} images with alpha channels")
    if lq_alpha_images:
        print("\nExample LQ files with alpha:")
        for f in lq_alpha_images[:5]:
            print(f"  - {f}")
        if len(lq_alpha_images) > 5:
            print(f"  ... and {len(lq_alpha_images) - 5} more")

    if hq_errors or lq_errors:
        print("\nErrors encountered:")
        for filename, error in (hq_errors + lq_errors)[:5]:
            print(f"  - {filename}: {error}")
        if len(hq_errors) + len(lq_errors) > 5:
            print(f"  ... and {len(hq_errors) + len(lq_errors) - 5} more errors")

    print("-" * 30)
    print("=" * 30)

    return {
        "hq_alpha": hq_alpha_images,
        "lq_alpha": lq_alpha_images,
        "hq_errors": hq_errors,
        "lq_errors": lq_errors,
    }


class LayerNorm(torch.nn.Module):
    def __init__(self, normalized_shape, eps=1e-6, data_format="channels_last"):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.ones(normalized_shape))
        self.bias = torch.nn.Parameter(torch.zeros(normalized_shape))
        self.eps = eps
        self.data_format = data_format
        if self.data_format not in ["channels_last", "channels_first"]:
            raise NotImplementedError
        self.normalized_shape = (normalized_shape,)

    def forward(self, x):
        if self.data_format == "channels_last":
            return torch.nn.functional.layer_norm(
                x, self.normalized_shape, self.weight, self.bias, self.eps
            )
        elif self.data_format == "channels_first":
            u = x.mean(1, keepdim=True)
            s = (x - u).pow(2).mean(1, keepdim=True)
            x = (x - u) / torch.sqrt(s + self.eps)
            x = self.weight[:, None, None] * x + self.bias[:, None, None]
            return x


def remove_alpha_channels(hq_folder, lq_folder):
    """Remove alpha channels from images in HQ/LQ folders."""
    print("\n" + "=" * 30)
    print("  Removing Alpha Channels")
    print("=" * 30)

    alpha_results = find_alpha_channels(hq_folder, lq_folder)
    if not (alpha_results["hq_alpha"] or alpha_results["lq_alpha"]):
        print("\nNo images with alpha channels found to process.")
        return

    operation = get_file_operation_choice()
    destination = ""
    if operation != "inplace":
        destination = get_destination_path()
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)

    def remove_alpha(image_path, output_path):
        try:
            with Image.open(image_path) as img:
                if img.mode in ("RGBA", "LA"):
                    background = Image.new(
                        "RGB" if img.mode == "RGBA" else "L", img.size, "white"
                    )
                    if img.mode == "RGBA":
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img.convert("L"))
                    background.save(output_path, quality=95)
                    return True
                elif img.mode == "P" and "transparency" in img.info:
                    converted = img.convert("RGBA")
                    background = Image.new("RGB", img.size, "white")
                    background.paste(converted, mask=converted.split()[3])
                    background.save(output_path, quality=95)
                    return True
                else:
                    if operation == "copy":
                        shutil.copy2(image_path, output_path)
                    elif operation == "move":
                        shutil.move(image_path, output_path)
                    return True
        except Exception as e:
            return False, str(e)

    processed_count = 0
    errors = []

    for filename in tqdm(alpha_results["hq_alpha"], desc="Processing HQ Images"):
        src_path = os.path.join(hq_folder, filename)
        dest_path = (
            src_path
            if operation == "inplace"
            else os.path.join(
                destination,
                "hq",
                get_unique_filename(os.path.join(destination, "hq"), filename),
            )
        )

        try:
            if remove_alpha(src_path, dest_path):
                processed_count += 1
            else:
                errors.append(f"Failed to process HQ: {filename}")
        except Exception as e:
            errors.append(f"Error processing HQ {filename}: {e}")

    for filename in tqdm(alpha_results["lq_alpha"], desc="Processing LQ Images"):
        src_path = os.path.join(lq_folder, filename)
        dest_path = (
            src_path
            if operation == "inplace"
            else os.path.join(
                destination,
                "lq",
                get_unique_filename(os.path.join(destination, "lq"), filename),
            )
        )

        try:
            if remove_alpha(src_path, dest_path):
                processed_count += 1
            else:
                errors.append(f"Failed to process LQ: {filename}")
        except Exception as e:
            errors.append(f"Error processing LQ {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove Alpha Channels Summary")
    print("-" * 30)
    print(f"Successfully processed: {processed_count} images")
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)


def fix_corrupted_images(folder_path, grayscale=False):
    """Re-save images to fix corruption issues."""
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

    def process_image(input_path, dest_path=None):
        try:
            image = cv2.imread(input_path)
            if image is None:
                return False, "Failed to read image"

            if grayscale:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            save_path = dest_path if dest_path else input_path
            return cv2.imwrite(save_path, image), None
        except Exception as e:
            return False, str(e)

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

        success, error = process_image(input_path, dest_path)

        if success:
            processed_count += 1
            if operation == "move" and input_path != dest_path:
                os.remove(input_path)
        else:
            errors.append(f"Error processing {filename}: {error}")

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


def tile_images(
    folder_path,
    folder_type="",
    operation="inplace",
    dest_dir="",
    tile_size=None,
    overlap=None,
    method=None,
    tiles_per_image=None,
):
    """Create tiles from images with various options."""
    print("\n" + "=" * 30)
    print(f"  Image Tiling {folder_type}")  # Add folder type to header
    print("=" * 30)

    # Only prompt for missing parameters
    if not operation:
        operation = get_file_operation_choice()
    if not dest_dir and operation != "inplace":
        dest_dir = get_destination_path()
        if not dest_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(dest_dir, exist_ok=True)
    if tile_size is None:
        while True:
            try:
                tile_size = int(input("Enter tile size (e.g., 512): ").strip())
                if tile_size > 0:
                    break
                print("Tile size must be positive.")
            except ValueError:
                print("Please enter a valid number.")
    if overlap is None:
        while True:
            try:
                overlap = float(
                    input("Enter overlap fraction (0.0 to 0.5, default 0.0): ").strip()
                    or 0.0
                )
                if 0.0 <= overlap <= 0.5:
                    break
                print("Overlap must be between 0.0 and 0.5")
            except ValueError:
                print("Please enter a valid number.")
    if method is None:
        while True:
            method = (
                input("Select tiling method (random/sequential/best): ").strip().lower()
            )
            if method in ["random", "sequential", "best"]:
                break
            print("Please enter 'random', 'sequential', or 'best'")
    if method == "random" and tiles_per_image is None:
        while True:
            try:
                tiles_per_image = int(
                    input("Enter number of tiles per image (default 1): ").strip() or 1
                )
                if tiles_per_image > 0:
                    break
                print("Number of tiles must be positive.")
            except ValueError:
                print("Please enter a valid number.")

    def extract_tiles(img, size, overlap_frac):
        h, w = img.shape[:2]
        stride = int(size * (1 - overlap_frac))
        tiles = []
        for y in range(0, h - size + 1, stride):
            for x in range(0, w - size + 1, stride):
                tile = img[y : y + size, x : x + size]
                if method == "best":
                    gray = (
                        cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
                        if len(tile.shape) > 2
                        else tile
                    )
                    score = cv2.Laplacian(gray, cv2.CV_64F).var()
                    tiles.append((tile, score, (x, y)))
                else:
                    tiles.append((tile, None, (x, y)))
        return tiles

    image_files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
    ]

    processed_count = 0
    errors = []

    for filename in tqdm(image_files, desc="Processing Images"):
        try:
            img_path = os.path.join(folder_path, filename)
            img = cv2.imread(img_path)
            if img is None:
                errors.append(f"Could not read {filename}")
                continue

            tiles = extract_tiles(img, tile_size, overlap)

            if method == "best":
                tiles.sort(key=lambda x: x[1], reverse=True)
                selected_tiles = tiles[:tiles_per_image] if tiles_per_image else tiles
            elif method == "random" and tiles_per_image:
                if len(tiles) > tiles_per_image:
                    selected_tiles = random.sample(tiles, tiles_per_image)
                else:
                    selected_tiles = tiles
            else:  # sequential
                selected_tiles = tiles

            base_name = os.path.splitext(filename)[0]
            for i, (tile, _, pos) in enumerate(selected_tiles):
                if operation == "inplace":
                    tile_filename = f"{base_name}_tile_{i}_x{pos[0]}_y{pos[1]}.png"
                    tile_path = os.path.join(folder_path, tile_filename)
                else:
                    tile_filename = f"{base_name}_tile_{i}_x{pos[0]}_y{pos[1]}.png"
                    tile_path = os.path.join(dest_dir, tile_filename)

                cv2.imwrite(tile_path, tile)
                processed_count += 1

        except Exception as e:
            errors.append(f"Error processing {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Image Tiling Summary")
    print("-" * 30)
    print(f"Total tiles created: {processed_count}")
    if errors:
        print("\nErrors encountered:")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(
                f"  ... and {len(errors) - 5} more issues (check log if detailed logging was added)."
            )
    print("-" * 30)
    print("=" * 30)


def tile_single_folder(folder_path):
    """Handle tiling for a single folder."""
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

    # Get tiling parameters
    tile_params = get_tiling_parameters()
    if not tile_params:
        return

    tile_images(folder_path, "", operation, dest_dir, **tile_params)


def get_tiling_parameters():
    """Get and validate tiling parameters from user."""
    try:
        while True:
            try:
                tile_size = int(input("Enter tile size (e.g., 512): ").strip())
                if tile_size > 0:
                    break
                print("Tile size must be positive.")
            except ValueError:
                print("Please enter a valid number.")

        while True:
            try:
                overlap = float(
                    input("Enter overlap fraction (0.0 to 0.5, default 0.0): ").strip()
                    or 0.0
                )
                if 0.0 <= overlap <= 0.5:
                    break
                print("Overlap must be between 0.0 and 0.5")
            except ValueError:
                print("Please enter a valid number.")

        while True:
            method = (
                input("Select tiling method (random/sequential/best): ").strip().lower()
            )
            if method in ["random", "sequential", "best"]:
                break
            print("Please enter 'random', 'sequential', or 'best'")

        tiles_per_image = None
        if method == "random":
            while True:
                try:
                    tiles_per_image = int(
                        input("Enter number of tiles per image (default 1): ").strip()
                        or 1
                    )
                    if tiles_per_image > 0:
                        break
                    print("Number of tiles must be positive.")
                except ValueError:
                    print("Please enter a valid number.")

        return {
            "tile_size": tile_size,
            "overlap": overlap,
            "method": method,
            "tiles_per_image": tiles_per_image,
        }
    except Exception as e:
        print(f"Error getting tiling parameters: {e}")
        return None


def tile_dataset_menu(default_hq_folder="", default_lq_folder=""):
    """Menu system for dataset tiling functionality."""
    print("\n" + "=" * 30)
    print("  Dataset Image Tiling")
    print("=" * 30)

    print("\nSelect Tiling Mode:")
    print("  1. Single Folder Tiling (Source/HQ dataset)")
    print("  2. HQ/LQ Dataset Pair Tiling")

    while True:
        mode = input("Enter mode (1 or 2): ").strip()
        if mode in ["1", "2"]:
            break
        print("Invalid choice. Please enter 1 or 2.")

    if mode == "1":
        # Single folder tiling
        folder_path = input("Enter path to folder containing images to tile: ").strip()
        if not os.path.isdir(folder_path):
            print("Invalid folder path.")
            return
        tile_single_folder(folder_path)

    else:  # mode == "2"
        print("\nHQ/LQ Dataset Tiling Options:")
        print("  1. Use current HQ/LQ folders")
        print("  2. Specify new HQ/LQ folder paths")

        while True:
            source = input("Enter choice (1 or 2): ").strip()
            if source in ["1", "2"]:
                break
            print("Invalid choice. Please enter 1 or 2.")

        hq_path = ""
        lq_path = ""

        if source == "1":
            if not default_hq_folder or not default_lq_folder:
                print("No HQ/LQ folders are currently set. Please use option 2.")
                return
            hq_path = default_hq_folder
            lq_path = default_lq_folder
        else:
            print("\nEnter paths for HQ/LQ folders:")
            hq_path = input("HQ folder path: ").strip()
            lq_path = input("LQ folder path: ").strip()
            if not (os.path.isdir(hq_path) and os.path.isdir(lq_path)):
                print("Invalid folder path(s).")
                return

        tile_hq_lq_dataset(hq_path, lq_path)


def tile_hq_lq_dataset(hq_folder, lq_folder):
    """Handle tiling for HQ/LQ dataset pairs with alignment preservation."""
    print("\n" + "=" * 30)
    print("  HQ/LQ Dataset Pair Tiling")
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
        os.makedirs(os.path.join(dest_dir, "hq_tiles"), exist_ok=True)
        os.makedirs(os.path.join(dest_dir, "lq_tiles"), exist_ok=True)

    # Get tiling parameters (same parameters will be used for both HQ and LQ)
    tile_params = get_tiling_parameters()
    if not tile_params:
        return

    # Process the paired dataset
    processed_count, errors = tile_aligned_pairs(
        hq_folder, lq_folder, operation, dest_dir, **tile_params
    )

    print("\n" + "-" * 30)
    print("  HQ/LQ Dataset Tiling Summary")
    print("-" * 30)
    print(f"Total tile pairs created: {processed_count}")
    if errors:
        print("\nErrors encountered:")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)


def tile_aligned_pairs(hq_folder, lq_folder, operation, dest_dir, **params):
    """Process HQ and LQ pairs maintaining alignment and scale."""
    hq_files = sorted([f for f in os.listdir(hq_folder) if is_image_file(f)])
    lq_files = sorted([f for f in os.listdir(lq_folder) if is_image_file(f)])
    matching_pairs = [(f, f) for f in hq_files if f in lq_files]

    if not matching_pairs:
        print("No matching HQ/LQ pairs found.")
        return 0, []

    print(f"\nProcessing {len(matching_pairs)} HQ/LQ pairs...")
    processed_pairs = 0
    errors = []

    for hq_file, lq_file in tqdm(matching_pairs, desc="Processing Pairs"):
        try:
            # Load images using PIL for better format support
            hq_img = Image.open(os.path.join(hq_folder, hq_file))
            lq_img = Image.open(os.path.join(lq_folder, lq_file))

            # Convert to numpy arrays for processing
            hq_array = np.array(hq_img)
            lq_array = np.array(lq_img)

            # Get dimensions and calculate scale
            h_hq, w_hq = hq_array.shape[:2]
            h_lq, w_lq = lq_array.shape[:2]
            scale_x = w_hq / w_lq
            scale_y = h_hq / h_lq

            # Verify scale is consistent
            if abs(scale_x - scale_y) > 0.01:  # Allow small difference
                errors.append(
                    f"Inconsistent scale in {hq_file}: x={scale_x:.2f}, y={scale_y:.2f}"
                )
                continue

            scale = (scale_x + scale_y) / 2  # Use average scale
            print(f"Processing pair with scale factor: {scale:.2f}x")

            # Calculate tile sizes
            lq_tile_size = params["tile_size"]
            hq_tile_size = int(lq_tile_size * scale)

            # Ensure tile sizes don't exceed image dimensions
            if lq_tile_size > min(h_lq, w_lq) or hq_tile_size > min(h_hq, w_hq):
                max_lq_size = min(h_lq, w_lq)
                lq_tile_size = max_lq_size
                hq_tile_size = int(max_lq_size * scale)
                print(
                    f"Warning: Adjusting tile size to {lq_tile_size} (LQ) and {hq_tile_size} (HQ) for pair {hq_file}"
                )

            # Calculate stride with overlap
            lq_stride = int(lq_tile_size * (1 - params["overlap"]))
            hq_stride = int(hq_tile_size * (1 - params["overlap"]))

            # Generate valid positions
            valid_positions = []
            for y in range(0, h_lq - lq_tile_size + 1, lq_stride):
                for x in range(0, w_lq - lq_tile_size + 1, lq_stride):
                    # Calculate corresponding HQ coordinates
                    hq_x = int(x * scale)
                    hq_y = int(y * scale)

                    # Verify HQ coordinates are within bounds
                    if hq_x + hq_tile_size <= w_hq and hq_y + hq_tile_size <= h_hq:
                        lq_tile = lq_array[y : y + lq_tile_size, x : x + lq_tile_size]
                        hq_tile = hq_array[
                            hq_y : hq_y + hq_tile_size, hq_x : hq_x + hq_tile_size
                        ]

                        score = None
                        if params["method"] == "best":
                            # Calculate score based on both tiles
                            lq_gray = (
                                cv2.cvtColor(lq_tile, cv2.COLOR_RGB2GRAY)
                                if len(lq_tile.shape) > 2
                                else lq_tile
                            )
                            hq_gray = (
                                cv2.cvtColor(hq_tile, cv2.COLOR_RGB2GRAY)
                                if len(hq_tile.shape) > 2
                                else hq_tile
                            )
                            score = (
                                cv2.Laplacian(lq_gray, cv2.CV_64F).var()
                                + cv2.Laplacian(hq_gray, cv2.CV_64F).var()
                            ) / 2

                        valid_positions.append((x, y, hq_x, hq_y, score))

            # Select positions based on method
            selected_positions = []
            if params["method"] == "best":
                valid_positions.sort(key=lambda x: x[4], reverse=True)
                selected_positions = (
                    valid_positions[: params["tiles_per_image"]]
                    if params["tiles_per_image"]
                    else valid_positions
                )
            elif params["method"] == "random" and params["tiles_per_image"]:
                selected_positions = random.sample(
                    valid_positions,
                    min(params["tiles_per_image"], len(valid_positions)),
                )
            else:  # sequential
                selected_positions = valid_positions

            # Extract and save tiles
            base_name = os.path.splitext(hq_file)[0]
            for i, (lq_x, lq_y, hq_x, hq_y, _) in enumerate(selected_positions):
                # Extract tiles maintaining original scales
                lq_tile = lq_array[
                    lq_y : lq_y + lq_tile_size, lq_x : lq_x + lq_tile_size
                ]
                hq_tile = hq_array[
                    hq_y : hq_y + hq_tile_size, hq_x : hq_x + hq_tile_size
                ]

                # Create filenames that indicate the scale relationship
                tile_suffix = f"_tile_{i}_x{lq_x}_y{lq_y}_scale{scale:.1f}.png"

                if operation == "inplace":
                    hq_path = os.path.join(hq_folder, base_name + tile_suffix)
                    lq_path = os.path.join(lq_folder, base_name + tile_suffix)
                else:
                    hq_path = os.path.join(
                        dest_dir, "hq_tiles", base_name + tile_suffix
                    )
                    lq_path = os.path.join(
                        dest_dir, "lq_tiles", base_name + tile_suffix
                    )

                # Save tiles maintaining their original scales
                Image.fromarray(hq_tile).save(hq_path, "PNG")
                Image.fromarray(lq_tile).save(lq_path, "PNG")
                processed_pairs += 1

            hq_img.close()
            lq_img.close()

        except Exception as e:
            errors.append(f"Error processing pair {hq_file}: {str(e)}")

    return processed_pairs, errors


def create_comparison_images(hq_folder, lq_folder):
    """Create side-by-side comparison images of HQ/LQ pairs."""
    print("\n" + "=" * 30)
    print("  Creating HQ/LQ Comparison Images")
    print("=" * 30)

    # Get destination path
    output_dir = get_destination_path()
    if not output_dir:
        print("Operation aborted as no destination path was provided.")
        return
    os.makedirs(output_dir, exist_ok=True)

    # Setup text parameters
    lq_label = "LQ"
    hq_label = "HQ"
    label_color = (255, 255, 255)  # White
    stroke_color = (0, 0, 0)  # Black
    stroke_width = 1
    font_size = 15

    # Font setup with better fallback handling
    try:
        # First try Arial
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        try:
            # Try Arial from Windows system font directory
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
        except IOError:
            try:
                # Try DejaVu Sans as another option (common on Linux)
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size
                )
            except IOError:
                print("Warning: Could not load TrueType fonts. Using default PIL font.")
                font = ImageFont.load_default()

    # Get the list of matching pairs
    hq_files = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    available_pairs = [
        f for f in hq_files if os.path.isfile(os.path.join(lq_folder, f))
    ]

    if not available_pairs:
        print("No matching HQ/LQ pairs found.")
        return

    # Get number of pairs to process
    while True:
        try:
            num_pairs_str = input("Enter the number of pairs to compare: ").strip()
            num_pairs = int(num_pairs_str)
            if num_pairs <= 0:
                print("Please enter a positive number.")
            elif num_pairs > len(available_pairs):
                print(
                    f"Only {len(available_pairs)} pairs available. Will use all of them."
                )
                num_pairs = len(available_pairs)
                break
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Randomly select pairs
    selected_pairs = random.sample(available_pairs, num_pairs)
    processed_count = 0
    errors = []

    def draw_text_with_stroke(
        draw, position, text, font, fill, stroke_fill, stroke_width
    ):
        x, y = position
        # Draw stroke
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill)
        # Draw main text
        draw.text((x, y), text, font=font, fill=fill)

    for filename in tqdm(selected_pairs, desc="Creating Comparisons"):
        try:
            lq_path = os.path.join(lq_folder, filename)
            hq_path = os.path.join(hq_folder, filename)
            output_path = os.path.join(output_dir, filename)

            # Open images
            lq_img = Image.open(lq_path).convert("RGB")
            hq_img = Image.open(hq_path).convert("RGB")

            # Resize to match dimensions
            target_size = (
                min(lq_img.size[0], hq_img.size[0]),
                min(lq_img.size[1], hq_img.size[1]),
            )
            lq_img = lq_img.resize(target_size, Image.Resampling.LANCZOS)
            hq_img = hq_img.resize(target_size, Image.Resampling.LANCZOS)

            # Create composite image
            composite_img = Image.new(
                "RGB", (target_size[0], target_size[1]), (255, 255, 255)
            )
            composite_img.paste(lq_img, (0, 0))
            composite_img.paste(
                hq_img,
                (0, 0),
                mask=hq_img.split()[3] if hq_img.mode == "RGBA" else None,
            )

            # Add labels
            draw = ImageDraw.Draw(composite_img)
            text_padding = 5

            # Draw labels with stroke effect
            draw_text_with_stroke(
                draw,
                (text_padding, text_padding),
                lq_label,
                font,
                label_color,
                stroke_color,
                stroke_width,
            )
            draw_text_with_stroke(
                draw,
                (
                    target_size[0] - text_padding - font.getsize(hq_label)[0],
                    text_padding,
                ),
                hq_label,
                font,
                label_color,
                stroke_color,
                stroke_width,
            )

            # Save the composite image
            composite_img.save(output_path, quality=100, subsampling=0)
            processed_count += 1

        except Exception as e:
            errors.append(f"Error processing {filename}: {e}")

    print("\n" + "-" * 30)
    print(" Create Comparisons Summary")
    print("-" * 30)
    print(f"Total pairs to process: {num_pairs}")
    print(f"Successfully created: {processed_count} comparisons")

    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)


def create_gif_comparison(hq_folder, lq_folder):
    """Create animated GIF/WebP comparisons of HQ/LQ pairs with transition effects."""
    print("\n" + "=" * 30)
    print("  Creating HQ/LQ Animated Comparisons")
    print("=" * 30)

    # Get output format
    while True:
        format_choice = input("Select output format (gif/webp): ").strip().lower()
        if format_choice in ["gif", "webp"]:
            break
        print("Invalid format. Please enter 'gif' or 'webp'.")

    # Get destination path
    output_dir = get_destination_path()
    if not output_dir:
        print("Operation aborted as no destination path was provided.")
        return
    os.makedirs(output_dir, exist_ok=True)

    # Get available pairs
    hq_files = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    available_pairs = [
        f for f in hq_files if os.path.isfile(os.path.join(lq_folder, f))
    ]

    if not available_pairs:
        print("No matching HQ/LQ pairs found.")
        return

    # Get number of pairs to process
    while True:
        try:
            num_pairs_str = input(
                "Enter the number of pairs to create animations for: "
            )
            num_pairs = int(num_pairs_str)
            if num_pairs <= 0:
                print("Please enter a positive number.")
            elif num_pairs > len(available_pairs):
                print(
                    f"Only {len(available_pairs)} pairs available. Will use all of them."
                )
                num_pairs = len(available_pairs)
                break
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get FPS
    while True:
        try:
            fps = float(
                input("Enter FPS (frames per second, e.g., 30): ").strip() or 30
            )
            if fps > 0:
                break
            print("FPS must be positive.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get transition duration percentage
    while True:
        try:
            transition_percent = float(
                input(
                    "Enter transition duration as percentage of total animation (10-90): "
                ).strip()
                or 50
            )
            if 10 <= transition_percent <= 90:
                break
            print("Percentage must be between 10 and 90.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get transition speed multiplier
    while True:
        try:
            speed_multiplier = float(
                input(
                    "Enter transition speed multiplier (0.5 = slower, 2.0 = faster): "
                ).strip()
                or 1.0
            )
            if speed_multiplier > 0:
                break
            print("Speed multiplier must be positive.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get transition type
    print("\nSelect transition type:")
    print("1. Fade")
    print("2. Slide (Left to Right)")
    print("3. Slide (Right to Left)")
    print("4. Zoom")
    print("5. Cut")
    print("6. Special")
    while True:
        transition = input("Enter choice (1-6): ").strip()
        if transition in ["1", "2", "3", "4", "5", "6"]:
            break
        print("Invalid choice. Please enter 1-6.")

    # Calculate frames based on FPS and transition percentage
    total_duration = 2.0  # Total animation duration in seconds
    transition_duration = (transition_percent / 100.0) * total_duration
    static_duration = (total_duration - transition_duration) / 2

    num_transition_frames = int(fps * transition_duration)
    num_static_frames = int(fps * static_duration)

    # Function to create separator line for slide transitions
    def create_separator(
        img, position, thickness=2, color="white", direction="vertical"
    ):
        """Create separator line with custom settings."""
        separator = img.copy()
        draw = ImageDraw.Draw(separator)

        if color == "white":
            line_color = (255, 255, 255)
            edge_color = (0, 0, 0)
        else:  # black
            line_color = (0, 0, 0)
            edge_color = (255, 255, 255)

        if direction == "vertical":
            x = int(position)
            # Draw thin edge lines
            draw.line([(x - 1, 0), (x - 1, img.height)], fill=edge_color, width=1)
            draw.line(
                [(x + thickness, 0), (x + thickness, img.height)],
                fill=edge_color,
                width=1,
            )
            # Draw main line
            draw.line([(x, 0), (x, img.height)], fill=line_color, width=thickness)

        return separator

    # Randomly select pairs
    selected_pairs = random.sample(available_pairs, num_pairs)
    processed_count = 0
    errors = []

    def apply_easing(progress, mode="ease-in-out"):
        # Simple cubic ease-in-out
        if mode == "ease-in-out":
            if progress < 0.5:
                return 4 * progress * progress * progress
            else:
                return 1 - pow(-2 * progress + 2, 3) / 2
        return progress

    for filename in tqdm(selected_pairs, desc="Creating Animated Comparisons"):
        try:
            lq_path = os.path.join(lq_folder, filename)
            hq_path = os.path.join(hq_folder, filename)
            output_name = f"comparison_{os.path.splitext(filename)[0]}.{format_choice}"
            output_path = os.path.join(output_dir, output_name)

            # Open images
            lq_img = Image.open(lq_path).convert("RGB")
            hq_img = Image.open(hq_path).convert("RGB")

            # Resize to match dimensions
            target_size = (
                min(lq_img.size[0], hq_img.size[0]),
                min(lq_img.size[1], hq_img.size[1]),
            )
            lq_img = lq_img.resize(target_size, Image.Resampling.LANCZOS)
            hq_img = hq_img.resize(target_size, Image.Resampling.LANCZOS)

            frames = []

            # Add static LQ frames
            frames.extend([np.array(lq_img)] * num_static_frames)

            # Add transition frames with easing
            for i in range(num_transition_frames):
                progress = i / (num_transition_frames - 1)
                eased_progress = apply_easing(progress, "ease-in-out")

                if transition == "1":  # Fade
                    frame = Image.blend(lq_img, hq_img, eased_progress)
                    frames.append(np.array(frame))

                elif transition in ["2", "3"]:  # Slide transitions
                    frame = Image.new("RGB", target_size)
                    offset = int(target_size[0] * eased_progress)  # Use eased progress

                    if transition == "2":  # Left to Right
                        frame.paste(lq_img, (0, 0))
                        frame.paste(hq_img.crop((0, 0, offset, target_size[1])), (0, 0))
                        frame = create_separator(frame, offset, 2, "white")
                    else:  # Right to Left
                        reverse_offset = target_size[0] - offset
                        frame.paste(hq_img, (0, 0))
                        frame.paste(
                            lq_img.crop(
                                (reverse_offset, 0, target_size[0], target_size[1])
                            ),
                            (reverse_offset, 0),
                        )
                        frame = create_separator(frame, reverse_offset, 2, "white")
                    frames.append(np.array(frame))

                elif transition == "4":  # Zoom with easing
                    zoom_size = (
                        int(target_size[0] * (1 + 0.2 * (1 - eased_progress))),
                        int(target_size[1] * (1 + 0.2 * (1 - eased_progress))),
                    )
                    zoomed = Image.blend(
                        lq_img.resize(zoom_size, Image.Resampling.LANCZOS),
                        hq_img.resize(zoom_size, Image.Resampling.LANCZOS),
                        eased_progress,
                    )
                    # Center crop
                    left = (zoom_size[0] - target_size[0]) // 2
                    top = (zoom_size[1] - target_size[1]) // 2
                    frame = zoomed.crop(
                        (left, top, left + target_size[0], top + target_size[1])
                    )
                    frames.append(np.array(frame))

                elif transition == "5":  # Dynamic Cut
                    # Calculate dynamic cut timing
                    cut_sequence = []
                    quick_cuts = int(num_transition_frames * 0.3)  # 30% quick cuts
                    rest_frames = num_transition_frames - quick_cuts

                    # Generate dynamic cut sequence
                    current_frame = 0
                    while current_frame < num_transition_frames:
                        if current_frame < quick_cuts:
                            cut_duration = max(
                                2, int(fps * 0.1)
                            )  # Quick cuts (0.1 sec)
                        else:
                            cut_duration = max(
                                5, int(fps * 0.5)
                            )  # Longer cuts (0.5 sec)

                        cut_sequence.extend([current_frame % 2] * cut_duration)
                        current_frame += cut_duration

                    # Add cut transition frames
                    for is_hq in cut_sequence[:num_transition_frames]:
                        frames.append(np.array(hq_img if is_hq else lq_img))

                elif transition == "6":  # Special Creative Transition
                    third = num_transition_frames // 3

                    # Phase 1: Fade with slight zoom (first third)
                    for i in range(third):
                        progress = i / third
                        zoom_progress = apply_easing(progress, "ease-in-out")
                        zoom_size = (
                            int(target_size[0] * (1 + 0.1 * (1 - zoom_progress))),
                            int(target_size[1] * (1 + 0.1 * (1 - zoom_progress))),
                        )

                        zoomed_lq = lq_img.resize(zoom_size, Image.Resampling.LANCZOS)
                        zoomed_hq = hq_img.resize(zoom_size, Image.Resampling.LANCZOS)

                        blended = Image.blend(zoomed_lq, zoomed_hq, zoom_progress * 0.5)

                        # Center crop
                        left = (zoom_size[0] - target_size[0]) // 2
                        top = (zoom_size[1] - target_size[1]) // 2
                        frame = blended.crop(
                            (left, top, left + target_size[0], top + target_size[1])
                        )
                        frames.append(np.array(frame))

                    # Phase 2: Quick cuts with fade (second third)
                    for i in range(third):
                        progress = apply_easing(i / third, "ease-in-out")
                        if i % 3 == 0:  # Quick cut every 3 frames
                            frame = Image.blend(lq_img, hq_img, 0.5 + (progress * 0.5))
                        else:
                            frame = Image.blend(lq_img, hq_img, progress)
                        frames.append(np.array(frame))

                    # Phase 3: Slide with fade (final third)
                    for i in range(third):
                        progress = apply_easing(i / third, "ease-in-out")
                        frame = Image.new("RGB", target_size)
                        offset = int(target_size[0] * progress)

                        # Create base frame with fade
                        base = Image.blend(lq_img, hq_img, progress)
                        frame.paste(base, (0, 0))

                        # Add sliding HQ portion
                        frame.paste(hq_img.crop((0, 0, offset, target_size[1])), (0, 0))
                        frames.append(np.array(frame))

            # Add static HQ frames
            frames.extend([np.array(hq_img)] * num_static_frames)

            # Adjust frame timing based on speed multiplier
            adjusted_duration = (1.0 / fps) / speed_multiplier

            # Save as GIF or WebP
            import imageio

            if format_choice == "gif":
                imageio.mimsave(output_path, frames, duration=adjusted_duration, loop=0)
            else:  # webp
                imageio.mimsave(
                    output_path,
                    frames,
                    duration=adjusted_duration,
                    loop=0,
                    format="WEBP",
                    quality=90,
                )

            processed_count += 1

        except Exception as e:
            errors.append(f"Error processing {filename}: {e}")

    print("\n" + "-" * 30)
    print(" Create Animated Comparison Summary")
    print("-" * 30)
    print(f"Format: {format_choice.upper()}")
    print(f"FPS: {fps}")
    print(f"Transition Duration: {transition_percent}% of total")
    print(f"Speed Multiplier: {speed_multiplier}x")
    print(f"Successfully created: {processed_count} animations")

    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)


# --- Extract Frames Utility ---
def extract_frames_menu():
    print("\n--- Extract Frames from Video ---")
    video_path = input("Enter path to video file: ").strip()
    if not os.path.isfile(video_path):
        print("Error: Video file does not exist.")
        return
    out_dir = input("Enter output directory for frames: ").strip()
    if not out_dir:
        print("Error: Output directory required.")
        return
    os.makedirs(out_dir, exist_ok=True)

    # Model selection
    model_options = [
        ("ConvNextS", 0),
        ("ConvNextL", 1),
        ("VITS", 2),
        ("VITB", 3),
        ("VITL", 4),
        ("VITG", 5),
    ]
    print("Select embedding model:")
    for i, (name, _) in enumerate(model_options):
        print(f"  {i+1}. {name}")
    while True:
        model_choice = input("Model [1-6, default 1]: ").strip() or "1"
        if model_choice in [str(i + 1) for i in range(6)]:
            model_idx = int(model_choice) - 1
            break
        print("Invalid choice.")
    model_name = model_options[model_idx][0]

    # Distance function
    dist_options = [
        ("euclid", "Euclidean Distance"),
        ("cosine", "Cosine Distance"),
    ]
    print("Select distance function:")
    for i, (_, desc) in enumerate(dist_options):
        print(f"  {i+1}. {desc}")
    while True:
        dist_choice = input("Distance [1-2, default 1]: ").strip() or "1"
        if dist_choice in ["1", "2"]:
            dist_idx = int(dist_choice) - 1
            break
        print("Invalid choice.")
    dist_name = dist_options[dist_idx][0]

    # Threshold
    default_threshold = 2.3 if dist_name == "euclid" else 0.3
    threshold = input(f"Enter threshold (default {default_threshold}): ").strip()
    try:
        threshold = float(threshold) if threshold else default_threshold
    except Exception:
        print("Invalid threshold, using default.")
        threshold = default_threshold

    # Scale
    scale = input("Enter scale factor (default 4): ").strip()
    try:
        scale = int(scale) if scale else 4
    except Exception:
        print("Invalid scale, using 4.")
        scale = 4

    # Max frames
    max_len = input("Max frames to extract (default 1000): ").strip()
    try:
        max_len = int(max_len) if max_len else 1000
    except Exception:
        print("Invalid max, using 1000.")
        max_len = 1000

    # Device
    device = input("Device (cuda/cpu, default cuda): ").strip() or "cuda"

    # --- Inline enum, model, and distance logic ---
    class EmbeddedModel:
        ConvNextS = 0
        ConvNextL = 1
        VITS = 2
        VITB = 3
        VITL = 4
        VITG = 5

    def enum_to_model(enum):
        import torch

        if enum == EmbeddedModel.ConvNextS:
            # convnext_small
            state = torch.hub.load_state_dict_from_url(
                url="https://github.com/umzi2/Dataset_Preprocessing/releases/download/SPARK_model_duplication/convnextS_1kpretrained_official_style.pth",
                map_location="cpu",
                weights_only=True,
            )
            from timm.layers import trunc_normal_, DropPath

            class Block(torch.nn.Module):
                def __init__(self, dim, drop_path=0.0, layer_scale_init_value=1e-6):
                    super().__init__()
                    self.dwconv = torch.nn.Conv2d(
                        dim, dim, kernel_size=7, padding=3, groups=dim
                    )
                    self.norm = LayerNorm(dim, eps=1e-6, data_format="channels_last")
                    self.pwconv1 = torch.nn.Linear(dim, 4 * dim)
                    self.act = torch.nn.GELU()
                    self.pwconv2 = torch.nn.Linear(4 * dim, dim)
                    self.gamma = (
                        torch.nn.Parameter(
                            layer_scale_init_value * torch.ones((dim)),
                            requires_grad=True,
                        )
                        if layer_scale_init_value > 0
                        else None
                    )
                    self.drop_path = (
                        DropPath(drop_path) if drop_path > 0.0 else torch.nn.Identity()
                    )

                def forward(self, x):
                    input = x
                    x = self.dwconv(x)
                    x = x.permute(0, 2, 3, 1)
                    x = self.norm(x)
                    x = self.pwconv1(x)
                    x = self.act(x)
                    x = self.pwconv2(x)
                    if self.gamma is not None:
                        x = self.gamma * x
                    x = x.permute(0, 3, 1, 2)
                    x = input + self.drop_path(x)
                    return x

            class ConvNeXt(torch.nn.Module):
                def __init__(
                    self, in_chans=3, depths=[3, 3, 27, 3], dims=[96, 192, 384, 768]
                ):
                    super().__init__()
                    self.downsample_layers = torch.nn.ModuleList()
                    stem = torch.nn.Sequential(
                        torch.nn.Conv2d(in_chans, dims[0], kernel_size=4, stride=4),
                        LayerNorm(dims[0], eps=1e-6, data_format="channels_first"),
                    )
                    self.downsample_layers.append(stem)
                    for i in range(3):
                        downsample_layer = torch.nn.Sequential(
                            LayerNorm(dims[i], eps=1e-6, data_format="channels_first"),
                            torch.nn.Conv2d(
                                dims[i], dims[i + 1], kernel_size=2, stride=2
                            ),
                        )
                        self.downsample_layers.append(downsample_layer)
                    self.stages = torch.nn.ModuleList()
                    for i in range(4):
                        stage = torch.nn.Sequential(
                            *[Block(dim=dims[i]) for _ in range(depths[i])]
                        )
                        self.stages.append(stage)

                def forward(self, x):
                    for i in range(4):
                        x = self.downsample_layers[i](x)
                        x = self.stages[i](x)
                    return x.mean([-2, -1])

            model = ConvNeXt()
            model.load_state_dict(state)
            return model.eval()
        elif enum == EmbeddedModel.ConvNextL:
            state = torch.hub.load_state_dict_from_url(
                url="https://github.com/umzi2/Dataset_Preprocessing/releases/download/SPARK_model_duplication/convnextL_384_1kpretrained_official_style.pth",
                map_location="cpu",
                weights_only=True,
            )
            # ... (same as above, with different dims)
            # For brevity, use ConvNextS logic but with dims=[192, 384, 768, 1536]
            from timm.layers import trunc_normal_, DropPath

            class Block(torch.nn.Module):
                def __init__(self, dim, drop_path=0.0, layer_scale_init_value=1e-6):
                    super().__init__()
                    self.dwconv = torch.nn.Conv2d(
                        dim, dim, kernel_size=7, padding=3, groups=dim
                    )
                    self.norm = LayerNorm(dim, eps=1e-6, data_format="channels_first")
                    self.pwconv1 = torch.nn.Linear(dim, 4 * dim)
                    self.act = torch.nn.GELU()
                    self.pwconv2 = torch.nn.Linear(4 * dim, dim)
                    self.gamma = (
                        torch.nn.Parameter(
                            layer_scale_init_value * torch.ones((dim)),
                            requires_grad=True,
                        )
                        if layer_scale_init_value > 0
                        else None
                    )
                    self.drop_path = (
                        DropPath(drop_path) if drop_path > 0.0 else torch.nn.Identity()
                    )

                def forward(self, x):
                    input = x
                    x = self.dwconv(x)
                    x = x.permute(0, 2, 3, 1)
                    x = self.norm(x)
                    x = self.pwconv1(x)
                    x = self.act(x)
                    x = self.pwconv2(x)
                    if self.gamma is not None:
                        x = self.gamma * x
                    x = x.permute(0, 3, 1, 2)
                    x = input + self.drop_path(x)
                    return x

            class ConvNeXt(torch.nn.Module):
                def __init__(
                    self, in_chans=3, depths=[3, 3, 27, 3], dims=[192, 384, 768, 1536]
                ):
                    super().__init__()
                    self.downsample_layers = torch.nn.ModuleList()
                    stem = torch.nn.Sequential(
                        torch.nn.Conv2d(in_chans, dims[0], kernel_size=4, stride=4),
                        LayerNorm(dims[0], eps=1e-6, data_format="channels_first"),
                    )
                    self.downsample_layers.append(stem)
                    for i in range(3):
                        downsample_layer = torch.nn.Sequential(
                            LayerNorm(dims[i], eps=1e-6, data_format="channels_first"),
                            torch.nn.Conv2d(
                                dims[i], dims[i + 1], kernel_size=2, stride=2
                            ),
                        )
                        self.downsample_layers.append(downsample_layer)
                    self.stages = torch.nn.ModuleList()
                    for i in range(4):
                        stage = torch.nn.Sequential(
                            *[Block(dim=dims[i]) for _ in range(depths[i])]
                        )
                        self.stages.append(stage)

                def forward(self, x):
                    for i in range(4):
                        x = self.downsample_layers[i](x)
                        x = self.stages[i](x)
                    return x.mean([-2, -1])

            model = ConvNeXt(dims=[192, 384, 768, 1536])
            model.load_state_dict(state)
            return model.eval()
        elif enum == EmbeddedModel.VITS:
            return (
                __import__("torch")
                .hub.load("facebookresearch/dinov2", "dinov2_vits14")
                .eval()
            )
        elif enum == EmbeddedModel.VITB:
            return (
                __import__("torch")
                .hub.load("facebookresearch/dinov2", "dinov2_vitb14")
                .eval()
            )
        elif enum == EmbeddedModel.VITL:
            return (
                __import__("torch")
                .hub.load("facebookresearch/dinov2", "dinov2_vitl14")
                .eval()
            )
        elif enum == EmbeddedModel.VITG:
            return (
                __import__("torch")
                .hub.load("facebookresearch/dinov2", "dinov2_vitg14")
                .eval()
            )

    def cosine_dist(emb1, emb2):
        import torch.nn.functional as F

        emb1_norm = F.normalize(emb1, dim=-1)
        emb2_norm = F.normalize(emb2, dim=-1)
        return 1 - F.cosine_similarity(emb1_norm, emb2_norm).item()

    def euclid_dist(emb1, emb2):
        import torch

        return torch.cdist(emb1, emb2).item()

    # --- Embedding class ---
    class ImgToEmbedding:
        def __init__(
            self, model=EmbeddedModel.ConvNextS, amp=True, scale=4, device="cuda"
        ):
            import torch

            self.device = torch.device(device)
            self.scale = scale
            self.amp = amp
            self.model = enum_to_model(model).to(self.device)
            self.vit = model in [
                EmbeddedModel.VITS,
                EmbeddedModel.VITB,
                EmbeddedModel.VITL,
                EmbeddedModel.VITG,
            ]

        @staticmethod
        def check_img_size(x):
            import torch.nn.functional as F

            b, c, h, w = x.shape
            mod_pad_h = (14 - h % 14) % 14
            mod_pad_w = (14 - w % 14) % 14
            return F.pad(x, (0, mod_pad_w, 0, mod_pad_h), "reflect")

        def img_to_tensor(self, x):
            import torch

            if self.vit:
                return self.check_img_size(
                    torch.tensor(x.transpose((2, 0, 1)))[None, :, :, :].to(self.device)
                )
            return torch.tensor(x.transpose((2, 0, 1)))[None, :, :, :].to(self.device)

        def __call__(self, x):
            import torch

            if self.scale > 1:
                h, w = x.shape[:2]
                # No resize, just use as is (or implement if chainner_ext is available)
            with torch.amp.autocast(self.device.__str__(), torch.float16, self.amp):
                x = self.img_to_tensor(x)
                return self.model(x)

    # Select model enum
    model_enum = [
        EmbeddedModel.ConvNextS,
        EmbeddedModel.ConvNextL,
        EmbeddedModel.VITS,
        EmbeddedModel.VITB,
        EmbeddedModel.VITL,
        EmbeddedModel.VITG,
    ][model_idx]
    embedder = ImgToEmbedding(model=model_enum, amp=True, scale=scale, device=device)
    dist_fn = euclid_dist if dist_name == "euclid" else cosine_dist

    # --- Video to frames logic ---
    import cv2
    import numpy as np
    from tqdm import tqdm

    capture = cv2.VideoCapture(video_path)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    ref = None
    n = 0
    n_s = 0
    with tqdm(total=total_frames) as pbar:
        while capture.isOpened():
            ret, frame = capture.read()
            if n_s > max_len:
                break
            if not ret:
                break
            if ref is None:
                ref = embedder(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                )
            else:
                temp_embedd = embedder(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                )
                if dist_fn(ref, temp_embedd) > threshold:
                    cv2.imwrite(os.path.join(out_dir, f"frame_{n}.png"), frame)
                    ref = temp_embedd
                    n_s += 1
            n += 1
            pbar.update(1)
    capture.release()
    print(f"\nDone. Extracted up to {n_s} frames to {out_dir}.")

# --- END Extract Frames Utility ---


def main_menu():
    hq_folder = ""
    lq_folder = ""

    while True:
        print("\n" + "#" * 40)
        print("  Image Training Dataset Utility")
        print("#" * 40)
        print("\nCurrent Folders:")
        print(f"  HQ Folder: {hq_folder if hq_folder else 'Not set'}")
        print(f"  LQ Folder: {lq_folder if lq_folder else 'Not set'}")
        print("\nMenu:")
        print("  1. Set HQ/LQ Folders")
        option_map = {"1": ("Set HQ/LQ Folders", None)}
        next_option = 2
        if hq_folder and lq_folder:
            print("\n  --- HQ/LQ Dataset Analysis ---")
            print(f"  {next_option}. Find HQ/LQ Scale")
            option_map[str(next_option)] = (
                "Find HQ/LQ Scale",
                lambda: find_hq_lq_scale(hq_folder, lq_folder),
            )
            next_option += 1
            print(f"  {next_option}. Test HQ/LQ Scale")
            option_map[str(next_option)] = (
                "Test HQ/LQ Scale",
                lambda: test_hq_lq_scale(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Check Image Consistency (Formats/Modes in HQ & LQ)"
            )
            option_map[str(next_option)] = (
                "Check Image Consistency",
                lambda: (
                    check_consistency(hq_folder, "HQ"),
                    check_consistency(lq_folder, "LQ"),
                ),
            )
            next_option += 1
            print(f"  {next_option}. Report Image Dimensions (Stats for HQ & LQ)")
            option_map[str(next_option)] = (
                "Report Image Dimensions",
                lambda: (
                    report_dimensions(hq_folder, "HQ"),
                    report_dimensions(lq_folder, "LQ"),
                ),
            )
            next_option += 1
            print(
                f"  {next_option}. Find Extreme Dimensions (Biggest/Smallest in HQ & LQ)"
            )
            option_map[str(next_option)] = (
                "Find Extreme Dimensions",
                lambda: (
                    find_extreme_dimensions(hq_folder, "HQ"),
                    find_extreme_dimensions(lq_folder, "LQ"),
                ),
            )
            next_option += 1
            print(
                f"  {next_option}. Verify Image Integrity (Corrupted Files in HQ & LQ)"
            )
            option_map[str(next_option)] = (
                "Verify Image Integrity",
                lambda: verify_images(hq_folder, lq_folder),
            )
            next_option += 1
            print(f"  {next_option}. Find Misaligned Images (using Phase Correlation)")
            option_map[str(next_option)] = (
                "Find Misaligned Images",
                lambda: find_misaligned_images(hq_folder, lq_folder),
            )
            next_option += 1
            print(f"  {next_option}. Generate Full HQ/LQ Dataset REPORT")
            option_map[str(next_option)] = (
                "Generate Full HQ/LQ Dataset REPORT",
                lambda: generate_hq_lq_dataset_report(hq_folder, lq_folder),
            )
            next_option += 1
            print("\n  --- HQ/LQ Dataset Operations ---")
            print(f"  {next_option}. Remove Small Image Pairs (based on min dimension)")
            option_map[str(next_option)] = (
                "Remove Small Image Pairs",
                lambda: remove_small_image_pairs(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Extract Random Image Pairs (subset to new location)"
            )
            option_map[str(next_option)] = (
                "Extract Random Image Pairs",
                lambda: extract_random_pairs(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Shuffle Image Pairs (renames to sequential in place or new location)"
            )
            option_map[str(next_option)] = (
                "Shuffle Image Pairs",
                lambda: shuffle_image_pairs(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Transform Dataset (Rotate, Flip, Brightness, etc. on subset)"
            )
            option_map[str(next_option)] = (
                "Transform Dataset",
                lambda: transform_dataset(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Dataset Color Adjustment (Contrast, Saturation, etc. on subset)"
            )
            option_map[str(next_option)] = (
                "Dataset Color Adjustment",
                lambda: dataset_colour_adjustment(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Grayscale Conversion (convert subset to grayscale)"
            )
            option_map[str(next_option)] = (
                "Grayscale Conversion",
                lambda: grayscale_conversion(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Advanced Split/Adjust Dataset (Remove by criteria, Split)"
            )
            option_map[str(next_option)] = (
                "Advanced Split/Adjust Dataset",
                lambda: split_adjust_dataset(hq_folder, lq_folder),
            )
            next_option += 1
        print("\n  --- General Dataset Operations ---")
        print(
            f"  {next_option}. Combine Multiple Datasets (merges several HQ/LQ paired datasets)"
        )
        option_map[str(next_option)] = ("Combine Multiple Datasets", combine_datasets)
        next_option += 1
        print(f"  {next_option}. Find Alpha (detect images with alpha channels)")
        option_map[str(next_option)] = (
            "Find Alpha",
            lambda: find_alpha_channels(hq_folder, lq_folder),
        )
        next_option += 1
        print(f"  {next_option}. Remove Alpha (remove alpha channels from images)")
        option_map[str(next_option)] = (
            "Remove Alpha",
            lambda: remove_alpha_channels(hq_folder, lq_folder),
        )
        next_option += 1
        print(f"  {next_option}. Comparisons (create side-by-side HQ/LQ comparisons)")
        option_map[str(next_option)] = (
            "Comparisons",
            lambda: create_comparison_images(hq_folder, lq_folder),
        )
        next_option += 1
        print(
            f"  {next_option}. Fix Corrupted Images (re-save images to fix corruption)"
        )
        option_map[str(next_option)] = (
            "Fix Corrupted Images",
            lambda: fix_corrupted_images(hq_folder),
        )
        next_option += 1
        print(f"  {next_option}. HQ/LQ Dataset Image Tiling (create image tiles)")
        option_map[str(next_option)] = (
            "HQ/LQ Dataset Image Tiling",
            lambda: tile_dataset_menu(hq_folder, lq_folder),
        )
        next_option += 1
        print(
            f"  {next_option}. Create HQ/LQ Animated gif/webp Comparisons (animated gifs/webps of pairs)"
        )
        option_map[str(next_option)] = (
            "Create HQ/LQ Animated gif/webp Comparisons",
            lambda: create_gif_comparison(hq_folder, lq_folder),
        )
        next_option += 1
        print(f"  {next_option}. Extract Frames (from video)")
        option_map[str(next_option)] = ("Extract Frames", extract_frames_menu)
        next_option += 1
        print(f"  {next_option}. Exit")
        option_map[str(next_option)] = ("Exit", None)
        print("-" * 40)

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            hq_folder = get_folder_path("Enter HQ folder path: ")
            lq_folder = get_folder_path("Enter LQ folder path: ")
        elif choice in option_map and option_map[choice][1]:
            option_map[choice][1]()
        elif choice in option_map and option_map[choice][0] == "Exit":
            print("Exiting Image Training Dataset Utility. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")

        # Add a small pause or press enter to continue, especially after long reports
        if choice not in [
            "1",
            str(next_option - 1),
        ]:  # Don't pause after setting folders or exiting
            input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    # Setup global logging to a file for the entire session, if desired
    # This can be complex if functions also try to set up their own file handlers.
    # For simplicity, individual functions might log to console or specific files.
    # Default basicConfig here will just go to console if no file handler is set.
    # logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # A session log file:
    session_log_file = "image_dataset_utility_session.log"
    # Clear or append to session log
    # For this example, let's append. For clearing each session, mode='w'.
    # Be careful with multiple file handlers if functions also create them.
    # It's often better for functions to use `logging.getLogger(__name__)`
    # and configure handlers at the top level.

    # Minimal global logging to console. Functions can add specific file handlers.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    main_menu()
