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
from dataset_forge.menus.bhi_filtering_menu import bhi_filtering_menu
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
    options = {
        "1": (
            "Progressive Dataset Validation (All Checks)",
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
    while True:
        choice = show_menu(
            "Analysis Menu",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if choice is None or choice == "0":
            break
        action = options[choice][1]
        if callable(action):
            action()
