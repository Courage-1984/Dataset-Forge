import os
import logging
import numpy as np
from PIL import Image
from dataset_forge.utils.progress_utils import tqdm, image_map, smart_map
from dataset_forge.utils.parallel_utils import (
    parallel_image_processing,
    ProcessingType,
    ParallelConfig,
    setup_parallel_environment,
)
from dataset_forge.menus.session_state import parallel_config, user_preferences
from dataset_forge.utils.io_utils import is_image_file
from collections import Counter
import cv2
import shutil
import concurrent.futures
from dataset_forge.actions.analysis_ops_actions import (
    ScaleAnalyzer,
    DimensionAnalyzer,
    ConsistencyAnalyzer,
)
from dataset_forge.utils.image_ops import get_image_size
from dataset_forge.utils.monitoring import monitor_all
from dataset_forge.utils.cache_utils import in_memory_cache
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.printing import (
    print_info, print_success, print_warning, print_error,
    print_header, print_section
)
from dataset_forge.utils.color import Mocha


@monitor_all("analyze_single_image")
@in_memory_cache(maxsize=128)
def analyze_single_image(image_path: str) -> dict:
    """
    Analyze a single image and return its properties. (In-memory cached)
    Args:
        image_path: Path to the image file
    Returns:
        dict: Image properties including dimensions, format, mode, etc.
    Note:
        This function is cached in-memory for fast repeated analysis of the same file in a session.
    """
    try:
        with Image.open(image_path) as img:
            return {
                "path": image_path,
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": os.path.getsize(image_path),
                "success": True,
            }
    except Exception as e:
        return {"path": image_path, "error": str(e), "success": False}


@monitor_all("analyze_image_batch")
def analyze_image_batch(image_paths: list) -> list:
    """
    Analyze a batch of images in parallel.

    Args:
        image_paths: List of image file paths

    Returns:
        list: List of analysis results
    """
    return [analyze_single_image(path) for path in image_paths]


