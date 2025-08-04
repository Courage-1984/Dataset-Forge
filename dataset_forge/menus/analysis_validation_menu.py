from dataset_forge.utils.color import Mocha
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
from dataset_forge.menus import session_state
from dataset_forge.utils.input_utils import get_path_with_history
from dataset_forge.utils import monitoring


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
    @monitoring.time_and_record_menu_load(func_name)
    def _action(*args, **kwargs):
        return getattr(importlib.import_module(module_path), func_name)(
            *args, **kwargs
        )

    return _action


def comprehensive_validation_menu():
    """Sub-menu for comprehensive validation and reporting."""
    from dataset_forge.utils.printing import print_header, print_section
    from dataset_forge.utils.color import Mocha

    def progressive_validation_workflow():
        print_header(
            "🔍 Progressive Dataset Validation - Input/Output Selection",
            color=Mocha.teal,
        )
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

        print_section("Progressive Validation Progress", color=Mocha.teal)
        progressive_dataset_validation(hq, lq)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    def rich_reports_workflow():
        print_header(
            "📊 Rich Reports (HTML/Markdown) - Input/Output Selection",
            color=Mocha.peach,
        )
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
        from dataset_forge.actions.report_actions import generate_rich_report

        print_section("Rich Reports Progress", color=Mocha.peach)
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
        print_header(
            "⭐ Automated Dataset Quality Scoring - Input/Output Selection",
            color=Mocha.yellow,
        )
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

            print_section("Quality Scoring Progress", color=Mocha.yellow)
            score_hq_lq_folders(hq, lq)
        elif choice == "2":
            folder = get_path_with_history(
                "📁 Enter folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            from dataset_forge.actions.quality_scoring_actions import (
                score_images_with_pyiqa,
            )

            print_section("Quality Scoring Progress", color=Mocha.yellow)
            score_images_with_pyiqa(folder)
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    options = {
        "1": ("🔍 Run Comprehensive Validation Suite", progressive_validation_workflow),
        "2": ("📊 Generate Detailed Report (HTML/Markdown)", rich_reports_workflow),
        "3": ("⭐ Automated Dataset Quality Scoring", quality_scoring_workflow),
        "0": ("⬅️  Back", None),
    }
    from dataset_forge.utils.printing import print_error

    while True:
        key = show_menu(
            "📊 Dataset Analysis & Reporting",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


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
        "0": ("⬅️  Back", None),
    }
    from dataset_forge.utils.printing import print_error

    while True:
        key = show_menu(
            "🔍 Find & Fix Issues",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


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
        print("DEBUG: Entered find_native_resolution_workflow")
        print_header("🎯 Find Native Resolution", color=Mocha.yellow)
        from dataset_forge.utils.input_utils import (
            get_path_with_history,
            get_folder_path,
        )
        from dataset_forge.utils.printing import print_info, print_warning
        from dataset_forge.utils.menu import show_menu

        # Prompt for input type
        input_type_options = {
            "1": ("📁 Folder (HQ/LQ)", "folder"),
            "2": ("🖼️ Single Image", "image"),
            "0": ("⬅️  Back", None),
        }
        while True:
            input_type = show_menu(
                "Select input type", input_type_options, Mocha.lavender
            )
            print(f"DEBUG: input_type selected: {input_type}")
            if input_type is None or input_type == "0":
                print("DEBUG: input_type is None or 0, returning")
                return
            if input_type == "1":
                hq = get_path_with_history(
                    "📁 Enter HQ folder path:",
                    allow_hq_lq=True,
                    allow_single_folder=True,
                )
                lq = get_path_with_history(
                    "📁 Enter LQ folder path:",
                    allow_hq_lq=True,
                    allow_single_folder=True,
                )
                break
            elif input_type == "2":
                while True:
                    image_path = get_path_with_history("🖼️ Enter image file path:")
                    from dataset_forge.utils.file_utils import is_image_file
                    import os

                    if os.path.isfile(image_path) and is_image_file(image_path):
                        hq = image_path
                        lq = None
                        break
                    else:
                        print_warning(
                            "Selected path is not a valid image file. Please try again."
                        )
                break
            else:
                print_warning("Invalid selection. Please try again.")

        # Prompt for method
        method_options = {
            "1": ("🧪 getnative (VapourSynth, Python)", "getnative"),
            "2": ("⚡ resdet (C binary, fast)", "resdet"),
            "0": ("⬅️  Back", None),
        }
        while True:
            method = show_menu(
                "Choose native resolution detection method",
                method_options,
                Mocha.lavender,
            )
            print(f"DEBUG: method selected: {method}")
            if method is None or method == "0":
                print("DEBUG: method is None or 0, returning")
                return
            if method == "1":
                from dataset_forge.actions.getnative_actions import (
                    find_native_resolution,
                )

                if lq is not None:
                    find_native_resolution(hq, lq)
                else:
                    find_native_resolution(hq)
                break
            elif method == "2":
                from dataset_forge.actions.getnative_actions import (
                    find_native_resolution_resdet,
                )

                if lq is not None:
                    print_info(
                        "resdet only supports single image input. Please select a single image."
                    )
                else:
                    find_native_resolution_resdet(hq)
                break
            else:
                print_warning("Invalid selection. Please try again.")

        # At the end of the workflow, after all processing:
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()

    options = {
        "1": ("🔍 Check Dataset Consistency", check_consistency_workflow),
        "2": ("📐 Check/Test Aspect Ratios", test_aspect_ratio_workflow),
        "3": ("🔍 Find & Test HQ/LQ Scale", find_test_scale_workflow),
        "4": ("📏 Report Image Dimensions", report_dimensions_workflow),
        "5": ("🎯 Find Native Resolution", find_native_resolution_workflow),
        "6": (
            "⭐ BHI Filtering Analysis",
            lazy_action("dataset_forge.menus.bhi_filtering_menu", "bhi_filtering_menu"),
        ),
        "0": ("⬅️  Back", None),
    }
    from dataset_forge.utils.printing import print_error

    # Define menu context for help system
    menu_context = {
        "Purpose": "Analyze various dataset properties and characteristics",
        "Options": "6 analysis operations available",
        "Navigation": "Use numbers 1-6 to select, 0 to go back",
        "Key Features": "Consistency checking, aspect ratio testing, scale analysis, dimension reporting",
    }

    while True:
        key = show_menu(
            "📊 Analyze Properties",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Analyze Properties",
            menu_context=menu_context,
        )
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


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
        "0": ("⬅️  Back to Main Menu", None),
    }
    from dataset_forge.utils.printing import print_error

    # Define menu context for help system
    menu_context = {
        "Purpose": "Analyze dataset quality and validate image pairs",
        "Total Options": "3 main validation categories",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
        "Key Features": "Comprehensive validation, issue detection, property analysis",
    }

    while True:
        key = show_menu(
            "🔍 Analysis & Validation",
            options,
            header_color=Mocha.lavender,
            char="=",
            current_menu="Analysis & Validation",
            menu_context=menu_context,
        )
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            return
        action = options.get(key, (None, None))[1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )
