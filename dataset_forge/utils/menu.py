import importlib
import sys
from typing import Dict, Any, Optional, Callable

from .printing import (
    print_header,
    print_error,
    print_prompt,
    print_info,
    print_success,
    print_warning,
)
from .color import Mocha
from .audio_utils import play_error_sound
from .help_system import HelpSystem


def show_global_help(
    current_menu: str = "Main Menu",
    menu_context: Optional[Dict[str, Any]] = None,
    pause: bool = True,
) -> None:
    """Display global help information with context-aware content.

    Args:
        current_menu: Name of the current menu for context
        menu_context: Optional context information about the current menu
        pause: If True, prompt for Enter at the end
    """
    HelpSystem.show_menu_help(current_menu, menu_context, pause=pause)


def handle_global_command(
    command: str,
    current_menu: str = "Main Menu",
    menu_context: Optional[Dict[str, Any]] = None,
    pause: bool = True,
) -> bool:
    """Handle global commands and return True if command was handled.

    Args:
        command: The user input command
        current_menu: Name of the current menu
        menu_context: Optional context information
        pause: If True, prompt for Enter at the end (for help)

    Returns:
        True if command was handled as a global command, False otherwise
    """
    command_lower = command.lower().strip()

    if command_lower in ["help", "h", "?"]:
        show_global_help(current_menu, menu_context, pause=pause)
        return True

    elif command_lower in ["quit", "exit", "q"]:
        print_warning("\n🛑 Quitting Dataset Forge...")
        print_info("🧹 Cleaning up memory and resources...")

        # Cleanup operations
        try:
            from .memory_utils import clear_memory, clear_cuda_cache

            clear_memory()
            clear_cuda_cache()
        except Exception as e:
            print_error(f"Memory cleanup failed: {e}")

        try:
            from .audio_utils import play_shutdown_sound

            play_shutdown_sound(block=True)
        except Exception:
            pass

        print_success("👋 Thank you for using Dataset Forge!")
        sys.exit(0)

    return False


def show_menu(
    title,
    options,
    header_color,
    char="#",
    current_menu: str = "Menu",
    menu_context: Optional[Dict[str, Any]] = None,
):
    """Enhanced menu display with global command support.

    Args:
        title: Menu title
        options: Dictionary of menu options
        header_color: Color for the header
        char: Character for header decoration
        current_menu: Name of the current menu for help context
        menu_context: Optional context information for help
    """
    redraw_menu = True
    while True:
        if redraw_menu:
            print_header(title, char=char, color=header_color)
            # Display menu options
            for key, value in options.items():
                if key.lower() == "0":
                    print(
                        f"\033[38;2;249;226;175m[ {key} ]  \033[38;2;205;214;244m{value[0]}\033[0m"
                    )
                else:
                    print(
                        f"\033[38;2;137;180;250m[ {key} ]  \033[38;2;205;214;244m{value[0]}\033[0m"
                    )
            # Show global command hint on first display or after help
            print(
                f"\n{Mocha.lavender}💡 Tip: Type 'help' for global commands, 'quit' to exit{Mocha.reset}"
            )
            redraw_menu = False
        print_prompt("\nEnter your choice: ")
        choice = input().strip()
        # Handle global commands first
        if handle_global_command(choice, current_menu, menu_context, pause=True):
            redraw_menu = True
            continue
        # Handle regular menu options
        if choice in options:
            return choice
        else:
            print_error("Invalid choice. Please try again.")
            play_error_sound()
            redraw_menu = False


def lazy_action(module_name: str, func_name: str):
    """
    Returns a callable that lazy-loads and calls the specified function.
    """

    def _action(*args, **kwargs):
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func(*args, **kwargs)

    return _action


def lazy_menu(module_name: str, func_name: str):
    """
    Returns a callable that lazy-loads and calls the specified menu function.
    """

    def _menu(*args, **kwargs):
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func(*args, **kwargs)

    return _menu