@monitor_all("generate_hq_lq_dataset_report", critical_on_error=True)
def generate_hq_lq_dataset_report(hq_folder, lq_folder):
    print_header("HQ/LQ DATASET REPORT", char="=", color=Mocha.sapphire)
    print_section("Overall Dataset Information", char="-", color=Mocha.lavender)
    
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
        print_error(f"Error: One of the dataset folders not found: {fnf_e}")
        print_warning("Please ensure HQ and LQ folders are correctly set.")
        print_header("", char="=", color=Mocha.sapphire)
        return

    matching_pairs_list = [
        f for f in hq_files_list if f in lq_files_list
    ]  # Ensure it's a list for len

    print_info(f"HQ Folder: {hq_folder}")
    print_info(f"LQ Folder: {lq_folder}")
    print_info(f"Total HQ Images (root): {len(hq_files_list)}")
    print_info(f"Total LQ Images (root): {len(lq_files_list)}")
    print_info(f"Matching HQ/LQ Pairs (based on root filenames): {len(matching_pairs_list)}")

    hq_unique_files = [f for f in hq_files_list if f not in lq_files_list]
    lq_unique_files = [f for f in lq_files_list if f not in hq_files_list]
    print_info(f"Images unique to HQ folder (root): {len(hq_unique_files)}")
    if hq_unique_files and len(hq_unique_files) <= 5:
        print_info(f"  ({', '.join(hq_unique_files)})")
    elif hq_unique_files:
        print_info(f"  (e.g., {', '.join(hq_unique_files[:3])} ...)")

    print_info(f"Images unique to LQ folder (root): {len(lq_unique_files)}")
    if lq_unique_files and len(lq_unique_files) <= 5:
        print_info(f"  ({', '.join(lq_unique_files)})")
    elif lq_unique_files:
        print_info(f"  (e.g., {', '.join(lq_unique_files[:3])} ...)")

    print_section("Scale Analysis (based on root filenames)", char="-", color=Mocha.lavender)
    scale_results = find_hq_lq_scale(
        hq_folder, lq_folder, verbose=False
    )  # verbose=False for report summary
    if scale_results["scales"]:
        scale_counts = Counter(scale_results["scales"])
        most_common_scale = scale_counts.most_common(1)[0]
        print_info(
            f"Most common consistent scale: {most_common_scale[0]:.2f} (occurred {most_common_scale[1]} times out of {scale_results['processed_pairs']} pairs)"
        )
        other_scales = scale_counts.most_common()[1:6]  # Show up to 5 other scales
        if other_scales:
            print_info("Other consistent scales found:")
            for s, c in other_scales:
                print_info(f"  - {s:.2f} ({c} times)")
    else:
        print_warning("No consistent scales found among processed pairs.")
    if scale_results["inconsistent_scales"]:
        print_warning(
            f"Pairs with inconsistent width/height scales or processing errors: {len(scale_results['inconsistent_scales'])}"
        )
    if scale_results["missing_lq"]:
        print_warning(
            f"HQ files missing corresponding LQ file: {len(scale_results['missing_lq'])}"
        )
    if scale_results["missing_hq"]:
        print_warning(
            f"LQ files missing corresponding HQ file: {len(scale_results['missing_hq'])}"
        )

    print_section("Consistency Check (HQ)", char="-", color=Mocha.lavender)
    hq_consistency = check_consistency(hq_folder, "HQ", verbose=False)
    if hq_consistency["formats"]:
        print_info(
            f"HQ File Formats: {{ {k: len(v) for k, v in hq_consistency['formats'].items()} }}"
        )
    else:
        print_warning("HQ File Formats: No image files found or processed.")
    if hq_consistency["modes"]:
        print_info(
            f"HQ Color Modes: {{ {k: len(v) for k, v in hq_consistency['modes'].items()} }}"
        )
    else:
        print_warning("HQ Color Modes: No image files found or processed.")
    if hq_consistency["errors"]:
        print_warning(f"HQ files with processing errors: {len(hq_consistency['errors'])}")

    print_section("Consistency Check (LQ)", char="-", color=Mocha.lavender)
    lq_consistency = check_consistency(lq_folder, "LQ", verbose=False)
    if lq_consistency["formats"]:
        print_info(
            f"LQ File Formats: {{ {k: len(v) for k, v in lq_consistency['formats'].items()} }}"
        )
    else:
        print_warning("LQ File Formats: No image files found or processed.")
    if lq_consistency["modes"]:
        print_info(
            f"LQ Color Modes: {{ {k: len(v) for k, v in lq_consistency['modes'].items()} }}"
        )
    else:
        print_warning("LQ Color Modes: No image files found or processed.")
    if lq_consistency["errors"]:
        print_warning(f"LQ files with processing errors: {len(lq_consistency['errors'])}")

    print_section("Dimension Report (HQ)", char="-", color=Mocha.lavender)
    hq_dimensions_report = report_dimensions(hq_folder, "HQ", verbose=False)
    if hq_dimensions_report["dimensions"]:
        hq_widths = [dim[0] for dim in hq_dimensions_report["dimensions"]]
        hq_heights = [dim[1] for dim in hq_dimensions_report["dimensions"]]
        print_info(
            f"HQ Width (processed {len(hq_widths)} images): Min={min(hq_widths)}, Max={max(hq_widths)}, Avg={sum(hq_widths)/len(hq_widths):.2f}"
        )
        print_info(
            f"HQ Height (processed {len(hq_heights)} images): Min={min(hq_heights)}, Max={max(hq_heights)}, Avg={sum(hq_heights)/len(hq_heights):.2f}"
        )
        unique_dims_hq = sorted(list(set(hq_dimensions_report["dimensions"])))
        print_info(
            f"HQ Unique Dimensions (WxH): {len(unique_dims_hq)}. Examples: {unique_dims_hq[:min(3, len(unique_dims_hq))]}"
        )

    else:
        print_warning("HQ Dimensions: No images successfully processed for dimensions.")
    if hq_dimensions_report["errors"]:
        print_warning(f"HQ dimension processing errors: {len(hq_dimensions_report['errors'])}")

    print_section("Dimension Report (LQ)", char="-", color=Mocha.lavender)
    lq_dimensions_report = report_dimensions(lq_folder, "LQ", verbose=False)
    if lq_dimensions_report["dimensions"]:
        lq_widths = [dim[0] for dim in lq_dimensions_report["dimensions"]]
        lq_heights = [dim[1] for dim in lq_dimensions_report["dimensions"]]
        print_info(
            f"LQ Width (processed {len(lq_widths)} images): Min={min(lq_widths)}, Max={max(lq_widths)}, Avg={sum(lq_widths)/len(lq_widths):.2f}"
        )
        print_info(
            f"LQ Height (processed {len(lq_heights)} images): Min={min(lq_heights)}, Max={max(lq_heights)}, Avg={sum(lq_heights)/len(lq_heights):.2f}"
        )
        unique_dims_lq = sorted(list(set(lq_dimensions_report["dimensions"])))
        print_info(
            f"LQ Unique Dimensions (WxH): {len(unique_dims_lq)}. Examples: {unique_dims_lq[:min(3, len(unique_dims_lq))]}"
        )

    else:
        print_warning("LQ Dimensions: No images successfully processed for dimensions.")
    if lq_dimensions_report["errors"]:
        print_warning(f"LQ dimension processing errors: {len(lq_dimensions_report['errors'])}")

    print_section("Extreme Dimensions (HQ)", char="-", color=Mocha.lavender)
    hq_extreme_dims = find_extreme_dimensions(hq_folder, "HQ", verbose=False)
    if hq_extreme_dims["successfully_processed"] > 0:
        bd_hq = hq_extreme_dims["biggest_dimension"]
        sd_hq = hq_extreme_dims["smallest_dimension"]
        bf_hq = hq_extreme_dims["biggest_files"]
        sf_hq = hq_extreme_dims["smallest_files"]
        print_info(
            f"HQ Biggest Dimension (pixels): {bd_hq[0]}x{bd_hq[1]} (Area: {bd_hq[0]*bd_hq[1]})"
        )
        if bf_hq:
            print_info(f"  Files: {', '.join(bf_hq[:2])}{'...' if len(bf_hq) > 2 else ''}")
        print_info(
            f"HQ Smallest Dimension (pixels): {sd_hq[0]}x{sd_hq[1]} (Area: {sd_hq[0]*sd_hq[1]})"
        )
        if sf_hq:
            print_info(f"  Files: {', '.join(sf_hq[:2])}{'...' if len(sf_hq) > 2 else ''}")
    else:
        print_warning("HQ Extreme Dimensions: No images successfully processed.")
    if hq_extreme_dims["errors"]:
        print_warning(
            f"HQ extreme dimension processing errors: {len(hq_extreme_dims['errors'])}"
        )

    print_section("Extreme Dimensions (LQ)", char="-", color=Mocha.lavender)
    lq_extreme_dims = find_extreme_dimensions(lq_folder, "LQ", verbose=False)
    if lq_extreme_dims["successfully_processed"] > 0:
        bd_lq = lq_extreme_dims["biggest_dimension"]
        sd_lq = lq_extreme_dims["smallest_dimension"]
        bf_lq = lq_extreme_dims["biggest_files"]
        sf_lq = lq_extreme_dims["smallest_files"]
        print_info(
            f"LQ Biggest Dimension (pixels): {bd_lq[0]}x{bd_lq[1]} (Area: {bd_lq[0]*bd_lq[1]})"
        )
        if bf_lq:
            print_info(f"  Files: {', '.join(bf_lq[:2])}{'...' if len(bf_lq) > 2 else ''}")
        print_info(
            f"LQ Smallest Dimension (pixels): {sd_lq[0]}x{sd_lq[1]} (Area: {sd_lq[0]*sd_lq[1]})"
        )
        if sf_lq:
            print_info(f"  Files: {', '.join(sf_lq[:2])}{'...' if len(sf_lq) > 2 else ''}")
    else:
        print_warning("LQ Extreme Dimensions: No images successfully processed.")
    if lq_extreme_dims["errors"]:
        print_warning(
            f"LQ extreme dimension processing errors: {len(lq_extreme_dims['errors'])}"
        )

    print_section("File Size Analysis", char="-", color=Mocha.lavender)
    hq_size_report = analyze_file_sizes(hq_folder, "HQ", verbose=False)
    lq_size_report = analyze_file_sizes(lq_folder, "LQ", verbose=False)

    if hq_size_report["sizes"]:
        hq_sizes = hq_size_report["sizes"]
        print_info(
            f"HQ File Sizes: Min={min(hq_sizes):.2f}MB, Max={max(hq_sizes):.2f}MB, Avg={sum(hq_sizes)/len(hq_sizes):.2f}MB"
        )

    if lq_size_report["sizes"]:
        lq_sizes = lq_size_report["sizes"]
        print_info(
            f"LQ File Sizes: Min={min(lq_sizes):.2f}MB, Max={max(lq_sizes):.2f}MB, Avg={sum(lq_sizes)/len(lq_sizes):.2f}MB"
        )

    print_header("", char="=", color=Mocha.sapphire)
    print_success("HQ/LQ dataset report generation complete!")
    play_done_sound()


