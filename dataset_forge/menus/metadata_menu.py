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
from dataset_forge.actions.metadata_actions import (
    exif_scrubber_menu,
    icc_to_srgb_menu,
)

# Assume exif_scrubber_menu and icc_to_srgb_menu are available in the global scope for now


def metadata_menu():
    from dataset_forge.actions.metadata_actions import (
        exif_scrubber_menu,
        icc_to_srgb_menu,
    )
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.printing import print_error

    options = {
        "1": ("🧹 Scrub EXIF Metadata", exif_scrubber_menu),
        "2": ("🎯 Convert ICC Profile to sRGB", icc_to_srgb_menu),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage EXIF metadata and ICC color profiles",
        "Total Options": "2 metadata operations",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
        "Key Features": "EXIF scrubbing, ICC profile conversion",
    }

    while True:
        key = show_menu(
            "EXIF & ICC Profile Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Metadata Management",
            menu_context=menu_context,
        )
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            break
        action = options[key][1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )
