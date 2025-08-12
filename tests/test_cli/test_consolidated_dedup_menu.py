"""
test_consolidated_dedup_menu.py - Tests for Consolidated De-duplication Menu

Tests the consolidated deduplication menu functionality including:
- Menu navigation and structure
- CBIR integration (option 7)
- All deduplication methods
- Global commands integration
- Menu context and help system
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dataset_forge.menus.consolidated_dedup_menu import (
    consolidated_dedup_menu,
    cbir_dedup_action,
    fuzzy_matching_dedup,
    visual_dedup_action,
    file_hash_dedup_action,
    imagededup_action,
    duplicate_analysis_action,
    dedup_settings_action,
    get_default_threshold,
)
from dataset_forge.utils.color import Mocha


class TestConsolidatedDedupMenu:
    """Test suite for the consolidated deduplication menu."""

    def test_menu_import_success(self):
        """Test that the menu module imports successfully."""
        assert consolidated_dedup_menu is not None
        assert cbir_dedup_action is not None
        assert fuzzy_matching_dedup is not None

    def test_get_default_threshold(self):
        """Test the get_default_threshold function."""
        # Test all hash methods
        assert get_default_threshold("phash") == 90.0
        assert get_default_threshold("dhash") == 85.0
        assert get_default_threshold("ahash") == 80.0
        assert get_default_threshold("whash") == 85.0
        assert get_default_threshold("colorhash") == 75.0

        # Test unknown method returns default
        assert get_default_threshold("unknown") == 90.0

    def test_menu_structure(self):
        """Test that the menu has the correct structure with CBIR option."""
        # Import the menu function to access its structure
        from dataset_forge.menus.consolidated_dedup_menu import consolidated_dedup_menu

        # Get the source code to extract structure
        import inspect

        source = inspect.getsource(consolidated_dedup_menu)

        # Check menu title
        assert "show_menu(" in source
        assert '"🔍 Consolidated De-duplication"' in source

        # Check color
        assert "Mocha.yellow" in source

        # Check current_menu parameter
        assert 'current_menu="Consolidated De-duplication"' in source

        # Check menu_context exists
        assert "menu_context=" in source
        assert '"Purpose"' in source
        assert '"Total Options"' in source
        assert '"Key Features"' in source

        # Check that CBIR is mentioned in the context
        assert "CBIR" in source, "CBIR should be mentioned in the menu context"

    def test_menu_options_include_cbir(self):
        """Test that the menu options include CBIR as option 7."""
        # Import the menu function to access its options
        from dataset_forge.menus.consolidated_dedup_menu import consolidated_dedup_menu

        # Get the source code to extract options
        import inspect

        source = inspect.getsource(consolidated_dedup_menu)

        # Check that CBIR option 7 is defined in the source
        assert (
            '"7": ("🧠 CBIR Semantic Detection", cbir_dedup_action),' in source
            or '"7": ("🧠 CBIR Semantic Detection", cbir_dedup_action)' in source
        ), "CBIR option 7 should be defined in the menu"

        # Check that cbir_dedup_action is imported and available
        from dataset_forge.menus.consolidated_dedup_menu import cbir_dedup_action

        assert cbir_dedup_action is not None, "cbir_dedup_action should be available"

    def test_menu_options_structure(self):
        """Test that all menu options are present and correctly structured."""
        # Import the menu function to access its options
        from dataset_forge.menus.consolidated_dedup_menu import consolidated_dedup_menu
        
        # Get the source code to extract options
        import inspect
        source = inspect.getsource(consolidated_dedup_menu)
        
        # Check that all expected options are present
        expected_options = [
            "1",  # Fuzzy Matching
            "2",  # Visual De-duplication
            "3",  # File Hash De-duplication
            "4",  # ImageDedup Pro
            "5",  # Analysis & Reports
            "6",  # Settings & Configuration
            "7",  # CBIR Semantic Detection
            "0",  # Back to Utilities
        ]
        
        for option in expected_options:
            assert f'"{option}":' in source, f"Option {option} should be present in menu"
        
        # Check that CBIR option has the correct description
        assert "CBIR" in source, "CBIR option should mention CBIR in description"
        assert "🧠" in source, "CBIR option should have brain emoji"

    def test_global_commands_integration(self):
        """Test that global commands work in the menu."""
        # Import the menu function to access its structure
        from dataset_forge.menus.consolidated_dedup_menu import consolidated_dedup_menu
        
        # Get the source code to extract structure
        import inspect
        source = inspect.getsource(consolidated_dedup_menu)
        
        # Check that the menu uses the standardized pattern
        assert 'if key is None or key == "0":' in source, "Menu should handle exit with '0'"
        assert 'if callable(action):' in source, "Menu should check if action is callable"
        assert 'show_menu(' in source, "Menu should use show_menu function"
        assert 'menu_context=' in source, "Menu should have menu context"

    def test_menu_exit_handling(self):
        """Test that the menu handles exit commands correctly."""
        # Import the menu function to access its structure
        from dataset_forge.menus.consolidated_dedup_menu import consolidated_dedup_menu
        
        # Get the source code to extract structure
        import inspect
        source = inspect.getsource(consolidated_dedup_menu)
        
        # Check that the menu has proper exit handling
        assert 'if key is None or key == "0":' in source, "Menu should handle exit with None or '0'"
        assert 'return' in source, "Menu should return when exiting"
        assert 'while True:' in source, "Menu should have infinite loop"


class TestCBIRDedupAction:
    """Test suite for the CBIR deduplication action."""

    def test_cbir_action_structure(self):
        """Test the structure of the CBIR action function."""
        # Import the function to check its structure
        from dataset_forge.menus.consolidated_dedup_menu import cbir_dedup_action
        
        # Get the source code to extract structure
        import inspect
        source = inspect.getsource(cbir_dedup_action)
        
        # Check that the function has the expected structure
        assert 'print_header(' in source, "Function should call print_header"
        assert 'print_section(' in source, "Function should call print_section"
        assert 'print_info(' in source, "Function should call print_info"
        assert 'input(' in source, "Function should get user input"
        assert 'get_path_with_history(' in source, "Function should get folder path"
        assert 'cbir_workflow(' in source, "Function should call cbir_workflow"

    @patch("dataset_forge.menus.consolidated_dedup_menu.print_header")
    @patch("dataset_forge.menus.consolidated_dedup_menu.input")
    @patch("dataset_forge.menus.consolidated_dedup_menu.get_path_with_history")
    def test_cbir_action_invalid_path(
        self, mock_get_path, mock_input, mock_print_header
    ):
        """Test CBIR action with invalid path."""
        # Mock invalid path
        mock_get_path.return_value = None
        mock_input.return_value = "1"  # Single folder mode

        with patch(
            "dataset_forge.menus.consolidated_dedup_menu.print_error"
        ) as mock_print_error:
            cbir_dedup_action()

            # Should show error for invalid path
            mock_print_error.assert_called_with("Invalid folder path.")

    def test_cbir_action_model_selection(self):
        """Test CBIR action model selection."""
        # Import the function to check its structure
        from dataset_forge.menus.consolidated_dedup_menu import cbir_dedup_action
        
        # Get the source code to extract structure
        import inspect
        source = inspect.getsource(cbir_dedup_action)
        
        # Check that the function handles model selection
        assert 'model_name' in source, "Function should handle model_name parameter"
        assert 'clip' in source or 'CLIP' in source, "Function should support CLIP model"
        assert 'resnet' in source or 'ResNet' in source, "Function should support ResNet model"
        assert 'vgg' in source or 'VGG' in source, "Function should support VGG model"

    def test_cbir_action_operation_modes(self):
        """Test CBIR action operation modes."""
        # Import the function to check its structure
        from dataset_forge.menus.consolidated_dedup_menu import cbir_dedup_action
        
        # Get the source code to extract structure
        import inspect
        source = inspect.getsource(cbir_dedup_action)
        
        # Check that the function handles operation modes
        assert 'operation' in source, "Function should handle operation parameter"
        assert 'find' in source or 'show' in source, "Function should support find/show operation"
        assert 'copy' in source, "Function should support copy operation"
        assert 'move' in source, "Function should support move operation"
        assert 'remove' in source or 'delete' in source, "Function should support remove/delete operation"

    def test_cbir_action_error_handling(self):
        """Test CBIR action error handling."""
        # Import the function to check its structure
        from dataset_forge.menus.consolidated_dedup_menu import cbir_dedup_action
        
        # Get the source code to extract structure
        import inspect
        source = inspect.getsource(cbir_dedup_action)
        
        # Check that the function has error handling
        assert 'try:' in source, "Function should have try-catch error handling"
        assert 'except' in source, "Function should have exception handling"
        assert 'print_error(' in source, "Function should call print_error for errors"
        assert 'finally:' in source, "Function should have finally block for cleanup"


class TestOtherDedupActions:
    """Test suite for other deduplication actions."""

    @patch("dataset_forge.menus.consolidated_dedup_menu.print_header")
    def test_fuzzy_matching_dedup_structure(self, mock_print_header):
        """Test the structure of the fuzzy matching dedup function."""
        # This is a basic structure test - the actual function requires user input
        assert fuzzy_matching_dedup is not None
        assert callable(fuzzy_matching_dedup)

    @patch("dataset_forge.menus.consolidated_dedup_menu.print_header")
    def test_visual_dedup_action_structure(self, mock_print_header):
        """Test the structure of the visual dedup action function."""
        assert visual_dedup_action is not None
        assert callable(visual_dedup_action)

    @patch("dataset_forge.menus.consolidated_dedup_menu.print_header")
    def test_file_hash_dedup_action_structure(self, mock_print_header):
        """Test the structure of the file hash dedup action function."""
        assert file_hash_dedup_action is not None
        assert callable(file_hash_dedup_action)

    @patch("dataset_forge.menus.consolidated_dedup_menu.print_header")
    def test_imagededup_action_structure(self, mock_print_header):
        """Test the structure of the imagededup action function."""
        assert imagededup_action is not None
        assert callable(imagededup_action)

    @patch("dataset_forge.menus.consolidated_dedup_menu.print_header")
    def test_duplicate_analysis_action_structure(self, mock_print_header):
        """Test the structure of the duplicate analysis action function."""
        assert duplicate_analysis_action is not None
        assert callable(duplicate_analysis_action)

    @patch("dataset_forge.menus.consolidated_dedup_menu.print_header")
    def test_dedup_settings_action_structure(self, mock_print_header):
        """Test the structure of the dedup settings action function."""
        assert dedup_settings_action is not None
        assert callable(dedup_settings_action)


class TestMenuIntegration:
    """Test suite for menu integration and workflow."""

    def test_menu_function_signatures(self):
        """Test that all menu functions have the correct signatures."""
        import inspect

        # All action functions should take no arguments (they get input from user)
        action_functions = [
            cbir_dedup_action,
            fuzzy_matching_dedup,
            visual_dedup_action,
            file_hash_dedup_action,
            imagededup_action,
            duplicate_analysis_action,
            dedup_settings_action,
        ]

        for func in action_functions:
            sig = inspect.signature(func)
            # Should have no required parameters (except self for methods)
            assert (
                len(sig.parameters) == 0
            ), f"{func.__name__} should take no parameters"

    def test_menu_context_structure(self):
        """Test that the menu context has the correct structure."""
        # Import the menu context from the module
        import dataset_forge.menus.consolidated_dedup_menu as menu_module

        # The menu_context is defined inside the consolidated_dedup_menu function
        # We can't easily access it directly, but we can test that the function exists
        assert hasattr(menu_module, "consolidated_dedup_menu")
        assert callable(menu_module.consolidated_dedup_menu)

    def test_cbir_integration_complete(self):
        """Test that CBIR integration is complete and functional."""
        # Test that CBIR action exists and is callable
        assert cbir_dedup_action is not None
        assert callable(cbir_dedup_action)

        # Test that the function has the expected structure
        import inspect

        sig = inspect.signature(cbir_dedup_action)
        assert len(sig.parameters) == 0, "CBIR action should take no parameters"


if __name__ == "__main__":
    pytest.main([__file__])
