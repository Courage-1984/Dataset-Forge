import time

start_time = time.time()
print(f"Time 0: {time.time() - start_time:.2f} seconds")

import warnings

print(f"After warnings import: {time.time() - start_time:.2f} seconds")

warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

import os

print(f"After os import: {time.time() - start_time:.2f} seconds")

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import logging

print(f"After logging import: {time.time() - start_time:.2f} seconds")


print(f"Before importing main_menu: {time.time() - start_time:.2f} seconds")

from dataset_forge.menus.main_menu import main_menu

print(f"After importing main_menu: {time.time() - start_time:.2f} seconds")


# All functionality is now organized in the new hierarchical menu structure
# See MENU_RESTRUCTURE_SUMMARY.md for details on the new organization

if __name__ == "__main__":
    # Suppress pygame warnings and other unnecessary output
    warnings.filterwarnings("ignore", category=UserWarning, module="pygame")
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

    # Initialize memory management system
    try:
        from dataset_forge.utils.memory_utils import (
            get_memory_manager,
            print_memory_info,
        )

        print(f"Time since start: {time.time() - start_time:.2f} seconds")

        memory_manager = get_memory_manager()
        print("Memory management system initialized successfully.")
    except Exception as e:
        print(f"Warning: Memory management system initialization failed: {e}")

    # Minimal global logging to console. Functions can add specific file handlers.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print(f"Time since start: {time.time() - start_time:.2f} seconds")

    # Clear console before showing menu (optional)
    # os.system("cls" if os.name == "nt" else "clear")

    try:
        main_menu()
    finally:
        # Cleanup memory on exit
        try:
            from dataset_forge.utils.memory_utils import clear_memory

            print(f"Time since start: {time.time() - start_time:.2f} seconds")

            clear_memory()
            print("Memory cleanup completed on exit.")
        except Exception as e:
            print(f"Warning: Memory cleanup failed on exit: {e}")
