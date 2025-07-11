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


class AlphaAnalyzer:
    @staticmethod
    def find_alpha_channels(hq_folder=None, lq_folder=None, single_folder=None):
        """Find images with alpha channels in folders. Supports both single folder and HQ/LQ pair workflows."""
        print("\n" + "=" * 30)
        print("  Finding Images with Alpha Channels")
        print("=" * 30)

        def check_alpha_in_folder(folder_path, folder_name):
            images_with_alpha = []
            errors = []

            # Collect all image files recursively
            image_files = []
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    if is_image_file(filename):
                        # Get relative path from the root folder
                        rel_path = os.path.relpath(
                            os.path.join(root, filename), folder_path
                        )
                        image_files.append((rel_path, os.path.join(root, filename)))

            for rel_path, full_path in tqdm(
                image_files, desc=f"Checking {folder_name} (recursively)"
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
            print("Error: Invalid folder configuration.")
            return None

        results = {}
        for folder_path, folder_name in folders_to_check:
            alpha_images, errors = check_alpha_in_folder(folder_path, folder_name)
            results[f"{folder_name.lower()}_alpha"] = alpha_images
            results[f"{folder_name.lower()}_errors"] = errors

        print("\n" + "-" * 30)
        print("  Alpha Channel Analysis Summary")
        print("-" * 30)
        print(f"Workflow: {workflow_type.upper()}")

        if workflow_type == "paired":
            hq_alpha_images = results.get("hq_alpha", [])
            lq_alpha_images = results.get("lq_alpha", [])
            hq_errors = results.get("hq_errors", [])
            lq_errors = results.get("lq_errors", [])

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
                    print(
                        f"  ... and {len(hq_errors) + len(lq_errors) - 5} more errors"
                    )
        else:
            single_alpha_images = results.get("single_alpha", [])
            single_errors = results.get("single_errors", [])

            print(f"\nSingle Folder Results:")
            print(f"Found {len(single_alpha_images)} images with alpha channels")
            if single_alpha_images:
                print("\nExample files with alpha:")
                for f in single_alpha_images[:5]:
                    print(f"  - {f}")
                if len(single_alpha_images) > 5:
                    print(f"  ... and {len(single_alpha_images) - 5} more")

            if single_errors:
                print("\nErrors encountered:")
                for filename, error in single_errors[:5]:
                    print(f"  - {filename}: {error}")
                if len(single_errors) > 5:
                    print(f"  ... and {len(single_errors) - 5} more errors")

        print("-" * 30)
        print("=" * 30)

        return results


def find_alpha_channels(hq_folder=None, lq_folder=None, single_folder=None):
    return AlphaAnalyzer.find_alpha_channels(
        hq_folder=hq_folder, lq_folder=lq_folder, single_folder=single_folder
    )


def find_alpha_channels_menu():
    """Menu for finding alpha channels with workflow choice."""
    print("\n=== Find Images with Alpha Channels ===")
    print("Choose input mode:")
    print("  1. HQ/LQ paired folders")
    print("  2. Single folder")
    print("  0. Cancel")

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
            print("Error: Both HQ and LQ paths are required.")
            return

        if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
            print("Error: Both HQ and LQ paths must be valid directories.")
            return

        find_alpha_channels(hq_folder=hq_folder, lq_folder=lq_folder)

    elif choice == "2":
        # Single folder workflow
        single_folder = get_path_with_history(
            "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
        )

        if not single_folder:
            print("Error: Folder path is required.")
            return

        if not os.path.isdir(single_folder):
            print("Error: Folder path must be a valid directory.")
            return

        find_alpha_channels(single_folder=single_folder)

    elif choice == "0":
        print("Operation cancelled.")
        return

    else:
        print("Invalid choice. Operation cancelled.")


def remove_alpha_channels(hq_folder, lq_folder):
    """Remove alpha channels from images in HQ/LQ folders using AlphaRemover class."""
    print("\n" + "=" * 30)
    print("  Removing Alpha Channels")
    print("=" * 30)

    alpha_results = AlphaAnalyzer.find_alpha_channels(hq_folder, lq_folder)
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
