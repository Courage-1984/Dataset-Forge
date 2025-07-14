import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import logging

from dataset_forge.menus.main_menu import main_menu

import signal
import sys

# All functionality is now organized in the new hierarchical menu structure
# See MENU_RESTRUCTURE_SUMMARY.md for details on the new organization


def _sigint_handler(signum, frame):
    try:
        from dataset_forge.utils.memory_utils import clear_memory

        clear_memory()
    except Exception as e:
        print(f"[SIGINT] Memory cleanup failed: {e}")
    # Try to gracefully quit pygame audio if running
    try:
        import pygame

        if pygame.mixer.get_init():
            pygame.mixer.quit()
            print("[SIGINT] Pygame mixer quit.")
    except ImportError:
        pass
    except Exception as e:
        print(f"[SIGINT] Pygame mixer quit failed: {e}")
    print("\n🛑 Caught Ctrl+C (SIGINT). Cleaned up memory and audio. Exiting...")
    sys.exit(130)


signal.signal(signal.SIGINT, _sigint_handler)

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

        memory_manager = get_memory_manager()
        print("🧠 Memory management system initialized successfully.")
    except Exception as e:
        print(f"⚠️ Warning: Memory management system initialization failed: {e}")

    # Minimal global logging to console. Functions can add specific file handlers.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Clear console before showing menu (optional)
    # os.system("cls" if os.name == "nt" else "clear")

    try:
        main_menu()
    finally:
        # Cleanup memory on exit
        try:
            from dataset_forge.utils.memory_utils import clear_memory

            clear_memory()
            print("🧹 Memory cleanup completed on exit.")
        except Exception as e:
            print(f"⚠️ Warning: Memory cleanup failed on exit: {e}")
