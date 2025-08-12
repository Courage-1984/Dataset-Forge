"""
DPID (Detail-Preserving Image Downscaling) Actions for Dataset Forge.

This module provides comprehensive DPID downscaling functionality with support for:
- Umzi's DPID (pepedpid)
- Phhofm DPID
- BasicSR DPID
- OpenMMLab DPID

All methods support both single folder and HQ/LQ paired folder processing.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union, Tuple
import numpy as np
from PIL import Image
import cv2

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
    get_folder_path,
    get_destination_path,
    ask_float,
    ask_int,
    ask_yes_no,
)
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.menus import session_state
from dataset_forge.utils.progress_utils import smart_map
from dataset_forge.utils.menu import show_menu
from tqdm import tqdm


def dpid_menu():
    """Main DPID downscaling menu with all available methods."""
    print_header("🔽 DPID Detail-Preserving Image Downscaling", Mocha.mauve)

    options = {
        "1": ("🐸 Umzi's DPID (pepedpid)", umzi_dpid_menu),
        "2": ("🔧 Phhofm DPID", phhofm_dpid_menu),
        "3": ("⚡ BasicSR DPID", basicsr_dpid_menu),
        "4": ("🚀 OpenMMLab DPID", openmmlab_dpid_menu),
        "5": ("📊 DPID Method Comparison", compare_dpid_methods),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Detail-Preserving Image Downscaling using advanced algorithms",
        "Total Options": "5 DPID methods and comparison",
        "Navigation": "Use numbers 1-5 to select, 0 to go back",
        "Key Features": [
            "🐸 Umzi's DPID - Fast and efficient detail-preserving downscaling",
            "🔧 Phhofm DPID - Advanced DPID implementation with custom parameters",
            "⚡ BasicSR DPID - Optimized for super-resolution training data",
            "🚀 OpenMMLab DPID - High-quality downscaling for research",
            "📊 Method Comparison - Compare different DPID approaches",
        ],
        "Tips": [
            "🐸 Umzi's DPID is recommended for most use cases (fast and reliable)",
            "🔧 Phhofm DPID offers more control over downscaling parameters",
            "⚡ BasicSR DPID is optimized for super-resolution model training",
            "🚀 OpenMMLab DPID provides high-quality results for research",
            "📊 Use comparison to choose the best method for your dataset",
            "💡 DPID preserves image details better than standard downscaling",
            "⚙️ Adjust lambda parameters to control detail preservation vs smoothing",
            "🎨 All methods now support alpha channels (RGBA images)",
        ],
        "Technical Notes": [
            "DPID uses inverse joint bilateral filtering for detail preservation",
            "Lambda parameter controls detail preservation (0=smooth, 1=detail)",
            "All methods support both single folder and HQ/LQ paired processing",
            "Memory usage scales with image size and batch processing",
            "GPU acceleration available for BasicSR and OpenMMLab methods",
            "Alpha channels are preserved and processed separately from RGB channels",
            "RGBA images are automatically detected and handled correctly",
        ],
    }

    while True:
        try:
            key = show_menu(
                "🔽 DPID Detail-Preserving Image Downscaling",
                options,
                Mocha.mauve,
                current_menu="DPID Downscaling",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting DPID menu...")
            break


def umzi_dpid_menu():
    """Umzi's DPID downscaling menu."""
    print_header("🐸 Umzi's DPID (pepedpid) Downscaling", Mocha.green)

    try:
        from pepedpid import dpid_resize
    except ImportError:
        print_error(
            "❌ pepedpid is not installed. Please install it with: pip install pepedpid"
        )
        print_info("💡 You can install it from: https://github.com/umzi2/pepedpid")
        return

    options = {
        "1": ("📁 Single Folder Processing", umzi_dpid_single_folder),
        "2": ("🔗 HQ/LQ Paired Processing", umzi_dpid_hq_lq_pairs),
        "3": ("⚙️ Configure Parameters", configure_umzi_dpid_params),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Umzi's DPID implementation using pepedpid library",
        "Options": "3 processing modes available",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
        "Key Features": [
            "📁 Single Folder Processing - Process all images in one folder",
            "🔗 HQ/LQ Paired Processing - Process matching HQ/LQ image pairs",
            "⚙️ Configure Parameters - Set lambda and other DPID parameters",
        ],
        "Tips": [
            "🐸 Umzi's DPID is fast and memory-efficient",
            "💡 Lambda controls detail preservation (0.5 is recommended)",
            "📊 Supports multiple scale factors in one operation",
            "🔄 Use HQ/LQ processing for super-resolution training data",
            "🎨 Supports alpha channels (RGBA images) automatically",
        ],
    }

    while True:
        try:
            key = show_menu(
                "🐸 Umzi's DPID (pepedpid)",
                options,
                Mocha.green,
                current_menu="Umzi's DPID",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Umzi's DPID menu...")
            break


def phhofm_dpid_menu():
    """Phhofm DPID downscaling menu."""
    print_header("🔧 Phhofm DPID Downscaling", Mocha.blue)

    try:
        from pepedpid import dpid_resize
    except ImportError:
        print_error(
            "❌ pepedpid is not installed. Please install it with: pip install pepedpid"
        )
        return

    options = {
        "1": ("📁 Single Folder Processing", phhofm_dpid_single_folder),
        "2": ("🔗 HQ/LQ Paired Processing", phhofm_dpid_hq_lq_pairs),
        "3": ("⚙️ Configure Parameters", configure_phhofm_dpid_params),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Phhofm's DPID implementation with advanced parameters",
        "Options": "3 processing modes available",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
        "Key Features": [
            "📁 Single Folder Processing - Process all images in one folder",
            "🔗 HQ/LQ Paired Processing - Process matching HQ/LQ image pairs",
            "⚙️ Configure Parameters - Set advanced DPID parameters",
        ],
        "Tips": [
            "🔧 Phhofm DPID offers more control over downscaling",
            "💡 Custom lambda calculation based on scale factor",
            "📊 Advanced parameter tuning for specific use cases",
            "🔄 Optimized for high-quality downscaling results",
            "🎨 Supports alpha channels (RGBA images) automatically",
        ],
    }

    while True:
        try:
            key = show_menu(
                "🔧 Phhofm DPID",
                options,
                Mocha.blue,
                current_menu="Phhofm DPID",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Phhofm DPID menu...")
            break


def basicsr_dpid_menu():
    """BasicSR DPID downscaling menu."""
    print_header("⚡ BasicSR DPID Downscaling", Mocha.yellow)

    options = {
        "1": ("📁 Single Folder Processing", basicsr_dpid_single_folder),
        "2": ("🔗 HQ/LQ Paired Processing", basicsr_dpid_hq_lq_pairs),
        "3": ("⚙️ Configure Parameters", configure_basicsr_dpid_params),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "BasicSR DPID implementation optimized for super-resolution",
        "Options": "3 processing modes available",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
        "Key Features": [
            "📁 Single Folder Processing - Process all images in one folder",
            "🔗 HQ/LQ Paired Processing - Process matching HQ/LQ image pairs",
            "⚙️ Configure Parameters - Set BasicSR-specific parameters",
        ],
        "Tips": [
            "⚡ BasicSR DPID is optimized for super-resolution training",
            "💡 Uses Gaussian kernel with configurable parameters",
            "📊 Supports isotropic and anisotropic kernels",
            "🔄 Excellent for creating training pairs for SR models",
            "🎨 Supports alpha channels (RGBA images) automatically",
        ],
    }

    while True:
        try:
            key = show_menu(
                "⚡ BasicSR DPID",
                options,
                Mocha.yellow,
                current_menu="BasicSR DPID",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting BasicSR DPID menu...")
            break


def openmmlab_dpid_menu():
    """OpenMMLab DPID downscaling menu."""
    print_header("🚀 OpenMMLab DPID Downscaling", Mocha.red)

    options = {
        "1": ("📁 Single Folder Processing", openmmlab_dpid_single_folder),
        "2": ("🔗 HQ/LQ Paired Processing", openmmlab_dpid_hq_lq_pairs),
        "3": ("⚙️ Configure Parameters", configure_openmmlab_dpid_params),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "OpenMMLab DPID implementation for research and high-quality results",
        "Options": "3 processing modes available",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
        "Key Features": [
            "📁 Single Folder Processing - Process all images in one folder",
            "🔗 HQ/LQ Paired Processing - Process matching HQ/LQ image pairs",
            "⚙️ Configure Parameters - Set OpenMMLab-specific parameters",
        ],
        "Tips": [
            "🚀 OpenMMLab DPID provides high-quality research results",
            "💡 Advanced kernel generation with precise control",
            "📊 Supports complex anisotropic kernels",
            "🔄 Ideal for research and publication-quality results",
            "🎨 Supports alpha channels (RGBA images) automatically",
        ],
    }

    while True:
        try:
            key = show_menu(
                "🚀 OpenMMLab DPID",
                options,
                Mocha.red,
                current_menu="OpenMMLab DPID",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting OpenMMLab DPID menu...")
            break


def compare_dpid_methods():
    """Compare different DPID methods and their characteristics."""
    print_header("📊 DPID Method Comparison", Mocha.teal)

    comparison_data = {
        "🐸 Umzi's DPID (pepedpid)": {
            "Speed": "⭐⭐⭐⭐⭐",
            "Quality": "⭐⭐⭐⭐",
            "Memory": "⭐⭐⭐⭐⭐",
            "Ease of Use": "⭐⭐⭐⭐⭐",
            "Features": "Fast, efficient, good quality",
            "Best For": "General use, quick processing",
            "Dependencies": "pepedpid",
        },
        "🔧 Phhofm DPID": {
            "Speed": "⭐⭐⭐⭐",
            "Quality": "⭐⭐⭐⭐⭐",
            "Memory": "⭐⭐⭐⭐",
            "Ease of Use": "⭐⭐⭐⭐",
            "Features": "Advanced parameters, high quality",
            "Best For": "Quality-focused processing",
            "Dependencies": "pepedpid",
        },
        "⚡ BasicSR DPID": {
            "Speed": "⭐⭐⭐",
            "Quality": "⭐⭐⭐⭐⭐",
            "Memory": "⭐⭐⭐",
            "Ease of Use": "⭐⭐⭐",
            "Features": "SR-optimized, configurable kernels",
            "Best For": "Super-resolution training data",
            "Dependencies": "BasicSR, torch",
        },
        "🚀 OpenMMLab DPID": {
            "Speed": "⭐⭐⭐",
            "Quality": "⭐⭐⭐⭐⭐",
            "Memory": "⭐⭐⭐",
            "Ease of Use": "⭐⭐⭐",
            "Features": "Research-grade, advanced kernels",
            "Best For": "Research, publication quality",
            "Dependencies": "OpenMMLab, torch",
        },
    }

    print_section("📊 DPID Method Comparison", Mocha.teal)
    print_info("Comparison of different DPID implementations:")
    print_info("")

    for method, data in comparison_data.items():
        print_section(f"{method}", Mocha.lavender)
        for key, value in data.items():
            print_info(f"  {key}: {value}")
        print_info("")

    print_section("💡 Recommendations", Mocha.green)
    print_info("🐸 For most users: Start with Umzi's DPID (fast and reliable)")
    print_info("🔧 For quality focus: Use Phhofm DPID with custom parameters")
    print_info("⚡ For SR training: Use BasicSR DPID for optimal results")
    print_info("🚀 For research: Use OpenMMLab DPID for publication quality")
    print_info("")

    print_section("⚙️ Parameter Guidelines", Mocha.yellow)
    print_info("Lambda (λ) parameter controls detail preservation:")
    print_info("  • λ = 0.0: Maximum smoothing (no detail preservation)")
    print_info("  • λ = 0.5: Balanced detail preservation (recommended)")
    print_info("  • λ = 1.0: Maximum detail preservation (may introduce artifacts)")
    print_info("")

    input("Press Enter to continue...")


# Configuration functions for each method
def configure_umzi_dpid_params():
    """Configure Umzi's DPID parameters."""
    print_header("⚙️ Configure Umzi's DPID Parameters", Mocha.green)

    # Get lambda parameter
    lambda_val = ask_float(
        "Enter lambda value (0.0-1.0, 0.5 recommended): ",
        default=0.5,
        min_value=0.0,
        max_value=1.0,
    )

    # Get scale factors
    scales_input = input(
        "Enter scale factors (comma-separated, e.g., 0.5,0.25,0.125): "
    ).strip()
    if scales_input:
        try:
            scales = [float(s.strip()) for s in scales_input.split(",")]
            scales = [s for s in scales if 0.0 < s < 1.0]
        except ValueError:
            print_warning("Invalid scale factors, using default [0.5, 0.25]")
            scales = [0.5, 0.25]
    else:
        scales = [0.5, 0.25]

    # Save to session state
    session_state.umzi_dpid_lambda = lambda_val
    session_state.umzi_dpid_scales = scales

    print_success(f"✅ Umzi's DPID parameters configured:")
    print_info(f"  Lambda: {lambda_val}")
    print_info(f"  Scales: {scales}")

    play_done_sound()


def configure_phhofm_dpid_params():
    """Configure Phhofm DPID parameters."""
    print_header("⚙️ Configure Phhofm DPID Parameters", Mocha.blue)

    # Get lambda parameter
    lambda_val = ask_float(
        "Enter lambda value (0.0-1.0, 0.5 recommended): ",
        default=0.5,
        min_value=0.0,
        max_value=1.0,
    )

    # Get scale factors
    scales_input = input(
        "Enter scale factors (comma-separated, e.g., 0.5,0.25,0.125): "
    ).strip()
    if scales_input:
        try:
            scales = [float(s.strip()) for s in scales_input.split(",")]
            scales = [s for s in scales if 0.0 < s < 1.0]
        except ValueError:
            print_warning("Invalid scale factors, using default [0.5, 0.25]")
            scales = [0.5, 0.25]
    else:
        scales = [0.5, 0.25]

    # Save to session state
    session_state.phhofm_dpid_lambda = lambda_val
    session_state.phhofm_dpid_scales = scales

    print_success(f"✅ Phhofm DPID parameters configured:")
    print_info(f"  Lambda: {lambda_val}")
    print_info(f"  Scales: {scales}")

    play_done_sound()


def configure_basicsr_dpid_params():
    """Configure BasicSR DPID parameters."""
    print_header("⚙️ Configure BasicSR DPID Parameters", Mocha.yellow)

    # Get kernel parameters
    kernel_size = ask_int(
        "Enter kernel size (odd number, 21 recommended): ",
        default=21,
        min_value=3,
        max_value=51,
    )

    sigma = ask_float(
        "Enter sigma value (1.0-5.0, 2.0 recommended): ",
        default=2.0,
        min_value=0.1,
        max_value=10.0,
    )

    lambda_val = ask_float(
        "Enter lambda value (0.0-1.0, 0.5 recommended): ",
        default=0.5,
        min_value=0.0,
        max_value=1.0,
    )

    # Get scale factors
    scales_input = input(
        "Enter scale factors (comma-separated, e.g., 0.5,0.25,0.125): "
    ).strip()
    if scales_input:
        try:
            scales = [float(s.strip()) for s in scales_input.split(",")]
            scales = [s for s in scales if 0.0 < s < 1.0]
        except ValueError:
            print_warning("Invalid scale factors, using default [0.5, 0.25]")
            scales = [0.5, 0.25]
    else:
        scales = [0.5, 0.25]

    # Save to session state
    session_state.basicsr_dpid_kernel_size = kernel_size
    session_state.basicsr_dpid_sigma = sigma
    session_state.basicsr_dpid_lambda = lambda_val
    session_state.basicsr_dpid_scales = scales

    print_success(f"✅ BasicSR DPID parameters configured:")
    print_info(f"  Kernel Size: {kernel_size}")
    print_info(f"  Sigma: {sigma}")
    print_info(f"  Lambda: {lambda_val}")
    print_info(f"  Scales: {scales}")

    play_done_sound()


def configure_openmmlab_dpid_params():
    """Configure OpenMMLab DPID parameters."""
    print_header("⚙️ Configure OpenMMLab DPID Parameters", Mocha.red)

    # Get kernel parameters
    kernel_size = ask_int(
        "Enter kernel size (odd number, 21 recommended): ",
        default=21,
        min_value=3,
        max_value=51,
    )

    sigma = ask_float(
        "Enter sigma value (1.0-5.0, 2.0 recommended): ",
        default=2.0,
        min_value=0.1,
        max_value=10.0,
    )

    lambda_val = ask_float(
        "Enter lambda value (0.0-1.0, 0.5 recommended): ",
        default=0.5,
        min_value=0.0,
        max_value=1.0,
    )

    # Get scale factors
    scales_input = input(
        "Enter scale factors (comma-separated, e.g., 0.5,0.25,0.125): "
    ).strip()
    if scales_input:
        try:
            scales = [float(s.strip()) for s in scales_input.split(",")]
            scales = [s for s in scales if 0.0 < s < 1.0]
        except ValueError:
            print_warning("Invalid scale factors, using default [0.5, 0.25]")
            scales = [0.5, 0.25]
    else:
        scales = [0.5, 0.25]

    # Save to session state
    session_state.openmmlab_dpid_kernel_size = kernel_size
    session_state.openmmlab_dpid_sigma = sigma
    session_state.openmmlab_dpid_lambda = lambda_val
    session_state.openmmlab_dpid_scales = scales

    print_success(f"✅ OpenMMLab DPID parameters configured:")
    print_info(f"  Kernel Size: {kernel_size}")
    print_info(f"  Sigma: {sigma}")
    print_info(f"  Lambda: {lambda_val}")
    print_info(f"  Scales: {scales}")

    play_done_sound()


# Processing functions for each method
def umzi_dpid_single_folder():
    """Process single folder with Umzi's DPID."""
    print_header("🐸 Umzi's DPID - Single Folder Processing", Mocha.green)

    try:
        from pepedpid import dpid_resize
    except ImportError:
        print_error(
            "❌ pepedpid is not installed. Please install it with: pip install pepedpid"
        )
        return

    # Get input folder
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return

    # Get output base folder
    output_base = get_destination_path("Enter output base folder path: ")
    if not output_base:
        return

    # Get parameters
    lambda_val = getattr(session_state, "umzi_dpid_lambda", 0.5)
    scales = getattr(session_state, "umzi_dpid_scales", [0.5, 0.25])

    # Confirm parameters
    print_section("📋 Processing Parameters", Mocha.lavender)
    print_info(f"Input Folder: {input_folder}")
    print_info(f"Output Base: {output_base}")
    print_info(f"Lambda: {lambda_val}")
    print_info(f"Scales: {scales}")

    if not ask_yes_no("Proceed with processing? (y/n): "):
        return

    # Process images
    try:
        from dataset_forge.dpid.umzi_dpid import run_umzi_dpid_single_folder

        run_umzi_dpid_single_folder(
            input_folder=input_folder,
            output_base=output_base,
            scales=scales,
            overwrite=False,
            lambd=lambda_val,
        )
        print_success("✅ Umzi's DPID processing completed successfully!")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Error during processing: {e}")
        clear_memory()
        clear_cuda_cache()


def umzi_dpid_hq_lq_pairs():
    """Process HQ/LQ pairs with Umzi's DPID."""
    print_header("🐸 Umzi's DPID - HQ/LQ Paired Processing", Mocha.green)

    try:
        from pepedpid import dpid_resize
    except ImportError:
        print_error(
            "❌ pepedpid is not installed. Please install it with: pip install pepedpid"
        )
        return

    # Get HQ/LQ folders
    hq_folder = get_folder_path("Enter HQ folder path: ")
    if not hq_folder:
        return

    lq_folder = get_folder_path("Enter LQ folder path: ")
    if not lq_folder:
        return

    # Get output base folders
    out_hq_base = get_destination_path("Enter output HQ base folder path: ")
    if not out_hq_base:
        return

    out_lq_base = get_destination_path("Enter output LQ base folder path: ")
    if not out_lq_base:
        return

    # Get parameters
    lambda_val = getattr(session_state, "umzi_dpid_lambda", 0.5)
    scales = getattr(session_state, "umzi_dpid_scales", [0.5, 0.25])

    # Confirm parameters
    print_section("📋 Processing Parameters", Mocha.lavender)
    print_info(f"HQ Folder: {hq_folder}")
    print_info(f"LQ Folder: {lq_folder}")
    print_info(f"Output HQ Base: {out_hq_base}")
    print_info(f"Output LQ Base: {out_lq_base}")
    print_info(f"Lambda: {lambda_val}")
    print_info(f"Scales: {scales}")

    if not ask_yes_no("Proceed with processing? (y/n): "):
        return

    # Process images
    try:
        from dataset_forge.dpid.umzi_dpid import run_umzi_dpid_hq_lq

        run_umzi_dpid_hq_lq(
            hq_folder=hq_folder,
            lq_folder=lq_folder,
            out_hq_base=out_hq_base,
            out_lq_base=out_lq_base,
            scales=scales,
            overwrite=False,
            lambd=lambda_val,
        )
        print_success("✅ Umzi's DPID HQ/LQ processing completed successfully!")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Error during processing: {e}")
        clear_memory()
        clear_cuda_cache()


def phhofm_dpid_single_folder():
    """Process single folder with Phhofm DPID."""
    print_header("🔧 Phhofm DPID - Single Folder Processing", Mocha.blue)

    try:
        from pepedpid import dpid_resize
    except ImportError:
        print_error(
            "❌ pepedpid is not installed. Please install it with: pip install pepedpid"
        )
        return

    # Get input folder
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return

    # Get output base folder
    output_base = get_destination_path("Enter output base folder path: ")
    if not output_base:
        return

    # Get parameters
    lambda_val = getattr(session_state, "phhofm_dpid_lambda", 0.5)
    scales = getattr(session_state, "phhofm_dpid_scales", [0.5, 0.25])

    # Confirm parameters
    print_section("📋 Processing Parameters", Mocha.lavender)
    print_info(f"Input Folder: {input_folder}")
    print_info(f"Output Base: {output_base}")
    print_info(f"Lambda: {lambda_val}")
    print_info(f"Scales: {scales}")

    if not ask_yes_no("Proceed with processing? (y/n): "):
        return

    # Process images
    try:
        from dataset_forge.dpid.phhofm_dpid import run_phhofm_dpid_single_folder

        run_phhofm_dpid_single_folder(
            input_folder=input_folder,
            output_base=output_base,
            scales=scales,
            overwrite=False,
            lambd=lambda_val,
        )
        print_success("✅ Phhofm DPID processing completed successfully!")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Error during processing: {e}")
        clear_memory()
        clear_cuda_cache()


def phhofm_dpid_hq_lq_pairs():
    """Process HQ/LQ pairs with Phhofm DPID."""
    print_header("🔧 Phhofm DPID - HQ/LQ Paired Processing", Mocha.blue)

    try:
        from pepedpid import dpid_resize
    except ImportError:
        print_error(
            "❌ pepedpid is not installed. Please install it with: pip install pepedpid"
        )
        return

    # Get HQ/LQ folders
    hq_folder = get_folder_path("Enter HQ folder path: ")
    if not hq_folder:
        return

    lq_folder = get_folder_path("Enter LQ folder path: ")
    if not lq_folder:
        return

    # Get output base folders
    out_hq_base = get_destination_path("Enter output HQ base folder path: ")
    if not out_hq_base:
        return

    out_lq_base = get_destination_path("Enter output LQ base folder path: ")
    if not out_lq_base:
        return

    # Get parameters
    lambda_val = getattr(session_state, "phhofm_dpid_lambda", 0.5)
    scales = getattr(session_state, "phhofm_dpid_scales", [0.5, 0.25])

    # Confirm parameters
    print_section("📋 Processing Parameters", Mocha.lavender)
    print_info(f"HQ Folder: {hq_folder}")
    print_info(f"LQ Folder: {lq_folder}")
    print_info(f"Output HQ Base: {out_hq_base}")
    print_info(f"Output LQ Base: {out_lq_base}")
    print_info(f"Lambda: {lambda_val}")
    print_info(f"Scales: {scales}")

    if not ask_yes_no("Proceed with processing? (y/n): "):
        return

    # Process images
    try:
        from dataset_forge.dpid.phhofm_dpid import run_phhofm_dpid_hq_lq

        run_phhofm_dpid_hq_lq(
            hq_folder=hq_folder,
            lq_folder=lq_folder,
            out_hq_base=out_hq_base,
            out_lq_base=out_lq_base,
            scales=scales,
            overwrite=False,
            lambd=lambda_val,
        )
        print_success("✅ Phhofm DPID HQ/LQ processing completed successfully!")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Error during processing: {e}")
        clear_memory()
        clear_cuda_cache()


def basicsr_dpid_single_folder():
    """Process single folder with BasicSR DPID."""
    print_header("⚡ BasicSR DPID - Single Folder Processing", Mocha.yellow)

    # Get input folder
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return

    # Get output base folder
    output_base = get_destination_path("Enter output base folder path: ")
    if not output_base:
        return

    # Get parameters
    kernel_size = getattr(session_state, "basicsr_dpid_kernel_size", 21)
    sigma = getattr(session_state, "basicsr_dpid_sigma", 2.0)
    lambda_val = getattr(session_state, "basicsr_dpid_lambda", 0.5)
    scales = getattr(session_state, "basicsr_dpid_scales", [0.5, 0.25])

    # Confirm parameters
    print_section("📋 Processing Parameters", Mocha.lavender)
    print_info(f"Input Folder: {input_folder}")
    print_info(f"Output Base: {output_base}")
    print_info(f"Kernel Size: {kernel_size}")
    print_info(f"Sigma: {sigma}")
    print_info(f"Lambda: {lambda_val}")
    print_info(f"Scales: {scales}")

    if not ask_yes_no("Proceed with processing? (y/n): "):
        return

    # Process images
    try:
        from dataset_forge.dpid.basicsr_dpid import run_basicsr_dpid_single_folder

        run_basicsr_dpid_single_folder(
            input_folder=input_folder,
            output_base=output_base,
            scales=scales,
            overwrite=False,
            kernel_size=kernel_size,
            sigma=sigma,
            lambd=lambda_val,
            isotropic=True,
        )
        print_success("✅ BasicSR DPID processing completed successfully!")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Error during processing: {e}")
        clear_memory()
        clear_cuda_cache()


def basicsr_dpid_hq_lq_pairs():
    """Process HQ/LQ pairs with BasicSR DPID."""
    print_header("⚡ BasicSR DPID - HQ/LQ Paired Processing", Mocha.yellow)

    # Get HQ/LQ folders
    hq_folder = get_folder_path("Enter HQ folder path: ")
    if not hq_folder:
        return

    lq_folder = get_folder_path("Enter LQ folder path: ")
    if not lq_folder:
        return

    # Get output base folders
    out_hq_base = get_destination_path("Enter output HQ base folder path: ")
    if not out_hq_base:
        return

    out_lq_base = get_destination_path("Enter output LQ base folder path: ")
    if not out_lq_base:
        return

    # Get parameters
    kernel_size = getattr(session_state, "basicsr_dpid_kernel_size", 21)
    sigma = getattr(session_state, "basicsr_dpid_sigma", 2.0)
    lambda_val = getattr(session_state, "basicsr_dpid_lambda", 0.5)
    scales = getattr(session_state, "basicsr_dpid_scales", [0.5, 0.25])

    # Confirm parameters
    print_section("📋 Processing Parameters", Mocha.lavender)
    print_info(f"HQ Folder: {hq_folder}")
    print_info(f"LQ Folder: {lq_folder}")
    print_info(f"Output HQ Base: {out_hq_base}")
    print_info(f"Output LQ Base: {out_lq_base}")
    print_info(f"Kernel Size: {kernel_size}")
    print_info(f"Sigma: {sigma}")
    print_info(f"Lambda: {lambda_val}")
    print_info(f"Scales: {scales}")

    if not ask_yes_no("Proceed with processing? (y/n): "):
        return

    # Process images
    try:
        from dataset_forge.dpid.basicsr_dpid import run_basicsr_dpid_hq_lq

        run_basicsr_dpid_hq_lq(
            hq_folder=hq_folder,
            lq_folder=lq_folder,
            out_hq_base=out_hq_base,
            out_lq_base=out_lq_base,
            scales=scales,
            overwrite=False,
            kernel_size=kernel_size,
            sigma=sigma,
            lambd=lambda_val,
            isotropic=True,
        )
        print_success("✅ BasicSR DPID HQ/LQ processing completed successfully!")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Error during processing: {e}")
        clear_memory()
        clear_cuda_cache()


def openmmlab_dpid_single_folder():
    """Process single folder with OpenMMLab DPID."""
    print_header("🚀 OpenMMLab DPID - Single Folder Processing", Mocha.red)

    # Get input folder
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return

    # Get output base folder
    output_base = get_destination_path("Enter output base folder path: ")
    if not output_base:
        return

    # Get parameters
    kernel_size = getattr(session_state, "openmmlab_dpid_kernel_size", 21)
    sigma = getattr(session_state, "openmmlab_dpid_sigma", 2.0)
    lambda_val = getattr(session_state, "openmmlab_dpid_lambda", 0.5)
    scales = getattr(session_state, "openmmlab_dpid_scales", [0.5, 0.25])

    # Confirm parameters
    print_section("📋 Processing Parameters", Mocha.lavender)
    print_info(f"Input Folder: {input_folder}")
    print_info(f"Output Base: {output_base}")
    print_info(f"Kernel Size: {kernel_size}")
    print_info(f"Sigma: {sigma}")
    print_info(f"Lambda: {lambda_val}")
    print_info(f"Scales: {scales}")

    if not ask_yes_no("Proceed with processing? (y/n): "):
        return

    # Process images
    try:
        from dataset_forge.dpid.openmmlab_dpid import run_openmmlab_dpid_single_folder

        run_openmmlab_dpid_single_folder(
            input_folder=input_folder,
            output_base=output_base,
            scales=scales,
            overwrite=False,
            kernel_size=kernel_size,
            sigma=sigma,
            lambd=lambda_val,
            isotropic=True,
        )
        print_success("✅ OpenMMLab DPID processing completed successfully!")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Error during processing: {e}")
        clear_memory()
        clear_cuda_cache()


def openmmlab_dpid_hq_lq_pairs():
    """Process HQ/LQ pairs with OpenMMLab DPID."""
    print_header("🚀 OpenMMLab DPID - HQ/LQ Paired Processing", Mocha.red)

    # Get HQ/LQ folders
    hq_folder = get_folder_path("Enter HQ folder path: ")
    if not hq_folder:
        return

    lq_folder = get_folder_path("Enter LQ folder path: ")
    if not lq_folder:
        return

    # Get output base folders
    out_hq_base = get_destination_path("Enter output HQ base folder path: ")
    if not out_hq_base:
        return

    out_lq_base = get_destination_path("Enter output LQ base folder path: ")
    if not out_lq_base:
        return

    # Get parameters
    kernel_size = getattr(session_state, "openmmlab_dpid_kernel_size", 21)
    sigma = getattr(session_state, "openmmlab_dpid_sigma", 2.0)
    lambda_val = getattr(session_state, "openmmlab_dpid_lambda", 0.5)
    scales = getattr(session_state, "openmmlab_dpid_scales", [0.5, 0.25])

    # Confirm parameters
    print_section("📋 Processing Parameters", Mocha.lavender)
    print_info(f"HQ Folder: {hq_folder}")
    print_info(f"LQ Folder: {lq_folder}")
    print_info(f"Output HQ Base: {out_hq_base}")
    print_info(f"Output LQ Base: {out_lq_base}")
    print_info(f"Kernel Size: {kernel_size}")
    print_info(f"Sigma: {sigma}")
    print_info(f"Lambda: {lambda_val}")
    print_info(f"Scales: {scales}")

    if not ask_yes_no("Proceed with processing? (y/n): "):
        return

    # Process images
    try:
        from dataset_forge.dpid.openmmlab_dpid import run_openmmlab_dpid_hq_lq

        run_openmmlab_dpid_hq_lq(
            hq_folder=hq_folder,
            lq_folder=lq_folder,
            out_hq_base=out_hq_base,
            out_lq_base=out_lq_base,
            scales=scales,
            overwrite=False,
            kernel_size=kernel_size,
            sigma=sigma,
            lambd=lambda_val,
            isotropic=True,
        )
        print_success("✅ OpenMMLab DPID HQ/LQ processing completed successfully!")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Error during processing: {e}")
        clear_memory()
        clear_cuda_cache()
