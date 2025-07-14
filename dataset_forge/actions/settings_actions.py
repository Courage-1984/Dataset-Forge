from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.input_utils import get_folder_path
from dataset_forge.menus.session_state import parallel_config, user_preferences
from dataset_forge.utils.parallel_utils import get_optimal_worker_count, ProcessingType
import os


def settings_menu_action(hq_folder, lq_folder):
    """Business logic for settings menu: set and display HQ/LQ folders and parallel processing settings."""
    while True:
        print_section("Settings", char="-", color=Mocha.sky)
        print_info(f"Current HQ Folder: {hq_folder or 'Not Set'}")
        print_info(f"Current LQ Folder: {lq_folder or 'Not Set'}")
        print("\n[1] Set HQ/LQ Folders")
        print("[2] Parallel Processing Settings")
        print("[3] User Preferences")
        print("[4] System Information")
        print("[0] Back to Main Menu")

        choice = input("Choice: ").strip()

        if choice == "1":
            hq_folder, lq_folder = set_folders(hq_folder, lq_folder)
        elif choice == "2":
            configure_parallel_processing()
        elif choice == "3":
            configure_user_preferences()
        elif choice == "4":
            show_system_information()
        elif choice == "0":
            break
        else:
            print_warning("Invalid choice. Please try again.")

    return hq_folder, lq_folder


def set_folders(hq_folder, lq_folder):
    """Set HQ and LQ folder paths."""
    print_section("Set Folders", char="-", color=Mocha.sky)
    print_info("Set the paths to your HQ and LQ image folders.")

    hq_folder = get_folder_path("Enter the path to the HQ folder: ")
    lq_folder = get_folder_path("Enter the path to the LQ folder: ")

    if hq_folder and lq_folder:
        print_success("Folders updated successfully.")
    else:
        print_warning("One or both folders were not set.")

    return hq_folder, lq_folder


def configure_parallel_processing():
    """Configure parallel processing settings."""
    print_section("Parallel Processing Settings", char="-", color=Mocha.sky)

    while True:
        print_info("Current Settings:")
        print(f"  Max Workers: {parallel_config['max_workers'] or 'Auto-detect'}")
        print(f"  Processing Type: {parallel_config['processing_type']}")
        print(f"  Use GPU: {parallel_config['use_gpu']}")
        print(f"  GPU Memory Fraction: {parallel_config['gpu_memory_fraction']}")
        print(f"  Chunk Size: {parallel_config['chunk_size']}")
        print(f"  CPU Only: {parallel_config['cpu_only']}")

        print("\n[1] Set Max Workers")
        print("[2] Set Processing Type")
        print("[3] Configure GPU Settings")
        print("[4] Set Chunk Size")
        print("[5] Reset to Defaults")
        print("[0] Back to Settings")

        choice = input("Choice: ").strip()

        if choice == "1":
            set_max_workers()
        elif choice == "2":
            set_processing_type()
        elif choice == "3":
            configure_gpu_settings()
        elif choice == "4":
            set_chunk_size()
        elif choice == "5":
            reset_parallel_settings()
        elif choice == "0":
            break
        else:
            print_warning("Invalid choice. Please try again.")


def set_max_workers():
    """Set the maximum number of workers for parallel processing."""
    print_info(f"Current CPU count: {os.cpu_count()}")
    print_info("Recommended settings:")
    print(f"  - I/O bound tasks: {get_optimal_worker_count('io')}")
    print(f"  - CPU bound tasks: {get_optimal_worker_count('cpu')}")
    print(f"  - GPU tasks: {get_optimal_worker_count('gpu')}")

    value = input("Enter max workers (or 'auto' for auto-detect): ").strip().lower()

    if value == "auto" or value == "":
        parallel_config["max_workers"] = None
        print_success("Set to auto-detect.")
    else:
        try:
            workers = int(value)
            if workers > 0:
                parallel_config["max_workers"] = workers
                print_success(f"Set max workers to {workers}.")
            else:
                print_warning("Max workers must be positive.")
        except ValueError:
            print_warning("Invalid input. Please enter a number or 'auto'.")


