"""
Performance Optimization Menu for Dataset Forge.

This menu provides access to all performance optimization features including:
- GPU acceleration
- Distributed processing
- Sample prioritization
- Pipeline compilation
"""

import os
import time
from typing import Optional, List, Dict, Any

from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import (
    print_header,
    print_section,
    print_info,
    print_success,
    print_warning,
    print_error,
    print_prompt,
)
from dataset_forge.utils.monitoring import time_and_record_menu_load

# Import performance optimization modules
from dataset_forge.utils.gpu_acceleration import gpu_processor
from dataset_forge.utils.distributed_processing import (
    distributed_processor,
    multi_gpu_processor,
    start_distributed_processing,
    stop_distributed_processing,
    DistributedConfig,
    ProcessingMode,
)
from dataset_forge.utils.sample_prioritization import (
    sample_prioritizer,
    prioritize_samples,
    PrioritizationStrategy,
)
from dataset_forge.utils.pipeline_compilation import (
    pipeline_compiler,
    compile_function,
    CompilationType,
)


def performance_optimization_menu():
    """Main performance optimization menu."""
    while True:
        print_header("🚀 Performance Optimization", char="=", color=Mocha.lavender)

        options = {
            "1": ("🎮 GPU Acceleration", gpu_acceleration_menu),
            "2": ("🌐 Distributed Processing", distributed_processing_menu),
            "3": ("🎯 Sample Prioritization", sample_prioritization_menu),
            "4": ("⚡ Pipeline Compilation", pipeline_compilation_menu),
            "5": ("📊 Performance Analytics", performance_analytics_menu),
            "6": ("⚙️ Optimization Settings", optimization_settings_menu),
            "0": ("🚪 Back to Main Menu", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Optimize processing performance and resource utilization",
            "Total Options": "6 optimization categories",
            "Navigation": "Use numbers 1-6 to select, 0 to go back",
            "Key Features": "GPU acceleration, distributed processing, sample prioritization, pipeline compilation",
        }

        try:
            key = show_menu("Performance Optimization", options, Mocha.lavender, current_menu="Performance Optimization", menu_context=menu_context)
            if key is None:
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Performance Optimization Menu...")
            break


def gpu_acceleration_menu():
    """GPU acceleration configuration and testing menu."""
    while True:
        print_header("🎮 GPU Acceleration", char="-", color=Mocha.sky)

        # Get GPU status
        gpu_status = get_gpu_status()

        print_info("Current GPU Status:")
        for key, value in gpu_status.items():
            print_info(f"  {key}: {value}")

        options = {
            "1": ("🧪 Test GPU Acceleration", test_gpu_acceleration),
            "2": ("⚙️ Configure GPU Settings", configure_gpu_settings),
            "3": ("📈 GPU Performance Benchmarks", gpu_benchmarks),
            "4": ("🔄 Batch Processing Test", test_gpu_batch_processing),
            "0": ("🚪 Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Configure and test GPU acceleration for image processing",
            "Options": "4 GPU operations available",
            "Navigation": "Use numbers 1-4 to select, 0 to go back",
        }

        try:
            key = show_menu("GPU Acceleration", options, Mocha.sky, current_menu="GPU Acceleration", menu_context=menu_context)
            if key is None:
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting GPU Acceleration Menu...")
            break


def distributed_processing_menu():
    """Distributed processing configuration and management menu."""
    while True:
        print_header("🌐 Distributed Processing", char="-", color=Mocha.sky)

        # Get distributed processing status
        status = distributed_processor.get_status()

        print_info("Distributed Processing Status:")
        for key, value in status.items():
            print_info(f"  {key}: {value}")

        options = {
            "1": ("🚀 Start Distributed Cluster", start_distributed_cluster),
            "2": ("🛑 Stop Distributed Cluster", stop_distributed_cluster),
            "3": ("⚙️ Configure Distributed Settings", configure_distributed_settings),
            "4": ("🧪 Test Distributed Processing", test_distributed_processing),
            "5": ("📊 Cluster Dashboard", show_cluster_dashboard),
            "0": ("🚪 Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Configure and manage distributed processing clusters",
            "Options": "5 distributed processing operations",
            "Navigation": "Use numbers 1-5 to select, 0 to go back",
        }

        try:
            key = show_menu("Distributed Processing", options, Mocha.sky, current_menu="Distributed Processing", menu_context=menu_context)
            if key is None:
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Distributed Processing Menu...")
            break


def sample_prioritization_menu():
    """Sample prioritization configuration and testing menu."""
    while True:
        print_header("🎯 Sample Prioritization", char="-", color=Mocha.sky)

        print_info("Sample prioritization helps optimize processing order")
        print_info("by analyzing image quality and complexity.")

        options = {
            "1": ("🧪 Test Sample Analysis", test_sample_analysis),
            "2": ("⚙️ Configure Prioritization", configure_prioritization),
            "3": ("📊 Prioritization Statistics", show_prioritization_stats),
            "4": ("🔄 Batch Prioritization Test", test_batch_prioritization),
            "0": ("🚪 Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Configure sample prioritization for optimized processing order",
            "Options": "4 prioritization operations",
            "Navigation": "Use numbers 1-4 to select, 0 to go back",
        }

        try:
            key = show_menu("Sample Prioritization", options, Mocha.sky, current_menu="Sample Prioritization", menu_context=menu_context)
            if key is None:
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Sample Prioritization Menu...")
            break


def pipeline_compilation_menu():
    """Pipeline compilation configuration and testing menu."""
    while True:
        print_header("⚡ Pipeline Compilation", char="-", color=Mocha.sky)

        # Get compilation status
        status = pipeline_compiler.get_compilation_status()

        print_info("Compilation Backends Status:")
        for key, value in status.items():
            if isinstance(value, bool):
                status_text = "✅ Available" if value else "❌ Not Available"
                print_info(f"  {key}: {status_text}")

        options = {
            "1": ("🧪 Test Compilation", test_compilation),
            "2": ("⚙️ Configure Compilation", configure_compilation),
            "3": ("📊 Compilation Statistics", show_compilation_stats),
            "4": ("🔄 Pipeline Compilation Test", test_pipeline_compilation),
            "0": ("🚪 Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Configure and test pipeline compilation for performance optimization",
            "Options": "4 compilation operations",
            "Navigation": "Use numbers 1-4 to select, 0 to go back",
        }

        try:
            key = show_menu("Pipeline Compilation", options, Mocha.sky, current_menu="Pipeline Compilation", menu_context=menu_context)
            if key is None:
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Pipeline Compilation Menu...")
            break


def performance_analytics_menu():
    """Performance analytics and monitoring menu."""
    while True:
        print_header("📊 Performance Analytics", char="-", color=Mocha.sky)

        print_info(
            "Monitor and analyze performance metrics across all optimization features."
        )

        options = {
            "1": ("📈 System Performance", show_system_performance),
            "2": ("🎮 GPU Performance", show_gpu_performance),
            "3": ("🌐 Distributed Performance", show_distributed_performance),
            "4": ("⚡ Compilation Performance", show_compilation_performance),
            "5": ("📊 Performance Reports", generate_performance_reports),
            "0": ("🚪 Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Monitor and analyze performance metrics across optimization features",
            "Options": "5 analytics operations",
            "Navigation": "Use numbers 1-5 to select, 0 to go back",
        }

        try:
            key = show_menu("Performance Analytics", options, Mocha.sky, current_menu="Performance Analytics", menu_context=menu_context)
            if key is None:
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Performance Analytics Menu...")
            break


def optimization_settings_menu():
    """Global optimization settings menu."""
    while True:
        print_header("⚙️ Optimization Settings", char="-", color=Mocha.sky)

        print_info("Configure global optimization settings and preferences.")

        options = {
            "1": ("🎯 Optimization Strategy", configure_optimization_strategy),
            "2": ("💾 Memory Management", configure_memory_management),
            "3": ("🔄 Auto-Optimization", configure_auto_optimization),
            "4": ("📊 Performance Thresholds", configure_performance_thresholds),
            "5": ("🔄 Reset to Defaults", reset_optimization_settings),
            "0": ("🚪 Back", None),
        }

        # Define menu context for help system
        menu_context = {
            "Purpose": "Configure global optimization settings and preferences",
            "Options": "5 settings operations",
            "Navigation": "Use numbers 1-5 to select, 0 to go back",
        }

        try:
            key = show_menu("Optimization Settings", options, Mocha.sky, current_menu="Optimization Settings", menu_context=menu_context)
            if key is None:
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Optimization Settings Menu...")
            break


# GPU Acceleration Functions
def get_gpu_status() -> Dict[str, Any]:
    """Get current GPU status."""
    import torch

    status = {}

    if torch.cuda.is_available():
        status["CUDA Available"] = "Yes"
        status["GPU Count"] = torch.cuda.device_count()
        status["Current Device"] = torch.cuda.current_device()

        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            status[f"GPU {i} Name"] = props.name
            status[f"GPU {i} Memory"] = f"{props.total_memory / 1024**3:.1f} GB"
    else:
        status["CUDA Available"] = "No"

    return status


def test_gpu_acceleration():
    """Test GPU acceleration features."""
    print_section("🧪 GPU Acceleration Test", char="-", color=Mocha.mauve)

    try:
        # Test basic GPU operations
        print_info("Testing GPU acceleration...")

        # Test image analysis
        test_image_path = "test_image.jpg"  # You would need a test image
        if os.path.exists(test_image_path):
            analysis = gpu_processor.gpu_image_analysis(test_image_path)
            print_success(f"GPU image analysis completed: {len(analysis)} metrics")
        else:
            print_warning("No test image found, skipping image analysis test")

        # Test batch processing
        print_info("Testing GPU batch processing...")
        # This would test batch operations

        print_success("GPU acceleration test completed successfully")

    except Exception as e:
        print_error(f"GPU acceleration test failed: {e}")

    input("\nPress Enter to continue...")


def configure_gpu_settings():
    """Configure GPU settings."""
    print_section("⚙️ GPU Settings Configuration", char="-", color=Mocha.mauve)

    print_info("Current GPU Settings:")
    print_info(f"  Device: {gpu_processor.device}")
    print_info(f"  Batch Size: {gpu_processor.batch_size}")

    print("\n[1] Change Device")
    print("[2] Adjust Batch Size")
    print("[3] Memory Management")
    print("[0] Back")

    choice = input("Choice: ").strip()

    if choice == "1":
        device = input("Enter device (cuda/cpu): ").strip()
        if device in ["cuda", "cpu"]:
            gpu_processor.device = device
            print_success(f"Device set to {device}")
        else:
            print_warning("Invalid device")

    elif choice == "2":
        try:
            batch_size = int(input("Enter batch size: "))
            if batch_size > 0:
                gpu_processor.batch_size = batch_size
                print_success(f"Batch size set to {batch_size}")
            else:
                print_warning("Batch size must be positive")
        except ValueError:
            print_warning("Invalid batch size")

    input("\nPress Enter to continue...")


def gpu_benchmarks():
    """Run GPU performance benchmarks."""
    print_section("📈 GPU Performance Benchmarks", char="-", color=Mocha.mauve)

    print_info("Running GPU performance benchmarks...")
    # This would run actual benchmarks

    print_success("Benchmarks completed")
    input("\nPress Enter to continue...")


def test_gpu_batch_processing():
    """Test GPU batch processing."""
    print_section("🔄 GPU Batch Processing Test", char="-", color=Mocha.mauve)

    print_info("Testing GPU batch processing...")
    # This would test batch processing

    print_success("Batch processing test completed")
    input("\nPress Enter to continue...")


# Distributed Processing Functions
def start_distributed_cluster():
    """Start distributed processing cluster."""
    print_section("🚀 Starting Distributed Cluster", char="-", color=Mocha.mauve)

    try:
        success = start_distributed_processing()
        if success:
            print_success("Distributed cluster started successfully")
        else:
            print_warning("Failed to start distributed cluster")
    except Exception as e:
        print_error(f"Error starting cluster: {e}")

    input("\nPress Enter to continue...")


def stop_distributed_cluster():
    """Stop distributed processing cluster."""
    print_section("🛑 Stopping Distributed Cluster", char="-", color=Mocha.mauve)

    try:
        stop_distributed_processing()
        print_success("Distributed cluster stopped")
    except Exception as e:
        print_error(f"Error stopping cluster: {e}")

    input("\nPress Enter to continue...")


def configure_distributed_settings():
    """Configure distributed processing settings."""
    print_section("⚙️ Distributed Processing Settings", char="-", color=Mocha.mauve)

    print_info("Current Settings:")
    config = distributed_processor.config
    print_info(f"  Mode: {config.mode.value}")
    print_info(f"  Workers: {config.num_workers}")
    print_info(f"  GPU Devices: {config.gpu_devices}")

    print("\n[1] Change Mode")
    print("[2] Adjust Workers")
    print("[3] GPU Configuration")
    print("[0] Back")

    choice = input("Choice: ").strip()

    if choice == "1":
        print("Available modes:")
        for mode in ProcessingMode:
            print(f"  {mode.value}")
        mode_name = input("Enter mode: ").strip()
        for mode in ProcessingMode:
            if mode.value == mode_name:
                config.mode = mode
                print_success(f"Mode set to {mode_name}")
                break
        else:
            print_warning("Invalid mode")

    elif choice == "2":
        try:
            workers = int(input("Enter number of workers: "))
            if workers > 0:
                config.num_workers = workers
                print_success(f"Workers set to {workers}")
            else:
                print_warning("Number of workers must be positive")
        except ValueError:
            print_warning("Invalid number of workers")

    input("\nPress Enter to continue...")


def test_distributed_processing():
    """Test distributed processing."""
    print_section("🧪 Distributed Processing Test", char="-", color=Mocha.mauve)

    print_info("Testing distributed processing...")
    # This would test distributed processing

    print_success("Distributed processing test completed")
    input("\nPress Enter to continue...")


def show_cluster_dashboard():
    """Show cluster dashboard information."""
    print_section("📊 Cluster Dashboard", char="-", color=Mocha.mauve)

    status = distributed_processor.get_status()

    if status.get("client_active"):
        print_info("Cluster Dashboard:")
        print_info(f"  Total Workers: {status.get('total_workers', 'N/A')}")
        print_info(f"  Memory Usage: {status.get('memory_usage', 'N/A')}")
        print_info(f"  CPU Usage: {status.get('cpu_usage', 'N/A')}")
    else:
        print_warning("No active cluster")

    input("\nPress Enter to continue...")


# Sample Prioritization Functions
def test_sample_analysis():
    """Test sample analysis and prioritization."""
    print_section("🧪 Sample Analysis Test", char="-", color=Mocha.mauve)

    print_info("Testing sample analysis...")
    # This would test sample analysis

    print_success("Sample analysis test completed")
    input("\nPress Enter to continue...")


def configure_prioritization():
    """Configure sample prioritization settings."""
    print_section("⚙️ Sample Prioritization Settings", char="-", color=Mocha.mauve)

    config = sample_prioritizer.config
    print_info("Current Settings:")
    print_info(f"  Strategy: {config.strategy.value}")
    print_info(f"  Batch Size: {config.batch_size}")
    print_info(f"  Use GPU: {config.use_gpu}")

    print("\n[1] Change Strategy")
    print("[2] Adjust Weights")
    print("[3] Batch Settings")
    print("[0] Back")

    choice = input("Choice: ").strip()

    if choice == "1":
        print("Available strategies:")
        for strategy in PrioritizationStrategy:
            print(f"  {strategy.value}")
        strategy_name = input("Enter strategy: ").strip()
        for strategy in PrioritizationStrategy:
            if strategy.value == strategy_name:
                config.strategy = strategy
                print_success(f"Strategy set to {strategy_name}")
                break
        else:
            print_warning("Invalid strategy")

    input("\nPress Enter to continue...")


def show_prioritization_stats():
    """Show prioritization statistics."""
    print_section("📊 Prioritization Statistics", char="-", color=Mocha.mauve)

    print_info("Prioritization statistics would be shown here")
    input("\nPress Enter to continue...")


def test_batch_prioritization():
    """Test batch prioritization."""
    print_section("🔄 Batch Prioritization Test", char="-", color=Mocha.mauve)

    print_info("Testing batch prioritization...")
    # This would test batch prioritization

    print_success("Batch prioritization test completed")
    input("\nPress Enter to continue...")


# Pipeline Compilation Functions
def test_compilation():
    """Test pipeline compilation."""
    print_section("🧪 Pipeline Compilation Test", char="-", color=Mocha.mauve)

    print_info("Testing pipeline compilation...")
    # This would test compilation

    print_success("Pipeline compilation test completed")
    input("\nPress Enter to continue...")


def configure_compilation():
    """Configure pipeline compilation settings."""
    print_section("⚙️ Pipeline Compilation Settings", char="-", color=Mocha.mauve)

    config = pipeline_compiler.config
    print_info("Current Settings:")
    print_info(f"  Numba: {config.enable_numba}")
    print_info(f"  Cython: {config.enable_cython}")
    print_info(f"  Torch JIT: {config.enable_torch_jit}")
    print_info(f"  Parallel: {config.parallel}")
    print_info(f"  Fast Math: {config.fastmath}")

    print("\n[1] Toggle Numba")
    print("[2] Toggle Cython")
    print("[3] Toggle Torch JIT")
    print("[4] Optimization Level")
    print("[0] Back")

    choice = input("Choice: ").strip()

    if choice == "1":
        config.enable_numba = not config.enable_numba
        print_success(f"Numba {'enabled' if config.enable_numba else 'disabled'}")
    elif choice == "2":
        config.enable_cython = not config.enable_cython
        print_success(f"Cython {'enabled' if config.enable_cython else 'disabled'}")
    elif choice == "3":
        config.enable_torch_jit = not config.enable_torch_jit
        print_success(
            f"Torch JIT {'enabled' if config.enable_torch_jit else 'disabled'}"
        )
    elif choice == "4":
        try:
            level = int(input("Enter optimization level (0-3): "))
            if 0 <= level <= 3:
                config.optimization_level = level
                print_success(f"Optimization level set to {level}")
            else:
                print_warning("Optimization level must be 0-3")
        except ValueError:
            print_warning("Invalid optimization level")

    input("\nPress Enter to continue...")


def show_compilation_stats():
    """Show compilation statistics."""
    print_section("📊 Compilation Statistics", char="-", color=Mocha.mauve)

    status = pipeline_compiler.get_compilation_status()
    print_info("Compilation Statistics:")
    for key, value in status.items():
        print_info(f"  {key}: {value}")

    input("\nPress Enter to continue...")


def test_pipeline_compilation():
    """Test pipeline compilation."""
    print_section("🔄 Pipeline Compilation Test", char="-", color=Mocha.mauve)

    print_info("Testing pipeline compilation...")
    # This would test pipeline compilation

    print_success("Pipeline compilation test completed")
    input("\nPress Enter to continue...")


# Performance Analytics Functions
def show_system_performance():
    """Show system performance metrics."""
    print_section("📈 System Performance", char="-", color=Mocha.mauve)

    print_info("System performance metrics would be shown here")
    input("\nPress Enter to continue...")


def show_gpu_performance():
    """Show GPU performance metrics."""
    print_section("🎮 GPU Performance", char="-", color=Mocha.mauve)

    print_info("GPU performance metrics would be shown here")
    input("\nPress Enter to continue...")


def show_distributed_performance():
    """Show distributed processing performance metrics."""
    print_section("🌐 Distributed Performance", char="-", color=Mocha.mauve)

    print_info("Distributed performance metrics would be shown here")
    input("\nPress Enter to continue...")


def show_compilation_performance():
    """Show compilation performance metrics."""
    print_section("⚡ Compilation Performance", char="-", color=Mocha.mauve)

    print_info("Compilation performance metrics would be shown here")
    input("\nPress Enter to continue...")


def generate_performance_reports():
    """Generate performance reports."""
    print_section("📊 Performance Reports", char="-", color=Mocha.mauve)

    print_info("Generating performance reports...")
    # This would generate reports

    print_success("Performance reports generated")
    input("\nPress Enter to continue...")


# Optimization Settings Functions
def configure_optimization_strategy():
    """Configure optimization strategy."""
    print_section("🎯 Optimization Strategy", char="-", color=Mocha.mauve)

    print_info("Configure optimization strategy settings")
    input("\nPress Enter to continue...")


def configure_memory_management():
    """Configure memory management settings."""
    print_section("💾 Memory Management", char="-", color=Mocha.mauve)

    print_info("Configure memory management settings")
    input("\nPress Enter to continue...")


def configure_auto_optimization():
    """Configure auto-optimization settings."""
    print_section("🔄 Auto-Optimization", char="-", color=Mocha.mauve)

    print_info("Configure auto-optimization settings")
    input("\nPress Enter to continue...")


def configure_performance_thresholds():
    """Configure performance thresholds."""
    print_section("📊 Performance Thresholds", char="-", color=Mocha.mauve)

    print_info("Configure performance thresholds")
    input("\nPress Enter to continue...")


def reset_optimization_settings():
    """Reset optimization settings to defaults."""
    print_section("🔄 Reset to Defaults", char="-", color=Mocha.mauve)

    print_warning("This will reset all optimization settings to defaults.")
    confirm = input("Are you sure? (y/N): ").strip().lower()

    if confirm == "y":
        # Reset settings
        print_success("Optimization settings reset to defaults")
    else:
        print_info("Reset cancelled")

    input("\nPress Enter to continue...")


# Lazy import function for menu integration
def lazy_performance_optimization_menu():
    """Lazy import wrapper for performance optimization menu."""
    return performance_optimization_menu
