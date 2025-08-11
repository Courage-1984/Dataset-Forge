import importlib
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils import monitoring
from dataset_forge.utils.audio_utils import play_startup_sound
from dataset_forge.utils.printing import print_info

# Helper for lazy importing submenu modules
# This returns a function that, when called, imports and calls the submenu


def lazy_menu(module_name: str, func_name: str):
    def _menu():
        # Use the decorator pattern
        decorated_func = monitoring.time_and_record_menu_load(func_name)(
            lambda: getattr(importlib.import_module(module_name), func_name)()
        )
        return decorated_func()  # Call the decorated function

    return _menu


def main_menu():
    # Play startup sound once per session
    play_startup_sound(block=False)

    # Define menu context for help system
    menu_context = {
        "Purpose": "Main navigation hub for all Dataset Forge features",
        "Total Options": "10 main categories",
        "Navigation": "Use numbers 1-10 to select, 0 to exit",
        "Key Features": [
            "📂 Dataset Management - Core dataset creation and organization tools",
            "✨ Image Processing & Augmentation - Most frequently used operations",
            "🔍 Analysis & Validation - Quality assurance and dataset analysis",
            "🛠️ Utilities - Helper tools and utilities",
            "🚀 Training & Inference - Advanced machine learning workflows",
            "🗂️ Enhanced Metadata Management - Specialized metadata operations",
            "⚙️ System & Settings - Configuration and preferences",
            "🩺 System Monitoring & Health - System maintenance and monitoring",
            "🚀 Performance Optimization - Advanced performance tuning",
            "🔗 Links - Reference materials and external resources",
        ],
        "Tips": [
            "Start with Dataset Management if you're new to Dataset Forge",
            "Use Image Processing & Augmentation for most common operations",
            "Analysis & Validation helps ensure dataset quality",
            "System Monitoring helps track resource usage during operations",
            "Use 'help' in any menu for context-aware assistance",
        ],
    }

    while True:
        try:
            options = {
                "1": (
                    "📂 Dataset Management",
                    lazy_menu(
                        "dataset_forge.menus.dataset_management_menu",
                        "dataset_management_menu",
                    ),
                ),
                "2": (
                    "✨ Image Processing & Augmentation",
                    lazy_menu(
                        "dataset_forge.menus.image_processing_menu",
                        "image_processing_menu",
                    ),
                ),
                "3": (
                    "🔍 Analysis & Validation",
                    lazy_menu(
                        "dataset_forge.menus.analysis_validation_menu",
                        "analysis_validation_menu",
                    ),
                ),
                "4": (
                    "🛠️ Utilities",
                    lazy_menu("dataset_forge.menus.utilities_menu", "utilities_menu"),
                ),
                "5": (
                    "🚀 Training & Inference",
                    lazy_menu(
                        "dataset_forge.menus.training_inference_menu",
                        "training_inference_menu",
                    ),
                ),
                "6": (
                    "🗂️ Enhanced Metadata Management",
                    lazy_menu(
                        "dataset_forge.menus.enhanced_metadata_menu",
                        "enhanced_metadata_menu",
                    ),
                ),
                "7": (
                    "⚙️ System & Settings",
                    lazy_menu(
                        "dataset_forge.menus.system_settings_menu",
                        "system_settings_menu",
                    ),
                ),
                "8": (
                    "🩺 System Monitoring & Health",
                    lazy_menu(
                        "dataset_forge.menus.system_monitoring_menu",
                        "system_monitoring_menu",
                    ),
                ),
                "9": (
                    "🚀 Performance Optimization",
                    lazy_menu(
                        "dataset_forge.menus.performance_optimization_menu",
                        "performance_optimization_menu",
                    ),
                ),
                "10": (
                    "🔗 Links",
                    lazy_menu("dataset_forge.menus.links_menu", "links_menu"),
                ),
                "0": ("🚪 Exit", None),
            }
            key = show_menu(
                "🎨 Dataset Forge - Main Menu 🎨",
                options,
                Mocha.lavender,
                current_menu="Main Menu",
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
