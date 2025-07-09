# compress_dir_menu.py - CLI entry for directory/folder compression
from dataset_forge.actions.compress_dir_actions import compress_directory
from dataset_forge.utils.input_utils import get_folder_path
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
)
from dataset_forge.utils.color import Mocha


def compress_dir_menu():
    print_header("Compress Directory", color=Mocha.lavender)
    print_info("Choose input mode:")
    mode_options = {
        "1": ("HQ/LQ paired folders", "paired"),
        "2": ("Single folder", "single"),
        "0": ("Cancel", None),
    }
    mode = show_menu("Select Input Mode", mode_options, header_color=Mocha.sapphire)
    if mode is None:
        print_info("Cancelled.")
        return
    if mode == "paired":
        hq_path = get_folder_path("Enter HQ folder path: ")
        lq_path = get_folder_path("Enter LQ folder path: ")
        single_folder = None
    else:
        single_folder = get_folder_path("Enter folder path: ")
        hq_path = lq_path = None

    print_info("\nChoose archive format:")
    fmt_options = {
        "1": ("ZIP (.zip)", "zip"),
        "2": ("TAR (.tar)", "tar"),
        "3": ("TAR.GZ (.tar.gz)", "gztar"),
        "0": ("Cancel", None),
    }
    fmt = show_menu("Select Archive Format", fmt_options, header_color=Mocha.sapphire)
    if fmt is None:
        print_info("Cancelled.")
        return

    compression_level = 5
    if fmt in ["zip", "gztar"]:
        try:
            compression_level = int(
                input("Enter compression level (1-9, default 5): ").strip() or "5"
            )
            if not (1 <= compression_level <= 9):
                print_info("Invalid level, using default 5.")
                compression_level = 5
        except Exception:
            print_info("Invalid input, using default 5.")
            compression_level = 5

    print_info("\nStarting directory compression...")
    compress_directory(
        src_hq=hq_path,
        src_lq=lq_path,
        single_folder=single_folder,
        archive_format=fmt,
        compression_level=compression_level,
    )
    print_success("Directory compression complete!")
