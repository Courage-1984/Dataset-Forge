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
from dataset_forge.menus.compress_menu import compress_menu
from dataset_forge.menus.compress_dir_menu import compress_dir_menu
from dataset_forge.menus import session_state
from dataset_forge.menus.sanitize_images_menu import sanitize_images_menu


def require_hq_lq(func):
    def wrapper(*args, **kwargs):
        if not session_state.hq_folder or not session_state.lq_folder:
            print_error(
                "HQ and LQ folders must be set in the Settings menu before using this option."
            )
            return
        return func(*args, **kwargs)

    return wrapper


def utilities_menu():
    from dataset_forge.actions.comparison_actions import (
        create_comparison_images,
        create_gif_comparison,
        compare_folders_menu,
    )

    options = {
        "1": (
            "Create Comparison Images (Side-by-side)",
            require_hq_lq(
                lambda: create_comparison_images(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "2": (
            "Create GIF Comparison",
            require_hq_lq(
                lambda: create_gif_comparison(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "3": ("Compare Folder Contents", compare_folders_menu),
        "4": ("Compress Images", compress_menu),
        "5": ("Compress Directory", compress_dir_menu),
        "6": ("Sanitize Images", sanitize_images_menu),
        "0": ("Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "Utilities",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action()
