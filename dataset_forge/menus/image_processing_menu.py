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


# Lazy import for degradations menu
def degradations_menu():
    """Lazy import wrapper for degradations_menu."""
    from dataset_forge.utils.menu import lazy_menu

    return lazy_menu("dataset_forge.menus.degradations_menu", "degradations_menu")()


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
        import importlib

        return getattr(importlib.import_module(module_path), func_name)(*args, **kwargs)

    return _action


def basic_transformations_menu():
    """Sub-menu for basic image transformations."""
    from dataset_forge.actions import transform_actions

    options = {
        "1": (
            "🔄 Resize Images",
            lazy_action(
                "dataset_forge.actions.transform_actions", "resize_images_menu"
            ),
        ),
        "2": (
            "✂️  Crop Images",
            lazy_action("dataset_forge.actions.transform_actions", "crop_images_menu"),
        ),
        "3": (
            "🔄 Rotate Images",
            lazy_action(
                "dataset_forge.actions.transform_actions", "rotate_images_menu"
            ),
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
        "6": (
            "💾 Resave Images",
            lazy_action("dataset_forge.menus.resave_images_menu", "resave_images_menu"),
        ),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Apply basic geometric transformations to images",
        "Options": "6 transformation types available",
        "Navigation": "Use numbers 1-6 to select, 0 to go back",
        "Key Features": [
            "🔄 Resize Images - Change image dimensions while maintaining aspect ratio",
            "✂️ Crop Images - Remove unwanted areas from images",
            "🔄 Rotate Images - Rotate images by specified angles",
            "🔄 Flip Images - Mirror images horizontally or vertically",
            "🔄 Shuffle Images - Randomize image order for training",
            "💾 Resave Images - Convert image formats and optimize file sizes",
        ],
        "Tips": [
            "Resize is useful for standardizing image dimensions",
            "Crop helps focus on important image regions",
            "Rotation corrects image orientation issues",
            "Flipping creates additional training variations",
            "Shuffling improves training randomization",
            "Resaving optimizes file formats and compression",
        ],
    }

    while True:
        key = show_menu(
            "🔄 Geometric Transformations",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Geometric Transformations",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        if callable(action):
            action()


def not_implemented_menu():
    """Placeholder for unimplemented features."""
    from dataset_forge.utils.printing import print_warning, print_info

    print_warning("This feature is not implemented yet.")
    print_info("Press Enter to return to the menu...")
    input()


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

    # Lazy imports for color adjustment menus
    def brightness_adjustment_menu():
        from dataset_forge.utils.menu import lazy_menu

        return lazy_menu(
            "dataset_forge.menus.color_adjustment_menu", "brightness_adjustment_menu"
        )()

    def contrast_adjustment_menu():
        from dataset_forge.utils.menu import lazy_menu

        return lazy_menu(
            "dataset_forge.menus.color_adjustment_menu", "contrast_adjustment_menu"
        )()

    def hue_adjustment_menu():
        from dataset_forge.utils.menu import lazy_menu

        return lazy_menu(
            "dataset_forge.menus.color_adjustment_menu", "hue_adjustment_menu"
        )()

    def saturation_adjustment_menu():
        from dataset_forge.utils.menu import lazy_menu

        return lazy_menu(
            "dataset_forge.menus.color_adjustment_menu", "saturation_adjustment_menu"
        )()

    options = {
        "1": ("☀️  Adjust Brightness", brightness_adjustment_menu),
        "2": ("🌓 Adjust Contrast", contrast_adjustment_menu),
        "3": ("🌈 Adjust Hue", hue_adjustment_menu),
        "4": ("🎨 Adjust Saturation", saturation_adjustment_menu),
        "5": ("🌅 Convert HDR to SDR", hdr_to_sdr_menu),
        "6": ("⚫️ Convert to Grayscale", grayscale_conversion_menu),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Adjust color, tone, and level properties of images",
        "Options": "6 adjustment types available",
        "Navigation": "Use numbers 1-6 to select, 0 to go back",
        "Key Features": [
            "☀️ Adjust Brightness - Increase or decrease image brightness levels",
            "🌓 Adjust Contrast - Enhance or reduce image contrast",
            "🌈 Adjust Hue - Shift image color hues",
            "🎨 Adjust Saturation - Modify color intensity and vibrancy",
            "🌅 Convert HDR to SDR - Convert high dynamic range to standard range",
            "⚫️ Convert to Grayscale - Remove color information for monochrome processing",
        ],
        "Tips": [
            "Brightness adjustments help normalize lighting conditions",
            "Contrast adjustments improve image clarity and definition",
            "Hue adjustments can correct color temperature issues",
            "Saturation adjustments control color intensity",
            "HDR to SDR conversion is useful for compatibility",
            "Grayscale conversion reduces data complexity for certain models",
        ],
    }

    while True:
        key = show_menu(
            "🎨 Color & Tone Adjustments",
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
        "Purpose": "Manage image metadata and color profiles for standardization",
        "Options": "2 metadata operations available",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
        "Key Features": [
            "🧹 Scrub EXIF Data - Remove camera and location metadata from images",
            "🎯 Convert ICC Profile to sRGB - Standardize color profiles for consistency",
        ],
        "Tips": [
            "EXIF scrubbing removes privacy-sensitive metadata",
            "ICC profile conversion ensures consistent color reproduction",
            "Metadata management is important for dataset standardization",
            "Clean metadata improves model training consistency",
            "Always backup original images before metadata operations",
        ],
    }

    while True:
        key = show_menu(
            "📋 Metadata Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Metadata Management",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        if callable(action):
            action()


def augmentation_submenu():
    """Sub-menu for image augmentation."""

    # Lazy import for augmentation menu
    def get_augmentation_menu():
        from dataset_forge.utils.menu import lazy_menu

        return lazy_menu("dataset_forge.menus.augmentation_menu", "augmentation_menu")

    get_augmentation_menu()()


def extract_sketches_menu():
    """Sub-menu for sketch extraction."""

    # Lazy import for sketch extraction menu
    def get_extract_sketches_menu():
        from dataset_forge.utils.menu import lazy_menu

        return lazy_menu(
            "dataset_forge.actions.sketch_extraction_actions", "extract_sketches_menu"
        )

    get_extract_sketches_menu()()


def image_processing_menu():
    """Main image processing menu."""
    options = {
        "1": ("🔄 Geometric Transformations", basic_transformations_menu),
        "2": ("🎨 Color & Tone Adjustments", colour_tone_levels_menu),
        "3": ("✨ Image Augmentation", augmentation_submenu),
        "4": ("🔽 DPID Detail-Preserving Downscaling", dpid_submenu),
        "5": ("📋 Metadata Management", metadata_menu),
        "6": ("✏️  Sketch Extraction", extract_sketches_menu),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Transform, enhance, and augment images for machine learning training",
        "Total Options": "6 processing categories",
        "Navigation": "Use numbers 1-6 to select, 0 to go back",
        "Key Features": [
            "🔄 Geometric Transformations - Resize, crop, rotate, flip, and shuffle images",
            "🎨 Color & Tone Adjustments - Brightness, contrast, hue, saturation, and grayscale",
            "✨ Image Augmentation - Advanced augmentation techniques for training",
            "🔽 DPID Detail-Preserving Downscaling - Advanced downscaling with detail preservation",
            "📋 Metadata Management - EXIF data scrubbing and color profile conversion",
            "✏️ Sketch Extraction - Extract sketch-like features from images",
        ],
        "Tips": [
            "Start with Geometric Transformations for basic image modifications",
            "Color adjustments help normalize image appearance",
            "Augmentation increases training dataset diversity",
            "DPID downscaling preserves image details better than standard methods",
            "Metadata management ensures clean, standardized images",
            "Sketch extraction creates specialized training data",
            "Always backup original images before processing",
        ],
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


def dpid_submenu():
    """Sub-menu for DPID downscaling."""
    from dataset_forge.actions.dpid_actions import dpid_menu
    dpid_menu()
