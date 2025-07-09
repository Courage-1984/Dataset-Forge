from dataset_forge.actions.hue_adjustment_actions import process_folder
from dataset_forge.utils.input_utils import get_folder_path
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
)


def hue_adjustment_menu():
    print_header("Hue/Brightness/Contrast Adjustment")
    input_folder = get_folder_path("Enter the path to the input folder: ")
    output_folder = get_folder_path("Enter the path to the output folder: ")
    try:
        brightness = input(
            "Brightness (e.g., 1.0 for no change, blank to skip): "
        ).strip()
        brightness = float(brightness) if brightness else None
        contrast = input("Contrast (e.g., 1.0 for no change, blank to skip): ").strip()
        contrast = float(contrast) if contrast else None
        hue = input("Hue shift (integer degrees, blank to skip): ").strip()
        hue = int(hue) if hue else None
        duplicates = input("Number of duplicates per image [1]: ").strip()
        duplicates = int(duplicates) if duplicates else 1
        real_name = input("Use real file names? (y/N): ").strip().lower() == "y"
    except ValueError:
        print_error("Invalid value entered. Please enter numbers where required.")
        return
    try:
        process_folder(
            input_folder=input_folder,
            output_folder=output_folder,
            brightness=brightness,
            contrast=contrast,
            hue=hue,
            duplicates=duplicates,
            real_name=real_name,
        )
        print_success("Hue/Brightness/Contrast adjustment completed.")
    except Exception as e:
        print_error(f"Error during adjustment: {e}")


# Register a static menu for favorites
hue_adjustment_menu.__menu_options__ = {
    "1": ("Run Hue/Brightness/Contrast Adjustment", hue_adjustment_menu),
    "0": ("Back to Main Menu", None),
}
