import importlib
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha

# Helper for lazy importing submenu modules
# This returns a function that, when called, imports and calls the submenu


def lazy_menu(module_name: str, func_name: str):
    def _menu():
        module = importlib.import_module(module_name)
        getattr(module, func_name)()

    return _menu


def main_menu():
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
                "🛠️ Utilities",
                lazy_menu("dataset_forge.menus.utilities_menu", "utilities_menu"),
            ),
            "6": (
                "⚙️ System & Settings",
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
            "0": ("🚪 Exit", None),
        }
        choice = show_menu(
            "🎨 Image Dataset Utility - Main Menu 🎨",
            options,
            Mocha.lavender,
        )
        if choice is None or choice == "0":
            break
        action = options[choice][1]
        if action:
            action()
