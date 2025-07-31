"""
Resave Images Actions

This module provides functionality to resave images in different formats with optional
grayscale conversion, following the Dataset Forge patterns for memory management,
parallel processing, and error handling.
"""

import os
import cv2
from typing import List, Optional, Tuple
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from dataset_forge.utils.memory_utils import auto_cleanup
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.file_utils import get_unique_filename, is_image_file
from dataset_forge.utils.monitoring import monitor_all
from dataset_forge.menus.session_state import parallel_config


def process_single_image(
    input_path: str, dest_dir: str, output_format: str = "png", grayscale: bool = False
) -> bool:
    """
    Process a single image by resaving it in the specified format.

    Args:
        input_path: Path to the input image file
        dest_dir: Directory to save the processed image
        output_format: Output format (png, jpg, jpeg, etc.)
        grayscale: Whether to convert to grayscale

    Returns:
        True if processing was successful, False otherwise

    Raises:
        FileNotFoundError: If input file doesn't exist
        PermissionError: If output directory is not writable
        ValueError: If image file is corrupted or unsupported
    """
    try:
        # Read the image
        image = cv2.imread(input_path)

        if image is None:
            print_error(f"Failed to read image: {input_path}")
            return False

        # Convert the image to grayscale if specified
        if grayscale:
            if len(image.shape) == 3:  # Color image
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # If already grayscale, no conversion needed

        # Get the base name of the file and split it to get the file name and extension
        filename_only = os.path.basename(input_path)
        file_name, _ = os.path.splitext(filename_only)

        # Create the output path with the specified format
        output_filename = f"{file_name}.{output_format.lower()}"

        # Ensure unique filename
        output_filename = get_unique_filename(dest_dir, output_filename)
        output_path = os.path.join(dest_dir, output_filename)

        # Determine compression parameters based on format
        compression_params = []
        if output_format.lower() in ["jpg", "jpeg"]:
            compression_params = [cv2.IMWRITE_JPEG_QUALITY, 95]
        elif output_format.lower() == "png":
            compression_params = [cv2.IMWRITE_PNG_COMPRESSION, 6]
        elif output_format.lower() == "webp":
            compression_params = [cv2.IMWRITE_WEBP_QUALITY, 95]

        # Write the image to the output path
        success = cv2.imwrite(output_path, image, compression_params)

        if not success:
            print_error(f"Failed to write image: {output_path}")
            return False

        return True

    except Exception as e:
        print_error(f"Error processing {input_path}: {e}")
        return False


def process_with_params(input_path, dest_dir, output_format, grayscale):
    """Process a single image with the given parameters."""
    return process_single_image(input_path, dest_dir, output_format, grayscale)