def find_hq_lq_scale(hq_folder, lq_folder, verbose=True):
    """Find HQ/LQ scale relationships with parallel processing."""
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    matching_files = sorted(hq_files & lq_files)

    if not matching_files:
        return {
            "scales": [],
            "processed_pairs": 0,
            "inconsistent_scales": [],
            "missing_lq": [],
            "missing_hq": [],
        }

    def analyze_pair(filename):
        """Analyze a single HQ/LQ pair."""
        try:
            hq_path = os.path.join(hq_folder, filename)
            lq_path = os.path.join(lq_folder, filename)

            hq_width, hq_height = get_image_size(hq_path)
            lq_width, lq_height = get_image_size(lq_path)

            if hq_width and lq_width and hq_height and lq_height:
                width_scale = hq_width / lq_width
                height_scale = hq_height / lq_height

                # Check if scales are consistent (within 1% tolerance)
                if abs(width_scale - height_scale) / width_scale < 0.01:
                    return {"success": True, "scale": width_scale, "filename": filename}
                else:
                    return {
                        "success": False,
                        "inconsistent": True,
                        "filename": filename,
                    }
            else:
                return {
                    "success": False,
                    "error": "Could not read dimensions",
                    "filename": filename,
                }
        except Exception as e:
            return {"success": False, "error": str(e), "filename": filename}

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # I/O bound task
        use_gpu=False,
    )

    # Process pairs in parallel
    results = smart_map(
        analyze_pair,
        matching_files,
        desc="Analyzing HQ/LQ scales",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    scales = []
    inconsistent_scales = []
    errors = []

    for result in results:
        if result["success"]:
            scales.append(result["scale"])
        elif result.get("inconsistent"):
            inconsistent_scales.append(result["filename"])
        else:
            errors.append(result["filename"])

    return {
        "scales": scales,
        "processed_pairs": len(matching_files),
        "inconsistent_scales": inconsistent_scales,
        "missing_lq": list(hq_files - lq_files),
        "missing_hq": list(lq_files - hq_files),
    }


def test_hq_lq_scale(hq_folder, lq_folder):
    """Test HQ/LQ scale relationships with parallel processing."""
    scale_results = find_hq_lq_scale(hq_folder, lq_folder, verbose=True)

    if scale_results["scales"]:
        print_section("Scale Analysis Results", char="-", color=Mocha.lavender)
        print_info(f"Processed pairs: {scale_results['processed_pairs']}")
        print_info(f"Consistent scales found: {len(scale_results['scales'])}")

        if scale_results["scales"]:
            scale_counts = Counter(scale_results["scales"])
            print_info("Most common scales:")
            for scale, count in scale_counts.most_common(5):
                print_info(f"  {scale:.2f}x: {count} pairs")

        if scale_results["inconsistent_scales"]:
            print_warning(
                f"Inconsistent scales: {len(scale_results['inconsistent_scales'])} pairs"
            )
            for filename in scale_results["inconsistent_scales"][:5]:
                print_warning(f"  {filename}")
            if len(scale_results["inconsistent_scales"]) > 5:
                print_warning(f"  ... and {len(scale_results['inconsistent_scales']) - 5} more")

    if scale_results["missing_lq"]:
        print_warning(f"HQ files missing LQ: {len(scale_results['missing_lq'])}")
    if scale_results["missing_hq"]:
        print_warning(f"LQ files missing HQ: {len(scale_results['missing_hq'])}")
    
    print_success("HQ/LQ scale analysis complete!")
    play_done_sound()


def check_consistency(folder_path, folder_name, verbose=True):
    """Check dataset consistency with parallel processing."""
    image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]

    if not image_files:
        return {"formats": {}, "modes": {}, "errors": []}

    def analyze_image(filename):
        """Analyze a single image for consistency."""
        try:
            image_path = os.path.join(folder_path, filename)
            with Image.open(image_path) as img:
                return {
                    "success": True,
                    "format": img.format,
                    "mode": img.mode,
                    "filename": filename,
                }
        except Exception as e:
            return {"success": False, "error": str(e), "filename": filename}

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    # Process images in parallel
    results = smart_map(
        analyze_image,
        image_files,
        desc=f"Checking {folder_name} consistency",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    formats = {}
    modes = {}
    errors = []

    for result in results:
        if result["success"]:
            format_key = result["format"] or "Unknown"
            mode_key = result["mode"] or "Unknown"

            if format_key not in formats:
                formats[format_key] = []
            formats[format_key].append(result["filename"])

            if mode_key not in modes:
                modes[mode_key] = []
            modes[mode_key].append(result["filename"])
        else:
            errors.append(result["filename"])

    return {"formats": formats, "modes": modes, "errors": errors}


def report_dimensions(folder_path, folder_name, verbose=True):
    """Report image dimensions with parallel processing."""
    image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]

    if not image_files:
        return {"dimensions": [], "errors": []}

    def get_dimensions(filename):
        """Get dimensions of a single image."""
        try:
            image_path = os.path.join(folder_path, filename)
            width, height = get_image_size(image_path)
            if width and height:
                return {
                    "success": True,
                    "dimensions": (width, height),
                    "filename": filename,
                }
            else:
                return {
                    "success": False,
                    "error": "Could not read dimensions",
                    "filename": filename,
                }
        except Exception as e:
            return {"success": False, "error": str(e), "filename": filename}

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    # Process images in parallel
    results = smart_map(
        get_dimensions,
        image_files,
        desc=f"Getting {folder_name} dimensions",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    dimensions = []
    errors = []

    for result in results:
        if result["success"]:
            dimensions.append(result["dimensions"])
        else:
            errors.append(result["filename"])

    return {"dimensions": dimensions, "errors": errors}


def find_extreme_dimensions(folder_path, folder_name, verbose=True):
    """Find extreme dimensions with parallel processing."""
    dimension_results = report_dimensions(folder_path, folder_name, verbose=False)

    if not dimension_results["dimensions"]:
        return {
            "successfully_processed": 0,
            "biggest_dimension": (0, 0),
            "smallest_dimension": (0, 0),
            "biggest_files": [],
            "smallest_files": [],
            "errors": dimension_results["errors"],
        }

    # Find extreme dimensions
    dimensions = dimension_results["dimensions"]
    areas = [w * h for w, h in dimensions]

    max_area_idx = areas.index(max(areas))
    min_area_idx = areas.index(min(areas))

    biggest_dimension = dimensions[max_area_idx]
    smallest_dimension = dimensions[min_area_idx]

    # Find files with these dimensions
    image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]

    def find_files_with_dimension(target_dim):
        """Find files with specific dimensions."""
        matching_files = []
        for filename in image_files:
            try:
                image_path = os.path.join(folder_path, filename)
                width, height = get_image_size(image_path)
                if width == target_dim[0] and height == target_dim[1]:
                    matching_files.append(filename)
            except:
                continue
        return matching_files

    # Setup parallel processing for finding files
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    biggest_files = find_files_with_dimension(biggest_dimension)
    smallest_files = find_files_with_dimension(smallest_dimension)

    return {
        "successfully_processed": len(dimension_results["dimensions"]),
        "biggest_dimension": biggest_dimension,
        "smallest_dimension": smallest_dimension,
        "biggest_files": biggest_files,
        "smallest_files": smallest_files,
        "errors": dimension_results["errors"],
    }


