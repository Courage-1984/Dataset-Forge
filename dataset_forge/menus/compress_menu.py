# compress_menu.py - CLI entry for image compression
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
    from dataset_forge.actions.compress_actions import compress_images

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
    if fmt == "png":
        use_oxipng = (
            input("Use Oxipng for additional compression? (y/N): ").strip().lower()
            == "y"
        )

    operation = get_file_operation_choice()
    if operation is None:
        print_info("Cancelled.")
        return

    dest_path = None
    if operation in ["copy", "move"]:
        dest_path = get_destination_path("Enter destination folder: ")
        if dest_path is None:
            print_info("Cancelled.")
            return

    print_info("\nStarting compression...")
    try:
        compress_images(
            hq_path=hq_path,
            lq_path=lq_path,
            single_folder=single_folder,
            output_format=fmt,
            quality=quality,
            use_oxipng=use_oxipng,
            operation=operation,
            dest_path=dest_path,
        )
        print_success("Compression completed successfully!")
    except Exception as e:
        print_error(f"Compression failed: {e}")
