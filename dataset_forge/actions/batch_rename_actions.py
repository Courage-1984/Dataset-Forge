import os
import shutil
import uuid
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import (
    print_success,
    print_info,
    print_error,
    print_header,
    print_section,
)
from dataset_forge.utils.audio_utils import play_done_sound


def batch_rename_menu():
    """Batch rename files in a folder or paired HQ/LQ folders with sequential numbers or custom prefix."""
    print_header("Batch Renaming Utility")
    input_path = input(
        "Enter input folder path (single folder or parent of hq/lq): "
    ).strip()
    if not os.path.exists(input_path):
        print_error(f"Input path does not exist: {input_path}")
        return
    hq_path = os.path.join(input_path, "hq")
    lq_path = os.path.join(input_path, "lq")
    is_pair = os.path.isdir(hq_path) and os.path.isdir(lq_path)
    if is_pair:
        print_info(f"Detected HQ/LQ folders: {hq_path}, {lq_path}")
    else:
        print_info(f"Detected single folder: {input_path}")
    print_info("Choose naming scheme:")
    print_info("  1. Sequential numbers (e.g., 00001, 00002)")
    print_info("  2. Custom prefix (e.g., my_dataset_00001)")
    scheme = input("Select scheme [1-2]: ").strip()
    if scheme == "2":
        prefix = input("Enter custom prefix: ").strip()
    else:
        prefix = ""
    padding = input("Enter zero padding width (default 5): ").strip()
    try:
        padding = int(padding) if padding else 5
    except Exception:
        padding = 5
    dry_run = (
        input("Dry run? (show what would be renamed, y/n, default y): ").strip().lower()
    )
    dry_run = dry_run != "n"
    if is_pair:
        batch_rename_hq_lq_folders(
            hq_path, lq_path, prefix=prefix, padding=padding, dry_run=dry_run
        )
    else:
        batch_rename_single_folder(
            input_path, prefix=prefix, padding=padding, dry_run=dry_run
        )


def batch_rename_single_folder(folder_path, prefix="", padding=5, dry_run=True):
    """Batch rename files in a single folder with sequential numbers or custom prefix."""
    files = sorted(
        [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]
    )
    print_info(f"Found {len(files)} files in {folder_path}.")

    if dry_run:
        for idx, filename in enumerate(files, 1):
            ext = os.path.splitext(filename)[1]
            new_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
            print_info(f"Would rename: {filename} -> {new_name}")
        print_info("Dry run complete. No files were renamed.")
        return

    # Two-phase approach: first rename all to temporary names, then to final names
    temp_renames = []
    final_renames = []

    # Phase 1: Create temporary names and plan final names
    for idx, filename in enumerate(files, 1):
        ext = os.path.splitext(filename)[1]
        final_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
        temp_name = f"temp_{uuid.uuid4().hex[:12]}{ext}"

        src = os.path.join(folder_path, filename)
        temp_path = os.path.join(folder_path, temp_name)
        final_path = os.path.join(folder_path, final_name)

        temp_renames.append((src, temp_path))
        final_renames.append((temp_path, final_path))

    # Phase 2: Execute temporary renames
    print_info("Phase 1: Renaming to temporary names...")
    for src, temp_path in temp_renames:
        try:
            os.rename(src, temp_path)
            log_operation("rename_temp", f"{src} -> {temp_path}")
        except FileExistsError:
            # If temp file exists, use a unique name
            base, ext = os.path.splitext(temp_path)
            counter = 1
            while os.path.exists(temp_path):
                temp_path = os.path.join(folder_path, f"{base}_{counter}{ext}")
                counter += 1
            os.rename(src, temp_path)
            log_operation("rename_temp", f"{src} -> {temp_path} (unique)")

    # Phase 3: Execute final renames
    print_info("Phase 2: Renaming to final names...")
    for temp_path, final_path in final_renames:
        try:
            os.rename(temp_path, final_path)
            log_operation("rename_final", f"{temp_path} -> {final_path}")
        except FileExistsError:
            # If final name exists, use a unique name
            base, ext = os.path.splitext(final_path)
            counter = 1
            while os.path.exists(final_path):
                final_path = os.path.join(folder_path, f"{base}_{counter}{ext}")
                counter += 1
            os.rename(temp_path, final_path)
            log_operation("rename_final", f"{temp_path} -> {final_path} (unique)")

    print_success(f"Batch renaming complete! Renamed {len(files)} files.")
    play_done_sound()


