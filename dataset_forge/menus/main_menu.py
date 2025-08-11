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
        "Purpose": "Main navigation hub for all Dataset Forge features - your command center for image dataset management",
        "Total Options": "10 main categories",
        "Navigation": "Use numbers 1-10 to select, 0 to exit",
        "Key Features": [
            "📂 Dataset Management - Create, organize, and manage your image datasets from scratch",
            "✨ Image Processing & Augmentation - Transform, enhance, and augment images for machine learning",
            "🔍 Analysis & Validation - Assess dataset quality, find issues, and validate your data",
            "🛠️ Utilities - Helper tools for comparison, compression, deduplication, and file management",
            "🚀 Training & Inference - Train models, run inference, and manage your ML workflows",
            "🗂️ Enhanced Metadata Management - Handle EXIF data, color profiles, and image metadata",
            "⚙️ System & Settings - Configure preferences, manage memory, and customize your environment",
            "🩺 System Monitoring & Health - Monitor resources, check system status, and maintain performance",
            "🚀 Performance Optimization - Optimize processing speed, memory usage, and system efficiency",
            "🔗 Links - Quick access to documentation, resources, and external tools",
        ],
        "Tips": [
            "🎯 Start with Dataset Management if you're new to Dataset Forge",
            "⚡ Use Image Processing & Augmentation for most common operations (resize, crop, enhance)",
            "🔍 Run Analysis & Validation to check dataset quality before processing",
            "🛠️ Utilities provide essential tools for dataset cleanup and organization",
            "🚀 Training & Inference is for advanced users working with ML models",
            "⚙️ Configure System & Settings first to optimize your workflow",
            "🩺 Use System Monitoring to track resource usage during large operations",
            "💡 Use 'help' in any menu for context-aware assistance",
            "🔄 Use '0' to go back or 'quit' to exit from any menu level",
        ],
        "Usage Examples": [
            "📂 New user workflow: 1 → Create dataset → 3 → Process images → 2 → Validate quality",
            "🔄 Regular workflow: 3 → Process images → 2 → Analyze results → 5 → Train model",
            "🧹 Cleanup workflow: 4 → Deduplication → 4 → Compression → 6 → Sanitization",
            "⚙️ Setup workflow: 7 → Configure settings → 8 → Monitor system → 9 → Optimize performance",
        ],
        "Performance Notes": [
            "💾 Large datasets (>10k images): Use chunked processing and monitor memory",
            "🚀 GPU operations: Ensure CUDA is available for accelerated processing",
            "📊 Analysis tools: Use sampling for quick previews on large datasets",
            "🔄 Batch operations: Process in smaller batches for better error recovery",
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
