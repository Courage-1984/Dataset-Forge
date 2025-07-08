import os


def batch_rename_menu():
    """Batch rename files in a folder or paired HQ/LQ folders with sequential numbers or custom prefix."""
    print("\n=== Batch Renaming Utility ===")
    input_path = input(
        "Enter input folder path (single folder or parent of hq/lq): "
    ).strip()
    if not os.path.exists(input_path):
        print(f"Input path does not exist: {input_path}")
        return
    hq_path = os.path.join(input_path, "hq")
    lq_path = os.path.join(input_path, "lq")
    is_pair = os.path.isdir(hq_path) and os.path.isdir(lq_path)
    if is_pair:
        print(f"Detected HQ/LQ folders: {hq_path}, {lq_path}")
    else:
        print(f"Detected single folder: {input_path}")
    print("Choose naming scheme:")
    print("  1. Sequential numbers (e.g., 00001, 00002)")
    print("  2. Custom prefix (e.g., my_dataset_00001)")
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


def batch_rename_hq_lq_folders(hq_path, lq_path, prefix="", padding=5, dry_run=True):
    """Batch rename HQ/LQ paired folders with sequential numbers or custom prefix."""
    hq_files = sorted(
        [f for f in os.listdir(hq_path) if os.path.isfile(os.path.join(hq_path, f))]
    )
    lq_files = sorted(
        [f for f in os.listdir(lq_path) if os.path.isfile(os.path.join(lq_path, f))]
    )
    matching_files = [f for f in hq_files if f in lq_files]
    print(f"Found {len(matching_files)} matching HQ/LQ pairs.")
    for idx, filename in enumerate(matching_files, 1):
        ext = os.path.splitext(filename)[1]
        new_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
        hq_src = os.path.join(hq_path, filename)
        lq_src = os.path.join(lq_path, filename)
        hq_dst = os.path.join(hq_path, new_name)
        lq_dst = os.path.join(lq_path, new_name)
        if dry_run:
            print(f"Would rename: {filename} -> {new_name}")
        else:
            os.rename(hq_src, hq_dst)
            os.rename(lq_src, lq_dst)
    if dry_run:
        print("Dry run complete. No files were renamed.")
    else:
        print("Batch renaming complete.")


def batch_rename_single_folder(folder_path, prefix="", padding=5, dry_run=True):
    """Batch rename files in a single folder with sequential numbers or custom prefix."""
    files = sorted(
        [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]
    )
    print(f"Found {len(files)} files in {folder_path}.")
    for idx, filename in enumerate(files, 1):
        ext = os.path.splitext(filename)[1]
        new_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
        src = os.path.join(folder_path, filename)
        dst = os.path.join(folder_path, new_name)
        if dry_run:
            print(f"Would rename: {filename} -> {new_name}")
        else:
            os.rename(src, dst)
    if dry_run:
        print("Dry run complete. No files were renamed.")
    else:
        print("Batch renaming complete.")
