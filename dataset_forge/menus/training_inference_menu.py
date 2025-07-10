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
from dataset_forge.actions.config_actions import (
    add_config_file,
    load_config_file,
    view_config_info,
    validate_dataset_from_config,
    validate_val_dataset_from_config,
    run_wtp_dataset_destroyer,
    run_trainner_redux,
    edit_hcl_file,
    edit_yml_file,
    list_and_upscale_with_model,
)


def manage_config_files_menu():
    """Sub-menu for managing configuration files."""
    options = {
        "1": ("Add/Load Config File", add_config_file),
        "2": ("Edit Config File", edit_config_file_workflow),
        "3": ("View Config Info", view_config_info),
        "0": ("Back", None),
    }
    
    while True:
        action = show_menu(
            "Manage Config Files (.hcl, .yml)",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def edit_config_file_workflow():
    """Workflow for editing config files."""
    print("\n=== Edit Config File ===")
    print("1. Edit .hcl config file")
    print("2. Edit .yml config file")
    print("0. Back")
    choice = input("Select file type: ")
    if choice == "1":
        edit_hcl_file()
    elif choice == "2":
        edit_yml_file()
    input("\nPress Enter to return to the menu...")


def validate_dataset_menu():
    """Sub-menu for dataset validation from config."""
    options = {
        "1": ("Validate Training HQ/LQ Dataset", validate_dataset_from_config),
        "2": ("Validate Validation HQ/LQ Dataset", validate_val_dataset_from_config),
        "0": ("Back", None),
    }
    
    while True:
        action = show_menu(
            "Validate Dataset from Config",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def run_training_models_menu():
    """Sub-menu for running training and models."""
    options = {
        "1": ("Run traiNNer-redux", run_trainner_redux),
        "2": ("List/Run Upscale with Model", list_and_upscale_with_model),
        "3": ("Run wtp_dataset_destroyer", run_wtp_dataset_destroyer),
        "0": ("Back", None),
    }
    
    while True:
        action = show_menu(
            "Run Training / Models",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def training_inference_menu():
    """Main training and inference menu with hierarchical structure."""
    options = {
        "1": ("Manage Config Files (.hcl, .yml)", manage_config_files_menu),
        "2": ("Validate Dataset from Config", validate_dataset_menu),
        "3": ("Run Training / Models", run_training_models_menu),
        "0": ("Back to Main Menu", None),
    }
    
    while True:
        action = show_menu(
            "Training & Inference",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action() 