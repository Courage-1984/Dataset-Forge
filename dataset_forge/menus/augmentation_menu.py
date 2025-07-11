import os
from dataset_forge.utils.input_utils import (
    select_folder,
    ask_yes_no,
    ask_int,
    ask_float,
)
from dataset_forge.utils.printing import print_section, print_success, print_warning
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha

# If path history is managed elsewhere, import and use it here
try:
    from dataset_forge.utils.path_history import (
        get_path_from_history,
        add_path_to_history,
    )
except ImportError:

    def get_path_from_history(*args, **kwargs):
        return None

    def add_path_to_history(*args, **kwargs):
        pass


def augmentation_menu():
    from dataset_forge.actions import augmentation_actions as aug

    options = augmentation_menu.__menu_options__
    while True:
        action = show_menu(
            "Augmentation Recipes",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()


# Register a static menu for favorites (customize as needed)
augmentation_menu.__menu_options__ = {
    "1": ("Run Augmentation Pipeline", lambda: None),
    "0": ("Back to Main Menu", None),
}
