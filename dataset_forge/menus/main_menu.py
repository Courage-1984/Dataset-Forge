import importlib
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils import monitoring
from dataset_forge.utils.audio_utils import play_startup_sound

# Helper for lazy importing submenu modules
# This returns a function that, when called, imports and calls the submenu


def lazy_menu(module_name: str, func_name: str):
    def _menu():
        monitoring.time_and_record_menu_load(
            func_name,
            lambda: getattr(importlib.import_module(module_name), func_name)(),
        )

    return _menu


def main_menu():
    # Play startup sound once per session
    play_startup_sound(block=False)
    while True:
        options = {
            "1": (
                "📂 Dataset Management",
                lazy_menu(
                    "dataset_forge.menus.dataset_management_menu",
                    "dataset_management_menu",
                ),
            ),
            "2": (
                "🔍 Analysis & Validation",
                lazy_menu(
                    "dataset_forge.menus.analysis_validation_menu",
                    "analysis_validation_menu",
                ),
            ),
            "3": (
                "✨ Image Processing & Augmentation",
                lazy_menu(
                    "dataset_forge.menus.image_processing_menu", "image_processing_menu"
                ),
            ),
            "4": (
                "🚀 Training & Inference",
                lazy_menu(
                    "dataset_forge.menus.training_inference_menu",
                    "training_inference_menu",
                ),
            ),
            "5": (
                "🛠️  Utilities",
                lazy_menu("dataset_forge.menus.utilities_menu", "utilities_menu"),
            ),
            "6": (
                "⚙️  System & Settings",
                lazy_menu(
                    "dataset_forge.menus.system_settings_menu", "system_settings_menu"
                ),
            ),
            "7": (
                "🔗 Links",
                lazy_menu("dataset_forge.menus.links_menu", "links_menu"),
            ),
            "8": (
                "🩺 System Monitoring & Health",
                lazy_menu(
                    "dataset_forge.menus.system_monitoring_menu",
                    "system_monitoring_menu",
                ),
            ),
            "9": (
                "🧩 Umzi's Dataset_Preprocessing",
                lazy_menu(
                    "dataset_forge.menus.umzi_dataset_preprocessing_menu",
                    "umzi_dataset_preprocessing_menu",
                ),
            ),
            "10": (
                "🗂️  Enhanced Metadata Management",
                lazy_menu(
                    "dataset_forge.menus.enhanced_metadata_menu",
                    "enhanced_metadata_menu",
                ),
            ),
            "0": ("🚪 Exit", None),
        }
        choice = show_menu(
            "🎨 Dataset Forge - Main Menu 🎨",
            options,
            Mocha.lavender,
        )
        if choice is None or choice == "0":
            return
        action = options[choice][1]
        if callable(action):
            action()
