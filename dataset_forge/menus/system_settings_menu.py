from dataset_forge.utils.menu import show_menu
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
from dataset_forge.menus.settings_menu import settings_menu
from dataset_forge.menus.user_profile_menu import user_profile_menu
from dataset_forge.menus.history_log_menu import history_log_menu
from dataset_forge.menus.links_menu import links_menu
from dataset_forge.utils.memory_utils import print_memory_info, clear_memory, get_memory_info


def user_profile_submenu():
    """Sub-menu for user profile management."""
    options = {
        "1": ("Profile Management", lambda: user_profile_menu()),
        "2": ("View/Edit Favorites & Presets", lambda: user_profile_menu()),
        "3": ("Manage Quick Access Paths", lambda: user_profile_menu()),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "User Profile",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def memory_management_submenu():
    """Sub-menu for memory management."""
    options = {
        "1": ("View Memory Information", lambda: print_memory_info(detailed=True)),
        "2": ("Clear Memory & CUDA Cache", lambda: clear_memory()),
        "3": ("Memory Optimization Recommendations", lambda: show_memory_optimization()),
        "0": ("Back", None),
    }

    while True:
        action = show_menu(
            "Memory Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()
        print_prompt("\nPress Enter to return to the menu...")
        input()


def show_memory_optimization():
    """Show memory optimization recommendations."""
    from dataset_forge.utils.memory_utils import optimize_for_large_operations
    
    print_section("Memory Optimization Recommendations", char="-", color=Mocha.sky)
    
    # Get current memory info
    memory_info = get_memory_info()
    
    # Get optimization recommendations
    recommendations = optimize_for_large_operations()
    
    print_info("Current System Status:")
    if memory_info["system"]:
        sys = memory_info["system"]
        print_info(f"  RAM Usage: {sys['used_gb']:.1f}GB / {sys['total_gb']:.1f}GB ({sys['percent_used']:.1f}%)")
    
    if memory_info["cuda"]:
        print_info("  GPU Memory:")
        for gpu_name, gpu_info in memory_info["cuda"].items():
            print_info(f"    {gpu_name}: {gpu_info['allocated_gb']:.1f}GB / {gpu_info['total_gb']:.1f}GB")
    
    print_info("\nRecommended Settings:")
    for key, value in recommendations.items():
        if key == "warning":
            print_warning(f"  {value}")
        else:
            print_info(f"  {key}: {value}")


def system_settings_menu():
    """Main system and settings menu with hierarchical structure."""
    options = {
        "1": ("Set Working Directories (HQ/LQ Folders)", settings_menu),
        "2": ("User Profile", user_profile_submenu),
        "3": ("Memory Management", memory_management_submenu),
        "4": ("View Change/History Log", history_log_menu),
        "5": ("Links (Community & Personal)", links_menu),
        "0": ("Back to Main Menu", None),
    }

    while True:
        action = show_menu(
            "System & Settings",
            options,
            header_color=Mocha.lavender,
            char="=",
        )
        if action is None:
            break
        action()
