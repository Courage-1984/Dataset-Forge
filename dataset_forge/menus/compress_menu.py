# compress_menu.py - CLI entry for image compression
from dataset_forge.actions.compress_actions import compress_images
from dataset_forge.utils.input_utils import (
    get_folder_path,
    get_file_operation_choice,
    get_destination_path,
)
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
)
from dataset_forge.utils.color import Mocha


def compress_menu():
    print_header("Compress Images", color=Mocha.lavender)
    print_info("Choose input mode:")
    mode_options = {
        "1": ("HQ/LQ paired folders", "paired"),
        "2": ("Single folder", "single"),
        "0": ("Cancel", None),
    }
    mode = show_menu("Select Input Mode", mode_options, header_color=Mocha.sapphire)
    if mode is None:
        print_info("Cancelled.")
        return
    if mode == "paired":
        hq_path = get_folder_path("Enter HQ folder path: ")
        lq_path = get_folder_path("Enter LQ folder path: ")
        single_folder = None
    else:
        single_folder = get_folder_path("Enter folder path: ")
        hq_path = lq_path = None

    print_info("\nChoose output format:")
    fmt_options = {
        "1": ("PNG (lossless, supports Oxipng)", "png"),
        "2": ("JPEG (lossy)", "jpeg"),
        "3": ("WebP (modern, lossy/lossless)", "webp"),
        "0": ("Cancel", None),
    }
    fmt = show_menu("Select Output Format", fmt_options, header_color=Mocha.sapphire)
    if fmt is None:
        print_info("Cancelled.")
        return

    quality = 85
    if fmt in ["jpeg", "webp"]:
        try:
            quality = int(input("Enter quality (1-100, default 85): ").strip() or "85")
            if not (1 <= quality <= 100):
                print_warning("Invalid quality, using default 85.")
                quality = 85
        except Exception:
            print_warning("Invalid input, using default 85.")
            quality = 85

    use_oxipng = False
    oxipng_level = 4
    oxipng_strip = None
    oxipng_alpha = False
    if fmt == "png":
        oxipng = (
            input("Use Oxipng for PNG optimization? (y/n, default y): ").strip().lower()
        )
        use_oxipng = oxipng != "n"
        if use_oxipng:
            try:
                oxipng_level = (
                    input("Oxipng level (0-6 or 'max', default 4): ").strip() or "4"
                )
                if oxipng_level != "max":
                    oxipng_level = int(oxipng_level)
                    if not (0 <= oxipng_level <= 6):
                        print_warning("Invalid level, using 4.")
                        oxipng_level = 4
            except Exception:
                print_warning("Invalid input, using 4.")
                oxipng_level = 4
            oxipng_strip = (
                input(
                    "Oxipng strip metadata? (none/safe/all or comma-list, default safe): "
                )
                .strip()
                .lower()
                or "safe"
            )
            if oxipng_strip == "none":
                oxipng_strip = None
            oxipng_alpha = (
                input(
                    "Use Oxipng --alpha for transparent pixel optimization? (y/n, default y): "
                )
                .strip()
                .lower()
            )
            oxipng_alpha = oxipng_alpha != "n"

    action = get_file_operation_choice()
    dest_dir = None
    if action in ["copy", "move"]:
        dest_dir = get_destination_path()

    print_info("\nStarting compression...")
    compress_images(
        src_hq=hq_path,
        src_lq=lq_path,
        single_folder=single_folder,
        output_format=fmt,
        quality=quality,
        oxipng_level=oxipng_level,
        action=action,
        dest_dir=dest_dir,
        use_oxipng=use_oxipng,
        oxipng_strip=oxipng_strip,
        oxipng_alpha=oxipng_alpha,
    )
    print_success("Compression complete!")
