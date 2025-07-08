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
from dataset_forge.actions import dataset_actions

# Assume hq_folder, lq_folder are available in the global scope for now


def dataset_menu():
    options = {
        "1": ("Create Multiscale Dataset", dataset_actions.create_multiscale_dataset),
        "2": ("Image Tiling", dataset_actions.image_tiling),
        "3": ("Combine Datasets", dataset_actions.combine_datasets),
        "4": (
            "Extract Random Pairs",
            lambda: dataset_actions.extract_random_pairs(hq_folder, lq_folder),
        ),
        "5": (
            "Shuffle Image Pairs",
            lambda: dataset_actions.shuffle_image_pairs(hq_folder, lq_folder),
        ),
        "6": (
            "Split and Adjust Dataset",
            lambda: dataset_actions.split_adjust_dataset(hq_folder, lq_folder),
        ),
        "7": (
            "Remove Small Image Pairs",
            lambda: dataset_actions.remove_small_image_pairs(hq_folder, lq_folder),
        ),
        "8": ("De-Duplicate", lambda: dataset_actions.de_dupe(hq_folder, lq_folder)),
        "9": ("Batch Rename", lambda: dataset_actions.batch_rename(hq_folder)),
        "10": ("Extract Frames from Video", dataset_actions.extract_frames_from_video),
        "11": (
            "Images Orientation Organization (Extract by Landscape/Portrait/Square)",
            images_orientation_organization_menu,
        ),
        "0": ("Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "Dataset Creation & Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def images_orientation_organization_menu():
    print_header("Images Orientation Organization (Extract by Landscape/Portrait/Square)")
    input_folder = input("Enter the path to the input folder: ").strip()
    output_folder = input("Enter the path to the output folder: ").strip()
    orientations = input("Enter orientations to extract (comma-separated: landscape,portrait,square): ").strip()
    orientation_list = [o.strip() for o in orientations.split(",") if o.strip()]
    operation = input("Operation (copy/move) [copy]: ").strip().lower() or "copy"
    try:
        dataset_actions.images_orientation_organization(
            input_folder=input_folder,
            output_folder=output_folder,
            orientations=orientation_list,
            operation=operation,
        )
        print_success("Images organized by orientation.")
    except Exception as e:
        print_error(f"Error: {e}")
