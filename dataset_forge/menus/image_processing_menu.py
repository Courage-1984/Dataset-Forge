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
from dataset_forge.actions.transform_actions import (
    downsample_images_menu,
    hdr_to_sdr_menu,
    dataset_colour_adjustment,
    grayscale_conversion,
    remove_alpha_channels_menu,
    transform_dataset,
)
from dataset_forge.menus.hue_adjustment_menu import hue_adjustment_menu
from dataset_forge.menus.augmentation_menu import augmentation_menu
from dataset_forge.actions.metadata_actions import (
    exif_scrubber_menu,
    icc_to_srgb_menu,
)
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


def basic_transformations_menu():
    """Sub-menu for basic image transformations."""
    options = {
        "1": ("Downsample Images", downsample_images_menu),
        "2": ("Convert HDR to SDR", hdr_to_sdr_menu),
        "3": (
            "Convert to Grayscale",
            require_hq_lq(
                lambda: grayscale_conversion(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "4": ("Remove Alpha Channel", remove_alpha_channels_menu),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Basic Transformations",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def color_tone_adjustments_menu():
    """Sub-menu for color and tone adjustments."""
    options = {
        "1": (
            "General Color/Tone Adjustments",
            require_hq_lq(
                lambda: dataset_colour_adjustment(
                    session_state.hq_folder, session_state.lq_folder
                )
            ),
        ),
        "2": ("Hue/Brightness/Contrast", hue_adjustment_menu),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Color & Tone Adjustments",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def metadata_menu():
    """Sub-menu for metadata operations."""
    options = {
        "1": ("Scrub EXIF Data", exif_scrubber_menu),
        "2": ("Convert ICC Profile to sRGB", icc_to_srgb_menu),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Metadata",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def augmentation_submenu():
    """Sub-menu for augmentation operations."""
    options = {
        "1": (
            "Run Augmentation Pipeline/Recipes",
            augmentation_menu,
        ),
        "2": ("Apply Custom Transformations", transform_dataset),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Augmentation",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def image_processing_menu():
    """Main image processing and augmentation menu with hierarchical structure."""
    options = {
        "1": ("Basic Transformations", basic_transformations_menu),
        "2": ("Color & Tone Adjustments", color_tone_adjustments_menu),
        "3": ("Metadata", metadata_menu),
        "4": ("Augmentation", augmentation_submenu),
        "0": ("Back to Main Menu", None),
    }

    while True:
        action = show_menu(
            "Image Processing & Augmentation",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action()
