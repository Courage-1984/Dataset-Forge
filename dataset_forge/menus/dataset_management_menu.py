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
from dataset_forge.utils.input_utils import (
    get_folder_path,
    get_path_with_history,
    ask_yes_no,
)
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
            "⚡ Advanced Preprocessing",
            lazy_menu(
                "dataset_forge.menus.umzi_dataset_preprocessing_menu",
                "umzi_dataset_preprocessing_menu",
            ),
        ),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Create datasets from various sources - build your image dataset from existing files, videos, or images",
        "Total Options": "4 creation methods",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": [
            "📁 Create from Source Folder - Extract images from an existing folder structure",
            "🎬 Create from Video - Extract frames from video files to create image datasets",
            "🖼️ Create from Images - Build dataset from individual image files",
            "⚡ Advanced Creation - Specialized creation methods for specific use cases",
        ],
        "Tips": [
            "📁 Source Folder: Best for existing image collections with organized structure",
            "🎬 Video Extraction: Great for creating datasets from video content (movies, recordings)",
            "🖼️ Individual Images: Use when you have scattered image files to organize",
            "⚡ Advanced: Provides specialized tools for specific ML and research tasks",
        ],
        "Usage Examples": [
            "📁 From folder: Select source folder → Choose output location → Set options → Process",
            "🎬 From video: Select video file → Set frame rate → Choose output folder → Extract frames",
            "🖼️ From images: Select image files → Choose organization method → Create dataset",
            "⚡ Advanced: Choose specialized method → Configure parameters → Execute creation",
        ],
        "Performance Notes": [
            "💾 Large folders: Use chunked processing to avoid memory issues",
            "🎬 Video processing: Frame extraction can be time-consuming for long videos",
            "🖼️ Image organization: Ensure consistent naming for better dataset structure",
            "⚡ Advanced methods: May require specific dependencies or configurations",
        ],
    }

    while True:
        try:
            key = show_menu(
                "📁 Dataset Creation",
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
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Combine multiple datasets or split existing datasets into subsets",
        "Options": "2 operations available",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
        "Key Features": [
            "🔗 Combine Multiple Datasets - Merge multiple datasets into one",
            "✂️ Split and Adjust Dataset - Divide dataset into training/validation sets",
        ],
        "Tips": [
            "Combine datasets when you have multiple sources to merge",
            "Split datasets to create training and validation sets",
            "Use split operations for machine learning workflows",
            "Combined datasets maintain original file organization",
        ],
    }

    while True:
        try:
            key = show_menu(
                "🔄 Dataset Operations",
                options,
                header_color=Mocha.sapphire,
                char="-",
                current_menu="Dataset Operations",
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
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage high-quality and low-quality image pairs for super-resolution training",
        "Options": "4 pair management operations",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": [
            "🔗 Create/Correct Manual Pairings - Manually create or fix HQ/LQ pairings",
            "🔍 Find Pairs with Fuzzy Matching - Automatically find matching pairs",
            "🎲 Extract Random Pairs - Select random subset of pairs",
            "🔄 Shuffle Image Pairs - Randomize pair order for training",
        ],
        "Tips": [
            "Manual pairings are best for small, curated datasets",
            "Fuzzy matching works well for large datasets with similar naming",
            "Extract random pairs to create smaller training sets",
            "Shuffle pairs to improve training randomization",
            "HQ/LQ pairs are essential for super-resolution model training",
        ],
    }

    while True:
        try:
            key = show_menu(
                "🔗 HQ/LQ Management",
                options,
                header_color=Mocha.sapphire,
                char="-",
                current_menu="HQ/LQ Management",
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
    from dataset_forge.actions import imagededup_actions

    def find_duplicates_wrapper():
        """Wrapper function to prompt for image directory and call find_duplicates."""
        image_dir = get_folder_path("📁 Enter image directory path: ")
        if image_dir:
            imagededup_actions.find_duplicates(image_dir)

    def remove_duplicates_wrapper():
        """Wrapper function to prompt for image directory and call remove_duplicates."""
        image_dir = get_folder_path("📁 Enter image directory path: ")
        if image_dir:
            dry_run = ask_yes_no(
                "Run in dry-run mode (show what would be done without actually doing it)?",
                default=True,
            )
            imagededup_actions.remove_duplicates(image_dir, dry_run=dry_run)

    def move_duplicates_wrapper():
        """Wrapper function to prompt for image directory and destination, then call move_duplicates."""
        image_dir = get_folder_path("📁 Enter image directory path: ")
        if image_dir:
            destination_dir = get_folder_path("📁 Enter destination directory path: ")
            if destination_dir:
                dry_run = ask_yes_no(
                    "Run in dry-run mode (show what would be done without actually doing it)?",
                    default=True,
                )
                imagededup_actions.move_duplicates(
                    image_dir, destination_dir, dry_run=dry_run
                )

    def dedupe_menu():
        options = {
            "1": ("🔍 Find Duplicates", find_duplicates_wrapper),
            "2": ("🗑️ Remove Duplicates", remove_duplicates_wrapper),
            "3": ("📁 Move Duplicates", move_duplicates_wrapper),
            "0": ("⬅️ Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Find and manage duplicate images in datasets",
            "Options": "3 duplicate operations",
            "Navigation": "Use numbers 1-3 to select, 0 to go back",
            "Key Features": [
                "🔍 Find Duplicates - Identify duplicate images without removing them",
                "🗑️ Remove Duplicates - Permanently delete duplicate images",
                "📁 Move Duplicates - Move duplicates to separate folder",
            ],
            "Tips": [
                "Always use Find Duplicates first to preview what will be affected",
                "Use dry-run mode to see what would be done without making changes",
                "Move Duplicates is safer than Remove Duplicates",
                "Duplicate detection uses advanced image similarity algorithms",
            ],
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
        dataset_actions.organize_hq_lq_by_orientation(hq_folder, lq_folder)

    def batch_rename_menu():
        options = {
            "1": ("📁 Single Folder", dataset_actions.batch_rename_single_folder),
            "2": ("🔗 HQ/LQ Folders", dataset_actions.batch_rename_hq_lq_folders),
            "0": ("⬅️ Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Batch rename files in datasets",
            "Options": "2 rename operations",
            "Navigation": "Use numbers 1-2 to select, 0 to go back",
            "Key Features": [
                "📁 Single Folder - Rename files in a single folder",
                "🔗 HQ/LQ Folders - Rename files in paired HQ/LQ folders",
            ],
            "Tips": [
                "Single folder renaming works for any image collection",
                "HQ/LQ folder renaming maintains pair relationships",
                "Renaming helps organize datasets for training",
                "Use consistent naming patterns for better organization",
            ],
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
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Clean and organize dataset files for better quality and organization",
        "Options": "4 cleaning operations available",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": [
            "🔍 Duplicate Management - Find and remove duplicate images",
            "📏 Remove Small Pairs - Remove pairs with small image dimensions",
            "📐 Organize by Orientation - Sort images by portrait/landscape",
            "📝 Batch Rename - Rename files with consistent patterns",
        ],
        "Tips": [
            "Start with Duplicate Management to clean your dataset",
            "Remove small pairs to ensure consistent image sizes",
            "Organize by orientation for specific training requirements",
            "Batch rename helps maintain consistent file naming",
            "Always backup your data before cleaning operations",
        ],
    }

    while True:
        try:
            key = show_menu(
                "🧹 Dataset Cleanup",
                options,
                header_color=Mocha.sapphire,
                char="-",
                current_menu="Dataset Cleanup",
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
        "1": ("📁 Dataset Creation", dataset_creation_menu),
        "2": ("🔄 Dataset Operations", combine_split_menu),
        "3": ("🔗 HQ/LQ Management", hq_lq_pairs_menu),
        "4": ("🧹 Dataset Cleanup", clean_organize_menu),
        "5": (
            "🎯 Image Alignment",
            lazy_action(
                "dataset_forge.actions.align_images_actions", "align_images_workflow"
            ),
        ),
        "6": (
            "📊 Dataset Analysis",
            lazy_menu(
                "dataset_forge.menus.dataset_health_scoring_menu",
                "dataset_health_scoring_menu",
            ),
        ),
        "7": (
            "⚡ Advanced Preprocessing",
            lazy_menu(
                "dataset_forge.menus.umzi_dataset_preprocessing_menu",
                "umzi_dataset_preprocessing_menu",
            ),
        ),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Comprehensive dataset creation, organization, and management tools - build and maintain your image datasets",
        "Total Options": "7 main categories",
        "Navigation": "Use numbers 1-7 to select, 0 to go back",
        "Key Features": [
            "📁 Dataset Creation - Build datasets from various sources (folders, videos, images)",
            "🔄 Dataset Operations - Combine multiple datasets or split existing ones into subsets",
            "🔗 HQ/LQ Management - Handle high-quality and low-quality image pairs for super-resolution",
            "🧹 Dataset Cleanup - Remove duplicates, organize files, and maintain dataset hygiene",
            "🎯 Image Alignment - Batch projective alignment for image pairs and sequences",
            "📊 Dataset Analysis - Assess dataset quality, health, and characteristics",
            "⚡ Advanced Preprocessing - Umzi's specialized preprocessing tools for ML workflows",
        ],
        "Tips": [
            "🎯 Start with Dataset Creation to build your first dataset from existing images",
            "🔄 Use Dataset Operations to merge multiple datasets or create training/validation splits",
            "🔗 HQ/LQ Management is essential for super-resolution and image restoration tasks",
            "🧹 Always run Dataset Cleanup to remove duplicates and organize your data",
            "🎯 Image Alignment helps ensure consistent positioning across image pairs",
            "📊 Use Dataset Analysis to identify quality issues before training models",
            "⚡ Advanced Preprocessing provides specialized tools for specific ML tasks",
        ],
        "Usage Examples": [
            "📁 New dataset: 1 → Create from folder → Select source → Choose output location",
            "🔄 Merge datasets: 2 → Combine datasets → Select folders → Choose merge strategy",
            "🔗 HQ/LQ pairs: 3 → Create pairs → Set HQ folder → Set LQ folder → Validate pairs",
            "🧹 Clean dataset: 4 → Remove duplicates → Choose method → Review results",
            "🎯 Align images: 5 → Select pairs → Choose alignment method → Process batch",
            "📊 Analyze quality: 6 → Run health check → Review metrics → Fix issues",
        ],
        "Performance Notes": [
            "💾 Large datasets: Use chunked processing and monitor disk space",
            "🔄 Batch operations: Process in smaller batches for better error recovery",
            "📊 Analysis: Use sampling for quick previews on datasets >10k images",
            "🔗 HQ/LQ pairs: Ensure consistent naming conventions for automatic pairing",
        ],
    }

    while True:
        try:
            key = show_menu(
                "📂 Dataset Management",
                options,
                header_color=Mocha.sapphire,
                char="-",
                current_menu="Dataset Management",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break
