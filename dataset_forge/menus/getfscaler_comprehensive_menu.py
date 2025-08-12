"""
Comprehensive getfscaler Menu Module for Dataset Forge

This module provides a comprehensive menu interface for getfscaler integration,
including single file analysis, batch processing, configuration management,
and advanced options as specified in the getfscaler_integration_guide.md.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import (
    print_info, print_success, print_warning, print_error, print_header, print_section
)
from dataset_forge.utils.input_utils import get_path_with_history, get_folder_path
from dataset_forge.utils.audio_utils import play_done_sound, play_error_sound
from dataset_forge.actions.getfscaler_actions import (
    GetfScalerIntegration,
    BatchGetfScaler,
    ConfigManager,
    find_native_resolution_getfscaler,
    batch_analyze_getfscaler,
    create_default_config
)


def getfscaler_comprehensive_menu():
    """Comprehensive getfscaler menu with multiple analysis options and advanced features."""
    options = {
        "1": ("🔍 Single File Analysis", single_file_analysis_menu),
        "2": ("📁 Batch Analysis", batch_analysis_menu),
        "3": ("⚙️ Configuration Management", configuration_menu),
        "4": ("📊 Advanced Analysis Options", advanced_analysis_menu),
        "5": ("📋 Help & Examples", help_examples_menu),
        "0": ("⬅️ Back to Find Native Resolution", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Comprehensive getfscaler integration for kernel detection and upscaling analysis",
        "Total Options": "5 main categories available",
        "Navigation": "Use numbers 1-5 to select, 0 to go back",
        "Key Features": [
            "Single File Analysis - Analyze individual images/videos for kernel detection",
            "Batch Analysis - Process multiple files with comprehensive reporting",
            "Configuration Management - Manage getfscaler settings and parameters",
            "Advanced Analysis Options - Custom parameters and advanced features",
            "Help & Examples - Usage examples and troubleshooting"
        ],
        "Tips": [
            "Start with Single File Analysis to test getfscaler functionality",
            "Use Batch Analysis for processing multiple files efficiently",
            "Configure settings in Configuration menu for optimal performance",
            "Check Help & Examples for usage guidance and troubleshooting"
        ]
    }

    while True:
        key = show_menu(
            "🔧 getfscaler Comprehensive Menu",
            options,
            Mocha.yellow,
            current_menu="getfscaler Comprehensive Menu",
            menu_context=menu_context
        )
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()


def single_file_analysis_menu():
    """Single file analysis menu with parameter configuration."""
    print_header("🔍 Single File Analysis", color=Mocha.yellow)
    
    # Get input file
    image_path = get_path_with_history("🖼️ Enter image/video file path:")
    if not image_path or not os.path.exists(image_path):
        print_error("❌ Invalid file path or file does not exist.")
        return
    
    # Parameter configuration
    print_section("Parameter Configuration", char="-", color=Mocha.lavender)
    
    # Native height
    while True:
        try:
            native_height_input = input("📏 Native height (default: 720.0): ").strip()
            if not native_height_input:
                native_height = 720.0
                break
            native_height = float(native_height_input)
            if native_height <= 0:
                print_warning("Native height must be positive. Please try again.")
                continue
            break
        except ValueError:
            print_warning("Invalid native height. Please enter a valid number.")
    
    # Native width (optional)
    native_width = None
    width_input = input("📐 Native width (optional, press Enter to skip): ").strip()
    if width_input:
        try:
            native_width = float(width_input)
            if native_width <= 0:
                print_warning("Native width must be positive. Using auto-calculation.")
                native_width = None
        except ValueError:
            print_warning("Invalid native width. Using auto-calculation.")
    
    # Crop value
    while True:
        try:
            crop_input = input("✂️ Crop pixels from edges (default: 8): ").strip()
            if not crop_input:
                crop = 8
                break
            crop = int(crop_input)
            if crop < 0:
                print_warning("Crop value must be non-negative. Please try again.")
                continue
            break
        except ValueError:
            print_warning("Invalid crop value. Please enter a valid integer.")
    
    # Frame selection (for videos)
    frame = None
    frame_input = input("🎬 Frame number (optional, press Enter for random): ").strip()
    if frame_input:
        try:
            frame = int(frame_input)
            if frame < 0:
                print_warning("Frame number must be non-negative. Using random frame.")
                frame = None
        except ValueError:
            print_warning("Invalid frame number. Using random frame.")
    
    # Debug mode
    debug = input("🐛 Enable debug mode? (y/N): ").strip().lower() == "y"
    
    # Build extra arguments
    extra_args = ["-nh", str(native_height)]
    if native_width:
        extra_args.extend(["-nw", str(native_width)])
    if crop != 8:
        extra_args.extend(["-c", str(crop)])
    if frame is not None:
        extra_args.extend(["-f", str(frame)])
    if debug:
        extra_args.append("--debug")
    
    # Execute analysis
    print_section("Analysis Execution", char="-", color=Mocha.lavender)
    find_native_resolution_getfscaler(image_path, None, extra_args)


def batch_analysis_menu():
    """Batch analysis menu for processing multiple files."""
    print_header("📁 Batch Analysis", color=Mocha.yellow)
    
    # Get directory
    directory = get_folder_path("📁 Enter directory path containing files to analyze:")
    if not directory or not os.path.isdir(directory):
        print_error("❌ Invalid directory path or directory does not exist.")
        return
    
    # Analysis parameters
    print_section("Batch Analysis Parameters", char="-", color=Mocha.lavender)
    
    # Native height
    while True:
        try:
            native_height_input = input("📏 Native height (default: 720.0): ").strip()
            if not native_height_input:
                native_height = 720.0
                break
            native_height = float(native_height_input)
            if native_height <= 0:
                print_warning("Native height must be positive. Please try again.")
                continue
            break
        except ValueError:
            print_warning("Invalid native height. Please enter a valid number.")
    
    # File patterns
    print_info("📋 Supported file patterns:")
    patterns_input = input("🔍 File patterns (default: *.png,*.jpg,*.jpeg,*.mp4,*.mkv): ").strip()
    if patterns_input:
        file_patterns = [p.strip() for p in patterns_input.split(",")]
    else:
        file_patterns = ["*.png", "*.jpg", "*.jpeg", "*.mp4", "*.mkv"]
    
    # Output file
    output_file = input("💾 Output file for results (optional, press Enter to skip): ").strip()
    if output_file and not output_file.endswith('.json'):
        output_file += '.json'
    
    # Execute batch analysis
    print_section("Batch Analysis Execution", char="-", color=Mocha.lavender)
    try:
        batch_analyze_getfscaler(directory, output_file, native_height=native_height)
    except Exception as e:
        print_error(f"❌ Batch analysis failed: {e}")
        play_error_sound()


def configuration_menu():
    """Configuration management menu."""
    print_header("⚙️ Configuration Management", color=Mocha.yellow)
    
    options = {
        "1": ("📝 Create Default Configuration", create_config),
        "2": ("📖 View Current Configuration", view_config),
        "3": ("🔧 Edit Configuration", edit_config),
        "4": ("🧪 Test Configuration", test_config),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage getfscaler configuration settings and parameters",
        "Total Options": "4 configuration options",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": [
            "Create Default Configuration - Generate default config file",
            "View Current Configuration - Display current settings",
            "Edit Configuration - Modify configuration parameters",
            "Test Configuration - Validate configuration settings"
        ],
        "Tips": [
            "Create a default configuration first to get started",
            "Test your configuration before running analysis",
            "Backup your configuration before making changes"
        ]
    }

    while True:
        key = show_menu(
            "⚙️ Configuration Management",
            options,
            Mocha.blue,
            current_menu="Configuration Management",
            menu_context=menu_context
        )
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()


def create_config():
    """Create default configuration file."""
    print_header("📝 Create Default Configuration", color=Mocha.blue)
    
    config_file = input("📄 Configuration file name (default: getfscaler_config.yaml): ").strip()
    if not config_file:
        config_file = "getfscaler_config.yaml"
    
    try:
        create_default_config(config_file)
        print_success(f"✅ Default configuration created: {config_file}")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Failed to create configuration: {e}")
        play_error_sound()


def view_config():
    """View current configuration."""
    print_header("📖 View Current Configuration", color=Mocha.blue)
    
    config_file = input("📄 Configuration file name (default: getfscaler_config.yaml): ").strip()
    if not config_file:
        config_file = "getfscaler_config.yaml"
    
    try:
        config = ConfigManager.load_config(config_file)
        print_section("Current Configuration", char="-", color=Mocha.lavender)
        print_info(f"📁 Executable Path: {config.exe_path}")
        print_info(f"📏 Default Native Height: {config.default_native_height}")
        print_info(f"✂️ Default Crop: {config.default_crop}")
        print_info(f"⏱️ Timeout Seconds: {config.timeout_seconds}")
        print_info(f"🔧 Max Workers: {config.max_workers}")
        print_info(f"📋 Supported Extensions: {', '.join(config.supported_extensions)}")
        play_done_sound()
    except Exception as e:
        print_error(f"❌ Failed to load configuration: {e}")
        play_error_sound()


def edit_config():
    """Edit configuration parameters."""
    print_header("🔧 Edit Configuration", color=Mocha.blue)
    
    config_file = input("📄 Configuration file name (default: getfscaler_config.yaml): ").strip()
    if not config_file:
        config_file = "getfscaler_config.yaml"
    
    try:
        config = ConfigManager.load_config(config_file)
        
        print_section("Edit Configuration Parameters", char="-", color=Mocha.lavender)
        
        # Edit executable path
        new_exe_path = input(f"📁 Executable path (current: {config.exe_path}): ").strip()
        if new_exe_path:
            config.exe_path = new_exe_path
        
        # Edit native height
        new_height = input(f"📏 Default native height (current: {config.default_native_height}): ").strip()
        if new_height:
            try:
                config.default_native_height = float(new_height)
            except ValueError:
                print_warning("Invalid native height. Keeping current value.")
        
        # Edit crop
        new_crop = input(f"✂️ Default crop (current: {config.default_crop}): ").strip()
        if new_crop:
            try:
                config.default_crop = int(new_crop)
            except ValueError:
                print_warning("Invalid crop value. Keeping current value.")
        
        # Save configuration
        ConfigManager.save_config(config, config_file)
        print_success(f"✅ Configuration updated and saved: {config_file}")
        play_done_sound()
        
    except Exception as e:
        print_error(f"❌ Failed to edit configuration: {e}")
        play_error_sound()


def test_config():
    """Test configuration settings."""
    print_header("🧪 Test Configuration", color=Mocha.blue)
    
    config_file = input("📄 Configuration file name (default: getfscaler_config.yaml): ").strip()
    if not config_file:
        config_file = "getfscaler_config.yaml"
    
    try:
        config = ConfigManager.load_config(config_file)
        
        print_section("Configuration Test Results", char="-", color=Mocha.lavender)
        
        # Test executable path
        print_info("🔍 Testing executable path...")
        try:
            scaler = GetfScalerIntegration(config.exe_path)
            print_success(f"✅ Executable found: {scaler.exe_path}")
        except FileNotFoundError as e:
            print_error(f"❌ Executable not found: {e}")
        
        # Test parameter validation
        print_info("🔍 Testing parameter validation...")
        try:
            validator = scaler.validator
            validator.validate_parameters(config.default_native_height, None, config.default_crop)
            print_success("✅ Parameter validation passed")
        except Exception as e:
            print_error(f"❌ Parameter validation failed: {e}")
        
        print_success("✅ Configuration test completed")
        play_done_sound()
        
    except Exception as e:
        print_error(f"❌ Configuration test failed: {e}")
        play_error_sound()


def advanced_analysis_menu():
    """Advanced analysis options menu."""
    print_header("📊 Advanced Analysis Options", color=Mocha.yellow)
    
    options = {
        "1": ("🎯 Custom Parameter Analysis", custom_parameter_analysis),
        "2": ("🔄 Multiple Native Heights", multiple_native_heights),
        "3": ("📊 Comparative Analysis", comparative_analysis),
        "4": ("🔬 Debug Mode Analysis", debug_mode_analysis),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Advanced getfscaler analysis options and custom configurations",
        "Total Options": "4 advanced options",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": [
            "Custom Parameter Analysis - Analyze with custom parameters",
            "Multiple Native Heights - Test different native heights",
            "Comparative Analysis - Compare different analysis methods",
            "Debug Mode Analysis - Detailed debug information"
        ],
        "Tips": [
            "Use custom parameters for specific analysis needs",
            "Test multiple native heights to find optimal results",
            "Debug mode provides detailed analysis information"
        ]
    }

    while True:
        key = show_menu(
            "📊 Advanced Analysis Options",
            options,
            Mocha.green,
            current_menu="Advanced Analysis Options",
            menu_context=menu_context
        )
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()


def custom_parameter_analysis():
    """Custom parameter analysis with advanced options."""
    print_header("🎯 Custom Parameter Analysis", color=Mocha.green)
    
    # Get input file
    image_path = get_path_with_history("🖼️ Enter image/video file path:")
    if not image_path or not os.path.exists(image_path):
        print_error("❌ Invalid file path or file does not exist.")
        return
    
    print_section("Custom Parameters", char="-", color=Mocha.lavender)
    
    # Advanced parameters
    params = {}
    
    # Native height
    while True:
        try:
            native_height = float(input("📏 Native height: ").strip())
            if native_height <= 0:
                print_warning("Native height must be positive.")
                continue
            params['native_height'] = native_height
            break
        except ValueError:
            print_warning("Invalid native height.")
    
    # Native width
    width_input = input("📐 Native width (press Enter to skip): ").strip()
    if width_input:
        try:
            params['native_width'] = float(width_input)
        except ValueError:
            print_warning("Invalid native width. Skipping.")
    
    # Crop
    while True:
        try:
            crop = int(input("✂️ Crop pixels: ").strip())
            if crop < 0:
                print_warning("Crop must be non-negative.")
                continue
            params['crop'] = crop
            break
        except ValueError:
            print_warning("Invalid crop value.")
    
    # Frame
    frame_input = input("🎬 Frame number (press Enter to skip): ").strip()
    if frame_input:
        try:
            params['frame'] = int(frame_input)
        except ValueError:
            print_warning("Invalid frame number. Skipping.")
    
    # Build command
    extra_args = ["-nh", str(params['native_height'])]
    if 'native_width' in params:
        extra_args.extend(["-nw", str(params['native_width'])])
    if 'crop' in params:
        extra_args.extend(["-c", str(params['crop'])])
    if 'frame' in params:
        extra_args.extend(["-f", str(params['frame'])])
    
    # Execute analysis
    print_section("Custom Analysis Execution", char="-", color=Mocha.lavender)
    find_native_resolution_getfscaler(image_path, None, extra_args)


def multiple_native_heights():
    """Analyze with multiple native heights."""
    print_header("🔄 Multiple Native Heights Analysis", color=Mocha.green)
    
    # Get input file
    image_path = get_path_with_history("🖼️ Enter image/video file path:")
    if not image_path or not os.path.exists(image_path):
        print_error("❌ Invalid file path or file does not exist.")
        return
    
    print_section("Multiple Native Heights", char="-", color=Mocha.lavender)
    
    # Get native heights
    heights_input = input("📏 Native heights (comma-separated, e.g., 480,720,1080): ").strip()
    if not heights_input:
        print_error("❌ No native heights specified.")
        return
    
    try:
        heights = [float(h.strip()) for h in heights_input.split(",")]
        heights = [h for h in heights if h > 0]
        if not heights:
            print_error("❌ No valid native heights specified.")
            return
    except ValueError:
        print_error("❌ Invalid native height format.")
        return
    
    # Execute analysis for each height
    print_section("Multiple Heights Analysis", char="-", color=Mocha.lavender)
    
    results = {}
    for height in heights:
        print_info(f"🔍 Analyzing with native height: {height}")
        extra_args = ["-nh", str(height)]
        find_native_resolution_getfscaler(image_path, None, extra_args)
        print_info("-" * 50)
    
    print_success("✅ Multiple heights analysis completed")
    play_done_sound()


def comparative_analysis():
    """Comparative analysis between different methods."""
    print_header("📊 Comparative Analysis", color=Mocha.green)
    
    # Get input file
    image_path = get_path_with_history("🖼️ Enter image/video file path:")
    if not image_path or not os.path.exists(image_path):
        print_error("❌ Invalid file path or file does not exist.")
        return
    
    print_section("Comparative Analysis Setup", char="-", color=Mocha.lavender)
    
    # Analysis parameters
    native_height = 720.0
    height_input = input(f"📏 Native height (default: {native_height}): ").strip()
    if height_input:
        try:
            native_height = float(height_input)
        except ValueError:
            print_warning("Invalid height. Using default.")
    
    # Analysis methods
    methods = [
        ("Standard Analysis", ["-nh", str(native_height)]),
        ("Debug Analysis", ["-nh", str(native_height), "--debug"]),
        ("Conservative Crop", ["-nh", str(native_height), "-c", "4"]),
        ("Aggressive Crop", ["-nh", str(native_height), "-c", "16"])
    ]
    
    print_section("Comparative Analysis Results", char="-", color=Mocha.lavender)
    
    for method_name, args in methods:
        print_info(f"🔍 {method_name}")
        print_info("=" * 40)
        find_native_resolution_getfscaler(image_path, None, args)
        print_info("-" * 50)
    
    print_success("✅ Comparative analysis completed")
    play_done_sound()


def debug_mode_analysis():
    """Debug mode analysis with detailed output."""
    print_header("🔬 Debug Mode Analysis", color=Mocha.green)
    
    # Get input file
    image_path = get_path_with_history("🖼️ Enter image/video file path:")
    if not image_path or not os.path.exists(image_path):
        print_error("❌ Invalid file path or file does not exist.")
        return
    
    print_section("Debug Analysis Setup", char="-", color=Mocha.lavender)
    
    # Debug parameters
    native_height = 720.0
    height_input = input(f"📏 Native height (default: {native_height}): ").strip()
    if height_input:
        try:
            native_height = float(height_input)
        except ValueError:
            print_warning("Invalid height. Using default.")
    
    # Execute debug analysis
    extra_args = ["-nh", str(native_height), "--debug"]
    
    print_section("Debug Analysis Execution", char="-", color=Mocha.lavender)
    find_native_resolution_getfscaler(image_path, None, extra_args)


def help_examples_menu():
    """Help and examples menu."""
    print_header("📋 Help & Examples", color=Mocha.yellow)
    
    options = {
        "1": ("📖 Usage Guide", show_usage_guide),
        "2": ("💡 Examples", show_examples),
        "3": ("🔧 Troubleshooting", show_troubleshooting),
        "4": ("📚 Integration Guide", show_integration_guide),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Help documentation and usage examples for getfscaler integration",
        "Total Options": "4 help options",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": [
            "Usage Guide - How to use getfscaler effectively",
            "Examples - Common usage examples and patterns",
            "Troubleshooting - Common issues and solutions",
            "Integration Guide - Technical integration details"
        ],
        "Tips": [
            "Read the usage guide before starting analysis",
            "Check troubleshooting for common issues",
            "Review examples for best practices"
        ]
    }

    while True:
        key = show_menu(
            "📋 Help & Examples",
            options,
            Mocha.mauve,
            current_menu="Help & Examples",
            menu_context=menu_context
        )
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()


def show_usage_guide():
    """Show usage guide."""
    print_header("📖 getfscaler Usage Guide", color=Mocha.mauve)
    
    print_section("Basic Usage", char="-", color=Mocha.lavender)
    print_info("🔧 getfscaler analyzes images/videos to determine the best inverse scaling kernel.")
    print_info("")
    print_info("📋 Basic Command Structure:")
    print_info("  getfscaler.exe <input_file> [options]")
    print_info("")
    print_info("📋 Common Parameters:")
    print_info("  -nh, --native-height: Target native height (default: 720.0)")
    print_info("  -nw, --native-width: Target native width (auto-calculated if not specified)")
    print_info("  -c, --crop: Pixels to crop from edges (default: 8)")
    print_info("  -f, --frame: Specific frame to analyze (random if not specified)")
    print_info("  --debug: Enable debug logging")
    print_info("")
    print_info("📋 Supported Formats:")
    print_info("  Images: PNG, JPG, JPEG, BMP, TIFF, TGA")
    print_info("  Videos: MP4, MKV, AVI, MOV, WMV, FLV")
    print_info("  Scripts: VPY, PY")
    
    input("\n⏸️ Press Enter to continue...")


def show_examples():
    """Show usage examples."""
    print_header("💡 getfscaler Examples", color=Mocha.mauve)
    
    print_section("Example 1: Basic Analysis", char="-", color=Mocha.lavender)
    print_info("🔍 Analyze image with default settings:")
    print_info("  getfscaler.exe image.png")
    print_info("")
    
    print_section("Example 2: Custom Native Height", char="-", color=Mocha.lavender)
    print_info("🔍 Analyze with specific native height:")
    print_info("  getfscaler.exe image.png -nh 1080")
    print_info("")
    
    print_section("Example 3: Video Frame Analysis", char="-", color=Mocha.lavender)
    print_info("🔍 Analyze specific frame of video:")
    print_info("  getfscaler.exe video.mp4 -nh 720 -f 100")
    print_info("")
    
    print_section("Example 4: Debug Mode", char="-", color=Mocha.lavender)
    print_info("🔍 Analyze with debug information:")
    print_info("  getfscaler.exe image.png -nh 720 --debug")
    print_info("")
    
    print_section("Example 5: Custom Crop", char="-", color=Mocha.lavender)
    print_info("🔍 Analyze with custom crop value:")
    print_info("  getfscaler.exe image.png -nh 720 -c 4")
    
    input("\n⏸️ Press Enter to continue...")


def show_troubleshooting():
    """Show troubleshooting guide."""
    print_header("🔧 getfscaler Troubleshooting", color=Mocha.mauve)
    
    print_section("Common Issues", char="-", color=Mocha.lavender)
    
    print_info("❌ Issue: getfscaler.exe not found")
    print_info("💡 Solution: Ensure getfscaler.exe is in your PATH or current directory")
    print_info("")
    
    print_info("❌ Issue: VapourSynth plugin missing")
    print_info("💡 Solution: Install required VapourSynth plugins (imwri, etc.)")
    print_info("")
    
    print_info("❌ Issue: Analysis timeout")
    print_info("💡 Solution: Try smaller native height or different parameters")
    print_info("")
    
    print_info("❌ Issue: No results generated")
    print_info("💡 Solution: Check if image contains upscaled content")
    print_info("")
    
    print_info("❌ Issue: Invalid file format")
    print_info("💡 Solution: Ensure file is in supported format (PNG, JPG, MP4, etc.)")
    
    input("\n⏸️ Press Enter to continue...")


def show_integration_guide():
    """Show integration guide."""
    print_header("📚 getfscaler Integration Guide", color=Mocha.mauve)
    
    print_section("Integration Overview", char="-", color=Mocha.lavender)
    print_info("🔧 getfscaler is integrated into Dataset Forge for kernel detection.")
    print_info("")
    print_info("📋 Integration Features:")
    print_info("  ✅ Comprehensive error handling and validation")
    print_info("  ✅ Output parsing and structured results")
    print_info("  ✅ Batch processing capabilities")
    print_info("  ✅ Configuration management")
    print_info("  ✅ Advanced analysis options")
    print_info("")
    print_info("📋 Menu Integration:")
    print_info("  Main Menu → Analysis & Validation → Find Native Resolution → getfscaler")
    print_info("")
    print_info("📋 Technical Details:")
    print_info("  - Uses subprocess for executable communication")
    print_info("  - Implements timeout and error handling")
    print_info("  - Provides structured JSON output")
    print_info("  - Supports batch processing and reporting")
    
    input("\n⏸️ Press Enter to continue...")


# Export main function for use in menus
__all__ = ['getfscaler_comprehensive_menu']
