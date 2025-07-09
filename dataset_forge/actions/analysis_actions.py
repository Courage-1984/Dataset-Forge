import os
import logging
import numpy as np
from PIL import Image
from tqdm import tqdm
from dataset_forge.io_utils import is_image_file
from collections import Counter
import cv2
import shutil
import concurrent.futures
from dataset_forge.analysis_ops import (
    ScaleAnalyzer,
    DimensionAnalyzer,
    ConsistencyAnalyzer,
)


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
            f"HQ File Formats: {{ {k: len(v) for k, v in hq_consistency['formats'].items()} }}"
        )
    else:
        print("HQ File Formats: No image files found or processed.")
    if hq_consistency["modes"]:
        print(
            f"HQ Color Modes: {{ {k: len(v) for k, v in hq_consistency['modes'].items()} }}"
        )
    else:
        print("HQ Color Modes: No image files found or processed.")
    if hq_consistency["errors"]:
        print(f"HQ files with processing errors: {len(hq_consistency['errors'])}")

    print("\n--- Consistency Check (LQ) ---")
    lq_consistency = check_consistency(lq_folder, "LQ", verbose=False)
    if lq_consistency["formats"]:
        print(
            f"LQ File Formats: {{ {k: len(v) for k, v in lq_consistency['formats'].items()} }}"
        )
    else:
        print("LQ File Formats: No image files found or processed.")
    if lq_consistency["modes"]:
        print(
            f"LQ Color Modes: {{ {k: len(v) for k, v in lq_consistency['modes'].items()} }}"
        )
    else:
        print("LQ Color Modes: No image files found or processed.")
    if lq_consistency["errors"]:
        print(f"LQ files with processing errors: {len(lq_consistency['errors'])}")

    print("\n--- Dimension Report (HQ) ---")
    hq_dimensions_report = report_dimensions(hq_folder, "HQ", verbose=False)
    if hq_dimensions_report["dimensions"]:
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
    lq_dimensions_report = report_dimensions(lq_folder, "LQ", verbose=False)
    if lq_dimensions_report["dimensions"]:
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


def find_hq_lq_scale(hq_folder, lq_folder, verbose=True):
    analyzer = ScaleAnalyzer()
    return analyzer.analyze(hq_folder, lq_folder, verbose=verbose)


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


def check_consistency(folder_path, folder_name, verbose=True):
    analyzer = ConsistencyAnalyzer()
    return analyzer.analyze(folder_path, folder_name, verbose=verbose)


def report_dimensions(folder_path, folder_name, verbose=True):
    analyzer = DimensionAnalyzer()
    return analyzer.analyze(folder_path, folder_name, verbose=verbose)


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
                    if file not in biggest_files:
                        biggest_files.append(file)

                # Check for smallest dimension (consider total pixels)
                if width * height < smallest_dim[0] * smallest_dim[1]:
                    smallest_dim = (width, height)
                    smallest_files = [file]
                elif width * height == smallest_dim[0] * smallest_dim[1]:
                    if file not in smallest_files:
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

    corrupted_files = []
    for file_path, label in tqdm(all_files_to_check, desc="Verifying Images"):
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception as e:
            corrupted_files.append((label, str(e)))

    if corrupted_files:
        print(f"\nCorrupted or unreadable images found: {len(corrupted_files)}")
        for i, (label, error) in enumerate(corrupted_files[:5]):
            print(f"  - {label}: {error}")
        if len(corrupted_files) > 5:
            print(f"  ... and {len(corrupted_files) - 5} more files.")
    else:
        print("All images passed integrity check.")
    print("-" * 30)
    print("=" * 30)
    return corrupted_files


def fix_corrupted_images(*args, **kwargs):
    """Fix corrupted images in a dataset."""
    pass


