"""
fuzzy_dedup_menu.py - Fuzzy Matching De-duplication Menu for Dataset Forge

Provides:
- Fuzzy matching duplicate detection using multiple perceptual hashing algorithms
- Configurable similarity thresholds for different hash methods
- Support for single folder and HQ/LQ paired folders
- Multiple operation modes: copy, move, delete
- Integration with existing duplicate detection methods
"""

import os
from typing import Dict, List, Tuple, Optional, Any
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
from dataset_forge.utils.input_utils import (
    get_path_with_history,
    get_file_operation_choice,
    get_destination_path,
)
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache


def fuzzy_dedup_menu():
    """Main fuzzy matching de-duplication menu."""

    # Define menu context for help system
    menu_context = {
        "Purpose": "Comprehensive fuzzy matching de-duplication using multiple perceptual hashing algorithms",
        "Total Options": "6 main operations",
        "Navigation": "Use numbers 1-6 to select, 0 to go back",
        "Key Features": [
            "🔍 Fuzzy Matching De-duplication - Multi-algorithm fuzzy matching with configurable thresholds",
            "👁️ Visual De-duplication - CLIP/LPIPS based semantic duplicate detection",
            "🔐 File Hash De-duplication - Perceptual hash based exact/near-duplicate detection",
            "🔍 ImageDedup Advanced - Professional duplicate detection with multiple hash methods",
            "📊 Duplicate Analysis - Comprehensive analysis and reporting tools",
            "⚙️ Fuzzy Matching Settings - Configure thresholds and algorithms",
        ],
        "Tips": [
            "Start with Fuzzy Matching for the most comprehensive duplicate detection",
            "Use Visual De-duplication for semantic similarity detection",
            "Use File Hash for fast exact/near-duplicate detection",
            "Always test with dry run before destructive operations",
            "Configure thresholds based on your dataset characteristics",
        ],
    }

    while True:
        options = {
            "1": ("🔍 Fuzzy Matching De-duplication", fuzzy_matching_dedup),
            "2": ("👁️ Visual De-duplication", visual_dedup_action),
            "3": ("🔐 File Hash De-duplication", file_hash_dedup_action),
            "4": ("🔍 ImageDedup Advanced", imagededup_action),
            "5": ("📊 Duplicate Analysis", duplicate_analysis_action),
            "6": ("⚙️ Fuzzy Matching Settings", fuzzy_settings_action),
            "0": ("⬅️ Back to Utilities", None),
        }

        key = show_menu(
            "🔍 Fuzzy Matching De-duplication",
            options,
            Mocha.yellow,
            current_menu="Fuzzy Matching De-duplication",
            menu_context=menu_context,
        )

        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()


