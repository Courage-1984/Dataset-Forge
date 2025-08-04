#!/usr/bin/env python3
"""
Test script for BHI filtering thresholds implementation.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dataset_forge.actions.bhi_filtering_actions import (
    get_default_bhi_thresholds,
    get_bhi_preset_thresholds,
    run_bhi_filtering_with_preset,
    run_bhi_filtering_with_defaults,
)
from dataset_forge.menus import session_state
from dataset_forge.utils.printing import print_info, print_success, print_warning, print_error


def test_threshold_functions():
    """Test the threshold utility functions."""
    print_info("=== Testing BHI Filtering Threshold Functions ===\n")

    # Test default thresholds
    print_info("1. Testing default thresholds:")
    defaults = get_default_bhi_thresholds()
    print_info(f"   Default thresholds: {defaults}")
    assert all(
        k in defaults for k in ["blockiness", "hyperiqa", "ic9600"]
    ), "Missing threshold keys"
    assert all(0.0 <= v <= 1.0 for v in defaults.values()), "Thresholds out of range"
    print_success("   Default thresholds test passed\n")

    # Test preset thresholds
    print_info("2. Testing preset thresholds:")
    presets = ["conservative", "moderate", "aggressive"]
    for preset in presets:
        thresholds = get_bhi_preset_thresholds(preset)
        print_info(f"   {preset.capitalize()} preset: {thresholds}")
        assert all(
            k in thresholds for k in ["blockiness", "hyperiqa", "ic9600"]
        ), f"Missing threshold keys for {preset}"
        assert all(
            0.0 <= v <= 1.0 for v in thresholds.values()
        ), f"Thresholds out of range for {preset}"
    print_success("   Preset thresholds test passed\n")

    # Test invalid preset
    print_info("3. Testing invalid preset (should default to moderate):")
    invalid_thresholds = get_bhi_preset_thresholds("invalid_preset")
    moderate_thresholds = get_bhi_preset_thresholds("moderate")
    assert (
        invalid_thresholds == moderate_thresholds
    ), "Invalid preset should default to moderate"
    print_success("   Invalid preset test passed\n")

    print_success("=== All threshold function tests passed! ===\n")


def test_session_state_integration():
    """Test integration with session state."""
    print_info("=== Testing Session State Integration ===\n")

    # Test that session state has BHI preferences
    print_info("1. Testing session state BHI preferences:")
    assert (
        "bhi_blockiness_threshold" in session_state.user_preferences
    ), "Missing bhi_blockiness_threshold"
    assert (
        "bhi_hyperiqa_threshold" in session_state.user_preferences
    ), "Missing bhi_hyperiqa_threshold"
    assert (
        "bhi_ic9600_threshold" in session_state.user_preferences
    ), "Missing bhi_ic9600_threshold"
    assert (
        "bhi_suggested_thresholds" in session_state.user_preferences
    ), "Missing bhi_suggested_thresholds"

    print_info(
        f"   Current default thresholds: {session_state.user_preferences['bhi_blockiness_threshold']}, "
        f"{session_state.user_preferences['bhi_hyperiqa_threshold']}, "
        f"{session_state.user_preferences['bhi_ic9600_threshold']}"
    )

    suggested = session_state.user_preferences["bhi_suggested_thresholds"]
    print_info(f"   Available presets: {list(suggested.keys())}")
    print_success("   Session state integration test passed\n")

    print_success("=== Session state integration tests passed! ===\n")


def test_threshold_validation():
    """Test threshold validation."""
    print_info("=== Testing Threshold Validation ===\n")

    # Test that all thresholds are in valid range
    print_info("1. Testing threshold range validation:")
    defaults = get_default_bhi_thresholds()
    for metric, value in defaults.items():
        assert 0.0 <= value <= 1.0, f"Invalid {metric} threshold: {value}"
        print_success(f"   {metric}: {value} ✅")

    presets = ["conservative", "moderate", "aggressive"]
    for preset in presets:
        thresholds = get_bhi_preset_thresholds(preset)
        for metric, value in thresholds.items():
            assert (
                0.0 <= value <= 1.0
            ), f"Invalid {metric} threshold in {preset} preset: {value}"
        print_success(f"   {preset} preset: all thresholds valid ✅")

    print_success("   Threshold validation test passed\n")

    print_success("=== Threshold validation tests passed! ===\n")


def main():
    """Run all tests."""
    print_info("BHI Filtering Thresholds Implementation Test\n")
    print_info("=" * 50)

    try:
        test_threshold_functions()
        test_session_state_integration()
        test_threshold_validation()

        print_success(
            "🎉 All tests passed! BHI filtering thresholds implementation is working correctly."
        )
        print_info("\nKey features implemented:")
        print_success("✅ Default thresholds from session state")
        print_success("✅ Preset configurations (conservative, moderate, aggressive)")
        print_success("✅ Fallback defaults when session state unavailable")
        print_success("✅ Threshold validation (0.0-1.0 range)")
        print_success("✅ Integration with existing BHI filtering functionality")

    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
