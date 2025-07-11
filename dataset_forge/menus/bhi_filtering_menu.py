from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering
from dataset_forge.utils.input_utils import get_folder_path
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
    print_section,
    print_warning,
)
from dataset_forge.menus import session_state


def show_threshold_presets():
    """Display available threshold presets."""
    print_section("BHI Filtering Threshold Presets", char="-")
    suggested = session_state.user_preferences["bhi_suggested_thresholds"]

    print_info("Available presets:")
    print("  [1] Conservative - Less aggressive filtering (thresholds: 0.3)")
    print("      Good for: High-quality datasets, minimal filtering")
    print("  [2] Moderate - Balanced filtering (thresholds: 0.5)")
    print("      Good for: General purpose, default recommendation")
    print("  [3] Aggressive - More aggressive filtering (thresholds: 0.7)")
    print("      Good for: Low-quality datasets, strict filtering")
    print("  [4] Custom - Set your own thresholds")
    print("  [5] Use Current Defaults - Use saved default thresholds")

    current_defaults = (
        f"Blockiness: {session_state.user_preferences['bhi_blockiness_threshold']}, "
        f"HyperIQA: {session_state.user_preferences['bhi_hyperiqa_threshold']}, "
        f"IC9600: {session_state.user_preferences['bhi_ic9600_threshold']}"
    )
    print(f"\nCurrent defaults: {current_defaults}")


def get_thresholds_from_preset():
    """Get thresholds based on user's preset choice."""
    show_threshold_presets()

    while True:
        choice = input("\nSelect preset [1-5]: ").strip()

        if choice == "1":  # Conservative
            return session_state.user_preferences["bhi_suggested_thresholds"][
                "conservative"
            ]
        elif choice == "2":  # Moderate
            return session_state.user_preferences["bhi_suggested_thresholds"][
                "moderate"
            ]
        elif choice == "3":  # Aggressive
            return session_state.user_preferences["bhi_suggested_thresholds"][
                "aggressive"
            ]
        elif choice == "4":  # Custom
            return get_custom_thresholds()
        elif choice == "5":  # Current defaults
            return {
                "blockiness": session_state.user_preferences[
                    "bhi_blockiness_threshold"
                ],
                "hyperiqa": session_state.user_preferences["bhi_hyperiqa_threshold"],
                "ic9600": session_state.user_preferences["bhi_ic9600_threshold"],
            }
        else:
            print_error("Invalid choice. Please select 1-5.")


def get_custom_thresholds():
    """Get custom thresholds from user input."""
    print_section("Custom Thresholds", char="-")
    print_info("Enter custom threshold values (0.0 to 1.0):")
    print_info("Lower values = more aggressive filtering")
    print_info("Higher values = less aggressive filtering")

    try:
        blockiness = float(input("Blockiness threshold [0.5]: ").strip() or "0.5")
        hyperiqa = float(input("HyperIQA threshold [0.5]: ").strip() or "0.5")
        ic9600 = float(input("IC9600 threshold [0.5]: ").strip() or "0.5")

        # Validate thresholds
        for name, value in [
            ("Blockiness", blockiness),
            ("HyperIQA", hyperiqa),
            ("IC9600", ic9600),
        ]:
            if not 0.0 <= value <= 1.0:
                print_warning(
                    f"{name} threshold should be between 0.0 and 1.0. Using 0.5."
                )
                if name == "Blockiness":
                    blockiness = 0.5
                elif name == "HyperIQA":
                    hyperiqa = 0.5
                else:
                    ic9600 = 0.5

        return {
            "blockiness": blockiness,
            "hyperiqa": hyperiqa,
            "ic9600": ic9600,
        }
    except ValueError:
        print_error("Invalid threshold value. Using moderate defaults.")
        return session_state.user_preferences["bhi_suggested_thresholds"]["moderate"]


def bhi_filtering_menu():
    print_header("BHI Filtering (Blockiness, HyperIQA, IC9600)")

    # Get input path
    input_path = get_folder_path("Enter the path to the folder to filter: ")
    if not input_path:
        return

    # Get thresholds
    thresholds = get_thresholds_from_preset()

    print_section("Selected Thresholds", char="-")
    print_info(f"Blockiness: {thresholds['blockiness']}")
    print_info(f"HyperIQA: {thresholds['hyperiqa']}")
    print_info(f"IC9600: {thresholds['ic9600']}")

    # Get action
    print_section("Action Selection", char="-")
    print_info("Available actions:")
    print("  [1] Move - Move filtered files to a separate folder")
    print("  [2] Delete - Permanently delete filtered files")
    print("  [3] Report - Only report what would be filtered (no changes)")

    action_map = {"1": "move", "2": "delete", "3": "report"}
    while True:
        action_choice = input("Select action [1-3]: ").strip()
        if action_choice in action_map:
            action = action_map[action_choice]
            break
        else:
            print_error("Invalid choice. Please select 1-3.")

    # Get batch size
    default_batch_size = session_state.user_preferences["default_batch_size"]
    batch_size_input = input(f"Batch size [{default_batch_size}]: ").strip()
    try:
        batch_size = (
            int(batch_size_input) if batch_size_input.isdigit() else default_batch_size
        )
    except ValueError:
        batch_size = default_batch_size

    # Get dry run preference
    dry_run = input("Dry run first? (y/N): ").strip().lower() == "y"

    # Confirm before proceeding
    print_section("Confirmation", char="-")
    print_info(f"Input folder: {input_path}")
    print_info(
        f"Thresholds: Blockiness={thresholds['blockiness']}, HyperIQA={thresholds['hyperiqa']}, IC9600={thresholds['ic9600']}"
    )
    print_info(f"Action: {action}")
    print_info(f"Batch size: {batch_size}")
    print_info(f"Dry run: {dry_run}")

    confirm = input("\nProceed with BHI filtering? (y/N): ").strip().lower()
    if confirm != "y":
        print_info("BHI filtering cancelled.")
        return

    try:
        results = run_bhi_filtering(
            input_path=input_path,
            thresholds=thresholds,
            action=action,
            batch_size=batch_size,
            dry_run=dry_run,
        )
        print_success("BHI filtering completed.")
        if action == "report" or dry_run:
            print_info(f"Results: {results}")
    except Exception as e:
        print_error(f"Error during BHI filtering: {e}")


# Register a static menu for favorites
bhi_filtering_menu.__menu_options__ = {
    "1": ("Run BHI Filtering Workflow", bhi_filtering_menu),
    "0": ("Back to Main Menu", None),
}
