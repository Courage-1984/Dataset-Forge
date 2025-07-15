from dataset_forge.utils.input_utils import get_folder_path, get_path_with_history
from dataset_forge.utils.printing import (
    print_info,
    print_error,
    print_success,
    print_warning,
    print_header,
)
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
import os


def imagededup_menu():
    """Menu for imagededup operations."""

    def single_folder_dedup():
        """Handle single folder deduplication."""
        from dataset_forge.actions.imagededup_actions import imagededup_workflow

        print_header("Single Folder Deduplication")

        # Get folder path
        folder = get_folder_path("Enter folder path: ")

        # Get hash method
        print("\nHash methods:")
        print("1. PHash (Perceptual Hash) - Recommended")
        print("2. DHash (Difference Hash)")
        print("3. AHash (Average Hash)")
        print("4. WHash (Wavelet Hash)")

        hash_choice = input("Select hash method [1]: ").strip() or "1"
        hash_methods = {"1": "phash", "2": "dhash", "3": "ahash", "4": "whash"}
        hash_method = hash_methods.get(hash_choice, "phash")

        # Get threshold
        try:
            threshold = int(input("Max distance threshold [10]: ").strip() or "10")
        except ValueError:
            threshold = 10

            # Get operation
        print("\nOperations:")
        print("1. Find duplicates (show only)")
        print("2. Remove duplicates")
        print("3. Move duplicates to separate folder")
        print("4. Generate duplicate report")
        print("5. Debug directory contents")

        op_choice = input("Select operation [1]: ").strip() or "1"
        operations = {
            "1": "find",
            "2": "remove",
            "3": "move",
            "4": "report",
            "5": "debug",
        }
        operation = operations.get(op_choice, "find")

        # Get additional parameters based on operation
        destination_dir = None
        output_file = None
        dry_run = True

        if operation == "find":
            save_results = (
                input("Save results to file? (y/n) [n]: ").strip().lower() or "n"
            )
            if save_results == "y":
                output_file = input("Enter output file path: ").strip()

        elif operation in ["remove", "move"]:
            confirm = (
                input("This will permanently modify files. Continue? (y/n) [n]: ")
                .strip()
                .lower()
                or "n"
            )
            if confirm == "y":
                dry_run = False
            else:
                print_warning("Operation cancelled.")
                return

        if operation == "move":
            destination_dir = get_folder_path(
                "Enter destination folder for duplicates: "
            )

        elif operation == "report":
            destination_dir = input(
                "Enter report output directory (leave blank for default): "
            ).strip()
            if not destination_dir:
                destination_dir = None
        elif operation == "debug":
            # Debug operation doesn't need additional parameters
            pass

        # Run the operation
        try:
            if operation == "debug":
                # Handle debug operation separately
                from dataset_forge.actions.imagededup_actions import ImageDedupHandler

                handler = ImageDedupHandler(hash_method)
                handler.debug_directory_contents(folder)
                return
            else:
                result = imagededup_workflow(
                    image_dir=folder,
                    operation=operation,
                    hash_method=hash_method,
                    max_distance_threshold=threshold,
                    destination_dir=destination_dir,
                    output_file=output_file,
                    dry_run=dry_run,
                )

            if operation == "find":
                duplicates = result.get("duplicates", {})
                total_duplicates = sum(len(dups) for dups in duplicates.values())
                print_success(
                    f"Found {len(duplicates)} duplicate groups with {total_duplicates} total duplicate files."
                )

                if duplicates:
                    print("\nDuplicate groups:")
                    for i, (original, dups) in enumerate(duplicates.items(), 1):
                        print(f"\nGroup {i}:")
                        print(f"  Original: {original}")
                        print(f"  Duplicates ({len(dups)}):")
                        for dup in dups:
                            print(f"    - {dup}")

        except Exception as e:
            print_error(f"Error during deduplication: {e}")

    def hq_lq_dedup():
        """Handle HQ/LQ paired dataset deduplication."""
        from dataset_forge.actions.imagededup_actions import imagededup_hq_lq_workflow

        print_header("HQ/LQ Paired Dataset Deduplication")

        # Get folder paths
        hq_folder = get_folder_path("Enter HQ folder path: ")
        lq_folder = get_folder_path("Enter LQ folder path: ")

        # Get hash method
        print("\nHash methods:")
        print("1. PHash (Perceptual Hash) - Recommended")
        print("2. DHash (Difference Hash)")
        print("3. AHash (Average Hash)")
        print("4. WHash (Wavelet Hash)")

        hash_choice = input("Select hash method [1]: ").strip() or "1"
        hash_methods = {"1": "phash", "2": "dhash", "3": "ahash", "4": "whash"}
        hash_method = hash_methods.get(hash_choice, "phash")

        # Get threshold
        try:
            threshold = int(input("Max distance threshold [10]: ").strip() or "10")
        except ValueError:
            threshold = 10

        # Get operation
        print("\nOperations:")
        print("1. Find duplicates (show only)")
        print("2. Remove duplicates")
        print("3. Move duplicates to separate folder")

        op_choice = input("Select operation [1]: ").strip() or "1"
        operations = {"1": "find", "2": "remove", "3": "move"}
        operation = operations.get(op_choice, "find")

        # Get additional parameters based on operation
        destination_dir = None
        dry_run = True

        if operation in ["remove", "move"]:
            confirm = (
                input("This will permanently modify files. Continue? (y/n) [n]: ")
                .strip()
                .lower()
                or "n"
            )
            if confirm == "y":
                dry_run = False
            else:
                print_warning("Operation cancelled.")
                return

        if operation == "move":
            destination_dir = get_folder_path(
                "Enter destination folder for duplicates: "
            )

        # Run the operation
        try:
            result = imagededup_hq_lq_workflow(
                hq_dir=hq_folder,
                lq_dir=lq_folder,
                operation=operation,
                hash_method=hash_method,
                max_distance_threshold=threshold,
                destination_dir=destination_dir,
                dry_run=dry_run,
            )

            if operation == "find":
                hq_duplicates = result.get("hq_duplicates", {})
                lq_duplicates = result.get("lq_duplicates", {})

                total_hq_duplicates = sum(len(dups) for dups in hq_duplicates.values())
                total_lq_duplicates = sum(len(dups) for dups in lq_duplicates.values())

                print_success(
                    f"Found {len(hq_duplicates)} duplicate groups with {total_hq_duplicates} HQ and {total_lq_duplicates} LQ duplicate files."
                )

                if hq_duplicates:
                    print("\nDuplicate groups:")
                    for i, (hq_original, hq_dups) in enumerate(
                        hq_duplicates.items(), 1
                    ):
                        print(f"\nGroup {i}:")
                        print(f"  HQ Original: {hq_original}")
                        print(f"  HQ Duplicates ({len(hq_dups)}):")
                        for hq_dup in hq_dups:
                            print(f"    - {hq_dup}")

                        # Show corresponding LQ duplicates
                        lq_original = os.path.join(
                            lq_folder, os.path.basename(hq_original)
                        )
                        if lq_original in lq_duplicates:
                            lq_dups = lq_duplicates[lq_original]
                            print(f"  LQ Duplicates ({len(lq_dups)}):")
                            for lq_dup in lq_dups:
                                print(f"    - {lq_dup}")

        except Exception as e:
            print_error(f"Error during HQ/LQ deduplication: {e}")

    def about_imagededup():
        """Show information about imagededup."""
        print_header("About ImageDedup")
        print_info(
            "ImageDedup is a Python library that provides functionality to find duplicate images in a given directory."
        )
        print_info(
            "It uses perceptual hashing algorithms to detect duplicate and near-duplicate images."
        )
        print_info("\nSupported hash methods:")
        print_info(
            "- PHash (Perceptual Hash): Most accurate, recommended for most use cases"
        )
        print_info("- DHash (Difference Hash): Faster than PHash, good accuracy")
        print_info("- AHash (Average Hash): Fastest, less accurate")
        print_info("- WHash (Wavelet Hash): Good balance of speed and accuracy")
        print_info("\nGitHub: https://github.com/idealo/imagededup")
        print_info("Documentation: https://idealo.github.io/imagededup/")

    options = {
        "1": ("Single Folder Deduplication", single_folder_dedup),
        "2": ("HQ/LQ Paired Dataset Deduplication", hq_lq_dedup),
        "3": ("About ImageDedup", about_imagededup),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "ImageDedup - Advanced Duplicate Detection",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_info("\nPress Enter to return to the menu...")
        input()


# Register a static menu for favorites
imagededup_menu.__menu_options__ = {
    "1": ("Single Folder Deduplication", lambda: imagededup_menu()),
    "2": ("HQ/LQ Paired Dataset Deduplication", lambda: imagededup_menu()),
    "3": ("About ImageDedup", lambda: imagededup_menu()),
    "0": ("Back", None),
}