def set_processing_type():
    """Set the processing type for parallel operations."""
    print_info("Processing Types:")
    print("  auto: Automatically choose based on task type")
    print("  thread: Use threading (good for I/O bound tasks)")
    print("  process: Use multiprocessing (good for CPU bound tasks)")

    value = input("Enter processing type (auto/thread/process): ").strip().lower()

    if value in ["auto", "thread", "process"]:
        parallel_config["processing_type"] = value
        print_success(f"Set processing type to {value}.")
    else:
        print_warning(
            "Invalid processing type. Please choose auto, thread, or process."
        )


def configure_gpu_settings():
    """Configure GPU-related settings."""
    print_info("GPU Settings:")
    print(f"  Current Use GPU: {parallel_config['use_gpu']}")
    print(f"  Current GPU Memory Fraction: {parallel_config['gpu_memory_fraction']}")
    print(f"  Current CPU Only: {parallel_config['cpu_only']}")

    print("\n[1] Toggle GPU Usage")
    print("[2] Set GPU Memory Fraction")
    print("[3] Toggle CPU Only Mode")
    print("[0] Back")

    choice = input("Choice: ").strip()

    if choice == "1":
        parallel_config["use_gpu"] = not parallel_config["use_gpu"]
        print_success(f"GPU usage set to {parallel_config['use_gpu']}.")
    elif choice == "2":
        try:
            fraction = float(input("Enter GPU memory fraction (0.1-1.0): "))
            if 0.1 <= fraction <= 1.0:
                parallel_config["gpu_memory_fraction"] = fraction
                print_success(f"GPU memory fraction set to {fraction}.")
            else:
                print_warning("Fraction must be between 0.1 and 1.0.")
        except ValueError:
            print_warning("Invalid input. Please enter a number between 0.1 and 1.0.")
    elif choice == "3":
        parallel_config["cpu_only"] = not parallel_config["cpu_only"]
        if parallel_config["cpu_only"]:
            parallel_config["use_gpu"] = False
        print_success(f"CPU only mode set to {parallel_config['cpu_only']}.")
    elif choice == "0":
        pass
    else:
        print_warning("Invalid choice.")


def set_chunk_size():
    """Set the chunk size for process pool operations."""
    try:
        size = int(input("Enter chunk size (1-100): "))
        if 1 <= size <= 100:
            parallel_config["chunk_size"] = size
            print_success(f"Chunk size set to {size}.")
        else:
            print_warning("Chunk size must be between 1 and 100.")
    except ValueError:
        print_warning("Invalid input. Please enter a number between 1 and 100.")


def reset_parallel_settings():
    """Reset parallel processing settings to defaults."""
    parallel_config.update(
        {
            "max_workers": None,
            "processing_type": "auto",
            "use_gpu": True,
            "gpu_memory_fraction": 0.8,
            "chunk_size": 1,
            "timeout": None,
            "cpu_only": False,
        }
    )
    print_success("Parallel processing settings reset to defaults.")


