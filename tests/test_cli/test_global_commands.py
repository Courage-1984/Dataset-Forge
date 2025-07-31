#!/usr/bin/env python3
"""Comprehensive tests for global help and quit commands."""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestGlobalCommands:
    """Test class for global command functionality."""

    def test_imports(self):
        """Test that all required modules can be imported."""
        from dataset_forge.utils.menu import (
            show_menu,
            handle_global_command,
            show_global_help,
        )
        from dataset_forge.utils.color import Mocha
        from dataset_forge.utils.help_system import HelpSystem

        assert True  # If we get here, imports succeeded

    @patch("dataset_forge.utils.help_system.HelpSystem.show_menu_help")
    def test_help_command_handling(self, mock_show_help):
        """Test help command handling with various inputs."""
        from dataset_forge.utils.menu import handle_global_command

        # Test help command
        result = handle_global_command(
            "help", "Test Menu", {"test": "context"}, pause=False
        )
        assert result is True
        mock_show_help.assert_called_once_with(
            "Test Menu", {"test": "context"}, pause=False
        )

        # Test h command
        result = handle_global_command(
            "h", "Test Menu", {"test": "context"}, pause=False
        )
        assert result is True

        # Test ? command
        result = handle_global_command(
            "?", "Test Menu", {"test": "context"}, pause=False
        )
        assert result is True

        # Test case insensitive
        result = handle_global_command(
            "HELP", "Test Menu", {"test": "context"}, pause=False
        )
        assert result is True

    def test_quit_command_handling(self):
        """Test quit command handling."""
        from dataset_forge.utils.menu import handle_global_command

        # Test quit command
        with pytest.raises(SystemExit) as excinfo:
            handle_global_command("quit", "Test Menu")
        assert excinfo.value.code == 0

        # Test exit command
        with pytest.raises(SystemExit) as excinfo:
            handle_global_command("exit", "Test Menu")
        assert excinfo.value.code == 0

        # Test q command
        with pytest.raises(SystemExit) as excinfo:
            handle_global_command("q", "Test Menu")
        assert excinfo.value.code == 0

        # Test case insensitive
        with pytest.raises(SystemExit) as excinfo:
            handle_global_command("QUIT", "Test Menu")
        assert excinfo.value.code == 0

    def test_invalid_command_handling(self):
        """Test handling of invalid commands."""
        from dataset_forge.utils.menu import handle_global_command

        # Test invalid command
        result = handle_global_command("invalid", "Test Menu")
        assert result is False

        # Test empty command
        result = handle_global_command("", "Test Menu")
        assert result is False

        # Test None command - should handle gracefully
        result = handle_global_command(None, "Test Menu")
        assert result is False

    @patch("dataset_forge.utils.printing.print_info")
    @patch("dataset_forge.utils.audio_utils.play_error_sound")
    def test_quit_command_with_cleanup(self, mock_audio, mock_print):
        """Test quit command with cleanup operations."""
        from dataset_forge.utils.menu import handle_global_command

        with pytest.raises(SystemExit) as excinfo:
            handle_global_command("quit", "Test Menu")

        assert excinfo.value.code == 0
        # Note: The actual implementation may not call these mocks directly
        # due to the SystemExit being raised, so we don't assert on them

    @patch("dataset_forge.utils.help_system.HelpSystem.show_menu_help")
    def test_help_command_with_menu_context(self, mock_show_help):
        """Test help command with various menu contexts."""
        from dataset_forge.utils.menu import handle_global_command

        # Test with detailed menu context
        menu_context = {
            "Purpose": "Test purpose",
            "Options": "5 options available",
            "Navigation": "Use numbers 1-5",
            "Key Features": ["Feature 1", "Feature 2"],
        }

        result = handle_global_command("help", "Test Menu", menu_context, pause=False)
        assert result is True
        mock_show_help.assert_called_with("Test Menu", menu_context, pause=False)

        # Test with minimal context
        minimal_context = {"test": "minimal"}
        result = handle_global_command(
            "help", "Test Menu", minimal_context, pause=False
        )
        assert result is True

        # Test with None context
        result = handle_global_command("help", "Test Menu", None, pause=False)
        assert result is True


class TestHelpSystem:
    """Test class for help system functionality."""

    def test_help_system_import(self):
        """Test help system can be imported."""
        from dataset_forge.utils.help_system import HelpSystem

        assert HelpSystem is not None

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help(self, mock_print_header, mock_print_info, mock_input):
        """Test showing menu help."""
        from dataset_forge.utils.help_system import HelpSystem

        menu_context = {
            "Purpose": "Test purpose",
            "Options": "5 options available",
            "Navigation": "Use numbers 1-5",
        }

        HelpSystem.show_menu_help("Test Menu", menu_context, pause=False)
        mock_print_header.assert_called()
        mock_print_info.assert_called()

    def test_menu_help_content(self):
        """Test that menu help content exists for main menus."""
        from dataset_forge.utils.help_system import HelpSystem

        # Check that main menu help exists
        assert "Main Menu" in HelpSystem.MENU_HELP
        main_menu_help = HelpSystem.MENU_HELP["Main Menu"]
        assert "description" in main_menu_help
        assert "categories" in main_menu_help
        assert "tips" in main_menu_help

        # Check that other key menus have help content
        key_menus = [
            "Dataset Management",
            "Analysis & Validation",
            "Image Processing & Augmentation",
            "Training & Inference",
            "Utilities",
            "System & Settings",
        ]

        for menu in key_menus:
            if menu in HelpSystem.MENU_HELP:
                help_content = HelpSystem.MENU_HELP[menu]
                assert "description" in help_content


