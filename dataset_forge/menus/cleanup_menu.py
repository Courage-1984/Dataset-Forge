"""
cleanup_menu.py - Cleanup and Optimization Menu for Dataset Forge

Provides:
- Cache folder cleanup (.pytest_cache, __pycache__)
- System cache cleanup
- Comprehensive cleanup operations
- Cache usage analysis
"""

from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import print_info
from dataset_forge.actions.cleanup_actions import (
    cleanup_pytest_cache,
    cleanup_pycache,
    cleanup_all_cache_folders,
    comprehensive_cleanup,
    analyze_cache_usage,
)


def cleanup_menu():
    """Cleanup and optimization menu for Dataset Forge."""
    options = {
        "1": ("🧹 Remove .pytest_cache folders", cleanup_pytest_cache),
        "2": ("🧹 Remove __pycache__ folders", cleanup_pycache),
        "3": ("🧹 Remove All Cache Folders", cleanup_all_cache_folders),
        "4": ("🧹 Comprehensive System Cleanup", comprehensive_cleanup),
        "5": ("📊 Analyze Cache Usage", analyze_cache_usage),
        "0": ("⬅️ Back to System Monitoring", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Cleanup and optimization tools for Dataset Forge project",
        "Options": "5 cleanup operations available",
        "Navigation": "Use numbers 1-5 to select, 0 to go back",
        "Key Features": [
            "Remove .pytest_cache folders - Clean up pytest test cache",
            "Remove __pycache__ folders - Clean up Python bytecode cache",
            "Remove All Cache Folders - Clean up both types of cache folders",
            "Comprehensive System Cleanup - Full system cleanup including caches and memory",
            "Analyze Cache Usage - View cache usage statistics and recommendations"
        ],
        "Tips": [
            "Use 'Analyze Cache Usage' first to see what needs cleaning",
            "Comprehensive cleanup is recommended for major cleanup operations",
            "Cache folders are automatically regenerated when needed",
            "Cleanup operations include automatic memory management"
        ]
    }

    while True:
        try:
            key = show_menu(
                "🧹 Cleanup & Optimization",
                options,
                Mocha.lavender,
                current_menu="Cleanup & Optimization",
                menu_context=menu_context
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Cleanup Menu...")
            return 