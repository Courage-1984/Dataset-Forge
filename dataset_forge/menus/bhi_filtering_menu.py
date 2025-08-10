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
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.file_utils import perform_file_operation, get_unique_filename
from dataset_forge.menus import session_state


def bhi_filtering_menu():
    from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering

    print_header("🧹 BHI Filtering - Input/Output Selection", color=Mocha.sapphire)
    # Get input folder
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        print_error("No input folder specified.")
        return
    
    # Get action type from user
    print_section("Action Selection", color=Mocha.sapphire)
    print_info("What would you like to do with filtered files?")
    print_info("1. Move files to a new folder")
    print_info("2. Copy files to a new folder") 
    print_info("3. Delete files in-place")
    print_info("4. Report only (dry run)")
    
    action_choice = input("Enter your choice (1-4, default: 1): ").strip() or "1"
    
    action = None
    output_folder = None
    
    if action_choice == "1":
        action = "move"
        output_folder = get_folder_path("Enter destination folder for moved files: ")
        if not output_folder:
            print_error("No destination folder specified.")
            return
    elif action_choice == "2":
        action = "copy"
        output_folder = get_folder_path("Enter destination folder for copied files: ")
        if not output_folder:
            print_error("No destination folder specified.")
            return
    elif action_choice == "3":
        action = "delete"
        print_warning("⚠️  This will permanently delete files! Are you sure?")
        print_warning("This action cannot be undone!")
        confirm = input("Type 'YES' to confirm deletion: ").strip()
        if confirm != "YES":
            print_info("Operation cancelled.")
            return
    elif action_choice == "4":
        action = "report"
        print_info("Running in report mode - no files will be modified.")
    else:
        print_error("Invalid choice. Please select 1-4.")
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
    print_info(f"Starting BHI filtering with action: {action}")
    if output_folder:
        print_info(f"Destination: {output_folder}")
    
    try:
        run_bhi_filtering(
            input_path=input_folder,
            output_folder=output_folder,
            action=action,
            thresholds={
                "blockiness": blockiness_threshold,
                "hyperiqa": hyperiqa_threshold,
                "ic9600": ic9600_threshold,
            },
        )
        print_success("BHI filtering completed successfully!")
        play_done_sound()
    except Exception as e:
        print_error(f"BHI filtering failed: {e}")
    input("\nPress Enter to return to the menu...")


# Register a static menu for favorites
bhi_filtering_menu.__menu_options__ = {
    "1": ("Run BHI Filtering Workflow", bhi_filtering_menu),
    "0": ("Back to Main Menu", None),
}
