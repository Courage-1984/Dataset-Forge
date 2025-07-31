from dataset_forge.menus.model_management_menu import (
    openmodeldb_model_browser_menu,
    openmodeldb_model_browser_cli_interactive,
)
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import print_error


def training_inference_menu():
    while True:
        options = {
            "1": ("📝 Add Training/Inference Config", None),
            "2": ("📂 Load Config", None),
            "3": ("ℹ️  View Config Info", None),
            "4": ("✅ Validate HQ/LQ Dataset", None),
            "5": ("✅ Validate Val Dataset", None),
            "6": ("🛠️  Run wtp_dataset_destroyer", None),
            "7": ("🚀 Run traiNNer-redux", None),
            "8": ("✏️  Edit .hcl Config File (wtp_dataset_destroyer)", None),
            "9": ("✏️  Edit .yml Config File (traiNNer-redux)", None),
            "10": ("📋 List/Upscale with Model", None),
            "11": ("🧠 OpenModelDB Model Browser", openmodeldb_model_browser_menu),
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
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            return
        action = options[key][1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
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
        choice = show_menu(
            "OpenModelDB Model Browser - Choose Mode", options, Mocha.lavender, current_menu="OpenModelDB Model Browser Mode", menu_context=menu_context
        )
        if choice is None or choice == "0":
            break
        action = options[choice][1]
        if action:
            action()
