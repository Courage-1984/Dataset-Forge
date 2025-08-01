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
from concurrent.futures import ThreadPoolExecutor, as_completed
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
from dataset_forge.utils.audio_utils import play_done_sound


def process_single_image(
    input_path: str,
    dest_dir: str,
    output_format: str = "png",
    grayscale: bool = False,
    quality: int = 95,
    lossless: bool = True,
) -> bool:
    """
    Process a single image and save it with specified format and options.

    Args:
        input_path: Path to input image file
        dest_dir: Directory to save processed image
        output_format: Output format (png, jpg, webp, bmp, tiff)
        grayscale: Whether to convert to grayscale
        quality: JPEG/WebP quality (1-100, only used for lossy formats)
        lossless: Whether to use lossless compression (for PNG, WebP, TIFF)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read image
        image = cv2.imread(input_path)
        if image is None:
            print_error(f"Failed to read image: {input_path}")
            return False

        # Convert to grayscale if requested
        if grayscale:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Convert back to BGR for saving (OpenCV requirement)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Get filename without extension
        filename = os.path.splitext(os.path.basename(input_path))[0]

        # Create unique output filename
        output_filename = get_unique_filename(dest_dir, f"{filename}.{output_format}")
        output_path = os.path.join(dest_dir, output_filename)

        # Ensure output directory exists
        os.makedirs(dest_dir, exist_ok=True)

        # Set compression parameters based on format and lossless setting
        compression_params = []

        if output_format.lower() == "png":
            if lossless:
                # PNG lossless compression (level 6 for good balance)
                compression_params = [cv2.IMWRITE_PNG_COMPRESSION, 6]
            else:
                # PNG with minimal compression (still lossless)
                compression_params = [cv2.IMWRITE_PNG_COMPRESSION, 0]

        elif output_format.lower() == "jpg":
            # JPEG is always lossy, quality determines compression
            compression_params = [cv2.IMWRITE_JPEG_QUALITY, quality]

        elif output_format.lower() == "webp":
            if lossless:
                # WebP lossless
                compression_params = [cv2.IMWRITE_WEBP_QUALITY, 100]
            else:
                # WebP lossy with quality setting
                compression_params = [cv2.IMWRITE_WEBP_QUALITY, quality]

        elif output_format.lower() == "bmp":
            # BMP is always lossless, no compression
            compression_params = []

        elif output_format.lower() == "tiff":
            if lossless:
                # TIFF lossless with LZW compression
                compression_params = [cv2.IMWRITE_TIFF_COMPRESSION, 5]  # LZW
            else:
                # TIFF with JPEG compression (lossy)
                compression_params = [cv2.IMWRITE_TIFF_COMPRESSION, 7]  # JPEG

        # Save image with compression parameters
        success = cv2.imwrite(output_path, image, compression_params)

        if success:
            return True
        else:
            print_error(f"Failed to save: {output_filename}")
            return False

    except Exception as e:
        print_error(f"Error processing {input_path}: {e}")
        return False


def process_with_params(
    input_path, dest_dir, output_format, grayscale, quality, lossless
):
    """Process a single image with the given parameters."""
    return process_single_image(
        input_path, dest_dir, output_format, grayscale, quality, lossless
    )


@monitor_all("resave_images", critical_on_error=True)
@auto_cleanup
def resave_images(
    input_dir: str,
    dest_dir: str,
    output_format: str = "png",
    grayscale: bool = False,
    recursive: bool = False,
    quality: int = 95,
    lossless: bool = True,
    supported_formats: Optional[List[str]] = None,
) -> Tuple[int, int, int]:
    """
    Resave images from input directory to output directory with specified format.

    This function processes images in parallel, converting them to the specified
    output format with optional grayscale conversion and compression control.

    Args:
        input_dir: Directory containing input images
        dest_dir: Directory to save processed images
        output_format: Output format (png, jpg, webp, bmp, tiff)
        grayscale: Whether to convert images to grayscale
        recursive: Whether to process subdirectories
        quality: JPEG/WebP quality (1-100, only used for lossy formats)
        lossless: Whether to use lossless compression (for PNG, WebP, TIFF)
        supported_formats: List of supported image formats to process

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
        quality=quality,
        lossless=lossless,
    )
    results = []
    max_workers = min(2, parallel_config.get("max_workers", 4) or 4)

    # Process images with real-time progress tracking
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_path = {
            executor.submit(process_func, input_path): input_path
            for input_path in input_paths
        }

        # Process results with progress bar
        for future in tqdm(
            as_completed(future_to_path),
            total=len(input_paths),
            desc=f"Resaving images to {output_format.upper()}",
            unit="img",
        ):
            result = future.result()
            results.append(result)

    # Count results
    processed = sum(1 for result in results if result)
    failed = len(results) - processed

    # Log operation completion
    log_operation(
        "resave_images",
        f"Completed: {processed}/{len(input_paths)} images processed to {output_format.upper()}",
    )

    # Print summary
    print_success(f"✅ Successfully processed: {processed} images")
    if failed > 0:
        print_warning(f"⚠️ Failed to process: {failed} images")

    return processed, 0, failed


