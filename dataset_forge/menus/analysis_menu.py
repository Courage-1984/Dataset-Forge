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


# Lazy import for bhi filtering menu
def bhi_filtering_menu():
    """Lazy import wrapper for bhi_filtering_menu."""
    from dataset_forge.utils.menu import lazy_menu
    return lazy_menu("dataset_forge.menus.bhi_filtering_menu", "bhi_filtering_menu")()


from dataset_forge.menus import session_state
from dataset_forge.utils.input_utils import get_path_with_history
from dataset_forge.utils import monitoring


def require_hq_lq(func):
    def wrapper(*args, **kwargs):
        if not session_state.hq_folder or not session_state.lq_folder:
            print_error(
                "HQ and LQ folders must be set in the Settings menu before using this option."
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


# All action imports moved inside the menu options or functions that use them.


def analysis_menu():
    """Main analysis menu for dataset analysis and validation."""
    from dataset_forge.actions import analysis_actions
    from dataset_forge.actions import alpha_actions
    from dataset_forge.menus import bhi_filtering_menu

    def require_hq_lq(func):
        def wrapper(*args, **kwargs):
            hq_folder = get_folder_path("📁 Enter HQ folder path: ")
            lq_folder = get_folder_path(
                "📁 Enter LQ folder path: ", allow_blank=True, allow_hq_lq_options=False
            )
            return func(hq_folder, lq_folder, *args, **kwargs)

        return wrapper

    def lazy_action(module_path, func_name):
        def _action(*args, **kwargs):
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            return func(*args, **kwargs)

        return _action

    options = {
        "1": (
            "📊 Progressive Dataset Validation",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.analysis_actions",
                    "progressive_dataset_validation",
                )
            ),
        ),
        "2": (
            "Generate HQ/LQ Dataset Report",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.analysis_actions",
                    "generate_hq_lq_dataset_report",
                )
            ),
        ),
        "3": (
            "Find HQ/LQ Scale",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.analysis_actions", "find_hq_lq_scale"
                )
            ),
        ),
        "4": (
            "Test HQ/LQ Scale",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.analysis_actions", "test_hq_lq_scale"
                )
            ),
        ),
        "5": (
            "Check Dataset Consistency",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.analysis_actions", "check_consistency"
                )
            ),
        ),
        "6": (
            "Report Image Dimensions",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.analysis_actions", "report_dimensions"
                )
            ),
        ),
        "7": (
            "Find Extreme Image Dimensions",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.analysis_actions", "find_extreme_dimensions"
                )
            ),
        ),
        "8": (
            "Verify Images (Corruption Check)",
            require_hq_lq(
                lazy_action("dataset_forge.actions.analysis_actions", "verify_images")
            ),
        ),
        "9": (
            "Fix Corrupted Images",
            lazy_action(
                "dataset_forge.actions.corruption_actions", "fix_corrupted_images"
            ),
        ),
        "10": (
            "Find Misaligned Images",
            require_hq_lq(
                lazy_action(
                    "dataset_forge.actions.analysis_actions", "find_misaligned_images"
                )
            ),
        ),
        "11": (
            "Find Images with Alpha Channel",
            lazy_action(
                "dataset_forge.actions.alpha_actions", "find_alpha_channels_menu"
            ),
        ),
        "12": ("BHI Filtering (Blockiness, HyperIQA, IC9600)", bhi_filtering_menu),
        "13": (
            "Test Aspect Ratio",
            lazy_action("dataset_forge.actions.analysis_actions", "test_aspect_ratio"),
        ),
        "0": ("Back to Main Menu", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Analyze dataset quality and validate image pairs",
        "Total Options": "13 analysis operations",
        "Navigation": "Use numbers 1-13 to select, 0 to go back",
        "Key Features": "Dataset validation, quality assessment, corruption detection, pair analysis",
    }

    while True:
        key = show_menu(
            "Analysis Menu",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Analysis Menu",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options[key][1]
        if callable(action):
            action()
