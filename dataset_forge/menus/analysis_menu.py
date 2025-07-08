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
from dataset_forge.actions.analysis_actions import (
    generate_hq_lq_dataset_report,
    find_hq_lq_scale,
    test_hq_lq_scale,
    check_consistency,
    report_dimensions,
    find_extreme_dimensions,
    verify_images,
    find_misaligned_images,
)
from dataset_forge.alpha import find_alpha_channels
from dataset_forge.corruption import fix_corrupted_images
from dataset_forge.menus.bhi_filtering_menu import bhi_filtering_menu
from dataset_forge.menus import session_state

# Assume require_hq_lq, hq_folder, lq_folder are available in the global scope for now


def require_hq_lq(func):
    def wrapper(*args, **kwargs):
        if not session_state.hq_folder or not session_state.lq_folder:
            print_error(
                "HQ and LQ folders must be set in the Settings menu before using this option."
            )
            return
        return func(*args, **kwargs)

    return wrapper


def analysis_menu():
    options = {
        "1": (
            "Generate HQ/LQ Dataset Report",
            require_hq_lq(
                lambda: generate_hq_lq_dataset_report(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "2": (
            "Find HQ/LQ Scale",
            require_hq_lq(
                lambda: find_hq_lq_scale(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "3": (
            "Test HQ/LQ Scale",
            require_hq_lq(
                lambda: test_hq_lq_scale(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "4": (
            "Check Dataset Consistency",
            require_hq_lq(
                lambda: (
                    check_consistency(session_state.hq_folder, "HQ"),
                    check_consistency(session_state.lq_folder, "LQ"),
                )
            ),
        ),
        "5": (
            "Report Image Dimensions",
            require_hq_lq(
                lambda: (
                    report_dimensions(session_state.hq_folder, "HQ"),
                    report_dimensions(session_state.lq_folder, "LQ"),
                )
            ),
        ),
        "6": (
            "Find Extreme Image Dimensions",
            require_hq_lq(
                lambda: (
                    find_extreme_dimensions(session_state.hq_folder, "HQ"),
                    find_extreme_dimensions(session_state.lq_folder, "LQ"),
                )
            ),
        ),
        "7": (
            "Verify Images (Corruption Check)",
            require_hq_lq(
                lambda: verify_images(session_state.hq_folder, session_state.lq_folder)
            ),
        ),
        "8": (
            "Fix Corrupted Images",
            require_hq_lq(lambda: fix_corrupted_images(session_state.hq_folder)),
        ),
        "9": (
            "Find Misaligned Images",
            require_hq_lq(
                lambda: find_misaligned_images(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "10": (
            "Find Images with Alpha Channel",
            require_hq_lq(
                lambda: find_alpha_channels(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
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
        print_prompt("\nPress Enter to return to the menu...")
        input()
