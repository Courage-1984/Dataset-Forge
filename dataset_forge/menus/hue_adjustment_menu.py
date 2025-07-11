from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.input_utils import get_folder_path


def hue_adjustment_menu():
    from dataset_forge.actions.hue_adjustment_actions import process_folder

    print_header("Hue Adjustment Menu", color=Mocha.sapphire)

    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        print_error("No input folder specified.")
        return

    output_folder = get_folder_path("Enter output folder path: ")
    if not output_folder:
        print_error("No output folder specified.")
        return

    try:
        hue_shift = float(
            input("Enter hue shift (-180 to 180, default 0): ").strip() or "0"
        )
        if not (-180 <= hue_shift <= 180):
            print_error("Hue shift must be between -180 and 180.")
            return
    except ValueError:
        print_error("Invalid hue shift value.")
        return

    try:
        brightness = float(
            input("Enter brightness adjustment (-100 to 100, default 0): ").strip()
            or "0"
        )
        if not (-100 <= brightness <= 100):
            print_error("Brightness must be between -100 and 100.")
            return
    except ValueError:
        print_error("Invalid brightness value.")
        return

    try:
        contrast = float(
            input("Enter contrast adjustment (-100 to 100, default 0): ").strip() or "0"
        )
        if not (-100 <= contrast <= 100):
            print_error("Contrast must be between -100 and 100.")
            return
    except ValueError:
        print_error("Invalid contrast value.")
        return

    print_info("Starting hue adjustment...")
    try:
        process_folder(input_folder, output_folder, hue_shift, brightness, contrast)
        print_success("Hue adjustment completed successfully!")
    except Exception as e:
        print_error(f"Hue adjustment failed: {e}")
    input("\nPress Enter to return to the menu...")


# Register a static menu for favorites
hue_adjustment_menu.__menu_options__ = {
    "1": ("Run Hue/Brightness/Contrast Adjustment", hue_adjustment_menu),
    "0": ("Back to Main Menu", None),
}
