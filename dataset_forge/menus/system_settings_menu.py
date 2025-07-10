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
from dataset_forge.menus.settings_menu import settings_menu
from dataset_forge.menus.user_profile_menu import user_profile_menu
from dataset_forge.menus.history_log_menu import history_log_menu
from dataset_forge.menus.links_menu import links_menu


def user_profile_submenu():
    """Sub-menu for user profile management."""
    options = {
        "1": ("Profile Management", lambda: user_profile_menu()),
        "2": ("View/Edit Favorites & Presets", lambda: user_profile_menu()),
        "3": ("Manage Quick Access Paths", lambda: user_profile_menu()),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "User Profile",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def system_settings_menu():
    """Main system and settings menu with hierarchical structure."""
    options = {
        "1": ("Set Working Directories (HQ/LQ Folders)", settings_menu),
        "2": ("User Profile", user_profile_submenu),
        "3": ("View Change/History Log", history_log_menu),
        "4": ("Links (Community & Personal)", links_menu),
        "0": ("Back to Main Menu", None),
    }

    while True:
        action = show_menu(
            "System & Settings",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action()
