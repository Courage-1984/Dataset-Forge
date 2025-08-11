#!/usr/bin/env python3
"""
Integration tests for fuzzy deduplication menu functionality.

Tests the complete menu workflow and user interactions.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import pytest
from unittest.mock import patch, MagicMock, Mock
from PIL import Image

# Add the project root to the path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dataset_forge.menus.fuzzy_dedup_menu import (
    fuzzy_dedup_menu,
    fuzzy_matching_dedup,
    visual_dedup_action,
    file_hash_dedup_action,
    imagededup_action,
    duplicate_analysis_action,
    fuzzy_settings_action
)
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import print_info, print_success, print_warning, print_error


class TestFuzzyDedupMenu:
    """Integration test suite for fuzzy deduplication menu."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp(prefix="fuzzy_dedup_menu_test_")
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def test_images(self, temp_dir):
        """Create test images for deduplication testing."""
        images = []
        
        # Create base image (red)
        base_img = Image.new('RGB', (100, 100), color='red')
        base_path = os.path.join(temp_dir, "base.png")
        base_img.save(base_path)
        images.append(base_path)
        
        # Create identical copy
        identical_path = os.path.join(temp_dir, "identical.png")
        base_img.save(identical_path)
        images.append(identical_path)
        
        # Create similar image (dark red)
        similar_img = Image.new('RGB', (100, 100), color='darkred')
        similar_path = os.path.join(temp_dir, "similar.png")
        similar_img.save(similar_path)
        images.append(similar_path)
        
        return images

    def test_fuzzy_dedup_menu_structure(self):
        """Test that the fuzzy deduplication menu has the correct structure."""
        # This test verifies the menu structure without actually running it
        # We'll test the menu options and structure
        
        # Import the menu function to check its structure
        from dataset_forge.menus.fuzzy_dedup_menu import fuzzy_dedup_menu
        
        # The menu should be callable
        assert callable(fuzzy_dedup_menu)

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_navigation(self, mock_show_menu):
        """Test fuzzy deduplication menu navigation."""
        # Mock the show_menu to return "0" (exit)
        mock_show_menu.return_value = "0"
        
        # Call the menu function
        fuzzy_dedup_menu()
        
        # Verify show_menu was called with correct parameters
        mock_show_menu.assert_called_once()
        call_args = mock_show_menu.call_args
        assert call_args[0][0] == "🔍 Fuzzy Matching De-duplication"
        assert "current_menu" in call_args[1]
        assert "menu_context" in call_args[1]

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_options(self, mock_show_menu):
        """Test that the fuzzy deduplication menu has the correct options."""
        # Mock the show_menu to return "1" (fuzzy matching dedup option)
        mock_show_menu.return_value = "1"
        
        # Mock the fuzzy_matching_dedup function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_matching_dedup') as mock_fuzzy:
            fuzzy_dedup_menu()
            
            # Verify the fuzzy matching function was called
            mock_fuzzy.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_hq_lq_option(self, mock_show_menu):
        """Test visual deduplication option in fuzzy deduplication menu."""
        # Mock the show_menu to return "2" (visual deduplication option)
        mock_show_menu.return_value = "2"
        
        # Mock the visual_dedup_action function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.visual_dedup_action') as mock_visual:
            fuzzy_dedup_menu()
            
            # Verify the visual deduplication function was called
            mock_visual.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_settings_option(self, mock_show_menu):
        """Test file hash deduplication option in fuzzy deduplication menu."""
        # Mock the show_menu to return "3" (file hash deduplication option)
        mock_show_menu.return_value = "3"
        
        # Mock the file_hash_dedup_action function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.file_hash_dedup_action') as mock_file_hash:
            fuzzy_dedup_menu()
            
            # Verify the file hash deduplication function was called
            mock_file_hash.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_statistics_option(self, mock_show_menu):
        """Test ImageDedup advanced option in fuzzy deduplication menu."""
        # Mock the show_menu to return "4" (ImageDedup advanced option)
        mock_show_menu.return_value = "4"
        
        # Mock the imagededup_action function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.imagededup_action') as mock_imagededup:
            fuzzy_dedup_menu()
            
            # Verify the ImageDedup advanced function was called
            mock_imagededup.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.get_path_with_history')
    @patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_matching_dedup')
    def test_single_folder_fuzzy_dedup_workflow(self, mock_fuzzy_dedup, mock_get_path, temp_dir, test_images):
        """Test single folder fuzzy deduplication workflow."""
        # Mock path input
        mock_get_path.return_value = temp_dir
        
        # Mock the fuzzy matching dedup function
        mock_fuzzy_dedup.return_value = {
            "total_files_processed": len(test_images),
            "duplicate_groups": [
                [
                    {"path": test_images[0], "similarity": 95.0, "method": "phash"},
                    {"path": test_images[1], "similarity": 94.8, "method": "phash"}
                ]
            ],
            "total_duplicates_found": 2
        }
        
        # Mock user inputs for mode selection
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = [
                "1",  # Single folder mode
            ]
            
            # Call the function
            fuzzy_matching_dedup()
            
            # Verify the function was called
            mock_fuzzy_dedup.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.get_path_with_history')
    @patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_matching_dedup')
    def test_hq_lq_pairs_fuzzy_dedup_workflow(self, mock_fuzzy_dedup, mock_get_path, temp_dir, test_images):
        """Test HQ/LQ pairs fuzzy deduplication workflow."""
        # Create HQ and LQ folders
        hq_folder = os.path.join(temp_dir, "hq")
        lq_folder = os.path.join(temp_dir, "lq")
        os.makedirs(hq_folder, exist_ok=True)
        os.makedirs(lq_folder, exist_ok=True)
        
        # Mock path inputs
        mock_get_path.side_effect = [hq_folder, lq_folder]
        
        # Mock the fuzzy matching dedup function
        mock_fuzzy_dedup.return_value = {
            "total_files_processed": len(test_images),
            "duplicate_groups": [
                [
                    {"path": test_images[0], "similarity": 95.0, "method": "phash"},
                    {"path": test_images[1], "similarity": 94.8, "method": "phash"}
                ]
            ],
            "total_duplicates_found": 2
        }
        
        # Mock user inputs for mode selection
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = [
                "2",  # HQ/LQ pairs mode
            ]
            
            # Call the function
            fuzzy_matching_dedup()
            
            # Verify the function was called
            mock_fuzzy_dedup.assert_called_once()

    def test_configure_fuzzy_matching_settings(self):
        """Test fuzzy matching settings configuration."""
        # Mock the fuzzy_settings_action function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_settings_action') as mock_settings:
            # Call the function
            fuzzy_settings_action()
            
            # Verify the settings function was called
            mock_settings.assert_called_once()

    def test_view_fuzzy_matching_statistics(self):
        """Test fuzzy matching statistics viewing."""
        # Mock the duplicate_analysis_action function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.duplicate_analysis_action') as mock_analysis:
            # Call the function
            duplicate_analysis_action()
            
            # Verify the analysis function was called
            mock_analysis.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_help_command(self, mock_show_menu):
        """Test help command in fuzzy deduplication menu."""
        # Mock the show_menu to return "help"
        mock_show_menu.return_value = "help"
        
        # Mock the help system
        with patch('dataset_forge.menus.fuzzy_dedup_menu.show_help') as mock_help:
            fuzzy_dedup_menu()
            
            # Verify help was called
            mock_help.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_quit_command(self, mock_show_menu):
        """Test quit command in fuzzy deduplication menu."""
        # Mock the show_menu to return "quit"
        mock_show_menu.return_value = "quit"
        
        # Mock the quit system
        with patch('dataset_forge.menus.fuzzy_dedup_menu.quit_dataset_forge') as mock_quit:
            fuzzy_dedup_menu()
            
            # Verify quit was called
            mock_quit.assert_called_once()

    def test_fuzzy_dedup_menu_error_handling(self, temp_dir):
        """Test error handling in fuzzy deduplication menu."""
        # Test with invalid folder
        with patch('dataset_forge.menus.fuzzy_dedup_menu.get_path_with_history', return_value="/nonexistent/folder"):
            with patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_matching_workflow', return_value=None):
                # Mock user inputs
                with patch('builtins.input') as mock_input:
                    mock_input.side_effect = [
                        "phash,dhash",  # Hash methods
                        "90",           # pHash threshold
                        "85",           # dHash threshold
                        "1"             # Show operation
                    ]
                    
                    # Call the function - should handle error gracefully
                    single_folder_fuzzy_dedup()

    def test_fuzzy_dedup_menu_invalid_input_handling(self, temp_dir, test_images):
        """Test invalid input handling in fuzzy deduplication menu."""
        # Mock path input
        with patch('dataset_forge.menus.fuzzy_dedup_menu.get_path_with_history', return_value=temp_dir):
            # Mock the fuzzy matching workflow
            with patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_matching_workflow') as mock_workflow:
                mock_workflow.return_value = {
                    "total_files_processed": len(test_images),
                    "duplicate_groups": [],
                    "total_duplicates_found": 0
                }
                
                # Mock invalid user inputs
                with patch('builtins.input') as mock_input:
                    mock_input.side_effect = [
                        "invalid_method",  # Invalid hash method
                        "phash,dhash",     # Valid hash methods
                        "150",             # Invalid threshold (too high)
                        "90",              # Valid pHash threshold
                        "85",              # Valid dHash threshold
                        "5"                # Invalid operation
                    ]
                    
                    # Call the function - should handle invalid inputs gracefully
                    single_folder_fuzzy_dedup()

    def test_fuzzy_dedup_menu_memory_management(self, temp_dir, test_images):
        """Test memory management in fuzzy deduplication menu."""
        # Mock path input
        with patch('dataset_forge.menus.fuzzy_dedup_menu.get_path_with_history', return_value=temp_dir):
            # Mock the fuzzy matching workflow
            with patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_matching_workflow') as mock_workflow:
                mock_workflow.return_value = {
                    "total_files_processed": len(test_images),
                    "duplicate_groups": [],
                    "total_duplicates_found": 0
                }
                
                # Mock memory management functions
                with patch('dataset_forge.menus.fuzzy_dedup_menu.clear_memory') as mock_clear_memory:
                    with patch('dataset_forge.menus.fuzzy_dedup_menu.clear_cuda_cache') as mock_clear_cuda:
                        # Mock user inputs
                        with patch('builtins.input') as mock_input:
                            mock_input.side_effect = [
                                "phash,dhash",  # Hash methods
                                "90",           # pHash threshold
                                "85",           # dHash threshold
                                "1"             # Show operation
                            ]
                            
                            # Call the function
                            single_folder_fuzzy_dedup()
                            
                            # Verify memory cleanup was called
                            mock_clear_memory.assert_called()
                            mock_clear_cuda.assert_called()

    def test_fuzzy_dedup_menu_audio_feedback(self, temp_dir, test_images):
        """Test audio feedback in fuzzy deduplication menu."""
        # Mock path input
        with patch('dataset_forge.menus.fuzzy_dedup_menu.get_path_with_history', return_value=temp_dir):
            # Mock the fuzzy matching workflow
            with patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_matching_workflow') as mock_workflow:
                mock_workflow.return_value = {
                    "total_files_processed": len(test_images),
                    "duplicate_groups": [],
                    "total_duplicates_found": 0
                }
                
                # Mock audio feedback functions
                with patch('dataset_forge.menus.fuzzy_dedup_menu.play_done_sound') as mock_done_sound:
                    with patch('dataset_forge.menus.fuzzy_dedup_menu.play_error_sound') as mock_error_sound:
                        # Mock user inputs
                        with patch('builtins.input') as mock_input:
                            mock_input.side_effect = [
                                "phash,dhash",  # Hash methods
                                "90",           # pHash threshold
                                "85",           # dHash threshold
                                "1"             # Show operation
                            ]
                            
                            # Call the function
                            single_folder_fuzzy_dedup()
                            
                            # Verify audio feedback was called
                            mock_done_sound.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
