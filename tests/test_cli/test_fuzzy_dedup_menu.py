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
        # Mock the show_menu to return "1" (single folder option)
        mock_show_menu.return_value = "1"
        
        # Mock the single_folder_fuzzy_dedup function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.single_folder_fuzzy_dedup') as mock_single:
            fuzzy_dedup_menu()
            
            # Verify the single folder function was called
            mock_single.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_hq_lq_option(self, mock_show_menu):
        """Test HQ/LQ pairs option in fuzzy deduplication menu."""
        # Mock the show_menu to return "2" (HQ/LQ pairs option)
        mock_show_menu.return_value = "2"
        
        # Mock the hq_lq_pairs_fuzzy_dedup function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.hq_lq_pairs_fuzzy_dedup') as mock_hq_lq:
            fuzzy_dedup_menu()
            
            # Verify the HQ/LQ pairs function was called
            mock_hq_lq.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_settings_option(self, mock_show_menu):
        """Test settings option in fuzzy deduplication menu."""
        # Mock the show_menu to return "3" (settings option)
        mock_show_menu.return_value = "3"
        
        # Mock the configure_fuzzy_matching_settings function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.configure_fuzzy_matching_settings') as mock_settings:
            fuzzy_dedup_menu()
            
            # Verify the settings function was called
            mock_settings.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.show_menu')
    def test_fuzzy_dedup_menu_statistics_option(self, mock_show_menu):
        """Test statistics option in fuzzy deduplication menu."""
        # Mock the show_menu to return "4" (statistics option)
        mock_show_menu.return_value = "4"
        
        # Mock the view_fuzzy_matching_statistics function
        with patch('dataset_forge.menus.fuzzy_dedup_menu.view_fuzzy_matching_statistics') as mock_stats:
            fuzzy_dedup_menu()
            
            # Verify the statistics function was called
            mock_stats.assert_called_once()

    @patch('dataset_forge.menus.fuzzy_dedup_menu.get_path_with_history')
    @patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_matching_workflow')
    def test_single_folder_fuzzy_dedup_workflow(self, mock_workflow, mock_get_path, temp_dir, test_images):
        """Test single folder fuzzy deduplication workflow."""
        # Mock path input
        mock_get_path.return_value = temp_dir
        
        # Mock the fuzzy matching workflow
        mock_workflow.return_value = {
            "total_files_processed": len(test_images),
            "duplicate_groups": [
                [
                    {"path": test_images[0], "similarity": 95.0, "method": "phash"},
                    {"path": test_images[1], "similarity": 94.8, "method": "phash"}
                ]
            ],
            "total_duplicates_found": 2
        }
        
        # Mock user inputs for hash methods, thresholds, and operation
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = [
                "phash,dhash",  # Hash methods
                "90",           # pHash threshold
                "85",           # dHash threshold
                "1"             # Show operation
            ]
            
            # Call the function
            single_folder_fuzzy_dedup()
            
            # Verify the workflow was called with correct parameters
            mock_workflow.assert_called_once()
            call_args = mock_workflow.call_args
            assert call_args[1]["folder"] == temp_dir
            assert call_args[1]["hash_methods"] == ["phash", "dhash"]
            assert call_args[1]["thresholds"] == {"phash": 90, "dhash": 85}
            assert call_args[1]["operation"] == "show"

    @patch('dataset_forge.menus.fuzzy_dedup_menu.get_path_with_history')
    @patch('dataset_forge.menus.fuzzy_dedup_menu.fuzzy_matching_workflow')
    def test_hq_lq_pairs_fuzzy_dedup_workflow(self, mock_workflow, mock_get_path, temp_dir, test_images):
        """Test HQ/LQ pairs fuzzy deduplication workflow."""
        # Create HQ and LQ folders
        hq_folder = os.path.join(temp_dir, "hq")
        lq_folder = os.path.join(temp_dir, "lq")
        os.makedirs(hq_folder, exist_ok=True)
        os.makedirs(lq_folder, exist_ok=True)
        
        # Mock path inputs
        mock_get_path.side_effect = [hq_folder, lq_folder]
        
        # Mock the fuzzy matching workflow
        mock_workflow.return_value = {
            "total_files_processed": len(test_images),
            "duplicate_groups": [
                [
                    {"path": test_images[0], "similarity": 95.0, "method": "phash"},
                    {"path": test_images[1], "similarity": 94.8, "method": "phash"}
                ]
            ],
            "total_duplicates_found": 2
        }
        
        # Mock user inputs for hash methods, thresholds, and operation
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = [
                "phash,dhash",  # Hash methods
                "90",           # pHash threshold
                "85",           # dHash threshold
                "1"             # Show operation
            ]
            
            # Call the function
            hq_lq_pairs_fuzzy_dedup()
            
            # Verify the workflow was called with correct parameters
            mock_workflow.assert_called_once()
            call_args = mock_workflow.call_args
            assert call_args[1]["hq_folder"] == hq_folder
            assert call_args[1]["lq_folder"] == lq_folder
            assert call_args[1]["hash_methods"] == ["phash", "dhash"]
            assert call_args[1]["thresholds"] == {"phash": 90, "dhash": 85}
            assert call_args[1]["operation"] == "show"

    def test_configure_fuzzy_matching_settings(self):
        """Test fuzzy matching settings configuration."""
        # Mock user inputs for settings
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = [
                "phash,dhash,ahash",  # Default hash methods
                "90",                 # pHash threshold
                "85",                 # dHash threshold
                "80",                 # aHash threshold
                "100",                # Batch size
                "y"                   # Enable progress display
            ]
            
            # Call the function
            configure_fuzzy_matching_settings()
            
            # This function should complete without errors
            # We're testing that it handles user input correctly

    def test_view_fuzzy_matching_statistics(self):
        """Test fuzzy matching statistics viewing."""
        # Mock statistics data
        mock_stats = {
            "total_operations": 10,
            "total_files_processed": 1000,
            "total_duplicates_found": 150,
            "average_processing_time": 5.5,
            "most_used_hash_methods": ["phash", "dhash"]
        }
        
        # Mock the statistics retrieval
        with patch('dataset_forge.menus.fuzzy_dedup_menu.get_fuzzy_matching_statistics', return_value=mock_stats):
            # Call the function
            view_fuzzy_matching_statistics()
            
            # This function should complete without errors
            # We're testing that it displays statistics correctly

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