def fuzzy_matching_dedup():
    """Fuzzy matching de-duplication using multiple perceptual hashing algorithms."""
    print_header("🔍 Fuzzy Matching De-duplication", color=Mocha.yellow)

    # Get folder path
    print_section("Input Selection", color=Mocha.yellow)
    print_info("1. Single folder")
    print_info("2. HQ/LQ paired folders")
    mode_choice = input("Select mode [1]: ").strip() or "1"

    if mode_choice == "1":
        folder = get_path_with_history(
            "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        if not folder or not os.path.isdir(folder):
            print_error("Invalid folder path.")
            return
        hq_folder = lq_folder = None
    elif mode_choice == "2":
        hq_folder = get_path_with_history(
            "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        lq_folder = get_path_with_history(
            "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
        )
        if (
            not hq_folder
            or not lq_folder
            or not os.path.isdir(hq_folder)
            or not os.path.isdir(lq_folder)
        ):
            print_error("Invalid HQ or LQ folder path.")
            return
        folder = None
    else:
        print_error("Invalid mode selection.")
        return

    # Get hash methods
    print_section("Hash Method Selection", color=Mocha.yellow)
    print_info("Select hash methods to use (comma-separated):")
    print_info("1. pHash (perceptual hash) - Most accurate")
    print_info("2. dHash (difference hash) - Fast, good for minor changes")
    print_info("3. aHash (average hash) - Simple, fast")
    print_info("4. wHash (wavelet hash) - Good for rotation/scaling")
    print_info("5. colorHash (color distribution) - Color-based similarity")
    print_info("6. All methods (recommended)")

    method_choice = input("Select methods [6]: ").strip() or "6"

    hash_methods = {
        "1": "phash",
        "2": "dhash",
        "3": "ahash",
        "4": "whash",
        "5": "colorhash",
        "6": "all",
    }

    selected_methods = []
    if method_choice == "6":
        selected_methods = ["phash", "dhash", "ahash", "whash", "colorhash"]
    else:
        for choice in method_choice.split(","):
            choice = choice.strip()
            if choice in hash_methods:
                selected_methods.append(hash_methods[choice])

    if not selected_methods:
        print_error("No valid hash methods selected.")
        return

    # Get thresholds
    print_section("Similarity Thresholds", color=Mocha.yellow)
    print_info(
        "Enter similarity thresholds for each method (0-100, higher = more similar):"
    )
    print_info("Recommended thresholds:")
    print_info("- pHash: 85-95 (85 = very similar, 95 = nearly identical)")
    print_info("- dHash: 80-90 (80 = very similar, 90 = nearly identical)")
    print_info("- aHash: 75-85 (75 = very similar, 85 = nearly identical)")
    print_info("- wHash: 80-90 (80 = very similar, 90 = nearly identical)")
    print_info("- colorHash: 70-80 (70 = similar colors, 80 = very similar colors)")

    thresholds = {}
    for method in selected_methods:
        default_threshold = {
            "phash": 90,
            "dhash": 85,
            "ahash": 80,
            "whash": 85,
            "colorhash": 75,
        }.get(method, 80)

        try:
            threshold = input(f"Threshold for {method} [{default_threshold}]: ").strip()
            threshold = int(threshold) if threshold else default_threshold
            if 0 <= threshold <= 100:
                thresholds[method] = threshold
            else:
                print_warning(
                    f"Invalid threshold for {method}, using default {default_threshold}"
                )
                thresholds[method] = default_threshold
        except ValueError:
            print_warning(
                f"Invalid threshold for {method}, using default {default_threshold}"
            )
            thresholds[method] = default_threshold

    # Get operation
    print_section("Operation Selection", color=Mocha.yellow)
    print_info("What would you like to do with the fuzzy duplicates?")
    print_info("1. Copy to folder")
    print_info("2. Move to folder")
    print_info("3. Delete in-place")
    print_info("4. Show only (dry run)")

    operation_choice = input("Select operation [4]: ").strip() or "4"
    operations = {"1": "copy", "2": "move", "3": "delete", "4": "show"}
    operation = operations.get(operation_choice, "show")

    destination_dir = None
    if operation in ["copy", "move"]:
        destination_dir = get_destination_path()
        if not destination_dir:
            print_error("Destination directory is required for copy/move operations.")
            return

    # Confirm destructive operations
    if operation == "delete":
        print_warning("⚠️ This will permanently delete files! Are you sure?")
        confirm = input("Type 'YES' to confirm deletion: ").strip()
        if confirm != "YES":
            print_info("Operation cancelled.")
            return

    # Run fuzzy matching
    print_section("Fuzzy Matching Progress", color=Mocha.yellow)
    try:
        from dataset_forge.actions.fuzzy_dedup_actions import fuzzy_matching_workflow

        results = fuzzy_matching_workflow(
            folder=folder,
            hq_folder=hq_folder,
            lq_folder=lq_folder,
            hash_methods=selected_methods,
            thresholds=thresholds,
            operation=operation,
            destination_dir=destination_dir,
        )

        if results:
            total_groups = len(results.get("duplicate_groups", []))
            total_files = results.get("total_files_processed", 0)
            total_duplicates = results.get("total_duplicates_found", 0)

            print_success(f"Fuzzy matching completed!")
            print_info(f"Processed {total_files} files")
            print_info(f"Found {total_groups} duplicate groups")
            print_info(f"Total duplicate files: {total_duplicates}")

            if operation != "show" and total_duplicates > 0:
                print_success(
                    f"Successfully {operation}d {total_duplicates} duplicate files"
                )
                play_done_sound()

            # Show detailed results
            if results.get("duplicate_groups"):
                print_section("Duplicate Groups Found", color=Mocha.peach)
                for i, group in enumerate(results["duplicate_groups"], 1):
                    print_info(f"\nGroup {i} ({len(group)} files):")
                    for file_info in group:
                        similarity = file_info.get("similarity", "N/A")
                        method = file_info.get("method", "N/A")
                        print_info(
                            f"  - {file_info['path']} (similarity: {similarity}%, method: {method})"
                        )

        else:
            print_success("No fuzzy duplicates found!")
            play_done_sound()

    except Exception as e:
        print_error(f"Error during fuzzy matching: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def visual_dedup_action():
    """Launch visual de-duplication menu."""
    from dataset_forge.menus.visual_dedup_menu import visual_dedup_menu

    visual_dedup_menu()


def file_hash_dedup_action():
    """Launch file hash de-duplication menu."""
    from dataset_forge.menus.de_dupe_menu import de_dupe_menu

    de_dupe_menu()


def imagededup_action():
    """Launch ImageDedup advanced menu."""
    from dataset_forge.menus.imagededup_menu import imagededup_menu

    imagededup_menu()


def duplicate_analysis_action():
    """Comprehensive duplicate analysis and reporting."""
    print_header("📊 Duplicate Analysis", color=Mocha.yellow)

    # Get folder path
    folder = get_path_with_history(
        "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
    )
    if not folder or not os.path.isdir(folder):
        print_error("Invalid folder path.")
        return

    print_section("Analysis Options", color=Mocha.yellow)
    print_info("Select analysis types:")
    print_info("1. File size analysis")
    print_info("2. Hash-based analysis")
    print_info("3. Visual similarity analysis")
    print_info("4. Comprehensive analysis (all methods)")

    analysis_choice = input("Select analysis [4]: ").strip() or "4"

    try:
        from dataset_forge.actions.fuzzy_dedup_actions import (
            duplicate_analysis_workflow,
        )

        results = duplicate_analysis_workflow(
            folder=folder, analysis_type=analysis_choice
        )

        if results:
            print_section("Analysis Results", color=Mocha.peach)
            print_info(f"Total files analyzed: {results.get('total_files', 0)}")
            print_info(
                f"Potential duplicates found: {results.get('potential_duplicates', 0)}"
            )
            print_info(
                f"Storage space that could be saved: {results.get('space_savings', 'N/A')}"
            )

            # Show detailed breakdown
            if results.get("breakdown"):
                print_info("\nBreakdown by type:")
                for dup_type, count in results["breakdown"].items():
                    print_info(f"  - {dup_type}: {count}")

            # Offer to save report
            save_report = input("\nSave analysis report? (y/n) [n]: ").strip().lower()
            if save_report == "y":
                report_path = input("Enter report file path: ").strip()
                if report_path:
                    try:
                        with open(report_path, "w") as f:
                            f.write(str(results))
                        print_success(f"Report saved to {report_path}")
                    except Exception as e:
                        print_error(f"Error saving report: {e}")

        play_done_sound()

    except Exception as e:
        print_error(f"Error during analysis: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def fuzzy_settings_action():
    """Configure fuzzy matching settings."""
    print_header("⚙️ Fuzzy Matching Settings", color=Mocha.yellow)

    print_section("Current Settings", color=Mocha.yellow)
    print_info("Default similarity thresholds:")
    print_info("- pHash: 90% (nearly identical)")
    print_info("- dHash: 85% (very similar)")
    print_info("- aHash: 80% (similar)")
    print_info("- wHash: 85% (very similar)")
    print_info("- colorHash: 75% (similar colors)")

    print_section("Algorithm Information", color=Mocha.yellow)
    print_info("🔍 pHash (Perceptual Hash):")
    print_info("  - Most accurate for detecting similar images")
    print_info("  - Resistant to minor changes in brightness, contrast")
    print_info("  - Recommended threshold: 85-95%")

    print_info("\n🔍 dHash (Difference Hash):")
    print_info("  - Fast and good for detecting minor changes")
    print_info("  - Sensitive to edges and details")
    print_info("  - Recommended threshold: 80-90%")

    print_info("\n🔍 aHash (Average Hash):")
    print_info("  - Simple and fast algorithm")
    print_info("  - Less accurate but good for quick screening")
    print_info("  - Recommended threshold: 75-85%")

    print_info("\n🔍 wHash (Wavelet Hash):")
    print_info("  - Good for detecting rotation and scaling")
    print_info("  - Uses wavelet transform for analysis")
    print_info("  - Recommended threshold: 80-90%")

    print_info("\n🔍 colorHash (Color Hash):")
    print_info("  - Based on color distribution")
    print_info("  - Good for finding images with similar colors")
    print_info("  - Recommended threshold: 70-80%")

    print_section("Usage Tips", color=Mocha.yellow)
    print_info("• Start with higher thresholds (90-95%) for conservative detection")
    print_info("• Lower thresholds (70-80%) will find more potential duplicates")
    print_info("• Use multiple hash methods for comprehensive detection")
    print_info("• Always test with dry run before destructive operations")
    print_info("• Consider your dataset characteristics when setting thresholds")

    print_prompt("\n⏸️ Press Enter to return to the Fuzzy Matching menu...")
    input()


if __name__ == "__main__":
    fuzzy_dedup_menu()
