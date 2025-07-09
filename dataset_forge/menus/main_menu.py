from dataset_forge.menus.dataset_menu import dataset_menu
from dataset_forge.menus.analysis_menu import analysis_menu, require_hq_lq
from dataset_forge.menus.transform_menu import transform_menu
from dataset_forge.menus.augmentation_menu import augmentation_menu
from dataset_forge.menus.metadata_menu import metadata_menu
from dataset_forge.menus.comparison_menu import comparison_menu
from dataset_forge.menus.config_menu import config_menu
from dataset_forge.menus.settings_menu import settings_menu
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import print_info
from dataset_forge.actions.batch_rename_actions import batch_rename_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.menus import session_state
from dataset_forge.menus.compress_menu import compress_menu
from dataset_forge.menus.compress_dir_menu import compress_dir_menu
from dataset_forge.menus.links_menu import links_menu
from dataset_forge.menus.user_profile_menu import user_profile_menu
from dataset_forge.menus.correct_hq_lq_pairing_menu import (
    correct_hq_lq_pairing_menu,
    fuzzy_hq_lq_pairing_menu,
)
from dataset_forge.menus.history_log_menu import history_log_menu
from dataset_forge.menus.outlier_detection_menu import outlier_detection_menu
from dataset_forge.actions.analysis_actions import progressive_dataset_validation
from dataset_forge.utils.input_utils import get_path_with_history
from dataset_forge.actions.report_actions import generate_rich_report
from dataset_forge.menus.quality_scoring_menu import quality_scoring_menu
from dataset_forge.menus.visual_dedup_menu import visual_dedup_menu


def progressive_validation_menu():
    print("\n=== Progressive Dataset Validation ===")
    hq = get_path_with_history(
        "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
    )
    lq = get_path_with_history(
        "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
    )
    session_state.hq_folder = hq
    session_state.lq_folder = lq
    progressive_dataset_validation(hq, lq)
    input("\nPress Enter to return to the main menu...")


def rich_reports_menu():
    print("\n=== Rich Reports (HTML/Markdown) ===")
    print("Generate a detailed report with plots and sample images.")
    print("1. HQ/LQ parent_path workflow")
    print("2. Single-folder workflow")
    print("0. Return to main menu")
    choice = input("Select workflow: ")
    if choice == "1":
        hq = input("Enter HQ folder path: ")
        lq = input("Enter LQ folder path: ")
        folder = None
    elif choice == "2":
        hq = lq = None
        folder = input("Enter folder path: ")
    else:
        return
    # Output options
    format = input("Report format? (html/md) [html]: ").strip().lower() or "html"
    if format not in ("html", "md"):
        format = "html"
    output_path = input("Output path (leave blank for default): ").strip() or None
    try:
        sample_count = int(input("How many sample images? [5]: ") or "5")
    except ValueError:
        sample_count = 5
    try:
        max_quality_images = int(
            input("Max images for quality scores? [100]: ") or "100"
        )
    except ValueError:
        max_quality_images = 100
    # Generate report
    generate_rich_report(
        hq_path=hq,
        lq_path=lq,
        single_folder_path=folder,
        output_path=output_path,
        format=format,
        sample_count=sample_count,
        max_quality_images=max_quality_images,
    )
    input("\nPress Enter to return to the main menu...")


def main_menu():
    """Main menu for the Image Dataset Utility."""
    main_options = main_menu.__menu_options__
    while True:
        try:
            action = show_menu(
                "Image Dataset Utility - Main Menu",
                main_options,
                header_color=Mocha.lavender,
            )
            if action is None:
                print_info("Exiting...")
                break
            action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break


# Register a static menu for favorites
main_menu.__menu_options__ = {
    "1": ("\U0001f4c2 DATASET", dataset_menu),
    "2": ("\U0001f4ca ANALYSIS", analysis_menu),
    "3": ("\U0001f4c8 RICH REPORTS", rich_reports_menu),
    "4": ("\U0001f4a1 AUTOMATED DATASET QUALITY SCORING", quality_scoring_menu),
    "5": ("\U0001f4be PROGRESSIVE DATASET VALIDATION", progressive_validation_menu),
    "6": ("\U0001f50e OUTLIER & ANOMALY DETECTION", outlier_detection_menu),
    "7": ("\u2728 TRANSFORM", transform_menu),
    "8": ("\U0001f347 AUGMENTATION RECIPES", augmentation_menu),
    "9": ("\U0001f5c2\ufe0f  METADATA", metadata_menu),
    "10": ("\U0001f50d COMPARISON", comparison_menu),
    "11": ("\U0001f4dd BATCH RENAME", batch_rename_menu),
    "12": ("\U0001f4c1 CONFIG", config_menu),
    "13": ("\u2699\ufe0f  SETTINGS", settings_menu),
    "14": ("\U0001f4e6 COMPRESS IMAGES", compress_menu),
    "15": ("\U0001f4e6 COMPRESS DIRECTORY", compress_dir_menu),
    "16": ("\U0001f517 LINKS", links_menu),
    "17": ("\U0001f464 USER PROFILE", user_profile_menu),
    "18": ("\U0001f4d3 VIEW CHANGE/HISTORY LOG", history_log_menu),
    "19": ("\U0001f527 CORRECT/CREATE HQ LQ PAIRING", correct_hq_lq_pairing_menu),
    "20": (
        "\U0001f50a AUTOMATIC HQ/LQ PAIRING (FUZZY MATCHING)",
        fuzzy_hq_lq_pairing_menu,
    ),
    "21": (
        "\U0001f5d1\ufe0f  VISUAL DUPLICATE & NEAR-DUPLICATE DETECTION",
        visual_dedup_menu,
    ),
    "0": ("\U0001f6aa EXIT", None),
}
