import importlib
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_section,
    print_success,
    print_warning,
    print_error,
    print_info,
    print_prompt,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.menus import session_state
from dataset_forge.utils import monitoring


def require_hq_lq(func):
    def wrapper(*args, **kwargs):
        if not session_state.hq_folder or not session_state.lq_folder:
            print_error(
                "❌ HQ and LQ folders must be set in the Settings menu before using this option."
            )
            return
        return func(*args, **kwargs)

    return wrapper


def lazy_action(module_path, func_name):
    @monitoring.time_and_record_menu_load(func_name)
    def _action(*args, **kwargs):
        return getattr(importlib.import_module(module_path), func_name)(*args, **kwargs)

    return _action


def utilities_menu():
    from dataset_forge.utils.printing import print_error

    options = {
        "1": (
            "🔍 Comparison Tools",
            lazy_action(
                "dataset_forge.actions.comparison_actions", "compare_folders_menu"
            ),
        ),
        "2": (
            "🖼️ Visual Comparisons",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.comparison_actions",
                    "create_comparison_images",
                )
            ),
        ),
        "3": (
            "🎬 GIF Comparisons",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.comparison_actions",
                    "create_comparison_gifs",
                )
            ),
        ),
        "4": (
            "🔍 Consolidated De-duplication",
            lazy_menu(
                "dataset_forge.menus.consolidated_dedup_menu", "consolidated_dedup_menu"
            ),
        ),
        "5": (
            "🗜️ Consolidated Compression",
            lazy_menu(
                "dataset_forge.menus.consolidated_compression_menu",
                "consolidated_compression_menu",
            ),
        ),
        "6": (
            "🧹 Sanitization Tools",
            lazy_menu(
                "dataset_forge.menus.sanitize_images_menu", "sanitize_images_menu"
            ),
        ),
        "7": (
            "🌳 Directory Tools",
            lazy_menu("dataset_forge.menus.directory_tree_menu", "directory_tree_menu"),
        ),
        "8": (
            "📁 File Filtering",
            filter_non_images_menu,
        ),
        "0": ("⬅️ Back to Main Menu", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Helper tools and utilities for dataset management and analysis",
        "Total Options": "8 utility categories",
        "Navigation": "Use numbers 1-8 to select, 0 to go back",
        "Key Features": [
            "🔍 Comparison Tools - Compare folders and analyze differences",
            "🖼️ Visual Comparisons - Create side-by-side comparison images",
            "🎬 GIF Comparisons - Generate animated comparison GIFs",
            "🔍 Consolidated De-duplication - Comprehensive duplicate detection and removal",
            "🗜️ Consolidated Compression - Compress individual images and directories",
            "🧹 Sanitization Tools - Clean and sanitize image files",
            "🌳 Directory Tools - Enhanced directory tree visualization",
            "📁 File Filtering - Filter and manage non-image files",
        ],
        "Tips": [
            "Comparison tools help identify differences between datasets",
            "Visual comparisons are great for quality assessment",
            "Consolidated De-duplication combines all duplicate detection methods",
            "Consolidated Compression handles both individual and batch compression",
            "Sanitization tools ensure image file integrity",
            "Directory tools provide detailed folder structure analysis",
        ],
    }

    while True:
        try:
            key = show_menu(
                "🛠️ Utilities",
                options,
                Mocha.lavender,
                current_menu="Utilities",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break


def filter_non_images_menu():
    """Filter non-images menu with standardized pattern."""
    from dataset_forge.actions.dataset_actions import filter_non_images
    from dataset_forge.utils.input_utils import (
        get_path_with_history,
        get_file_operation_choice,
        get_destination_path,
    )
    from dataset_forge.utils.printing import (
        print_info,
        print_success,
        print_warning,
        print_error,
        print_header,
        print_section,
    )
    from dataset_forge.utils.color import Mocha
    import os

    def run_single_folder_filter():
        """Run single folder filter workflow."""
        folder = get_path_with_history(
            "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        if not folder or not os.path.isdir(folder):
            print_error("Folder does not exist.")
            return

        operation = get_file_operation_choice()
        dest_dir = None
        if operation in ("move", "copy"):
            dest_dir = get_destination_path()
            if not dest_dir:
                print_error("Destination directory is required for move/copy.")
                return

        dry_run = input("Dry run (no changes)? [y/N]: ").strip().lower() == "y"

        try:
            result = filter_non_images(
                folder=folder,
                hq_folder=None,
                lq_folder=None,
                operation=operation,
                dest_dir=dest_dir,
                dry_run=dry_run,
            )
            print_success(f"Filter non-Images complete. Results: {result}")
        except Exception as e:
            print_error(f"Error: {e}")

    def run_hq_lq_filter():
        """Run HQ/LQ paired folders filter workflow."""
        hq = get_path_with_history(
            "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        if not os.path.isdir(hq) or not os.path.isdir(lq):
            print_error("Both HQ and LQ folders must exist.")
            return

        operation = get_file_operation_choice()
        dest_dir = None
        if operation in ("move", "copy"):
            dest_dir = get_destination_path()
            if not dest_dir:
                print_error("Destination directory is required for move/copy.")
                return

        dry_run = input("Dry run (no changes)? [y/N]: ").strip().strip().lower() == "y"

        try:
            result = filter_non_images(
                folder=None,
                hq_folder=hq,
                lq_folder=lq,
                operation=operation,
                dest_dir=dest_dir,
                dry_run=dry_run,
            )
            print_success(f"Filter non-Images complete. Results: {result}")
        except Exception as e:
            print_error(f"Error: {e}")

    options = {
        "1": ("Single folder", run_single_folder_filter),
        "2": ("HQ/LQ paired folders", run_hq_lq_filter),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Filter non-image files from folders",
        "Total Options": "2 filtering modes",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
        "Key Features": [
            "Single folder filtering - Remove non-image files from a single folder",
            "HQ/LQ paired folders filtering - Remove non-image files from paired folders",
            "Support for move, copy, delete operations",
            "Dry run mode for safe testing",
        ],
        "Tips": [
            "Use dry run mode first to preview changes",
            "Choose appropriate operation based on your needs",
            "Ensure backup before using delete operation",
        ],
    }

    while True:
        key = show_menu(
            "🧹 Filter non-Images",
            options,
            Mocha.lavender,
            current_menu="Filter non-Images",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()


def directory_tree_menu():
    """Directory tree menu integration."""
    # Lazy import for directory tree menu
    from dataset_forge.utils.menu import lazy_menu

    return lazy_menu("dataset_forge.menus.directory_tree_menu", "directory_tree_menu")()
