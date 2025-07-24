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


def config_menu():
    from dataset_forge.utils.printing import print_error, print_header, print_section
    from dataset_forge.utils.color import Mocha

    options = config_menu.__menu_options__
    while True:
        print_header(
            "⚙️ Configuration & Model Management - Input/Output Selection",
            color=Mocha.mauve,
        )
        key = show_menu(
            "Configuration & Model Management",
            options,
            header_color=Mocha.mauve,
            char="=",
        )
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
        if callable(action):
            print_section("Configuration Progress", color=Mocha.mauve)
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


config_menu.__menu_options__ = {
    "1": ("Add Config File", add_config_file),
    "2": ("Load Config File", load_config_file),
    "3": ("View Config Info", view_config_info),
    "4": ("Validate HQ/LQ Dataset from Config", validate_dataset_from_config),
    "5": ("Validate Val Dataset HQ/LQ Pair", validate_val_dataset_from_config),
    "6": ("Run wtp_dataset_destroyer", run_wtp_dataset_destroyer),
    "7": ("Edit .hcl config file", edit_hcl_file),
    "8": ("Run traiNNer-redux", run_trainner_redux),
    "9": ("Edit .yml config file", edit_yml_file),
    "10": ("List/Run Upscale with Model", list_and_upscale_with_model),
    "0": ("Back to Main Menu", None),
}
