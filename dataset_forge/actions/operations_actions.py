import os
import shutil
import random
from subprocess import CalledProcessError
from tqdm import tqdm
from PIL import Image
from dataset_forge.utils.file_utils import (
    is_image_file,
    get_unique_filename,
    IMAGE_TYPES,
)
from dataset_forge.utils.input_utils import (
    get_pairs_to_process,
    get_file_operation_choice,
    get_destination_path,
)
import logging
import numpy as np
from tqdm import tqdm
from collections import Counter, defaultdict
import cv2
import concurrent.futures
from PIL import Image, ImageEnhance, UnidentifiedImageError, ImageFont, ImageDraw
import subprocess
from dataset_forge.utils.image_ops import ColorAdjuster
from dataset_forge.utils import dpid_phhofm


def split_dataset_in_half(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Splitting Dataset in Half")
    print("=" * 30)

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

    # Find matching pairs
    matching_files = [f for f in hq_files if f in lq_files]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_pairs = len(matching_files)
    split_point = num_pairs // 2

    # Shuffle before splitting to ensure random distribution if desired,
    # or keep sorted if alphabetical split is intended.
    # For a true random half, shuffle:
    # random.shuffle(matching_files)

    first_half_files = matching_files[:split_point]
    second_half_files = matching_files[split_point:]

    print(
        f"Found {num_pairs} matching pairs. Splitting into {len(first_half_files)} for first half and {len(second_half_files)} for second half."
    )

    operation = get_file_operation_choice()

    output_base_dir = ""
    if operation != "inplace":
        output_base_dir = get_destination_path()  # Get base output path
        if not output_base_dir:
            print(
                "Operation aborted as no destination path was provided for copy/move."
            )
            return

        output_dir_1_hq = os.path.join(output_base_dir, "split_1", "hq")
        output_dir_1_lq = os.path.join(output_base_dir, "split_1", "lq")
        output_dir_2_hq = os.path.join(output_base_dir, "split_2", "hq")
        output_dir_2_lq = os.path.join(output_base_dir, "split_2", "lq")

        for d in [output_dir_1_hq, output_dir_1_lq, output_dir_2_hq, output_dir_2_lq]:
            os.makedirs(d, exist_ok=True)
    else:
        print(
            "Performing inplace split. This means no files will be moved or copied; the split is conceptual."
        )
        print("If you intended to move files, please choose 'copy' or 'move'.")

    # Process first half
    print(
        f"\nProcessing first half ({len(first_half_files)} pairs) using {operation}..."
    )
    processed_first_half = 0
    errors_first_half = []
    if operation != "inplace":
        for filename in tqdm(
            first_half_files, desc=f"{operation.capitalize()}ing First Half"
        ):
            hq_src = os.path.join(hq_folder, filename)
            lq_src = os.path.join(lq_folder, filename)

            try:
                hq_dest = os.path.join(
                    output_dir_1_hq, get_unique_filename(output_dir_1_hq, filename)
                )
                lq_dest = os.path.join(
                    output_dir_1_lq, get_unique_filename(output_dir_1_lq, filename)
                )
                if operation == "copy":
                    shutil.copy2(hq_src, hq_dest)
                    shutil.copy2(lq_src, lq_dest)
                elif operation == "move":
                    shutil.move(hq_src, hq_dest)
                    shutil.move(lq_src, lq_dest)
                processed_first_half += 1
            except Exception as e:
                errors_first_half.append(
                    f"Error {operation}ing pair {filename} to split_1: {e}"
                )
    else:  # Inplace, just count
        processed_first_half = len(first_half_files)

    # Process second half
    print(
        f"\nProcessing second half ({len(second_half_files)} pairs) using {operation}..."
    )
    processed_second_half = 0
    errors_second_half = []
    if operation != "inplace":
        for filename in tqdm(
            second_half_files, desc=f"{operation.capitalize()}ing Second Half"
        ):
            hq_src = os.path.join(hq_folder, filename)
            lq_src = os.path.join(lq_folder, filename)

            try:
                hq_dest = os.path.join(
                    output_dir_2_hq, get_unique_filename(output_dir_2_hq, filename)
                )
                lq_dest = os.path.join(
                    output_dir_2_lq, get_unique_filename(output_dir_2_lq, filename)
                )
                if operation == "copy":
                    shutil.copy2(hq_src, hq_dest)
                    shutil.copy2(lq_src, lq_dest)
                elif operation == "move":
                    # Important: If moving, source files for second half might have been moved
                    # if they were also part of the first_half_files source during the 'move' operation.
                    # This logic assumes source folders (hq_folder, lq_folder) are not modified by the first half's 'move'.
                    # If 'move' is from original, ensure files are still there.
                    # However, typical use of 'move' here is to move *from* original *to* new split folders.
                    if os.path.exists(hq_src) and os.path.exists(lq_src):
                        shutil.move(hq_src, hq_dest)
                        shutil.move(lq_src, lq_dest)
                    else:
                        errors_second_half.append(
                            f"Source file {filename} already moved or missing for second half."
                        )
                        continue  # Skip if source is gone
                processed_second_half += 1
            except Exception as e:
                errors_second_half.append(
                    f"Error {operation}ing pair {filename} to split_2: {e}"
                )
    else:  # Inplace, just count
        processed_second_half = len(second_half_files)

    print("\nSplit in half operation complete.")
    if operation == "inplace":
        print(
            f"Note: 'Inplace' operation for splitting means {processed_first_half} pairs identified for first half, {processed_second_half} for second. No files were moved or copied."
        )
    else:
        print(
            f"Total processed into first half: {processed_first_half}, into second half: {processed_second_half}"
        )
        if errors_first_half or errors_second_half:
            print("Errors encountered during split:")
            for e in errors_first_half:
                print(f"  - {e}")
            for e in errors_second_half:
                print(f"  - {e}")

    print("=" * 30)


def remove_pairs_by_count_percentage(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Remove Pairs by Count/Percentage")
    print("=" * 30)

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
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_available = len(matching_files)
    print(f"Found {num_available} matching pairs.")

    while True:
        amount_str = input(
            f"Enter amount to remove (e.g., 100 or 10% of {num_available} pairs): "
        ).strip()
        num_to_remove = 0
        if amount_str.endswith("%"):
            try:
                percentage = float(amount_str[:-1])
                if 0 <= percentage <= 100:
                    num_to_remove = int(num_available * (percentage / 100))
                    break
                else:
                    print("Percentage must be between 0 and 100.")
            except ValueError:
                print("Invalid percentage format.")
        else:
            try:
                num = int(amount_str)
                if 0 <= num <= num_available:
                    num_to_remove = num
                    break
                else:
                    print(
                        f"Number of pairs to remove must be between 0 and {num_available}."
                    )
            except ValueError:
                print("Invalid number format.")

    if num_to_remove == 0:
        print("No pairs to remove. Exiting operation.")
        print("=" * 30)
        return

    print(f"Will identify {num_to_remove} pairs for removal.")

    operation = (
        get_file_operation_choice()
    )  # This will be "remove", "copy to remove", "move to remove"
    action_verb = "remove"
    if operation == "copy":
        action_verb = "copy (as removal)"
    if operation == "move":
        action_verb = "move (as removal)"

    destination = None
    dest_hq_folder = None
    dest_lq_folder = None

    if operation == "move" or operation == "copy":
        destination_prompt = (
            "Enter the destination directory path to move/copy the 'removed' pairs:"
        )
        destination = (
            get_destination_path(prompt=destination_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )  # a bit of a hack for older signature
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        dest_hq_folder = os.path.join(
            destination, "removed_hq" if operation == "move" else "copied_removed_hq"
        )
        dest_lq_folder = os.path.join(
            destination, "removed_lq" if operation == "move" else "copied_removed_lq"
        )
        os.makedirs(dest_hq_folder, exist_ok=True)
        os.makedirs(dest_lq_folder, exist_ok=True)
        print(f"Pairs designated for 'removal' will be {operation}d to {destination}")

    pairs_to_remove_names = random.sample(matching_files, num_to_remove)

    print(
        f"\nPerforming '{action_verb}' operation on {len(pairs_to_remove_names)} pairs..."
    )

    processed_count = 0
    errors = []

    for filename in tqdm(
        pairs_to_remove_names, desc=f"{action_verb.capitalize()}ing Pairs"
    ):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            if operation == "move":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.move(hq_path, hq_dest)
                shutil.move(lq_path, lq_dest)
            elif operation == "copy":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.copy2(hq_path, hq_dest)
                shutil.copy2(lq_path, lq_dest)
            elif operation == "inplace":  # This means actual deletion
                os.remove(hq_path)
                os.remove(lq_path)
            processed_count += 1
        except Exception as e:
            errors.append(f"Error {action_verb}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove by Count/Percentage Summary")
    print("-" * 30)
    print(f"Requested to {action_verb}: {num_to_remove} pairs.")
    print(f"Successfully {action_verb}d: {processed_count} pairs.")
    if operation == "inplace":
        print("  (Files were deleted from the source folders).")
    elif operation in ["copy", "move"]:
        print(f"  (Files were {operation}d to {destination}).")

    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    print("-" * 30)
    print("=" * 30)


def remove_pairs_by_size(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Remove Pairs by File Size")
    print("=" * 30)

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
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_available = len(matching_files)
    print(f"Found {num_available} matching pairs.")

    while True:
        try:
            size_threshold_str = (
                input("Enter size threshold (e.g., 100KB, 2MB, 500B for bytes): ")
                .strip()
                .upper()
            )
            multiplier = 1
            if size_threshold_str.endswith("KB"):
                multiplier = 1024
                size_threshold_str = size_threshold_str[:-2]
            elif size_threshold_str.endswith("MB"):
                multiplier = 1024 * 1024
                size_threshold_str = size_threshold_str[:-2]
            elif size_threshold_str.endswith("B"):
                size_threshold_str = size_threshold_str[:-1]

            size_threshold = float(size_threshold_str) * multiplier
            if size_threshold >= 0:
                break
            else:
                print("Size threshold must be non-negative.")
        except ValueError:
            print(
                "Invalid input. Please enter a number, optionally followed by KB, MB, or B."
            )

    while True:
        criteria = (
            input(
                f"Remove pairs where EITHER image's size is (above/below) {size_threshold / multiplier:.2f}{('KB' if multiplier==1024 else ('MB' if multiplier==1024*1024 else 'B'))}? "
            )
            .strip()
            .lower()
        )
        if criteria in ["above", "below"]:
            break
        else:
            print("Invalid criteria. Please enter 'above' or 'below'.")

    operation = get_file_operation_choice()
    action_verb = "remove"
    if operation == "copy":
        action_verb = "copy (as removal)"
    if operation == "move":
        action_verb = "move (as removal)"

    destination = None
    dest_hq_folder = None
    dest_lq_folder = None

    if operation == "move" or operation == "copy":
        destination_prompt = (
            "Enter destination directory for pairs meeting size criteria:"
        )
        destination = (
            get_destination_path(prompt=destination_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        dest_hq_folder = os.path.join(destination, "size_criteria_hq")
        dest_lq_folder = os.path.join(destination, "size_criteria_lq")
        os.makedirs(dest_hq_folder, exist_ok=True)
        os.makedirs(dest_lq_folder, exist_ok=True)
        print(f"Pairs matching criteria will be {operation}d to {destination}")

    pairs_to_process_names = []
    skipped_due_error = []
    for filename in tqdm(matching_files, desc="Checking File Sizes"):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            hq_size = os.path.getsize(hq_path)
            lq_size = os.path.getsize(lq_path)
            process_pair = False
            if criteria == "above" and (
                hq_size > size_threshold or lq_size > size_threshold
            ):
                process_pair = True
            elif criteria == "below" and (
                hq_size < size_threshold or lq_size < size_threshold
            ):
                process_pair = True

            if process_pair:
                pairs_to_process_names.append(filename)
        except Exception as e:
            # print(f"Error getting size for pair {filename}: {e}")
            skipped_due_error.append(f"{filename}: {e}")

    if not pairs_to_process_names:
        print(
            f"No pairs found matching the criteria: size {criteria} {size_threshold / multiplier:.2f}{('KB' if multiplier==1024 else ('MB' if multiplier==1024*1024 else 'B'))}. Exiting."
        )
        if skipped_due_error:
            print(
                f"Skipped {len(skipped_due_error)} pairs due to errors during size check."
            )
        print("=" * 30)
        return

    print(
        f"\nWill {action_verb} {len(pairs_to_process_names)} pairs matching: size {criteria} {size_threshold / multiplier:.2f}{('KB' if multiplier==1024 else ('MB' if multiplier==1024*1024 else 'B'))}."
    )
    if skipped_due_error:
        print(
            f"Note: Skipped {len(skipped_due_error)} pairs due to errors during size check (e.g., file not found)."
        )

    processed_count = 0
    errors = []

    for filename in tqdm(
        pairs_to_process_names, desc=f"{action_verb.capitalize()}ing Pairs by Size"
    ):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            if operation == "move":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.move(hq_path, hq_dest)
                shutil.move(lq_path, lq_dest)
            elif operation == "copy":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.copy2(hq_path, hq_dest)
                shutil.copy2(lq_path, lq_dest)
            elif operation == "inplace":  # Actual deletion
                os.remove(hq_path)
                os.remove(lq_path)
            processed_count += 1
        except Exception as e:
            errors.append(f"Error {action_verb}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove by File Size Summary")
    print("-" * 30)
    print(
        f"Criteria: Size {criteria} {size_threshold / multiplier:.2f}{('KB' if multiplier==1024 else ('MB' if multiplier==1024*1024 else 'B'))}."
    )
    print(f"Successfully {action_verb}d: {processed_count} pairs.")
    if operation == "inplace":
        print("  (Files were deleted from the source folders).")
    elif operation in ["copy", "move"]:
        print(f"  (Files were {operation}d to {destination}).")

    if errors:
        print(f"Errors encountered during {action_verb} operation: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    if skipped_due_error:
        print(
            f"Pairs skipped due to read errors during initial check: {len(skipped_due_error)}"
        )
        for i, error in enumerate(skipped_due_error[: min(len(skipped_due_error), 2)]):
            print(f"  - {error}")
        if len(skipped_due_error) > 2:
            print(f"  ... and {len(skipped_due_error) - 2} more skipped.")
    print("-" * 30)
    print("=" * 30)


def remove_pairs_by_dimensions(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Remove Pairs by Dimensions")
    print("=" * 30)

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
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_available = len(matching_files)
    print(f"Found {num_available} matching pairs.")

    while True:
        # Clarify if criteria applies to HQ, LQ, or BOTH images in a pair
        target_image = (
            input(
                "Apply dimension criteria to (hq/lq/both_must_match_criteria) images in a pair? "
            )
            .strip()
            .lower()
        )
        if target_image in ["hq", "lq", "both_must_match_criteria"]:
            break
        else:
            print(
                "Invalid input. Please enter 'hq', 'lq', or 'both_must_match_criteria'."
            )

    while True:
        dim_type = (
            input(
                "Filter by (width/height/area/any_dimension)? 'area' is width*height. 'any_dimension' checks width OR height. "
            )
            .strip()
            .lower()
        )
        if dim_type in ["width", "height", "area", "any_dimension"]:
            break
        else:
            print(
                "Invalid input. Please enter 'width', 'height', 'area', or 'any_dimension'."
            )

    min_val = -1.0  # Use float for area
    max_val = float("inf")

    while True:
        try:
            min_val_str = input(
                f"Enter MINIMUM {dim_type} (pixels/pixels^2 for area). Leave blank for no minimum: "
            ).strip()
            min_val = float(min_val_str) if min_val_str else -1.0
            if min_val != -1.0 and min_val < 0:
                print("Minimum value cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    while True:
        try:
            max_val_str = input(
                f"Enter MAXIMUM {dim_type} (pixels/pixels^2 for area). Leave blank for no maximum: "
            ).strip()
            max_val = float(max_val_str) if max_val_str else float("inf")
            if max_val != float("inf") and max_val < 0:  # max_val can be 0
                print("Maximum value cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    if min_val != -1.0 and max_val != float("inf") and min_val > max_val:
        print("Minimum value cannot be greater than maximum value. Aborting.")
        return

    # Ask if the user wants to remove pairs *within* this range or *outside* this range.
    while True:
        removal_logic = (
            input(
                f"Remove pairs with {dim_type} (within/outside) this range [{min_val if min_val != -1.0 else 'any'} - {max_val if max_val != float('inf') else 'any'}]? "
            )
            .strip()
            .lower()
        )
        if removal_logic in ["within", "outside"]:
            break
        else:
            print("Invalid choice. Please enter 'within' or 'outside'.")

    operation = get_file_operation_choice()
    action_verb = "remove"
    if operation == "copy":
        action_verb = "copy (as removal)"
    if operation == "move":
        action_verb = "move (as removal)"

    destination = None
    dest_hq_folder = None
    dest_lq_folder = None

    if operation == "move" or operation == "copy":
        destination_prompt = (
            "Enter destination directory for pairs matching dimension criteria:"
        )
        destination = (
            get_destination_path(prompt=destination_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        dest_hq_folder = os.path.join(destination, "dimension_criteria_hq")
        dest_lq_folder = os.path.join(destination, "dimension_criteria_lq")
        os.makedirs(dest_hq_folder, exist_ok=True)
        os.makedirs(dest_lq_folder, exist_ok=True)
        print(f"Pairs matching criteria will be {operation}d to {destination}")

    pairs_to_process_names = []
    skipped_due_error = []

    for filename in tqdm(matching_files, desc="Checking Dimensions"):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            with Image.open(hq_path) as hq_img, Image.open(lq_path) as lq_img:
                hq_w, hq_h = hq_img.size
                lq_w, lq_h = lq_img.size

                def check_dim(w, h, dim_type, min_v, max_v):
                    val_to_check = 0
                    if dim_type == "width":
                        val_to_check = w
                    elif dim_type == "height":
                        val_to_check = h
                    elif dim_type == "area":
                        val_to_check = w * h
                    elif dim_type == "any_dimension":
                        # For 'any_dimension', it's within range if EITHER width OR height is in range
                        in_range_w = (min_v == -1.0 or w >= min_v) and (
                            max_v == float("inf") or w <= max_v
                        )
                        in_range_h = (min_v == -1.0 or h >= min_v) and (
                            max_v == float("inf") or h <= max_v
                        )
                        return in_range_w or in_range_h

                    return (min_v == -1.0 or val_to_check >= min_v) and (
                        max_v == float("inf") or val_to_check <= max_v
                    )

                hq_matches_range = check_dim(hq_w, hq_h, dim_type, min_val, max_val)
                lq_matches_range = check_dim(lq_w, lq_h, dim_type, min_val, max_val)

                pair_is_within_range = False
                if target_image == "hq":
                    pair_is_within_range = hq_matches_range
                elif target_image == "lq":
                    pair_is_within_range = lq_matches_range
                elif (
                    target_image == "both_must_match_criteria"
                ):  # Both HQ and LQ images must individually satisfy the range
                    pair_is_within_range = hq_matches_range and lq_matches_range

                # Determine if the pair should be processed based on removal_logic
                process_pair = False
                if removal_logic == "within" and pair_is_within_range:
                    process_pair = True
                elif removal_logic == "outside" and not pair_is_within_range:
                    process_pair = True

                if process_pair:
                    pairs_to_process_names.append(filename)
        except Exception as e:
            # print(f"Error processing dimensions for pair {filename}: {e}")
            skipped_due_error.append(f"{filename}: {e}")

    if not pairs_to_process_names:
        print(f"No pairs found matching the dimension criteria. Exiting operation.")
        if skipped_due_error:
            print(
                f"Skipped {len(skipped_due_error)} pairs due to errors reading images."
            )
        print("=" * 30)
        return

    print(
        f"\nWill {action_verb} {len(pairs_to_process_names)} pairs. Criteria: Target '{target_image}', Dim '{dim_type}', Range [{min_val if min_val != -1.0 else 'any'}-{max_val if max_val != float('inf') else 'any'}], Logic '{removal_logic}'."
    )
    if skipped_due_error:
        print(
            f"Note: Skipped {len(skipped_due_error)} pairs due to errors reading image dimensions."
        )

    processed_count = 0
    errors = []

    for filename in tqdm(
        pairs_to_process_names, desc=f"{action_verb.capitalize()}ing Pairs by Dimension"
    ):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            if operation == "move":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.move(hq_path, hq_dest)
                shutil.move(lq_path, lq_dest)
            elif operation == "copy":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.copy2(hq_path, hq_dest)
                shutil.copy2(lq_path, lq_dest)
            elif operation == "inplace":  # Actual deletion
                os.remove(hq_path)
                os.remove(lq_path)
            processed_count += 1
        except Exception as e:
            errors.append(f"Error {action_verb}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove by Dimensions Summary")
    print("-" * 30)
    print(
        f"Criteria: Target '{target_image}', Dim '{dim_type}', Range [{min_val if min_val != -1.0 else 'any'} - {max_val if max_val != float('inf') else 'any'}], Logic '{removal_logic}'."
    )
    print(f"Successfully {action_verb}d: {processed_count} pairs.")
    if operation == "inplace":
        print("  (Files were deleted from the source folders).")
    elif operation in ["copy", "move"]:
        print(f"  (Files were {operation}d to {destination}).")

    if errors:
        print(f"Errors encountered during {action_verb} operation: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    if skipped_due_error:
        print(
            f"Pairs skipped due to read errors during initial check: {len(skipped_due_error)}"
        )
    print("-" * 30)
    print("=" * 30)


def remove_pairs_by_file_type(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print(" Remove Pairs by File Type")
    print("=" * 30)

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
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        print("=" * 30)
        return

    num_available = len(matching_files)
    print(f"Found {num_available} matching pairs.")

    print("\nSupported image types:")
    for i, img_type in enumerate(IMAGE_TYPES):
        print(f"  {i+1}. {img_type.lstrip('.')}")

    while True:
        file_type_input = (
            input("Enter file type to target for removal (e.g., 'png' or 'jpg'): ")
            .strip()
            .lower()
        )
        if not file_type_input.startswith("."):
            file_type_to_remove_normalized = "." + file_type_input
        else:
            file_type_to_remove_normalized = file_type_input

        if file_type_to_remove_normalized in IMAGE_TYPES:
            break
        else:
            print(
                f"Invalid file type '{file_type_input}'. Please enter a supported image type (e.g., png, jpg, webp)."
            )

    # Ask if we are removing pairs IF HQ is type, IF LQ is type, or IF BOTH are type.
    while True:
        target_choice = (
            input(
                f"Remove pair if (hq/lq/both/either) is of type '{file_type_to_remove_normalized}'? "
            )
            .strip()
            .lower()
        )
        if target_choice in ["hq", "lq", "both", "either"]:
            break
        else:
            print("Invalid choice. Please enter 'hq', 'lq', 'both', or 'either'.")

    operation = get_file_operation_choice()
    action_verb = "remove"
    if operation == "copy":
        action_verb = "copy (as removal)"
    if operation == "move":
        action_verb = "move (as removal)"

    destination = None
    dest_hq_folder = None
    dest_lq_folder = None

    if operation == "move" or operation == "copy":
        destination_prompt = f"Enter destination directory for pairs where {target_choice} is type '{file_type_to_remove_normalized}':"
        destination = (
            get_destination_path(prompt=destination_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        dest_hq_folder = os.path.join(destination, "filetype_criteria_hq")
        dest_lq_folder = os.path.join(destination, "filetype_criteria_lq")
        os.makedirs(dest_hq_folder, exist_ok=True)
        os.makedirs(dest_lq_folder, exist_ok=True)
        print(f"Pairs matching criteria will be {operation}d to {destination}")

    pairs_to_process_names = []
    for filename in matching_files:
        hq_is_target_type = filename.lower().endswith(file_type_to_remove_normalized)
        lq_is_target_type = filename.lower().endswith(
            file_type_to_remove_normalized
        )  # Assuming LQ has same name and thus same original type logic

        process_pair = False
        if target_choice == "hq" and hq_is_target_type:
            process_pair = True
        elif (
            target_choice == "lq" and lq_is_target_type
        ):  # This is often same as HQ due to naming
            process_pair = True
        elif target_choice == "both" and (hq_is_target_type and lq_is_target_type):
            process_pair = True
        elif target_choice == "either" and (hq_is_target_type or lq_is_target_type):
            process_pair = True

        if process_pair:
            pairs_to_process_names.append(filename)

    if not pairs_to_process_names:
        print(
            f"No pairs found matching criteria: {target_choice} is type '{file_type_to_remove_normalized}'. Exiting."
        )
        print("=" * 30)
        return

    print(
        f"\nWill {action_verb} {len(pairs_to_process_names)} pairs where {target_choice} is of type '{file_type_to_remove_normalized}'."
    )

    processed_count = 0
    errors = []

    for filename in tqdm(
        pairs_to_process_names, desc=f"{action_verb.capitalize()}ing Pairs by File Type"
    ):
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)

        try:
            if operation == "move":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.move(hq_path, hq_dest)
                shutil.move(lq_path, lq_dest)
            elif operation == "copy":
                hq_dest = os.path.join(
                    dest_hq_folder, get_unique_filename(dest_hq_folder, filename)
                )
                lq_dest = os.path.join(
                    dest_lq_folder, get_unique_filename(dest_lq_folder, filename)
                )
                shutil.copy2(hq_path, hq_dest)
                shutil.copy2(lq_path, lq_dest)
            elif operation == "inplace":  # Actual deletion
                os.remove(hq_path)
                os.remove(lq_path)
            processed_count += 1
        except Exception as e:
            errors.append(f"Error {action_verb}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print(" Remove by File Type Summary")
    print("-" * 30)
    print(
        f"Criteria: {target_choice.capitalize()} image file type is '{file_type_to_remove_normalized}'."
    )
    print(f"Successfully {action_verb}d: {processed_count} pairs.")
    if operation == "inplace":
        print("  (Files were deleted from the source folders).")
    elif operation in ["copy", "move"]:
        print(f"  (Files were {operation}d to {destination}).")

    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    print("-" * 30)
    print("=" * 30)


# --- Function from remove_small_pairs.py ---
def is_small(img_path, min_size):
    try:
        with Image.open(img_path) as img:
            w, h = img.size
            return w < min_size or h < min_size
    except Exception as e:
        # print(f"Error reading {img_path}: {e}") # Avoid verbose error during check
        return True  # treat unreadable images as "too small"


# --- Functions from transform_dataset.py ---
def apply_transformation_to_image(
    image_path, transform_type, value, operation, dest_path=None, quality=95
):
    try:
        with Image.open(image_path) as img:
            original_format = img.format  # Preserve original format if possible
            output_img = None

            if transform_type == "brightness":
                enhancer = ImageEnhance.Brightness(img)
                output_img = enhancer.enhance(value)
            elif transform_type == "contrast":
                enhancer = ImageEnhance.Contrast(img)
                output_img = enhancer.enhance(value)
            elif transform_type == "saturation":  # PIL's Color is for saturation
                if (
                    img.mode == "L"
                ):  # Grayscale image, saturation has no effect or can cause error
                    output_img = img.copy()  # Keep as is
                    # logging.info(f"Saturation no-op for grayscale image: {image_path}")
                else:
                    enhancer = ImageEnhance.Color(img)
                    output_img = enhancer.enhance(value)
            elif transform_type == "sharpness":
                enhancer = ImageEnhance.Sharpness(img)
                output_img = enhancer.enhance(value)
            elif transform_type == "rotate":
                # Ensure expand=True for rotate to prevent cropping, fillcolor for background if needed
                output_img = img.rotate(
                    value, expand=True, fillcolor=None
                )  # None usually means black or white depending on mode
            elif transform_type == "flip_horizontal":
                output_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif transform_type == "flip_vertical":
                output_img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif transform_type == "grayscale":
                if img.mode != "L":  # Only convert if not already grayscale
                    output_img = img.convert("L")
                else:
                    output_img = img.copy()  # Already grayscale, just copy
            else:
                logging.error(
                    f"Unknown transform_type: {transform_type} for {image_path}"
                )
                return False

            if (
                output_img is None
            ):  # Should not happen if all branches assign output_img
                logging.error(
                    f"Output image is None after transform {transform_type} for {image_path}"
                )
                return False

            save_params = {}
            if original_format and original_format.upper() in ["JPEG", "JPG"]:
                save_params["quality"] = quality
                # save_params['subsampling'] = 0 # Optional: Keep original subsampling if known, 0 for best quality
                # save_params['icc_profile'] = img.info.get('icc_profile') # Preserve color profile

            if operation == "inplace":
                output_img.save(image_path, format=original_format, **save_params)
            elif operation in ["copy", "move"]:
                if dest_path is None:
                    logging.error(
                        f"Destination path is None for {operation} on {image_path}"
                    )
                    return False
                output_img.save(dest_path, format=original_format, **save_params)
                if operation == "move":
                    if os.path.exists(image_path):  # Ensure it exists before removing
                        os.remove(image_path)
            return True

    except UnidentifiedImageError:
        logging.error(
            f"UnidentifiedImageError: Cannot open or read image file {image_path}. It may be corrupted or not a supported format."
        )
        return False
    except IOError as ioe:
        logging.error(
            f"IOError processing image {image_path} for {transform_type}: {ioe}"
        )
        return False
    except Exception as e:
        logging.error(
            f"Unexpected error applying {transform_type} to {image_path}: {e}"
        )
        return False


# --- Functions from dataset_color_adjustment.py ---
def adjust_image_color(
    image_path, adjustment_type, factor, operation, dest_path=None, quality=95
):
    # This function is very similar to apply_transformation_to_image,
    # could be merged or use a common core if PIL Enhance objects are handled generically.
    # For now, keeping separate as per original structure.
    try:
        if adjustment_type == "hue":
            # Use OpenCV for hue adjustment
            import cv2
            import numpy as np

            img_bgr = cv2.imread(image_path)
            if img_bgr is None:
                logging.error(f"Could not read image for hue adjustment: {image_path}")
                return False
            img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            # factor is now degrees (0-179)
            try:
                hue_shift = int(factor)
            except Exception:
                hue_shift = 0
            img_hsv[..., 0] = (img_hsv[..., 0].astype(int) + hue_shift) % 180
            img_bgr_shifted = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
            # Save result
            save_path = image_path if operation == "inplace" else dest_path
            if save_path is None:
                logging.error(
                    f"Destination path is None for hue adjustment on {image_path}"
                )
                return False
            # Use cv2.imwrite for BGR images
            result = cv2.imwrite(save_path, img_bgr_shifted)
            if not result:
                logging.error(f"cv2.imwrite failed for {save_path}")
                return False
            if (
                operation == "move"
                and os.path.exists(image_path)
                and save_path != image_path
            ):
                os.remove(image_path)
            return True
        # ... existing code ...
        with Image.open(image_path) as img:
            original_format = img.format
            output_img = None
            enhancer = None

            if adjustment_type == "brightness":
                enhancer = ImageEnhance.Brightness(img)
            elif adjustment_type == "contrast":
                enhancer = ImageEnhance.Contrast(img)
            elif adjustment_type == "color":  # This is saturation in PIL's terminology
                if img.mode == "L":  # Grayscale image
                    output_img = img.copy()  # No change
                else:
                    enhancer = ImageEnhance.Color(img)
            elif adjustment_type == "sharpness":
                enhancer = ImageEnhance.Sharpness(img)
            else:
                logging.error(
                    f"Unknown adjustment_type: {adjustment_type} for {image_path}"
                )
                return False

            if enhancer:  # If not grayscale 'color'
                output_img = enhancer.enhance(factor)
            elif output_img is None:  # Grayscale 'color' case, output_img was set
                logging.error(
                    f"Output image is None after adjustment {adjustment_type} for {image_path} - logic error."
                )
                return False

            save_params = {}
            if original_format and original_format.upper() in ["JPEG", "JPG"]:
                save_params["quality"] = quality
                # save_params['icc_profile'] = img.info.get('icc_profile')

            if operation == "inplace":
                output_img.save(image_path, format=original_format, **save_params)
            elif operation in ["copy", "move"]:
                if dest_path is None:
                    logging.error(
                        f"Destination path is None for {operation} on {image_path} (color adjust)"
                    )
                    return False
                output_img.save(dest_path, format=original_format, **save_params)
                if operation == "move":
                    if os.path.exists(image_path):
                        os.remove(image_path)
            return True

    except UnidentifiedImageError:
        logging.error(
            f"UnidentifiedImageError: Cannot open or read image file {image_path} for color adjustment."
        )
        return False
    except IOError as ioe:
        logging.error(
            f"IOError during color adjustment for {image_path} ({adjustment_type}): {ioe}"
        )
        return False
    except Exception as e:
        logging.error(
            f"Unexpected error adjusting {adjustment_type} for {image_path}: {e}"
        )
        return False


def remove_small_image_pairs(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Removing Small Image Pairs")
    print("=" * 30)

    while True:
        try:
            min_size = int(input("Enter the minimum allowed dimension (e.g., 80): "))
            if min_size >= 0:
                break
            else:
                print("Please enter a non-negative integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    operation = get_file_operation_choice()
    destination = ""
    if operation == "move":
        destination = get_destination_path()
        if not destination:
            print("Operation aborted as no destination path was provided for move.")
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)
    elif operation == "copy":
        destination = get_destination_path()
        if not destination:
            print("Operation aborted as no destination path was provided for copy.")
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)

    removed_count = 0
    checked_count = 0
    errors = []

    lq_files = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    # Filter to only include pairs that exist in both folders
    hq_files_set = set(os.listdir(hq_folder))
    matching_files = [f for f in lq_files if f in hq_files_set and is_image_file(f)]

    print(f"Checking {len(matching_files)} HQ/LQ pairs...")

    for filename in tqdm(matching_files, desc="Processing Small Pairs"):
        lq_path = os.path.join(lq_folder, filename)
        hq_path = os.path.join(hq_folder, filename)

        # This check is redundant due to pre-filtering, but kept for safety.
        if not os.path.isfile(hq_path):
            # errors.append(f"Skipping {filename}: HQ pair not found.") # Should not happen with matching_files
            continue

        checked_count += 1

        lq_is_small = is_small(lq_path, min_size)
        hq_is_small = is_small(hq_path, min_size)

        if lq_is_small or hq_is_small:
            try:
                if operation == "inplace":
                    # For remove, inplace means direct deletion
                    os.remove(lq_path)
                    os.remove(hq_path)
                    # logging.info(f"Removed (inplace) small pair: {filename}")
                else:  # copy or move
                    hq_dest_folder = os.path.join(destination, "hq")
                    lq_dest_folder = os.path.join(destination, "lq")
                    hq_dest_path = os.path.join(
                        hq_dest_folder,
                        get_unique_filename(hq_dest_folder, filename),
                    )
                    lq_dest_path = os.path.join(
                        lq_dest_folder,
                        get_unique_filename(lq_dest_folder, filename),
                    )

                    if operation == "copy":
                        shutil.copy2(hq_path, hq_dest_path)
                        shutil.copy2(lq_path, lq_dest_path)
                        # logging.info(f"Copied small pair {filename} to {destination}")
                    elif operation == "move":
                        shutil.move(hq_path, hq_dest_path)
                        shutil.move(lq_path, lq_dest_path)
                        # logging.info(f"Moved small pair {filename} to {destination}")
                removed_count += 1
            except Exception as e:
                errors.append(f"Error {operation}ing {filename}: {e}")
                logging.error(f"Error {operation}ing small pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove Small Pairs Summary")
    print("-" * 30)
    print(f"Checked {checked_count} pairs.")
    print(
        f"Processed ({operation}ed) {removed_count} image pairs where either dimension was smaller than {min_size}."
    )
    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    print("-" * 30)
    print("=" * 30)


# --- Function from extract_val_random.py ---
def extract_random_pairs(input_hq_folder, input_lq_folder):
    print("\n" + "=" * 30)
    print("  Extracting Random Image Pairs")
    print("=" * 30)

    operation = get_file_operation_choice()

    output_base_dir = ""
    if operation != "inplace":
        output_base_dir = get_destination_path()
        if not output_base_dir:
            print(
                "Operation aborted as no destination path was provided for copy/move."
            )
            return

    while True:
        try:
            num_pairs_str = input(
                "Enter the number of random pairs to extract (default is 15 if left blank): "
            ).strip()
            num_pairs = int(num_pairs_str) if num_pairs_str else 15
            if num_pairs > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    hq_files = [
        f
        for f in os.listdir(input_hq_folder)
        if os.path.isfile(os.path.join(input_hq_folder, f)) and is_image_file(f)
    ]
    lq_files = [
        f
        for f in os.listdir(input_lq_folder)
        if os.path.isfile(os.path.join(input_lq_folder, f)) and is_image_file(f)
    ]

    available_pairs = [f for f in hq_files if f in lq_files]

    if len(available_pairs) < num_pairs:
        print(
            f"Warning: Only {len(available_pairs)} matching HQ/LQ pairs found, which is less than the requested {num_pairs} pairs. Extracting {len(available_pairs)} pairs instead."
        )
        num_pairs = len(available_pairs)

    if num_pairs == 0:
        print("No pairs to process. Exiting.")
        return

    selected_files = random.sample(available_pairs, num_pairs)

    if operation != "inplace":
        output_hq_dir = os.path.join(output_base_dir, "hq")
        output_lq_dir = os.path.join(output_base_dir, "lq")
        os.makedirs(output_hq_dir, exist_ok=True)
        os.makedirs(output_lq_dir, exist_ok=True)
        print(
            f"Processing {num_pairs} random pairs to {output_base_dir} using {operation}..."
        )
    else:
        print(
            f"Selected {num_pairs} random pairs. 'Inplace' operation means no files will be moved or copied."
        )

    processed_count = 0
    errors = []
    for filename in tqdm(selected_files, desc=f"{operation.capitalize()}ing Pairs"):
        hq_src_path = os.path.join(input_hq_folder, filename)
        lq_src_path = os.path.join(input_lq_folder, filename)

        try:
            if operation == "copy":
                hq_dest_path = os.path.join(
                    output_hq_dir, get_unique_filename(output_hq_dir, filename)
                )
                lq_dest_path = os.path.join(
                    output_lq_dir, get_unique_filename(output_lq_dir, filename)
                )
                shutil.copy2(hq_src_path, hq_dest_path)
                shutil.copy2(lq_src_path, lq_dest_path)
                processed_count += 1
            elif operation == "move":
                hq_dest_path = os.path.join(
                    output_hq_dir, get_unique_filename(output_hq_dir, filename)
                )
                lq_dest_path = os.path.join(
                    output_lq_dir, get_unique_filename(output_lq_dir, filename)
                )
                shutil.move(hq_src_path, hq_dest_path)
                shutil.move(lq_src_path, lq_dest_path)
                processed_count += 1
            elif operation == "inplace":
                # For extraction, "inplace" means no file operation, only selection.
                # The files are already "selected" in the `selected_files` list.
                # We count them as "processed" in terms of selection.
                processed_count += 1  # Count as selected
                continue
        except Exception as e:
            errors.append(f"Error {operation}ing pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Extract Random Pairs Summary")
    print("-" * 30)
    print(f"Requested pairs for extraction: {num_pairs}")
    if operation != "inplace":
        print(f"Successfully {operation}d: {processed_count} pairs.")
    else:
        print(
            f"Successfully selected: {processed_count} pairs (no files moved/copied due to 'inplace')."
        )

    if errors:
        print(f"Errors encountered during file operations: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more issues.")
    if operation == "inplace":
        print(
            "Note: 'Inplace' operation for extraction means no files were moved or copied, only selected."
        )
    print("-" * 30)
    print("=" * 30)


# --- Functions from shuffle_images.py ---
def shuffle_image_pairs(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Shuffling Image Pairs (with Renaming)")
    print("=" * 30)

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

    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found to shuffle.")
        print("=" * 30)
        return

    print(f"Found {len(matching_files)} matching pairs to shuffle and rename.")

    operation = get_file_operation_choice()  # copy, move, inplace

    # For inplace, files are renamed in original folders.
    # For copy/move, files are copied/moved to new folders and then renamed within those new folders.

    output_hq_dir = hq_folder
    output_lq_dir = lq_folder

    if operation != "inplace":
        output_base_dir_prompt = (
            "Enter base destination directory for shuffled & renamed pairs: "
        )
        output_base_dir = (
            get_destination_path(prompt=output_base_dir_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )

        if not output_base_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return

        # Create subfolders like "shuffled_hq" and "shuffled_lq"
        # Or just "hq" and "lq" if the user intends the base_dir to be the new dataset root.
        # Let's assume user provides a new dataset root.
        output_hq_dir = os.path.join(output_base_dir, "hq")  # Standardized output
        output_lq_dir = os.path.join(output_base_dir, "lq")
        os.makedirs(output_hq_dir, exist_ok=True)
        os.makedirs(output_lq_dir, exist_ok=True)
        print(
            f"Shuffled pairs will be {operation}d and renamed in: {output_hq_dir} and {output_lq_dir}"
        )
    else:
        print("Shuffling and renaming files in-place within original folders.")

    # Create pairs: (original_filename, extension)
    # This ensures that if we shuffle, the extension is tied to the original file.
    original_pairs_info = []
    for fname in matching_files:
        original_pairs_info.append(
            {"original_name": fname, "ext": os.path.splitext(fname)[1]}
        )

    random.shuffle(original_pairs_info)  # Shuffle the list of dicts

    # Generate new sequential names (e.g., 00001.ext, 00002.ext)
    # The new name will use the original extension of the file it's being assigned to after shuffle.

    processed_count = 0
    errors = []

    # Temporary renaming for inplace shuffle to avoid collisions
    # (e.g. a.jpg -> 00001.jpg, b.jpg -> a.jpg - this would fail without temp)
    temp_suffix = "_shuffletemp_" + str(
        random.randint(10000, 99999)
    )  # Unique temp suffix

    # --- Stage 1: Copy or Move to destination (if not inplace), or rename to temp (if inplace) ---
    # This list will hold info about files in their (potentially new) locations before final renaming.
    files_in_final_location_for_renaming = []

    print(f"\nStage 1: Preparing files for shuffling ({operation})...")
    if operation == "inplace":
        # Rename to temporary names in source folders
        for idx, pair_info in enumerate(
            tqdm(original_pairs_info, desc="Renaming to Temp (Inplace)")
        ):
            orig_name = pair_info["original_name"]
            ext = pair_info["ext"]

            hq_src_path = os.path.join(hq_folder, orig_name)
            lq_src_path = os.path.join(lq_folder, orig_name)

            # Create a unique temporary name that's unlikely to already exist or be a target name
            temp_name_base = f"{idx:05d}{temp_suffix}"
            hq_temp_path = os.path.join(hq_folder, temp_name_base + ext)
            lq_temp_path = os.path.join(lq_folder, temp_name_base + ext)

            try:
                if os.path.exists(hq_src_path):
                    os.rename(hq_src_path, hq_temp_path)
                else:
                    errors.append(f"Inplace-Temp: HQ Source {hq_src_path} not found.")
                    continue
                if os.path.exists(lq_src_path):
                    os.rename(lq_src_path, lq_temp_path)
                else:  # Rollback HQ rename if LQ fails
                    os.rename(hq_temp_path, hq_src_path)
                    errors.append(
                        f"Inplace-Temp: LQ Source {lq_src_path} not found. HQ rename for {orig_name} rolled back."
                    )
                    continue

                files_in_final_location_for_renaming.append(
                    {
                        "current_hq_path": hq_temp_path,
                        "current_lq_path": lq_temp_path,
                        "original_ext": ext,  # This is the extension of the file that will eventually get this slot's new name.
                        # No, this should be the extension of THIS file.
                        # The `original_pairs_info` is shuffled.
                        # The new name (00001, 00002) will take *this* file's extension.
                    }
                )
            except Exception as e:
                errors.append(f"Error renaming {orig_name} to temporary: {e}")
    else:  # "copy" or "move"
        for pair_info in tqdm(
            original_pairs_info, desc=f"{operation.capitalize()}ing to Destination"
        ):
            orig_name = pair_info["original_name"]
            ext = pair_info["ext"]

            hq_src_path = os.path.join(hq_folder, orig_name)
            lq_src_path = os.path.join(lq_folder, orig_name)

            # Destination files will initially keep their original names in the new location
            # get_unique_filename is important if multiple source datasets could have same names.
            # Here, `orig_name` is already unique within its source, so unique check is for destination.

            # For shuffle, the crucial part is that the *pairing* based on original names is maintained
            # during copy/move, and *then* they are renamed according to the shuffle order.
            # The `original_pairs_info` is ALREADY shuffled.
            # So, `pair_info` is for the file that will end up at a certain position in the shuffle.

            # Let's re-think. `original_pairs_info` is a shuffled list of what *was* in the source.
            # We need to copy/move these files using their original names, then rename them
            # based on their new position in the `original_pairs_info` list.

            # No, the current `pair_info` from `original_pairs_info` (which is shuffled) IS the file
            # that should receive the (idx+1)th name.

            # If copying/moving, the file `orig_name` is processed. Its new name will be based on its
            # position in the shuffled list `original_pairs_info`.

            # Correct approach for copy/move:
            # Iterate 0 to N-1 for new names. `original_pairs_info[i]` is the original file that gets new name `i`.
            # This is what the original script was closer to for copy/move.

            # Let's stick to: `original_pairs_info` is shuffled. Iterate through it.
            # Each item `pair_info` represents an original file.
            # This file will be given a new name corresponding to its current index in the shuffled list.

            hq_dest_path_initial = os.path.join(
                output_hq_dir, get_unique_filename(output_hq_dir, orig_name)
            )
            lq_dest_path_initial = os.path.join(
                output_lq_dir, get_unique_filename(output_lq_dir, orig_name)
            )

            try:
                if operation == "copy":
                    if os.path.exists(hq_src_path):
                        shutil.copy2(hq_src_path, hq_dest_path_initial)
                    else:
                        errors.append(f"Copy: HQ Source {hq_src_path} not found.")
                        continue
                    if os.path.exists(lq_src_path):
                        shutil.copy2(lq_src_path, lq_dest_path_initial)
                    else:
                        errors.append(f"Copy: LQ Source {lq_src_path} not found.")
                        os.remove(hq_dest_path_initial)
                        continue  # Clean up copied HQ
                elif operation == "move":
                    if os.path.exists(hq_src_path):
                        shutil.move(hq_src_path, hq_dest_path_initial)
                    else:
                        errors.append(f"Move: HQ Source {hq_src_path} not found.")
                        continue
                    if os.path.exists(lq_src_path):
                        shutil.move(lq_src_path, lq_dest_path_initial)
                    else:  # This case is tricky for move, as HQ is already gone. Log error.
                        errors.append(
                            f"Move: LQ Source {lq_src_path} not found after HQ was moved. HQ is at {hq_dest_path_initial}."
                        )
                        continue

                files_in_final_location_for_renaming.append(
                    {
                        "current_hq_path": hq_dest_path_initial,  # Path in the *new* directory
                        "current_lq_path": lq_dest_path_initial,  # Path in the *new* directory
                        "original_ext": ext,  # The extension of this specific file.
                    }
                )
            except Exception as e:
                errors.append(
                    f"Error {operation}ing file {orig_name} to destination: {e}"
                )

    # --- Stage 2: Rename files (which are now in their final folders) to new sequential shuffled names ---
    print(f"\nStage 2: Renaming files to final shuffled order...")
    # `files_in_final_location_for_renaming` now contains paths to files that are
    # either temp-named (inplace) or copied/moved to destination with original-ish names.
    # The order of this list corresponds to the shuffled order.

    for idx, file_detail in enumerate(
        tqdm(files_in_final_location_for_renaming, desc="Final Renaming")
    ):
        # The new name is based on the index 'idx' in the shuffled list.
        # The extension comes from the file itself (which was stored in 'original_ext' or can be derived).
        current_hq_path = file_detail["current_hq_path"]
        current_lq_path = file_detail["current_lq_path"]
        # Get extension from current path, as original_ext might be from a different context if logic was mixed.
        # Safest is to get ext from current_hq_path (assuming hq/lq share it)
        ext_for_new_name = os.path.splitext(current_hq_path)[1]

        new_name_base = f"{idx+1:05d}"  # e.g., 00001, 00002
        final_hq_name = new_name_base + ext_for_new_name
        final_lq_name = new_name_base + ext_for_new_name

        # The directory for renaming is the directory of the current_path
        final_hq_path = os.path.join(os.path.dirname(current_hq_path), final_hq_name)
        final_lq_path = os.path.join(os.path.dirname(current_lq_path), final_lq_name)

        try:
            # Avoid renaming to itself if names collide due to prior unique naming, though unlikely with sequential.
            if current_hq_path != final_hq_path:
                # Ensure final path doesn't exist if we are not careful with get_unique_filename logic before.
                # However, for sequential renaming, this should be fine.
                if os.path.exists(final_hq_path):
                    errors.append(
                        f"Final Renaming: Target HQ path {final_hq_path} unexpectedly exists before rename."
                    )
                    continue
                os.rename(current_hq_path, final_hq_path)

            if current_lq_path != final_lq_path:
                if os.path.exists(final_lq_path):
                    errors.append(
                        f"Final Renaming: Target LQ path {final_lq_path} unexpectedly exists before rename."
                    )
                    os.rename(final_hq_path, current_hq_path)
                    continue  # Rollback HQ
                os.rename(current_lq_path, final_lq_path)

            processed_count += 1
        except Exception as e:
            errors.append(
                f"Error during final rename of '{os.path.basename(current_hq_path)}' to '{final_hq_name}': {e}"
            )

    # Cleanup: Remove original files if operation was 'move' and it was done in stages (not directly relevant here as move is to new name)
    # The current logic for 'move' already puts it in the final place with a temp/original name.

    print("\n" + "-" * 30)
    print("  Shuffle Image Pairs Summary")
    print("-" * 30)
    print(f"Total matching pairs considered: {len(matching_files)}")
    print(f"Successfully processed (shuffled & renamed): {processed_count} pairs.")
    if operation == "inplace":
        print(f"  Files were renamed in-place in {hq_folder} and {lq_folder}.")
    else:
        print(
            f"  Files were {operation}d and renamed in {output_hq_dir} and {output_lq_dir}."
        )

    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error_msg in enumerate(
            errors[: min(len(errors), 10)]
        ):  # Show more errors if many
            print(f"  - {error_msg}")
        if len(errors) > 10:
            print(
                f"  ... and {len(errors) - 10} more issues (check log if detailed logging was added)."
            )
    print("-" * 30)
    print("=" * 30)


def transform_dataset(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Transforming Dataset")
    print("=" * 30)

    BATCH_SIZE = 1000  # Process this many pairs at a time

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
    matching_files = [f for f in hq_files_list if f in lq_files_list]

    if not matching_files:
        print("No matching HQ/LQ pairs found for transformation.")
        print("=" * 30)
        return

    # Get subset of pairs to process
    files_to_process = get_pairs_to_process(matching_files, operation_name="transform")
    if not files_to_process:
        print("=" * 30)
        return

    num_selected_for_transform = len(files_to_process)

    transform_options = {
        "1": "brightness",
        "2": "contrast",
        "3": "saturation",
        "4": "sharpness",
        "5": "rotate",
        "6": "flip_horizontal",
        "7": "flip_vertical",
        "8": "grayscale",
    }

    print("\nSelect a transformation:")
    for key, value in transform_options.items():
        print(f"  {key}. {value.replace('_', ' ').capitalize()}")

    while True:
        transform_choice = input("Enter the number of your choice: ").strip()
        if transform_choice in transform_options:
            selected_transform = transform_options[transform_choice]
            break
        else:
            print("Invalid choice. Please enter a valid number.")

    value = (
        None  # For transforms like flip/grayscale, value is not directly used from user
    )
    if selected_transform in ["brightness", "contrast", "saturation", "sharpness"]:
        while True:
            try:
                val_str = input(
                    f"Enter {selected_transform} factor (e.g., 0.5 for half, 1.0 for original, 1.5 for 50% more): "
                ).strip()
                value = float(val_str)
                if value >= 0:  # Allow 0 for some factors, e.g., brightness to black
                    break
                else:
                    print("Factor must be non-negative.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    elif selected_transform == "rotate":
        while True:
            try:
                val_str = input(
                    "Enter rotation angle in degrees (e.g., 90, -90, 180). Positive = counter-clockwise: "
                ).strip()
                value = float(val_str)  # Allow float angles
                break
            except ValueError:
                print("Invalid input. Please enter a number for angle.")

    operation = get_file_operation_choice()

    destination_hq_folder = ""
    destination_lq_folder = ""
    if operation != "inplace":
        output_base_dir_prompt = (
            f"Enter base destination directory for {operation}ed transformed pairs: "
        )
        output_base_dir = (
            get_destination_path(prompt=output_base_dir_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not output_base_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        # Sanitize transform name for folder
        sane_transform_name = selected_transform.replace("_", "-")
        destination_hq_folder = os.path.join(
            output_base_dir, f"transformed_{sane_transform_name}_hq"
        )
        destination_lq_folder = os.path.join(
            output_base_dir, f"transformed_{sane_transform_name}_lq"
        )
        os.makedirs(destination_hq_folder, exist_ok=True)
        os.makedirs(destination_lq_folder, exist_ok=True)
        print(
            f"Transformed pairs will be {operation}d to respective subfolders in {output_base_dir}"
        )
    else:
        print(
            f"Performing '{selected_transform}' transformation in-place on {num_selected_for_transform} selected pairs."
        )

    processed_count = 0
    errors = []

    print(
        f"\nApplying transformation ({selected_transform}) to {num_selected_for_transform} randomly selected and ordered pairs..."
    )

    # Batching loop
    for batch_start in range(0, len(files_to_process), BATCH_SIZE):
        batch = files_to_process[batch_start : batch_start + BATCH_SIZE]
        print(f"Processing batch {batch_start//BATCH_SIZE+1} ({len(batch)} pairs)...")
        for filename in tqdm(
            batch,
            desc=f"Transforming Pairs ({selected_transform}) [Batch {batch_start//BATCH_SIZE+1}]",
        ):
            hq_src_path = os.path.join(hq_folder, filename)
            lq_src_path = os.path.join(lq_folder, filename)

            hq_dest_path_for_apply = None
            lq_dest_path_for_apply = None

            if operation != "inplace":
                hq_dest_path_for_apply = os.path.join(
                    destination_hq_folder,
                    get_unique_filename(destination_hq_folder, filename),
                )
                lq_dest_path_for_apply = os.path.join(
                    destination_lq_folder,
                    get_unique_filename(destination_lq_folder, filename),
                )
            else:  # inplace
                hq_dest_path_for_apply = hq_src_path  # For inplace, apply_transformation saves to source path
                lq_dest_path_for_apply = lq_src_path

            hq_success = apply_transformation_to_image(
                hq_src_path,
                selected_transform,
                value,
                operation,
                hq_dest_path_for_apply,
            )
            lq_success = False  # Initialize
            if (
                hq_success or operation != "move"
            ):  # If HQ failed on move, LQ source might still be there to try
                # If HQ succeeded on move, LQ source is gone unless it's a different file (not a pair)
                # This logic assumes paired operations. If HQ move failed, LQ src is still there.
                # If HQ move succeeded, LQ src should also be moved from original.
                # For 'move', apply_transformation_to_image handles removal of src_path *after* saving to dest_path.
                # So, lq_src_path should still be original path.
                lq_success = apply_transformation_to_image(
                    lq_src_path,
                    selected_transform,
                    value,
                    operation,
                    lq_dest_path_for_apply,
                )

            if hq_success and lq_success:
                processed_count += 1
            else:
                # Construct more detailed error
                err_msg = f"Pair {filename}: "
                if not hq_success:
                    err_msg += f"HQ failed. "
                if not lq_success:
                    err_msg += f"LQ failed."
                errors.append(err_msg)
                logging.warning(
                    f"Failed to fully transform pair {filename}. HQ status: {hq_success}, LQ status: {lq_success}"
                )

    print("\n" + "-" * 30)
    print("  Transform Dataset Summary")
    print("-" * 30)
    print(
        f"Transformation: {selected_transform} (Value: {value if value is not None else 'N/A'})"
    )
    print(f"Operation: {operation.capitalize()}")
    print(f"Total matching pairs in source: {len(matching_files)}")
    print(f"Number of pairs selected for transformation: {num_selected_for_transform}")
    print(f"Successfully transformed: {processed_count} pairs.")
    if errors:
        print(f"Errors or partial failures encountered for {len(errors)} pairs:")
        for i, error_msg in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error_msg}")
        if len(errors) > 5:
            print(
                f"  ... and {len(errors) - 5} more issues (check console/log for details)."
            )
    print("-" * 30)
    print("=" * 30)


def dataset_colour_adjustment(hq_folder, lq_folder):
    """Adjust color properties of HQ/LQ images using ColorAdjuster class."""
    print("\n" + "=" * 30)
    print("  Dataset Color Adjustment")
    print("=" * 30)

    adjustment_type = (
        input("Enter adjustment type (brightness/contrast/color/sharpness): ")
        .strip()
        .lower()
    )
    try:
        factor = float(input("Enter adjustment factor (e.g., 1.2 for +20%): ").strip())
    except Exception:
        print("Invalid factor. Aborting.")
        return
    operation = get_file_operation_choice()
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path()
        if not dest_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(dest_dir, exist_ok=True)

    adjuster = ColorAdjuster(adjustment_type, factor)
    for folder, label in [(hq_folder, "HQ"), (lq_folder, "LQ")]:
        image_files = [
            f
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and is_image_file(f)
        ]
        for filename in tqdm(image_files, desc=f"Adjusting {label}"):
            src_path = os.path.join(folder, filename)
            dest_path = (
                src_path
                if operation == "inplace"
                else os.path.join(dest_dir, get_unique_filename(dest_dir, filename))
            )
            success, msg = adjuster.process(
                src_path, output_path=dest_path, operation=operation
            )
            if not success:
                print(f"Error adjusting {label} {filename}: {msg}")
    print("Adjustment complete.")


def grayscale_conversion(hq_folder, lq_folder):
    """Convert HQ/LQ images to grayscale using ColorAdjuster class."""
    print("\n" + "=" * 30)
    print("  Grayscale Conversion")
    print("=" * 30)

    operation = get_file_operation_choice()
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path()
        if not dest_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(dest_dir, exist_ok=True)

    for folder, label in [(hq_folder, "HQ"), (lq_folder, "LQ")]:
        image_files = [
            f
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and is_image_file(f)
        ]
        for filename in tqdm(image_files, desc=f"Converting {label}"):
            src_path = os.path.join(folder, filename)
            dest_path = (
                src_path
                if operation == "inplace"
                else os.path.join(dest_dir, get_unique_filename(dest_dir, filename))
            )
            # Use ColorAdjuster with adjustment_type 'color' and factor 0 for grayscale
            adjuster = ColorAdjuster("color", 0)
            success, msg = adjuster.process(
                src_path, output_path=dest_path, operation=operation
            )
            if not success:
                print(f"Error converting {label} {filename}: {msg}")
    print("Grayscale conversion complete.")


def remove_small_image_pairs(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Removing Small Image Pairs")
    print("=" * 30)

    while True:
        try:
            min_size = int(input("Enter the minimum allowed dimension (e.g., 80): "))
            if min_size >= 0:
                break
            else:
                print("Please enter a non-negative integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    operation = get_file_operation_choice()
    destination = ""
    if operation == "move":
        destination = get_destination_path()
        if not destination:
            print("Operation aborted as no destination path was provided for move.")
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)
    elif operation == "copy":
        destination = get_destination_path()
        if not destination:
            print("Operation aborted as no destination path was provided for copy.")
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)

    removed_count = 0
    checked_count = 0
    errors = []

    lq_files = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    # Filter to only include pairs that exist in both folders
    hq_files_set = set(os.listdir(hq_folder))
    matching_files = [f for f in lq_files if f in hq_files_set and is_image_file(f)]

    print(f"Checking {len(matching_files)} HQ/LQ pairs...")

    for filename in tqdm(matching_files, desc="Processing Small Pairs"):
        lq_path = os.path.join(lq_folder, filename)
        hq_path = os.path.join(hq_folder, filename)

        # This check is redundant due to pre-filtering, but kept for safety.
        if not os.path.isfile(hq_path):
            # errors.append(f"Skipping {filename}: HQ pair not found.") # Should not happen with matching_files
            continue

        checked_count += 1

        lq_is_small = is_small(lq_path, min_size)
        hq_is_small = is_small(hq_path, min_size)

        if lq_is_small or hq_is_small:
            try:
                if operation == "inplace":
                    # For remove, inplace means direct deletion
                    os.remove(lq_path)
                    os.remove(hq_path)
                    # logging.info(f"Removed (inplace) small pair: {filename}")
                else:  # copy or move
                    hq_dest_folder = os.path.join(destination, "hq")
                    lq_dest_folder = os.path.join(destination, "lq")
                    hq_dest_path = os.path.join(
                        hq_dest_folder,
                        get_unique_filename(hq_dest_folder, filename),
                    )
                    lq_dest_path = os.path.join(
                        lq_dest_folder,
                        get_unique_filename(lq_dest_folder, filename),
                    )

                    if operation == "copy":
                        shutil.copy2(hq_path, hq_dest_path)
                        shutil.copy2(lq_path, lq_dest_path)
                        # logging.info(f"Copied small pair {filename} to {destination}")
                    elif operation == "move":
                        shutil.move(hq_path, hq_dest_path)
                        shutil.move(lq_path, lq_dest_path)
                        # logging.info(f"Moved small pair {filename} to {destination}")
                removed_count += 1
            except Exception as e:
                errors.append(f"Error {operation}ing {filename}: {e}")
                logging.error(f"Error {operation}ing small pair {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove Small Pairs Summary")
    print("-" * 30)
    print(f"Checked {checked_count} pairs.")
    print(
        f"Processed ({operation}ed) {removed_count} image pairs where either dimension was smaller than {min_size}."
    )
    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    print("-" * 30)
    print("=" * 30)


def split_adjust_dataset(hq_folder, lq_folder):
    print("\nSplit/Adjust Dataset Options:")
    print(
        "  1. Split dataset in half (moves/copies to subfolders 'split_1', 'split_2')"
    )
    print(
        "  2. Remove pairs by count or percentage (deletes or moves/copies to 'removed')"
    )
    print("  3. Remove pairs by file size (deletes or moves/copies to 'size_criteria')")
    print(
        "  4. Remove pairs by dimensions (deletes or moves/copies to 'dimension_criteria')"
    )
    print(
        "  5. Remove pairs by file type (deletes or moves/copies to 'filetype_criteria')"
    )
    print("  6. Back to main menu")

    while True:
        choice = input("Enter your choice for Split/Adjust: ").strip()
        if choice == "1":
            split_dataset_in_half(hq_folder, lq_folder)
        elif choice == "2":
            remove_pairs_by_count_percentage(hq_folder, lq_folder)
        elif choice == "3":
            remove_pairs_by_size(hq_folder, lq_folder)
        elif choice == "4":
            remove_pairs_by_dimensions(hq_folder, lq_folder)
        elif choice == "5":
            remove_pairs_by_file_type(hq_folder, lq_folder)
        elif choice == "6":
            break
        else:
            print("Invalid choice for Split/Adjust. Please try again.")
        # After an operation, re-display split/adjust menu or break to main?
        # Current: re-displays split/adjust menu. User must select 6 to go back.


def optimize_png_menu(hq_folder, lq_folder):
    import glob
    import shutil
    from PIL import Image
    import subprocess
    import sys
    import os

    print("\n" + "=" * 30)
    print("  Optimize PNG Images")
    print("=" * 30)

    if not hq_folder and not lq_folder:
        print("No HQ or LQ folder set. Please set folders first.")
        return

    print("Which folder(s) do you want to optimize?")
    print("  1. HQ folder only")
    print("  2. LQ folder only")
    print("  3. Both HQ and LQ folders")
    while True:
        choice = input("Enter choice (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("Invalid choice. Please enter 1, 2, or 3.")

    folders = []
    if choice == "1":
        folders = [(hq_folder, "HQ")]
    elif choice == "2":
        folders = [(lq_folder, "LQ")]
    else:
        folders = [(hq_folder, "HQ"), (lq_folder, "LQ")]

    for folder, label in folders:
        if not folder or not os.path.isdir(folder):
            print(f"{label} folder not set or does not exist. Skipping.")
            continue
        print(f"\nProcessing {label} folder: {folder}")
        image_files = [
            f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))
        ]
        png_files = []
        for fname in image_files:
            src_path = os.path.join(folder, fname)
            base, ext = os.path.splitext(fname)
            if ext.lower() == ".png":
                png_files.append(src_path)
                continue
            # Convert to PNG
            try:
                with Image.open(src_path) as img:
                    png_path = os.path.join(folder, base + ".png")
                    img.save(png_path, format="PNG")
                    png_files.append(png_path)
                # Optionally, remove the original file (ask user)
                # os.remove(src_path)
            except Exception as e:
                print(f"Failed to convert {fname} to PNG: {e}")
        if not png_files:
            print(f"No PNG files to optimize in {label} folder.")
            continue
        # Run oxipng
        print(f"Optimizing {len(png_files)} PNG files in {label} folder with oxipng...")
        try:
            # Check if oxipng is installed
            result = subprocess.run(["oxipng", "--version"], capture_output=True)
            if result.returncode != 0:
                print(
                    "oxipng is not installed or not found in PATH. Please install oxipng."
                )
                continue
        except FileNotFoundError:
            print(
                "oxipng is not installed or not found in PATH. Please install oxipng."
            )
            continue
        # Run oxipng on all PNGs in the folder
        try:
            # Use -o 4 --strip safe --alpha
            cmd = ["oxipng", "-o", "4", "--strip", "safe", "--alpha"] + png_files
            subprocess.run(cmd, check=True)
            print(f"oxipng optimization complete for {label} folder.")
        except CalledProcessError as e:
            print(f"oxipng failed: {e}")
        except Exception as e:
            print(f"Error running oxipng: {e}")
    print("\nPNG optimization finished.")
    print("=" * 30)


def convert_to_webp_menu(hq_folder, lq_folder):
    import os
    from PIL import Image

    print("\n" + "=" * 30)
    print("  Convert Images to WebP")
    print("=" * 30)

    if not hq_folder and not lq_folder:
        print("No HQ or LQ folder set. Please set folders first.")
        return

    print("Which folder(s) do you want to convert?")
    print("  1. HQ folder only")
    print("  2. LQ folder only")
    print("  3. Both HQ and LQ folders")
    while True:
        choice = input("Enter choice (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("Invalid choice. Please enter 1, 2, or 3.")

    folders = []
    if choice == "1":
        folders = [(hq_folder, "HQ")]
    elif choice == "2":
        folders = [(lq_folder, "LQ")]
    else:
        folders = [(hq_folder, "HQ"), (lq_folder, "LQ")]

    remove_original = None
    while remove_original not in ["y", "n"]:
        remove_original = (
            input("Remove original files after conversion? (y/n): ").strip().lower()
        )

    for folder, label in folders:
        if not folder or not os.path.isdir(folder):
            print(f"{label} folder not set or does not exist. Skipping.")
            continue
        print(f"\nProcessing {label} folder: {folder}")
        image_files = [
            f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))
        ]
        converted = 0
        errors = 0
        for fname in image_files:
            src_path = os.path.join(folder, fname)
            base, ext = os.path.splitext(fname)
            if ext.lower() == ".webp":
                continue
            try:
                with Image.open(src_path) as img:
                    webp_path = os.path.join(folder, base + ".webp")
                    img.save(webp_path, format="WEBP", quality=95)
                if remove_original == "y":
                    os.remove(src_path)
                converted += 1
            except Exception as e:
                print(f"Failed to convert {fname} to WebP: {e}")
                errors += 1
        print(
            f"Converted {converted} images to WebP in {label} folder. Errors: {errors}"
        )
    print("\nWebP conversion finished.")
    print("=" * 30)


# --- DPID Implementation: BasicSR ---
def dpid_basicsr(img, h, w, l=0.5):
    # img: float32, range [0, 1]
    img = np.clip(img, 0, 1)
    img_lr = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
    img_sr = cv2.resize(
        img_lr, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR
    )
    detail = img - img_sr
    img_lr = img_lr + l * cv2.resize(detail, (w, h), interpolation=cv2.INTER_LINEAR)
    img_lr = np.clip(img_lr, 0, 1)
    return img_lr


# --- DPID Implementation: OpenMMLab ---
def dpid_openmmlab(img, h, w, l=0.5):
    # img: float32, range [0, 1]
    # This is a direct adaptation of the BasicSR version, as OpenMMLab's is nearly identical for DPID
    img = np.clip(img, 0, 1)
    img_lr = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
    img_sr = cv2.resize(
        img_lr, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR
    )
    detail = img - img_sr
    img_lr = img_lr + l * cv2.resize(detail, (w, h), interpolation=cv2.INTER_LINEAR)
    img_lr = np.clip(img_lr, 0, 1)
    return img_lr


# --- Downsampling Menu ---
def downsample_images_menu():
    print("\n=== Downsample Images (Batch/Single, Multiple Methods) ===")
    print("Select downsampling implementation:")
    print("  1. DPID (BasicSR)")
    print("  2. DPID (OpenMMLab)")
    print("  3. OpenCV INTER_AREA")
    print("  4. OpenCV INTER_LANCZOS4")
    print("  5. OpenCV INTER_CUBIC")
    print("  6. PIL LANCZOS")
    print("  7. Phhofm's DPID Downscaler (pepedpid)")
    method = input("Enter method number (default 1): ").strip() or "1"
    if method != "7":
        # ... existing code for other methods ...
        input_folder = input("Enter path to HR (100%) images folder: ").strip()
        if not os.path.isdir(input_folder):
            print(f"Input folder '{input_folder}' does not exist.")
            return
        output_folder = input(
            "Enter base output folder (subfolders will be created for each scale): "
        ).strip()
        if not output_folder:
            print("Output folder is required.")
            return
        os.makedirs(output_folder, exist_ok=True)
        # Scales
        scale_str = input(
            "Enter scale factors (comma-separated, e.g. 0.75,0.5,0.25): "
        ).strip()
        try:
            scales = [float(s) for s in scale_str.split(",") if 0 < float(s) < 1]
        except Exception:
            print("Invalid scale factors.")
            return
        if not scales:
            print("No valid scales provided.")
            return
        dpid_lambda = 0.5
        if method in ["1", "2"]:
            try:
                dpid_lambda = float(
                    input(
                        "Enter DPID lambda (0=smooth, 1=detail, default 0.5): "
                    ).strip()
                    or 0.5
                )
            except Exception:
                dpid_lambda = 0.5
        # ... rest of existing code for other methods ...
        # ...
        # (Unchanged)
        # ...
        return
    # --- Phhofm's DPID Downscaler integration ---
    from dataset_forge import dpid_phhofm

    print("Phhofm's DPID Downscaler selected.")
    print("Choose mode:")
    print("  1. Single folder")
    print("  2. HQ/LQ paired folders (preserve alignment)")
    mode = input("Select mode (1=single, 2=pair): ").strip()
    if mode == "2":
        hq_folder = input("Enter HQ folder path: ").strip()
        lq_folder = input("Enter LQ folder path: ").strip()
        out_hq_folder = input("Enter HQ output folder: ").strip()
        out_lq_folder = input("Enter LQ output folder: ").strip()
        scale = input("Enter downscale factor (integer >=2, e.g. 2, 3, 4): ").strip()
        try:
            scale = int(scale)
            if scale < 2:
                raise ValueError
        except Exception:
            print("Invalid scale factor.")
            return
        output_ext = (
            input("Output extension (.png/.jpg/.webp, default .png): ").strip()
            or ".png"
        )
        threads = input("Threads (default 4): ").strip()
        try:
            threads = int(threads) if threads else 4
        except Exception:
            threads = 4
        skip_existing = (
            input("Skip existing files? (y/n, default n): ").strip().lower() == "y"
        )
        verbose = input("Verbose output? (y/n, default n): ").strip().lower() == "y"
        processed, skipped, failed = dpid_phhofm.downscale_hq_lq_pair(
            hq_folder,
            lq_folder,
            out_hq_folder,
            out_lq_folder,
            scale,
            output_ext=output_ext,
            threads=threads,
            skip_existing=skip_existing,
            verbose=verbose,
        )
        print(f"\nOperation complete:")
        print(f"  Processed: {processed} pairs")
        print(f"  Skipped:   {skipped} pairs")
        print(f"  Failed:    {failed} pairs")
        print(f"  Output HQ: {out_hq_folder}")
        print(f"  Output LQ: {out_lq_folder}")
    else:
        input_folder = input("Enter input folder path: ").strip()
        output_folder = input("Enter output folder path: ").strip()
        scale = input("Enter downscale factor (integer >=2, e.g. 2, 3, 4): ").strip()
        try:
            scale = int(scale)
            if scale < 2:
                raise ValueError
        except Exception:
            print("Invalid scale factor.")
            return
        output_ext = (
            input("Output extension (.png/.jpg/.webp, default .png): ").strip()
            or ".png"
        )
        threads = input("Threads (default 4): ").strip()
        try:
            threads = int(threads) if threads else 4
        except Exception:
            threads = 4
        recursive = (
            input("Process subdirectories recursively? (y/n, default n): ")
            .strip()
            .lower()
            == "y"
        )
        skip_existing = (
            input("Skip existing files? (y/n, default n): ").strip().lower() == "y"
        )
        verbose = input("Verbose output? (y/n, default n): ").strip().lower() == "y"
        processed, skipped, failed = dpid_phhofm.downscale_folder(
            input_folder,
            output_folder,
            scale,
            output_ext=output_ext,
            threads=threads,
            recursive=recursive,
            skip_existing=skip_existing,
            verbose=verbose,
        )
        print(f"\nOperation complete:")
        print(f"  Processed: {processed} images")
        print(f"  Skipped:   {skipped} images")
        print(f"  Failed:    {failed} images")
        print(f"  Output:    {output_folder}")


class ToneMapper:
    """Base class for HDR to SDR tone mapping using ffmpeg."""

    def __init__(self, algorithm="hable"):
        self.algorithm = algorithm

    def ffmpeg_command(self, input_path, output_path):
        # Compose the ffmpeg command for the selected algorithm
        return [
            "ffmpeg",
            "-i",
            input_path,
            "-vf",
            f"zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap={self.algorithm}:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            output_path,
        ]

    def run(self, input_path, output_path):
        cmd = self.ffmpeg_command(input_path, output_path)
        print("\nRunning ffmpeg command:")
        print(" ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
            print(f"\nTone mapping complete! Output: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error running ffmpeg: {e}")


def hdr_to_sdr_menu():
    print("\n=== HDR to SDR Tone Mapping ===")
    input_path = input("Enter path to input HDR video: ").strip()
    if not input_path or not os.path.isfile(input_path):
        print(f"Input file '{input_path}' does not exist.")
        return
    output_path = input("Enter path for output SDR video: ").strip()
    if not output_path:
        print("Output path is required.")
        return
    print("Select tone mapping algorithm:")
    print("  1. hable (default)")
    print("  2. reinhard")
    print("  3. mobius")
    algo_choice = input("Enter algorithm number (1/2/3): ").strip() or "1"
    algo_map = {"1": "hable", "2": "reinhard", "3": "mobius"}
    algorithm = algo_map.get(algo_choice, "hable")
    tonemapper = ToneMapper(algorithm=algorithm)
    tonemapper.run(input_path, output_path)


def split_single_folder_in_sets(folder):
    print("\n" + "=" * 30)
    print("  Splitting Single Folder Dataset")
    print("=" * 30)

    files = sorted(
        [
            f
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and is_image_file(f)
        ]
    )

    if not files:
        print("No images found in the folder.")
        print("=" * 30)
        return

    num_files = len(files)
    # Ask user for number of splits
    while True:
        n_splits_input = input("How many splits? (default: 2): ").strip()
        if not n_splits_input:
            n_splits = 2
            break
        try:
            n_splits = int(n_splits_input)
            if n_splits >= 2:
                break
            else:
                print("Please enter a number >= 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Ask user for split ratios
    while True:
        if n_splits == 2:
            prompt = "Enter split ratio as percentage for first set (e.g., 50 for 50/50, 80 for 80/20) [default: 50]: "
        else:
            prompt = f"Enter split ratios as comma-separated percentages for {n_splits} sets (e.g., 60,20,20): "
        split_input = input(prompt).strip()
        if not split_input and n_splits == 2:
            split_ratios = [0.5, 0.5]
            break
        try:
            if n_splits == 2 and split_input:
                split_val = float(split_input)
                if 0 < split_val < 100:
                    split_ratios = [split_val / 100.0, 1 - (split_val / 100.0)]
                    break
                else:
                    print("Please enter a value between 1 and 99.")
            else:
                parts = [float(x.strip()) for x in split_input.split(",") if x.strip()]
                if len(parts) != n_splits:
                    print(f"Please enter {n_splits} values.")
                    continue
                total = sum(parts)
                if abs(total - 100.0) > 1e-3:
                    print("Split ratios must sum to 100.")
                    continue
                split_ratios = [x / 100.0 for x in parts]
                break
        except ValueError:
            print("Invalid input. Please enter numbers.")

    # Shuffle before splitting to ensure random distribution if desired
    shuffle_choice = (
        input("Shuffle files before splitting? (y/n) [n]: ").strip().lower() or "n"
    )
    if shuffle_choice == "y":
        import random

        random.shuffle(files)

    # Compute split indices
    split_indices = [0]
    acc = 0
    for ratio in split_ratios:
        acc += int(round(ratio * num_files))
        split_indices.append(acc)
    # Adjust last index to ensure all files are included (due to rounding)
    split_indices[-1] = num_files

    split_file_lists = [
        files[split_indices[i] : split_indices[i + 1]] for i in range(n_splits)
    ]

    print(
        f"Found {num_files} images. Splitting into {[len(lst) for lst in split_file_lists]} for each set."
    )

    # Ask for operation
    while True:
        operation = (
            input("Operation [copy/move] (default: copy): ").strip().lower() or "copy"
        )
        if operation in ("copy", "move"):
            break
        print("Invalid operation. Please enter 'copy' or 'move'.")

    # Ask for destination folder
    while True:
        output_base_dir = input("Enter destination folder for split output: ").strip()
        if output_base_dir:
            break
        print("Destination folder is required.")

    output_dirs = []
    for i in range(n_splits):
        d = os.path.join(output_base_dir, f"split_{i+1}")
        os.makedirs(d, exist_ok=True)
        output_dirs.append(d)

    processed_counts = [0] * n_splits
    error_lists = [[] for _ in range(n_splits)]

    for i, file_list in enumerate(split_file_lists):
        print(f"\nProcessing set {i+1} ({len(file_list)} images) using {operation}...")
        for filename in tqdm(file_list, desc=f"{operation.capitalize()}ing Set {i+1}"):
            src = os.path.join(folder, filename)
            try:
                dest = os.path.join(
                    output_dirs[i], get_unique_filename(output_dirs[i], filename)
                )
                if operation == "copy":
                    shutil.copy2(src, dest)
                elif operation == "move":
                    if os.path.exists(src):
                        shutil.move(src, dest)
                    else:
                        error_lists[i].append(
                            f"Source file {filename} already moved or missing for set {i+1}."
                        )
                        continue
                processed_counts[i] += 1
            except Exception as e:
                error_lists[i].append(
                    f"Error {operation}ing file {filename} to split_{i+1}: {e}"
                )

    print("\nSplit operation complete.")
    for i, count in enumerate(processed_counts):
        print(f"Total processed into set {i+1}: {count}")
    any_errors = any(error_lists)
    if any_errors:
        print("Errors encountered during split:")
        for i, errors in enumerate(error_lists):
            for e in errors:
                print(f"  [Set {i+1}] {e}")
    print("=" * 30)
