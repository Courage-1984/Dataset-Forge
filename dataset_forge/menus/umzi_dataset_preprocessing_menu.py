import importlib
from dataset_forge.utils.menu import show_menu, lazy_action
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import print_header


def umzi_dataset_preprocessing_menu():
    options = {
        "1": (
            "🧩 Best Tile Extraction (Tiles)",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "best_tile_extraction_action",
            ),
        ),
        "2": (
            "🎬 Video Frame Extraction (Embedding Deduplication)",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "video_frame_extraction_action",
            ),
        ),
        "3": (
            "🧹 Duplicate Image Detection & Removal",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "duplicate_image_detection_action",
            ),
        ),
        "4": (
            "🧪 Threshold-Based Image Filtering (IQA)",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "iqa_filtering_action",
            ),
        ),
        "0": ("⬅️  Back to Main Menu", None),
    }
    # Define menu context for help system
    menu_context = {
        "Purpose": "Advanced dataset preprocessing tools from PepeDP",
        "Total Options": "4 preprocessing operations",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": "Tile extraction, video frame extraction, duplicate detection, IQA filtering",
    }

    while True:
        key = show_menu(
            "🐸 Umzi's Dataset Preprocessing (PepeDP)",
            options,
            header_color=Mocha.lavender,
            char="-",
            current_menu="Umzi's Dataset Preprocessing",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options[key][1]
        if callable(action):
            action()
