"""
Resave Images Menu

This module provides the menu interface for the resave images functionality,
following the Dataset Forge patterns for menu organization and lazy imports.
"""

from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.monitoring import time_and_record_menu_load
from dataset_forge.utils.printing import print_info


def lazy_action(action_name: str):
    """Lazy import helper for menu actions."""
    if action_name == "resave_images_workflow":
        from dataset_forge.actions.resave_images_actions import resave_images_workflow

        return resave_images_workflow
    elif action_name == "resave_images_menu":
        from dataset_forge.actions.resave_images_actions import resave_images_menu

        return resave_images_menu
    else:
        raise ValueError(f"Unknown action: {action_name}")


@time_and_record_menu_load("resave_images_menu")
def resave_images_menu():
    """
    Menu for resave images functionality.

    This function provides a menu interface for accessing the resave images
    functionality with different options and workflows.
    """
    options = {
        "1": (
            "🔄 Resave Images (Interactive)",
            lambda: lazy_action("resave_images_workflow")(),
        ),
        "2": (
            "📁 Resave Single Folder",
            lambda: lazy_action("resave_images_workflow")(recursive=False),
        ),
        "3": (
            "📂 Resave with Recursion",
            lambda: lazy_action("resave_images_workflow")(recursive=True),
        ),
        "4": (
            "⚫ Convert to Grayscale",
            lambda: lazy_action("resave_images_workflow")(grayscale=True),
        ),
        "0": ("🚪 Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Resave images with different formats and options",
        "Total Options": "4 resave operations",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": "Interactive resave, single folder, recursive, grayscale conversion",
    }

    while True:
        try:
            key = show_menu("🔄 Resave Images", options, Mocha.lavender, current_menu="Resave Images", menu_context=menu_context)
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break
        except Exception as e:
            print_info(f"Menu error: {e}")
            break