def configure_user_preferences():
    """Configure user preferences."""
    print_section("User Preferences", char="-", color=Mocha.sky)

    while True:
        print_info("Current Preferences:")
        print(f"  Play Audio: {user_preferences['play_audio']}")
        print(f"  Show Progress: {user_preferences['show_progress']}")
        print(f"  Verbose Output: {user_preferences['verbose_output']}")
        print(f"  Auto Save Reports: {user_preferences['auto_save_reports']}")
        print(f"  Default Batch Size: {user_preferences['default_batch_size']}")
        print(f"  Default Quality: {user_preferences['default_quality']}")
        print(f"  Default Tile Size: {user_preferences['default_tile_size']}")
        print(
            f"  BHI Blockiness Threshold: {user_preferences['bhi_blockiness_threshold']}"
        )
        print(f"  BHI HyperIQA Threshold: {user_preferences['bhi_hyperiqa_threshold']}")
        print(f"  BHI IC9600 Threshold: {user_preferences['bhi_ic9600_threshold']}")

        print("\n[1] Toggle Audio")
        print("[2] Toggle Progress Display")
        print("[3] Toggle Verbose Output")
        print("[4] Toggle Auto Save Reports")
        print("[5] Set Default Batch Size")
        print("[6] Set Default Quality")
        print("[7] Set Default Tile Size")
        print("[8] Configure BHI Filtering Thresholds")
        print("[9] Reset to Defaults")
        print("[0] Back to Settings")

        choice = input("Choice: ").strip()

        if choice == "1":
            user_preferences["play_audio"] = not user_preferences["play_audio"]
            print_success(f"Audio set to {user_preferences['play_audio']}.")
        elif choice == "2":
            user_preferences["show_progress"] = not user_preferences["show_progress"]
            print_success(
                f"Progress display set to {user_preferences['show_progress']}."
            )
        elif choice == "3":
            user_preferences["verbose_output"] = not user_preferences["verbose_output"]
            print_success(
                f"Verbose output set to {user_preferences['verbose_output']}."
            )
        elif choice == "4":
            user_preferences["auto_save_reports"] = not user_preferences[
                "auto_save_reports"
            ]
            print_success(
                f"Auto save reports set to {user_preferences['auto_save_reports']}."
            )
        elif choice == "5":
            try:
                size = int(input("Enter default batch size (1-64): "))
                if 1 <= size <= 64:
                    user_preferences["default_batch_size"] = size
                    print_success(f"Default batch size set to {size}.")
                else:
                    print_warning("Batch size must be between 1 and 64.")
            except ValueError:
                print_warning("Invalid input. Please enter a number between 1 and 64.")
        elif choice == "6":
            try:
                quality = int(input("Enter default quality (1-100): "))
                if 1 <= quality <= 100:
                    user_preferences["default_quality"] = quality
                    print_success(f"Default quality set to {quality}.")
                else:
                    print_warning("Quality must be between 1 and 100.")
            except ValueError:
                print_warning("Invalid input. Please enter a number between 1 and 100.")
        elif choice == "7":
            try:
                tile_size = int(input("Enter default tile size (64-2048): "))
                if 64 <= tile_size <= 2048:
                    user_preferences["default_tile_size"] = tile_size
                    print_success(f"Default tile size set to {tile_size}.")
                else:
                    print_warning("Tile size must be between 64 and 2048.")
            except ValueError:
                print_warning(
                    "Invalid input. Please enter a number between 64 and 2048."
                )
        elif choice == "8":
            configure_bhi_thresholds()
        elif choice == "9":
            reset_user_preferences()
        elif choice == "0":
            break
        else:
            print_warning("Invalid choice. Please try again.")