def batch_rename_hq_lq_folders(hq_path, lq_path, prefix="", padding=5, dry_run=True):
    """Batch rename HQ/LQ paired folders with sequential numbers or custom prefix."""
    hq_files = sorted(
        [f for f in os.listdir(hq_path) if os.path.isfile(os.path.join(hq_path, f))]
    )
    lq_files = sorted(
        [f for f in os.listdir(lq_path) if os.path.isfile(os.path.join(lq_path, f))]
    )
    matching_files = [f for f in hq_files if f in lq_files]
    print_info(f"Found {len(matching_files)} matching HQ/LQ pairs.")

    if dry_run:
        for idx, filename in enumerate(matching_files, 1):
            ext = os.path.splitext(filename)[1]
            new_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
            print_info(f"Would rename: {filename} -> {new_name}")
        print_info("Dry run complete. No files were renamed.")
        return

    # Two-phase approach for HQ/LQ folders
    hq_temp_renames = []
    lq_temp_renames = []
    hq_final_renames = []
    lq_final_renames = []

    # Phase 1: Create temporary names and plan final names
    for idx, filename in enumerate(matching_files, 1):
        ext = os.path.splitext(filename)[1]
        final_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
        temp_name = f"temp_{uuid.uuid4().hex[:12]}{ext}"

        hq_src = os.path.join(hq_path, filename)
        lq_src = os.path.join(lq_path, filename)
        hq_temp_path = os.path.join(hq_path, temp_name)
        lq_temp_path = os.path.join(lq_path, temp_name)
        hq_final_path = os.path.join(hq_path, final_name)
        lq_final_path = os.path.join(lq_path, final_name)

        hq_temp_renames.append((hq_src, hq_temp_path))
        lq_temp_renames.append((lq_src, lq_temp_path))
        hq_final_renames.append((hq_temp_path, hq_final_path))
        lq_final_renames.append((lq_temp_path, lq_final_path))

    # Phase 2: Execute temporary renames
    print_info("Phase 1: Renaming to temporary names...")
    for hq_src, hq_temp_path in hq_temp_renames:
        try:
            os.rename(hq_src, hq_temp_path)
            log_operation("rename_temp_hq", f"{hq_src} -> {hq_temp_path}")
        except FileExistsError:
            # If temp file exists, use a unique name
            base, ext = os.path.splitext(hq_temp_path)
            counter = 1
            while os.path.exists(hq_temp_path):
                hq_temp_path = os.path.join(hq_path, f"{base}_{counter}{ext}")
                counter += 1
            os.rename(hq_src, hq_temp_path)
            log_operation("rename_temp_hq", f"{hq_src} -> {hq_temp_path} (unique)")

    for lq_src, lq_temp_path in lq_temp_renames:
        try:
            os.rename(lq_src, lq_temp_path)
            log_operation("rename_temp_lq", f"{lq_src} -> {lq_temp_path}")
        except FileExistsError:
            # If temp file exists, use a unique name
            base, ext = os.path.splitext(lq_temp_path)
            counter = 1
            while os.path.exists(lq_temp_path):
                lq_temp_path = os.path.join(lq_path, f"{base}_{counter}{ext}")
                counter += 1
            os.rename(lq_src, lq_temp_path)
            log_operation("rename_temp_lq", f"{lq_src} -> {lq_temp_path} (unique)")

    # Phase 3: Execute final renames
    print_info("Phase 2: Renaming to final names...")
    for hq_temp_path, hq_final_path in hq_final_renames:
        try:
            os.rename(hq_temp_path, hq_final_path)
            log_operation("rename_final_hq", f"{hq_temp_path} -> {hq_final_path}")
        except FileExistsError:
            # If final name exists, use a unique name
            base, ext = os.path.splitext(hq_final_path)
            counter = 1
            while os.path.exists(hq_final_path):
                hq_final_path = os.path.join(hq_path, f"{base}_{counter}{ext}")
                counter += 1
            os.rename(hq_temp_path, hq_final_path)
            log_operation(
                "rename_final_hq", f"{hq_temp_path} -> {hq_final_path} (unique)"
            )

    for lq_temp_path, lq_final_path in lq_final_renames:
        try:
            os.rename(lq_temp_path, lq_final_path)
            log_operation("rename_final_lq", f"{lq_temp_path} -> {lq_final_path}")
        except FileExistsError:
            # If final name exists, use a unique name
            base, ext = os.path.splitext(lq_final_path)
            counter = 1
            while os.path.exists(lq_final_path):
                lq_final_path = os.path.join(lq_path, f"{base}_{counter}{ext}")
                counter += 1
            os.rename(lq_temp_path, lq_final_path)
            log_operation(
                "rename_final_lq", f"{lq_temp_path} -> {lq_final_path} (unique)"
            )

    print_success(
        f"HQ/LQ batch renaming complete! Renamed {len(matching_files)} pairs."
    )
    play_done_sound()
