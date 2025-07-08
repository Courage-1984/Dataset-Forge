from dataset_forge.utils.printing import (
    print_section,
    print_info,
    print_success,
    print_prompt,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.input_utils import get_folder_path


def settings_menu_action(hq_folder, lq_folder):
    """Business logic for settings menu: set and display HQ/LQ folders."""
    print_section("Settings", char="-", color=Mocha.sky)
    print_info(f"Current HQ Folder: {hq_folder or 'Not Set'}")
    print_info(f"Current LQ Folder: {lq_folder or 'Not Set'}")
    print("\n[1] Set HQ/LQ Folders")
    print("[0] Back to Main Menu")
    choice = input("Choice: ").strip()
    if choice == "1":
        hq_folder = get_folder_path("Enter the path to the HQ folder: ")
        lq_folder = get_folder_path("Enter the path to the LQ folder: ")
        print_success("Folders updated.")
    return hq_folder, lq_folder
