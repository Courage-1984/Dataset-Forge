import os
import logging
import numpy as np
from PIL import Image
from tqdm import tqdm
from dataset_forge.io_utils import is_image_file
from collections import Counter, defaultdict
import cv2
import shutil
import concurrent.futures
from PIL import Image, ImageEnhance, UnidentifiedImageError, ImageFont, ImageDraw
from dataset_forge.analysis_ops import (
    ScaleAnalyzer,
    DimensionAnalyzer,
    ConsistencyAnalyzer,
)


def get_file_operation_choice():
    while True:
        choice = input("Enter operation choice (copy/move/inplace): ").strip().lower()
        if choice in ["copy", "move", "inplace"]:
            return choice
        else:
            print("Invalid choice. Please enter 'copy', 'move', or 'inplace'.")


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


def get_destination_path(is_optional=False):
    path = input("Enter destination path" + (" (optional): " if is_optional else ": "))
    if is_optional and not path:
        return None
    if not os.path.isdir(path):
        print(f"Path does not exist: {path}")
        return None
    return path


def get_unique_filename(dest_dir, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_name = filename
    while os.path.exists(os.path.join(dest_dir, unique_name)):
        unique_name = f"{base}_{counter}{ext}"
        counter += 1
    return unique_name


# Wrappers for backward compatibility


def find_hq_lq_scale(hq_folder, lq_folder, verbose=True):
    analyzer = ScaleAnalyzer()
    return analyzer.analyze(hq_folder, lq_folder, verbose=verbose)


def report_dimensions(folder_path, folder_name, verbose=True):
    analyzer = DimensionAnalyzer()
    return analyzer.analyze(folder_path, folder_name, verbose=verbose)


def check_consistency(folder_path, folder_name, verbose=True):
    analyzer = ConsistencyAnalyzer()
    return analyzer.analyze(folder_path, folder_name, verbose=verbose)


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
