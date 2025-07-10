from dataset_forge.menus.dataset_management_menu import dataset_management_menu
from dataset_forge.menus.analysis_validation_menu import analysis_validation_menu
from dataset_forge.menus.image_processing_menu import image_processing_menu
from dataset_forge.menus.training_inference_menu import training_inference_menu
from dataset_forge.menus.utilities_menu import utilities_menu
from dataset_forge.menus.system_settings_menu import system_settings_menu
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import print_info
from dataset_forge.utils.color import Mocha


def main_menu():
    """Main menu for the Image Dataset Utility."""
    main_options = main_menu.__menu_options__
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


# Register a static menu for favorites
main_menu.__menu_options__ = {
    "1": ("📂 Dataset Management", dataset_management_menu),
    "2": ("🔍 Analysis & Validation", analysis_validation_menu),
    "3": ("✨ Image Processing & Augmentation", image_processing_menu),
    "4": ("🚀 Training & Inference", training_inference_menu),
    "5": ("🛠️ Utilities", utilities_menu),
    "6": ("⚙️ System & Settings", system_settings_menu),
    "0": ("🚪 Exit", None),
}
