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
)
from dataset_forge.common import get_unique_filename
from dataset_forge.combine import combine_datasets
from dataset_forge.alpha import find_alpha_channels, remove_alpha_channels
from dataset_forge.comparison import create_comparison_images, create_gif_comparison
from dataset_forge.corruption import fix_corrupted_images
from dataset_forge.tiling import (
    tile_dataset_menu,
    tile_hq_lq_dataset,
    tile_aligned_pairs,
    tile_images,
)
from dataset_forge.frames import extract_frames_menu
from subprocess import run, CalledProcessError

# Setup logging for better error reporting in background tasks
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def main_menu():
    hq_folder = ""
    lq_folder = ""

    while True:
        print("\n" + "#" * 40)
        print("  Image Training Dataset Utility")
        print("#" * 40)
        print("\nCurrent Folders:")
        print(f"  HQ Folder: {hq_folder if hq_folder else 'Not set'}")
        print(f"  LQ Folder: {lq_folder if lq_folder else 'Not set'}")
        print("\nMenu:")
        print("  1. Set HQ/LQ Folders")
        option_map = {"1": ("Set HQ/LQ Folders", None)}
        next_option = 2
        if hq_folder and lq_folder:
            print("\n  --- HQ/LQ Dataset Analysis ---")
            print(f"  {next_option}. Find HQ/LQ Scale")
            option_map[str(next_option)] = (
                "Find HQ/LQ Scale",
                lambda: find_hq_lq_scale(hq_folder, lq_folder),
            )
            next_option += 1
            print(f"  {next_option}. Test HQ/LQ Scale")
            option_map[str(next_option)] = (
                "Test HQ/LQ Scale",
                lambda: test_hq_lq_scale(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Check Image Consistency (Formats/Modes in HQ & LQ)"
            )
            option_map[str(next_option)] = (
                "Check Image Consistency",
                lambda: (
                    check_consistency(hq_folder, "HQ"),
                    check_consistency(lq_folder, "LQ"),
                ),
            )
            next_option += 1
            print(f"  {next_option}. Report Image Dimensions (Stats for HQ & LQ)")
            option_map[str(next_option)] = (
                "Report Image Dimensions",
                lambda: (
                    report_dimensions(hq_folder, "HQ"),
                    report_dimensions(lq_folder, "LQ"),
                ),
            )
            next_option += 1
            print(
                f"  {next_option}. Find Extreme Dimensions (Biggest/Smallest in HQ & LQ)"
            )
            option_map[str(next_option)] = (
                "Find Extreme Dimensions",
                lambda: (
                    find_extreme_dimensions(hq_folder, "HQ"),
                    find_extreme_dimensions(lq_folder, "LQ"),
                ),
            )
            next_option += 1
            print(
                f"  {next_option}. Verify Image Integrity (Corrupted Files in HQ & LQ)"
            )
            option_map[str(next_option)] = (
                "Verify Image Integrity",
                lambda: verify_images(hq_folder, lq_folder),
            )
            next_option += 1
            print(f"  {next_option}. Find Misaligned Images (using Phase Correlation)")
            option_map[str(next_option)] = (
                "Find Misaligned Images",
                lambda: find_misaligned_images(hq_folder, lq_folder),
            )
            next_option += 1
            print(f"  {next_option}. Generate Full HQ/LQ Dataset REPORT")
            option_map[str(next_option)] = (
                "Generate Full HQ/LQ Dataset REPORT",
                lambda: generate_hq_lq_dataset_report(hq_folder, lq_folder),
            )
            next_option += 1
            print("\n  --- HQ/LQ Dataset Operations ---")
            print(f"  {next_option}. Remove Small Image Pairs (based on min dimension)")
            option_map[str(next_option)] = (
                "Remove Small Image Pairs",
                lambda: remove_small_image_pairs(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Extract Random Image Pairs (subset to new location)"
            )
            option_map[str(next_option)] = (
                "Extract Random Image Pairs",
                lambda: extract_random_pairs(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Shuffle Image Pairs (renames to sequential in place or new location)"
            )
            option_map[str(next_option)] = (
                "Shuffle Image Pairs",
                lambda: shuffle_image_pairs(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Transform Dataset (Rotate, Flip, Brightness, etc. on subset)"
            )
            option_map[str(next_option)] = (
                "Transform Dataset",
                lambda: transform_dataset(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Dataset Color Adjustment (Contrast, Saturation, etc. on subset)"
            )
            option_map[str(next_option)] = (
                "Dataset Color Adjustment",
                lambda: dataset_colour_adjustment(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Grayscale Conversion (convert subset to grayscale)"
            )
            option_map[str(next_option)] = (
                "Grayscale Conversion",
                lambda: grayscale_conversion(hq_folder, lq_folder),
            )
            next_option += 1
            print(
                f"  {next_option}. Advanced Split/Adjust Dataset (Remove by criteria, Split)"
            )
            option_map[str(next_option)] = (
                "Advanced Split/Adjust Dataset",
                lambda: split_adjust_dataset(hq_folder, lq_folder),
            )
            next_option += 1
        print("\n  --- General Dataset Operations ---")
        print(
            f"  {next_option}. Combine Multiple Datasets (merges several HQ/LQ paired datasets)"
        )
        option_map[str(next_option)] = ("Combine Multiple Datasets", combine_datasets)
        next_option += 1
        print(f"  {next_option}. Find Alpha (detect images with alpha channels)")
        option_map[str(next_option)] = (
            "Find Alpha",
            lambda: find_alpha_channels(hq_folder, lq_folder),
        )
        next_option += 1
        print(f"  {next_option}. Remove Alpha (remove alpha channels from images)")
        option_map[str(next_option)] = (
            "Remove Alpha",
            lambda: remove_alpha_channels(hq_folder, lq_folder),
        )
        next_option += 1
        print(f"  {next_option}. Comparisons (create side-by-side HQ/LQ comparisons)")
        option_map[str(next_option)] = (
            "Comparisons",
            lambda: create_comparison_images(hq_folder, lq_folder),
        )
        next_option += 1
        print(
            f"  {next_option}. Fix Corrupted Images (re-save images to fix corruption)"
        )
        option_map[str(next_option)] = (
            "Fix Corrupted Images",
            lambda: fix_corrupted_images(hq_folder),
        )
        next_option += 1
        print(
            f"  {next_option}. Optimize PNG (convert all to PNG and optimize with oxipng)"
        )
        option_map[str(next_option)] = (
            "Optimize PNG",
            lambda: optimize_png_menu(hq_folder, lq_folder),
        )
        next_option += 1
        print(f"  {next_option}. Convert to WebP (convert all images to WebP format)")
        option_map[str(next_option)] = (
            "Convert to WebP",
            lambda: convert_to_webp_menu(hq_folder, lq_folder),
        )
        next_option += 1
        print(f"  {next_option}. HQ/LQ Dataset Image Tiling (create image tiles)")
        option_map[str(next_option)] = (
            "HQ/LQ Dataset Image Tiling",
            lambda: tile_dataset_menu(hq_folder, lq_folder),
        )
        next_option += 1
        print(
            f"  {next_option}. Create HQ/LQ Animated gif/webp Comparisons (animated gifs/webps of pairs)"
        )
        option_map[str(next_option)] = (
            "Create HQ/LQ Animated gif/webp Comparisons",
            lambda: create_gif_comparison(hq_folder, lq_folder),
        )
        next_option += 1
        print(f"  {next_option}. Extract Frames (from video)")
        option_map[str(next_option)] = ("Extract Frames", extract_frames_menu)
        next_option += 1
        print(f"  {next_option}. Exit")
        option_map[str(next_option)] = ("Exit", None)
        print("-" * 40)

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            hq_folder = get_folder_path("Enter HQ folder path: ")
            lq_folder = get_folder_path("Enter LQ folder path: ")
        elif choice in option_map and option_map[choice][1]:
            option_map[choice][1]()
        elif choice in option_map and option_map[choice][0] == "Exit":
            print("Exiting Image Training Dataset Utility. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")

        # Add a small pause or press enter to continue, especially after long reports
        if choice not in [
            "1",
            str(next_option - 1),
        ]:  # Don't pause after setting folders or exiting
            input("\nPress Enter to return to the main menu...")


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
