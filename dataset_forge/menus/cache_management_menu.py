"""
Cache Management Menu for Dataset Forge

Provides comprehensive cache management capabilities:
- View cache statistics and performance
- Clear different types of caches
- Export cache analytics
- Cache warmup and preloading
- Cache integrity validation and repair
"""

import os
import json
from datetime import datetime
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
    print_section,
    print_prompt,
)
from dataset_forge.utils.cache_utils import (
    get_cache_statistics,
    cache_size_info,
    analyze_cache_performance,
    clear_all_caches,
    clear_disk_cache,
    clear_model_cache,
    clear_in_memory_cache,
    export_cache_statistics,
    validate_cache_integrity,
    repair_cache,
    warmup_cache,
    preload_cache,
    smart_cache,
    in_memory_cache,
    disk_cache,
    model_cache,
)
from dataset_forge.utils.monitoring import time_and_record_menu_load


def cache_management_menu():
    """Main cache management menu."""
    print_header("⚡ Cache Management")

    options = {
        "1": ("📊 View Cache Statistics", view_cache_statistics),
        "2": ("🧹 Clear Caches", clear_caches_menu),
        "3": ("📈 Cache Performance Analysis", cache_performance_analysis),
        "4": ("💾 Export Cache Data", export_cache_data),
        "5": ("🔧 Cache Maintenance", cache_maintenance_menu),
        "6": ("🔥 Cache Warmup", cache_warmup_menu),
        "7": ("📋 Cache Documentation", show_cache_documentation),
        "0": ("🚪 Back to Main Menu", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage and optimize caching system for improved performance",
        "Total Options": "4 cache management operations",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": "Cache statistics, clearing, maintenance, warmup",
    }

    while True:
        try:
            key = show_menu(
                "Cache Management",
                options,
                Mocha.lavender,
                current_menu="Cache Management",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Cache Management...")
            break


def view_cache_statistics():
    """Display comprehensive cache statistics."""
    print_section("📊 Cache Statistics")

    try:
        # Get cache statistics
        stats = get_cache_statistics()
        size_info = cache_size_info()

        print_info("Cache Hit/Miss Statistics:")
        print("-" * 50)

        for cache_type, data in stats.items():
            hits = data.get("hits", 0)
            misses = data.get("misses", 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0

            print(f"{cache_type.upper()}:")
            print(f"  Hits: {hits:,}")
            print(f"  Misses: {misses:,}")
            print(f"  Hit Rate: {hit_rate:.1f}%")
            print(f"  Evictions: {data.get('evictions', 0):,}")
            print()

        print_info("Cache Size Information:")
        print("-" * 50)

        for cache_type, info in size_info.items():
            if cache_type == "disk" or cache_type == "model":
                files = info.get("files", 0)
                size_mb = info.get("size_mb", 0)
                print(f"{cache_type.upper()}:")
                print(f"  Files: {files:,}")
                print(f"  Size: {size_mb:.2f} MB")
                print()

        # Show performance score
        analysis = analyze_cache_performance()
        performance_score = analysis.get("performance_score", 0)
        print_info(f"Overall Cache Performance Score: {performance_score:.1%}")

    except Exception as e:
        print_error(f"Failed to retrieve cache statistics: {e}")

    print_prompt("Press Enter to return to the menu...")
    input()


def clear_caches_menu():
    """Menu for clearing different types of caches."""
    print_section("🧹 Clear Caches")

    options = {
        "1": ("🗑️ Clear All Caches", clear_all_caches_action),
        "2": ("💾 Clear Disk Cache", clear_disk_cache_action),
        "3": ("🤖 Clear Model Cache", clear_model_cache_action),
        "4": ("🧠 Clear In-Memory Cache", clear_in_memory_cache_action),
        "0": ("🚪 Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Clear different types of caches to free up resources",
        "Options": "4 cache clearing operations",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
    }

    while True:
        try:
            key = show_menu(
                "Clear Caches",
                options,
                Mocha.lavender,
                current_menu="Clear Caches",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nReturning to Cache Management...")
            break


def clear_all_caches_action():
    """Clear all caches with confirmation."""
    print_section("🗑️ Clear All Caches")

    print_warning("This will clear ALL caches (in-memory, disk, and model).")
    print_warning("This action cannot be undone!")

    confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    if confirm in ["yes", "y"]:
        try:
            clear_all_caches()
            print_success("All caches cleared successfully!")
        except Exception as e:
            print_error(f"Failed to clear caches: {e}")
    else:
        print_info("Cache clearing cancelled.")

    print_prompt("Press Enter to return to the menu...")
    input()


def clear_disk_cache_action():
    """Clear disk cache with confirmation."""
    print_section("💾 Clear Disk Cache")

    print_warning("This will clear the persistent disk cache.")
    print_warning("Cached results will need to be recomputed.")

    confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    if confirm in ["yes", "y"]:
        try:
            clear_disk_cache()
            print_success("Disk cache cleared successfully!")
        except Exception as e:
            print_error(f"Failed to clear disk cache: {e}")
    else:
        print_info("Disk cache clearing cancelled.")

    print_prompt("Press Enter to return to the menu...")
    input()


def clear_model_cache_action():
    """Clear model cache with confirmation."""
    print_section("🤖 Clear Model Cache")

    print_warning("This will clear the model cache.")
    print_warning("Models will need to be reloaded on next use.")

    confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    if confirm in ["yes", "y"]:
        try:
            clear_model_cache()
            print_success("Model cache cleared successfully!")
        except Exception as e:
            print_error(f"Failed to clear model cache: {e}")
    else:
        print_info("Model cache clearing cancelled.")

    print_prompt("Press Enter to return to the menu...")
    input()


def clear_in_memory_cache_action():
    """Clear in-memory cache with confirmation."""
    print_section("🧠 Clear In-Memory Cache")

    print_warning("This will clear the in-memory cache.")
    print_warning("Session-only cached results will be lost.")

    confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    if confirm in ["yes", "y"]:
        try:
            clear_in_memory_cache()
            print_success("In-memory cache cleared successfully!")
        except Exception as e:
            print_error(f"Failed to clear in-memory cache: {e}")
    else:
        print_info("In-memory cache clearing cancelled.")

    print_prompt("Press Enter to return to the menu...")
    input()


def cache_performance_analysis():
    """Display detailed cache performance analysis."""
    print_section("📈 Cache Performance Analysis")

    try:
        analysis = analyze_cache_performance()

        print_info("Performance Metrics:")
        print("-" * 50)

        performance_score = analysis.get("performance_score", 0)
        print(f"Overall Performance Score: {performance_score:.1%}")

        stats = analysis.get("statistics", {})
        total_hits = sum(stats[cache_type]["hits"] for cache_type in stats)
        total_misses = sum(stats[cache_type]["misses"] for cache_type in stats)
        total_requests = total_hits + total_misses

        if total_requests > 0:
            print(f"Total Cache Requests: {total_requests:,}")
            print(f"Total Cache Hits: {total_hits:,}")
            print(f"Total Cache Misses: {total_misses:,}")
            print(f"Overall Hit Rate: {total_hits/total_requests:.1%}")

        print()
        print_info("Recommendations:")
        print("-" * 50)

        recommendations = analysis.get("recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("No specific recommendations at this time.")

        # Show cache size analysis
        size_info = analysis.get("size_info", {})
        print()
        print_info("Cache Size Analysis:")
        print("-" * 50)

        for cache_type, info in size_info.items():
            if cache_type in ["disk", "model"]:
                size_mb = info.get("size_mb", 0)
                files = info.get("files", 0)
                print(f"{cache_type.upper()}: {size_mb:.2f} MB ({files:,} files)")

                if size_mb > 1000:  # 1GB
                    print_warning(f"  ⚠️ Large {cache_type} cache detected")
                elif size_mb > 100:  # 100MB
                    print_info(f"  ℹ️ Moderate {cache_type} cache size")
                else:
                    print_success(f"  ✅ Healthy {cache_type} cache size")

    except Exception as e:
        print_error(f"Failed to analyze cache performance: {e}")

    print_prompt("Press Enter to return to the menu...")
    input()


def export_cache_data():
    """Export cache statistics and analysis to file."""
    print_section("💾 Export Cache Data")

    try:
        # Get default export path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = f"cache_statistics_{timestamp}.json"

        print_info(f"Default export path: {default_path}")
        export_path = input("Enter export path (or press Enter for default): ").strip()

        if not export_path:
            export_path = default_path

        # Ensure directory exists
        export_dir = os.path.dirname(export_path)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir, exist_ok=True)

        # Export data
        export_cache_statistics(export_path)

        # Show file info
        if os.path.exists(export_path):
            file_size = os.path.getsize(export_path)
            print_success(f"Cache data exported successfully!")
            print_info(f"File: {export_path}")
            print_info(f"Size: {file_size:,} bytes")

            # Show preview of exported data
            try:
                with open(export_path, "r") as f:
                    data = json.load(f)

                print()
                print_info("Exported Data Preview:")
                print("-" * 30)
                print(f"Timestamp: {datetime.fromtimestamp(data.get('timestamp', 0))}")
                print(f"Statistics: {len(data.get('statistics', {}))} cache types")
                print(f"Size Info: {len(data.get('size_info', {}))} cache types")
                print(f"Analysis: {len(data.get('analysis', {}))} metrics")

            except Exception as e:
                print_warning(f"Could not preview exported data: {e}")

    except Exception as e:
        print_error(f"Failed to export cache data: {e}")

    print_prompt("Press Enter to return to the menu...")
    input()


def cache_maintenance_menu():
    """Menu for cache maintenance operations."""
    print_section("🔧 Cache Maintenance")

    options = {
        "1": ("🔍 Validate Cache Integrity", validate_cache_integrity_action),
        "2": ("🔧 Repair Cache", repair_cache_action),
        "3": ("📊 Cache Health Check", cache_health_check),
        "0": ("🚪 Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Maintain and optimize cache system performance",
        "Options": "3 maintenance operations",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
    }

    while True:
        try:
            key = show_menu(
                "Cache Maintenance",
                options,
                Mocha.lavender,
                current_menu="Cache Maintenance",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nReturning to Cache Management...")
            break


def validate_cache_integrity_action():
    """Validate cache integrity and report issues."""
    print_section("🔍 Validate Cache Integrity")

    try:
        print_info("Validating cache integrity...")
        results = validate_cache_integrity()

        print_info("Validation Results:")
        print("-" * 50)

        all_valid = True
        for cache_type, is_valid in results.items():
            status = "✅ Valid" if is_valid else "❌ Issues Found"
            print(f"{cache_type.replace('_', ' ').title()}: {status}")
            if not is_valid:
                all_valid = False

        if all_valid:
            print_success("All caches are valid!")
        else:
            print_warning("Some cache issues were detected.")
            print_info("Consider running cache repair.")

    except Exception as e:
        print_error(f"Failed to validate cache integrity: {e}")

    print_prompt("Press Enter to return to the menu...")
    input()


def repair_cache_action():
    """Repair corrupted cache files."""
    print_section("🔧 Repair Cache")

    print_warning("This will attempt to repair corrupted cache files.")
    print_warning("Corrupted files will be removed.")

    confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    if confirm in ["yes", "y"]:
        try:
            repair_cache()
            print_success("Cache repair completed!")
        except Exception as e:
            print_error(f"Failed to repair cache: {e}")
    else:
        print_info("Cache repair cancelled.")

    print_prompt("Press Enter to return to the menu...")
    input()


def cache_health_check():
    """Perform a comprehensive cache health check."""
    print_section("📊 Cache Health Check")

    try:
        # Get all cache information
        stats = get_cache_statistics()
        size_info = cache_size_info()
        analysis = analyze_cache_performance()

        print_info("Cache Health Report:")
        print("=" * 60)

        # Overall health score
        performance_score = analysis.get("performance_score", 0)
        if performance_score >= 0.8:
            health_status = "🟢 Excellent"
        elif performance_score >= 0.6:
            health_status = "🟡 Good"
        elif performance_score >= 0.4:
            health_status = "🟠 Fair"
        else:
            health_status = "🔴 Poor"

        print(f"Overall Health: {health_status} ({performance_score:.1%})")
        print()

        # Check each cache type
        for cache_type in ["in_memory", "disk", "model"]:
            cache_stats = stats.get(cache_type, {})
            hits = cache_stats.get("hits", 0)
            misses = cache_stats.get("misses", 0)
            total = hits + misses

            if total > 0:
                hit_rate = hits / total
                if hit_rate >= 0.8:
                    status = "🟢 Good"
                elif hit_rate >= 0.6:
                    status = "🟡 Fair"
                else:
                    status = "🔴 Poor"

                print(f"{cache_type.upper()}: {status} ({hit_rate:.1%} hit rate)")
            else:
                print(f"{cache_type.upper()}: ⚪ No Data")

        print()

        # Size analysis
        print_info("Storage Analysis:")
        total_size_mb = 0
        for cache_type, info in size_info.items():
            if cache_type in ["disk", "model"]:
                size_mb = info.get("size_mb", 0)
                total_size_mb += size_mb
                files = info.get("files", 0)

                if size_mb > 1000:
                    status = "🔴 Large"
                elif size_mb > 100:
                    status = "🟡 Moderate"
                else:
                    status = "🟢 Healthy"

                print(
                    f"{cache_type.upper()}: {status} ({size_mb:.1f} MB, {files:,} files)"
                )

        print(f"Total Cache Size: {total_size_mb:.1f} MB")

        # Recommendations
        print()
        print_info("Health Recommendations:")
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("✅ Cache health is good!")

    except Exception as e:
        print_error(f"Failed to perform health check: {e}")

    print_prompt("Press Enter to return to the menu...")
    input()


def cache_warmup_menu():
    """Menu for cache warmup operations."""
    print_section("🔥 Cache Warmup")

    options = {
        "1": ("🚀 Quick Warmup", quick_cache_warmup),
        "2": ("📋 Custom Warmup", custom_cache_warmup),
        "3": ("🔄 Warmup Common Operations", warmup_common_operations),
        "0": ("🚪 Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Warm up caches for improved performance",
        "Options": "3 warmup operations",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
    }

    while True:
        try:
            key = show_menu(
                "Cache Warmup",
                options,
                Mocha.lavender,
                current_menu="Cache Warmup",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nReturning to Cache Management...")
            break


def quick_cache_warmup():
    """Perform a quick cache warmup with common operations."""
    print_section("🚀 Quick Cache Warmup")

    try:
        print_info("Performing quick cache warmup...")

        # Define common warmup operations
        warmup_operations = [
            # Add common operations that benefit from caching
            # This is a placeholder - actual operations would depend on what's available
        ]

        if warmup_operations:
            warmup_cache(warmup_operations)
            print_success("Quick cache warmup completed!")
        else:
            print_info("No warmup operations defined.")
            print_info("Use custom warmup to specify operations.")

    except Exception as e:
        print_error(f"Failed to perform quick warmup: {e}")

    print_prompt("Press Enter to return to the menu...")
    input()


def custom_cache_warmup():
    """Perform custom cache warmup with user-specified operations."""
    print_section("📋 Custom Cache Warmup")

    print_info("Custom warmup allows you to specify functions to preload.")
    print_info("This is useful for preparing caches before intensive operations.")

    print_warning("Custom warmup requires knowledge of available functions.")
    print_warning("Incorrect function calls may cause errors.")

    confirm = (
        input("Do you want to proceed with custom warmup? (yes/no): ").strip().lower()
    )
    if confirm not in ["yes", "y"]:
        print_info("Custom warmup cancelled.")
        print_prompt("Press Enter to return to the menu...")
        input()
        return

    try:
        # This would be implemented based on available functions
        print_info("Custom warmup functionality would be implemented here.")
        print_info(
            "It would allow users to specify functions and arguments to preload."
        )

    except Exception as e:
        print_error(f"Failed to perform custom warmup: {e}")

    print_prompt("Press Enter to return to the menu...")
    input()


def warmup_common_operations():
    """Warmup cache with common Dataset Forge operations."""
    print_section("🔄 Warmup Common Operations")

    try:
        print_info("Warming up cache for common operations...")

        # This would warm up common operations like:
        # - Image analysis functions
        # - Model loading functions
        # - Directory scanning functions
        # - etc.

        print_info("Common operations warmup would be implemented here.")
        print_info("It would preload frequently used functions.")

    except Exception as e:
        print_error(f"Failed to warmup common operations: {e}")

    print_prompt("Press Enter to return to the menu...")
    input()


def show_cache_documentation():
    """Show cache system documentation and usage examples."""
    print_section("📋 Cache Documentation")

    print_info("Dataset Forge Advanced Caching System")
    print_header("", char="=", color=Mocha.lavender)

    print_info("Cache Types:")
    print_header("", char="-", color=Mocha.lavender)
    print_info("🧠 In-Memory Cache: Fast, session-only results")
    print_info("💾 Disk Cache: Persistent, cross-session results")
    print_info("🤖 Model Cache: Specialized for model loading")
    print_info("🧠 Smart Cache: Auto-detects best strategy")

    print_info("")
    print_info("Usage Examples:")
    print_header("", char="-", color=Mocha.lavender)
    print_info("@in_memory_cache(maxsize=128, ttl_seconds=3600)")
    print_info("@disk_cache(compression=True, ttl_seconds=86400)")
    print_info("@model_cache(maxsize=10)")
    print_info("@smart_cache(cache_type='auto')")

    print_info("")
    print_info("Cache Management:")
    print_header("", char="-", color=Mocha.lavender)
    print_info("• View statistics and performance metrics")
    print_info("• Clear specific cache types")
    print_info("• Export cache data for analysis")
    print_info("• Validate and repair cache integrity")
    print_info("• Warm up cache for better performance")

    print_info("")
    print_info("Best Practices:")
    print_header("", char="-", color=Mocha.lavender)
    print_info("• Use in-memory cache for frequently accessed data")
    print_info("• Use disk cache for expensive computations")
    print_info("• Use model cache for model loading operations")
    print_info("• Monitor cache performance regularly")
    print_info("• Clear caches when disk space is low")

    print_prompt("Press Enter to return to the menu...")
    input()


# Export the main menu function for integration
__all__ = ["cache_management_menu"]
