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
from dataset_forge.menus import session_state
from dataset_forge.utils.input_utils import get_folder_path


def user_profile_submenu():
    """Sub-menu for user profile management."""

    # Lazy import for user profile menu
    def get_user_profile_menu():
        from dataset_forge.utils.menu import lazy_menu

        return lazy_menu("dataset_forge.menus.user_profile_menu", "user_profile_menu")

    options = {
        "1": ("👤 Profile Management", lambda: get_user_profile_menu()()),
        "2": ("⭐ View/Edit Favorites & Presets", lambda: get_user_profile_menu()()),
        "3": ("🚀 Manage Quick Access Paths", lambda: get_user_profile_menu()()),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage user profile settings and preferences",
        "Options": "3 profile operations",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
    }

    while True:
        key = show_menu(
            "👤 User Profile",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="User Profile",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()
        # No prompt after Back


def memory_management_submenu():
    """Sub-menu for memory management."""
    from dataset_forge.utils.memory_utils import get_memory_info, clear_memory

    options = {
        "1": ("📊 View Memory Information", lambda: print_memory_info(detailed=True)),
        "2": ("🧹 Clear Memory & CUDA Cache", lambda: clear_memory()),
        "3": (
            "💡 Memory Optimization Recommendations",
            lambda: show_memory_optimization(),
        ),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage system memory and optimization",
        "Options": "3 memory operations",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
    }

    while True:
        key = show_menu(
            "🧠 Memory Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Memory Management",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options[key][1]
        if callable(action):
            action()
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()


def show_memory_optimization():
    """Show memory optimization recommendations."""
    from dataset_forge.utils.memory_utils import (
        optimize_for_large_operations,
        get_memory_info,
    )

    print_section("💡 Memory Optimization Recommendations", char="-", color=Mocha.sky)

    # Get current memory info
    memory_info = get_memory_info()

    # Get optimization recommendations
    recommendations = optimize_for_large_operations()

    print_info("📊 Current System Status:")
    if memory_info["system"]:
        sys = memory_info["system"]
        print_info(
            f"  💾 RAM Usage: {sys['used_gb']:.1f}GB / {sys['total_gb']:.1f}GB ({sys['percent_used']:.1f}%)"
        )

    if memory_info["cuda"]:
        print_info("  🎮 GPU Memory:")
        for gpu_name, gpu_info in memory_info["cuda"].items():
            print_info(
                f"    {gpu_name}: {gpu_info['allocated_gb']:.1f}GB / {gpu_info['total_gb']:.1f}GB"
            )

    print_info("\n⚙️ Recommended Settings:")
    for key, value in recommendations.items():
        if key == "warning":
            print_warning(f"  ⚠️ {value}")
        else:
            print_info(f"  {key}: {value}")


def cache_management_submenu():
    """Sub-menu for cache management."""
    # Lazy import for cache management menu
    def get_cache_management_menu():
        from dataset_forge.utils.menu import lazy_menu
        return lazy_menu("dataset_forge.menus.cache_management_menu", "cache_management_menu")
    
    options = {
        "1": ("📊 View Cache Statistics", lambda: get_cache_management_menu()()),
        "2": ("🧹 Clear Caches", lambda: get_cache_management_menu()()),
        "3": ("📈 Performance Analysis", lambda: get_cache_management_menu()()),
        "4": ("🔧 Cache Maintenance", lambda: get_cache_management_menu()()),
        "0": ("⬅️  Back", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Manage cache settings and performance",
        "Options": "4 cache operations",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
    }

    while True:
        key = show_menu(
            "⚡ Cache Management",
            options,
            header_color=Mocha.sapphire,
            char="-",
            current_menu="Cache Management",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options[key][1]
        if callable(action):
            action()
        print_prompt("\n⏸️ Press Enter to return to the menu...")
        input()


def system_settings_menu():
    """Main system and settings menu with hierarchical structure."""
    options = {
        "1": ("📁 Set HQ Folder", set_hq_folder),
        "2": ("📁 Set LQ Folder", set_lq_folder),
        "3": ("👤 User Profile Management", user_profile_submenu),
        "4": ("🧠 Memory Management", memory_management_submenu),
        "5": ("⚡ Cache Management", cache_management_submenu),
        "6": ("📊 View Current Settings", view_settings),
        "7": ("⚡ Configure Parallel Processing", configure_parallel),
        "8": ("🔄 Reset Settings", reset_settings),
        "0": ("⬅️  Back to Main Menu", None),
    }
    # Define menu context for help system
    menu_context = {
        "Purpose": "Configure system settings and preferences",
        "Total Options": "8 settings categories",
        "Navigation": "Use numbers 1-8 to select, 0 to go back",
        "Key Features": "Folder paths, user profiles, memory management, cache settings",
    }

    while True:
        key = show_menu(
            "⚙️  System & Settings",
            options,
            header_color=Mocha.lavender,
            char="=",
            current_menu="System & Settings",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()


def set_hq_folder():
    print_header("📁 Set HQ Folder", color=Mocha.sapphire)
    folder = get_folder_path("📁 Enter HQ folder path: ")
    if folder:
        session_state.hq_folder = folder
        print_success(f"✅ HQ folder set to: {folder}")
    print_prompt("\n⏸️ Press Enter to continue...")
    input()


def set_lq_folder():
    print_header("📁 Set LQ Folder", color=Mocha.sapphire)
    folder = get_folder_path("📁 Enter LQ folder path: ")
    if folder:
        session_state.lq_folder = folder
        print_success(f"✅ LQ folder set to: {folder}")
    print_prompt("\n⏸️ Press Enter to continue...")
    input()


def view_settings():
    print_header("📊 Current Settings", color=Mocha.sapphire)
    print_info(f"📁 HQ Folder: {session_state.hq_folder or '❌ Not set'}")
    print_info(f"📁 LQ Folder: {session_state.lq_folder or '❌ Not set'}")
    print_info(
        f"⚡ Max Workers: {session_state.parallel_config.get('max_workers', '🔄 Auto')}"
    )
    print_info(
        f"🔄 Processing Type: {session_state.parallel_config.get('processing_type', '🔄 Auto')}"
    )
    print_info(
        f"🎮 Use GPU: {'✅ Yes' if session_state.parallel_config.get('use_gpu', True) else '❌ No'}"
    )
    print_prompt("\n⏸️ Press Enter to continue...")
    input()


def configure_parallel():
    print_header("⚡ Configure Parallel Processing", color=Mocha.sapphire)
    try:
        max_workers = input("👥 Max workers (leave blank for auto): ").strip()
        if max_workers:
            session_state.parallel_config["max_workers"] = int(max_workers)
        else:
            session_state.parallel_config["max_workers"] = None

        processing_type = (
            input("🔄 Processing type (auto/thread/process) [auto]: ").strip() or "auto"
        )
        session_state.parallel_config["processing_type"] = processing_type

        use_gpu = input("🎮 Use GPU? (y/n) [y]: ").strip().lower() != "n"
        session_state.parallel_config["use_gpu"] = use_gpu

        print_success("✅ Parallel processing settings updated!")
    except ValueError:
        print_error("❌ Invalid input. Settings not changed.")
    print_prompt("\n⏸️ Press Enter to continue...")
    input()


def reset_settings():
    print_header("🔄 Reset Settings", color=Mocha.sapphire)
    confirm = (
        input("⚠️ Are you sure you want to reset all settings? (y/n): ").strip().lower()
    )
    if confirm == "y":
        session_state.hq_folder = None
        session_state.lq_folder = None
        session_state.parallel_config = {
            "max_workers": None,
            "processing_type": "auto",
            "use_gpu": True,
            "gpu_memory_fraction": 0.8,
            "chunk_size": 1,
            "timeout": None,
            "cpu_only": False,
        }
        print_success("✅ Settings reset to defaults!")
    print_prompt("\n⏸️ Press Enter to continue...")
    input()
