import os
import shutil
from dataset_forge.io_utils_old import is_image_file
from dataset_forge.common import get_destination_path, get_unique_filename
from tqdm import tqdm
import logging

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
