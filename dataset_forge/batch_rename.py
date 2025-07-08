import os
from typing import Optional


def get_image_files(folder):
    SUPPORTED_FORMATS = (".png", ".jpg", ".jpeg", ".webp", ".tga", ".bmp", ".tiff")
    return sorted(
        [
            f
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
            and os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS
        ]
    )


def batch_rename_single_folder(
    folder: str, prefix: str = "", padding: int = 5, dry_run: bool = True
):
    files = get_image_files(folder)
    if not files:
        print(f"No images found in {folder}")
        return
    print(f"Found {len(files)} images in {folder}")
    for idx, fname in enumerate(files, 1):
        ext = os.path.splitext(fname)[1]
        new_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
        src = os.path.join(folder, fname)
        dst = os.path.join(folder, new_name)
        if dry_run:
            print(f"Would rename: {fname} -> {new_name}")
        else:
            if src != dst:
                os.rename(src, dst)
    if dry_run:
        print("Dry run complete. No files were renamed.")
    else:
        print("Renaming complete.")


def batch_rename_hq_lq_folders(
    hq_folder: str,
    lq_folder: str,
    prefix: str = "",
    padding: int = 5,
    dry_run: bool = True,
):
    hq_files = get_image_files(hq_folder)
    lq_files = get_image_files(lq_folder)
    hq_basenames = {os.path.splitext(f)[0]: f for f in hq_files}
    lq_basenames = {os.path.splitext(f)[0]: f for f in lq_files}
    common = sorted(set(hq_basenames.keys()) & set(lq_basenames.keys()))
    if not common:
        print("No matching HQ/LQ pairs found.")
        return
    print(f"Found {len(common)} HQ/LQ pairs.")
    for idx, base in enumerate(common, 1):
        hq_old = hq_basenames[base]
        lq_old = lq_basenames[base]
        hq_ext = os.path.splitext(hq_old)[1]
        lq_ext = os.path.splitext(lq_old)[1]
        new_base = f"{prefix}{str(idx).zfill(padding)}"
        hq_new = f"{new_base}{hq_ext}"
        lq_new = f"{new_base}{lq_ext}"
        hq_src = os.path.join(hq_folder, hq_old)
        hq_dst = os.path.join(hq_folder, hq_new)
        lq_src = os.path.join(lq_folder, lq_old)
        lq_dst = os.path.join(lq_folder, lq_new)
        if dry_run:
            print(f"Would rename: HQ {hq_old} -> {hq_new} | LQ {lq_old} -> {lq_new}")
        else:
            if hq_src != hq_dst:
                os.rename(hq_src, hq_dst)
            if lq_src != lq_dst:
                os.rename(lq_src, lq_dst)
    if dry_run:
        print("Dry run complete. No files were renamed.")
    else:
        print("Renaming complete.")
