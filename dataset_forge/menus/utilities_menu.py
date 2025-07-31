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
    def _action(*args, **kwargs):
        return monitoring.time_and_record_menu_load(
            func_name,
            lambda: getattr(importlib.import_module(module_path), func_name)(
                *args, **kwargs
            ),
        )

    return _action


def utilities_menu():
    from dataset_forge.utils.printing import print_error

    options = {
        "1": (
            "🖼️  Create Comparison Images (Side-by-side)",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.comparison_actions",
                    "create_comparison_images",
                )
            ),
        ),
        "2": (
            "🎬 Create GIF Comparison",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.comparison_actions", "create_gif_comparison"
                )
            ),
        ),
        "3": (
            "🔍 Compare Folder Contents",
            lazy_action(
                "dataset_forge.actions.comparison_actions", "compare_folders_menu"
            ),
        ),
        "4": (
            "🗜️  Compress Images",
            lazy_action("dataset_forge.menus.compress_menu", "compress_menu"),
        ),
        "5": (
            "📦 Compress Directory",
            lazy_action("dataset_forge.menus.compress_dir_menu", "compress_dir_menu"),
        ),
        "6": (
            "🧹 Sanitize Images",
            lazy_action(
                "dataset_forge.menus.sanitize_images_menu", "sanitize_images_menu"
            ),
        ),
        "7": ("🧹 Filter non-Images", lazy_action(__name__, "filter_non_images_menu")),
        "8": (
            "🌳 Enhanced Directory Tree",
            lazy_action(
                "dataset_forge.menus.directory_tree_menu", "directory_tree_menu"
            ),
        ),
        "0": ("⬅️  Back to Main Menu", None),
    }
    # Define menu context for help system
    menu_context = {
        "Purpose": "Access various utility functions and tools",
        "Total Options": "8 utility categories",
        "Navigation": "Use numbers 1-8 to select, 0 to go back",
        "Key Features": "Path management, file operations, directory trees, filtering",
    }

    while True:
        key = show_menu(
            "🛠️  Utilities",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Utilities",
            menu_context=menu_context,
        )
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


def filter_non_images_menu():
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
    )
    import os

    print_info("\n=== Filter non-Images ===")
    print_info("1. Single folder")
    print_info("2. HQ/LQ paired folders")
    print_info("0. Back")
    mode = input("Select mode [1-2, 0]: ").strip()
    if mode == "0":
        return
    if mode not in ("1", "2"):
        print_warning("Invalid selection.")
        return
    if mode == "1":
        folder = get_path_with_history(
            "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        if not folder or not os.path.isdir(folder):
            print_error("Folder does not exist.")
            return
        hq = lq = None
    else:
        hq = get_path_with_history(
            "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        if not os.path.isdir(hq) or not os.path.isdir(lq):
            print_error("Both HQ and LQ folders must exist.")
            return
        folder = None
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
            hq_folder=hq,
            lq_folder=lq,
            operation=operation,
            dest_dir=dest_dir,
            dry_run=dry_run,
        )
        print_success(f"Filter non-Images complete. Results: {result}")
    except Exception as e:
        print_error(f"Error: {e}")


def directory_tree_menu():
    """Directory tree menu integration."""
    from dataset_forge.menus.directory_tree_menu import directory_tree_menu as tree_menu

    tree_menu()
