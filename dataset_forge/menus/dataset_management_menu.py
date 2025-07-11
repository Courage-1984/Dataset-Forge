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
from dataset_forge.utils.input_utils import get_folder_path, get_path_with_history
from dataset_forge.menus.visual_dedup_menu import visual_dedup_menu
from dataset_forge.menus.imagededup_menu import imagededup_menu
from dataset_forge.menus.correct_hq_lq_pairing_menu import (
    correct_hq_lq_pairing_menu,
    fuzzy_hq_lq_pairing_menu,
)


def dataset_creation_menu():
    """Sub-menu for dataset creation and modification."""
    from dataset_forge.actions import dataset_actions

    options = {
        "1": ("Create Multiscale Dataset", dataset_actions.create_multiscale_dataset),
        "2": ("Extract Frames from Video", dataset_actions.extract_frames_from_video),
        "3": ("Image Tiling", dataset_actions.image_tiling),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Dataset Creation & Modification",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def combine_split_menu():
    """Sub-menu for combining or splitting datasets."""
    from dataset_forge.actions import dataset_actions

    def split_adjust_dataset_menu():
        hq_folder = get_folder_path("Enter HQ folder path (or single folder): ")
        lq_folder = get_folder_path(
            "Enter LQ folder path (leave blank for single-folder): ",
            allow_blank=True,
            allow_hq_lq_options=False,
        )
        dataset_actions.split_adjust_dataset(hq_folder, lq_folder)

    options = {
        "1": ("Combine Multiple Datasets", dataset_actions.combine_datasets),
        "2": ("Split and Adjust Dataset", split_adjust_dataset_menu),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Combine or Split Datasets",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def hq_lq_pairs_menu():
    """Sub-menu for managing HQ/LQ pairs."""
    from dataset_forge.actions import dataset_actions

    def extract_random_pairs():
        hq = get_folder_path("Enter HQ folder path: ")
        lq = get_folder_path(
            "Enter LQ folder path: ", allow_blank=True, allow_hq_lq_options=False
        )
        dataset_actions.extract_random_pairs(hq, lq)

    def shuffle_image_pairs():
        hq = get_folder_path("Enter HQ folder path: ")
        lq = get_folder_path(
            "Enter LQ folder path: ", allow_blank=True, allow_hq_lq_options=False
        )
        dataset_actions.shuffle_image_pairs(hq, lq)

    options = {
        "1": ("Create/Correct Manual Pairings", correct_hq_lq_pairing_menu),
        "2": ("Find Pairs with Fuzzy Matching (Automatic)", fuzzy_hq_lq_pairing_menu),
        "3": ("Extract Random Pairs", extract_random_pairs),
        "4": ("Shuffle Image Pairs", shuffle_image_pairs),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Manage HQ/LQ Pairs",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def clean_organize_menu():
    """Sub-menu for cleaning and organizing datasets."""
    from dataset_forge.actions import dataset_actions

    def dedupe_menu():
        print("\n=== De-Duplicate Images ===")
        hq_folder = get_folder_path(
            "Enter HQ folder path (or single folder for single deduplication): "
        )
        lq_folder = get_folder_path(
            "Enter LQ folder path (leave blank for single-folder deduplication): ",
            allow_blank=True,
            allow_hq_lq_options=False,
        )
        hash_type = (
            input("Hash type [phash/ahash/dhash/whash] (default: phash): ")
            .strip()
            .lower()
            or "phash"
        )
        mode = input("Mode [exact/near] (default: exact): ").strip().lower() or "exact"
        max_dist = 5
        if mode == "near":
            try:
                max_dist = int(
                    input(
                        "Max Hamming distance for near-duplicates (default: 5): "
                    ).strip()
                    or "5"
                )
            except ValueError:
                print_error("Invalid max distance, using default 5.")
                max_dist = 5
        op = (
            input("Operation [move/copy/delete] (default: move): ").strip().lower()
            or "move"
        )
        dest_dir = None
        if op in ("move", "copy"):
            dest_hq = get_folder_path(
                "Destination directory for HQ (leave blank for no move/copy): "
            )
            dest_lq = (
                get_folder_path(
                    "Destination directory for LQ (leave blank for no move/copy): "
                )
                if lq_folder
                else None
            )
            dest_dir = {"hq": dest_hq} if dest_hq else None
            if lq_folder and dest_lq:
                if dest_dir is None:
                    dest_dir = {}
                dest_dir["lq"] = dest_lq
        try:
            dataset_actions.de_dupe(
                hq_folder,
                lq_folder if lq_folder else None,
                hash_type=hash_type,
                mode=mode,
                max_dist=max_dist,
                op=op,
                dest_dir=dest_dir,
            )
            print_success("De-duplication complete.")
        except Exception as e:
            print_error(f"Error during de-duplication: {e}")

    def remove_small_pairs():
        hq = get_folder_path("Enter HQ folder path: ")
        lq = get_folder_path(
            "Enter LQ folder path: ", allow_blank=True, allow_hq_lq_options=False
        )
        dataset_actions.remove_small_image_pairs(hq, lq)

    def organize_by_orientation():
        print_header(
            "Images Orientation Organization (Extract by Landscape/Portrait/Square)"
        )
        input_folder = get_folder_path("Enter the path to the input folder: ")
        output_folder = get_folder_path("Enter the path to the output folder: ")
        orientations = input(
            "Enter orientations to extract (comma-separated: landscape,portrait,square): "
        ).strip()
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

    options = {
        "1": (
            "Visual De-duplication (Duplicates & Near-Duplicates)",
            visual_dedup_menu,
        ),
        "2": ("De-Duplicate (File Hash)", dedupe_menu),
        "3": ("ImageDedup - Advanced Duplicate Detection", imagededup_menu),
        "4": ("Batch Rename", batch_rename_menu),
        "5": ("Remove Image Pairs by Size", remove_small_pairs),
        "6": (
            "Organize by Orientation (Landscape/Portrait/Square)",
            organize_by_orientation,
        ),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Clean & Organize",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def dataset_management_menu():
    """Main dataset management menu with hierarchical structure."""
    options = {
        "1": ("Create Dataset from Source", dataset_creation_menu),
        "2": ("Combine or Split Datasets", combine_split_menu),
        "3": ("Manage HQ/LQ Pairs", hq_lq_pairs_menu),
        "4": ("Clean & Organize", clean_organize_menu),
        "0": ("Back to Main Menu", None),
    }

    while True:
        action = show_menu(
            "Dataset Management",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action()
