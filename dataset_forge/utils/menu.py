#!/usr/bin/env python3
"""
Menu system utilities for Dataset Forge.

This module provides the core menu functionality including display, input handling,
global commands, and help system integration.
"""

import sys
import threading
from typing import Any, Dict, Optional

from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
    print_prompt,
)
from dataset_forge.utils.audio_utils import play_shutdown_sound


def show_global_help(
    current_menu: str = "Main Menu",
    menu_context: Optional[Dict[str, Any]] = None,
    pause: bool = True,
) -> None:
    """Show context-aware help for the current menu."""
    print_header("Help", char="=", color="")
    
    if menu_context:
        print_info(f"Menu: {current_menu}")
        print_info(f"Purpose: {menu_context.get('Purpose', 'Not specified')}")
        print_info(f"Options: {menu_context.get('Options', 'Not specified')}")
        print_info(f"Navigation: {menu_context.get('Navigation', 'Not specified')}")
        
        if 'Key Features' in menu_context:
            print_info("Key Features:")
            for feature in menu_context['Key Features']:
                print_info(f"  • {feature}")
        
        if 'Tips' in menu_context:
            print_info("Tips:")
            for tip in menu_context['Tips']:
                print_info(f"  • {tip}")
    else:
        print_info(f"Help for: {current_menu}")
        print_info("No specific context available for this menu.")
    
    print_info("\nGlobal Commands:")
    print_info("  help, h, ? - Show this help")
    print_info("  quit, exit, q - Exit Dataset Forge")
    print_info("  0 - Go back to previous menu")
    print_info("  Ctrl+C - Emergency exit")
    
    if pause:
        input("\nPress Enter to continue...")


def handle_global_command(
    command: str,
    current_menu: str = "Main Menu",
    menu_context: Optional[Dict[str, Any]] = None,
    pause: bool = True,
) -> bool:
    """Handle global commands that work in any menu.
    
    Returns:
        True if a global command was handled, False otherwise
    """
    if not command:
        return False
    
    command_lower = command.lower().strip()
    
    # Help commands
    if command_lower in ["help", "h", "?"]:
        show_global_help(current_menu, menu_context, pause)
        return True
    
    # Quit commands
    elif command_lower in ["quit", "exit", "q"]:
        print_info("🔄 Shutting down Dataset Forge...")
        
        # Play shutdown sound in background
        try:
            # Play shutdown sound in a separate thread with better timeout handling
            def play_shutdown_with_timeout():
                try:
                    # Try to play the shutdown sound
                    play_shutdown_sound(block=True)
                except Exception as e:
                    print_error(f"Shutdown sound failed: {e}")

            shutdown_thread = threading.Thread(target=play_shutdown_with_timeout, daemon=True)
            shutdown_thread.start()
            
            # Wait for a reasonable time for the sound to play (most audio files are 1-3 seconds)
            shutdown_thread.join(timeout=3.0)
            
            # If thread is still running, let it continue in background
            if shutdown_thread.is_alive():
                print_info("Shutdown sound playing in background...")
            
        except Exception as e:
            print_error(f"Audio system error: {e}")

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
    print_info("")

    # Display options with emoji safety
    for key, (description, action) in options.items():
        try:
            # Normalize and sanitize the description
            safe_description = sanitize_emoji(normalize_unicode(description))
        except (NameError, ImportError):
            # Fallback if emoji utilities are not available
            safe_description = description
        print_info(f"{key}. {safe_description}")

    print_info("")

    # Get user input
    while True:
        try:
            print_prompt("Enter your choice: ")
            choice = input().strip()

            # Handle global commands
            if handle_global_command(choice, current_menu, menu_context):
                # Redraw the menu after global command
                print_header(safe_title, char, header_color)
                print_info("")
                for key, (description, action) in options.items():
                    try:
                        safe_description = sanitize_emoji(normalize_unicode(description))
                    except (NameError, ImportError):
                        safe_description = description
                    print_info(f"{key}. {safe_description}")
                print_info("")
                continue

            # Check if choice is valid
            if choice in options:
                return choice
            elif choice == "0":
                return None
            else:
                print_error(f"Invalid choice: {choice}")
                print_info("Please enter a valid option.")
                
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            return None


def lazy_action(module_name: str, func_name: str):
    """Create a lazy action that imports the module when called."""
    def _action(*args, **kwargs):
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        return func(*args, **kwargs)
    return _action


def lazy_menu(module_name: str, func_name: str):
    """Create a lazy menu that imports the module when called."""
    def _menu(*args, **kwargs):
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        return func(*args, **kwargs)
    return _menu
