import subprocess
import sys
import tempfile
import os
import platform

from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.color import Mocha


def find_native_resolution(image_path, lq_path=None, extra_args=None):
    """
    Runs getnative on the given image (and optionally LQ image) and prints the output or error.
    """
    from dataset_forge.utils.printing import print_info, print_error
    from dataset_forge.utils.audio_utils import play_error_sound
    import sys

    print_info("[DEBUG] Running getnative (VapourSynth) native resolution detection...")
    cmd = [sys.executable, "-m", "getnative"]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(image_path)
    if lq_path:
        cmd.append(lq_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            print_info(f"getnative output:\n{result.stdout.strip()}")
        elif result.stderr.strip():
            print_error(f"getnative error: {result.stderr.strip()}")
            play_error_sound()
        else:
            print_error("getnative returned no output and no error message.")
            play_error_sound()
    except Exception as e:
        print_error(f"[getnative] Exception: {e}")
        play_error_sound()
    print_info("[DEBUG] getnative workflow finished.")
    play_done_sound()


def find_native_resolution_resdet(image_path, extra_args=None):
    """
    Runs resdet on the given image and prints the output or error.
    Uses WSL if on Windows, otherwise runs natively.
    """
    import shutil
    import subprocess
    from dataset_forge.utils.printing import print_info, print_error
    from dataset_forge.utils.audio_utils import play_error_sound

    print_info(f"[DEBUG] Running resdet on: {image_path}")
    is_windows = platform.system().lower() == "windows"

    def to_wsl_path(win_path):
        # Convert C:/Users/... to /mnt/c/Users/...
        if win_path[1:3] == ":/" or win_path[1:3] == ":\\":
            drive = win_path[0].lower()
            rest = win_path[2:].replace("\\", "/")
            return f"/mnt/{drive}{rest}"
        return win_path

    if is_windows:
        wsl_exe = shutil.which("wsl")
        if not wsl_exe:
            print_error(
                "WSL is not installed or not in PATH. Please install WSL and resdet in your WSL environment."
            )
            play_error_sound()
            return
        wsl_image_path = to_wsl_path(image_path)
        cmd = ["wsl", "resdet"]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(wsl_image_path)
    else:
        resdet_path = shutil.which("resdet")
        if not resdet_path:
            print_error("resdet not found in PATH.")
            play_error_sound()
            return
        cmd = [resdet_path]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(image_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            print_info(f"resdet output:\n{result.stdout.strip()}")
        elif result.stderr.strip():
            print_error(f"resdet error: {result.stderr.strip()}")
            play_error_sound()
        else:
            print_error("resdet returned no output and no error message.")
            play_error_sound()
    except Exception as e:
        print_error(f"[resdet] Exception: {e}")
        play_error_sound()
    print_info("[DEBUG] resdet workflow finished.")
    play_done_sound()


def find_native_resolution_getfnative(image_path, lq_path=None, extra_args=None):
    """
    Runs GetFnative on the given image (and optionally LQ image) and prints the output or error.
    GetFnative is a script that helps find the native fractional resolution of upscaled material.

    Supports both getfnative.exe (full analysis) and getfnativeq.exe (quick analysis) executables.
    Automatically converts image files to VPY scripts for analysis.
    """
    from dataset_forge.utils.printing import (
        print_info,
        print_error,
        print_warning,
        print_success,
        print_header,
        print_section,
    )
    from dataset_forge.utils.audio_utils import play_error_sound, play_done_sound
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.input_utils import get_path_with_history
    import sys
    import shutil
    from pathlib import Path
    import subprocess
    import tempfile
    import os

    print_header("🔢 GetFnative Fractional Resolution Analysis", color=Mocha.yellow)
    print_info(
        "🎯 GetFnative helps find the native fractional resolution of upscaled material (primarily anime)"
    )

    # Check for GetFnative executables in PATH
    getfnative_exe = shutil.which("getfnative.exe")
    getfnativeq_exe = shutil.which("getfnativeq.exe")

    if not getfnative_exe and not getfnativeq_exe:
        print_error(
            "❌ GetFnative executables (getfnative.exe or getfnativeq.exe) not found in PATH"
        )
        print_info(
            "💡 Please ensure getfnative.exe and/or getfnativeq.exe are installed and added to your PATH"
        )
        print_info("📥 Download from: https://github.com/YomikoR/GetFnative")
        play_error_sound()
        return

    # Choose analysis type
    analysis_options = {
        "1": ("⚡ Quick Analysis (getfnativeq.exe)", "quick"),
        "2": ("🔍 Full Analysis (getfnative.exe)", "full"),
        "0": ("⬅️  Back", None),
    }

    while True:
        analysis_key = show_menu(
            "Choose GetFnative Analysis Type",
            analysis_options,
            Mocha.lavender,
            current_menu="GetFnative Analysis",
            menu_context={
                "Purpose": "Choose between quick and full GetFnative analysis",
                "Options": "2 analysis types available",
                "Navigation": "Use numbers 1-2 to select, 0 to go back",
                "Key Features": [
                    "Quick Analysis - Fast analysis with preset parameters",
                    "Full Analysis - Comprehensive analysis with all options",
                ],
                "Tips": [
                    "Use Quick Analysis for initial screening",
                    "Use Full Analysis for detailed results",
                ],
            },
        )

        if analysis_key is None or analysis_key == "0":
            return

        if analysis_key == "1":
            use_quick = True
            executable_path = getfnativeq_exe
            analysis_type = "Quick"
            break
        elif analysis_key == "2":
            use_quick = False
            executable_path = getfnative_exe
            analysis_type = "Full"
            break
        else:
            print_warning("Invalid selection. Please try again.")

    print_success(f"✅ Using GetFnative {analysis_type} executable: {executable_path}")

    def create_vpy_from_image(image_path, output_dir=None):
        """Create a VPY script from an image file."""
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Determine output directory
        if output_dir is None:
            output_dir = image_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)

        # Create VPY script path
        vpy_name = f"{image_path.stem}_getfnative.vpy"
        vpy_path = output_dir / vpy_name

        # Get absolute paths
        abs_image_path = image_path.absolute()
        abs_vpy_path = vpy_path.absolute()

        # Create VPY script content
        vpy_content = f"""# VPY script for GetFnative analysis
# Generated from: {abs_image_path}

import vapoursynth as vs
core = vs.core

# Load the image
clip = core.imwri.Read(r"{abs_image_path}", float_output=True)

# Set output
clip.set_output(0)
"""

        # Write VPY script
        with open(abs_vpy_path, "w", encoding="utf-8") as f:
            f.write(vpy_content)

        return str(abs_vpy_path)

    # Get input path (use provided or prompt for new one)
    if image_path:
        input_path = Path(image_path)
        print_info(f"📁 Using provided input: {input_path}")
    else:
        print_section("Input Selection", char="-", color=Mocha.lavender)
        input_path = get_path_with_history("🖼️ Enter image file or VPY script path:")
        input_path = Path(input_path)

    # Validate input path
    if not input_path.exists():
        print_error(f"❌ Input file not found: {input_path}")
        play_error_sound()
        return

    # Check if input is an image file and convert to VPY if needed
    if input_path.suffix.lower() in [
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
        ".tif",
        ".webp",
    ]:
        print_info(f"🖼️  Converting image to VPY script: {input_path}")
        try:
            vpy_path = create_vpy_from_image(str(input_path))
            print_success(f"✅ Created VPY script: {vpy_path}")
            input_path = vpy_path
        except Exception as e:
            print_error(f"❌ Failed to create VPY script: {e}")
            play_error_sound()
            return
    elif input_path.suffix.lower() == ".vpy":
        print_info(f"📜 Using existing VPY script: {input_path}")
        vpy_path = str(input_path)
    else:
        print_warning(f"⚠️  Unknown file type: {input_path.suffix}")
        print_info(
            "💡 GetFnative works best with image files (.png, .jpg, etc.) or VPY scripts"
        )
        # Try to use it anyway
        vpy_path = str(input_path)

    # Get analysis parameters
    print_section("Analysis Parameters", char="-", color=Mocha.lavender)
    params = {}

    # Common parameters
    frame_input = input("Frame number (default 0): ").strip()
    if frame_input:
        try:
            params["frame_no"] = int(frame_input)
        except ValueError:
            print_warning("⚠️  Invalid frame number, using default 0")

    base_height_input = input("Base height (default auto): ").strip()
    if base_height_input:
        try:
            params["base_height"] = int(base_height_input)
        except ValueError:
            print_warning("⚠️  Invalid base height, using auto")

    base_width_input = input("Base width (default auto): ").strip()
    if base_width_input:
        try:
            params["base_width"] = int(base_width_input)
        except ValueError:
            print_warning("⚠️  Invalid base width, using auto")

    mode_input = input("Mode (wh/w/h, default wh): ").strip()
    if mode_input and mode_input.lower() in ["wh", "w", "h"]:
        params["mode"] = mode_input.lower()

    save_dir_input = input("Save directory (default auto): ").strip()
    if save_dir_input:
        params["save_dir"] = save_dir_input

    save_ext_input = input("Save extension (default svg): ").strip()
    if save_ext_input:
        params["save_ext"] = save_ext_input

    # Full analysis specific parameters
    if not use_quick:
        print_section("Full Analysis Parameters", char="-", color=Mocha.lavender)

        crop_top_input = input("Crop top (default 0): ").strip()
        if crop_top_input:
            try:
                params["crop_top"] = int(crop_top_input)
            except ValueError:
                print_warning("⚠️  Invalid crop top, using 0")

        crop_bottom_input = input("Crop bottom (default 0): ").strip()
        if crop_bottom_input:
            try:
                params["crop_bottom"] = int(crop_bottom_input)
            except ValueError:
                print_warning("⚠️  Invalid crop bottom, using 0")

        crop_left_input = input("Crop left (default 0): ").strip()
        if crop_left_input:
            try:
                params["crop_left"] = int(crop_left_input)
            except ValueError:
                print_warning("⚠️  Invalid crop left, using 0")

        crop_right_input = input("Crop right (default 0): ").strip()
        if crop_right_input:
            try:
                params["crop_right"] = int(crop_right_input)
            except ValueError:
                print_warning("⚠️  Invalid crop right, using 0")

        min_height_input = input("Min src height (default auto): ").strip()
        if min_height_input:
            try:
                params["min_src_height"] = float(min_height_input)
            except ValueError:
                print_warning("⚠️  Invalid min src height, using auto")

        max_height_input = input("Max src height (default auto): ").strip()
        if max_height_input:
            try:
                params["max_src_height"] = float(max_height_input)
            except ValueError:
                print_warning("⚠️  Invalid max src height, using auto")

        step_length_input = input("Step length (default 0.25): ").strip()
        if step_length_input:
            try:
                params["step_length"] = float(step_length_input)
            except ValueError:
                print_warning("⚠️  Invalid step length, using 0.25")

        threshold_input = input("Threshold (default 0.015): ").strip()
        if threshold_input:
            try:
                params["threshold"] = float(threshold_input)
            except ValueError:
                print_warning("⚠️  Invalid threshold, using 0.015")

        linear_light_input = input("Linear light (y/n, default n): ").strip().lower()
        if linear_light_input == "y":
            params["linear_light"] = True

    # Build command
    cmd = [executable_path, vpy_path]

    # Add parameters
    param_mapping = {
        "frame_no": "--frame",
        "base_height": "--base-height",
        "base_width": "--base-width",
        "crop_top": "--crop-top",
        "crop_bottom": "--crop-bottom",
        "crop_left": "--crop-left",
        "crop_right": "--crop-right",
        "min_src_height": "--min-src-height",
        "max_src_height": "--max-src-height",
        "step_length": "--step-length",
        "threshold": "--threshold",
        "mode": "--mode",
        "save_dir": "--save-dir",
        "save_ext": "--save-ext",
        "linear_light": "--linear-light",
    }

    for key, value in params.items():
        if value is not None and key in param_mapping:
            if key == "linear_light" and value:
                cmd.append(param_mapping[key])
            else:
                cmd.extend([param_mapping[key], str(value)])

    # Add extra arguments if provided
    if extra_args:
        cmd.extend(extra_args)

    # Add LQ path if provided
    if lq_path:
        print_warning(
            "⚠️  LQ path provided, but GetFnative typically works with single images"
        )
        print_info(
            "💡 Processing HQ image only. LQ analysis may require manual VPY script creation"
        )

    print_section("Analysis Execution", char="-", color=Mocha.lavender)
    print_info(f"🚀 Running GetFnative {analysis_type} analysis...")
    print_info(f"📜 VPY script: {vpy_path}")
    print_info(f"🔧 Command: {' '.join(cmd)}")

    try:
        # Run GetFnative with appropriate timeout
        timeout = 180 if use_quick else 300  # 3 minutes for quick, 5 minutes for full
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        print_section("Analysis Results", char="-", color=Mocha.lavender)

        if result.returncode == 0:
            print_success(
                f"✅ GetFnative {analysis_type} analysis completed successfully!"
            )

            if result.stdout.strip():
                print_info("📊 Analysis Results:")
                print_info("-" * 50)
                print_info(result.stdout.strip())
            else:
                print_warning(
                    "⚠️  No output generated. Check if the image contains upscaled content."
                )

        else:
            print_error(f"❌ GetFnative {analysis_type} analysis failed!")

            if result.stderr.strip():
                print_error("🔍 Error Details:")
                print_error(result.stderr.strip())
            else:
                print_error(
                    "💡 No error details available. Check if the input is valid."
                )

    except subprocess.TimeoutExpired:
        print_error(
            f"⏰ GetFnative {analysis_type} analysis timed out after {timeout} seconds"
        )
        print_info("💡 Try using a smaller image or the quick analysis option")
        play_error_sound()
    except FileNotFoundError:
        print_error(f"❌ GetFnative executable not found: {executable_path}")
        print_info("💡 Please ensure GetFnative is properly installed and in your PATH")
        play_error_sound()
    except Exception as e:
        print_error(
            f"❌ GetFnative {analysis_type} analysis failed with exception: {e}"
        )
        play_error_sound()

    print_info(f"[DEBUG] GetFnative {analysis_type} workflow finished.")
    play_done_sound()


def find_native_resolution_getfscaler(image_path, lq_path=None, extra_args=None):
    """
    Enhanced getfscaler integration with comprehensive menu system.
    
    This function provides access to the comprehensive getfscaler menu with multiple
    analysis options, configuration management, and advanced features.
    """
    # Import and call the comprehensive getfscaler menu
    from dataset_forge.menus.getfscaler_comprehensive_menu import getfscaler_comprehensive_menu
    
    # Call the comprehensive menu
    getfscaler_comprehensive_menu()
