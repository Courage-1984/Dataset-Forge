import importlib
from dataset_forge.utils.menu import show_menu, lazy_action
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import print_header


def umzi_dataset_preprocessing_menu():
    print_header("Umzi's Dataset_Preprocessing", color=Mocha.lavender)
    options = {
        "1": (
            "🟪 Best Tile Extraction",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "best_tile_extraction_action",
            ),
        ),
        "2": (
            "🟦 Video Frame Extraction",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "video_frame_extraction_action",
            ),
        ),
        "3": (
            "🟩 Image Deduplication (create embeddings)",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "image_deduplication_create_embeddings_action",
            ),
        ),
        "4": (
            "🟧 Image Deduplication (find duplicates)",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "image_deduplication_find_duplicates_action",
            ),
        ),
        "5": (
            "🟫 IQA Filtering",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "iqa_filtering_action",
            ),
        ),
        "6": (
            "🟨 Embedding Extraction (single image)",
            lazy_action(
                "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                "embedding_extraction_action",
            ),
        ),
        "0": ("⬅️  Back to Main Menu", None),
    }
    while True:
        key = show_menu(
            "Umzi's Dataset_Preprocessing Menu",
            options,
            header_color=Mocha.lavender,
            char="-",
        )
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        if callable(action):
            action()
