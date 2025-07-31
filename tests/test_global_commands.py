#!/usr/bin/env python3
"""Test script for global help and quit commands."""

import sys
import os
import pytest

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all required modules can be imported."""
    try:
        from dataset_forge.utils.menu import (
            show_menu,
            handle_global_command,
            show_global_help,
        )
        from dataset_forge.utils.color import Mocha
        from dataset_forge.utils.help_system import HelpSystem

        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_help_system():
    """Test the help system functionality."""
    try:
        from dataset_forge.utils.help_system import HelpSystem

        print("\n🧪 Testing Help System...")

        # Test menu help
        print("Testing menu help...")
        HelpSystem.show_menu_help("Main Menu", {"test": "context"}, pause=False)

        print("✅ Help system test completed!")
        return True
    except Exception as e:
        print(f"❌ Help system test failed: {e}")
        return False


def test_global_commands():
    """Test global command handling."""
    try:
        from dataset_forge.utils.menu import handle_global_command

        print("\n🧪 Testing Global Commands...")

        # Test help command
        result = handle_global_command(
            "help", "Test Menu", {"test": "context"}, pause=False
        )
        print(f"Help command result: {result}")

        # Test quit command (should raise SystemExit)
        print("Testing quit command handling...")
        with pytest.raises(SystemExit) as excinfo:
            handle_global_command("quit", "Test Menu")
        assert excinfo.value.code == 0
        print("Quit command raised SystemExit as expected.")

        # Test invalid command
        result = handle_global_command("invalid", "Test Menu")
        print(f"Invalid command result: {result}")

        print("✅ Global commands test completed!")
        return True
    except Exception as e:
        print(f"❌ Global commands test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing Global Help and Quit Commands")
    print("=" * 50)

    # Test imports
    if not test_imports():
        return False

    # Test help system
    if not test_help_system():
        return False

    # Test global commands
    if not test_global_commands():
        return False

    print("\n🎉 All tests passed! Global help and quit commands are working.")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
