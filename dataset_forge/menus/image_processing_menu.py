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
    from dataset_forge.actions.transform_actions import (
        crop_image_menu,
        flip_image_menu,
        rotate_image_menu,
    )
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.printing import print_error

    options = {
        "1": ("✂️  Crop Image", crop_image_menu),
        "2": ("↔️  Flip Image", flip_image_menu),
        "3": ("🔄 Rotate Image", rotate_image_menu),
        "4": (
            "⬇️  Downsample Images",
            lazy_action(
                "dataset_forge.actions.transform_actions", "downsample_images_menu"
            ),
        ),
        "5": (
            "🧹 Remove Alpha Channel",
            lazy_action(
                "dataset_forge.actions.transform_actions", "remove_alpha_channels_menu"
            ),
        ),
        "6": (
            "🔀 Shuffle Images",
            lazy_action(
                "dataset_forge.actions.transform_actions", "shuffle_images_menu"
            ),
        ),
        "0": ("⬅️  Back", None),
    }
    while True:
        key = show_menu(
            "🔄 Basic Transformations",
            options,
            header_color=Mocha.sapphire,
            char="-",
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
    while True:
        action = show_menu(
            "🎨 Colour, Tone & Levels Adjustments",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None or action == "0":
            break
        if callable(action):
            action()
        input("Press Enter to return to the menu...")


def metadata_menu():
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
    while True:
        action = show_menu(
            "📋 EXIF & ICC Profile Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None or action == "0":
            break
        if callable(action):
            action()
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()


def augmentation_submenu():
    augmentation_menu()


def extract_sketches_menu():
    from dataset_forge.actions.sketch_extraction_actions import (
        extract_sketches_workflow,
    )
    from dataset_forge.utils.input_utils import get_path_with_history
    from dataset_forge.utils.printing import print_info, print_error

    print_header("✏️  Find & extract sketches/drawings/line art", color=Mocha.mauve)
    print_info("Choose input mode:")
    print_info("  1. 📂 HQ/LQ paired folders")
    print_info("  2. 📁 Single folder")
    print_info("  0. ❌ Cancel")
    choice = input("🎯 Select mode: ").strip()
    if choice == "1":
        hq_folder = get_path_with_history("📁 Enter HQ folder path:")
        lq_folder = get_path_with_history("📁 Enter LQ folder path:")
        if not hq_folder or not lq_folder:
            print_error("❌ Both HQ and LQ paths are required.")
            return
        try:
            confidence = float(
                input("🎯 Confidence threshold (default 0.5): ").strip() or "0.5"
            )
        except Exception:
            confidence = 0.5
        extract_sketches_workflow(
            hq_folder=hq_folder, lq_folder=lq_folder, confidence_threshold=confidence
        )
    elif choice == "2":
        folder = get_path_with_history("📁 Enter folder path:")
        if not folder:
            print_error("❌ Folder path is required.")
            return
        try:
            confidence = float(
                input("🎯 Confidence threshold (default 0.5): ").strip() or "0.5"
            )
        except Exception:
            confidence = 0.5
        extract_sketches_workflow(single_folder=folder, confidence_threshold=confidence)
    elif choice == "0":
        print_info("❌ Operation cancelled.")
        return
    else:
        print_error("❌ Invalid choice. Operation cancelled.")
        return


def image_processing_menu():
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha

    options = {
        "1": ("🔄 Basic Transformations", basic_transformations_menu),
        "2": ("🎨 Colour, Tone & Levels Adjustments", colour_tone_levels_menu),
        "3": ("🧪 Degradations", degradations_menu),
        "4": (
            "🚀 Augmentation",
            lazy_action("dataset_forge.menus.augmentation_menu", "augmentation_menu"),
        ),
        "5": (
            "📋 Metadata",
            lazy_action("dataset_forge.menus.metadata_menu", "metadata_menu"),
        ),
        "6": (
            "✏️  Find & extract sketches/drawings/line art",
            extract_sketches_menu,
        ),
        "0": ("⬅️  Back to Main Menu", None),
    }
    while True:
        choice = show_menu(
            "✨ Image Processing & Augmentation",
            options,
            header_color=Mocha.sapphire,
            char="=",
        )
        if choice is None or choice == "0":
            return
        action = options[choice][1]
        if callable(action):
            action()
