import os
import random
import shutil
from PIL import Image, ImageEnhance, UnidentifiedImageError, ImageFont, ImageDraw
from collections import Counter, defaultdict
from tqdm import tqdm
import cv2
import numpy as np
import concurrent.futures
import logging
import sys
import traceback
import imageio
import torch
from dataset_forge.io_utils import (
    log_uncaught_exceptions,
    get_folder_path,
    get_file_operation_choice,
    get_destination_path,
    get_pairs_to_process,
    is_image_file,
    IMAGE_TYPES,
)
from dataset_forge.analysis import (
    find_hq_lq_scale,
    test_hq_lq_scale,
    check_consistency,
    report_dimensions,
    find_extreme_dimensions,
    verify_images,
    find_misaligned_images,
    generate_hq_lq_dataset_report,
)
from dataset_forge.operations import (
    remove_small_image_pairs,
    extract_random_pairs,
    shuffle_image_pairs,
    transform_dataset,
    dataset_colour_adjustment,
    grayscale_conversion,
    split_adjust_dataset,
    optimize_png_menu,
    convert_to_webp_menu,
    downsample_images_menu,
    hdr_to_sdr_menu,
)
from dataset_forge.common import get_unique_filename
from dataset_forge.combine import combine_datasets
from dataset_forge.alpha import find_alpha_channels, remove_alpha_channels
from dataset_forge.comparison import create_comparison_images, create_gif_comparison
from dataset_forge.corruption import fix_corrupted_images
from dataset_forge.tiling import (
    tile_single_folder as best_tile_single_folder,
    tile_hq_lq_dataset as best_tile_hq_lq_dataset,
    Tiler,
    TilingStrategyFactory,
)
from dataset_forge.frames import extract_frames_menu
from subprocess import run, CalledProcessError
import subprocess
import yaml
import re
import gc
from dataset_forge import de_dupe
from dataset_forge import ICCToSRGBConverter
from dataset_forge import exif_scrubber
from dataset_forge.batch_rename import (
    batch_rename_single_folder,
    batch_rename_hq_lq_folders,
)
from dataset_forge.tiling_grid import tile_single_folder_grid, tile_hq_lq_dataset_grid
from dataset_forge.hue_adjustment import process_folder as hue_adjustment_process_folder
from dataset_forge import folder_compare
from dataset_forge import move_copy
from dataset_forge.bhi_filtering import run_bhi_filtering
from dataset_forge import dpid_phhofm
from dataset_forge import multiscale
import json

# Define global variables for dataset folders and config
hq_folder = ""
lq_folder = ""
config = None
config_path = None


# --- Catppuccin Mocha ANSI Color Helper ---
class Mocha:
    # Catppuccin Mocha palette (https://catppuccin.com/palette/mocha)
    rosewater = "\033[38;2;245;224;220m"
    flamingo = "\033[38;2;242;205;205m"
    pink = "\033[38;2;245;194;231m"
    mauve = "\033[38;2;203;166;247m"
    red = "\033[38;2;243;139;168m"
    maroon = "\033[38;2;235;160;172m"
    peach = "\033[38;2;250;179;135m"
    yellow = "\033[38;2;249;226;175m"
    green = "\033[38;2;166;227;161m"
    teal = "\033[38;2;148;226;213m"
    sky = "\033[38;2;137;220;235m"
    sapphire = "\033[38;2;116;199;236m"
    blue = "\033[38;2;137;180;250m"
    lavender = "\033[38;2;180;190;254m"
    text = "\033[38;2;205;214;244m"
    subtext1 = "\033[38;2;186;194;222m"
    subtext0 = "\033[38;2;166;173;200m"
    overlay2 = "\033[38;2;147;153;178m"
    overlay1 = "\033[38;2;127;132;156m"
    overlay0 = "\033[38;2;108;112;134m"
    surface2 = "\033[38;2;88;91;112m"
    surface1 = "\033[38;2;69;71;90m"
    surface0 = "\033[38;2;49;50;68m"
    base = "\033[38;2;30;30;46m"
    mantle = "\03cha[38;2;24;24;37m"
    crust = "\033[38;2;17;17;27m"
    reset = "\033[0m"
    bold = "\033[1m"
    underline = "\033[4m"


# --- Print helpers using Catppuccin Mocha ---
def print_header(title, char="#", color=Mocha.mauve):
    print(color + Mocha.bold + char * 50 + Mocha.reset)
    print(color + Mocha.bold + f"{title.center(50)}" + Mocha.reset)
    print(color + Mocha.bold + char * 50 + Mocha.reset)


def print_section(title, char="-", color=Mocha.sapphire):
    print(color + char * 40 + Mocha.reset)
    print(color + Mocha.bold + f"{title.center(40)}" + Mocha.reset)
    print(color + char * 40 + Mocha.reset)


def print_success(msg):
    print(Mocha.green + Mocha.bold + "✔ " + msg + Mocha.reset)


def print_warning(msg):
    print(Mocha.peach + Mocha.bold + "! " + msg + Mocha.reset)


def print_error(msg):
    print(Mocha.red + Mocha.bold + "✖ " + msg + Mocha.reset)


def print_info(msg):
    print(Mocha.sky + msg + Mocha.reset)


def print_prompt(msg):
    print(Mocha.yellow + msg + Mocha.reset, end="")


