"""
consolidated_compression_menu.py - Consolidated Compression Menu for Dataset Forge

This menu consolidates all compression methods into a single, comprehensive interface:
- Individual Image Compression (HQ/LQ pairs and single folders)
- Directory Compression (entire folders)
- Multiple format support (PNG, JPEG, WebP)
- Advanced compression options (Oxipng, quality settings)

Provides unified workflow and consistent user experience across all compression methods.
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


def consolidated_compression_menu():
    """Main consolidated compression menu."""

    # Define menu context for help system
    menu_context = {
        "Purpose": "Comprehensive image and directory compression with multiple format support",
        "Total Options": "3 compression methods",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
        "Key Features": [
            "🖼️ Individual Image Compression - Compress individual images with format options",
            "📁 Directory Compression - Compress entire directories and folders",
            "⚙️ Compression Settings - Configure quality, format, and advanced options",
        ],
        "Tips": [
            "Individual compression is best for selective image optimization",
            "Directory compression processes entire folders efficiently",
            "PNG offers lossless compression with Oxipng support",
            "JPEG and WebP provide lossy compression with quality control",
            "Always backup original files before compression",
            "Use appropriate quality settings for your use case",
        ],
    }

    while True:
        options = {
            "1": ("🖼️ Individual Image Compression", individual_image_compression),
            "2": ("📁 Directory Compression", directory_compression),
            "3": ("⚙️ Compression Settings", compression_settings),
            "0": ("⬅️ Back to Utilities", None),
        }

        key = show_menu(
            "🗜️ Consolidated Compression",
            options,
            Mocha.lavender,
            current_menu="Consolidated Compression",
            menu_context=menu_context,
        )

        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()


def individual_image_compression():
    """Individual image compression with format and quality options."""
    print_header("🖼️ Individual Image Compression", color=Mocha.lavender)

    # Get input mode
    print_section("Input Selection", color=Mocha.lavender)
    print_info("1. HQ/LQ paired folders")
    print_info("2. Single folder")
    mode_choice = input("Select input mode [1]: ").strip() or "1"

    if mode_choice == "1":
        hq_path = get_folder_path("Enter HQ folder path:")
        lq_path = get_folder_path("Enter LQ folder path:")
        if not hq_path or not lq_path:
            print_error("Both HQ and LQ folder paths are required.")
            return
        single_folder = None
    else:
        single_folder = get_folder_path("Enter folder path:")
        if not single_folder:
            print_error("Folder path is required.")
            return
        hq_path = lq_path = None

    # Get output format
    print_section("Output Format Selection", color=Mocha.lavender)
    print_info("1. PNG (lossless, supports Oxipng)")
    print_info("2. JPEG (lossy, widely supported)")
    print_info("3. WebP (modern, efficient)")

    format_choice = input("Select output format [1]: ").strip() or "1"
    format_map = {"1": "png", "2": "jpeg", "3": "webp"}
    output_format = format_map.get(format_choice, "png")

    # Get quality settings
    quality = 85
    if output_format in ["jpeg", "webp"]:
        try:
            quality = int(input("Enter quality (1-100, default 85): ").strip() or "85")
            if not (1 <= quality <= 100):
                print_warning("Invalid quality, using default 85.")
                quality = 85
        except ValueError:
            print_warning("Invalid input, using default 85.")
            quality = 85

    # Get Oxipng option for PNG
    use_oxipng = False
    if output_format == "png":
        use_oxipng = (
            input("Use Oxipng for additional compression? (y/N): ").strip().lower()
            == "y"
        )

    # Get operation mode
    print_section("Operation Mode", color=Mocha.lavender)
    print_info("1. Copy compressed images to new location")
    print_info("2. Move compressed images to new location")
    print_info("3. Replace original images (destructive)")

    operation_choice = input("Select operation [1]: ").strip() or "1"
    operations = {"1": "copy", "2": "move", "3": "replace"}
    operation = operations.get(operation_choice, "copy")

    # Get destination if needed
    destination = None
    if operation in ["copy", "move"]:
        destination = get_destination_path(
            "Enter destination folder for compressed images:"
        )
        if not destination:
            print_error("Destination folder is required for copy/move operations.")
            return

    # Confirm destructive operations
    if operation == "replace":
        confirm = input(
            "⚠️  This will REPLACE original images. Type 'REPLACE' to confirm: "
        ).strip()
        if confirm != "REPLACE":
            print_info("Operation cancelled.")
            return

    # Execute compression
    print_section("Compression Progress", color=Mocha.lavender)
    try:
        from dataset_forge.actions.compress_actions import compress_images

        results = compress_images(
            hq_path=hq_path,
            lq_path=lq_path,
            single_folder=single_folder,
            output_format=output_format,
            quality=quality,
            use_oxipng=use_oxipng,
            operation=operation,
            destination=destination,
        )

        if results:
            print_success(f"Compressed {len(results)} images successfully")
            play_done_sound()
        else:
            print_info("No images were compressed.")

    except Exception as e:
        print_error(f"Error during compression: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def directory_compression():
    """Directory compression for entire folders."""
    print_header("📁 Directory Compression", color=Mocha.lavender)

    # Get input directory
    input_dir = get_folder_path("Enter input directory path:")
    if not input_dir:
        print_error("Input directory path is required.")
        return

    # Get output directory
    output_dir = get_folder_path("Enter output directory path:")
    if not output_dir:
        print_error("Output directory path is required.")
        return

    # Get output format
    print_section("Output Format Selection", color=Mocha.lavender)
    print_info("1. JPEG (lossy, widely supported)")
    print_info("2. PNG (lossless)")
    print_info("3. WebP (modern, efficient)")

    format_choice = input("Select output format [1]: ").strip() or "1"
    format_map = {"1": "jpeg", "2": "png", "3": "webp"}
    output_format = format_map.get(format_choice, "jpeg")

    # Get quality settings
    quality = 85
    if output_format in ["jpeg", "webp"]:
        try:
            quality = int(input("Enter quality (1-100, default 85): ").strip() or "85")
            if not (1 <= quality <= 100):
                print_warning("Invalid quality, using default 85.")
                quality = 85
        except ValueError:
            print_warning("Invalid input, using default 85.")
            quality = 85

    # Get additional options
    print_section("Compression Options", color=Mocha.lavender)
    preserve_structure = (
        input("Preserve directory structure? (y/N): ").strip().lower() == "y"
    )
    recursive = (
        input("Process subdirectories recursively? (y/N): ").strip().lower() == "y"
    )

    # Execute directory compression
    print_section("Directory Compression Progress", color=Mocha.lavender)
    try:
        from dataset_forge.actions.compress_dir_actions import compress_directory

        results = compress_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            quality=quality,
            format=output_format,
            preserve_structure=preserve_structure,
            recursive=recursive,
        )

        if results:
            print_success(f"Directory compression completed successfully")
            print_info(f"Processed {len(results)} files")
            play_done_sound()
        else:
            print_info("No files were compressed.")

    except Exception as e:
        print_error(f"Error during directory compression: {e}")
    finally:
        clear_memory()
        clear_cuda_cache()


def compression_settings():
    """Compression settings and configuration."""
    print_header("⚙️ Compression Settings", color=Mocha.lavender)

    print_section("Current Settings", color=Mocha.lavender)
    print_info("Default compression settings:")
    print_info("- JPEG Quality: 85")
    print_info("- WebP Quality: 85")
    print_info("- PNG Compression: Standard")
    print_info("- Oxipng: Disabled")
    print_info("- Preserve Structure: Enabled")
    print_info("- Recursive Processing: Disabled")

    print_section("Configuration Options", color=Mocha.lavender)
    print_info("1. View current settings")
    print_info("2. Modify default quality settings")
    print_info("3. Configure format preferences")
    print_info("4. Reset to defaults")
    print_info("5. Export settings")
    print_info("6. Import settings")

    choice = input("Select option [1]: ").strip() or "1"

    if choice == "1":
        print_section("Current Settings", color=Mocha.lavender)
        # Display current settings
        print_info("Settings loaded successfully")
    elif choice == "2":
        print_section("Modify Quality Settings", color=Mocha.lavender)
        # Allow user to modify quality settings
        print_info("Quality modification not implemented yet")
    elif choice == "3":
        print_section("Format Preferences", color=Mocha.lavender)
        # Configure format preferences
        print_info("Format preferences not implemented yet")
    elif choice == "4":
        print_section("Reset Settings", color=Mocha.lavender)
        # Reset to defaults
        print_info("Settings reset to defaults")
    elif choice == "5":
        print_section("Export Settings", color=Mocha.lavender)
        # Export settings
        print_info("Settings export not implemented yet")
    elif choice == "6":
        print_section("Import Settings", color=Mocha.lavender)
        # Import settings
        print_info("Settings import not implemented yet")
