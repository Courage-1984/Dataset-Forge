"""
Tests for cleanup actions in Dataset Forge.

This module tests all cleanup functionality including:
- Finding cache folders
- Removing cache folders
- Comprehensive cleanup operations
- Cache usage analysis
"""

import os
import tempfile
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the cleanup actions
from dataset_forge.actions.cleanup_actions import (
    find_cache_folders,
    remove_cache_folders,
    cleanup_pytest_cache,
    cleanup_pycache,
    cleanup_all_cache_folders,
    comprehensive_cleanup,
    analyze_cache_usage,
)


class TestFindCacheFolders:
    """Test cache folder discovery functionality."""

    def test_find_cache_folders_empty(self, tmp_path):
        """Test finding cache folders in empty directory."""
        with patch('dataset_forge.actions.cleanup_actions.print_info'):
            result = find_cache_folders(str(tmp_path))
        
        assert isinstance(result, dict)
        assert "pytest_cache" in result
        assert "pycache" in result
        assert result["pytest_cache"] == []
        assert result["pycache"] == []

    def test_find_cache_folders_with_pytest_cache(self, tmp_path):
        """Test finding .pytest_cache folders."""
        # Create some .pytest_cache folders
        pytest_cache1 = tmp_path / "dir1" / ".pytest_cache"
        pytest_cache1.mkdir(parents=True)
        pytest_cache2 = tmp_path / "dir2" / "subdir" / ".pytest_cache"
        pytest_cache2.mkdir(parents=True)
        
        with patch('dataset_forge.actions.cleanup_actions.print_info'):
            result = find_cache_folders(str(tmp_path))
        
        assert len(result["pytest_cache"]) == 2
        assert str(pytest_cache1) in result["pytest_cache"]
        assert str(pytest_cache2) in result["pytest_cache"]
        assert result["pycache"] == []

    def test_find_cache_folders_with_pycache(self, tmp_path):
        """Test finding __pycache__ folders."""
        # Create some __pycache__ folders
        pycache1 = tmp_path / "dir1" / "__pycache__"
        pycache1.mkdir(parents=True)
        pycache2 = tmp_path / "dir2" / "subdir" / "__pycache__"
        pycache2.mkdir(parents=True)
        
        with patch('dataset_forge.actions.cleanup_actions.print_info'):
            result = find_cache_folders(str(tmp_path))
        
        assert len(result["pycache"]) == 2
        assert str(pycache1) in result["pycache"]
        assert str(pycache2) in result["pycache"]
        assert result["pytest_cache"] == []

    def test_find_cache_folders_mixed(self, tmp_path):
        """Test finding both types of cache folders."""
        # Create mixed cache folders
        pytest_cache = tmp_path / "dir1" / ".pytest_cache"
        pytest_cache.mkdir(parents=True)
        pycache = tmp_path / "dir2" / "__pycache__"
        pycache.mkdir(parents=True)
        
        with patch('dataset_forge.actions.cleanup_actions.print_info'):
            result = find_cache_folders(str(tmp_path))
        
        assert len(result["pytest_cache"]) == 1
        assert len(result["pycache"]) == 1
        assert str(pytest_cache) in result["pytest_cache"]
        assert str(pycache) in result["pycache"]


class TestRemoveCacheFolders:
    """Test cache folder removal functionality."""

    def test_remove_cache_folders_empty_list(self):
        """Test removing empty list of folders."""
        with patch('dataset_forge.actions.cleanup_actions.print_info'):
            successful, failed = remove_cache_folders([], "test_cache")
        
        assert successful == 0
        assert failed == []

    def test_remove_cache_folders_success(self, tmp_path):
        """Test successful folder removal."""
        # Create test folders
        folder1 = tmp_path / "test_folder1"
        folder1.mkdir()
        folder2 = tmp_path / "test_folder2"
        folder2.mkdir()
        
        folders = [str(folder1), str(folder2)]
        
        with patch('dataset_forge.actions.cleanup_actions.print_success'):
            successful, failed = remove_cache_folders(folders, "test_cache")
        
        assert successful == 2
        assert failed == []
        assert not folder1.exists()
        assert not folder2.exists()

    def test_remove_cache_folders_permission_error(self, tmp_path):
        """Test handling permission errors."""
        # Create a folder that can't be removed (simulate permission error)
        folder = tmp_path / "protected_folder"
        folder.mkdir()
        
        with patch('shutil.rmtree', side_effect=PermissionError("Permission denied")):
            with patch('dataset_forge.actions.cleanup_actions.print_error'):
                successful, failed = remove_cache_folders([str(folder)], "test_cache")
        
        assert successful == 0
        assert len(failed) == 1
        assert str(folder) in failed

    def test_remove_cache_folders_nonexistent(self, tmp_path):
        """Test handling nonexistent folders."""
        nonexistent_folder = str(tmp_path / "nonexistent")
        
        with patch('dataset_forge.actions.cleanup_actions.print_warning'):
            successful, failed = remove_cache_folders([nonexistent_folder], "test_cache")
        
        assert successful == 0
        assert failed == []


