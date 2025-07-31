#!/usr/bin/env python3
"""Tests for help system functionality."""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHelpSystem:
    """Test class for help system functionality."""

    def test_help_system_import(self):
        """Test that help system can be imported."""
        from dataset_forge.utils.help_system import HelpSystem

        assert HelpSystem is not None

    def test_menu_help_structure(self):
        """Test that menu help has proper structure."""
        from dataset_forge.utils.help_system import HelpSystem

        # Check that MENU_HELP exists and is a dictionary
        assert hasattr(HelpSystem, "MENU_HELP")
        assert isinstance(HelpSystem.MENU_HELP, dict)

        # Check that main menu help exists
        assert "Main Menu" in HelpSystem.MENU_HELP
        main_menu_help = HelpSystem.MENU_HELP["Main Menu"]

        # Check required fields
        assert "description" in main_menu_help
        assert "categories" in main_menu_help
        assert "tips" in main_menu_help

    def test_feature_help_structure(self):
        """Test that feature help has proper structure."""
        from dataset_forge.utils.help_system import HelpSystem

        # Check that FEATURE_HELP exists and is a dictionary
        assert hasattr(HelpSystem, "FEATURE_HELP")
        assert isinstance(HelpSystem.FEATURE_HELP, dict)

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help_basic(self, mock_print_header, mock_print_info, mock_input):
        """Test basic menu help display."""
        from dataset_forge.utils.help_system import HelpSystem

        menu_context = {
            "Purpose": "Test purpose",
            "Options": "5 options available",
            "Navigation": "Use numbers 1-5",
        }

        HelpSystem.show_menu_help("Test Menu", menu_context, pause=False)

        # Should call print functions
        mock_print_header.assert_called()
        mock_print_info.assert_called()

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help_with_none_context(
        self, mock_print_header, mock_print_info, mock_input
    ):
        """Test menu help display with None context."""
        from dataset_forge.utils.help_system import HelpSystem

        HelpSystem.show_menu_help("Test Menu", None, pause=False)

        # Should still work with None context
        mock_print_header.assert_called()
        mock_print_info.assert_called()

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help_with_empty_context(
        self, mock_print_header, mock_print_info, mock_input
    ):
        """Test menu help display with empty context."""
        from dataset_forge.utils.help_system import HelpSystem

        HelpSystem.show_menu_help("Test Menu", {}, pause=False)

        # Should work with empty context
        mock_print_header.assert_called()
        mock_print_info.assert_called()

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help_with_detailed_context(
        self, mock_print_header, mock_print_info, mock_input
    ):
        """Test menu help display with detailed context."""
        from dataset_forge.utils.help_system import HelpSystem

        detailed_context = {
            "Purpose": "Comprehensive test purpose",
            "Options": "Multiple options available",
            "Navigation": "Complex navigation instructions",
            "Key Features": ["Feature A", "Feature B", "Feature C"],
            "Tips": ["Tip 1", "Tip 2"],
            "Examples": ["Example 1", "Example 2"],
            "Notes": "Additional notes",
        }

        HelpSystem.show_menu_help("Test Menu", detailed_context, pause=False)

        # Should handle detailed context
        mock_print_header.assert_called()
        mock_print_info.assert_called()

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help_with_pause(
        self, mock_print_header, mock_print_info, mock_input
    ):
        """Test menu help display with pause enabled."""
        from dataset_forge.utils.help_system import HelpSystem

        menu_context = {"Purpose": "Test purpose", "Options": "5 options available"}

        HelpSystem.show_menu_help("Test Menu", menu_context, pause=True)

        # Should call input when pause is True
        mock_input.assert_called()

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help_without_pause(
        self, mock_print_header, mock_print_info, mock_input
    ):
        """Test menu help display without pause."""
        from dataset_forge.utils.help_system import HelpSystem

        menu_context = {"Purpose": "Test purpose", "Options": "5 options available"}

        HelpSystem.show_menu_help("Test Menu", menu_context, pause=False)

        # Should not call input when pause is False
        mock_input.assert_not_called()

    def test_show_feature_help(self):
        """Test feature help display."""
        from dataset_forge.utils.help_system import HelpSystem

        with patch(
            "dataset_forge.utils.help_system.print_warning"
        ) as mock_print_warning:
            HelpSystem.show_feature_help("test_feature", pause=False)
            mock_print_warning.assert_called()

    def test_show_global_commands_help(self):
        """Test global commands help display."""
        from dataset_forge.utils.help_system import HelpSystem

        with patch("dataset_forge.utils.help_system.print_info") as mock_print_info:
            HelpSystem._show_global_commands()
            mock_print_info.assert_called()

    def test_menu_help_content_validation(self):
        """Test that menu help content is valid."""
        from dataset_forge.utils.help_system import HelpSystem

        # Test key menus have proper content
        key_menus = [
            "Main Menu",
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

                # Check that content is a dictionary
                assert isinstance(help_content, dict)

                # Check that description exists and is a string
                if "description" in help_content:
                    assert isinstance(help_content["description"], str)
                    assert len(help_content["description"]) > 0

    def test_feature_help_content_validation(self):
        """Test that feature help content is valid."""
        from dataset_forge.utils.help_system import HelpSystem

        # Test that feature help content is properly structured
        for feature, content in HelpSystem.FEATURE_HELP.items():
            # Check that content is a dictionary
            assert isinstance(content, dict)

            # Check that description exists and is a string
            if "description" in content:
                assert isinstance(content["description"], str)
                assert len(content["description"]) > 0

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help_error_handling(
        self, mock_print_header, mock_print_info, mock_input
    ):
        """Test menu help error handling."""
        from dataset_forge.utils.help_system import HelpSystem

        # Test with various problematic inputs
        problematic_contexts = [
            {"Purpose": None},  # None value
            {"Purpose": 123},  # Non-string value
            {"Purpose": ""},  # Empty string
            {"Purpose": "Test", "Options": []},  # List instead of string
        ]

        for context in problematic_contexts:
            # Should not raise exceptions
            HelpSystem.show_menu_help("Test Menu", context, pause=False)

            # Should still call print functions
            mock_print_header.assert_called()
            mock_print_info.assert_called()

    def test_help_system_methods_exist(self):
        """Test that all required help system methods exist."""
        from dataset_forge.utils.help_system import HelpSystem

        # Check that required methods exist
        required_methods = [
            "show_menu_help",
            "show_feature_help",
            "_show_global_commands",
        ]

        for method in required_methods:
            assert hasattr(HelpSystem, method)
            assert callable(getattr(HelpSystem, method))

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help_with_special_characters(
        self, mock_print_header, mock_print_info, mock_input
    ):
        """Test menu help with special characters in context."""
        from dataset_forge.utils.help_system import HelpSystem

        special_context = {
            "Purpose": "Test with special chars: !@#$%^&*()",
            "Options": "Options with unicode: 🎯📂🔍",
            "Navigation": "Navigation with symbols: → ← ↑ ↓",
            "Key Features": ["Feature with emoji 🚀", "Feature with symbols < > &"],
        }

        HelpSystem.show_menu_help("Test Menu", special_context, pause=False)

        # Should handle special characters gracefully
        mock_print_header.assert_called()
        mock_print_info.assert_called()

    def test_help_system_class_structure(self):
        """Test help system class structure."""
        from dataset_forge.utils.help_system import HelpSystem

        # Check that it's a class
        assert isinstance(HelpSystem, type)

        # Check that it has the required class attributes
        assert hasattr(HelpSystem, "MENU_HELP")
        assert hasattr(HelpSystem, "FEATURE_HELP")

        # Check that attributes are dictionaries
        assert isinstance(HelpSystem.MENU_HELP, dict)
        assert isinstance(HelpSystem.FEATURE_HELP, dict)

    @patch("builtins.input", return_value="")
    @patch("dataset_forge.utils.help_system.print_info")
    @patch("dataset_forge.utils.help_system.print_header")
    def test_show_menu_help_integration(
        self, mock_print_header, mock_print_info, mock_input
    ):
        """Integration test for menu help functionality."""
        from dataset_forge.utils.help_system import HelpSystem

        # Test comprehensive menu context
        comprehensive_context = {
            "Purpose": "Integration test purpose",
            "Options": "Multiple options available",
            "Navigation": "Use numbers 1-10 for navigation",
            "Key Features": [
                "Feature A: Advanced functionality",
                "Feature B: Basic functionality",
                "Feature C: Experimental functionality",
            ],
            "Tips": [
                "Tip 1: Always backup your data",
                "Tip 2: Use the help system when unsure",
            ],
            "Examples": ["Example 1: Basic usage", "Example 2: Advanced usage"],
            "Notes": "Important notes about this menu",
        }

        # Test the complete flow
        HelpSystem.show_menu_help(
            "Integration Test Menu", comprehensive_context, pause=False
        )

        # Verify that all expected functions were called
        mock_print_header.assert_called()
        mock_print_info.assert_called()

        # Verify that input was not called (pause=False)
        mock_input.assert_not_called()

        # Test with pause enabled
        HelpSystem.show_menu_help(
            "Integration Test Menu", comprehensive_context, pause=True
        )

        # Verify that input was called (pause=True)
        mock_input.assert_called()


def test_help_system_comprehensive():
    """Comprehensive test for help system functionality."""
    from dataset_forge.utils.help_system import HelpSystem

    # Test various menu contexts
    test_contexts = [
        {
            "Purpose": "Comprehensive test",
            "Options": "Multiple options",
            "Navigation": "Complex navigation",
            "Key Features": ["Feature A", "Feature B", "Feature C"],
            "Tips": ["Tip 1", "Tip 2"],
            "Examples": ["Example 1", "Example 2"],
        },
        {"Purpose": "Simple test", "Options": "Single option"},
        {},
        None,
    ]

    for context in test_contexts:
        with patch("builtins.input", return_value=""):
            with patch("dataset_forge.utils.help_system.print_info"):
                with patch("dataset_forge.utils.help_system.print_header"):
                    # All contexts should work without raising exceptions
                    HelpSystem.show_menu_help("Test Menu", context, pause=False)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
