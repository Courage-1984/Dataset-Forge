from dataset_forge.menus.dataset_menu import dataset_menu
from dataset_forge.menus.analysis_menu import analysis_menu
from dataset_forge.menus.transform_menu import transform_menu
from dataset_forge.menus.metadata_menu import metadata_menu
from dataset_forge.menus.comparison_menu import comparison_menu
from dataset_forge.menus.config_menu import config_menu
from dataset_forge.menus.settings_menu import settings_menu
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import print_info
from dataset_forge.actions.batch_rename_actions import batch_rename_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.menus import session_state
from dataset_forge.menus.compress_menu import compress_menu
from dataset_forge.menus.compress_dir_menu import compress_dir_menu


def main_menu():
    """Main menu for the Image Dataset Utility."""
    main_options = {
        "1": ("\U0001f4c2 DATASET", dataset_menu),
        "2": ("\U0001f4ca ANALYSIS", analysis_menu),
        "3": ("\u2728 TRANSFORM", transform_menu),
        "4": ("\U0001f5c2\ufe0f  METADATA", metadata_menu),
        "5": ("\U0001f50d COMPARISON", comparison_menu),
        "6": ("\U0001f4dd BATCH RENAME", batch_rename_menu),
        "7": ("\U0001f4c1 CONFIG", config_menu),
        "8": ("\u2699\ufe0f  SETTINGS", settings_menu),
        "9": ("\U0001f4e6 COMPRESS IMAGES", compress_menu),
        "10": ("\U0001f4e6 COMPRESS DIRECTORY", compress_dir_menu),
        "0": ("\U0001f6aa EXIT", None),
    }
    while True:
        try:
            action = show_menu(
                "Image Dataset Utility - Main Menu",
                main_options,
                header_color=Mocha.lavender,
            )
            if action is None:
                print_info("Exiting...")
                break
            action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break
