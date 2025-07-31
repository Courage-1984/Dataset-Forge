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
from dataset_forge.menus.degradations_menu import degradations_menu


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
        print(f"DEBUG: lazy_action importing {module_path}.{func_name}")
        import importlib

        return getattr(importlib.import_module(module_path), func_name)(*args, **kwargs)

    return _action


def basic_transformations_menu():
    """Sub-menu for basic image transformations."""
    from dataset_forge.actions import transform_actions

    options = {
        "1": (
            "🔄 Resize Images",
            lazy_action("dataset_forge.actions.transform_actions", "resize_images_menu"),
        ),
        "2": (
            "✂️ Crop Images",
            lazy_action("dataset_forge.actions.transform_actions", "crop_images_menu"),
        ),
        "3": (
            "🔄 Rotate Images",
            lazy_action("dataset_forge.actions.transform_actions", "rotate_images_menu"),
        ),
        "4": (
            "🔄 Flip Images",
            lazy_action("dataset_forge.actions.transform_actions", "flip_images_menu"),
        ),
        "5": (
            "🔄 Shuffle Images",
            lazy_action(
                "dataset_forge.actions.transform_actions", "shuffle_images_menu"
            ),
        ),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Apply basic geometric transformations to images",
        "Options": "5 transformation types available",
        "Navigation": "Use numbers 1-5 to select, 0 to go back",
    }

    while True:
        key = show_menu(
            "🔄 Basic Transformations",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Basic Transformations",
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


def not_implemented_menu():
    from dataset_forge.utils.printing import print_warning

    print_warning("This feature is not implemented yet.")
    input("Press Enter to return to the menu...")


def colour_tone_levels_menu():
    """Sub-menu for color, tone, and level adjustments."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.actions.transform_actions import (
        hdr_to_sdr_menu,
        grayscale_conversion,
    )

    def grayscale_conversion_menu():
        from dataset_forge.utils.input_utils import get_path_with_history
        from dataset_forge.utils.printing import print_info

        print_info(
            "This tool converts all images in both HQ and LQ folders to grayscale."
        )
        hq_folder = get_path_with_history("Enter HQ folder path:")
        lq_folder = get_path_with_history("Enter LQ folder path:")
        if not hq_folder or not lq_folder:
            print_info("Both HQ and LQ folder paths are required.")
            return
        grayscale_conversion(hq_folder, lq_folder)

    from dataset_forge.menus.color_adjustment_menu import (
        brightness_adjustment_menu,
        contrast_adjustment_menu,
        hue_adjustment_menu,
        saturation_adjustment_menu,
    )

    options = {
        "1": ("☀️  Adjust Brightness", brightness_adjustment_menu),
        "2": ("🌓 Adjust Contrast", contrast_adjustment_menu),
        "3": ("🌈 Adjust Hue", hue_adjustment_menu),
        "4": ("🎨 Adjust Saturation (Not implemented)", saturation_adjustment_menu),
        "5": ("🌅 Convert HDR to SDR", hdr_to_sdr_menu),
        "6": ("⚫️ Convert to Grayscale", grayscale_conversion_menu),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Adjust color, tone, and level properties of images",
        "Options": "6 adjustment types available",
        "Navigation": "Use numbers 1-6 to select, 0 to go back",
    }

    while True:
        key = show_menu(
            "🎨 Colour, Tone & Levels Adjustments",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Color & Tone Adjustments",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        if callable(action):
            action()
        input("Press Enter to return to the menu...")


def metadata_menu():
    """Sub-menu for metadata operations."""
    from dataset_forge.actions.metadata_actions import (
        exif_scrubber_menu,
        icc_to_srgb_menu,
    )

    options = {
        "1": (
            "🧹 Scrub EXIF Data",
            lazy_action("dataset_forge.actions.metadata_actions", "exif_scrubber_menu"),
        ),
        "2": (
            "🎯 Convert ICC Profile to sRGB",
            lazy_action("dataset_forge.actions.metadata_actions", "icc_to_srgb_menu"),
        ),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage image metadata and color profiles",
        "Options": "2 metadata operations available",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
    }

    while True:
        key = show_menu(
            "📋 Metadata Operations",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Metadata Operations",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        if callable(action):
            action()


def augmentation_submenu():
    """Sub-menu for image augmentation."""
    from dataset_forge.menus.augmentation_menu import augmentation_menu

    augmentation_menu()


def extract_sketches_menu():
    """Sub-menu for sketch extraction."""
    from dataset_forge.actions.sketch_extraction_actions import extract_sketches_menu

    extract_sketches_menu()


def image_processing_menu():
    """Main image processing menu."""
    options = {
        "1": ("🔄 Basic Transformations", basic_transformations_menu),
        "2": ("🎨 Colour, Tone & Levels", colour_tone_levels_menu),
        "3": ("📋 Metadata Operations", metadata_menu),
        "4": ("✨ Augmentation", augmentation_submenu),
        "5": ("✏️ Extract Sketches", extract_sketches_menu),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Transform, enhance, and augment images for ML training",
        "Total Options": "5 processing categories",
        "Navigation": "Use numbers 1-5 to select, 0 to go back",
        "Key Features": "Geometric transformations, color adjustments, metadata management, augmentation",
    }

    while True:
        key = show_menu(
            "✨ Image Processing & Augmentation",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Image Processing & Augmentation",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        if callable(action):
            action()