class TestCleanupFunctions:
    """Test the main cleanup functions."""

    @patch('dataset_forge.actions.cleanup_actions.find_cache_folders')
    @patch('dataset_forge.actions.cleanup_actions.remove_cache_folders')
    @patch('dataset_forge.actions.cleanup_actions.clear_memory')
    @patch('dataset_forge.actions.cleanup_actions.clear_cuda_cache')
    def test_cleanup_pytest_cache(self, mock_clear_cuda, mock_clear_memory, 
                                 mock_remove, mock_find):
        """Test pytest cache cleanup."""
        mock_find.return_value = {
            "pytest_cache": ["/path/to/pytest_cache1", "/path/to/pytest_cache2"],
            "pycache": []
        }
        mock_remove.return_value = (2, [])
        
        with patch('dataset_forge.actions.cleanup_actions.print_header'), \
             patch('dataset_forge.actions.cleanup_actions.print_section'), \
             patch('dataset_forge.actions.cleanup_actions.print_success'), \
             patch('dataset_forge.actions.cleanup_actions.print_info'):
            cleanup_pytest_cache()
        
        mock_find.assert_called_once()
        mock_remove.assert_called_once_with(
            ["/path/to/pytest_cache1", "/path/to/pytest_cache2"], 
            ".pytest_cache"
        )
        mock_clear_memory.assert_called_once()
        mock_clear_cuda.assert_called_once()

    @patch('dataset_forge.actions.cleanup_actions.find_cache_folders')
    @patch('dataset_forge.actions.cleanup_actions.remove_cache_folders')
    @patch('dataset_forge.actions.cleanup_actions.clear_memory')
    @patch('dataset_forge.actions.cleanup_actions.clear_cuda_cache')
    def test_cleanup_pycache(self, mock_clear_cuda, mock_clear_memory, 
                           mock_remove, mock_find):
        """Test pycache cleanup."""
        mock_find.return_value = {
            "pytest_cache": [],
            "pycache": ["/path/to/pycache1", "/path/to/pycache2"]
        }
        mock_remove.return_value = (2, [])
        
        with patch('dataset_forge.actions.cleanup_actions.print_header'), \
             patch('dataset_forge.actions.cleanup_actions.print_section'), \
             patch('dataset_forge.actions.cleanup_actions.print_success'), \
             patch('dataset_forge.actions.cleanup_actions.print_info'):
            cleanup_pycache()
        
        mock_find.assert_called_once()
        mock_remove.assert_called_once_with(
            ["/path/to/pycache1", "/path/to/pycache2"], 
            "__pycache__"
        )
        mock_clear_memory.assert_called_once()
        mock_clear_cuda.assert_called_once()

    @patch('dataset_forge.actions.cleanup_actions.find_cache_folders')
    @patch('dataset_forge.actions.cleanup_actions.remove_cache_folders')
    @patch('dataset_forge.actions.cleanup_actions.clear_memory')
    @patch('dataset_forge.actions.cleanup_actions.clear_cuda_cache')
    def test_cleanup_all_cache_folders(self, mock_clear_cuda, mock_clear_memory, 
                                     mock_remove, mock_find):
        """Test cleanup of all cache folders."""
        mock_find.return_value = {
            "pytest_cache": ["/path/to/pytest_cache"],
            "pycache": ["/path/to/pycache"]
        }
        mock_remove.side_effect = [(1, []), (1, [])]
        
        with patch('dataset_forge.actions.cleanup_actions.print_header'), \
             patch('dataset_forge.actions.cleanup_actions.print_section'), \
             patch('dataset_forge.actions.cleanup_actions.print_success'), \
             patch('dataset_forge.actions.cleanup_actions.print_info'):
            cleanup_all_cache_folders()
        
        assert mock_remove.call_count == 2
        mock_clear_memory.assert_called_once()
        mock_clear_cuda.assert_called_once()