def analyze_file_sizes(folder_path, folder_name, verbose=True):
    """Analyze file sizes with parallel processing."""
    image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]

    if not image_files:
        return {"sizes": [], "errors": []}

    def get_file_size(filename):
        """Get file size of a single image."""
        try:
            image_path = os.path.join(folder_path, filename)
            size_bytes = os.path.getsize(image_path)
            size_mb = size_bytes / (1024 * 1024)  # Convert to MB
            return {"success": True, "size_mb": size_mb, "filename": filename}
        except Exception as e:
            return {"success": False, "error": str(e), "filename": filename}

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    # Process files in parallel
    results = smart_map(
        get_file_size,
        image_files,
        desc=f"Analyzing {folder_name} file sizes",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    sizes = []
    errors = []

    for result in results:
        if result["success"]:
            sizes.append(result["size_mb"])
        else:
            errors.append(result["filename"])

    return {"sizes": sizes, "errors": errors}


# Keep existing functions that don't need parallel processing
@monitor_all("verify_images", critical_on_error=True)
def verify_images(hq_folder, lq_folder):
    """Verify image integrity with parallel processing."""
    hq_files = [f for f in os.listdir(hq_folder) if is_image_file(f)]
    lq_files = [f for f in os.listdir(lq_folder) if is_image_file(f)]

    all_files = []
    for filename in hq_files:
        all_files.append(("hq", os.path.join(hq_folder, filename)))
    for filename in lq_files:
        all_files.append(("lq", os.path.join(lq_folder, filename)))

    def verify_single_image(file_info):
        """Verify a single image."""
        folder_type, file_path = file_info
        try:
            with Image.open(file_path) as img:
                img.verify()
            return {"success": True, "folder": folder_type, "path": file_path}
        except Exception as e:
            return {
                "success": False,
                "folder": folder_type,
                "path": file_path,
                "error": str(e),
            }

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    # Process images in parallel
    results = smart_map(
        verify_single_image,
        all_files,
        desc="Verifying images",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    hq_errors = []
    lq_errors = []
    successful = 0

    for result in results:
        if result["success"]:
            successful += 1
        else:
            if result["folder"] == "hq":
                hq_errors.append(result["path"])
            else:
                lq_errors.append(result["path"])

    print_section("Image verification complete", char="-", color=Mocha.lavender)
    print_info(f"  Successful: {successful}")
    print_info(f"  HQ errors: {len(hq_errors)}")
    print_info(f"  LQ errors: {len(lq_errors)}")

    if hq_errors:
        print_warning("HQ errors:")
        for error in hq_errors[:5]:
            print_warning(f"  {error}")
        if len(hq_errors) > 5:
            print_warning(f"  ... and {len(hq_errors) - 5} more")

    if lq_errors:
        print_warning("LQ errors:")
        for error in lq_errors[:5]:
            print_warning(f"  {error}")
        if len(lq_errors) > 5:
            print_warning(f"  ... and {len(lq_errors) - 5} more")


@monitor_all("fix_corrupted_images", critical_on_error=True)
def fix_corrupted_images(*args, **kwargs):
    """Redirect to corruption actions."""
    from dataset_forge.actions.corruption_actions import (
        fix_corrupted_images as fix_corrupted,
    )

    return fix_corrupted(*args, **kwargs)


def find_misaligned_images(hq_folder, lq_folder):
    """Find misaligned image pairs with parallel processing."""
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    matching_files = sorted(hq_files & lq_files)

    if not matching_files:
        print_warning("No matching files found.")
        return

    def check_alignment(filename):
        """Check alignment of a single pair."""
        try:
            hq_path = os.path.join(hq_folder, filename)
            lq_path = os.path.join(lq_folder, filename)

            hq_width, hq_height = get_image_size(hq_path)
            lq_width, lq_height = get_image_size(lq_path)

            if hq_width and lq_width and hq_height and lq_height:
                width_scale = hq_width / lq_width
                height_scale = hq_height / lq_height

                # Check if scales are consistent (within 1% tolerance)
                if abs(width_scale - height_scale) / width_scale < 0.01:
                    return {"aligned": True, "filename": filename}
                else:
                    return {
                        "aligned": False,
                        "filename": filename,
                        "width_scale": width_scale,
                        "height_scale": height_scale,
                    }
            else:
                return {
                    "aligned": False,
                    "filename": filename,
                    "error": "Could not read dimensions",
                }
        except Exception as e:
            return {"aligned": False, "filename": filename, "error": str(e)}

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    # Process pairs in parallel
    results = smart_map(
        check_alignment,
        matching_files,
        desc="Checking alignment",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    aligned = []
    misaligned = []

    for result in results:
        if result["aligned"]:
            aligned.append(result["filename"])
        else:
            misaligned.append(result)

    print_section("Alignment check complete", char="-", color=Mocha.lavender)
    print_info(f"  Aligned pairs: {len(aligned)}")
    print_info(f"  Misaligned pairs: {len(misaligned)}")

    if misaligned:
        print_warning("Misaligned pairs:")
        for item in misaligned[:5]:
            print_warning(f"  {item['filename']}")
            if "width_scale" in item:
                print_warning(
                    f"    Width scale: {item['width_scale']:.2f}, Height scale: {item['height_scale']:.2f}"
                )
            if "error" in item:
                print_warning(f"    Error: {item['error']}")
        if len(misaligned) > 5:
            print_warning(f"  ... and {len(misaligned) - 5} more")


def find_alpha_channels(*args, **kwargs):
    """Redirect to alpha actions."""
    from dataset_forge.actions.alpha_actions import find_alpha_channels as find_alpha

    return find_alpha(*args, **kwargs)


def bhi_filtering(*args, **kwargs):
    """Redirect to BHI filtering actions with enhanced functionality."""
    from dataset_forge.actions.bhi_filtering_actions import (
        run_bhi_filtering as bhi_filter,
        run_bhi_filtering_with_preset,
        run_bhi_filtering_with_defaults,
        get_bhi_preset_thresholds,
        get_default_bhi_thresholds,
    )

    # Check if preset is specified
    preset = kwargs.pop("preset", None)
    if preset:
        return run_bhi_filtering_with_preset(*args, preset_name=preset, **kwargs)

    # Check if thresholds are provided
    thresholds = kwargs.get("thresholds", None)
    if thresholds is None:
        # Use defaults if no thresholds provided
        return run_bhi_filtering_with_defaults(*args, **kwargs)

    # Use provided thresholds
    return bhi_filter(*args, **kwargs)


def test_aspect_ratio(hq_folder=None, lq_folder=None, single_path=None, tolerance=0.01):
    """Test aspect ratio consistency with parallel processing."""
    if single_path:
        folders = [single_path]
        folder_names = ["Single"]
    elif hq_folder and lq_folder:
        folders = [hq_folder, lq_folder]
        folder_names = ["HQ", "LQ"]
    else:
        print_error("Please provide either single_path or both hq_folder and lq_folder.")
        return

    def analyze_aspect_ratios(folder_info):
        """Analyze aspect ratios for a single folder."""
        folder_path, folder_name = folder_info
        image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]

        if not image_files:
            return {"folder": folder_name, "aspects": [], "errors": []}

        def get_aspect_ratio(filename):
            """Get aspect ratio of a single image."""
            try:
                image_path = os.path.join(folder_path, filename)
                width, height = get_image_size(image_path)
                if width and height:
                    aspect = width / height
                    return {"success": True, "aspect": aspect, "filename": filename}
                else:
                    return {
                        "success": False,
                        "error": "Could not read dimensions",
                        "filename": filename,
                    }
            except Exception as e:
                return {"success": False, "error": str(e), "filename": filename}

        # Setup parallel processing
        config = ParallelConfig(
            max_workers=parallel_config.get("max_workers"),
            processing_type=ProcessingType.THREAD,
            use_gpu=False,
        )

        # Process images in parallel
        results = smart_map(
            get_aspect_ratio,
            image_files,
            desc=f"Analyzing {folder_name} aspect ratios",
            max_workers=config.max_workers,
            processing_type=ProcessingType.THREAD,
        )

        aspects = []
        errors = []

        for result in results:
            if result["success"]:
                aspects.append(result["aspect"])
            else:
                errors.append(result["filename"])

        return {"folder": folder_name, "aspects": aspects, "errors": errors}

    # Setup parallel processing for folders
    config = ParallelConfig(
        max_workers=len(folders), processing_type=ProcessingType.THREAD, use_gpu=False
    )

    # Process folders in parallel
    folder_results = smart_map(
        analyze_aspect_ratios,
        list(zip(folders, folder_names)),
        desc="Analyzing aspect ratios",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    for result in folder_results:
        folder_name = result["folder"]
        aspects = result["aspects"]
        errors = result["errors"]

        if aspects:
            print_section(f"{folder_name} Aspect Ratios", char="-", color=Mocha.lavender)
            print_info(f"  Count: {len(aspects)}")
            print_info(f"  Min: {min(aspects):.3f}")
            print_info(f"  Max: {max(aspects):.3f}")
            print_info(f"  Mean: {sum(aspects)/len(aspects):.3f}")
            print_info(f"  Std: {np.std(aspects):.3f}")

            # Check for consistency
            mean_aspect = sum(aspects) / len(aspects)
            consistent = [
                a for a in aspects if abs(a - mean_aspect) / mean_aspect < tolerance
            ]
            print_info(
                f"  Consistent (within {tolerance*100}%): {len(consistent)}/{len(aspects)}"
            )

        if errors:
            print_warning(f"  Errors: {len(errors)}")


@monitor_all("progressive_dataset_validation", critical_on_error=True)
def progressive_dataset_validation(hq_folder, lq_folder):
    """Run progressive dataset validation with parallel processing."""
    print_header("Starting progressive dataset validation...", color=Mocha.lavender)

    # Step 1: Basic file count and matching
    print_section("1. Basic file analysis", char="-", color=Mocha.lavender)
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    matching_files = hq_files & lq_files

    print_info(f"   HQ files: {len(hq_files)}")
    print_info(f"   LQ files: {len(lq_files)}")
    print_info(f"   Matching pairs: {len(matching_files)}")

    if len(matching_files) == 0:
        print_error("   ERROR: No matching files found!")
        return

    # Step 2: Image integrity check
    print_section("2. Image integrity check", char="-", color=Mocha.lavender)
    verify_images(hq_folder, lq_folder)

    # Step 3: Scale analysis
    print_section("3. Scale analysis", char="-", color=Mocha.lavender)
    scale_results = find_hq_lq_scale(hq_folder, lq_folder, verbose=False)
    if scale_results["scales"]:
        scale_counts = Counter(scale_results["scales"])
        most_common_scale = scale_counts.most_common(1)[0]
        print_info(
            f"   Most common scale: {most_common_scale[0]:.2f}x ({most_common_scale[1]} pairs)"
        )

    # Step 4: Dimension analysis
    print_section("4. Dimension analysis", char="-", color=Mocha.lavender)
    hq_dims = report_dimensions(hq_folder, "HQ", verbose=False)
    lq_dims = report_dimensions(lq_folder, "LQ", verbose=False)

    if hq_dims["dimensions"]:
        hq_areas = [w * h for w, h in hq_dims["dimensions"]]
        print_info(
            f"   HQ: {len(hq_dims['dimensions'])} images, avg area: {sum(hq_areas)/len(hq_areas):.0f} pixels"
        )

    if lq_dims["dimensions"]:
        lq_areas = [w * h for w, h in lq_dims["dimensions"]]
        print_info(
            f"   LQ: {len(lq_dims['dimensions'])} images, avg area: {sum(lq_areas)/len(lq_areas):.0f} pixels"
        )

    # Step 5: Consistency check
    print_section("5. Consistency check", char="-", color=Mocha.lavender)
    hq_consistency = check_consistency(hq_folder, "HQ", verbose=False)
    lq_consistency = check_consistency(lq_folder, "LQ", verbose=False)

    print_info(f"   HQ formats: {len(hq_consistency['formats'])}")
    print_info(f"   LQ formats: {len(lq_consistency['formats'])}")

    print_success("\nProgressive validation complete!")
