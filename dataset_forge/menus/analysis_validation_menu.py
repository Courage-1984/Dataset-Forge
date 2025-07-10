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
from dataset_forge.actions.analysis_actions import (
    progressive_dataset_validation,
    generate_hq_lq_dataset_report,
    find_hq_lq_scale,
    test_hq_lq_scale,
    check_consistency,
    report_dimensions,
    find_extreme_dimensions,
    verify_images,
    find_misaligned_images,
    test_aspect_ratio,
)
from dataset_forge.actions.alpha_actions import find_alpha_channels_menu
from dataset_forge.actions.corruption_actions import (
    fix_corrupted_images,
    fix_corrupted_images_hq_lq,
)
from dataset_forge.menus.bhi_filtering_menu import bhi_filtering_menu
from dataset_forge.menus import session_state
from dataset_forge.utils.input_utils import get_path_with_history
from dataset_forge.actions.outlier_detection_actions import detect_outliers
from dataset_forge.actions.report_actions import generate_rich_report
from dataset_forge.actions.quality_scoring_actions import (
    score_images_with_pyiqa,
    plot_quality_histogram,
    filter_images_by_quality,
    score_hq_lq_folders,
)


def require_hq_lq(func):
    def wrapper(*args, **kwargs):
        if not session_state.hq_folder or not session_state.lq_folder:
            print_error(
                "HQ and LQ folders must be set in the Settings menu before using this option."
            )
            return
        return func(*args, **kwargs)

    return wrapper


def comprehensive_validation_menu():
    """Sub-menu for comprehensive validation and reporting."""

    def progressive_validation_workflow():
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
        input("\nPress Enter to return to the menu...")

    def rich_reports_workflow():
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
        input("\nPress Enter to return to the menu...")

    def quality_scoring_workflow():
        print("\n=== Automated Dataset Quality Scoring ===")
        print("1. Score HQ/LQ folders")
        print("2. Score single folder")
        print("0. Return to main menu")
        choice = input("Select workflow: ")
        if choice == "1":
            hq = get_path_with_history(
                "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            lq = get_path_with_history(
                "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            score_hq_lq_folders(hq, lq)
        elif choice == "2":
            folder = get_path_with_history(
                "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            score_images_with_pyiqa(folder)
        input("\nPress Enter to return to the menu...")

    options = {
        "1": ("Run Comprehensive Validation Suite", progressive_validation_workflow),
        "2": ("Generate Detailed Report (HTML/Markdown)", rich_reports_workflow),
        "3": ("Automated Dataset Quality Scoring", quality_scoring_workflow),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Dataset Analysis & Reporting",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()


def find_fix_issues_menu():
    """Sub-menu for finding and fixing dataset issues."""

    def verify_fix_corruption():
        print("\n=== Verify & Fix Image Corruption ===")
        hq = input("Enter HQ folder path (or single folder): ").strip()
        lq = input("Enter LQ folder path (leave blank for single-folder): ").strip()
        if lq:
            fix_corrupted_images_hq_lq(hq, lq)
        else:
            fix_corrupted_images(hq)
        input("\nPress Enter to return to the menu...")

    def find_misaligned_workflow():
        print("\n=== Find Misaligned Images ===")
        hq = get_path_with_history(
            "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        find_misaligned_images(hq, lq)
        input("\nPress Enter to return to the menu...")

    def find_outliers_workflow():
        print("\n=== Find Outliers & Anomalies ===")
        print("1. HQ/LQ folder pair")
        print("2. Single folder")
        choice = input("Select mode: ")
        if choice == "1":
            hq = get_path_with_history(
                "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            lq = get_path_with_history(
                "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            detect_outliers(hq_folder=hq, lq_folder=lq)
        elif choice == "2":
            folder = get_path_with_history(
                "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            detect_outliers(single_path=folder)
        input("\nPress Enter to return to the menu...")

    options = {
        "1": ("Verify & Fix Image Corruption", verify_fix_corruption),
        "2": ("Find Misaligned Image Pairs", find_misaligned_workflow),
        "3": ("Find Outliers & Anomalies", find_outliers_workflow),
        "4": ("Find Images with Alpha Channel", find_alpha_channels_menu),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Find & Fix Issues",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()


def analyze_properties_menu():
    """Sub-menu for analyzing dataset properties."""

    def check_consistency_workflow():
        print("\n=== Check Dataset Consistency ===")
        hq = get_path_with_history(
            "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        check_consistency(hq, "HQ")
        check_consistency(lq, "LQ")
        input("\nPress Enter to return to the menu...")

    def test_aspect_ratio_workflow():
        print("\n=== Test Aspect Ratio ===")
        print("1. HQ/LQ folder pair (compare matching files)")
        print("2. Single folder (report all image aspect ratios)")
        print("3. Single image (report aspect ratio)")
        choice = input("Select mode: ")
        if choice == "1":
            hq = get_path_with_history(
                "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            lq = get_path_with_history(
                "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            test_aspect_ratio(hq_folder=hq, lq_folder=lq)
        elif choice == "2":
            folder = get_path_with_history(
                "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            test_aspect_ratio(single_path=folder)
        elif choice == "3":
            image = get_path_with_history(
                "Enter image path:", allow_hq_lq=False, allow_single_folder=False
            )
            test_aspect_ratio(single_path=image)
        input("\nPress Enter to return to the menu...")

    def find_test_scale_workflow():
        print("\n=== Find & Test HQ/LQ Scale ===")
        hq = get_path_with_history(
            "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        find_hq_lq_scale(hq, lq)
        test_hq_lq_scale(hq, lq)
        input("\nPress Enter to return to the menu...")

    def report_dimensions_workflow():
        print("\n=== Report Image Dimensions ===")
        hq = get_path_with_history(
            "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        report_dimensions(hq, "HQ")
        report_dimensions(lq, "LQ")
        find_extreme_dimensions(hq, "HQ")
        find_extreme_dimensions(lq, "LQ")
        input("\nPress Enter to return to the menu...")

    options = {
        "1": ("Check Dataset Consistency", check_consistency_workflow),
        "2": ("Check/Test Aspect Ratios", test_aspect_ratio_workflow),
        "3": ("Find & Test HQ/LQ Scale", find_test_scale_workflow),
        "4": ("Report Image Dimensions (List & Extremes)", report_dimensions_workflow),
        "5": (
            "BHI Filtering Analysis (Blockiness, HyperIQA, etc.)",
            bhi_filtering_menu,
        ),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Analyze Properties",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()


def analysis_validation_menu():
    """Main analysis and validation menu with hierarchical structure."""
    options = {
        "1": ("Run Comprehensive Validation Suite", comprehensive_validation_menu),
        "2": ("Generate Detailed Report (HTML/Markdown)", comprehensive_validation_menu),
        "3": ("Automated Dataset Quality Scoring", comprehensive_validation_menu),
        "4": ("Find & Fix Issues", find_fix_issues_menu),
        "5": ("Analyze Properties", analyze_properties_menu),
        "0": ("Back to Main Menu", None),
    }

    while True:
        action = show_menu(
            "Analysis & Validation",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action()
