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


def training_inference_menu():
    from dataset_forge.actions.config_actions import (
        create_training_config,
        create_inference_config,
        validate_config,
        list_available_models,
    )

    options = {
        "1": ("📝 Create Training Config", create_training_config),
        "2": ("🎯 Create Inference Config", create_inference_config),
        "3": ("✅ Validate Config", validate_config),
        "4": ("📋 List Available Models", list_available_models),
        "0": ("⬅️ Back to Main Menu", None),
    }
    while True:
        action = show_menu(
            "🚀 Training & Inference",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action()