@monitor_all("resave_images", critical_on_error=True)
@auto_cleanup
def resave_images(
    input_dir: str,
    dest_dir: str,
    output_format: str = "png",
    grayscale: bool = False,
    recursive: bool = False,
    supported_formats: Optional[List[str]] = None,
) -> Tuple[int, int, int]:
    """
    Resave images from input directory to output directory with specified format.

    This function processes images in parallel, converting them to the specified
    output format with optional grayscale conversion. It uses the Dataset Forge
    parallel processing system for optimal performance.

    Args:
        input_dir: Directory containing the input images
        dest_dir: Directory to store the output images
        output_format: Output format (png, jpg, jpeg, webp, etc.)
        grayscale: Whether to convert images to grayscale
        recursive: Whether to process subdirectories recursively
        supported_formats: List of supported input formats (default: all image formats)

    Returns:
        Tuple of (processed_count, skipped_count, failed_count)

    Raises:
        FileNotFoundError: If input directory doesn't exist
        PermissionError: If output directory is not writable
        ValueError: If output format is not supported
    """
    # Validate input directory
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    if not os.path.isdir(input_dir):
        raise ValueError(f"Input path is not a directory: {input_dir}")

    # Create output directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Validate output format
    supported_output_formats = ["png", "jpg", "jpeg", "webp", "bmp", "tiff"]
    if output_format.lower() not in supported_output_formats:
        raise ValueError(f"Unsupported output format: {output_format}")

    # Set default supported input formats if not specified
    if supported_formats is None:
        supported_formats = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]

    # Collect input image paths
    input_paths = []

    if recursive:
        for root, _, files in os.walk(input_dir):
            for file in files:
                if any(file.lower().endswith(fmt) for fmt in supported_formats):
                    input_paths.append(os.path.join(root, file))
    else:
        with os.scandir(input_dir) as entries:
            for entry in entries:
                if entry.is_file() and any(
                    entry.name.lower().endswith(fmt) for fmt in supported_formats
                ):
                    input_paths.append(entry.path)

    if not input_paths:
        print_warning(f"No supported image files found in: {input_dir}")
        return 0, 0, 0

    print_info(f"Found {len(input_paths)} images to process")
    print_info(f"Output format: {output_format.upper()}")
    if grayscale:
        print_info("Converting to grayscale")

    # Process images in parallel with reduced workers to avoid memory issues
    process_func = partial(
        process_with_params,
        dest_dir=dest_dir,
        output_format=output_format,
        grayscale=grayscale,
    )
    results = []
    max_workers = min(2, parallel_config.get("max_workers", 4) or 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for input_path in tqdm(
            input_paths, desc=f"Resaving images to {output_format.upper()}"
        ):
            results.append(executor.submit(process_func, input_path))

    # Count results
    processed = sum(1 for result in results if result.result())
    failed = len(input_paths) - processed
    skipped = 0  # No skipping in this implementation

    # Log operation
    log_operation(
        "resave_images",
        f"Processed {processed}/{len(input_paths)} images to {output_format.upper()}",
    )

    # Print summary
    print_success(f"Resaving complete: {processed} processed, {failed} failed")

    return processed, skipped, failed


def resave_images_workflow(
    input_dir: Optional[str] = None,
    dest_dir: Optional[str] = None,
    output_format: str = "png",
    grayscale: bool = False,
    recursive: bool = False,
) -> None:
    """
    Interactive workflow for resaving images.

    This function provides an interactive interface for the resave images functionality,
    allowing users to specify input/output directories and processing options.

    Args:
        input_dir: Optional input directory path
        dest_dir: Optional output directory path
        output_format: Output format for resaved images
        grayscale: Whether to convert to grayscale
        recursive: Whether to process subdirectories recursively
    """
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_header, print_section, print_prompt

    print_header("🔄 Resave Images Workflow")

    # Get input directory
    if input_dir is None:
        print_section("Input Directory")
        input_dir = get_folder_path("Select input directory containing images:")
        if not input_dir:
            print_warning("No input directory selected. Exiting workflow.")
            return

    # Get output directory
    if dest_dir is None:
        print_section("Output Directory")
        dest_dir = get_folder_path("Select output directory for resaved images:")
        if not dest_dir:
            print_warning("No output directory selected. Exiting workflow.")
            return

            # Get output format
    if (
        input_dir is None and dest_dir is None
    ):  # Only ask for format if no parameters provided
        print_section("Output Format")
        format_options = {
            "1": ("PNG", "png"),
            "2": ("JPEG", "jpg"),
            "3": ("WebP", "webp"),
            "4": ("BMP", "bmp"),
            "5": ("TIFF", "tiff"),
        }

        print_info("Select output format:")
        for key, (name, fmt) in format_options.items():
            print_info(f"  {key}. {name} (.{fmt})")

        while True:
            choice = input("\nEnter your choice (1-5): ").strip()
            if choice in format_options:
                output_format = format_options[choice][1]
                break
            else:
                print_error("Invalid choice. Please enter 1-5.")

    # Get processing options
    if (
        input_dir is None and dest_dir is None
    ):  # Only ask for options if no parameters provided
        print_section("Processing Options")

        # Grayscale option
        grayscale_choice = input("Convert images to grayscale? (y/N): ").strip().lower()
        grayscale = grayscale_choice in ["y", "yes"]

        # Recursive option
        recursive_choice = (
            input("Process subdirectories recursively? (y/N): ").strip().lower()
        )
        recursive = recursive_choice in ["y", "yes"]

    # Confirm and process
    print_section("Processing Summary")
    print_info(f"Input directory: {input_dir}")
    print_info(f"Output directory: {dest_dir}")
    print_info(f"Output format: {output_format.upper()}")
    print_info(f"Grayscale: {'Yes' if grayscale else 'No'}")
    print_info(f"Recursive: {'Yes' if recursive else 'No'}")

    confirm = input("\nProceed with resaving? (Y/n): ").strip().lower()
    if confirm in ["n", "no"]:
        print_info("Operation cancelled.")
        return

    try:
        # Process images
        processed, skipped, failed = resave_images(
            input_dir=input_dir,
            dest_dir=dest_dir,
            output_format=output_format,
            grayscale=grayscale,
            recursive=recursive,
        )

        # Show results
        print_section("Results Summary")
        print_success(f"✅ Successfully processed: {processed} images")
        if skipped > 0:
            print_warning(f"⚠️ Skipped: {skipped} images")
        if failed > 0:
            print_error(f"❌ Failed: {failed} images")

        print_prompt("Press Enter to return to the menu...")

    except Exception as e:
        print_error(f"Error during resaving: {e}")
        log_operation("resave_images", f"Failed: {e}")
        print_prompt("Press Enter to return to the menu...")


def resave_images_menu():
    """
    Menu for resave images functionality.

    This function provides a menu interface for accessing the resave images
    functionality with different options and workflows.
    """
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.monitoring import time_and_record_menu_load

    @time_and_record_menu_load("resave_images_menu")
    def resave_images_menu_internal():
        options = {
            "1": ("🔄 Resave Images (Interactive)", lambda: resave_images_workflow()),
            "2": (
                "📁 Resave Single Folder",
                lambda: resave_images_workflow(recursive=False),
            ),
            "3": (
                "📂 Resave with Recursion",
                lambda: resave_images_workflow(recursive=True),
            ),
            "4": (
                "⚫ Convert to Grayscale",
                lambda: resave_images_workflow(grayscale=True),
            ),
            "0": ("🚪 Back", None),
        }

        while True:
            try:
                action = show_menu("🔄 Resave Images", options, Mocha.lavender)
                if action is None:
                    break
                action()
            except (KeyboardInterrupt, EOFError):
                print_info("\nExiting...")
                break
            except Exception as e:
                print_error(f"Menu error: {e}")
                break

    resave_images_menu_internal()
