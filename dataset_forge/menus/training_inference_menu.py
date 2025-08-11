# Use lazy_menu for model management menu functions
def openmodeldb_model_browser_menu():
    """Lazy import wrapper for openmodeldb_model_browser_menu."""
    from dataset_forge.utils.menu import lazy_menu
    return lazy_menu("dataset_forge.menus.model_management_menu", "openmodeldb_model_browser_menu")()

def openmodeldb_model_browser_cli_interactive():
    """Lazy import wrapper for openmodeldb_model_browser_cli_interactive."""
    from dataset_forge.utils.menu import lazy_menu
    return lazy_menu("dataset_forge.menus.model_management_menu", "openmodeldb_model_browser_cli_interactive")()

from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import print_error


def training_inference_menu():
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
    
    while True:
        options = {
            "1": ("📝 Add Training/Inference Config", add_config_file),
            "2": ("📂 Load Config", load_config_file),
            "3": ("ℹ️  View Config Info", view_config_info),
            "4": ("✅ Validate HQ/LQ Dataset", validate_dataset_from_config),
            "5": ("✅ Validate Val Dataset", validate_val_dataset_from_config),
            "6": ("🛠️  Run wtp_dataset_destroyer", run_wtp_dataset_destroyer),
            "7": ("🚀 Run traiNNer-redux", run_trainner_redux),
            "8": ("✏️  Edit .hcl Config File (wtp_dataset_destroyer)", edit_hcl_file),
            "9": ("✏️  Edit .yml Config File (traiNNer-redux)", edit_yml_file),
            "10": ("📋 List/Upscale with Model", list_and_upscale_with_model),
            "11": ("🧠 OpenModelDB Model Browser", openmodeldb_model_browser_mode_menu),
            "0": ("⬅️  Back to Main Menu", None),
        }
        # Define menu context for help system
        menu_context = {
            "Purpose": "Manage training and inference configurations and operations",
            "Total Options": "11 training operations",
            "Navigation": "Use numbers 1-11 to select, 0 to go back",
            "Key Features": "Config management, dataset validation, model browser, training tools",
        }

        key = show_menu(
            "🚀 Training & Inference",
            options,
            Mocha.lavender,
            current_menu="Training & Inference",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


def openmodeldb_model_browser_mode_menu():
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha

    options = {
        "1": ("🧾 Basic Menu (classic)", openmodeldb_model_browser_menu),
        "2": (
            "🖱️ CLI-interactive (modern, live search)",
            openmodeldb_model_browser_cli_interactive,
        ),
        "0": ("⬅️  Back", None),
    }
    # Define menu context for help system
    menu_context = {
        "Purpose": "Choose OpenModelDB model browser interface mode",
        "Options": "2 browser modes available",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
    }

    while True:
        key = show_menu(
            "OpenModelDB Model Browser - Choose Mode",
            options,
            Mocha.lavender,
            current_menu="OpenModelDB Model Browser Mode",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options[key][1]
        if action:
            action()
