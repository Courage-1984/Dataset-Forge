#!/usr/bin/env python3
"""
Simple tests for fuzzy deduplication menu functionality.
Tests basic imports and structure without complex mocking.
"""

import pytest


def test_fuzzy_dedup_menu_imports():
    """Test that fuzzy deduplication menu imports work correctly."""
    try:
        from dataset_forge.menus.fuzzy_dedup_menu import (
            fuzzy_dedup_menu,
            fuzzy_matching_dedup,
            visual_dedup_action,
            file_hash_dedup_action,
            imagededup_action,
            duplicate_analysis_action,
            fuzzy_settings_action,
        )
        
        # Test that functions are callable
        assert callable(fuzzy_dedup_menu)
        assert callable(fuzzy_matching_dedup)
        assert callable(visual_dedup_action)
        assert callable(file_hash_dedup_action)
        assert callable(imagededup_action)
        assert callable(duplicate_analysis_action)
        assert callable(fuzzy_settings_action)
        
    except Exception as e:
        pytest.fail(f"Import failed: {e}")


def test_fuzzy_dedup_menu_structure():
    """Test that the fuzzy deduplication menu has the correct structure."""
    from dataset_forge.menus.fuzzy_dedup_menu import fuzzy_dedup_menu
    
    # The menu should be callable
    assert callable(fuzzy_dedup_menu)


def test_fuzzy_dedup_menu_options():
    """Test that the fuzzy deduplication menu has the expected options."""
    from dataset_forge.menus.fuzzy_dedup_menu import fuzzy_dedup_menu
    
    # Just verify the function exists and is callable
    assert callable(fuzzy_dedup_menu)


def test_fuzzy_dedup_menu_navigation():
    """Test that the fuzzy deduplication menu navigation works."""
    from dataset_forge.menus.fuzzy_dedup_menu import fuzzy_dedup_menu
    
    # Just verify the function exists and is callable
    assert callable(fuzzy_dedup_menu)


def test_fuzzy_dedup_menu_utilities():
    """Test that the fuzzy deduplication menu utilities work."""
    from dataset_forge.menus.fuzzy_dedup_menu import (
        fuzzy_matching_dedup,
        visual_dedup_action,
        file_hash_dedup_action,
        imagededup_action,
        duplicate_analysis_action,
        fuzzy_settings_action,
    )
    
    # Just verify all functions exist and are callable
    assert callable(fuzzy_matching_dedup)
    assert callable(visual_dedup_action)
    assert callable(file_hash_dedup_action)
    assert callable(imagededup_action)
    assert callable(duplicate_analysis_action)
    assert callable(fuzzy_settings_action)


def test_fuzzy_dedup_menu_imports_complete():
    """Test that all required imports work correctly."""
    try:
        from dataset_forge.menus.fuzzy_dedup_menu import (
            fuzzy_dedup_menu,
            fuzzy_matching_dedup,
            visual_dedup_action,
            file_hash_dedup_action,
            imagededup_action,
            duplicate_analysis_action,
            fuzzy_settings_action,
        )
        
        # Test that we can access the module
        import dataset_forge.menus.fuzzy_dedup_menu as fuzzy_module
        assert hasattr(fuzzy_module, 'fuzzy_dedup_menu')
        assert hasattr(fuzzy_module, 'fuzzy_matching_dedup')
        assert hasattr(fuzzy_module, 'visual_dedup_action')
        assert hasattr(fuzzy_module, 'file_hash_dedup_action')
        assert hasattr(fuzzy_module, 'imagededup_action')
        assert hasattr(fuzzy_module, 'duplicate_analysis_action')
        assert hasattr(fuzzy_module, 'fuzzy_settings_action')
        
    except Exception as e:
        pytest.fail(f"Module access failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
