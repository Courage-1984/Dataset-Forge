from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_info,
    print_prompt,
    print_error,
    print_success,
)
from dataset_forge.utils.color import Mocha
import re
import sys
import importlib

# Only import menu functions directly
# from dataset_forge.menus.main_menu import main_menu # Removed to break circular import


# Recursively extract menu options from the main menu tree
# Returns: [("Parent > Child", callable), ...]
def extract_menu_tree():
    # Lazy import to avoid circular import
    def get_main_menu():
        from dataset_forge.menus.main_menu import main_menu

        return main_menu

    tree = []
    visited = set()

    def walk_menu(parent_label, menu_func):
        if menu_func in visited:
            return
        visited.add(menu_func)
        options = getattr(menu_func, "__menu_options__", None)
        if options is None:
            # If no static options, treat as a leaf action
            tree.append((parent_label, menu_func))
            return
        for key, (label, action) in options.items():
            full_label = f"{parent_label} > {label}" if parent_label else label
            if callable(action):
                walk_menu(full_label, action)
            else:
                tree.append((full_label, action))

    # Start from the main menu's static options
    main_menu = get_main_menu()
    main_options = getattr(main_menu, "__menu_options__", None)
    if main_options:
        for key, (label, action) in main_options.items():
            if callable(action):
                walk_menu(label, action)
            else:
                tree.append((label, action))
    return tree


def get_menu_options(menu_func):
    # Monkeypatch: run the menu function in a special mode to get its options
    # This is a hack, but works for static menu definitions
    import types

    options_holder = {}

    def fake_show_menu(title, options, **kwargs):
        options_holder.update(options)
        return None

    orig_show_menu = sys.modules[menu_func.__module__].show_menu
    sys.modules[menu_func.__module__].show_menu = fake_show_menu
    try:
        menu_func()
    except Exception:
        pass
    sys.modules[menu_func.__module__].show_menu = orig_show_menu
    return options_holder


def user_profile_menu():
    from dataset_forge.actions import user_profile_actions
    from dataset_forge.utils.printing import print_error

    options = {
        "1": ("👤 Profile Management", profile_management_menu),
        "2": ("⭐ Favorites", favorites_menu),
        "3": ("📁 Favorite Paths", favorite_paths_menu),
        "4": ("⚙️ Settings", settings_menu),
        "0": ("⬅️  Back", None),
    }
    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage user profiles and preferences",
        "Total Options": "4 profile operations",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": "Profile management, favorites, paths, settings",
    }

    while True:
        key = show_menu(
            "User Profile Management",
            options,
            header_color=Mocha.mauve,
            char="=",
            current_menu="User Profile Management",
            menu_context=menu_context,
        )
        if key is None:
            break
        action = options.get(key, (None, None))[1]
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


def profile_management_menu():
    while True:
        profiles = user_profile_actions.list_profiles()
        active = user_profile_actions.get_active_profile()
        print_info("\nUser Profiles:")
        for idx, name in enumerate(profiles, 1):
            marker = "*" if name == active else " "
            print_info(f"[{idx}] {name} {marker}")
        print_info("[C] Create Profile")
        print_info("[L] Load Profile")
        print_info("[D] Delete Profile")
        print_info("[0] Back")
        choice = input("Choice: ").strip().upper()
        if choice == "0":
            break
        elif choice == "C":
            name = input("Enter new profile name (alphanumeric/underscore): ").strip()
            if not re.match(r"^[A-Za-z0-9_]+$", name):
                print_error("Invalid name. Use only letters, numbers, and underscores.")
                continue
            try:
                user_profile_actions.create_profile(name)
                print_success(f"Profile '{name}' created and activated.")
            except Exception as e:
                print_error(str(e))
        elif choice == "L":
            idx = input("Enter number to load: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(profiles):
                user_profile_actions.set_active_profile(profiles[int(idx) - 1])
                print_success(f"Profile '{profiles[int(idx)-1]}' activated.")
        elif choice == "D":
            idx = input("Enter number to delete: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(profiles):
                user_profile_actions.delete_profile(profiles[int(idx) - 1])
                print_success(f"Profile '{profiles[int(idx)-1]}' deleted.")


def favorites_menu():
    while True:
        profile = user_profile_actions.load_user_profile()
        favorites = profile["favorites"]
        print_info("\nFavorite Menu Items:")
        for idx, fav in enumerate(favorites, 1):
            print_info(f"[{idx}] {fav}")
        print_info("[A] Add Favorite")
        print_info("[R] Remove Favorite")
        print_info("[0] Back")
        choice = input("Choice: ").strip().upper()
        if choice == "0":
            break
        elif choice == "A":
            menu_tree = extract_menu_tree()
            print_info("\nAll Menu Items:")
            for idx, (label, _) in enumerate(menu_tree, 1):
                print_info(f"[{idx}] {label}")
            sel = input("Enter number(s) to add (comma-separated): ").strip()
            for s in sel.split(","):
                s = s.strip()
                if s.isdigit() and 1 <= int(s) <= len(menu_tree):
                    user_profile_actions.add_favorite(menu_tree[int(s) - 1][0])
        elif choice == "R":
            idx = input("Enter number to remove: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(favorites):
                user_profile_actions.remove_favorite(favorites[int(idx) - 1])
        elif choice.isdigit() and 1 <= int(choice) <= len(favorites):
            # Run the favorite as a menu action
            menu_tree = extract_menu_tree()
            # Find the action by label
            label = favorites[int(choice) - 1]
            for l, action in menu_tree:
                if l == label and callable(action):
                    action()
                    break


def presets_menu():
    while True:
        profile = user_profile_actions.load_user_profile()
        presets = profile["presets"]
        print_info("\nPresets:")
        for idx, preset in enumerate(presets, 1):
            print_info(f"[{idx}] {preset}")
        print_info("[A] Add Preset")
        print_info("[R] Remove Preset")
        print_info("[0] Back")
        choice = input("Choice: ").strip().upper()
        if choice == "0":
            break
        elif choice == "A":
            name = input("Preset name: ").strip()
            details = input("Preset details/params (as text): ").strip()
            if name:
                user_profile_actions.add_preset({"name": name, "details": details})
        elif choice == "R":
            idx = input("Enter number to remove: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(presets):
                user_profile_actions.remove_preset(int(idx) - 1)


def favorite_paths_menu():
    while True:
        profile = user_profile_actions.load_user_profile()
        paths = profile["favorite_paths"]
        print_info("\nFavorite Paths:")
        for idx, path in enumerate(paths, 1):
            print_info(f"[{idx}] {path}")
        print_info("[A] Add Path")
        print_info("[R] Remove Path")
        print_info("[0] Back")
        choice = input("Choice: ").strip().upper()
        if choice == "0":
            break
        elif choice == "A":
            path = input("Enter path to add: ").strip()
            if path:
                user_profile_actions.add_favorite_path(path)
        elif choice == "R":
            idx = input("Enter number to remove: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(paths):
                user_profile_actions.remove_favorite_path(paths[int(idx) - 1])


def settings_menu():
    while True:
        profile = user_profile_actions.load_user_profile()
        settings = profile["settings"]
        print_info("\nUser Settings:")
        for k, v in settings.items():
            print_info(f"{k}: {v}")
        print_info("[U] Update Setting")
        print_info("[0] Back")
        choice = input("Choice: ").strip().upper()
        if choice == "0":
            break
        elif choice == "U":
            key = input("Setting key: ").strip()
            value = input("Setting value: ").strip()
            if key:
                user_profile_actions.update_setting(key, value)
