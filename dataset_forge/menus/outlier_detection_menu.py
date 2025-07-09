from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import print_info, print_warning, print_prompt
from dataset_forge.utils.color import Mocha
from dataset_forge.actions.outlier_detection_actions import detect_outliers
from dataset_forge.utils.input_utils import get_path_with_history


def outlier_detection_menu():
    print_info("\nOutlier & Anomaly Detection:")
    print_info(
        "Detect images that are very different from the rest using clustering or embedding-based methods."
    )
    print_info("You can analyze:")
    print_info("  1. HQ/LQ folder pair (flag outliers in both)")
    print_info("  2. Single folder (flag outliers in one set)")
    print_info("")
    mode = input("Select mode: [1] HQ/LQ pair, [2] Single folder: ").strip()
    if mode == "1":
        hq = get_path_with_history(
            "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        detect_outliers(hq_folder=hq, lq_folder=lq)
    elif mode == "2":
        folder = get_path_with_history(
            "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        detect_outliers(single_path=folder)
    else:
        print_warning("Invalid mode selected.")
    print_prompt("\nPress Enter to return to the menu...")
    input()
