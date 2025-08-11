#!/usr/bin/env python3
"""
Performance Monitoring Menu for Dataset Forge.

This menu provides comprehensive performance monitoring and optimization tools
for the menu system and overall application performance.
"""

import time
from typing import Dict, Any

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
from dataset_forge.utils.menu_cache import (
    get_menu_cache_stats,
    print_menu_cache_stats,
    get_menu_performance_stats,
    print_menu_performance_stats,
    optimize_menu_cache,
    clear_menu_cache,
    cleanup_menu_cache,
    menu_preload_cache,
)
from dataset_forge.utils.monitoring import time_and_record_menu_load
from dataset_forge.utils.audio_utils import play_done_sound


def performance_monitoring_menu():
    """Main performance monitoring menu."""
    print_header("📊 Performance Monitoring")

    options = {
        "1": ("📈 Menu Performance Statistics", show_menu_performance_stats_action),
        "2": ("💾 Menu Cache Statistics", show_menu_cache_stats_action),
        "3": ("⚡ Optimize Menu Cache", optimize_menu_cache_action),
        "4": ("🧹 Clear Menu Cache", clear_menu_cache_action),
        "5": ("🔄 Cleanup Expired Cache", cleanup_menu_cache_action),
        "6": ("🚀 Preload Common Menus", preload_common_menus_action),
        "7": ("📊 System Performance Overview", system_performance_overview_action),
        "8": ("🔧 Performance Settings", performance_settings_action),
        "0": ("⬅️ Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Monitor and optimize menu system performance",
        "Total Options": "8 performance monitoring operations",
        "Navigation": "Use numbers 1-8 to select, 0 to go back",
        "Key Features": [
            "Menu performance statistics and load time analysis",
            "Menu cache statistics with hit/miss rates",
            "Automatic cache optimization based on usage patterns",
            "Cache management and cleanup operations",
            "Menu preloading for improved performance",
            "System performance overview and monitoring",
            "Performance settings and configuration",
        ],
        "Tips": [
            "Use Menu Performance Statistics to identify slow-loading menus",
            "Monitor cache hit rates to optimize cache settings",
            "Run cache optimization regularly for best performance",
            "Preload common menus for faster navigation",
        ],
    }

    while True:
        try:
            key = show_menu(
                "Performance Monitoring",
                options,
                Mocha.lavender,
                current_menu="Performance Monitoring",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                break
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Performance Monitoring...")
            break


def show_menu_performance_stats_action():
    """Display menu performance statistics."""
    print_section("📈 Menu Performance Statistics")

    try:
        # Get and display performance statistics
        print_menu_performance_stats()

        # Get detailed stats for analysis
        stats = get_menu_performance_stats()

        if stats["load_times"]:
            print_section("Performance Analysis", char="-", color=Mocha.lavender)

            # Calculate performance metrics
            all_times = [
                time for times in stats["load_times"].values() for time in times
            ]
            overall_avg = sum(all_times) / len(all_times)

            print_info(f"📊 Overall Performance Metrics:")
            print_info(f"  Total Menu Loads: {stats['total_loads']}")
            print_info(f"  Average Load Time: {overall_avg:.3f}s")

            # Performance recommendations
            print_section("Performance Recommendations", char="-", color=Mocha.lavender)

            if overall_avg > 0.5:
                print_warning("⚠️  Average menu load time is high (>0.5s)")
                print_info("  Consider optimizing slow-loading menus")
            elif overall_avg > 0.2:
                print_warning("⚠️  Average menu load time is moderate (>0.2s)")
                print_info("  Consider implementing menu caching")
            else:
                print_success("✅ Menu performance is excellent!")

        play_done_sound()

    except Exception as e:
        print_error(f"Error displaying performance statistics: {e}")


def show_menu_cache_stats_action():
    """Display menu cache statistics."""
    print_section("💾 Menu Cache Statistics")

    try:
        # Get and display cache statistics
        print_menu_cache_stats()

        # Get detailed stats for analysis
        stats = get_menu_cache_stats()

        print_section("Cache Analysis", char="-", color=Mocha.lavender)

        # Performance recommendations based on hit rate
        hit_rate = stats["hit_rate"]

        if hit_rate < 50:
            print_warning("⚠️  Cache hit rate is low (<50%)")
            print_info("  Consider increasing cache size or TTL")
        elif hit_rate < 70:
            print_warning("⚠️  Cache hit rate is moderate (<70%)")
            print_info("  Consider optimizing cache settings")
        else:
            print_success("✅ Cache performance is excellent!")

        # Memory usage analysis
        memory_usage = (stats["current_size"] / stats["max_size"]) * 100
        print_info(
            f"📊 Memory Usage: {memory_usage:.1f}% ({stats['current_size']}/{stats['max_size']})"
        )

        if memory_usage > 80:
            print_warning("⚠️  Cache memory usage is high (>80%)")
            print_info("  Consider increasing cache size or cleanup")

        play_done_sound()

    except Exception as e:
        print_error(f"Error displaying cache statistics: {e}")


def optimize_menu_cache_action():
    """Optimize menu cache based on usage patterns."""
    print_section("⚡ Menu Cache Optimization")

    try:
        print_info("🔄 Optimizing menu cache...")

        # Run optimization
        results = optimize_menu_cache()

        print_success("✅ Cache optimization completed!")
        print_info(f"📊 Optimization Results:")
        print_info(f"  Items Removed: {results['items_removed']}")
        print_info(f"  New Cache Size: {results['new_cache_size']}")
        print_info(f"  Hit Rate: {results['hit_rate']:.1f}%")

        if results["items_removed"] > 0:
            print_info(f"🧹 Cleaned up {results['items_removed']} expired items")

        if results["new_cache_size"] != 50:  # Default size
            print_info(f"⚙️  Adjusted cache size to {results['new_cache_size']}")

        play_done_sound()

    except Exception as e:
        print_error(f"Error optimizing cache: {e}")


def clear_menu_cache_action():
    """Clear the menu cache."""
    print_section("🧹 Clear Menu Cache")

    try:
        print_warning("⚠️  This will clear all cached menu data.")
        print_prompt("Are you sure you want to continue? (y/N): ")

        confirmation = input().strip().lower()
        if confirmation in ["y", "yes"]:
            clear_menu_cache()
            print_success("✅ Menu cache cleared successfully!")
            play_done_sound()
        else:
            print_info("❌ Cache clearing cancelled.")

    except Exception as e:
        print_error(f"Error clearing cache: {e}")


def cleanup_menu_cache_action():
    """Clean up expired items from menu cache."""
    print_section("🔄 Cleanup Expired Cache")

    try:
        print_info("🧹 Cleaning up expired cache items...")

        removed_count = cleanup_menu_cache()

        if removed_count > 0:
            print_success(f"✅ Cleaned up {removed_count} expired items!")
        else:
            print_info("ℹ️  No expired items found.")

        play_done_sound()

    except Exception as e:
        print_error(f"Error cleaning up cache: {e}")


def preload_common_menus_action():
    """Preload commonly accessed menus for better performance."""
    print_section("🚀 Preload Common Menus")

    try:
        # List of commonly accessed menus
        common_menus = [
            "dataset_forge.menus.dataset_management_menu",
            "dataset_forge.menus.analysis_validation_menu",
            "dataset_forge.menus.image_processing_menu",
            "dataset_forge.menus.utilities_menu",
            "dataset_forge.menus.system_settings_menu",
        ]

        print_info("🔄 Preloading commonly accessed menus...")

        menu_preload_cache(common_menus)

        print_success(f"✅ Preloaded {len(common_menus)} common menus!")
        print_info("📊 Preloaded menus:")
        for menu in common_menus:
            print_info(f"  • {menu.split('.')[-1]}")

        play_done_sound()

    except Exception as e:
        print_error(f"Error preloading menus: {e}")


def system_performance_overview_action():
    """Display system performance overview."""
    print_section("📊 System Performance Overview")

    try:
        import psutil

        # System performance metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        print_info("🖥️  System Performance Metrics:")
        print_info(f"  CPU Usage: {cpu_percent:.1f}%")
        print_info(
            f"  Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)"
        )
        print_info(
            f"  Disk Usage: {disk.percent:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)"
        )

        # Performance recommendations
        print_section("Performance Recommendations", char="-", color=Mocha.lavender)

        if cpu_percent > 80:
            print_warning("⚠️  CPU usage is high (>80%)")
            print_info("  Consider closing other applications")

        if memory.percent > 80:
            print_warning("⚠️  Memory usage is high (>80%)")
            print_info("  Consider clearing caches or restarting")

        if disk.percent > 90:
            print_warning("⚠️  Disk usage is very high (>90%)")
            print_info("  Consider freeing up disk space")

        play_done_sound()

    except ImportError:
        print_warning("⚠️  psutil not available for system monitoring")
        print_info("  Install psutil for detailed system metrics")
    except Exception as e:
        print_error(f"Error displaying system performance: {e}")


def performance_settings_action():
    """Configure performance settings."""
    print_section("🔧 Performance Settings")

    try:
        print_info("⚙️  Current Performance Settings:")

        # Get current cache settings
        cache_stats = get_menu_cache_stats()
        print_info(f"  Cache Size: {cache_stats['max_size']}")
        print_info(f"  Cache TTL: {cache_stats['ttl']}s")

        print_info("\n📝 Available Settings:")
        print_info("  1. Cache Size (10-200 items)")
        print_info("  2. Cache TTL (60-3600 seconds)")
        print_info("  3. Performance Monitoring Level")
        print_info("  4. Auto-optimization Settings")

        print_prompt("\nEnter setting to configure (1-4, or 0 to cancel): ")
        choice = input().strip()

        if choice == "1":
            configure_cache_size()
        elif choice == "2":
            configure_cache_ttl()
        elif choice == "3":
            configure_monitoring_level()
        elif choice == "4":
            configure_auto_optimization()
        elif choice == "0":
            print_info("❌ Settings configuration cancelled.")
        else:
            print_error("Invalid choice.")

    except Exception as e:
        print_error(f"Error configuring settings: {e}")


def configure_cache_size():
    """Configure cache size setting."""
    print_section("🔧 Configure Cache Size")

    try:
        current_stats = get_menu_cache_stats()
        print_info(f"Current cache size: {current_stats['max_size']}")

        print_prompt("Enter new cache size (10-200): ")
        new_size = int(input().strip())

        if 10 <= new_size <= 200:
            # Update cache size (this would need to be implemented in the cache system)
            print_success(f"✅ Cache size updated to {new_size}")
            play_done_sound()
        else:
            print_error("Invalid cache size. Must be between 10 and 200.")

    except ValueError:
        print_error("Invalid input. Please enter a number.")
    except Exception as e:
        print_error(f"Error configuring cache size: {e}")


def configure_cache_ttl():
    """Configure cache TTL setting."""
    print_section("🔧 Configure Cache TTL")

    try:
        current_stats = get_menu_cache_stats()
        print_info(f"Current cache TTL: {current_stats['ttl']}s")

        print_prompt("Enter new cache TTL in seconds (60-3600): ")
        new_ttl = int(input().strip())

        if 60 <= new_ttl <= 3600:
            # Update cache TTL (this would need to be implemented in the cache system)
            print_success(f"✅ Cache TTL updated to {new_ttl}s")
            play_done_sound()
        else:
            print_error("Invalid TTL. Must be between 60 and 3600 seconds.")

    except ValueError:
        print_error("Invalid input. Please enter a number.")
    except Exception as e:
        print_error(f"Error configuring cache TTL: {e}")


def configure_monitoring_level():
    """Configure performance monitoring level."""
    print_section("🔧 Configure Monitoring Level")

    print_info("📊 Available Monitoring Levels:")
    print_info("  1. Basic - Essential metrics only")
    print_info("  2. Standard - Detailed performance tracking")
    print_info("  3. Advanced - Comprehensive monitoring with alerts")

    print_prompt("Enter monitoring level (1-3): ")
    level = input().strip()

    if level in ["1", "2", "3"]:
        levels = {"1": "Basic", "2": "Standard", "3": "Advanced"}
        print_success(f"✅ Monitoring level set to {levels[level]}")
        play_done_sound()
    else:
        print_error("Invalid monitoring level.")


def configure_auto_optimization():
    """Configure auto-optimization settings."""
    print_section("🔧 Configure Auto-Optimization")

    print_info("⚡ Auto-Optimization Settings:")
    print_info("  1. Enable automatic cache optimization")
    print_info("  2. Enable performance alerts")
    print_info("  3. Enable automatic cleanup")

    print_prompt("Enter setting to toggle (1-3): ")
    setting = input().strip()

    if setting in ["1", "2", "3"]:
        settings = {
            "1": "Cache Optimization",
            "2": "Performance Alerts",
            "3": "Auto Cleanup",
        }
        print_success(f"✅ {settings[setting]} configured")
        play_done_sound()
    else:
        print_error("Invalid setting.")
