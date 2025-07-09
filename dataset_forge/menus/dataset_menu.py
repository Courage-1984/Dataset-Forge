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
from dataset_forge.menus import session_state
from tqdm import tqdm

# Assume hq_folder, lq_folder are available in the global scope for now


def dataset_menu():
    options = {
        "1": ("Create Multiscale Dataset", dataset_actions.create_multiscale_dataset),
        "2": ("Image Tiling", dataset_actions.image_tiling),
        "3": ("Combine Datasets", dataset_actions.combine_datasets),
        "4": (
            "Extract Random Pairs",
            lambda: dataset_actions.extract_random_pairs(
                input("Enter HQ folder path: ").strip(),
                input("Enter LQ folder path: ").strip(),
            ),
        ),
        "5": (
            "Shuffle Image Pairs",
            lambda: dataset_actions.shuffle_image_pairs(
                input("Enter HQ folder path: ").strip(),
                input("Enter LQ folder path: ").strip(),
            ),
        ),
        "6": (
            "Split and Adjust Dataset",
            lambda: (
                (lambda hq, lq: split_adjust_dataset_menu(hq, lq))(
                    input("Enter HQ folder path (or single folder): ").strip(),
                    input(
                        "Enter LQ folder path (leave blank for single-folder): "
                    ).strip(),
                )
            ),
        ),
        "7": (
            "Remove Small Image Pairs",
            lambda: dataset_actions.remove_small_image_pairs(
                input("Enter HQ folder path: ").strip(),
                input("Enter LQ folder path: ").strip(),
            ),
        ),
        "8": ("De-Duplicate", dedupe_menu),
        "9": (
            "Batch Rename",
            lambda: dataset_actions.batch_rename(
                input("Enter folder path to batch rename: ").strip()
            ),
        ),
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
    print_header(
        "Images Orientation Organization (Extract by Landscape/Portrait/Square)"
    )
    input_folder = input("Enter the path to the input folder: ").strip()
    output_folder = input("Enter the path to the output folder: ").strip()
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


def dedupe_menu():
    print("\n=== De-Duplicate Images ===")
    hq_folder = input(
        "Enter HQ folder path (or single folder for single deduplication): "
    ).strip()
    lq_folder = input(
        "Enter LQ folder path (leave blank for single-folder deduplication): "
    ).strip()
    hash_type = (
        input("Hash type [phash/ahash/dhash/whash] (default: phash): ").strip().lower()
        or "phash"
    )
    mode = input("Mode [exact/near] (default: exact): ").strip().lower() or "exact"
    max_dist = 5
    if mode == "near":
        try:
            max_dist = int(
                input("Max Hamming distance for near-duplicates (default: 5): ").strip()
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
        dest_hq = input(
            "Destination directory for HQ (leave blank for no move/copy): "
        ).strip()
        dest_lq = (
            input(
                "Destination directory for LQ (leave blank for no move/copy): "
            ).strip()
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


def split_adjust_dataset_menu(hq_folder, lq_folder):
    # Unified: always call dataset_actions.split_adjust_dataset, which now handles single-folder and paired logic
    dataset_actions.split_adjust_dataset(hq_folder, lq_folder)
