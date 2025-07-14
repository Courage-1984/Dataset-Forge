from dataset_forge.menus.training_inference_menu import training_inference_menu
from dataset_forge.menus.dataset_management_menu import dataset_management_menu
from dataset_forge.menus.analysis_validation_menu import analysis_validation_menu
from dataset_forge.menus.image_processing_menu import image_processing_menu
from dataset_forge.menus.utilities_menu import utilities_menu
from dataset_forge.menus.system_settings_menu import system_settings_menu
from dataset_forge.menus.links_menu import links_menu
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha


def main_menu():
    while True:
        options = {
            "1": ("📂 Dataset Management", dataset_management_menu),
            "2": ("🔍 Analysis & Validation", analysis_validation_menu),
            "3": ("✨ Image Processing & Augmentation", image_processing_menu),
            "4": ("🚀 Training & Inference", training_inference_menu),
            "5": ("🛠️ Utilities", utilities_menu),
            "6": ("⚙️ System & Settings", system_settings_menu),
            "7": ("🔗 Links", links_menu),
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
