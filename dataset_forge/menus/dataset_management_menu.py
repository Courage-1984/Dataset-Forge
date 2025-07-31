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
from dataset_forge.utils.input_utils import get_folder_path, get_path_with_history
from dataset_forge.utils import monitoring
from dataset_forge.utils.menu import lazy_menu
from dataset_forge.menus.correct_hq_lq_pairing_menu import (
    correct_hq_lq_pairing_menu,
    fuzzy_hq_lq_pairing_menu,
)


def lazy_action(module_path, func_name):
    def _action(*args, **kwargs):
        return monitoring.time_and_record_menu_load(
            func_name,
            lambda: getattr(importlib.import_module(module_path), func_name)(
                *args, **kwargs
            ),
        )

    return _action


def dataset_creation_menu():
    """Sub-menu for dataset creation and modification."""
    from dataset_forge.actions import dataset_actions
    from dataset_forge.utils.menu import lazy_action

    options = {
        "1": (
            "📐 Create Multiscale Dataset",
            dataset_actions.create_multiscale_dataset,
        ),
        "2": (
            "🎬 Video Frame Extraction (PepeDP)",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "video_frame_extraction_action",
            ),
        ),
        "3": (
            "🧩 Best Tile Extraction (PepeDP)",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "best_tile_extraction_action",
            ),
        ),
        "0": ("⬅️  Back", None),
    }

    while True:
        key = show_menu(
            "🎯 Create Dataset from Source",
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
            print(f"DEBUG: Calling action for menu selection: {action}")
            try:
                action()
            except Exception as e:
                print_error(f"Exception in menu action: {e}")
                input("Press Enter to return to the menu...")
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


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

    while True:
        action = show_menu(
            "🔗 Combine or Split Datasets",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None or action == "0":
            break
        if callable(action):
            action()


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

    while True:
        action = show_menu(
            "🔗 Manage HQ/LQ Pairs",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None or action == "0":
            break
        if callable(action):
            action()


def clean_organize_menu():
    """Sub-menu for cleaning and organizing datasets."""
    from dataset_forge.actions import dataset_actions

    def dedupe_menu():
        print_header("🧹 De-Duplicate Images", color=Mocha.peach)
        hq_folder = get_folder_path(
            "📁 Enter HQ folder path (or single folder for single deduplication): "
        )
        lq_folder = get_folder_path(
            "📁 Enter LQ folder path (leave blank for single-folder deduplication): ",
            allow_blank=True,
            allow_hq_lq_options=False,
        )
        hash_type = (
            input("🔐 Hash type [phash/ahash/dhash/whash] (default: phash): ")
            .strip()
            .lower()
            or "phash"
        )
        mode = (
            input("🎯 Mode [exact/near] (default: exact): ").strip().lower() or "exact"
        )
        max_dist = 5
        if mode == "near":
            try:
                max_dist = int(
                    input(
                        "📏 Max Hamming distance for near-duplicates (default: 5): "
                    ).strip()
                    or "5"
                )
            except ValueError:
                print_error("❌ Invalid max distance, using default 5.")
                max_dist = 5
        op = (
            input("⚡ Operation [move/copy/delete] (default: move): ").strip().lower()
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
            dataset_actions.dedupe(
                hq_folder=hq_folder,
                lq_folder=lq_folder,
                hash_type=hash_type,
                mode=mode,
                max_dist=max_dist,
                op=op,
                dest_dir=dest_dir,
            )
            print_success("✅ De-duplication complete.")
        except Exception as e:
            print_error(f"❌ Error: {e}")

    def remove_small_pairs():
        hq = get_folder_path("📁 Enter HQ folder path: ")
        lq = get_folder_path(
            "📁 Enter LQ folder path: ", allow_blank=True, allow_hq_lq_options=False
        )
        dataset_actions.remove_small_image_pairs(hq, lq)

    def organize_by_orientation():
        print_header(
            "🔄 Images Orientation Organization (Extract by Landscape/Portrait/Square)",
            color=Mocha.teal,
        )
        input_folder = get_folder_path("📁 Enter the path to the input folder: ")
        output_folder = get_folder_path("📁 Enter the path to the output folder: ")
        orientations = input(
            "📐 Enter orientations to extract (comma-separated: landscape,portrait,square): "
        ).strip()
        orientation_list = [o.strip() for o in orientations.split(",") if o.strip()]
        operation = input("⚡ Operation (copy/move) [copy]: ").strip().lower() or "copy"
        try:
            dataset_actions.images_orientation_organization(
                input_folder=input_folder,
                output_folder=output_folder,
                orientations=orientation_list,
                operation=operation,
            )
            print_success("✅ Images organized by orientation.")
        except Exception as e:
            print_error(f"❌ Error: {e}")

    def batch_rename_menu():
        print_header("✏️ Batch Rename Images", color=Mocha.mauve)
        input_folder = get_folder_path("📁 Enter the path to the input folder: ")
        prefix = input("🏷️ Enter prefix for new filenames: ").strip()
        start_number = input("🔢 Enter starting number (default: 1): ").strip() or "1"
        try:
            start_number = int(start_number)
        except ValueError:
            print_error("❌ Invalid starting number, using 1.")
            start_number = 1
        extension = input("📄 Enter file extension (default: jpg): ").strip() or "jpg"
        try:
            dataset_actions.batch_rename(
                input_folder=input_folder,
                prefix=prefix,
                start_number=start_number,
                extension=extension,
            )
            print_success("✅ Batch rename complete.")
        except Exception as e:
            print_error(f"❌ Error: {e}")

    options = {
        "1": (
            "👁️  Visual De-duplication (Duplicates & Near-Duplicates)",
            lazy_menu("dataset_forge.menus.visual_dedup_menu", "visual_dedup_menu"),
        ),
        "2": ("🔐 De-Duplicate (File Hash)", dedupe_menu),
        "3": (
            "🔍 ImageDedup - Advanced Duplicate Detection",
            lazy_menu("dataset_forge.menus.imagededup_menu", "imagededup_menu"),
        ),
        "4": (
            "🧠 CBIR (Semantic Duplicate Detection)",
            lazy_menu("dataset_forge.menus.cbir_menu", "cbir_menu"),
        ),
        "5": ("✏️  Batch Rename", batch_rename_menu),
        "6": ("📏 Remove Image Pairs by Size", remove_small_pairs),
        "7": (
            "🔄 Organize by Orientation (Landscape/Portrait/Square)",
            organize_by_orientation,
        ),
        "0": ("⬅️  Back", None),
    }
    while True:
        choice = show_menu(
            "🧹 Clean & Organize",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if choice is None or choice == "0":
            break
        action = options[choice][1]
        if callable(action):
            action()


def dataset_management_menu():
    """Main dataset management menu with hierarchical structure."""
    # Define menu context for help system
    menu_context = {
        "Total Options": "7 main categories",
        "Purpose": "Dataset creation, organization, and management",
        "Navigation": "Use numbers 1-7 to select, 0 to go back",
    }

    options = {
        "1": (
            "🎯 Create Dataset from Source",
            lazy_action(__name__, "dataset_creation_menu"),
        ),
        "2": (
            "🔗 Combine or Split Datasets",
            lazy_action(__name__, "combine_split_menu"),
        ),
        "3": ("🔗 Manage HQ/LQ Pairs", lazy_action(__name__, "hq_lq_pairs_menu")),
        "4": ("🧹 Clean & Organize", lazy_action(__name__, "clean_organize_menu")),
        "5": (
            "🧭 Align Images (Batch Projective Alignment)",
            lazy_action(
                "dataset_forge.actions.align_images_actions", "align_images_workflow"
            ),
        ),
        "6": (
            "🩺 Dataset Health Scoring",
            lazy_action(
                "dataset_forge.menus.dataset_health_scoring_menu",
                "dataset_health_scoring_menu",
            ),
        ),
        "7": (
            "🐸 Umzi's Dataset Preprocessing (PepeDP)",
            lazy_action(
                "dataset_forge.menus.umzi_dataset_preprocessing_menu",
                "umzi_dataset_preprocessing_menu",
            ),
        ),
        "0": ("⬅️  Back to Main Menu", None),
    }
    while True:
        choice = show_menu(
            "📂 Dataset Management",
            options,
            header_color=Mocha.lavender,
            char="=",
            current_menu="Dataset Management",
            menu_context=menu_context,
        )
        if choice is None or choice == "0":
            return
        action = options[choice][1]
        if callable(action):
            action()
