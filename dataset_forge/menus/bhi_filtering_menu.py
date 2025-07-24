from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
    print_warning,
    print_section,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.input_utils import get_folder_path
from dataset_forge.menus import session_state


def bhi_filtering_menu():
    from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering

    print_header("🧹 BHI Filtering - Input/Output Selection", color=Mocha.sapphire)
    # Get input folder
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        print_error("No input folder specified.")
        return
    # Get output folder
    output_folder = get_folder_path("Enter output folder path: ")
    if not output_folder:
        print_error("No output folder specified.")
        return
    # Get thresholds from user preferences or ask user
    thresholds = session_state.user_preferences.get("bhi_suggested_thresholds", {}).get(
        "moderate", {}
    )
    try:
        blockiness_threshold = float(
            input(
                f"Blockiness threshold (default {thresholds.get('blockiness', 0.5)}): "
            ).strip()
            or str(thresholds.get("blockiness", 0.5))
        )
        hyperiqa_threshold = float(
            input(
                f"HyperIQA threshold (default {thresholds.get('hyperiqa', 0.5)}): "
            ).strip()
            or str(thresholds.get("hyperiqa", 0.5))
        )
        ic9600_threshold = float(
            input(
                f"IC9600 threshold (default {thresholds.get('ic9600', 0.5)}): "
            ).strip()
            or str(thresholds.get("ic9600", 0.5))
        )
    except ValueError:
        print_error("Invalid threshold values.")
        return
    print_section("BHI Filtering Progress", color=Mocha.sapphire)
    print_info("Starting BHI filtering...")
    try:
        run_bhi_filtering(
            input_path=input_folder,
            thresholds={
                "blockiness": blockiness_threshold,
                "hyperiqa": hyperiqa_threshold,
                "ic9600": ic9600_threshold,
            },
        )
        print_success("BHI filtering completed successfully!")
    except Exception as e:
        print_error(f"BHI filtering failed: {e}")
    input("\nPress Enter to return to the menu...")


# Register a static menu for favorites
bhi_filtering_menu.__menu_options__ = {
    "1": ("Run BHI Filtering Workflow", bhi_filtering_menu),
    "0": ("Back to Main Menu", None),
}