def resave_images_workflow(
    input_dir: Optional[str] = None,
    dest_dir: Optional[str] = None,
    output_format: str = "png",
    grayscale: bool = False,
    recursive: bool = False,
    quality: int = 95,
    lossless: bool = True,
) -> None:
    """
    Interactive workflow for resaving images with format conversion and compression control.

    This workflow prompts the user for input/output directories and processing options,
    then calls the resave_images function to process the images.

    Args:
        input_dir: Optional input directory (if not provided, will prompt user)
        dest_dir: Optional output directory (if not provided, will prompt user)
        output_format: Output format (png, jpg, webp, bmp, tiff)
        grayscale: Whether to convert to grayscale
        recursive: Whether to process subdirectories
        quality: JPEG/WebP quality (1-100, only used for lossy formats)
        lossless: Whether to use lossless compression (for PNG, WebP, TIFF)
    """
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_header, print_section, print_prompt
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.monitoring import time_and_record_menu_load

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

        # Get processing options
        print_header("🔄 Resave Images - Processing Options", color=Mocha.blue)

        # Get output format
        format_choice = (
            input("Output format (png/jpg/webp/bmp/tiff) [default: png]: ")
            .strip()
            .lower()
        )
        if format_choice:
            output_format = format_choice

        # Get quality setting for lossy formats
        if output_format.lower() in ["jpg", "webp"]:
            quality_input = input(f"Quality (1-100) [default: {quality}]: ").strip()
            if quality_input:
                try:
                    quality = int(quality_input)
                    if quality < 1 or quality > 100:
                        print_warning("Quality must be between 1-100, using default")
                        quality = 95
                except ValueError:
                    print_warning("Invalid quality value, using default")
                    quality = 95

        # Get lossless setting for formats that support it
        if output_format.lower() in ["png", "webp", "tiff"]:
            lossless_input = (
                input("Use lossless compression? (y/n) [default: y]: ").strip().lower()
            )
            if lossless_input:
                lossless = lossless_input in ["y", "yes", "1", "true"]

        # Get grayscale option
        grayscale_input = (
            input("Convert to grayscale? (y/n) [default: n]: ").strip().lower()
        )
        if grayscale_input:
            grayscale = grayscale_input in ["y", "yes", "1", "true"]

        # Get recursive option
        recursive_input = (
            input("Process subdirectories? (y/n) [default: n]: ").strip().lower()
        )
        if recursive_input:
            recursive = recursive_input in ["y", "yes", "1", "true"]

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
        # Call the main resave function
        processed, skipped, failed = resave_images(
            input_dir=input_dir,
            dest_dir=dest_dir,
            output_format=output_format,
            grayscale=grayscale,
            recursive=recursive,
            quality=quality,
            lossless=lossless,
        )

        # Show results
        print_section("Results Summary")
        print_success(f"✅ Successfully processed: {processed} images")
        if skipped > 0:
            print_warning(f"⚠️ Skipped: {skipped} images")
        if failed > 0:
            print_error(f"❌ Failed: {failed} images")

        print_success("Image resaving workflow complete!")
        play_done_sound()
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
                key = show_menu(
                    "🔄 Resave Images",
                    options,
                    Mocha.lavender,
                )
                if key is None or key == "0":
                    return
                action = options[key][1]
                if callable(action):
                    action()
            except (KeyboardInterrupt, EOFError):
                print_info("\nExiting...")
                break
            except Exception as e:
                print_error(f"Menu error: {e}")
                break

    resave_images_menu_internal()
