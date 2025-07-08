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
from dataset_forge.config_menu import (
    add_config_file,
    load_config_file,
    view_config_info,
    validate_dataset_from_config,
    validate_val_dataset_from_config,
    run_wtp_dataset_destroyer,
    run_trainner_redux,
    edit_hcl_file,
    edit_yml_file,
    list_and_upscale_with_model,
)

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


def orientation_organization_menu():
    print("\n=== Images Orientation Organization ===")
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
    print("Choose operation:")
    print("  1. Copy (default)")
    print("  2. Move")
    op_choice = input("Select operation [1-2]: ").strip()
    operation = "move" if op_choice == "2" else "copy"
    print("Select orientation(s) to extract (comma separated):")
    print(
        "  1. Landscape\n  2. Portrait\n  3. Square\n  (e.g. 1,2 for both landscape and portrait)"
    )
    orient_choice = input("Enter choice(s): ").strip()
    orient_map = {"1": "landscape", "2": "portrait", "3": "square"}
    if orient_choice:
        orientations = [
            orient_map[c.strip()]
            for c in orient_choice.split(",")
            if c.strip() in orient_map
        ]
    else:
        orientations = ["landscape"]
    if not orientations:
        print("No valid orientations selected.")
        return
    if is_pair:
        output_hq = input("Enter HQ output folder: ").strip()
        output_lq = input("Enter LQ output folder: ").strip()
        from dataset_forge import orientation_organizer

        orientation_organizer.organize_hq_lq_by_orientation(
            hq_folder=hq_path,
            lq_folder=lq_path,
            output_hq_folder=output_hq,
            output_lq_folder=output_lq,
            orientations=orientations,
            operation=operation,
        )
        print(
            f"Done! Processed HQ/LQ pairs for orientations: {', '.join(orientations)}."
        )
    else:
        output_folder = input("Enter output folder: ").strip()
        from dataset_forge import orientation_organizer

        orientation_organizer.organize_images_by_orientation(
            input_folder=input_path,
            output_folder=output_folder,
            orientations=orientations,
            operation=operation,
        )
        print(f"Done! Processed images for orientations: {', '.join(orientations)}.")


# --- Helper to ensure HQ/LQ folders are set ---
def require_hq_lq(func):
    def wrapper(*args, **kwargs):
        global hq_folder, lq_folder
        while not (
            hq_folder
            and lq_folder
            and os.path.isdir(hq_folder)
            and os.path.isdir(lq_folder)
        ):
            print_warning(
                "HQ and LQ folders must be set and valid before running this action."
            )
            settings_menu()
        return func(*args, **kwargs)

    return wrapper


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


# ===================== NEW MENU SYSTEM (Gemini Refactor) =====================


def show_menu(title, options, header_color=Mocha.mauve, char="#"):
    """Generic function to display a menu and get user choice."""
    print_header(title, char=char, color=header_color)
    for key, value in options.items():
        if key.lower() == "0":
            print(f"{Mocha.yellow}[ {key} ]  {Mocha.text}{value[0]}{Mocha.reset}")
        else:
            print(f"{Mocha.blue}[ {key} ]  {Mocha.text}{value[0]}{Mocha.reset}")
    while True:
        print_prompt("\nEnter your choice: ")
        choice = input().strip()
        if choice in options:
            return options[choice][1]
        else:
            print_error("Invalid choice. Please try again.")


