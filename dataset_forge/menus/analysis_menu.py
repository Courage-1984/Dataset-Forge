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


def require_hq_lq(func):
    def wrapper(*args, **kwargs):
        if not session_state.hq_folder or not session_state.lq_folder:
            print_error(
                "HQ and LQ folders must be set in the Settings menu before using this option."
            )
            return
        return func(*args, **kwargs)

    return wrapper


# All action imports moved inside the menu options or functions that use them.


def analysis_menu():
    from dataset_forge.actions.analysis_actions import (
        generate_hq_lq_dataset_report,
        find_hq_lq_scale,
        test_hq_lq_scale,
        check_consistency,
        report_dimensions,
        find_extreme_dimensions,
        verify_images,
        find_misaligned_images,
        test_aspect_ratio,
        progressive_dataset_validation,
    )
    from dataset_forge.actions.alpha_actions import find_alpha_channels_menu
    from dataset_forge.actions.corruption_actions import (
        fix_corrupted_images,
        fix_corrupted_images_hq_lq,
    )

    options = {
        "1": (
            "Progressive Dataset Validation (All Checks)",
            require_hq_lq(
                lambda: progressive_dataset_validation(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "2": (
            "Generate HQ/LQ Dataset Report",
            require_hq_lq(
                lambda: generate_hq_lq_dataset_report(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "3": (
            "Find HQ/LQ Scale",
            require_hq_lq(
                lambda: find_hq_lq_scale(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "4": (
            "Test HQ/LQ Scale",
            require_hq_lq(
                lambda: test_hq_lq_scale(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "5": (
            "Check Dataset Consistency",
            require_hq_lq(
                lambda: (
                    check_consistency(session_state.hq_folder, "HQ"),
                    check_consistency(session_state.lq_folder, "LQ"),
                )
            ),
        ),
        "6": (
            "Report Image Dimensions",
            require_hq_lq(
                lambda: (
                    report_dimensions(session_state.hq_folder, "HQ"),
                    report_dimensions(session_state.lq_folder, "LQ"),
                )
            ),
        ),
        "7": (
            "Find Extreme Image Dimensions",
            require_hq_lq(
                lambda: (
                    find_extreme_dimensions(session_state.hq_folder, "HQ"),
                    find_extreme_dimensions(session_state.lq_folder, "LQ"),
                )
            ),
        ),
        "8": (
            "Verify Images (Corruption Check)",
            require_hq_lq(
                lambda: verify_images(session_state.hq_folder, session_state.lq_folder)
            ),
        ),
        "9": (
            "Fix Corrupted Images",
            lambda: (
                (
                    lambda hq, lq: (
                        fix_corrupted_images_hq_lq(hq, lq)
                        if lq
                        else fix_corrupted_images(hq)
                    )
                )(
                    input("Enter HQ folder path (or single folder): ").strip(),
                    input(
                        "Enter LQ folder path (leave blank for single-folder): "
                    ).strip(),
                )
            ),
        ),
        "10": (
            "Find Misaligned Images",
            require_hq_lq(
                lambda: find_misaligned_images(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "11": ("Find Images with Alpha Channel", find_alpha_channels_menu),
        "12": ("BHI Filtering (Blockiness, HyperIQA, IC9600)", bhi_filtering_menu),
        "13": ("Test Aspect Ratio", test_aspect_ratio),
        "0": ("Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "Analysis Menu",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action()
