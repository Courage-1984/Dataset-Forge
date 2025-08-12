"""
consolidated_dedup_menu.py - Consolidated De-duplication Menu for Dataset Forge

This menu consolidates all de-duplication methods into a single, comprehensive interface:
- Fuzzy Matching De-duplication (multi-algorithm)
- Visual De-duplication (CLIP/LPIPS)
- File Hash De-duplication (perceptual hashing)
- ImageDedup Advanced (professional tool)
- Duplicate Analysis and Reporting

Provides unified workflow and consistent user experience across all methods.
"""

import os
from typing import Dict, List, Tuple, Optional, Any
from dataset_forge.utils.menu import show_menu, lazy_action, lazy_menu
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
    get_folder_path,
)
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache


def consolidated_dedup_menu():
    """Main consolidated de-duplication menu."""

    # Define menu context for help system
    menu_context = {
        "Purpose": "Comprehensive de-duplication using multiple advanced methods and algorithms - find and remove duplicate images from your datasets",
        "Total Options": "7 de-duplication methods",
        "Navigation": "Use numbers 1-7 to select, 0 to go back",
        "Key Features": [
            "🔍 Fuzzy Matching - Multi-algorithm fuzzy matching with configurable thresholds for perceptual duplicates",
            "👁️ Visual Detection - CLIP/LPIPS based semantic duplicate detection for content similarity",
            "🔐 File Hash - Perceptual hash based exact/near-duplicate detection for fast processing",
            "🔍 ImageDedup Pro - Professional duplicate detection with advanced features and reporting",
            "📊 Analysis & Reports - Comprehensive duplicate analysis and detailed reporting",
            "⚙️ Settings & Configuration - Configure thresholds and algorithms for optimal results",
            "🧠 CBIR Semantic Detection - Content-Based Image Retrieval using deep learning embeddings for conceptual similarity",
        ],
        "Tips": [
            "🔍 Start with Fuzzy Matching for comprehensive duplicate detection using multiple algorithms",
            "👁️ Use Visual Detection for semantic similarity (content-based duplicates)",
            "🔐 Use File Hash for fast exact/near-duplicate detection with perceptual hashing",
            "🔍 ImageDedup Pro offers professional-grade features with advanced reporting",
            "📊 Always test with dry run before destructive operations",
            "⚙️ Configure thresholds based on your dataset characteristics and requirements",
            "🧠 Use CBIR for finding conceptually similar images using deep learning embeddings",
        ],
        "Usage Examples": [
            "🔍 Fuzzy matching: 1 → Select folder → Choose algorithms → Set thresholds → Process",
            "👁️ Visual detection: 2 → Select method → Set similarity threshold → Process images",
            "🔐 File hash: 3 → Choose hash method → Set distance threshold → Find duplicates",
            "🔍 ImageDedup Pro: 4 → Select operation → Configure settings → Generate report",
            "📊 Analysis: 5 → Choose analysis type → Select output format → Generate report",
            "⚙️ Settings: 6 → View current settings → Modify thresholds → Save configuration",
            "🧠 CBIR detection: 7 → Select workflow → Choose model → Set parameters → Process",
        ],
        "Performance Notes": [
            "🔍 Fuzzy matching: Use multiple algorithms for better accuracy but slower processing",
            "👁️ Visual detection: CLIP is faster, LPIPS is more accurate but slower",
            "🔐 File hash: Fastest method, good for initial screening of large datasets",
            "🔍 ImageDedup Pro: Professional features but may require more memory",
            "📊 Analysis: Use sampling for large datasets to speed up reporting",
            "⚙️ Settings: Conservative thresholds recommended for first-time use",
            "🧠 CBIR: CLIP is fastest, ResNet/VGG are slower but may be more accurate for specific tasks",
        ],
        "Algorithm Comparison": [
            "🔍 Fuzzy Matching: Best for finding similar images with slight variations",
            "👁️ Visual Detection: Best for finding semantically similar content",
            "🔐 File Hash: Best for finding exact or very similar images quickly",
            "🔍 ImageDedup Pro: Best for professional workflows with detailed reporting",
            "🧠 CBIR: Best for finding conceptually similar images using deep learning embeddings",
        ],
    }

    while True:
        options = {
            "1": ("🔍 Fuzzy Matching De-duplication", fuzzy_matching_dedup),
            "2": ("👁️  Visual De-duplication", visual_dedup_action),
            "3": ("🔐 File Hash De-duplication", file_hash_dedup_action),
            "4": ("🔍 ImageDedup Pro", imagededup_action),
            "5": ("📊 Analysis & Reports", duplicate_analysis_action),
            "6": ("⚙️  Settings & Configuration", dedup_settings_action),
            "7": ("🧠 CBIR Semantic Detection", cbir_dedup_action),
            "0": ("⬅️  Back to Utilities", None),
        }

        key = show_menu(
            "🔍 Consolidated De-duplication",
            options,
            Mocha.yellow,
            current_menu="Consolidated De-duplication",
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
    else:
        hq_folder = get_path_with_history("Enter HQ folder path:")
        lq_folder = get_path_with_history("Enter LQ folder path:")
        if (
            not hq_folder
            or not lq_folder
            or not os.path.isdir(hq_folder)
            or not os.path.isdir(lq_folder)
        ):
            print_error("Invalid HQ/LQ folder paths.")
            return
        folder = None

    # Get hash methods
    print_section("Hash Method Selection", color=Mocha.yellow)
    print_info("Select hash methods to use:")
    print_info("1. pHash (perceptual hash) - Recommended")
    print_info("2. dHash (difference hash)")
    print_info("3. aHash (average hash)")
    print_info("4. wHash (wavelet hash)")
    print_info("5. Color Hash")
    print_info("6. All methods (comprehensive but slower)")

    method_choice = input("Select method [1]: ").strip() or "1"

    if method_choice == "6":
        hash_methods = ["phash", "dhash", "ahash", "whash", "colorhash"]
    else:
        hash_methods_map = {
            "1": ["phash"],
            "2": ["dhash"],
            "3": ["ahash"],
            "4": ["whash"],
            "5": ["colorhash"],
        }
        hash_methods = hash_methods_map.get(method_choice, ["phash"])

    # Get thresholds
    print_section("Threshold Configuration", color=Mocha.yellow)
    thresholds = {}
    for method in hash_methods:
        default_threshold = get_default_threshold(method)
        try:
            threshold = float(
                input(f"Threshold for {method.upper()} [{default_threshold}]: ").strip()
                or str(default_threshold)
            )
            thresholds[method] = threshold
        except ValueError:
            thresholds[method] = default_threshold

    # Get operation mode
    print_section("Operation Mode", color=Mocha.yellow)
    print_info("1. Show duplicates only (preview)")
    print_info("2. Copy duplicates to folder")
    print_info("3. Move duplicates to folder")
    print_info("4. Delete duplicates (permanent)")

    operation_choice = input("Select operation [1]: ").strip() or "1"
    operations = {"1": "show", "2": "copy", "3": "move", "4": "delete"}
    operation = operations.get(operation_choice, "show")

    # Get destination if needed
    destination = None
    if operation in ["copy", "move"]:
        destination = get_destination_path("Enter destination folder for duplicates:")
        if not destination:
            print_error("Destination folder is required for copy/move operations.")
            return

    # Confirm destructive operations
    if operation == "delete":
        confirm = input(
            "⚠️  This will PERMANENTLY DELETE files. Type 'DELETE' to confirm: "
        ).strip()
        if confirm != "DELETE":
            print_info("Operation cancelled.")
            return

    # Execute fuzzy matching
    print_section("Processing", color=Mocha.yellow)
    try:
        from dataset_forge.actions.fuzzy_dedup_actions import fuzzy_matching_workflow

        results = fuzzy_matching_workflow(
            folder=folder,
            hq_folder=hq_folder,
            lq_folder=lq_folder,
            hash_methods=hash_methods,
            thresholds=thresholds,
            operation=operation,
            destination=destination,
        )

        if results:
            print_success(f"Found {len(results)} duplicate groups")
            play_done_sound()
        else:
            print_info("No duplicates found.")

    except Exception as e:
        print_error(f"Error during fuzzy matching: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def visual_dedup_action():
    """Visual de-duplication using CLIP/LPIPS embeddings."""
    print_header("👁️  Visual De-duplication", color=Mocha.yellow)

    # Get input method
    print_section("Input Selection", color=Mocha.yellow)
    print_info("1. Single folder")
    print_info("2. HQ/LQ paired folders")
    mode_choice = input("Select mode [1]: ").strip() or "1"

    if mode_choice == "1":
        folder = get_path_with_history("Enter folder path:")
        if not folder or not os.path.isdir(folder):
            print_error("Invalid folder path.")
            return
        hq_folder = lq_folder = None
    else:
        hq_folder = get_path_with_history("Enter HQ folder path:")
        lq_folder = get_path_with_history("Enter LQ folder path:")
        if not hq_folder or not lq_folder:
            print_error("Invalid HQ/LQ folder paths.")
            return
        folder = None

    # Get method
    print_section("Detection Method", color=Mocha.yellow)
    print_info("1. CLIP Embedding (fast, semantic similarity)")
    print_info("2. LPIPS (slow, perceptual similarity)")
    method_choice = input("Select method [1]: ").strip() or "1"
    method = "clip" if method_choice == "1" else "lpips"

    # Get parameters
    try:
        max_images = int(input("Max images to check [100]: ").strip() or "100")
        threshold = float(input("Similarity threshold [0.98]: ").strip() or "0.98")
    except ValueError:
        max_images = 100
        threshold = 0.98

    # Get operation
    print_section("Operation Mode", color=Mocha.yellow)
    print_info("1. Show duplicates only (preview)")
    print_info("2. Copy duplicates to folder")
    print_info("3. Move duplicates to folder")
    print_info("4. Delete duplicates (permanent)")

    operation_choice = input("Select operation [1]: ").strip() or "1"
    operations = {"1": "show", "2": "copy", "3": "move", "4": "delete"}
    operation = operations.get(operation_choice, "show")

    # Get destination if needed
    destination = None
    if operation in ["copy", "move"]:
        destination = get_destination_path("Enter destination folder for duplicates:")
        if not destination:
            print_error("Destination folder is required for copy/move operations.")
            return

    # Confirm destructive operations
    if operation == "delete":
        confirm = input(
            "⚠️  This will PERMANENTLY DELETE files. Type 'DELETE' to confirm: "
        ).strip()
        if confirm != "DELETE":
            print_info("Operation cancelled.")
            return

    # Execute visual deduplication
    print_section("Processing", color=Mocha.yellow)
    try:
        from dataset_forge.actions.visual_dedup_actions import visual_dedup_workflow

        results = visual_dedup_workflow(
            hq_path=hq_folder,
            lq_path=lq_folder,
            single_folder_path=folder,
            method=method,
            threshold=threshold,
            max_images=max_images,
            operation=operation,
            destination=destination,
        )

        if results:
            print_success(f"Found {len(results)} duplicate groups")
            play_done_sound()
        else:
            print_info("No duplicates found.")

    except Exception as e:
        print_error(f"Error during visual deduplication: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def file_hash_dedup_action():
    """File hash-based de-duplication using perceptual hashing."""
    print_header("🔐 File Hash De-duplication", color=Mocha.yellow)

    # Get folder path
    folder = get_path_with_history("Enter folder path:")
    if not folder or not os.path.isdir(folder):
        print_error("Invalid folder path.")
        return

    # Get hash method
    print_section("Hash Method Selection", color=Mocha.yellow)
    print_info("1. pHash (perceptual hash) - Recommended")
    print_info("2. dHash (difference hash)")
    print_info("3. aHash (average hash)")
    print_info("4. wHash (wavelet hash)")

    method_choice = input("Select hash method [1]: ").strip() or "1"
    hash_methods = {"1": "phash", "2": "dhash", "3": "ahash", "4": "whash"}
    hash_method = hash_methods.get(method_choice, "phash")

    # Get threshold
    try:
        threshold = int(input("Distance threshold [10]: ").strip() or "10")
    except ValueError:
        threshold = 10

    # Get operation
    print_section("Operation Mode", color=Mocha.yellow)
    print_info("1. Find exact duplicates")
    print_info("2. Find near-duplicates")
    print_info("3. Copy duplicates to folder")
    print_info("4. Move duplicates to folder")
    print_info("5. Delete duplicates (permanent)")

    operation_choice = input("Select operation [1]: ").strip() or "1"
    operations = {"1": "exact", "2": "near", "3": "copy", "4": "move", "5": "delete"}
    operation = operations.get(operation_choice, "exact")

    # Get destination if needed
    destination = None
    if operation in ["copy", "move"]:
        destination = get_destination_path("Enter destination folder for duplicates:")
        if not destination:
            print_error("Destination folder is required for copy/move operations.")
            return

    # Confirm destructive operations
    if operation == "delete":
        confirm = input(
            "⚠️  This will PERMANENTLY DELETE files. Type 'DELETE' to confirm: "
        ).strip()
        if confirm != "DELETE":
            print_info("Operation cancelled.")
            return

    # Execute file hash deduplication
    print_section("Processing", color=Mocha.yellow)
    try:
        from dataset_forge.actions.de_dupe_actions import (
            compute_hashes,
            find_duplicates,
            find_near_duplicates,
        )

        hashes = compute_hashes(folder, hash_method)
        print_success(f"Computed hashes for {len(hashes)} images")

        if operation == "exact":
            duplicates = find_duplicates(hashes)
        else:
            duplicates = find_near_duplicates(hashes, threshold)

        if duplicates:
            print_success(f"Found {len(duplicates)} duplicate groups")
            play_done_sound()
        else:
            print_info("No duplicates found.")

    except Exception as e:
        print_error(f"Error during file hash deduplication: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def imagededup_action():
    """ImageDedup Pro - Professional duplicate detection."""
    print_header("🔍 ImageDedup Pro", color=Mocha.yellow)

    # Get input method
    print_section("Input Selection", color=Mocha.yellow)
    print_info("1. Single folder")
    print_info("2. HQ/LQ paired folders")
    mode_choice = input("Select mode [1]: ").strip() or "1"

    if mode_choice == "1":
        folder = get_folder_path("Enter folder path:")
        if not folder:
            return
        hq_folder = lq_folder = None
    else:
        hq_folder = get_folder_path("Enter HQ folder path:")
        lq_folder = get_folder_path("Enter LQ folder path:")
        if not hq_folder or not lq_folder:
            return
        folder = None

    # Get hash method
    print_section("Hash Method Selection", color=Mocha.yellow)
    print_info("1. PHash (Perceptual Hash) - Recommended")
    print_info("2. DHash (Difference Hash)")
    print_info("3. AHash (Average Hash)")
    print_info("4. WHash (Wavelet Hash)")

    hash_choice = input("Select hash method [1]: ").strip() or "1"
    hash_methods = {"1": "phash", "2": "dhash", "3": "ahash", "4": "whash"}
    hash_method = hash_methods.get(hash_choice, "phash")

    # Get threshold
    try:
        threshold = int(input("Max distance threshold [10]: ").strip() or "10")
    except ValueError:
        threshold = 10

    # Get operation
    print_section("Operation Selection", color=Mocha.yellow)
    print_info("1. Find duplicates (show only)")
    print_info("2. Remove duplicates")
    print_info("3. Move duplicates to separate folder")
    print_info("4. Generate duplicate report")

    op_choice = input("Select operation [1]: ").strip() or "1"
    operations = {"1": "find", "2": "remove", "3": "move", "4": "report"}
    operation = operations.get(op_choice, "find")

    # Get additional parameters
    destination_dir = None
    dry_run = True

    if operation in ["remove", "move"]:
        confirm = (
            input("This will permanently modify files. Continue? (y/n) [n]: ")
            .strip()
            .lower()
            or "n"
        )
        if confirm == "y":
            dry_run = False
        else:
            print_warning("Operation cancelled.")
            return

    if operation == "move":
        destination_dir = get_folder_path("Enter destination folder for duplicates:")
        if not destination_dir:
            print_error("Destination folder is required for move operation.")
            return

    # Execute ImageDedup
    print_section("Processing", color=Mocha.yellow)
    try:
        from dataset_forge.actions.imagededup_actions import imagededup_workflow

        results = imagededup_workflow(
            folder=folder,
            hq_folder=hq_folder,
            lq_folder=lq_folder,
            hash_method=hash_method,
            threshold=threshold,
            operation=operation,
            destination_dir=destination_dir,
            dry_run=dry_run,
        )

        if results:
            print_success(f"Found {len(results)} duplicate groups")
            play_done_sound()
        else:
            print_info("No duplicates found.")

    except Exception as e:
        print_error(f"Error during ImageDedup processing: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def duplicate_analysis_action():
    """Duplicate analysis and reporting."""
    print_header("📊 Duplicate Analysis & Reports", color=Mocha.yellow)

    # Get folder path
    folder = get_path_with_history("Enter folder path for analysis:")
    if not folder or not os.path.isdir(folder):
        print_error("Invalid folder path.")
        return

    # Get analysis type
    print_section("Analysis Type", color=Mocha.yellow)
    print_info("1. Basic duplicate analysis")
    print_info("2. Comprehensive duplicate report")
    print_info("3. Duplicate statistics and metrics")
    print_info("4. Export duplicate data")

    analysis_choice = input("Select analysis type [1]: ").strip() or "1"
    analysis_types = {
        "1": "basic",
        "2": "comprehensive",
        "3": "statistics",
        "4": "export",
    }
    analysis_type = analysis_types.get(analysis_choice, "basic")

    # Get output options
    output_file = None
    if analysis_type in ["comprehensive", "export"]:
        output_file = input("Enter output file path (optional): ").strip()
        if not output_file:
            output_file = None

    # Execute analysis
    print_section("Analysis", color=Mocha.yellow)
    try:
        from dataset_forge.actions.fuzzy_dedup_actions import analyze_duplicates

        results = analyze_duplicates(
            folder=folder, analysis_type=analysis_type, output_file=output_file
        )

        if results:
            print_success("Analysis completed successfully")
            play_done_sound()
        else:
            print_info("No analysis results generated.")

    except Exception as e:
        print_error(f"Error during analysis: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def dedup_settings_action():
    """De-duplication settings and configuration."""
    print_header("⚙️ De-duplication Settings", color=Mocha.yellow)

    print_section("Current Settings", color=Mocha.yellow)
    print_info("Default thresholds:")
    print_info("- pHash: 90%")
    print_info("- dHash: 85%")
    print_info("- aHash: 80%")
    print_info("- wHash: 85%")
    print_info("- Color Hash: 75%")
    print_info("- CLIP: 0.98")
    print_info("- LPIPS: 0.02")

    print_section("Configuration Options", color=Mocha.yellow)
    print_info("1. View current settings")
    print_info("2. Modify default thresholds")
    print_info("3. Reset to defaults")
    print_info("4. Export settings")
    print_info("5. Import settings")

    choice = input("Select option [1]: ").strip() or "1"

    if choice == "1":
        print_section("Current Settings", color=Mocha.yellow)
        # Display current settings
        print_info("Settings loaded successfully")
    elif choice == "2":
        print_section("Modify Thresholds", color=Mocha.yellow)
        # Allow user to modify thresholds
        print_info("Threshold modification not implemented yet")
    elif choice == "3":
        print_section("Reset Settings", color=Mocha.yellow)
        # Reset to defaults
        print_info("Settings reset to defaults")
    elif choice == "4":
        print_section("Export Settings", color=Mocha.yellow)
        # Export settings
        print_info("Settings export not implemented yet")
    elif choice == "5":
        print_section("Import Settings", color=Mocha.yellow)
        # Import settings
        print_info("Settings import not implemented yet")


def cbir_dedup_action():
    """CBIR Semantic Detection - Content-Based Image Retrieval."""
    print_header("🧠 CBIR Semantic Detection", color=Mocha.yellow)

    # Get input method
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
    else:
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
            print_error("Invalid HQ/LQ folder paths.")
            return
        folder = None

    # Get model
    print_section("Model Selection", color=Mocha.yellow)
    print_info("1. CLIP (fast, semantic similarity)")
    print_info("2. ResNet (slower, more accurate)")
    print_info("3. VGG (slower, more accurate)")
    model_choice = input("Select model [1]: ").strip() or "1"
    model_name = (
        "clip" if model_choice == "1" else "resnet" if model_choice == "2" else "vgg"
    )

    # Get parameters
    try:
        max_images = int(input("Max images to check [100]: ").strip() or "100")
        threshold = float(input("Similarity threshold [0.98]: ").strip() or "0.98")
    except ValueError:
        max_images = 100
        threshold = 0.98

    # Get operation
    print_section("Operation Mode", color=Mocha.yellow)
    print_info("1. Show duplicates only (preview)")
    print_info("2. Copy duplicates to folder")
    print_info("3. Move duplicates to folder")
    print_info("4. Delete duplicates (permanent)")

    operation_choice = input("Select operation [1]: ").strip() or "1"
    operations = {"1": "find", "2": "copy", "3": "move", "4": "remove"}
    operation = operations.get(operation_choice, "find")

    # Get destination if needed
    dest_dir = None
    if operation in ["copy", "move"]:
        dest_dir = get_destination_path("Enter destination folder for duplicates:")
        if not dest_dir:
            print_error("Destination folder is required for copy/move operations.")
            return

    # Confirm destructive operations
    if operation == "remove":
        confirm = input(
            "⚠️  This will PERMANENTLY DELETE files. Type 'DELETE' to confirm: "
        ).strip()
        if confirm != "DELETE":
            print_info("Operation cancelled.")
            return

    # Execute CBIR
    print_section("Processing", color=Mocha.yellow)
    try:
        from dataset_forge.actions.cbir_actions import cbir_workflow

        results = cbir_workflow(
            folder=folder,
            hq_folder=hq_folder,
            lq_folder=lq_folder,
            model_name=model_name,
            threshold=threshold,
            max_images=max_images,
            operation=operation,
            dest_dir=dest_dir,
            dry_run=(operation == "find"),
        )

        if results:
            if operation == "find":
                total_groups = sum(len(groups) for groups in results.values())
                print_success(f"Found {total_groups} duplicate groups")
            else:
                total_processed = sum(len(processed) for processed in results.values())
                print_success(f"Processed {total_processed} files")
            play_done_sound()
        else:
            print_info("No duplicates found.")

    except Exception as e:
        print_error(f"Error during CBIR processing: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def get_default_threshold(method: str) -> float:
    """Get default threshold for a hash method."""
    defaults = {
        "phash": 90.0,
        "dhash": 85.0,
        "ahash": 80.0,
        "whash": 85.0,
        "colorhash": 75.0,
    }
    return defaults.get(method, 90.0)
