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
from dataset_forge.menus.hue_adjustment_menu import hue_adjustment_menu
from dataset_forge.menus import session_state


def require_hq_lq(func):
    def wrapper(*args, **kwargs):
        if not session_state.hq_folder or not session_state.lq_folder:
            print_error(
                "HQ and LQ folders must be set in the Settings menu before using this option."
            )
            return
        return func(*args, **kwargs)

    return wrapper


def transform_menu():
    from dataset_forge.actions.transform_actions import (
        downsample_images_menu,
        hdr_to_sdr_menu,
        dataset_colour_adjustment,
        grayscale_conversion,
        transform_dataset,
    )
    from dataset_forge.actions.alpha_actions import remove_alpha_channels_menu

    options = {
        "1": ("Downsample Images", downsample_images_menu),
        "2": ("Convert HDR to SDR", hdr_to_sdr_menu),
        "3": (
            "Color/Tone Adjustments",
            require_hq_lq(
                lambda: dataset_colour_adjustment(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "4": ("Hue/Brightness/Contrast Adjustment", hue_adjustment_menu),
        "5": (
            "Grayscale Conversion",
            require_hq_lq(
                lambda: grayscale_conversion(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "6": ("Remove Alpha Channel", remove_alpha_channels_menu),
        "7": ("Apply Custom Transformations", transform_dataset),
        "0": ("Back to Main Menu", None),
    }
    while True:
        choice = show_menu(
            "Transform Menu",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if choice is None or choice == "0":
            break
        action = options[choice][1]
        if callable(action):
            action()
