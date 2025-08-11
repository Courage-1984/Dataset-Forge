import os
from dataset_forge.utils.io_utils import is_image_file
from PIL import Image
import shutil
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.input_utils import (
    get_file_operation_choice,
    get_destination_path,
    get_path_with_history,
)
from dataset_forge.utils.file_utils import get_unique_filename
from dataset_forge.utils.image_ops import AlphaRemover
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import (
    print_success,
    print_info,
    print_error,
    print_header,
    print_section,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.audio_utils import play_done_sound


class AlphaAnalyzer:
    @staticmethod
    def find_alpha_channels(hq_folder=None, lq_folder=None, single_folder=None):
        """Find images with alpha channels in folders. Supports both single folder and HQ/LQ pair workflows."""
        print_header("Finding Images with Alpha Channels")

        def check_alpha_in_folder(folder_path, folder_name):
            images_with_alpha = []
            errors = []

            # Collect all image files recursively with progress bar
            image_files = []
            total_files = 0

            # First, count total files for progress bar
            for root, dirs, files in os.walk(folder_path):
                total_files += len(files)

            # Now collect image files with progress bar
            with tqdm(
                total=total_files,
                desc=f"Discovering images in {folder_name}",
                unit="files",
            ) as pbar:
                for root, dirs, files in os.walk(folder_path):
                    for filename in files:
                        pbar.update(1)
                        if is_image_file(filename):
                            # Get relative path from the root folder
                            rel_path = os.path.relpath(
                                os.path.join(root, filename), folder_path
                            )
                            image_files.append((rel_path, os.path.join(root, filename)))

            # Check alpha channels with progress bar
            for rel_path, full_path in tqdm(
                image_files, desc=f"Checking {folder_name} for alpha channels"
            ):
                try:
                    with Image.open(full_path) as img:
                        if img.mode in ("RGBA", "LA") or (
                            img.mode == "P" and "transparency" in img.info
                        ):
                            images_with_alpha.append(rel_path)
                except Exception as e:
                    errors.append((rel_path, str(e)))

            return images_with_alpha, errors

        # Determine workflow type
        if single_folder:
            # Single folder workflow
            workflow_type = "single"
            folders_to_check = [(single_folder, "Single")]
        elif hq_folder and lq_folder:
            # HQ/LQ pair workflow
            workflow_type = "paired"
            folders_to_check = [(hq_folder, "HQ"), (lq_folder, "LQ")]
        else:
            print_error("Invalid folder configuration.")
            return None

        results = {}
        for folder_path, folder_name in folders_to_check:
            alpha_images, errors = check_alpha_in_folder(folder_path, folder_name)
            results[f"{folder_name.lower()}_alpha"] = alpha_images
            results[f"{folder_name.lower()}_errors"] = errors

        print_section("Alpha Channel Analysis Summary")
        print_info(f"Workflow: {workflow_type.upper()}")

        if workflow_type == "paired":
            hq_alpha_images = results.get("hq_alpha", [])
            lq_alpha_images = results.get("lq_alpha", [])
            hq_errors = results.get("hq_errors", [])
            lq_errors = results.get("lq_errors", [])

            print_info(f"\nHQ Folder Results:")
            print_info(f"Found {len(hq_alpha_images)} images with alpha channels")
            if hq_alpha_images:
                print_info("\nExample HQ files with alpha:")
                for f in hq_alpha_images[:5]:
                    print_info(f"  - {f}")
                if len(hq_alpha_images) > 5:
                    print_info(f"  ... and {len(hq_alpha_images) - 5} more")

            print_info(f"\nLQ Folder Results:")
            print_info(f"Found {len(lq_alpha_images)} images with alpha channels")
            if lq_alpha_images:
                print_info("\nExample LQ files with alpha:")
                for f in lq_alpha_images[:5]:
                    print_info(f"  - {f}")
                if len(lq_alpha_images) > 5:
                    print_info(f"  ... and {len(lq_alpha_images) - 5} more")

            if hq_errors or lq_errors:
                print_error("\nErrors encountered:")
                for filename, error in (hq_errors + lq_errors)[:5]:
                    print_error(f"  - {filename}: {error}")
                if len(hq_errors) + len(lq_errors) > 5:
                    print_error(
                        f"  ... and {len(hq_errors) + len(lq_errors) - 5} more errors"
                    )
        else:
            single_alpha_images = results.get("single_alpha", [])
            single_errors = results.get("single_errors", [])

            print_info(f"\nSingle Folder Results:")
            print_info(f"Found {len(single_alpha_images)} images with alpha channels")
            if single_alpha_images:
                print_info("\nExample files with alpha:")
                for f in single_alpha_images[:5]:
                    print_info(f"  - {f}")
                if len(single_alpha_images) > 5:
                    print_info(f"  ... and {len(single_alpha_images) - 5} more")

            if single_errors:
                print_error("\nErrors encountered:")
                for filename, error in single_errors[:5]:
                    print_error(f"  - {filename}: {error}")
                if len(single_errors) > 5:
                    print_error(f"  ... and {len(single_errors) - 5} more errors")

        print_section("Analysis Complete")

        # Play completion sound
        play_done_sound()

        return results


def find_alpha_channels(hq_folder=None, lq_folder=None, single_folder=None):
    return AlphaAnalyzer.find_alpha_channels(
        hq_folder=hq_folder, lq_folder=lq_folder, single_folder=single_folder
    )


def find_alpha_channels_menu():
    """Menu for finding alpha channels with workflow choice."""
    print_header("Find Images with Alpha Channels")
    print_info("Choose input mode:")
    print_info("  1. HQ/LQ paired folders")
    print_info("  2. Single folder")
    print_info("  0. Cancel")

    choice = input("Select mode: ").strip()

    if choice == "1":
        # HQ/LQ pair workflow
        hq_folder = get_path_with_history(
            "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq_folder = get_path_with_history(
            "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )

        if not hq_folder or not lq_folder:
            print_error("Both HQ and LQ paths are required.")
            return

        if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
            print_error("Both HQ and LQ paths must be valid directories.")
            return

        find_alpha_channels(hq_folder=hq_folder, lq_folder=lq_folder)

    elif choice == "2":
        # Single folder workflow
        single_folder = get_path_with_history(
            "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
        )

        if not single_folder:
            print_error("Folder path is required.")
            return

        if not os.path.isdir(single_folder):
            print_error("Folder path must be a valid directory.")
            return

        find_alpha_channels(single_folder=single_folder)

    elif choice == "0":
        print_info("Operation cancelled.")
        return

    else:
        print_error("Invalid choice. Operation cancelled.")


def remove_alpha_channels(hq_folder, lq_folder):
    """Remove alpha channels from images in HQ/LQ folders using AlphaRemover class."""
    print_header("Removing Alpha Channels")

    alpha_results = AlphaAnalyzer.find_alpha_channels(hq_folder, lq_folder)
    if not (alpha_results["hq_alpha"] or alpha_results["lq_alpha"]):
        print_info("\nNo images with alpha channels found to process.")
        return

    operation = get_file_operation_choice()
    destination = ""
    if operation != "inplace":
        destination = get_destination_path()
        if not destination:
            print_error(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)

    remover = AlphaRemover()
    processed_count = 0
    errors = []

    for rel_path in tqdm(alpha_results["hq_alpha"], desc="Processing HQ Images"):
        src_path = os.path.join(hq_folder, rel_path)

        # For copy/move operations, preserve directory structure
        if operation == "inplace":
            dest_path = src_path
        else:
            if os.path.dirname(rel_path):
                # Create subdirectories in destination
                subdir = os.path.join(destination, "hq", os.path.dirname(rel_path))
                os.makedirs(subdir, exist_ok=True)
                dest_path = os.path.join(subdir, os.path.basename(rel_path))
            else:
                dest_path = os.path.join(destination, "hq", rel_path)

        try:
            success, msg = remover.process(
                src_path, output_path=dest_path, operation=operation
            )
            if success:
                processed_count += 1
            else:
                errors.append(f"Failed to process HQ: {rel_path} ({msg})")
        except Exception as e:
            errors.append(f"Error processing HQ {rel_path}: {e}")

    for rel_path in tqdm(alpha_results["lq_alpha"], desc="Processing LQ Images"):
        src_path = os.path.join(lq_folder, rel_path)

        # For copy/move operations, preserve directory structure
        if operation == "inplace":
            dest_path = src_path
        else:
            if os.path.dirname(rel_path):
                # Create subdirectories in destination
                subdir = os.path.join(destination, "lq", os.path.dirname(rel_path))
                os.makedirs(subdir, exist_ok=True)
                dest_path = os.path.join(subdir, os.path.basename(rel_path))
            else:
                dest_path = os.path.join(destination, "lq", rel_path)

        try:
            success, msg = remover.process(
                src_path, output_path=dest_path, operation=operation
            )
            if success:
                processed_count += 1
            else:
                errors.append(f"Failed to process LQ: {rel_path} ({msg})")
        except Exception as e:
            errors.append(f"Error processing LQ {rel_path}: {e}")

    print_section("Remove Alpha Channels Summary")
    print_success(f"Successfully processed: {processed_count} images")
    if errors:
        print_error(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print_error(f"  - {error}")
        if len(errors) > 5:
            print_error(f"  ... and {len(errors) - 5} more errors")
    print_section("Operation Complete")

    # Play completion sound
    play_done_sound()


def remove_alpha_channels_menu():
    """
    Menu for removing alpha channels from images (recursive version).

    This function provides a user interface for removing alpha channels
    from images in a folder, converting RGBA to RGB, with recursive processing.
    """
    from dataset_forge.utils.input_utils import (
        get_file_operation_choice,
        get_destination_path,
        get_path_with_history,
    )
    from dataset_forge.utils.printing import (
        print_header,
        print_info,
        print_error,
        print_success,
    )
    from dataset_forge.utils.color import Mocha

    print_header("Remove Alpha Channels (Recursive)", color=Mocha.lavender)
    print_info(
        "This tool removes alpha channels from images, converting RGBA to RGB.\n"
        "It processes all subdirectories recursively.\n"
    )

    # Get input folder
    input_folder = get_path_with_history(
        "Enter path to input folder:", allow_hq_lq=True, allow_single_folder=True
    )
    if not input_folder or not os.path.isdir(input_folder):
        print_error("Input path must be a valid directory.")
        return

    # Get operation type
    operation = get_file_operation_choice()

    # Get destination directory if needed
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path("Enter destination folder: ")
        if not dest_dir:
            print_error("Operation aborted as destination path was not provided.")
            return
        os.makedirs(dest_dir, exist_ok=True)

    # Find all images with alpha channels recursively
    print_info("Scanning for images with alpha channels (recursively)...")
    alpha_results = AlphaAnalyzer.find_alpha_channels(single_folder=input_folder)
    image_files_with_alpha = alpha_results.get("single_alpha", [])

    if not image_files_with_alpha:
        print_info("No images with alpha channels found in the input folder.")
        return

    print_info(
        f"\nFound {len(image_files_with_alpha)} images with alpha channels to process."
    )

    # Setup parallel processing
    from dataset_forge.utils.parallel_utils import ParallelConfig, ProcessingType
    from dataset_forge.menus import session_state

    config = ParallelConfig(
        max_workers=session_state.parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    @monitor_all("remove_alpha_channel", critical_on_error=True)
    def remove_alpha_channel(image_file):
        """Remove alpha channel from a single image."""
        try:
            input_path = os.path.join(input_folder, image_file)

            if operation == "inplace":
                output_path = input_path
            else:
                # Preserve directory structure in destination
                if os.path.dirname(image_file):
                    # Create subdirectories in destination
                    subdir = os.path.join(dest_dir, os.path.dirname(image_file))
                    os.makedirs(subdir, exist_ok=True)
                    output_path = os.path.join(subdir, os.path.basename(image_file))
                else:
                    output_path = os.path.join(dest_dir, image_file)

            with Image.open(input_path) as img:
                # Check if image has alpha channel
                if img.mode in ("RGBA", "LA", "PA"):
                    # Convert to RGB or L (grayscale)
                    if img.mode == "RGBA":
                        # Create white background
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(
                            img, mask=img.split()[-1]
                        )  # Use alpha channel as mask
                        img_rgb = background
                    elif img.mode == "LA":
                        # Convert to grayscale
                        img_rgb = img.convert("L")
                    else:  # PA
                        img_rgb = img.convert("RGB")
                else:
                    # No alpha channel, just copy
                    img_rgb = img

                # Save image
                if operation == "inplace":
                    img_rgb.save(input_path)
                else:
                    img_rgb.save(output_path)

            return True

        except Exception as e:
            print_error(f"Failed to remove alpha channel from {image_file}: {e}")
            return False

    # Process images in parallel
    from dataset_forge.utils.parallel_utils import parallel_image_processing

    results = parallel_image_processing(
        remove_alpha_channel,
        image_files_with_alpha,
        desc="Removing alpha channels",
        max_workers=config.max_workers,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print_success(f"\nAlpha channel removal complete:")
    print_info(f"  Successful images: {successful}")
    print_info(f"  Failed images: {failed}")
    print_info(f"  Operation: {operation}")
    if operation != "inplace":
        print_info(f"  Destination: {dest_dir}")

    # Log operation
    from dataset_forge.utils.history_log import log_operation

    log_operation(
        "remove_alpha_channels",
        f"{operation}, {successful}/{len(image_files_with_alpha)} images (recursive)",
    )

    # Play completion sound
    play_done_sound()
