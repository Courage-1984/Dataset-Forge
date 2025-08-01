import importlib
from dataset_forge.utils.menu import show_menu, lazy_action
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
from dataset_forge.utils import monitoring
from dataset_forge.utils.menu import lazy_menu


# Lazy imports for correct HQ/LQ pairing menus
def correct_hq_lq_pairing_menu():
    """Lazy import wrapper for correct_hq_lq_pairing_menu."""
    from dataset_forge.utils.menu import lazy_menu

    return lazy_menu(
        "dataset_forge.menus.correct_hq_lq_pairing_menu", "correct_hq_lq_pairing_menu"
    )()


def fuzzy_hq_lq_pairing_menu():
    """Lazy import wrapper for fuzzy_hq_lq_pairing_menu."""
    from dataset_forge.utils.menu import lazy_menu

    return lazy_menu(
        "dataset_forge.menus.correct_hq_lq_pairing_menu", "fuzzy_hq_lq_pairing_menu"
    )()


# lazy_action is already imported at the top of the file


def dataset_creation_menu():
    """Sub-menu for creating datasets from various sources."""
    from dataset_forge.actions import dataset_actions

    def create_dataset_from_source():
        source_folder = get_folder_path("📁 Enter source folder path: ")
        output_folder = get_folder_path("📁 Enter output folder path: ")
        dataset_actions.create_dataset_from_source(source_folder, output_folder)

    def create_dataset_from_video():
        video_path = get_folder_path("🎬 Enter video file path: ")
        output_folder = get_folder_path("📁 Enter output folder path: ")
        dataset_actions.create_dataset_from_video(video_path, output_folder)

    def create_dataset_from_images():
        image_folder = get_folder_path("📁 Enter image folder path: ")
        output_folder = get_folder_path("📁 Enter output folder path: ")
        dataset_actions.create_dataset_from_images(image_folder, output_folder)

    options = {
        "1": ("📁 Create from Source Folder", create_dataset_from_source),
        "2": ("🎬 Create from Video", create_dataset_from_video),
        "3": ("🖼️ Create from Images", create_dataset_from_images),
        "4": (
            "🐸 Umzi's Dataset Preprocessing",
            lazy_menu(
                "dataset_forge.menus.umzi_dataset_preprocessing_menu",
                "umzi_dataset_preprocessing_menu",
            ),
        ),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Create new datasets from various sources",
        "Options": "4 creation methods available",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
    }

    while True:
        try:
            key = show_menu(
                "🎯 Create Dataset from Source",
                options,
                header_color=Mocha.sapphire,
                char="-",
                current_menu="Dataset Creation",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break


def combine_split_menu():
    """Sub-menu for combining or splitting datasets."""
    from dataset_forge.actions import dataset_actions

    def split_adjust_dataset_menu():
        hq_folder = get_folder_path("📁 Enter HQ folder path (or single folder): ")
        lq_folder = get_folder_path(
            "📁 Enter LQ folder path (leave blank for single-folder): ",
            allow_blank=True,
            allow_hq_lq_options=False,
        )
        dataset_actions.split_adjust_dataset(hq_folder, lq_folder)

    options = {
        "1": ("🔗 Combine Multiple Datasets", dataset_actions.combine_datasets),
        "2": ("✂️ Split and Adjust Dataset", split_adjust_dataset_menu),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Combine or split existing datasets",
        "Options": "2 operations available",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
    }

    while True:
        try:
            key = show_menu(
                "🔗 Combine or Split Datasets",
                options,
                header_color=Mocha.sapphire,
                char="-",
                current_menu="Combine/Split Datasets",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break


def hq_lq_pairs_menu():
    """Sub-menu for managing HQ/LQ pairs."""
    from dataset_forge.actions import dataset_actions

    def extract_random_pairs():
        hq = get_folder_path("📁 Enter HQ folder path: ")
        lq = get_folder_path(
            "📁 Enter LQ folder path: ", allow_blank=True, allow_hq_lq_options=False
        )
        dataset_actions.extract_random_pairs(hq, lq)

    def shuffle_image_pairs():
        hq = get_folder_path("📁 Enter HQ folder path: ")
        lq = get_folder_path(
            "📁 Enter LQ folder path: ", allow_blank=True, allow_hq_lq_options=False
        )
        dataset_actions.shuffle_image_pairs(hq, lq)

    options = {
        "1": ("🔗 Create/Correct Manual Pairings", correct_hq_lq_pairing_menu),
        "2": (
            "🔍 Find Pairs with Fuzzy Matching (Automatic)",
            fuzzy_hq_lq_pairing_menu,
        ),
        "3": ("🎲 Extract Random Pairs", extract_random_pairs),
        "4": ("🔄 Shuffle Image Pairs", shuffle_image_pairs),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage high-quality and low-quality image pairs",
        "Options": "4 pair management operations",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
    }

    while True:
        try:
            key = show_menu(
                "🔗 Manage HQ/LQ Pairs",
                options,
                header_color=Mocha.sapphire,
                char="-",
                current_menu="HQ/LQ Pair Management",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break


def clean_organize_menu():
    """Sub-menu for cleaning and organizing datasets."""
    from dataset_forge.actions import dataset_actions

    def dedupe_menu():
        options = {
            "1": ("🔍 Find Duplicates", dataset_actions.find_duplicates),
            "2": ("🗑️ Remove Duplicates", dataset_actions.remove_duplicates),
            "3": ("📁 Move Duplicates", dataset_actions.move_duplicates),
            "0": ("⬅️  Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Find and manage duplicate images",
            "Options": "3 duplicate operations",
            "Navigation": "Use numbers 1-3 to select, 0 to go back",
        }

        while True:
            try:
                key = show_menu(
                    "🔍 Duplicate Management",
                    options,
                    header_color=Mocha.sapphire,
                    char="-",
                    current_menu="Duplicate Management",
                    menu_context=menu_context,
                )
                if key is None or key == "0":
                    break
                action = options[key][1]
                if callable(action):
                    action()
            except (KeyboardInterrupt, EOFError):
                print_info("\nExiting...")
                break

    def remove_small_pairs():
        hq_folder = get_folder_path("📁 Enter HQ folder path: ")
        lq_folder = get_folder_path(
            "📁 Enter LQ folder path: ", allow_blank=True, allow_hq_lq_options=False
        )
        dataset_actions.remove_small_pairs(hq_folder, lq_folder)

    def organize_by_orientation():
        hq_folder = get_folder_path("📁 Enter HQ folder path: ")
        lq_folder = get_folder_path(
            "📁 Enter LQ folder path: ", allow_blank=True, allow_hq_lq_options=False
        )
        dataset_actions.organize_images_by_orientation(hq_folder, lq_folder)

    def batch_rename_menu():
        options = {
            "1": ("📁 Single Folder", dataset_actions.batch_rename_single_folder),
            "2": ("🔗 HQ/LQ Folders", dataset_actions.batch_rename_hq_lq_folders),
            "0": ("⬅️  Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Batch rename files in datasets",
            "Options": "2 rename modes available",
            "Navigation": "Use numbers 1-2 to select, 0 to go back",
        }

        while True:
            try:
                key = show_menu(
                    "📝 Batch Rename",
                    options,
                    header_color=Mocha.sapphire,
                    char="-",
                    current_menu="Batch Rename",
                    menu_context=menu_context,
                )
                if key is None or key == "0":
                    break
                action = options[key][1]
                if callable(action):
                    action()
            except (KeyboardInterrupt, EOFError):
                print_info("\nExiting...")
                break

    options = {
        "1": ("🔍 Duplicate Management", dedupe_menu),
        "2": ("📏 Remove Small Pairs", remove_small_pairs),
        "3": ("📐 Organize by Orientation", organize_by_orientation),
        "4": ("📝 Batch Rename", batch_rename_menu),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Clean and organize dataset files",
        "Options": "4 cleaning operations available",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
    }

    while True:
        try:
            key = show_menu(
                "🧹 Clean & Organize",
                options,
                header_color=Mocha.sapphire,
                char="-",
                current_menu="Clean & Organize",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break


def dataset_management_menu():
    """Main dataset management menu."""
    options = {
        "1": ("🎯 Create Dataset from Source", dataset_creation_menu),
        "2": ("🔗 Combine or Split Datasets", combine_split_menu),
        "3": ("🔗 Manage HQ/LQ Pairs", hq_lq_pairs_menu),
        "4": ("🧹 Clean & Organize", clean_organize_menu),
        "5": (
            "🧭 Align Images",
            lazy_action(
                "dataset_forge.actions.align_images_actions", "align_images_workflow"
            ),
        ),
        "6": (
            "🩺 Dataset Health Scoring",
            lazy_menu(
                "dataset_forge.menus.dataset_health_scoring_menu",
                "dataset_health_scoring_menu",
            ),
        ),
        "7": (
            "🐸 Umzi's Dataset Preprocessing",
            lazy_menu(
                "dataset_forge.menus.umzi_dataset_preprocessing_menu",
                "umzi_dataset_preprocessing_menu",
            ),
        ),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Comprehensive dataset creation, organization, and management",
        "Total Options": "7 main categories",
        "Navigation": "Use numbers 1-7 to select, 0 to go back",
        "Key Features": "Dataset creation, pair management, cleaning, alignment, health scoring",
    }

    while True:
        try:
            choice = show_menu(
                "📂 Dataset Management",
                options,
                header_color=Mocha.sapphire,
                char="-",
                current_menu="Dataset Management",
                menu_context=menu_context,
            )
            if choice is None or choice == "0":
                return
            action = options[choice][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break