def find_misaligned_images(hq_folder, lq_folder):
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

    def get_destination_path(prompt="Enter destination path: "):
        path = input(prompt)
        if not path:
            return None
        if not os.path.isdir(path):
            print(f"Path does not exist: {path}")
            return None
        return path

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
            cv_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if cv_img is None:
                pil_img = Image.open(image_path).convert("L")
                cv_img = np.array(pil_img)

            if cv_img is None:
                logging.error(
                    f"Failed to load image {image_path} with both OpenCV and PIL."
                )
                return None

            if cv_img.dtype != np.uint8:
                cv_img = cv2.normalize(cv_img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            return cv_img
        except Exception as e:
            logging.error(f"Exception loading image {image_path}: {e}")
            return None

    def compare_pair_phase_correlation(rel_path_tuple):
        rel_path, hq_abs_path, lq_abs_path = rel_path_tuple

        img1_gray = load_image_gray_cv(hq_abs_path)
        img2_gray = load_image_gray_cv(lq_abs_path)

        if img1_gray is None or img2_gray is None:
            return (rel_path, None, "error_loading_image")

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
            shift, _ = cv2.phaseCorrelate(img1_float, img2_float)
            alignment_score = np.linalg.norm(shift)
            return (rel_path, alignment_score, "ok")
        except cv2.error as cv2_e:
            logging.error(
                f"OpenCV error comparing {hq_abs_path} and {lq_abs_path}: {cv2_e}"
            )
            return (rel_path, None, f"error_phase_correlate_cv2: {cv2_e}")
        except Exception as e:
            logging.error(
                f"Generic error comparing {hq_abs_path} and {lq_abs_path}: {e}"
            )
            return (rel_path, None, f"error_phase_correlate: {e}")

    pairs_to_check = [
        (rel_path, hq_files_map[rel_path], lq_files_map[rel_path])
        for rel_path in common_rel_paths
    ]

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for result in tqdm(
            executor.map(compare_pair_phase_correlation, pairs_to_check),
            total=len(pairs_to_check),
            desc="Phase Correlation Alignment Check",
        ):
            results.append(result)

    misaligned = [
        (rel_path, score)
        for rel_path, score, status in results
        if status == "ok" and score is not None and score > threshold
    ]
    errors = [
        (rel_path, status) for rel_path, score, status in results if status != "ok"
    ]

    print(f"\nMisaligned pairs above threshold ({threshold}): {len(misaligned)}")
    for rel_path, score in misaligned[:5]:
        print(f"  - {rel_path}: alignment score {score:.4f}")
    if len(misaligned) > 5:
        print(f"  ... and {len(misaligned) - 5} more pairs.")

    if errors:
        print(f"\nPairs with errors: {len(errors)}")
        for rel_path, status in errors[:5]:
            print(f"  - {rel_path}: {status}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more pairs.")

    if action in ["move", "copy"] and misaligned:
        for rel_path, _ in misaligned:
            hq_src = hq_files_map[rel_path]
            lq_src = lq_files_map[rel_path]
            hq_dst = os.path.join(dest_hq_misaligned, os.path.basename(hq_src))
            lq_dst = os.path.join(dest_lq_misaligned, os.path.basename(lq_src))
            if action == "move":
                shutil.move(hq_src, hq_dst)
                shutil.move(lq_src, lq_dst)
            else:
                shutil.copy2(hq_src, hq_dst)
                shutil.copy2(lq_src, lq_dst)
        print(f"Misaligned pairs have been {action}d to destination folders.")

    print("-" * 30)
    print("=" * 30)
    return misaligned, errors


def find_alpha_channels(*args, **kwargs):
    """Find images with alpha channels in HQ/LQ datasets."""
    pass


def bhi_filtering(*args, **kwargs):
    """Perform BHI filtering (Blockiness, HyperIQA, IC9600) on a dataset."""
    pass


def test_aspect_ratio(hq_folder=None, lq_folder=None, single_path=None, tolerance=0.01):
    """
    Test aspect ratio for HQ/LQ folder pair, single folder, or single image.
    - If hq_folder and lq_folder are provided: compare aspect ratios for matching files.
    - If single_path is a folder: report aspect ratios for all images in the folder.
    - If single_path is a file: report aspect ratio for the image.
    """
    from dataset_forge.utils.file_utils import is_image_file
    from dataset_forge.image_ops import get_image_size
    from dataset_forge.utils.printing import (
        print_info,
        print_error,
        print_success,
        print_warning,
    )
    import os
    from tqdm import tqdm

    if hq_folder and lq_folder:
        # HQ/LQ folder pair mode
        print_info("\nTesting aspect ratios for HQ/LQ folder pair...")
        hq_files = {
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        }
        lq_files = {
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        }
        matching_files = sorted(hq_files & lq_files)
        mismatches = []
        for fname in tqdm(matching_files, desc="Comparing aspect ratios"):
            hq_path = os.path.join(hq_folder, fname)
            lq_path = os.path.join(lq_folder, fname)
            try:
                hq_w, hq_h = get_image_size(hq_path)
                lq_w, lq_h = get_image_size(lq_path)
                hq_aspect = hq_w / hq_h if hq_h != 0 else 0
                lq_aspect = lq_w / lq_h if lq_h != 0 else 0
                if abs(hq_aspect - lq_aspect) > tolerance:
                    mismatches.append((fname, hq_aspect, lq_aspect))
            except Exception as e:
                print_error(f"Failed to get aspect ratio for {fname}: {e}")
        print_info(f"\nChecked {len(matching_files)} HQ/LQ pairs.")
        if mismatches:
            print_warning(
                f"{len(mismatches)} pairs have mismatched aspect ratios (tolerance {tolerance}):"
            )
            for fname, hq_aspect, lq_aspect in mismatches[:10]:
                print_info(f"  {fname}: HQ {hq_aspect:.4f}, LQ {lq_aspect:.4f}")
            if len(mismatches) > 10:
                print_info(f"  ...and {len(mismatches)-10} more.")
        else:
            print_success("All HQ/LQ pairs have matching aspect ratios.")
        return
    if single_path:
        if os.path.isdir(single_path):
            # Single folder mode
            print_info(
                f"\nTesting aspect ratios for all images in folder: {single_path}"
            )
            files = [
                f
                for f in os.listdir(single_path)
                if os.path.isfile(os.path.join(single_path, f)) and is_image_file(f)
            ]
            aspects = []
            for fname in tqdm(files, desc="Calculating aspect ratios"):
                path = os.path.join(single_path, fname)
                try:
                    w, h = get_image_size(path)
                    aspect = w / h if h != 0 else 0
                    aspects.append((fname, aspect, w, h))
                except Exception as e:
                    print_error(f"Failed to get aspect ratio for {fname}: {e}")
            print_info(f"\nChecked {len(aspects)} images.")
            if aspects:
                aspect_counts = {}
                for _, aspect, _, _ in aspects:
                    rounded = round(aspect, 4)
                    aspect_counts[rounded] = aspect_counts.get(rounded, 0) + 1
                print_info("Aspect ratio distribution (rounded to 4 decimals):")
                for aspect, count in sorted(aspect_counts.items(), key=lambda x: -x[1]):
                    print_info(f"  {aspect}: {count} images")
                print_info("Examples:")
                for fname, aspect, w, h in aspects[:5]:
                    print_info(f"  {fname}: {w}x{h} (aspect {aspect:.4f})")
            return
        elif os.path.isfile(single_path):
            # Single image mode
            print_info(f"\nTesting aspect ratio for image: {single_path}")
            try:
                w, h = get_image_size(single_path)
                aspect = w / h if h != 0 else 0
                print_info(f"Image size: {w}x{h}")
                print_info(f"Aspect ratio: {aspect:.4f}")
            except Exception as e:
                print_error(f"Failed to get aspect ratio: {e}")
            return
        else:
            print_error(f"Path does not exist: {single_path}")
            return
    print_error(
        "You must provide either HQ/LQ folders or a single path (folder or image)."
    )


def progressive_dataset_validation(hq_folder, lq_folder):
    """
    Runs all relevant dataset checks (consistency, corruption, scale, etc.) and produces a single report.
    """
    from dataset_forge.utils.printing import (
        print_header,
        print_section,
        print_success,
        print_warning,
        print_error,
    )

    print_header("\n=== Progressive Dataset Validation ===")
    results = {}
    # 1. Scale Analysis
    print_section("\n[1/6] Scale Analysis")
    scale_results = find_hq_lq_scale(hq_folder, lq_folder, verbose=False)
    results["scale"] = scale_results
    # 2. Consistency Check
    print_section("\n[2/6] Consistency Check (HQ)")
    hq_consistency = check_consistency(hq_folder, "HQ", verbose=False)
    results["hq_consistency"] = hq_consistency
    print_section("\n[3/6] Consistency Check (LQ)")
    lq_consistency = check_consistency(lq_folder, "LQ", verbose=False)
    results["lq_consistency"] = lq_consistency
    # 3. Corruption Check
    print_section("\n[4/6] Corruption Check")
    corrupted = verify_images(hq_folder, lq_folder)
    results["corruption"] = corrupted
    # 4. Dimension Report
    print_section("\n[5/6] Dimension Report (HQ)")
    hq_dim = report_dimensions(hq_folder, "HQ", verbose=False)
    results["hq_dimensions"] = hq_dim
    print_section("\n[6/6] Dimension Report (LQ)")
    lq_dim = report_dimensions(lq_folder, "LQ", verbose=False)
    results["lq_dimensions"] = lq_dim
    print_success("\n=== Progressive Validation Complete ===")
    print_info = print_success  # Use green for summary
    print_info("\nSummary:")
    print_info(f"  HQ images: {len(hq_dim.get('dimensions', []))}")
    print_info(f"  LQ images: {len(lq_dim.get('dimensions', []))}")
    print_info(f"  Matching HQ/LQ pairs: {len(scale_results.get('scales', []))}")
    if scale_results.get("inconsistent_scales"):
        print_warning(
            f"  Inconsistent scales: {len(scale_results['inconsistent_scales'])}"
        )
    if corrupted:
        print_warning(f"  Corrupted/problematic images found: {len(corrupted)}")
    if hq_consistency.get("errors"):
        print_warning(
            f"  HQ files with processing errors: {len(hq_consistency['errors'])}"
        )
    if lq_consistency.get("errors"):
        print_warning(
            f"  LQ files with processing errors: {len(lq_consistency['errors'])}"
        )
    print_success("\nSee above for detailed results.")
    return results
