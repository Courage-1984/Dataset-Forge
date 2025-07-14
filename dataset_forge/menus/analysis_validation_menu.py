import importlib
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
from dataset_forge.menus import session_state
from dataset_forge.utils.input_utils import get_path_with_history


def require_hq_lq(func):
    def wrapper(*args, **kwargs):
        if not session_state.hq_folder or not session_state.lq_folder:
            print_error(
                "❌ HQ and LQ folders must be set in the Settings menu before using this option."
            )
            return
        return func(*args, **kwargs)

    return wrapper


def lazy_action(module_path, func_name):
    def _action(*args, **kwargs):
        module = importlib.import_module(module_path)
        return getattr(module, func_name)(*args, **kwargs)

    return _action


def comprehensive_validation_menu():
    """Sub-menu for comprehensive validation and reporting."""

    def progressive_validation_workflow():
        print_header("🔍 Progressive Dataset Validation", color=Mocha.teal)
        hq = get_path_with_history(
            "📁 Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "📁 Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        session_state.hq_folder = hq
        session_state.lq_folder = lq
        from dataset_forge.actions.analysis_actions import (
            progressive_dataset_validation,
        )

        progressive_dataset_validation(hq, lq)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def rich_reports_workflow():
        print_header("📊 Rich Reports (HTML/Markdown)", color=Mocha.mauve)
        print_info("Generate a detailed report with plots and sample images.")
        print("1. 📂 HQ/LQ parent_path workflow")
        print("2. 📁 Single-folder workflow")
        print("0. ⬅️ Return to main menu")
        choice = input("🎯 Select workflow: ")
        if choice == "1":
            hq = input("📁 Enter HQ folder path: ")
            lq = input("📁 Enter LQ folder path: ")
            folder = None
        elif choice == "2":
            hq = lq = None
            folder = input("📁 Enter folder path: ")
        else:
            return
        # Output options
        format = input("📄 Report format? (html/md) [html]: ").strip().lower() or "html"
        if format not in ("html", "md"):
            format = "html"
        output_path = (
            input("📁 Output path (leave blank for default): ").strip() or None
        )
        try:
            sample_count = int(input("🖼️ How many sample images? [5]: ") or "5")
        except ValueError:
            sample_count = 5
        try:
            max_quality_images = int(
                input("📊 Max images for quality scores? [100]: ") or "100"
            )
        except ValueError:
            max_quality_images = 100
        # Generate report
        from dataset_forge.actions.report_actions import generate_rich_report

        generate_rich_report(
            hq_path=hq,
            lq_path=lq,
            single_folder_path=folder,
            output_path=output_path,
            format=format,
            sample_count=sample_count,
            max_quality_images=max_quality_images,
        )
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def quality_scoring_workflow():
        print_header("⭐ Automated Dataset Quality Scoring", color=Mocha.yellow)
        print("1. 📊 Score HQ/LQ folders")
        print("2. 📁 Score single folder")
        print("0. ⬅️ Return to main menu")
        choice = input("🎯 Select workflow: ")
        if choice == "1":
            hq = get_path_with_history(
                "📁 Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            lq = get_path_with_history(
                "📁 Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            from dataset_forge.actions.quality_scoring_actions import (
                score_hq_lq_folders,
            )

            score_hq_lq_folders(hq, lq)
        elif choice == "2":
            folder = get_path_with_history(
                "📁 Enter folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            from dataset_forge.actions.quality_scoring_actions import (
                score_images_with_pyiqa,
            )

            score_images_with_pyiqa(folder)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    options = {
        "1": ("🔍 Run Comprehensive Validation Suite", progressive_validation_workflow),
        "2": ("📊 Generate Detailed Report (HTML/Markdown)", rich_reports_workflow),
        "3": ("⭐ Automated Dataset Quality Scoring", quality_scoring_workflow),
        "0": ("⬅️ Back", None),
    }

    while True:
        action = show_menu(
            "📊 Dataset Analysis & Reporting",
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
        print_header("🔧 Verify & Fix Image Corruption", color=Mocha.red)
        hq = input("📁 Enter HQ folder path (or single folder): ").strip()
        lq = input("📁 Enter LQ folder path (leave blank for single-folder): ").strip()
        if lq:
            from dataset_forge.actions.corruption_actions import (
                fix_corrupted_images_hq_lq,
            )

            fix_corrupted_images_hq_lq(hq, lq)
        else:
            from dataset_forge.actions.corruption_actions import fix_corrupted_images

            fix_corrupted_images(hq)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def find_misaligned_workflow():
        print_header("🔍 Find Misaligned Images", color=Mocha.peach)
        hq = get_path_with_history(
            "📁 Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "📁 Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        from dataset_forge.actions.analysis_actions import find_misaligned_images

        find_misaligned_images(hq, lq)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def find_outliers_workflow():
        print_header("🎯 Find Outliers & Anomalies", color=Mocha.maroon)
        print("1. 📂 HQ/LQ folder pair")
        print("2. 📁 Single folder")
        choice = input("🎯 Select mode: ")
        if choice == "1":
            hq = get_path_with_history(
                "📁 Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            lq = get_path_with_history(
                "📁 Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            from dataset_forge.actions.outlier_detection_actions import detect_outliers

            detect_outliers(hq_folder=hq, lq_folder=lq)
        elif choice == "2":
            folder = get_path_with_history(
                "📁 Enter folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            detect_outliers(single_path=folder)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def find_alpha_channels_menu():
        print_header("🖼️ Find Images with Alpha Channel", color=Mocha.sky)
        folder = get_path_with_history(
            "📁 Enter folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        from dataset_forge.actions.alpha_actions import find_alpha_channels_menu

        find_alpha_channels_menu(folder)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    options = {
        "1": ("🔧 Verify & Fix Image Corruption", verify_fix_corruption),
        "2": ("🔍 Find Misaligned Image Pairs", find_misaligned_workflow),
        "3": ("🎯 Find Outliers & Anomalies", find_outliers_workflow),
        "4": ("🖼️ Find Images with Alpha Channel", find_alpha_channels_menu),
        "0": ("⬅️ Back", None),
    }

    while True:
        action = show_menu(
            "🔍 Find & Fix Issues",
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
        print_header("🔍 Check Dataset Consistency", color=Mocha.teal)
        hq = get_path_with_history(
            "📁 Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "📁 Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        from dataset_forge.actions.analysis_actions import check_consistency

        check_consistency(hq, lq)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def test_aspect_ratio_workflow():
        print_header("📐 Check/Test Aspect Ratios", color=Mocha.sky)
        hq = get_path_with_history(
            "📁 Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "📁 Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        from dataset_forge.actions.analysis_actions import test_aspect_ratio

        test_aspect_ratio(hq, lq)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def find_test_scale_workflow():
        print_header("🔍 Find & Test HQ/LQ Scale", color=Mocha.mauve)
        hq = get_path_with_history(
            "📁 Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "📁 Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        from dataset_forge.actions.analysis_actions import (
            find_hq_lq_scale,
            test_hq_lq_scale,
        )

        find_hq_lq_scale(hq, lq)
        test_hq_lq_scale(hq, lq)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def report_dimensions_workflow():
        print_header("📏 Report Image Dimensions", color=Mocha.peach)
        hq = get_path_with_history(
            "📁 Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "📁 Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        from dataset_forge.actions.analysis_actions import (
            report_dimensions,
            find_extreme_dimensions,
        )

        report_dimensions(hq, lq)
        find_extreme_dimensions(hq, lq)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def find_native_resolution_workflow():
        print_header("🎯 Find Native Resolution", color=Mocha.yellow)
        hq = get_path_with_history(
            "📁 Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq = get_path_with_history(
            "📁 Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        from dataset_forge.actions.getnative_actions import find_native_resolution

        find_native_resolution(hq, lq)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    options = {
        "1": ("🔍 Check Dataset Consistency", check_consistency_workflow),
        "2": ("📐 Check/Test Aspect Ratios", test_aspect_ratio_workflow),
        "3": ("🔍 Find & Test HQ/LQ Scale", find_test_scale_workflow),
        "4": ("📏 Report Image Dimensions", report_dimensions_workflow),
        "5": ("🎯 Find Native Resolution", find_native_resolution_workflow),
        "6": ("⭐ BHI Filtering Analysis", lazy_action(__name__, "bhi_filtering_menu")),
        "0": ("⬅️ Back", None),
    }

    while True:
        action = show_menu(
            "📊 Analyze Properties",
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
        "1": (
            "🔍 Run Comprehensive Validation Suite",
            lazy_action(__name__, "comprehensive_validation_menu"),
        ),
        "2": ("🔧 Find & Fix Issues", lazy_action(__name__, "find_fix_issues_menu")),
        "3": (
            "🧪 Analyze Properties",
            lazy_action(__name__, "analyze_properties_menu"),
        ),
        "0": ("⬅️ Back to Main Menu", None),
    }

    while True:
        action = show_menu(
            "Analysis & Validation Menu",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action()
