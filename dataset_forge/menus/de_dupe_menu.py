import os
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_section,
    print_success,
    print_warning,
    print_error,
    print_info,
    print_prompt,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.input_utils import (
    get_path_with_history,
    get_file_operation_choice,
    get_destination_path,
)
from dataset_forge.actions.de_dupe_actions import (
    compute_hashes,
    find_duplicates,
    find_near_duplicates,
    align_and_operate_on_pairs,
)


def de_dupe_menu():
    """Menu for file hash-based de-duplication operations."""

    # Define menu context for help system
    menu_context = {
        "Purpose": "File hash-based de-duplication using perceptual hashing",
        "Total Options": "3 main operations",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
        "Key Features": [
            "Exact duplicate detection using perceptual hashes",
            "Near-duplicate detection with configurable distance threshold",
            "Support for single folder and HQ/LQ paired folders",
            "Multiple hash methods: phash, dhash, ahash, whash",
        ],
        "Tips": [
            "Use exact duplicates for identical images",
            "Use near-duplicates for similar images with slight differences",
            "Always test with dry run first",
            "Backup your data before performing destructive operations",
        ],
    }

    while True:
        options = {
            "1": ("🔍 Find Exact Duplicates", find_exact_duplicates),
            "2": ("🔍 Find Near-Duplicates", find_near_duplicates_menu),
            "3": ("ℹ️ About File Hash De-duplication", about_file_hash_dedup),
            "0": ("⬅️ Back to Utilities", None),
        }

        key = show_menu(
            "🔐 De-Duplicate (File Hash)",
            options,
            Mocha.yellow,
            current_menu="File Hash De-duplication",
            menu_context=menu_context,
        )

        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()


def find_exact_duplicates():
    """Find exact duplicates using perceptual hashing."""
    print_header("🔍 Find Exact Duplicates", color=Mocha.yellow)

    # Get folder path
    folder = get_path_with_history(
        "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
    )
    if not folder or not os.path.isdir(folder):
        print_error("Invalid folder path.")
        return

    # Get hash method
    print_section("Hash Method Selection", color=Mocha.yellow)
    print_info("1. pHash (perceptual hash) - Recommended")
    print_info("2. dHash (difference hash)")
    print_info("3. aHash (average hash)")
    print_info("4. wHash (wavelet hash)")

    method_choice = input("Select hash method [1]: ").strip() or "1"
    hash_methods = {"1": "phash", "2": "dhash", "3": "ahash", "4": "whash"}
    hash_method = hash_methods.get(method_choice, "phash")

    print_section("Processing", color=Mocha.yellow)
    print_info(f"Computing {hash_method.upper()} hashes for images in {folder}...")

    try:
        # Compute hashes
        hashes = compute_hashes(folder, hash_method)
        print_success(f"Computed hashes for {len(hashes)} images")

        # Find duplicates
        print_info("Finding exact duplicates...")
        duplicate_groups = find_duplicates(hashes)

        if not duplicate_groups:
            print_success("No exact duplicates found!")
            return

        print_success(f"Found {len(duplicate_groups)} groups of exact duplicates")

        # Show results
        for i, group in enumerate(duplicate_groups, 1):
            print_info(f"\nGroup {i} ({len(group)} files):")
            for filename in group:
                print_info(f"  - {filename}")

        # Offer operations
        offer_duplicate_operations(duplicate_groups, folder, "exact")

    except Exception as e:
        print_error(f"Error during exact duplicate detection: {e}")


def find_near_duplicates_menu():
    """Find near-duplicates using perceptual hashing."""
    print_header("🔍 Find Near-Duplicates", color=Mocha.yellow)

    # Get folder path
    folder = get_path_with_history(
        "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
    )
    if not folder or not os.path.isdir(folder):
        print_error("Invalid folder path.")
        return

    # Get hash method
    print_section("Hash Method Selection", color=Mocha.yellow)
    print_info("1. pHash (perceptual hash) - Recommended")
    print_info("2. dHash (difference hash)")
    print_info("3. aHash (average hash)")
    print_info("4. wHash (wavelet hash)")

    method_choice = input("Select hash method [1]: ").strip() or "1"
    hash_methods = {"1": "phash", "2": "dhash", "3": "ahash", "4": "whash"}
    hash_method = hash_methods.get(method_choice, "phash")

    # Get distance threshold
    try:
        max_distance = int(input("Enter max Hamming distance [5]: ").strip() or "5")
    except ValueError:
        max_distance = 5

    print_section("Processing", color=Mocha.yellow)
    print_info(f"Computing {hash_method.upper()} hashes for images in {folder}...")

    try:
        # Compute hashes
        hashes = compute_hashes(folder, hash_method)
        print_success(f"Computed hashes for {len(hashes)} images")

        # Find near-duplicates
        print_info(f"Finding near-duplicates with max distance {max_distance}...")
        duplicate_groups = find_near_duplicates(hashes, max_distance)

        if not duplicate_groups:
            print_success("No near-duplicates found!")
            return

        print_success(f"Found {len(duplicate_groups)} groups of near-duplicates")

        # Show results
        for i, group in enumerate(duplicate_groups, 1):
            print_info(f"\nGroup {i} ({len(group)} files):")
            for filename in group:
                print_info(f"  - {filename}")

        # Offer operations
        offer_duplicate_operations(duplicate_groups, folder, "near")

    except Exception as e:
        print_error(f"Error during near-duplicate detection: {e}")


