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
# Lazy imports for emoji utilities to avoid circular dependencies


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
    # Handle None or empty commands gracefully
    if command is None or not isinstance(command, str):
        return False
    
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

        # Play shutdown sound non-blocking to prevent hanging
        try:
            from .audio_utils import play_shutdown_sound
            import threading
            import time

            # Play shutdown sound in a separate thread with better timeout handling
            def play_shutdown_with_timeout():
                try:
                    # Try to play the shutdown sound
                    play_shutdown_sound(block=True)
                except Exception as e:
                    print(f"Shutdown sound failed: {e}")

            shutdown_thread = threading.Thread(target=play_shutdown_with_timeout, daemon=True)
            shutdown_thread.start()
            
            # Wait for a reasonable time for the sound to play (most audio files are 1-3 seconds)
            shutdown_thread.join(timeout=3.0)
            
            # If thread is still running, let it continue in background
            if shutdown_thread.is_alive():
                print("Shutdown sound playing in background...")
            
        except Exception as e:
            print(f"Audio system error: {e}")

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
    """Display a menu with options and handle user input with emoji validation.

    Args:
        title: Menu title
        options: Dictionary of options with (description, action) tuples
        header_color: Color for the header
        char: Character to use for header decoration
        current_menu: Name of the current menu for help system
        menu_context: Optional context information for help system

    Returns:
        The selected option key or None if cancelled
    """
    # Lazy import emoji utilities to avoid circular dependencies
    try:
        from .emoji_utils import validate_menu_emojis, normalize_unicode, sanitize_emoji
        
        # Validate emojis in menu options
        emoji_issues = validate_menu_emojis(options)
        if emoji_issues["invalid"]:
            print_warning(f"⚠️  Found {len(emoji_issues['invalid'])} invalid emojis in menu options")
        
        # Normalize and sanitize the title
        safe_title = sanitize_emoji(normalize_unicode(title))
    except ImportError:
        # Fallback if emoji utilities are not available
        safe_title = title
    
    # Print header
    print_header(safe_title, char, header_color)
    print()

    # Display options with emoji safety
    for key, (description, action) in options.items():
        try:
            # Normalize and sanitize the description
            safe_description = sanitize_emoji(normalize_unicode(description))
        except (NameError, ImportError):
            # Fallback if emoji utilities are not available
            safe_description = description
        print(f"{key}. {safe_description}")

    print()

    # Get user input
    while True:
        try:
            print_prompt("Enter your choice: ")
            choice = input().strip()

            # Handle global commands
            if handle_global_command(choice, current_menu, menu_context):
                # Redraw the menu after global command
                print_header(safe_title, char, header_color)
                print()
                for key, (description, action) in options.items():
                    try:
                        safe_description = sanitize_emoji(normalize_unicode(description))
                    except (NameError, ImportError):
                        safe_description = description
                    print(f"{key}. {safe_description}")
                print()
                continue

            # Check if choice is valid
            if choice in options:
                return choice
            elif choice == "0" and "0" in options:
                return "0"
            else:
                print_error(f"Invalid choice: {choice}")
                print_info("Please enter a valid option number.")

        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            return None
        except Exception as e:
            print_error(f"Error reading input: {e}")
            return None


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
