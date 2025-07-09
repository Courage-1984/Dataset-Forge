from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering
from dataset_forge.utils.input_utils import get_folder_path
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
)


def bhi_filtering_menu():
    print_header("BHI Filtering (Blockiness, HyperIQA, IC9600)")
    input_path = get_folder_path("Enter the path to the folder to filter: ")
    try:
        blockiness = float(input("Blockiness threshold (e.g., 0.5): ").strip())
        hyperiqa = float(input("HyperIQA threshold (e.g., 0.5): ").strip())
        ic9600 = float(input("IC9600 threshold (e.g., 0.5): ").strip())
    except ValueError:
        print_error("Invalid threshold value. Please enter a number.")
        return
    action = input("Action (move/delete/report) [move]: ").strip().lower() or "move"
    if action not in ("move", "delete", "report"):
        print_error("Invalid action. Must be 'move', 'delete', or 'report'.")
        return
    batch_size = input("Batch size [8]: ").strip()
    batch_size = int(batch_size) if batch_size.isdigit() else 8
    dry_run = input("Dry run? (y/N): ").strip().lower() == "y"
    try:
        results = run_bhi_filtering(
            input_path=input_path,
            thresholds={
                "blockiness": blockiness,
                "hyperiqa": hyperiqa,
                "ic9600": ic9600,
            },
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
