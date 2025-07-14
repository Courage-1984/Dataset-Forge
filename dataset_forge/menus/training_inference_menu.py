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

    options = {
        "1": ("📝 Add Training/Inference Config", add_config_file),
        "2": ("📂 Load Config", load_config_file),
        "3": ("ℹ️ View Config Info", view_config_info),
        "4": ("✅ Validate HQ/LQ Dataset", validate_dataset_from_config),
        "5": ("✅ Validate Val Dataset", validate_val_dataset_from_config),
        "6": ("🛠️ Run wtp_dataset_destroyer", run_wtp_dataset_destroyer),
        "7": ("🚀 Run traiNNer-redux", run_trainner_redux),
        "8": ("✏️ Edit .hcl Config File", edit_hcl_file),
        "9": ("✏️ Edit .yml Config File", edit_yml_file),
        "10": ("📋 List/Upscale with Model", list_and_upscale_with_model),
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
