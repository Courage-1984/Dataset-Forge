# compress_dir_menu.py - CLI entry for directory/folder compression
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.input_utils import get_folder_path


def compress_dir_menu():
    from dataset_forge.actions.compress_dir_actions import compress_directory

    print_header("Compress Directory", color=Mocha.lavender)
    input_dir = get_folder_path("Enter input directory path: ")
    if not input_dir:
        print_error("No input directory specified.")
        return

    output_dir = get_folder_path("Enter output directory path: ")
    if not output_dir:
        print_error("No output directory specified.")
        return

    try:
        quality = int(input("Enter quality (1-100, default 85): ").strip() or "85")
        if not (1 <= quality <= 100):
            print_error("Quality must be between 1 and 100.")
            return
    except ValueError:
        print_error("Invalid quality value.")
        return

    format_choice = (
        input("Output format (jpeg/png/webp, default jpeg): ").strip().lower() or "jpeg"
    )
    if format_choice not in ["jpeg", "png", "webp"]:
        print_error("Invalid format. Using jpeg.")
        format_choice = "jpeg"

    print_info("Starting directory compression...")
    try:
        compress_directory(input_dir, output_dir, quality=quality, format=format_choice)
        print_success("Directory compression completed successfully!")
    except Exception as e:
        print_error(f"Compression failed: {e}")