def configure_bhi_thresholds():
    """Configure BHI filtering thresholds."""
    print_section("BHI Filtering Thresholds", char="-", color=Mocha.sky)

    while True:
        print_info("Current BHI Thresholds:")
        print(f"  Blockiness: {user_preferences['bhi_blockiness_threshold']}")
        print(f"  HyperIQA: {user_preferences['bhi_hyperiqa_threshold']}")
        print(f"  IC9600: {user_preferences['bhi_ic9600_threshold']}")

        print_info("\nSuggested Threshold Presets:")
        suggested = user_preferences["bhi_suggested_thresholds"]
        print(
            f"  Conservative: Blockiness={suggested['conservative']['blockiness']}, "
            f"HyperIQA={suggested['conservative']['hyperiqa']}, "
            f"IC9600={suggested['conservative']['ic9600']}"
        )
        print(
            f"  Moderate: Blockiness={suggested['moderate']['blockiness']}, "
            f"HyperIQA={suggested['moderate']['hyperiqa']}, "
            f"IC9600={suggested['moderate']['ic9600']}"
        )
        print(
            f"  Aggressive: Blockiness={suggested['aggressive']['blockiness']}, "
            f"HyperIQA={suggested['aggressive']['hyperiqa']}, "
            f"IC9600={suggested['aggressive']['ic9600']}"
        )

        print("\n[1] Set Blockiness Threshold")
        print("[2] Set HyperIQA Threshold")
        print("[3] Set IC9600 Threshold")
        print("[4] Use Conservative Preset")
        print("[5] Use Moderate Preset")
        print("[6] Use Aggressive Preset")
        print("[0] Back to User Preferences")

        choice = input("Choice: ").strip()

        if choice == "1":
            try:
                threshold = float(input("Enter Blockiness threshold (0.0-1.0): "))
                if 0.0 <= threshold <= 1.0:
                    user_preferences["bhi_blockiness_threshold"] = threshold
                    print_success(f"Blockiness threshold set to {threshold}.")
                else:
                    print_warning("Threshold must be between 0.0 and 1.0.")
            except ValueError:
                print_warning(
                    "Invalid input. Please enter a number between 0.0 and 1.0."
                )
        elif choice == "2":
            try:
                threshold = float(input("Enter HyperIQA threshold (0.0-1.0): "))
                if 0.0 <= threshold <= 1.0:
                    user_preferences["bhi_hyperiqa_threshold"] = threshold
                    print_success(f"HyperIQA threshold set to {threshold}.")
                else:
                    print_warning("Threshold must be between 0.0 and 1.0.")
            except ValueError:
                print_warning(
                    "Invalid input. Please enter a number between 0.0 and 1.0."
                )
        elif choice == "3":
            try:
                threshold = float(input("Enter IC9600 threshold (0.0-1.0): "))
                if 0.0 <= threshold <= 1.0:
                    user_preferences["bhi_ic9600_threshold"] = threshold
                    print_success(f"IC9600 threshold set to {threshold}.")
                else:
                    print_warning("Threshold must be between 0.0 and 1.0.")
            except ValueError:
                print_warning(
                    "Invalid input. Please enter a number between 0.0 and 1.0."
                )
        elif choice == "4":
            user_preferences["bhi_blockiness_threshold"] = suggested["conservative"][
                "blockiness"
            ]
            user_preferences["bhi_hyperiqa_threshold"] = suggested["conservative"][
                "hyperiqa"
            ]
            user_preferences["bhi_ic9600_threshold"] = suggested["conservative"][
                "ic9600"
            ]
            print_success("Applied conservative preset thresholds.")
        elif choice == "5":
            user_preferences["bhi_blockiness_threshold"] = suggested["moderate"][
                "blockiness"
            ]
            user_preferences["bhi_hyperiqa_threshold"] = suggested["moderate"][
                "hyperiqa"
            ]
            user_preferences["bhi_ic9600_threshold"] = suggested["moderate"]["ic9600"]
            print_success("Applied moderate preset thresholds.")
        elif choice == "6":
            user_preferences["bhi_blockiness_threshold"] = suggested["aggressive"][
                "blockiness"
            ]
            user_preferences["bhi_hyperiqa_threshold"] = suggested["aggressive"][
                "hyperiqa"
            ]
            user_preferences["bhi_ic9600_threshold"] = suggested["aggressive"]["ic9600"]
            print_success("Applied aggressive preset thresholds.")
        elif choice == "0":
            break
        else:
            print_warning("Invalid choice. Please try again.")


def reset_user_preferences():
    """Reset user preferences to defaults."""
    user_preferences.update(
        {
            "play_audio": True,
            "show_progress": True,
            "verbose_output": False,
            "auto_save_reports": True,
            "default_batch_size": 8,
            "default_quality": 85,
            "default_tile_size": 512,
            "bhi_blockiness_threshold": 0.5,
            "bhi_hyperiqa_threshold": 0.5,
            "bhi_ic9600_threshold": 0.5,
        }
    )
    print_success("User preferences reset to defaults.")


def show_system_information():
    """Display system information relevant to parallel processing."""
    print_section("System Information", char="-", color=Mocha.sky)

    print_info(f"CPU Count: {os.cpu_count()}")
    print_info(f"Platform: {os.name}")

    try:
        import torch

        if torch.cuda.is_available():
            print_info(f"CUDA Available: Yes")
            print_info(f"CUDA Version: {torch.version.cuda}")
            print_info(f"GPU Count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print_info(f"  GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        else:
            print_info("CUDA Available: No")
    except ImportError:
        print_info("PyTorch not available")

    try:
        import psutil

        memory = psutil.virtual_memory()
        print_info(f"Total RAM: {memory.total / 1024**3:.1f} GB")
        print_info(f"Available RAM: {memory.available / 1024**3:.1f} GB")
    except ImportError:
        print_info("psutil not available for memory information")

    input("\nPress Enter to continue...")