class TestComprehensiveCleanup:
    """Test comprehensive cleanup functionality."""

    @patch('dataset_forge.actions.cleanup_actions.cleanup_all_cache_folders')
    @patch('dataset_forge.actions.cleanup_actions.clear_disk_cache')
    @patch('dataset_forge.actions.cleanup_actions.clear_in_memory_cache')
    @patch('dataset_forge.actions.cleanup_actions.clear_cuda_cache')
    @patch('dataset_forge.actions.cleanup_actions.clear_memory')
    def test_comprehensive_cleanup_success(self, mock_clear_memory, mock_clear_cuda,
                                         mock_clear_in_memory, mock_clear_disk,
                                         mock_cleanup_all):
        """Test successful comprehensive cleanup."""
        with patch('dataset_forge.actions.cleanup_actions.print_header'), \
             patch('dataset_forge.actions.cleanup_actions.print_section'), \
             patch('dataset_forge.actions.cleanup_actions.print_success'), \
             patch('dataset_forge.actions.cleanup_actions.print_info'):
            comprehensive_cleanup()
        
        mock_cleanup_all.assert_called_once()
        mock_clear_disk.assert_called_once()
        mock_clear_in_memory.assert_called_once()
        mock_clear_cuda.assert_called_once()
        mock_clear_memory.assert_called_once()

    @patch('dataset_forge.actions.cleanup_actions.cleanup_all_cache_folders')
    @patch('dataset_forge.actions.cleanup_actions.clear_disk_cache')
    @patch('dataset_forge.actions.cleanup_actions.clear_in_memory_cache')
    @patch('dataset_forge.actions.cleanup_actions.clear_cuda_cache')
    @patch('dataset_forge.actions.cleanup_actions.clear_memory')
    def test_comprehensive_cleanup_with_errors(self, mock_clear_memory, mock_clear_cuda,
                                             mock_clear_in_memory, mock_clear_disk,
                                             mock_cleanup_all):
        """Test comprehensive cleanup with some errors."""
        mock_clear_disk.side_effect = Exception("Disk cache error")
        mock_clear_in_memory.side_effect = Exception("Memory cache error")
        
        with patch('dataset_forge.actions.cleanup_actions.print_header'), \
             patch('dataset_forge.actions.cleanup_actions.print_section'), \
             patch('dataset_forge.actions.cleanup_actions.print_success'), \
             patch('dataset_forge.actions.cleanup_actions.print_error'), \
             patch('dataset_forge.actions.cleanup_actions.print_info'):
            comprehensive_cleanup()
        
        mock_cleanup_all.assert_called_once()
        mock_clear_disk.assert_called_once()
        mock_clear_in_memory.assert_called_once()
        mock_clear_cuda.assert_called_once()
        mock_clear_memory.assert_called_once()


class TestAnalyzeCacheUsage:
    """Test cache usage analysis functionality."""

    @patch('dataset_forge.actions.cleanup_actions.find_cache_folders')
    def test_analyze_cache_usage_no_folders(self, mock_find):
        """Test analysis with no cache folders."""
        mock_find.return_value = {
            "pytest_cache": [],
            "pycache": []
        }
        
        with patch('dataset_forge.actions.cleanup_actions.print_header'), \
             patch('dataset_forge.actions.cleanup_actions.print_section'), \
             patch('dataset_forge.actions.cleanup_actions.print_info'), \
             patch('dataset_forge.actions.cleanup_actions.print_success'):
            analyze_cache_usage()
        
        mock_find.assert_called_once()

    @patch('dataset_forge.actions.cleanup_actions.find_cache_folders')
    def test_analyze_cache_usage_with_folders(self, mock_find, tmp_path):
        """Test analysis with cache folders."""
        # Create test cache folders with files
        pytest_cache = tmp_path / "dir1" / ".pytest_cache"
        pytest_cache.mkdir(parents=True)
        (pytest_cache / "test_file.txt").write_text("test content")
        
        pycache = tmp_path / "dir2" / "__pycache__"
        pycache.mkdir(parents=True)
        (pycache / "test_file.pyc").write_bytes(b"test bytecode")
        
        mock_find.return_value = {
            "pytest_cache": [str(pytest_cache)],
            "pycache": [str(pycache)]
        }
        
        with patch('dataset_forge.actions.cleanup_actions.print_header'), \
             patch('dataset_forge.actions.cleanup_actions.print_section'), \
             patch('dataset_forge.actions.cleanup_actions.print_info'):
            analyze_cache_usage()
        
        mock_find.assert_called_once() 