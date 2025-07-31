"""
cleanup_actions.py - Cleanup and Optimization Actions for Dataset Forge

Provides:
- Recursive removal of .pytest_cache folders
- Recursive removal of __pycache__ folders
- Project cleanup and optimization utilities
- Cache cleanup and maintenance
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
    print_section,
)
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.cache_utils import clear_disk_cache, clear_in_memory_cache
from dataset_forge.utils.progress_utils import smart_map


def find_cache_folders(root_path: str = ".") -> Dict[str, List[str]]:
    """
    Find all .pytest_cache and __pycache__ folders in the project.
    
    Args:
        root_path: Root directory to search from (default: current directory)
        
    Returns:
        Dictionary with 'pytest_cache' and 'pycache' lists of found paths
    """
    root = Path(root_path).resolve()
    pytest_cache_folders = []
    pycache_folders = []
    
    print_info(f"Searching for cache folders in: {root}")
    
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name == ".pytest_cache":
                pytest_cache_folders.append(str(path))
            elif path.name == "__pycache__":
                pycache_folders.append(str(path))
    
    return {
        "pytest_cache": pytest_cache_folders,
        "pycache": pycache_folders
    }


def remove_cache_folders(folders: List[str], folder_type: str) -> Tuple[int, List[str]]:
    """
    Remove cache folders and return statistics.
    
    Args:
        folders: List of folder paths to remove
        folder_type: Type of folder for logging purposes
        
    Returns:
        Tuple of (successful_removals, failed_paths)
    """
    if not folders:
        print_info(f"No {folder_type} folders found.")
        return 0, []
    
    print_section(f"Removing {folder_type} folders")
    print_info(f"Found {len(folders)} {folder_type} folders to remove")
    
    successful_removals = 0
    failed_paths = []
    
    for folder_path in folders:
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print_success(f"✓ Removed: {folder_path}")
                successful_removals += 1
            else:
                print_warning(f"⚠ Folder no longer exists: {folder_path}")
        except PermissionError as e:
            print_error(f"✗ Permission denied: {folder_path} - {e}")
            failed_paths.append(folder_path)
        except Exception as e:
            print_error(f"✗ Failed to remove: {folder_path} - {e}")
            failed_paths.append(folder_path)
    
    return successful_removals, failed_paths


def cleanup_pytest_cache() -> None:
    """Remove all .pytest_cache folders recursively from the project."""
    print_header("🧹 Pytest Cache Cleanup")
    
    # Find all .pytest_cache folders
    cache_folders = find_cache_folders()
    pytest_folders = cache_folders["pytest_cache"]
    
    if not pytest_folders:
        print_info("No .pytest_cache folders found in the project.")
        return
    
    # Remove the folders
    successful, failed = remove_cache_folders(pytest_folders, ".pytest_cache")
    
    # Summary
    print_section("Cleanup Summary")
    print_success(f"Successfully removed {successful} .pytest_cache folders")
    if failed:
        print_warning(f"Failed to remove {len(failed)} folders due to permissions or other issues")
        for failed_path in failed:
            print_info(f"  - {failed_path}")
    
    # Clear memory after cleanup
    clear_memory()
    clear_cuda_cache()


def cleanup_pycache() -> None:
    """Remove all __pycache__ folders recursively from the project."""
    print_header("🧹 Python Cache Cleanup")
    
    # Find all __pycache__ folders
    cache_folders = find_cache_folders()
    pycache_folders = cache_folders["pycache"]
    
    if not pycache_folders:
        print_info("No __pycache__ folders found in the project.")
        return
    
    # Remove the folders
    successful, failed = remove_cache_folders(pycache_folders, "__pycache__")
    
    # Summary
    print_section("Cleanup Summary")
    print_success(f"Successfully removed {successful} __pycache__ folders")
    if failed:
        print_warning(f"Failed to remove {len(failed)} folders due to permissions or other issues")
        for failed_path in failed:
            print_info(f"  - {failed_path}")
    
    # Clear memory after cleanup
    clear_memory()
    clear_cuda_cache()


def cleanup_all_cache_folders() -> None:
    """Remove all .pytest_cache and __pycache__ folders recursively from the project."""
    print_header("🧹 Complete Cache Cleanup")
    
    # Find all cache folders
    cache_folders = find_cache_folders()
    pytest_folders = cache_folders["pytest_cache"]
    pycache_folders = cache_folders["pycache"]
    
    total_folders = len(pytest_folders) + len(pycache_folders)
    
    if total_folders == 0:
        print_info("No cache folders found in the project.")
        return
    
    print_info(f"Found {len(pytest_folders)} .pytest_cache folders and {len(pycache_folders)} __pycache__ folders")
    
    # Remove pytest cache folders
    if pytest_folders:
        print_section("Removing .pytest_cache folders")
        pytest_successful, pytest_failed = remove_cache_folders(pytest_folders, ".pytest_cache")
    else:
        pytest_successful, pytest_failed = 0, []
    
    # Remove pycache folders
    if pycache_folders:
        print_section("Removing __pycache__ folders")
        pycache_successful, pycache_failed = remove_cache_folders(pycache_folders, "__pycache__")
    else:
        pycache_successful, pycache_failed = 0, []
    
    # Summary
    print_section("Complete Cleanup Summary")
    total_successful = pytest_successful + pycache_successful
    total_failed = len(pytest_failed) + len(pycache_failed)
    
    print_success(f"Successfully removed {total_successful} cache folders:")
    print_info(f"  - {pytest_successful} .pytest_cache folders")
    print_info(f"  - {pycache_successful} __pycache__ folders")
    
    if total_failed > 0:
        print_warning(f"Failed to remove {total_failed} folders due to permissions or other issues")
        if pytest_failed:
            print_info("Failed .pytest_cache folders:")
            for failed_path in pytest_failed:
                print_info(f"  - {failed_path}")
        if pycache_failed:
            print_info("Failed __pycache__ folders:")
            for failed_path in pycache_failed:
                print_info(f"  - {failed_path}")
    
    # Clear memory after cleanup
    clear_memory()
    clear_cuda_cache()


def comprehensive_cleanup() -> None:
    """Perform comprehensive cleanup including cache folders and system caches."""
    print_header("🧹 Comprehensive System Cleanup")
    
    # Step 1: Remove cache folders
    print_section("Step 1: Removing Cache Folders")
    cleanup_all_cache_folders()
    
    # Step 2: Clear system caches
    print_section("Step 2: Clearing System Caches")
    try:
        clear_disk_cache()
        print_success("✓ Disk cache cleared")
    except Exception as e:
        print_error(f"✗ Failed to clear disk cache: {e}")
    
    try:
        clear_in_memory_cache()
        print_success("✓ In-memory cache cleared")
    except Exception as e:
        print_error(f"✗ Failed to clear in-memory cache: {e}")
    
    # Step 3: Clear GPU memory
    print_section("Step 3: Clearing GPU Memory")
    try:
        clear_cuda_cache()
        print_success("✓ GPU memory cleared")
    except Exception as e:
        print_error(f"✗ Failed to clear GPU memory: {e}")
    
    # Step 4: Clear system memory
    print_section("Step 4: Clearing System Memory")
    try:
        clear_memory()
        print_success("✓ System memory cleared")
    except Exception as e:
        print_error(f"✗ Failed to clear system memory: {e}")
    
    print_section("Cleanup Complete")
    print_success("Comprehensive cleanup completed successfully!")
    print_info("All cache folders, system caches, and memory have been cleared.")


def analyze_cache_usage() -> None:
    """Analyze and display cache usage statistics."""
    print_header("📊 Cache Usage Analysis")
    
    # Find cache folders
    cache_folders = find_cache_folders()
    pytest_folders = cache_folders["pytest_cache"]
    pycache_folders = cache_folders["pycache"]
    
    print_section("Cache Folder Analysis")
    print_info(f"Found {len(pytest_folders)} .pytest_cache folders")
    print_info(f"Found {len(pycache_folders)} __pycache__ folders")
    
    # Calculate total size
    total_size = 0
    folder_sizes = {}
    
    for folder_path in pytest_folders + pycache_folders:
        try:
            folder_size = sum(
                f.stat().st_size for f in Path(folder_path).rglob('*') if f.is_file()
            )
            folder_sizes[folder_path] = folder_size
            total_size += folder_size
        except Exception as e:
            print_warning(f"Could not calculate size for {folder_path}: {e}")
    
    # Display results
    if total_size > 0:
        print_section("Size Analysis")
        print_info(f"Total cache size: {total_size / (1024*1024):.2f} MB")
        
        # Show largest folders
        sorted_folders = sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True)
        if sorted_folders:
            print_info("Largest cache folders:")
            for folder_path, size in sorted_folders[:5]:  # Top 5
                size_mb = size / (1024*1024)
                print_info(f"  - {folder_path}: {size_mb:.2f} MB")
    else:
        print_info("No cache folders found or all folders are empty.")
    
    # Recommendations
    print_section("Recommendations")
    if total_size > 100 * 1024 * 1024:  # More than 100MB
        print_warning("Large cache usage detected. Consider running cleanup.")
    elif total_size > 0:
        print_info("Moderate cache usage. Cleanup optional.")
    else:
        print_success("No cache folders found. System is clean!") 