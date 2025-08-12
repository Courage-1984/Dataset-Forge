"""
Test module for getfscaler comprehensive menu functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from dataset_forge.menus.getfscaler_comprehensive_menu import (
    getfscaler_comprehensive_menu,
    single_file_analysis_menu,
    batch_analysis_menu,
    configuration_menu,
    advanced_analysis_menu,
    help_examples_menu
)


class TestGetfScalerComprehensiveMenu:
    """Test class for getfscaler comprehensive menu functionality."""

    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.show_menu')
    def test_getfscaler_comprehensive_menu_structure(self, mock_show_menu):
        """Test that the comprehensive menu has the correct structure."""
        # Mock show_menu to return "0" to exit immediately
        mock_show_menu.return_value = "0"
        
        # Call the menu function
        getfscaler_comprehensive_menu()
        
        # Verify show_menu was called with correct parameters
        mock_show_menu.assert_called_once()
        call_args = mock_show_menu.call_args
        
        # Check title
        assert call_args[0][0] == "🔧 getfscaler Comprehensive Menu"
        
        # Check options structure
        options = call_args[0][1]
        expected_options = ["1", "2", "3", "4", "5", "0"]
        
        for option in expected_options:
            assert option in options
            assert len(options[option]) == 2  # (description, function)
            assert callable(options[option][1]) or options[option][1] is None

    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.show_menu')
    def test_menu_context_integration(self, mock_show_menu):
        """Test that menu context is properly defined."""
        # Mock show_menu to return "0" to exit immediately
        mock_show_menu.return_value = "0"
        
        # Call the menu function
        getfscaler_comprehensive_menu()
        
        # Get the call arguments
        call_args = mock_show_menu.call_args
        menu_context = call_args[1]['menu_context']
        
        # Verify menu context structure
        assert 'Purpose' in menu_context
        assert 'Total Options' in menu_context
        assert 'Navigation' in menu_context
        assert 'Key Features' in menu_context
        assert 'Tips' in menu_context
        
        # Verify content
        assert "Comprehensive getfscaler integration" in menu_context['Purpose']
        assert "5 main categories" in menu_context['Total Options']
        assert "Single File Analysis" in str(menu_context['Key Features'])

    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.input')
    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.get_path_with_history')
    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.find_native_resolution_getfscaler')
    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.os.path.exists')
    def test_single_file_analysis_menu_basic(self, mock_exists, mock_find_native, mock_get_path, mock_input):
        """Test single file analysis menu basic functionality."""
        # Mock inputs
        mock_get_path.return_value = "/test/image.png"
        mock_exists.return_value = True  # File exists
        mock_input.side_effect = ["", "", "", "", "", "n"]  # Use defaults and no debug
        
        # Call the function
        single_file_analysis_menu()
        
        # Verify get_path_with_history was called
        mock_get_path.assert_called_once()
        
        # Verify find_native_resolution_getfscaler was called with correct args
        mock_find_native.assert_called_once()
        call_args = mock_find_native.call_args
        assert call_args[0][0] == "/test/image.png"
        assert "-nh" in call_args[0][2]  # extra_args should contain native height

    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.input')
    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.get_folder_path')
    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.batch_analyze_getfscaler')
    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.os.path.isdir')
    def test_batch_analysis_menu_basic(self, mock_isdir, mock_batch_analyze, mock_get_folder, mock_input):
        """Test batch analysis menu basic functionality."""
        # Mock inputs
        mock_get_folder.return_value = "/test/directory"
        mock_isdir.return_value = True  # Directory exists
        mock_input.side_effect = ["", "", ""]  # Use defaults
        
        # Call the function
        batch_analysis_menu()
        
        # Verify get_folder_path was called
        mock_get_folder.assert_called_once()
        
        # Verify batch_analyze_getfscaler was called
        mock_batch_analyze.assert_called_once()
        call_args = mock_batch_analyze.call_args
        assert call_args[0][0] == "/test/directory"

    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.show_menu')
    def test_configuration_menu_structure(self, mock_show_menu):
        """Test configuration menu structure."""
        # Mock show_menu to return "0" to exit immediately
        mock_show_menu.return_value = "0"
        
        # Call the menu function
        configuration_menu()
        
        # Verify show_menu was called
        mock_show_menu.assert_called_once()
        call_args = mock_show_menu.call_args
        
        # Check title
        assert call_args[0][0] == "⚙️ Configuration Management"
        
        # Check options structure
        options = call_args[0][1]
        expected_options = ["1", "2", "3", "4", "0"]
        
        for option in expected_options:
            assert option in options

    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.show_menu')
    def test_advanced_analysis_menu_structure(self, mock_show_menu):
        """Test advanced analysis menu structure."""
        # Mock show_menu to return "0" to exit immediately
        mock_show_menu.return_value = "0"
        
        # Call the menu function
        advanced_analysis_menu()
        
        # Verify show_menu was called
        mock_show_menu.assert_called_once()
        call_args = mock_show_menu.call_args
        
        # Check title
        assert call_args[0][0] == "📊 Advanced Analysis Options"
        
        # Check options structure
        options = call_args[0][1]
        expected_options = ["1", "2", "3", "4", "0"]
        
        for option in expected_options:
            assert option in options

    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.show_menu')
    def test_help_examples_menu_structure(self, mock_show_menu):
        """Test help examples menu structure."""
        # Mock show_menu to return "0" to exit immediately
        mock_show_menu.return_value = "0"
        
        # Call the menu function
        help_examples_menu()
        
        # Verify show_menu was called
        mock_show_menu.assert_called_once()
        call_args = mock_show_menu.call_args
        
        # Check title
        assert call_args[0][0] == "📋 Help & Examples"
        
        # Check options structure
        options = call_args[0][1]
        expected_options = ["1", "2", "3", "4", "0"]
        
        for option in expected_options:
            assert option in options

    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.input')
    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.get_path_with_history')
    def test_single_file_analysis_menu_invalid_path(self, mock_get_path, mock_input):
        """Test single file analysis menu with invalid path."""
        # Mock invalid path
        mock_get_path.return_value = "/nonexistent/image.png"
        mock_input.side_effect = ["", "", "", "", "", "n"]
        
        # Call the function
        single_file_analysis_menu()
        
        # Verify get_path_with_history was called
        mock_get_path.assert_called_once()

    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.input')
    @patch('dataset_forge.menus.getfscaler_comprehensive_menu.get_folder_path')
    def test_batch_analysis_menu_invalid_directory(self, mock_get_folder, mock_input):
        """Test batch analysis menu with invalid directory."""
        # Mock invalid directory
        mock_get_folder.return_value = "/nonexistent/directory"
        mock_input.side_effect = ["", "", ""]
        
        # Call the function
        batch_analysis_menu()
        
        # Verify get_folder_path was called
        mock_get_folder.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