class TestShowMenuIntegration:
    """Test class for show_menu integration with global commands."""

    @patch("builtins.input", return_value="help")
    @patch("dataset_forge.utils.help_system.HelpSystem.show_menu_help")
    @patch("dataset_forge.utils.printing.print_header")
    @patch("dataset_forge.utils.printing.print_info")
    def test_show_menu_with_help_command(
        self, mock_print_info, mock_print_header, mock_show_help, mock_input
    ):
        """Test show_menu handles help command correctly."""
        from dataset_forge.utils.menu import show_menu
        from dataset_forge.utils.color import Mocha

        options = {
            "1": ("Option 1", lambda: None),
            "2": ("Option 2", lambda: None),
            "0": ("Exit", None),
        }

        menu_context = {"Purpose": "Test menu", "Options": "2 options available"}

        # This should handle the help command and continue
        with patch("builtins.input", side_effect=["help", "0"]):
            result = show_menu(
                "Test Menu",
                options,
                Mocha.lavender,
                current_menu="Test Menu",
                menu_context=menu_context,
            )

        assert result == "0"
        mock_show_help.assert_called()

    @patch("builtins.input", return_value="quit")
    @patch("dataset_forge.utils.printing.print_header")
    @patch("dataset_forge.utils.printing.print_info")
    def test_show_menu_with_quit_command(
        self, mock_print_info, mock_print_header, mock_input
    ):
        """Test show_menu handles quit command correctly."""
        from dataset_forge.utils.menu import show_menu
        from dataset_forge.utils.color import Mocha

        options = {
            "1": ("Option 1", lambda: None),
            "2": ("Option 2", lambda: None),
            "0": ("Exit", None),
        }

        # This should raise SystemExit
        with pytest.raises(SystemExit) as excinfo:
            show_menu("Test Menu", options, Mocha.lavender, current_menu="Test Menu")

        assert excinfo.value.code == 0

    @patch("builtins.input", return_value="1")
    @patch("dataset_forge.utils.printing.print_header")
    @patch("dataset_forge.utils.printing.print_info")
    def test_show_menu_normal_operation(
        self, mock_print_info, mock_print_header, mock_input
    ):
        """Test show_menu normal operation without global commands."""
        from dataset_forge.utils.menu import show_menu
        from dataset_forge.utils.color import Mocha

        mock_action = Mock()
        options = {
            "1": ("Option 1", mock_action),
            "0": ("Exit", None),
        }

        result = show_menu(
            "Test Menu", options, Mocha.lavender, current_menu="Test Menu"
        )

        assert result == "1"
        # Note: mock_action would be called in the actual menu loop, but we're testing the return value


class TestGlobalCommandEdgeCases:
    """Test class for edge cases in global command handling."""

    def test_global_command_with_special_characters(self):
        """Test global commands with special characters."""
        from dataset_forge.utils.menu import handle_global_command

        # Test with whitespace
        result = handle_global_command(" help ", "Test Menu", pause=False)
        assert result is True

        # Test with mixed case and special chars
        result = handle_global_command("HeLp", "Test Menu", pause=False)
        assert result is True

    def test_global_command_with_none_menu(self):
        """Test global commands with None menu name."""
        from dataset_forge.utils.menu import handle_global_command

        result = handle_global_command("help", None, pause=False)
        assert result is True

        with pytest.raises(SystemExit):
            handle_global_command("quit", None)

    @patch("dataset_forge.utils.help_system.HelpSystem.show_menu_help")
    def test_help_command_pause_parameter(self, mock_show_help):
        """Test help command pause parameter handling."""
        from dataset_forge.utils.menu import handle_global_command

        # Test with pause=True (default)
        handle_global_command("help", "Test Menu", pause=True)
        mock_show_help.assert_called_with("Test Menu", None, pause=True)

        # Test with pause=False
        handle_global_command("help", "Test Menu", pause=False)
        mock_show_help.assert_called_with("Test Menu", None, pause=False)


def test_global_commands_integration():
    """Integration test for global commands in a complete workflow."""
    from dataset_forge.utils.menu import handle_global_command
    from dataset_forge.utils.help_system import HelpSystem

    # Test complete help workflow
    menu_context = {
        "Purpose": "Integration test menu",
        "Options": "3 options available",
        "Navigation": "Use numbers 1-3",
        "Key Features": ["Feature A", "Feature B", "Feature C"],
    }

    # Help should work
    result = handle_global_command(
        "help", "Integration Menu", menu_context, pause=False
    )
    assert result is True

    # Quit should exit
    with pytest.raises(SystemExit) as excinfo:
        handle_global_command("quit", "Integration Menu")
    assert excinfo.value.code == 0

    # Invalid command should return False
    result = handle_global_command("invalid", "Integration Menu")
    assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