def dataset_menu():
    options = {
        "1": ("Create Multiscale Dataset", multiscale_dataset_menu),
        "2": ("Image Tiling", tiling_menu),
        "3": ("Combine Datasets", combine_datasets),
        "4": (
            "Extract Random Pairs",
            require_hq_lq(lambda: extract_random_pairs(hq_folder, lq_folder)),
        ),
        "5": (
            "Shuffle Image Pairs",
            require_hq_lq(lambda: shuffle_image_pairs(hq_folder, lq_folder)),
        ),
        "6": (
            "Split and Adjust Dataset",
            require_hq_lq(lambda: split_adjust_dataset(hq_folder, lq_folder)),
        ),
        "7": (
            "Remove Small Image Pairs",
            require_hq_lq(lambda: remove_small_image_pairs(hq_folder, lq_folder)),
        ),
        "8": ("De-Duplicate", de_dupe_menu),
        "9": ("Batch Rename", batch_rename_menu),
        "10": ("Extract Frames from Video", extract_frames_menu),
        "11": (
            "Images Orientation Organization (Extract by Landscape/Portrait/Square)",
            orientation_organization_menu,
        ),
        "0": ("Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "Dataset Creation & Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        input_with_cancel("\nPress Enter to return to the menu...")


def analysis_menu():
    options = {
        "1": (
            "Generate HQ/LQ Dataset Report",
            require_hq_lq(lambda: generate_hq_lq_dataset_report(hq_folder, lq_folder)),
        ),
        "2": (
            "Find HQ/LQ Scale",
            require_hq_lq(lambda: find_hq_lq_scale(hq_folder, lq_folder)),
        ),
        "3": (
            "Test HQ/LQ Scale",
            require_hq_lq(lambda: test_hq_lq_scale(hq_folder, lq_folder)),
        ),
        "4": (
            "Check Dataset Consistency",
            require_hq_lq(
                lambda: (
                    check_consistency(hq_folder, "HQ"),
                    check_consistency(lq_folder, "LQ"),
                )
            ),
        ),
        "5": (
            "Report Image Dimensions",
            require_hq_lq(
                lambda: (
                    report_dimensions(hq_folder, "HQ"),
                    report_dimensions(lq_folder, "LQ"),
                )
            ),
        ),
        "6": (
            "Find Extreme Image Dimensions",
            require_hq_lq(
                lambda: (
                    find_extreme_dimensions(hq_folder, "HQ"),
                    find_extreme_dimensions(lq_folder, "LQ"),
                )
            ),
        ),
        "7": (
            "Verify Images (Corruption Check)",
            require_hq_lq(lambda: verify_images(hq_folder, lq_folder)),
        ),
        "8": (
            "Fix Corrupted Images",
            require_hq_lq(lambda: fix_corrupted_images(hq_folder)),
        ),
        "9": (
            "Find Misaligned Images",
            require_hq_lq(lambda: find_misaligned_images(hq_folder, lq_folder)),
        ),
        "10": (
            "Find Images with Alpha Channel",
            require_hq_lq(lambda: find_alpha_channels(hq_folder, lq_folder)),
        ),
        "11": ("BHI Filtering (Blockiness, HyperIQA, IC9600)", bhi_filtering_menu),
        "0": ("Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "Dataset Analysis & Reporting",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        input_with_cancel("\nPress Enter to return to the menu...")


def transform_menu():
    options = {
        "1": ("Downsample Images", downsample_images_menu),
        "2": ("Convert HDR to SDR", hdr_to_sdr_menu),
        "3": (
            "Color/Tone Adjustments",
            require_hq_lq(lambda: dataset_colour_adjustment(hq_folder, lq_folder)),
        ),
        "4": ("Hue/Brightness/Contrast Adjustment", hue_adjustment_menu),
        "5": (
            "Grayscale Conversion",
            require_hq_lq(lambda: grayscale_conversion(hq_folder, lq_folder)),
        ),
        "6": (
            "Remove Alpha Channel",
            require_hq_lq(lambda: remove_alpha_channels(hq_folder, lq_folder)),
        ),
        "7": ("Apply Custom Transformations", transform_dataset),
        "0": ("Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "Image Transformations", options, header_color=Mocha.sapphire, char="-"
        )
        if action is None:
            break
        action()
        input_with_cancel("\nPress Enter to return to the menu...")


def metadata_menu():
    options = {
        "1": ("Scrub EXIF Metadata", exif_scrubber_menu),
        "2": ("Convert ICC Profile to sRGB", icc_to_srgb_menu),
        "0": ("Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "EXIF & ICC Profile Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        input_with_cancel("\nPress Enter to return to the menu...")


def comparison_menu():
    options = {
        "1": (
            "Create Comparison Images",
            require_hq_lq(lambda: create_comparison_images(hq_folder, lq_folder)),
        ),
        "2": (
            "Create GIF Comparison",
            require_hq_lq(lambda: create_gif_comparison(hq_folder, lq_folder)),
        ),
        "3": ("Compare Folders", compare_folders_menu),
        "0": ("Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "Comparison Tools", options, header_color=Mocha.sapphire, char="-"
        )
        if action is None:
            break
        action()
        input_with_cancel("\nPress Enter to return to the menu...")


def config_menu():
    options = {
        "1": ("Add Config File", add_config_file),
        "2": ("Load Config File", load_config_file),
        "3": ("View Config Info", view_config_info),
        "4": ("Validate HQ/LQ Dataset from Config", validate_dataset_from_config),
        "5": ("Validate Val Dataset HQ/LQ Pair", validate_val_dataset_from_config),
        "6": ("Run wtp_dataset_destroyer", run_wtp_dataset_destroyer),
        "7": ("Edit .hcl config file", edit_hcl_file),
        "8": ("Run traiNNer-redux", run_trainner_redux),
        "9": ("Edit .yml config file", edit_yml_file),
        "10": ("List/Run Upscale with Model", list_and_upscale_with_model),
        "0": ("Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "Configuration & Model Management",
            options,
            header_color=Mocha.mauve,
            char="=",
        )
        if action is None:
            break
        action()
        input_with_cancel("\nPress Enter to return to the menu...")


def settings_menu():
    # This is a placeholder. You can expand this with more settings.
    global hq_folder, lq_folder
    print_section("Settings", char="-", color=Mocha.sky)
    print_info(f"Current HQ Folder: {hq_folder or 'Not Set'}")
    print_info(f"Current LQ Folder: {lq_folder or 'Not Set'}")
    print("\n[1] Set HQ/LQ Folders")
    print("[0] Back to Main Menu")
    choice = input("Choice: ").strip()
    if choice == "1":
        hq_folder = get_folder_path("Enter the path to the HQ folder: ")
        lq_folder = get_folder_path("Enter the path to the LQ folder: ")
        print_success("Folders updated.")
    else:
        return


def main_menu():
    """Main menu for the Image Dataset Utility."""
    main_options = {
        "1": ("\U0001f4c2 DATASET", dataset_menu),
        "2": ("\U0001f4ca ANALYSIS", analysis_menu),
        "3": ("\u2728 TRANSFORM", transform_menu),
        "4": ("\U0001f5c2\ufe0f  METADATA", metadata_menu),
        "5": ("\U0001f50d COMPARISON", comparison_menu),
        "6": ("\U0001f4c1 CONFIG", config_menu),
        "7": ("\u2699\ufe0f  SETTINGS", settings_menu),
        "0": ("\U0001f6aa EXIT", None),
    }
    while True:
        try:
            action = show_menu("Image Dataset Utility - Main Menu", main_options)
            if action is None:
                print_info("Exiting...")
                break
            action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break


# ===================== END NEW MENU SYSTEM =====================


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