def offer_duplicate_operations(duplicate_groups, folder, duplicate_type):
    """Offer operations on found duplicates."""
    print_section("Duplicate Operations", color=Mocha.peach)
    print_info(f"What would you like to do with the {duplicate_type} duplicates?")
    print_info("1. Move to folder")
    print_info("2. Copy to folder")
    print_info("3. Delete in-place")
    print_info("0. Do nothing")

    action = input("Select action: ").strip()

    if action == "0":
        return

    if action in ("1", "2"):
        dest_dir = get_destination_path()
        if not dest_dir:
            print_error("Destination directory is required for move/copy.")
            return

        operation = "move" if action == "1" else "copy"

        # Confirm operation
        print_warning(
            f"This will {operation} {sum(len(group) - 1 for group in duplicate_groups)} files."
        )
        confirm = input(f"Proceed with {operation}? [y/N]: ").strip().lower()
        if confirm != "y":
            print_info("Operation cancelled.")
            return

        try:
            # For single folder, we need to handle the operation manually
            moved_files = []
            for group in duplicate_groups:
                # Keep first file, operate on the rest
                files_to_operate = list(group)[1:]
                for filename in files_to_operate:
                    src_path = os.path.join(folder, filename)
                    dst_path = os.path.join(dest_dir, filename)

                    if operation == "move":
                        os.rename(src_path, dst_path)
                    else:  # copy
                        import shutil

                        shutil.copy2(src_path, dst_path)

                    moved_files.append(filename)

            print_success(
                f"Successfully {operation}d {len(moved_files)} files to {dest_dir}"
            )

        except Exception as e:
            print_error(f"Error during {operation} operation: {e}")

    elif action == "3":
        # Confirm deletion
        total_files = sum(len(group) - 1 for group in duplicate_groups)
        print_warning(f"This will DELETE {total_files} files permanently!")
        confirm = input("Proceed with deletion? [y/N]: ").strip().lower()
        if confirm != "y":
            print_info("Deletion cancelled.")
            return

        try:
            deleted_files = []
            for group in duplicate_groups:
                # Keep first file, delete the rest
                files_to_delete = list(group)[1:]
                for filename in files_to_delete:
                    file_path = os.path.join(folder, filename)
                    os.remove(file_path)
                    deleted_files.append(filename)

            print_success(f"Successfully deleted {len(deleted_files)} files")

        except Exception as e:
            print_error(f"Error during deletion: {e}")


def about_file_hash_dedup():
    """Show information about file hash de-duplication."""
    print_header("About File Hash De-duplication", color=Mocha.yellow)
    print_info(
        "File hash de-duplication uses perceptual hashing algorithms to identify duplicate images."
    )
    print_info("\nHash Methods:")
    print_info("• pHash (perceptual hash) - Most accurate, recommended for most cases")
    print_info("• dHash (difference hash) - Fast, good for detecting minor changes")
    print_info("• aHash (average hash) - Simple, fast, but less accurate")
    print_info("• wHash (wavelet hash) - Good for detecting rotation and scaling")

    print_info("\nDuplicate Types:")
    print_info("• Exact Duplicates - Identical hash values (same image)")
    print_info("• Near-Duplicates - Similar hash values (similar images)")

    print_info("\nUse Cases:")
    print_info("• Remove identical copies of images")
    print_info("• Find similar images with slight differences")
    print_info("• Clean up datasets with duplicate content")

    print_info("\nSafety:")
    print_info("• Always use dry run or backup before destructive operations")
    print_info("• Test on a small subset first")
    print_info("• Verify results before proceeding with bulk operations")

    print_prompt("\n⏸️ Press Enter to return to the File Hash De-duplication menu...")


if __name__ == "__main__":
    de_dupe_menu()
