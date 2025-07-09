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
    options = metadata_menu.__menu_options__
    while True:
        action = show_menu(
            "EXIF & ICC Profile Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


metadata_menu.__menu_options__ = {
    "1": ("Scrub EXIF Metadata", exif_scrubber_menu),
    "2": ("Convert ICC Profile to sRGB", icc_to_srgb_menu),
    "0": ("Back to Main Menu", None),
}