def release_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def de_dupe_menu():
    print("\n=== Duplicate & Near-Duplicate Image Detection ===")
    hq = hq_folder or input("Enter HQ folder path: ").strip()
    lq = lq_folder or input("Enter LQ folder path: ").strip()
    if not os.path.isdir(hq) or not os.path.isdir(lq):
        print("Both HQ and LQ folders must be set and exist.")
        return
    print("Choose hash type:")
    print("  1. phash (default)")
    print("  2. dhash")
    print("  3. ahash")
    print("  4. whash")
    hash_choice = input("Select hash type [1-4]: ").strip()
    hash_map = {"1": "phash", "2": "dhash", "3": "ahash", "4": "whash"}
    hash_type = hash_map.get(hash_choice, "phash")
    print("\nDetection mode:")
    print("  1. Exact duplicates (identical hash)")
    print("  2. Near-duplicates (small Hamming distance)")
    mode = input("Select mode [1-2]: ").strip()
    max_dist = 5
    if mode == "2":
        try:
            max_dist = int(
                input("Max Hamming distance for near-duplicates (default 5): ").strip()
                or "5"
            )
        except Exception:
            max_dist = 5
    print("\nOperation on found duplicates:")
    print("  1. Move to _dupes folders")
    print("  2. Copy to _dupes folders")
    print("  3. Delete (careful!)")
    op_choice = input("Select operation [1-3]: ").strip()
    op_map = {"1": "move", "2": "copy", "3": "delete"}
    op = op_map.get(op_choice, "move")
    # Compute hashes
    print(f"Computing {hash_type} hashes for HQ folder...")
    hq_hashes = de_dupe.compute_hashes(hq, hash_func=hash_type)
    if hq_hashes is None:
        print("No images found in HQ folder.")
        return
    print(f"Found {len(hq_hashes)} images in HQ folder.")
    # Find groups
    if mode == "2":
        groups = de_dupe.find_near_duplicates(hq_hashes, max_distance=max_dist) or []
        print(f"Found {len(groups)} near-duplicate groups.")
    else:
        groups = de_dupe.find_duplicates(hq_hashes) or []
        print(f"Found {len(groups)} duplicate groups.")
    if not groups:
        print("No duplicates or near-duplicates found.")
        return
    # Show summary
    for i, group in enumerate(groups, 1):
        print(f"Group {i}: {', '.join(group)}")
    confirm = input(f"Proceed to {op} these duplicates? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return
    # Prepare dest dirs if needed
    dest_dir = None
    if op in ("move", "copy"):
        hq_dupes = os.path.join(os.path.dirname(hq), os.path.basename(hq) + "_dupes")
        lq_dupes = os.path.join(os.path.dirname(lq), os.path.basename(lq) + "_dupes")
        dest_dir = {"hq": hq_dupes, "lq": lq_dupes}
    # Operate on pairs
    de_dupe.align_and_operate_on_pairs(groups, hq, lq, op=op, dest_dir=dest_dir)
    print("Done!")


def icc_to_srgb_menu():
    print("\n=== ICC to sRGB Conversion ===")
    input_path = input("Enter input file or folder path: ").strip()
    if not os.path.exists(input_path):
        print(f"Input path does not exist: {input_path}")
        return
    print("Choose operation mode:")
    print("  1. In place (overwrite original files)")
    print("  2. Copy to new folder (preserve originals)")
    op_choice = input("Select mode [1-2]: ").strip()
    if op_choice == "1":
        operation = "inplace"
        output_path = None
    elif op_choice == "2":
        operation = "copy"
        output_path = input("Enter output folder path: ").strip()
        if not output_path:
            print("Output folder path required for copy mode.")
            return
        os.makedirs(output_path, exist_ok=True)
    else:
        print("Invalid choice.")
        return
    converter = ICCToSRGBConverter()
    print(f"Processing {input_path} ...")
    success, result = converter.process(
        input_path, output_path=output_path, operation=operation
    )
    if success:
        print("ICC to sRGB conversion completed successfully.")
    else:
        print(f"Error: {result}")


def exif_scrubber_menu():
    print("\n=== Metadata (EXIF) Scrubber ===")
    if not exif_scrubber.has_exiftool():
        print(
            "ExifTool is not installed or not in PATH. Please install ExifTool and ensure it is available."
        )
        print("See: https://exiftool.org/")
        return
    print("Choose mode:")
    print("  1. Single folder")
    print("  2. HQ/LQ paired folders (preserve alignment)")
    mode = input("Select mode [1-2]: ").strip()
    if mode == "1":
        folder = input("Enter input folder path: ").strip()
        if not os.path.isdir(folder):
            print(f"Folder does not exist: {folder}")
            return
        print(f"Scrubbing EXIF metadata from all images in: {folder}")
        count, failed = exif_scrubber.scrub_exif_single_folder(folder)
        print(f"Processed {count} images.")
        if failed:
            print(f"Failed to process {len(failed)} files: {failed}")
        else:
            print("All images processed successfully.")
    elif mode == "2":
        hq_folder = input("Enter HQ folder path: ").strip()
        lq_folder = input("Enter LQ folder path: ").strip()
        if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
            print("Both HQ and LQ folders must exist.")
            return
        print(
            f"Scrubbing EXIF metadata from paired HQ/LQ folders:\n  HQ: {hq_folder}\n  LQ: {lq_folder}"
        )
        count, failed = exif_scrubber.scrub_exif_hq_lq_folders(hq_folder, lq_folder)
        print(f"Processed {count} HQ/LQ image pairs.")
        if failed:
            print(f"Failed to process {len(failed)} pairs:")
            for fname, err in failed:
                print(f"  {fname}: {err}")
        else:
            print("All HQ/LQ pairs processed successfully.")
    else:
        print("Invalid mode.")


def batch_rename_menu():
    print("\n=== Batch Renaming Utility ===")
    input_path = input(
        "Enter input folder path (single folder or parent of hq/lq): "
    ).strip()
    if not os.path.exists(input_path):
        print(f"Input path does not exist: {input_path}")
        return
    # Check if input_path contains hq/lq subfolders
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


def hue_adjustment_menu():
    print("\n=== Hue/Brightness/Contrast Adjustment ===")
    input_path = input("Enter input folder path (single or parent of hq/lq): ").strip()
    if not os.path.exists(input_path):
        print(f"Input path does not exist: {input_path}")
        return
    # Check for HQ/LQ subfolders
    hq_path = os.path.join(input_path, "hq")
    lq_path = os.path.join(input_path, "lq")
    is_pair = os.path.isdir(hq_path) and os.path.isdir(lq_path)
    if is_pair:
        print(f"Detected HQ/LQ folders: {hq_path}, {lq_path}")
    else:
        print(f"Detected single folder: {input_path}")
    # Get adjustment options
    try:
        duplicates = int(
            input("Number of duplicates to create (default 1): ").strip() or 1
        )
    except Exception:
        duplicates = 1
    enable_brightness = (
        input("Enable brightness shifting? (y/n, default n): ").strip().lower() == "y"
    )
    enable_contrast = (
        input("Enable contrast shifting? (y/n, default n): ").strip().lower() == "y"
    )
    enable_hue = input("Enable hue shifting? (y/n, default n): ").strip().lower() == "y"
    brightness = None
    contrast = None
    hue = None
    if enable_brightness:
        try:
            brightness = float(
                input("Base brightness factor (e.g. 1.0): ").strip() or 1.0
            )
        except Exception:
            brightness = 1.0
    if enable_contrast:
        try:
            contrast = float(input("Base contrast factor (e.g. 1.0): ").strip() or 1.0)
        except Exception:
            contrast = 1.0
    if enable_hue:
        try:
            hue = int(input("Base hue shift (0-180, e.g. 0): ").strip() or 0)
        except Exception:
            hue = 0
    real_name = (
        input("Use real file names for output? (y/n, default n): ").strip().lower()
        == "y"
    )
    if is_pair:
        output_hq = input("Enter HQ output folder: ").strip()
        output_lq = input("Enter LQ output folder: ").strip()
        hue_adjustment_process_folder(
            hq_path,
            output_hq,
            brightness=brightness,
            contrast=contrast,
            hue=hue,
            duplicates=duplicates,
            real_name=real_name,
            paired_lq_folder=lq_path,
            paired_output_lq_folder=output_lq,
        )
    else:
        output_folder = input("Enter output folder: ").strip()
        hue_adjustment_process_folder(
            input_path,
            output_folder,
            brightness=brightness,
            contrast=contrast,
            hue=hue,
            duplicates=duplicates,
            real_name=real_name,
        )
    print("Adjustment complete.")


def compare_folders_menu():
    print("\n=== Compare Folders ===")
    folder1 = input("Enter path to first folder: ").strip()
    folder2 = input("Enter path to second folder: ").strip()
    if not os.path.isdir(folder1) or not os.path.isdir(folder2):
        print_error("Both paths must be valid directories.")
        return
    ext_input = input(
        "Filter by file extensions (comma-separated, blank for all): "
    ).strip()
    extensions = (
        [
            (
                e.strip().lower()
                if e.strip().startswith(".")
                else "." + e.strip().lower()
            )
            for e in ext_input.split(",")
            if e.strip()
        ]
        if ext_input
        else None
    )
    missing1, missing2 = folder_compare.compare_folders(folder1, folder2, extensions)
    if not missing1 and not missing2:
        print_success(
            "Both folders contain the same files"
            + (f" (filtered by {', '.join(extensions)})" if extensions else "")
            + "."
        )
    else:
        if missing1:
            print_warning(f"Files missing in {folder1}:")
            for f in missing1:
                print(f"  {f}")
        if missing2:
            print_warning(f"Files missing in {folder2}:")
            for f in missing2:
                print(f"  {f}")


def bhi_filtering_menu():
    print("\n=== BHI FILTERING (Blockiness, HyperIQA, IC9600) ===")
    input_path = input("Enter input folder path (single or parent of hq/lq): ").strip()
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
    # Thresholds
    print(
        "Enter thresholds for filtering (images below any threshold will be filtered):"
    )
    try:
        blockiness_thr = float(
            input("Blockiness threshold (default 0.5): ").strip() or 0.5
        )
    except Exception:
        blockiness_thr = 0.5
    try:
        hyperiqa_thr = float(input("HyperIQA threshold (default 0.5): ").strip() or 0.5)
    except Exception:
        hyperiqa_thr = 0.5
    try:
        ic9600_thr = float(input("IC9600 threshold (default 0.5): ").strip() or 0.5)
    except Exception:
        ic9600_thr = 0.5
    thresholds = {
        "blockiness": blockiness_thr,
        "hyperiqa": hyperiqa_thr,
        "ic9600": ic9600_thr,
    }
    print("Choose action on filtered images:")
    print("  1. Move to _bhi_filtered folder")
    print("  2. Delete")
    print("  3. Report only (dry run)")
    action_choice = input("Select action [1-3]: ").strip()
    action_map = {"1": "move", "2": "delete", "3": "report"}
    action = action_map.get(action_choice, "move")
    batch_size = input("Batch size (default 8): ").strip()
    try:
        batch_size = int(batch_size) if batch_size else 8
    except Exception:
        batch_size = 8
    dry_run = action == "report"
    if is_pair:
        run_bhi_filtering(
            hq_path,
            thresholds,
            action=action,
            batch_size=batch_size,
            paired=True,
            lq_folder=lq_path,
            dry_run=dry_run,
            verbose=True,
        )
    else:
        run_bhi_filtering(
            input_path,
            thresholds,
            action=action,
            batch_size=batch_size,
            paired=False,
            dry_run=dry_run,
            verbose=True,
        )
    print("BHI filtering complete.")


def tiling_menu():
    print("\n=== Image Tiling Menu ===")
    print("Select tiling type:")
    print("1. Best (Laplacian/IC9600)")
    print("2. Linear (grid)")
    print("3. Random")
    print("4. Overlap")
    tiling_type_map = {"1": "best", "2": "linear", "3": "random", "4": "overlap"}
    tiling_type = input("Select type (1-4): ").strip()
    tiling_type = tiling_type_map.get(tiling_type, "best")
    print("\n1. Single Folder Tiling")
    print("2. HQ/LQ Pair Tiling")
    mode = input("Select mode (1=single, 2=pair): ").strip()
    if tiling_type == "best":
        if mode == "1":
            in_folder = input("Enter input folder: ").strip()
            out_folder = input("Enter output folder: ").strip()
            tile_size = int(input("Enter tile size (default 512): ") or 512)
            process_type = (
                input("Process type (thread/process/for, default thread): ").strip()
                or "thread"
            )
            func_type = (
                input(
                    "Complexity function (laplacian/ic9600, default laplacian): "
                ).strip()
                or "laplacian"
            )
            from dataset_forge.tiling import TilingStrategyFactory, Tiler

            strategy = TilingStrategyFactory.get_strategy(func_type)
            tiler = Tiler(strategy)
            tiler.run(
                in_folder=in_folder,
                out_folder=out_folder,
                tile_size=tile_size,
                process_type=process_type,
            )
        elif mode == "2":
            hq_folder = input("Enter HQ folder: ").strip()
            lq_folder = input("Enter LQ folder: ").strip()
            out_hq_folder = input("Enter HQ output folder: ").strip()
            out_lq_folder = input("Enter LQ output folder: ").strip()
            tile_size = int(input("Enter tile size (default 512): ") or 512)
            process_type = (
                input("Process type (thread/process/for, default thread): ").strip()
                or "thread"
            )
            func_type = (
                input(
                    "Complexity function (laplacian/ic9600, default laplacian): "
                ).strip()
                or "laplacian"
            )
            from dataset_forge.tiling import tile_hq_lq_dataset

            tile_hq_lq_dataset(
                hq_folder=hq_folder,
                lq_folder=lq_folder,
                out_hq_folder=out_hq_folder,
                out_lq_folder=out_lq_folder,
                tile_size=tile_size,
                process_type=process_type,
                func_type=func_type,
            )
        else:
            print("Invalid mode.")
    else:
        # linear, random, overlap
        if mode == "1":
            in_folder = input("Enter input folder: ").strip()
            out_folder = input("Enter output folder: ").strip()
            tile_size = int(input("Enter tile size (default 512): ") or 512)
            process_type = (
                input("Process type (thread/process, default thread): ").strip()
                or "thread"
            )
            n_tiles = input("Number of tiles per image (blank for default): ").strip()
            n_tiles = int(n_tiles) if n_tiles else None
            overlap = 0.25
            if tiling_type == "overlap":
                overlap = float(input("Overlap fraction (default 0.25): ") or 0.25)
            shuffle_tiles = (
                input("Shuffle tiles? (y/n, default n): ").strip().lower() == "y"
            )
            real_name = (
                input("Use real file names for output? (y/n, default n): ")
                .strip()
                .lower()
                == "y"
            )
            num_work = input("Number of workers (blank for default): ").strip()
            num_work = int(num_work) if num_work else None
            tile_single_folder_grid(
                in_folder=in_folder,
                out_folder=out_folder,
                tile_size=tile_size,
                process_type=process_type,
                tiler_type=tiling_type,
                n_tiles=n_tiles,
                overlap=overlap,
                shuffle=shuffle_tiles,
                real_name=real_name,
                num_work=num_work,
            )
        elif mode == "2":
            hq_folder = input("Enter HQ folder: ").strip()
            lq_folder = input("Enter LQ folder: ").strip()
            out_hq_folder = input("Enter HQ output folder: ").strip()
            out_lq_folder = input("Enter LQ output folder: ").strip()
            tile_size = int(input("Enter tile size (default 512): ") or 512)
            process_type = (
                input("Process type (thread/process, default thread): ").strip()
                or "thread"
            )
            n_tiles = input("Number of tiles per image (blank for default): ").strip()
            n_tiles = int(n_tiles) if n_tiles else None
            overlap = 0.25
            if tiling_type == "overlap":
                overlap = float(input("Overlap fraction (default 0.25): ") or 0.25)
            shuffle_tiles = (
                input("Shuffle tiles? (y/n, default n): ").strip().lower() == "y"
            )
            real_name = (
                input("Use real file names for output? (y/n, default n): ")
                .strip()
                .lower()
                == "y"
            )
            num_work = input("Number of workers (blank for default): ").strip()
            num_work = int(num_work) if num_work else None
            tile_hq_lq_dataset_grid(
                hq_folder=hq_folder,
                lq_folder=lq_folder,
                out_hq_folder=out_hq_folder,
                out_lq_folder=out_lq_folder,
                tile_size=tile_size,
                process_type=process_type,
                tiler_type=tiling_type,
                n_tiles=n_tiles,
                overlap=overlap,
                shuffle=shuffle_tiles,
                real_name=real_name,
                num_work=num_work,
            )
        else:
            print("Invalid mode.")


def multiscale_dataset_menu():
    print("\n=== Multiscale Dataset Utility ===")
    input_path = input("Enter input folder path (single or parent of hq/lq): ").strip()
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
    print("Choose DPID downscale method:")
    for i, (k, v) in enumerate(multiscale.DPID_METHODS.items(), 1):
        print(f"  {i}. {v}")
    method_choice = input("Select method [1-3]: ").strip()
    method_keys = list(multiscale.DPID_METHODS.keys())
    dpid_method = (
        method_keys[int(method_choice) - 1]
        if method_choice in ["1", "2", "3"]
        else "basicsr"
    )
    print("Choose scales to generate:")
    print("  1. 75%\n  2. 50%\n  3. 25%\n  4. All (75%, 50%, 25%)")
    scale_choice = input("Select scale(s) [1-4]: ").strip()
    if scale_choice == "4":
        scales = [0.75, 0.5, 0.25]
    else:
        scale_map = {"1": 0.75, "2": 0.5, "3": 0.25}
        scales = [scale_map.get(scale_choice, 0.75)]
    output_base = input("Enter output base folder: ").strip()
    os.makedirs(output_base, exist_ok=True)
    l = 0.5
    if dpid_method in ["basicsr", "openmmlab"]:
        try:
            l = float(
                input("Enter DPID lambda (0=smooth, 1=detail, default 0.5): ").strip()
                or 0.5
            )
        except Exception:
            l = 0.5
    print("\nStarting multiscale downscaling...")
    if is_pair:
        results = multiscale.multiscale_downscale(
            hq_path,
            output_base,
            scales=scales,
            dpid_method=dpid_method,
            l=l,
            paired=True,
            lq_folder=lq_path,
        )
    else:
        results = multiscale.multiscale_downscale(
            input_path,
            output_base,
            scales=scales,
            dpid_method=dpid_method,
            l=l,
            paired=False,
        )
    print("\nDownscaling complete. Outputs:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    # --- Tiling Option ---
    do_tiling = (
        input("Do you want to run tiling on any of the downscaled outputs? (y/n): ")
        .strip()
        .lower()
        == "y"
    )
    if not do_tiling:
        return
    # List available outputs
    output_folders = []
    if is_pair:
        for v in results.values():
            output_folders.append((v["hq"], v["lq"]))
    else:
        for v in results.values():
            output_folders.append(v["folder"])
    print("Available downscaled outputs:")
    for i, out in enumerate(output_folders, 1):
        if is_pair:
            print(f"  {i}. HQ: {out[0]} | LQ: {out[1]}")
        else:
            print(f"  {i}. {out}")
    sel = input(f"Select output to tile [1-{len(output_folders)}]: ").strip()
    try:
        sel_idx = int(sel) - 1
        if is_pair:
            tile_hq = output_folders[sel_idx][0]
            tile_lq = output_folders[sel_idx][1]
        else:
            tile_folder = output_folders[sel_idx]
    except Exception:
        print("Invalid selection.")
        return
    print("Choose tiling method:")
    print("  1. Best (Laplacian/IC9600)")
    print("  2. Linear (grid)")
    print("  3. Random")
    print("  4. Overlap")
    tiling_type_map = {"1": "best", "2": "linear", "3": "random", "4": "overlap"}
    tiling_type = tiling_type_map.get(input("Select type (1-4): ").strip(), "best")
    tile_size = int(input("Enter tile size (default 512): ") or 512)
    process_type = (
        input("Process type (thread/process, default thread): ").strip() or "thread"
    )
    if is_pair:
        out_hq_folder = input("Enter HQ output folder for tiles: ").strip()
        out_lq_folder = input("Enter LQ output folder for tiles: ").strip()
        if tiling_type == "best":
            from dataset_forge.tiling import tile_hq_lq_dataset

            func_type = (
                input(
                    "Complexity function (laplacian/ic9600, default laplacian): "
                ).strip()
                or "laplacian"
            )
            tile_hq_lq_dataset(
                hq_folder=tile_hq,
                lq_folder=tile_lq,
                out_hq_folder=out_hq_folder,
                out_lq_folder=out_lq_folder,
                tile_size=tile_size,
                process_type=process_type,
                func_type=func_type,
            )
        else:
            from dataset_forge.tiling_grid import tile_hq_lq_dataset_grid

            n_tiles = input("Number of tiles per image (blank for default): ").strip()
            n_tiles = int(n_tiles) if n_tiles else None
            overlap = 0.25
            if tiling_type == "overlap":
                overlap = float(input("Overlap fraction (default 0.25): ") or 0.25)
            shuffle_tiles = (
                input("Shuffle tiles? (y/n, default n): ").strip().lower() == "y"
            )
            real_name = (
                input("Use real file names for output? (y/n, default n): ")
                .strip()
                .lower()
                == "y"
            )
            num_work = input("Number of workers (blank for default): ").strip()
            num_work = int(num_work) if num_work else None
            tile_hq_lq_dataset_grid(
                hq_folder=tile_hq,
                lq_folder=tile_lq,
                out_hq_folder=out_hq_folder,
                out_lq_folder=out_lq_folder,
                tile_size=tile_size,
                process_type=process_type,
                tiler_type=tiling_type,
                n_tiles=n_tiles,
                overlap=overlap,
                shuffle=shuffle_tiles,
                real_name=real_name,
                num_work=num_work,
            )
    else:
        out_folder = input("Enter output folder for tiles: ").strip()
        if tiling_type == "best":
            from dataset_forge.tiling import tile_single_folder

            func_type = (
                input(
                    "Complexity function (laplacian/ic9600, default laplacian): "
                ).strip()
                or "laplacian"
            )
            tile_single_folder(
                in_folder=tile_folder,
                out_folder=out_folder,
                tile_size=tile_size,
                process_type=process_type,
                func_type=func_type,
            )
        else:
            from dataset_forge.tiling_grid import tile_single_folder_grid

            n_tiles = input("Number of tiles per image (blank for default): ").strip()
            n_tiles = int(n_tiles) if n_tiles else None
            overlap = 0.25
            if tiling_type == "overlap":
                overlap = float(input("Overlap fraction (default 0.25): ") or 0.25)
            shuffle_tiles = (
                input("Shuffle tiles? (y/n, default n): ").strip().lower() == "y"
            )
            real_name = (
                input("Use real file names for output? (y/n, default n): ")
                .strip()
                .lower()
                == "y"
            )
            num_work = input("Number of workers (blank for default): ").strip()
            num_work = int(num_work) if num_work else None
            tile_single_folder_grid(
                in_folder=tile_folder,
                out_folder=out_folder,
                tile_size=tile_size,
                process_type=process_type,
                tiler_type=tiling_type,
                n_tiles=n_tiles,
                overlap=overlap,
                shuffle=shuffle_tiles,
                real_name=real_name,
                num_work=num_work,
            )
    print("Tiling complete.")


# --- Utility functions needed by menu and config functions ---
def input_with_cancel(prompt):
    val = input(prompt)
    if val.strip().lower() in ("cancel", "back", "c"):
        print("Returning to previous menu...")
        raise KeyboardInterrupt("User cancelled/back to previous menu")
    return val


def extract_val_paths_from_yml(yml_path):
    if not yml_path or not os.path.isfile(yml_path):
        return None, None
    try:
        with open(yml_path, "r") as f:
            yml_data = yaml.safe_load(f)
        val = yml_data.get("datasets", {}).get("val", {})
        val_hq = None
        val_lq = None
        if isinstance(val, dict):
            gt = val.get("dataroot_gt")
            lq = val.get("dataroot_lq")
            if isinstance(gt, list) and gt:
                val_hq = gt[0]
            elif isinstance(gt, str):
                val_hq = gt
            if isinstance(lq, list) and lq:
                val_lq = lq[0]
            elif isinstance(lq, str):
                val_lq = lq
        return val_hq, val_lq
    except Exception as e:
        print(f"Warning: Could not parse .yml for Val Dataset paths: {e}")
        return None, None


def extract_model_dir_from_yml(yml_path):
    if not yml_path or not os.path.isfile(yml_path):
        return None, None, None
    try:
        with open(yml_path, "r") as f:
            yml_data = yaml.safe_load(f)
        name = yml_data.get("name")
        yml_dir = os.path.dirname(yml_path)
        exp_dir = None
        for _ in range(4):
            candidate = os.path.join(yml_dir, "experiments")
            if os.path.isdir(candidate):
                exp_dir = candidate
                break
            yml_dir = os.path.dirname(yml_dir)
        if not name or not exp_dir:
            return name, None, []
        model_dir = os.path.join(exp_dir, name)
        models_subdir = os.path.join(model_dir, "models")
        model_files = []
        if os.path.isdir(models_subdir):
            for f in os.listdir(models_subdir):
                if f.startswith("net_g_ema_") and f.endswith(".safetensors"):
                    model_files.append(os.path.join(models_subdir, f))
        return name, model_dir, model_files
    except Exception as e:
        print(f"Warning: Could not parse .yml for model dir: {e}")
        return None, None, []


# --- Menu utility functions copied from main_old.py ---
def add_config_file():
    print("\n=== Add Config File ===")
    model_name = input("Enter model name (used as config filename): ").strip()
    scale = input("Enter scale (e.g., 2, 4): ").strip()
    hq_path = input("Enter path to HQ dataset: ").strip()
    lq_path = input("Enter path to LQ dataset: ").strip()
    yml_path = input("Enter path to traiNNer-redux .yml config: ").strip()
    hcl_path = input("Enter path to wtp_dataset_destroyer .hcl config: ").strip()
    min_lq_w = input("Enter minimum LQ width (px): ").strip()
    min_lq_h = input("Enter minimum LQ height (px): ").strip()
    config_data = {
        "model_name": model_name,
        "scale": float(scale),
        "hq_path": hq_path,
        "lq_path": lq_path,
        "yml_path": yml_path,
        "hcl_path": hcl_path,
        "min_lq_w": int(min_lq_w),
        "min_lq_h": int(min_lq_h),
    }
    # Parse .hcl for extra info if provided and file exists
    if hcl_path and os.path.isfile(hcl_path):
        try:
            with open(hcl_path, "r") as f:
                lines = f.readlines()
            for line in lines:
                if line.strip().startswith("input") and "=" in line:
                    config_data["hcl_input"] = line.split("=", 1)[1].strip().strip('"')
                if line.strip().startswith("output") and "=" in line:
                    config_data["hcl_output"] = line.split("=", 1)[1].strip().strip('"')
            in_global = False
            global_block = {}
            for line in lines:
                if line.strip().startswith("global {"):
                    in_global = True
                    continue
                if in_global:
                    if line.strip().startswith("}"):
                        break
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"')
                        try:
                            v = int(v)
                        except Exception:
                            pass
                        global_block[k] = v
            if global_block:
                config_data["hcl_global"] = global_block
        except Exception as e:
            print(f"Warning: Failed to parse .hcl file for extra info: {e}")
    # Parse .yml for Val Dataset paths
    val_hq, val_lq = extract_val_paths_from_yml(yml_path)
    if val_hq and val_lq:
        config_data["val_hq_path"] = val_hq
        config_data["val_lq_path"] = val_lq
        print(f"Extracted Val Dataset HQ: {val_hq}\nExtracted Val Dataset LQ: {val_lq}")
    else:
        add_val = (
            input(
                "Val Dataset paths not found in .yml. Add custom Val Dataset HQ/LQ paths? (y/n): "
            )
            .strip()
            .lower()
        )
        if add_val == "y":
            val_hq = input("Enter path to Val HQ dataset: ").strip()
            val_lq = input("Enter path to Val LQ dataset: ").strip()
            config_data["val_hq_path"] = val_hq
            config_data["val_lq_path"] = val_lq
    # Parse .yml for model dir and model files
    yml_name, model_dir, model_files = extract_model_dir_from_yml(yml_path)
    if model_dir:
        config_data["model_dir"] = model_dir
        config_data["model_files"] = model_files if model_files is not None else []
        print(f"Model directory: {model_dir}")
        print(
            f"Found {len(model_files) if model_files is not None else 0} model(s) in models subfolder."
        )
    config_dir = "configs"
    os.makedirs(config_dir, exist_ok=True)
    config_filename = os.path.join(config_dir, f"{model_name}_config.json")
    with open(config_filename, "w") as f:
        json.dump(config_data, f, indent=2)
    print(f"Config saved as {config_filename}")


def load_config_file():
    global config, config_path, hq_folder, lq_folder
    print("\n=== Load Config File ===")
    config_dir = "configs"
    if not os.path.isdir(config_dir):
        print("No configs directory found. No configs to load.")
        return
    config_files = [f for f in os.listdir(config_dir) if f.endswith("_config.json")]
    if not config_files:
        print("No config files found in 'configs' directory.")
        return
    print("Available config files:")
    for idx, fname in enumerate(config_files, 1):
        print(f"  {idx}. {fname}")
    while True:
        choice = input_with_cancel(
            f"Select config file [1-{len(config_files)}] or 'cancel': "
        ).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(config_files):
            selected = config_files[int(choice) - 1]
            break
        else:
            print("Invalid selection. Please enter a valid number or 'cancel'.")
    path = os.path.join(config_dir, selected)
    try:
        with open(path, "r") as f:
            config = json.load(f)
        config_path = path
        hq_folder = config.get("hq_path", "")
        lq_folder = config.get("lq_path", "")
        print(f"Loaded config from {path}")
    except Exception as e:
        print(f"Failed to load config: {e}")


def view_config_info():
    print("\n=== Config Info ===")
    if not config:
        print("No config loaded.")
        return
    for k, v in config.items():
        print(f"{k}: {v}")


def validate_dataset_from_config():
    print("\n=== Validate HQ/LQ Dataset Based on Config ===")
    if not config:
        print("No config loaded.")
        return
    from dataset_forge.analysis import find_hq_lq_scale, report_dimensions
    from dataset_forge.alpha import find_alpha_channels

    hq = config["hq_path"]
    lq = config["lq_path"]
    scale = float(config["scale"])
    min_w = int(config["min_lq_w"])
    min_h = int(config["min_lq_h"])
    print("- Checking scale...")
    scale_result = find_hq_lq_scale(hq, lq, verbose=False)
    if scale_result["scales"]:
        most_common = max(set(scale_result["scales"]), key=scale_result["scales"].count)
        if abs(most_common - scale) < 1e-2:
            print(f"  Scale OK: {most_common}")
        else:
            print(f"  Scale mismatch! Most common: {most_common}, expected: {scale}")
    else:
        print("  No valid scales found.")
    print("- Checking LQ min size...")
    dims = report_dimensions(lq, "LQ", verbose=False)
    too_small = [d for d in dims["dimensions"] if d[0] < min_w or d[1] < min_h]
    if too_small:
        print(f"  {len(too_small)} LQ images smaller than {min_w}x{min_h}")
    else:
        print("  All LQ images meet minimum size.")
    print("- Checking for alpha channels...")
    alpha = find_alpha_channels(hq, lq)
    if alpha["hq_alpha"] or alpha["lq_alpha"]:
        print(
            f"  Images with alpha found: HQ={len(alpha['hq_alpha'])}, LQ={len(alpha['lq_alpha'])}"
        )
    else:
        print("  No alpha channels found.")
    print("Validation complete.")


def validate_val_dataset_from_config():
    print("\n=== Validate Val Dataset HQ/LQ Pair Based on Config ===")
    if not config or not config.get("val_hq_path") or not config.get("val_lq_path"):
        print("No Val Dataset HQ/LQ paths set in loaded config.")
        return
    from dataset_forge.analysis import find_hq_lq_scale, report_dimensions
    from dataset_forge.alpha import find_alpha_channels

    hq = config["val_hq_path"]
    lq = config["val_lq_path"]
    scale = float(config.get("scale", 2))
    min_w = int(config.get("min_lq_w", 0))
    min_h = int(config.get("min_lq_h", 0))
    print("- Checking scale...")
    scale_result = find_hq_lq_scale(hq, lq, verbose=False)
    if scale_result["scales"]:
        most_common = max(set(scale_result["scales"]), key=scale_result["scales"].count)
        if abs(most_common - scale) < 1e-2:
            print(f"  Scale OK: {most_common}")
        else:
            print(f"  Scale mismatch! Most common: {most_common}, expected: {scale}")
    else:
        print("  No valid scales found.")
    print("- Checking LQ min size...")
    dims = report_dimensions(lq, "Val LQ", verbose=False)
    too_small = [d for d in dims["dimensions"] if d[0] < min_w or d[1] < min_h]
    if too_small:
        print(f"  {len(too_small)} Val LQ images smaller than {min_w}x{min_h}")
    else:
        print("  All Val LQ images meet minimum size.")
    print("- Checking for alpha channels...")
    alpha = find_alpha_channels(hq, lq)
    if alpha["hq_alpha"] or alpha["lq_alpha"]:
        print(
            f"  Images with alpha found: HQ={len(alpha['hq_alpha'])}, LQ={len(alpha['lq_alpha'])}"
        )
    else:
        print("  No alpha channels found.")
    print("Validation complete.")


def run_wtp_dataset_destroyer():
    if not config or not config.get("hcl_path"):
        print("No .hcl config path set in loaded config.")
        return
    hcl_path = config["hcl_path"]
    if not os.path.isfile(hcl_path):
        print(f".hcl config file not found: {hcl_path}")
        return
    destroyer_dir = os.path.dirname(hcl_path)
    hcl_filename = os.path.basename(hcl_path)
    venv_path = os.path.join(destroyer_dir, "venv", "Scripts", "activate")
    if not os.path.isfile(venv_path):
        venv_path = os.path.join(destroyer_dir, "..", "venv", "Scripts", "activate")
    destroyer_py = os.path.join(destroyer_dir, "destroyer.py")
    if not os.path.isfile(destroyer_py):
        print(f"destroyer.py not found in {destroyer_dir}")
        return
    print(f"Running wtp_dataset_destroyer in: {destroyer_dir}")
    print(f"Command:")
    print(f"cd {destroyer_dir}")
    print(f"venv\\Scripts\\activate")
    print(f"python destroyer.py -f {hcl_filename}")
    try:
        subprocess.run(
            f'cd "{destroyer_dir}" && venv\\Scripts\\activate && python destroyer.py -f "{hcl_filename}"',
            shell=True,
            check=True,
        )
    except Exception as e:
        print(f"Error running wtp_dataset_destroyer: {e}")


def run_trainner_redux():
    if not config or not config.get("yml_path"):
        print("No .yml config path set in loaded config.")
        return
    yml_path = config["yml_path"]
    if not os.path.isfile(yml_path):
        print(f".yml config file not found: {yml_path}")
        return
    yml_dir = os.path.dirname(yml_path)
    trainner_dir = yml_dir
    for _ in range(3):
        if os.path.isfile(os.path.join(trainner_dir, "train.py")):
            break
        trainner_dir = os.path.dirname(trainner_dir)
    train_py = os.path.join(trainner_dir, "train.py")
    if not os.path.isfile(train_py):
        print(f"train.py not found near {yml_path}")
        return
    print(f"Running traiNNer-redux in: {trainner_dir}")
    print(f"Command:")
    print(f"cd {trainner_dir}")
    print(f"conda activate trainner_redux")
    print(f"python train.py --auto_resume -opt {yml_path}")
    try:
        subprocess.run(
            f'cd "{trainner_dir}" && conda activate trainner_redux && python train.py --auto_resume -opt "{yml_path}"',
            shell=True,
            check=True,
        )
    except Exception as e:
        print(f"Error running traiNNer-redux: {e}")


def edit_hcl_file():
    if not config or not config.get("hcl_path"):
        print("No .hcl config path set in loaded config.")
        return
    hcl_path = config["hcl_path"]
    if not os.path.isfile(hcl_path):
        print(f".hcl config file not found: {hcl_path}")
        return
    print(f"Opening {hcl_path} in default editor...")
    try:
        if os.name == "nt":
            os.startfile(hcl_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", hcl_path])
        else:
            subprocess.run(["xdg-open", hcl_path])
    except Exception as e:
        print(f"Failed to open .hcl file: {e}")


def edit_yml_file():
    if not config or not config.get("yml_path"):
        print("No .yml config path set in loaded config.")
        return
    yml_path = config["yml_path"]
    if not os.path.isfile(yml_path):
        print(f".yml config file not found: {yml_path}")
        return
    print(f"Opening {yml_path} in default editor...")
    try:
        if os.name == "nt":
            os.startfile(yml_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", yml_path])
        else:
            subprocess.run(["xdg-open", yml_path])
    except Exception as e:
        print(f"Failed to open .yml file: {e}")


def list_and_upscale_with_model():
    if not config or not config.get("model_dir"):
        print("No model directory found in config.")
        return
    model_dir = config["model_dir"]
    models_subdir = os.path.join(model_dir, "models")
    if not os.path.isdir(models_subdir):
        print(f"Models directory not found: {models_subdir}")
        return
    model_files = [
        os.path.join(models_subdir, f)
        for f in os.listdir(models_subdir)
        if f.startswith("net_g_ema_") and f.endswith(".safetensors")
    ]
    if not model_files:
        print("No model files found in models directory.")
        return

    def model_sort_key(path):
        m = re.search(r"net_g_ema_(\d+)\.safetensors$", os.path.basename(path))
        return int(m.group(1)) if m else float("inf")

    model_files_sorted = sorted(model_files, key=model_sort_key)
    print("Available models:")
    for idx, m in enumerate(model_files_sorted, 1):
        print(f"  {idx}. {os.path.basename(m)}")
    while True:
        choice = input_with_cancel(
            f"Select model [1-{len(model_files_sorted)}] or 'cancel': "
        ).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(model_files_sorted):
            selected_model = model_files_sorted[int(choice) - 1]
            break
        else:
            print("Invalid selection. Please enter a valid number or 'cancel'.")
    model_used_name = os.path.splitext(os.path.basename(selected_model))[0]
    input_path = input_with_cancel(
        "Enter input image file or directory to upscale (or 'cancel'): "
    ).strip()
    output_path = input_with_cancel("Enter output directory (or 'cancel'): ").strip()
    script_path = os.path.join("dataset_forge", "upscale-script.py")
    if not os.path.isfile(script_path):
        script_path = input_with_cancel(
            "Enter path to upscale-script.py (or 'cancel'): "
        ).strip()
        if not os.path.isfile(script_path):
            print("upscale-script.py not found.")
            return
    if os.path.isdir(input_path):
        from glob import glob
        import shutil

        SUPPORTED_FORMATS = (
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".tga",
            ".bmp",
            ".tiff",
        )
        files = []
        for ext in SUPPORTED_FORMATS:
            files.extend(glob(os.path.join(input_path, f"*{ext}")))
        if not files:
            print("No supported images found in input directory.")
            return
        for file in files:
            base = os.path.splitext(os.path.basename(file))[0]
            out_file = f"{base}_{model_used_name}.png"
            out_full = os.path.join(output_path, out_file)
            print(f"Upscaling {file} -> {out_full}")
            try:
                subprocess.run(
                    f'python "{script_path}" --input "{file}" --output "{output_path}" --model "{selected_model}"',
                    shell=True,
                    check=True,
                )
                orig_out = os.path.join(output_path, os.path.basename(file))
                orig_out = os.path.splitext(orig_out)[0] + ".png"
                if os.path.exists(orig_out):
                    shutil.move(orig_out, out_full)
                    print(f"Saved: {out_full}")
            except Exception as e:
                print(f"Error upscaling {file}: {e}")
    else:
        base = os.path.splitext(os.path.basename(input_path))[0]
        out_file = f"{base}_{model_used_name}.png"
        out_full = os.path.join(output_path, out_file)
        print(f"Upscaling {input_path} -> {out_full}")
        try:
            subprocess.run(
                f'python "{script_path}" --input "{input_path}" --output "{output_path}" --model "{selected_model}"',
                shell=True,
                check=True,
            )
            orig_out = os.path.join(output_path, os.path.basename(input_path))
            orig_out = os.path.splitext(orig_out)[0] + ".png"
            if os.path.exists(orig_out):
                os.rename(orig_out, out_full)
                print(f"Saved: {out_full}")
        except Exception as e:
            print(f"Error upscaling {input_path}: {e}")


def main_menu():
    hq_folder = ""
    lq_folder = ""
    config = None
    config_path = None

    def input_with_cancel(prompt):
        val = input(prompt)
        if val.strip().lower() in ("cancel", "back", "c"):
            print("Returning to previous menu...")
            raise KeyboardInterrupt("User cancelled/back to previous menu")
        return val

    # --- Sub-menus ---
    def config_menu():
        while True:
            try:
                print_section("Configuration & Training", "=", Mocha.mauve)
                print(f"  1. Manage Configurations")
                print(f"  2. Dataset Validation")
                print(f"  3. Model Training & Upscaling")
                print(f"  4. Back to Main Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-4) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    manage_configurations_menu()
                elif choice == "2":
                    dataset_validation_menu()
                elif choice == "3":
                    model_training_menu()
                elif choice == "4":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def manage_configurations_menu():
        while True:
            try:
                print_section("Manage Configurations", "-", Mocha.sapphire)
                print(f"  1. Add New Configuration")
                print(f"  2. Load Configuration File")
                print(f"  3. View Loaded Configuration Info")
                print(f"  4. Edit .hcl Config File")
                print(f"  5. Edit .yml Config File")
                print(f"  6. Back to Configuration & Training Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-6) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    add_config_file()
                elif choice == "2":
                    load_config_file()
                elif choice == "3":
                    view_config_info()
                elif choice == "4":
                    edit_hcl_file()
                elif choice == "5":
                    edit_yml_file()
                elif choice == "6":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def dataset_validation_menu():
        while True:
            try:
                print_section("Dataset Validation", "-", Mocha.sapphire)
                print(f"  1. Validate Main HQ/LQ Dataset")
                print(f"  2. Validate Validation HQ/LQ Dataset")
                print(f"  3. Back to Configuration & Training Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-3) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    validate_dataset_from_config()
                elif choice == "2":
                    validate_val_dataset_from_config()
                elif choice == "3":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def model_training_menu():
        while True:
            try:
                print_section("Model Training & Upscaling", "-", Mocha.sapphire)
                print(f"  1. Run wtp-dataset-destroyer")
                print(f"  2. Run traiNNer-redux Training")
                print(f"  3. Upscale Images with Model")
                print(f"  4. Back to Configuration & Training Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-4) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    run_wtp_dataset_destroyer()
                elif choice == "2":
                    run_trainner_redux()
                elif choice == "3":
                    list_and_upscale_with_model()
                elif choice == "4":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def analysis_menu():
        while True:
            try:
                print_section("Dataset Analysis & Reporting", "=", Mocha.sapphire)
                print(f"  1. Scale Analysis")
                print(f"  2. Image Property Checks")
                print(f"  3. Generate Dataset Report")
                print(f"  4. Back to Main Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-4) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    scale_analysis_menu()
                elif choice == "2":
                    image_property_checks_menu()
                elif choice == "3":
                    generate_report_menu()
                elif choice == "4":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def scale_analysis_menu():
        while True:
            try:
                print_section("Scale Analysis", "-", Mocha.teal)
                print(f"  1. Find HQ/LQ Scale")
                print(f"  2. Test HQ/LQ Scale")
                print(f"  3. Back to Dataset Analysis Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-3) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    find_hq_lq_scale(hq_folder, lq_folder)
                elif choice == "2":
                    test_hq_lq_scale(hq_folder, lq_folder)
                elif choice == "3":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def image_property_checks_menu():
        while True:
            try:
                print_section("Image Property Checks", "-", Mocha.teal)
                print(f"  1. Check Image Consistency")
                print(f"  2. Report Image Dimensions")
                print(f"  3. Find Extreme Dimensions")
                print(f"  4. Verify Image Integrity")
                print(f"  5. Find Misaligned Images (HQ/LQ Pairs)")
                print(f"  6. Find Images with Alpha Channels")
                print(f"  7. Back to Dataset Analysis Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-7) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    check_consistency(hq_folder, "HQ")
                    check_consistency(lq_folder, "LQ")
                elif choice == "2":
                    report_dimensions(hq_folder, "HQ")
                    report_dimensions(lq_folder, "LQ")
                elif choice == "3":
                    find_extreme_dimensions(hq_folder, "HQ")
                    find_extreme_dimensions(lq_folder, "LQ")
                elif choice == "4":
                    verify_images(hq_folder, lq_folder)
                elif choice == "5":
                    find_misaligned_images(hq_folder, lq_folder)
                elif choice == "6":
                    find_alpha_channels(hq_folder, lq_folder)
                elif choice == "7":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def generate_report_menu():
        while True:
            try:
                print_section("Generate Dataset Report", "-", Mocha.teal)
                print(f"  1. Generate Full HQ/LQ Dataset Report")
                print(f"  2. Back to Dataset Analysis Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-2) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    generate_hq_lq_dataset_report(hq_folder, lq_folder)
                elif choice == "2":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def transformation_menu():
        while True:
            try:
                print_section("Dataset Transformation & Management", "=", Mocha.teal)
                print(f"  1. Dataset Filtering & Selection")
                print(f"  2. Dataset Arrangement")
                print(f"  3. Folder Utilities")
                print(f"  4. Back to Main Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-4) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    filtering_selection_menu()
                elif choice == "2":
                    arrangement_menu()
                elif choice == "3":
                    folder_utilities_menu()
                elif choice == "4":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def filtering_selection_menu():
        while True:
            try:
                print_section("Dataset Filtering & Selection", "-", Mocha.yellow)
                print(f"  1. Remove Small Image Pairs")
                print(f"  2. Extract Random Image Pairs")
                print(f"  3. Find & Remove Duplicate Images")
                print(f"  4. Back to Dataset Transformation Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-4) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    remove_small_image_pairs(hq_folder, lq_folder)
                elif choice == "2":
                    extract_random_pairs(hq_folder, lq_folder)
                elif choice == "3":
                    de_dupe_menu()
                elif choice == "4":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def arrangement_menu():
        while True:
            try:
                print_section("Dataset Arrangement", "-", Mocha.yellow)
                print(f"  1. Shuffle Image Pairs")
                print(f"  2. Combine Multiple Datasets")
                print(f"  3. Advanced Split & Adjust Dataset")
                print(f"  4. Back to Dataset Transformation Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-4) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    shuffle_image_pairs(hq_folder, lq_folder)
                elif choice == "2":
                    combine_datasets()
                elif choice == "3":
                    split_adjust_dataset(hq_folder, lq_folder)
                elif choice == "4":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def folder_utilities_menu():
        while True:
            try:
                print_section("Folder Utilities", "-", Mocha.yellow)
                print(f"  1. Batch Rename Images")
                print(f"  2. Compare Folders (Show Missing Files)")
                print(f"  3. Back to Dataset Transformation Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-3) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    batch_rename_menu()
                elif choice == "2":
                    compare_folders_menu()
                elif choice == "3":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def image_processing_menu():
        while True:
            try:
                print_section("Image Processing & Enhancement", "=", Mocha.pink)
                print(f"  1. Color & Tone Adjustments")
                print(f"  2. Image Content Modification")
                print(f"  3. Advanced Image Filtering")
                print(f"  4. Back to Main Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-4) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    color_tone_menu()
                elif choice == "2":
                    content_modification_menu()
                elif choice == "3":
                    advanced_filtering_menu()
                elif choice == "4":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def color_tone_menu():
        while True:
            try:
                print_section("Color & Tone Adjustments", "-", Mocha.pink)
                print(f"  1. Apply Dataset Color Adjustment")
                print(f"  2. Convert to Grayscale")
                print(f"  3. Adjust Hue/Brightness/Contrast")
                print(f"  4. Convert ICC Profile to sRGB")
                print(f"  5. Back to Image Processing Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-5) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    dataset_colour_adjustment(hq_folder, lq_folder)
                elif choice == "2":
                    grayscale_conversion(hq_folder, lq_folder)
                elif choice == "3":
                    hue_adjustment_menu()
                elif choice == "4":
                    icc_to_srgb_menu()
                elif choice == "5":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def content_modification_menu():
        while True:
            try:
                print_section("Image Content Modification", "-", Mocha.pink)
                print(f"  1. Remove Alpha Channels")
                print(f"  2. Fix Corrupted Images")
                print(f"  3. Remove Metadata (EXIF)")
                print(f"  4. Back to Image Processing Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-4) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    remove_alpha_channels(hq_folder, lq_folder)
                elif choice == "2":
                    fix_corrupted_images(hq_folder)
                elif choice == "3":
                    exif_scrubber_menu()
                elif choice == "4":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def advanced_filtering_menu():
        while True:
            try:
                print_section("Advanced Image Filtering", "-", Mocha.pink)
                print(f"  1. Apply BHI Filtering (Blockiness, HyperIQA, IC9600)")
                print(f"  2. Back to Image Processing Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-2) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    bhi_filtering_menu()
                elif choice == "2":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def optimization_menu():
        while True:
            try:
                print_section("Image Optimization & Conversion", "=", Mocha.yellow)
                print(f"  1. Optimize PNG Images")
                print(f"  2. Convert Images to WebP")
                print(f"  3. Downsample Images")
                print(f"  4. Back to Main Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-4) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    optimize_png_menu(hq_folder, lq_folder)
                elif choice == "2":
                    convert_to_webp_menu(hq_folder, lq_folder)
                elif choice == "3":
                    downsample_images_menu()
                elif choice == "4":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def tiling_menu_new():
        while True:
            try:
                print_section("Image Tiling Operations", "=", Mocha.mauve)
                print(f"  1. Single Folder Tiling")
                print(f"  2. HQ/LQ Paired Folder Tiling")
                print(f"  3. Back to Main Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-3) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    tile_single_folder_menu()
                elif choice == "2":
                    tile_hq_lq_folder_menu()
                elif choice == "3":
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                return

    def tile_single_folder_menu():
        tiling_menu()

    def tile_hq_lq_folder_menu():
        tiling_menu()

    def visual_comparisons_menu():
        while True:
            try:
                print_section("Visual Comparisons & Previews", "=", Mocha.sky)
                print(f"  1. Create Static Comparison Images")
                print(f"  2. Create Animated HQ/LQ Comparisons (GIF/WebP)")
                print(f"  3. Back to Main Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-3) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    create_comparison_images(hq_folder, lq_folder)
                elif choice == "2":
                    create_gif_comparison(hq_folder, lq_folder)
                elif choice == "3":
                    return
            except KeyboardInterrupt:
                return

    def video_processing_menu():
        while True:
            try:
                print_section("Video Processing", "=", Mocha.blue)
                print(f"  1. HDR to SDR Tone Mapping")
                print(f"  2. Extract Frames from Video")
                print(f"  3. Back to Main Menu")
                choice = input_with_cancel(
                    "Enter your choice (1-3) or 'c' to go back: "
                ).strip()
                if choice == "1":
                    hdr_to_sdr_menu()
                elif choice == "2":
                    extract_frames_menu()
                elif choice == "3":
                    return
            except KeyboardInterrupt:
                return

    # --- Main Menu Loop ---
    while True:
        try:
            os.system("cls" if os.name == "nt" else "clear")
            print_header("Image Training Dataset Utility")
            print_info(f"Current Folders:")
            print(
                f"  {Mocha.rosewater}HQ Folder:{Mocha.reset} {hq_folder if hq_folder else Mocha.red + 'Not set' + Mocha.reset}"
            )
            print(
                f"  {Mocha.rosewater}LQ Folder:{Mocha.reset} {lq_folder if lq_folder else Mocha.red + 'Not set' + Mocha.reset}"
            )
            print(
                f"  {Mocha.rosewater}Config:{Mocha.reset} {config_path if config_path else Mocha.red + 'Not loaded' + Mocha.reset}"
            )
            print_section("Main Menu", "=", Mocha.mauve)
            print(f" 1. Configuration & Training Tools")
            print(f" 2. Dataset Analysis & Reporting")
            print(f" 3. Dataset Transformation & Management")
            print(f" 4. Image Processing & Enhancement")
            print(f" 5. Image Optimization & Conversion")
            print(f" 6. Image Tiling Operations")
            print(f" 7. Visual Comparisons & Previews")
            print(f" 8. Video Processing")
            print(f" 9. Multiscale Dataset Utility")
            print(f"10. Exit Application")
            print("-" * 40)
            try:
                choice = input_with_cancel(
                    "Enter your choice (e.g., '1' for Configuration) or 'cancel': "
                ).strip()
            except KeyboardInterrupt:
                continue
            if choice == "1":
                config_menu()
            elif choice == "2":
                analysis_menu()
            elif choice == "3":
                transformation_menu()
            elif choice == "4":
                image_processing_menu()
            elif choice == "5":
                optimization_menu()
            elif choice == "6":
                tiling_menu_new()
            elif choice == "7":
                visual_comparisons_menu()
            elif choice == "8":
                video_processing_menu()
            elif choice == "9":
                multiscale_dataset_menu()
            elif choice == "10":
                print("Exiting Image Training Dataset Utility. Goodbye!")
                break
            else:
                print(
                    "Invalid choice. Please enter a number from the menu or 'cancel'."
                )
            try:
                input_with_cancel(
                    "\nPress Enter to return to the main menu (or type 'cancel'): "
                )
            except KeyboardInterrupt:
                continue
        except KeyboardInterrupt:
            print("Returned to main menu.")
            continue


if __name__ == "__main__":
    # Setup global logging to a file for the entire session, if desired
    # This can be complex if functions also try to set up their own file handlers.
    # For simplicity, individual functions might log to console or specific files.
    # Default basicConfig here will just go to console if no file handler is set.
    # logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # A session log file:
    session_log_file = "image_dataset_utility_session.log"
    # Clear or append to session log
    # For this example, let's append. For clearing each session, mode='w'.
    # Be careful with multiple file handlers if functions also create them.
    # It's often better for functions to use `logging.getLogger(__name__)`
    # and configure handlers at the top level.

    # Minimal global logging to console. Functions can add specific file handlers.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    main_menu()
