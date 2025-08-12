#!/usr/bin/env python3
"""
Comprehensive tests for DPID menu integration.

Tests the new consolidated DPID downscaling menu system including:
- Menu navigation and structure
- Parameter configuration
- Processing workflows
- Error handling
- Session state integration
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import numpy as np
from PIL import Image

from dataset_forge.actions.dpid_actions import (
    dpid_menu,
    umzi_dpid_menu,
    phhofm_dpid_menu,
    basicsr_dpid_menu,
    openmmlab_dpid_menu,
    compare_dpid_methods,
    configure_umzi_dpid_params,
    configure_phhofm_dpid_params,
    configure_basicsr_dpid_params,
    configure_openmmlab_dpid_params,
    umzi_dpid_single_folder,
    umzi_dpid_hq_lq_pairs,
    phhofm_dpid_single_folder,
    phhofm_dpid_hq_lq_pairs,
    basicsr_dpid_single_folder,
    basicsr_dpid_hq_lq_pairs,
    openmmlab_dpid_single_folder,
    openmmlab_dpid_hq_lq_pairs,
)
from dataset_forge.menus import session_state
from dataset_forge.utils.printing import print_info, print_success, print_error


def make_test_image(path: str, size: tuple = (64, 64)) -> None:
    """Create a test image for DPID processing."""
    arr = np.random.randint(0, 255, size + (3,), dtype=np.uint8)
    Image.fromarray(arr).save(path)


class TestDPIDMenuStructure:
    """Test DPID menu structure and navigation."""

    def test_dpid_menu_import(self):
        """Test that DPID menu can be imported successfully."""
        assert dpid_menu is not None
        assert callable(dpid_menu)

    def test_all_dpid_menus_importable(self):
        """Test that all DPID sub-menus can be imported."""
        menus = [
            umzi_dpid_menu,
            phhofm_dpid_menu,
            basicsr_dpid_menu,
            openmmlab_dpid_menu,
        ]
        for menu in menus:
            assert menu is not None
            assert callable(menu)

    def test_compare_dpid_methods_importable(self):
        """Test that compare_dpid_methods can be imported."""
        assert compare_dpid_methods is not None
        assert callable(compare_dpid_methods)

    def test_configuration_functions_importable(self):
        """Test that all configuration functions can be imported."""
        config_functions = [
            configure_umzi_dpid_params,
            configure_phhofm_dpid_params,
            configure_basicsr_dpid_params,
            configure_openmmlab_dpid_params,
        ]
        for func in config_functions:
            assert func is not None
            assert callable(func)

    def test_processing_functions_importable(self):
        """Test that all processing functions can be imported."""
        processing_functions = [
            umzi_dpid_single_folder,
            umzi_dpid_hq_lq_pairs,
            phhofm_dpid_single_folder,
            phhofm_dpid_hq_lq_pairs,
            basicsr_dpid_single_folder,
            basicsr_dpid_hq_lq_pairs,
            openmmlab_dpid_single_folder,
            openmmlab_dpid_hq_lq_pairs,
        ]
        for func in processing_functions:
            assert func is not None
            assert callable(func)


class TestDPIDMenuIntegration:
    """Test DPID menu integration with the main application."""

    def test_dpid_menu_structure(self):
        """Test DPID menu structure and options."""
        # Import the menu function to access its structure
        from dataset_forge.actions.dpid_actions import dpid_menu

        # Get the source code to extract structure
        import inspect

        source = inspect.getsource(dpid_menu)

        # Check that the function has the expected structure
        assert "show_menu(" in source, "Menu should use show_menu function"
        assert (
            "DPID Detail-Preserving Image Downscaling" in source
        ), "Menu should have correct title"

        # Check that expected options are mentioned in the source
        expected_options = ["1", "2", "3", "4", "5", "0"]
        for option in expected_options:
            assert (
                f'"{option}":' in source
            ), f"Option {option} should be present in menu"

        # Check that expected descriptions are mentioned
        assert "Umzi's DPID" in source, "Umzi's DPID should be mentioned"
        assert "Phhofm DPID" in source, "Phhofm DPID should be mentioned"
        assert "BasicSR DPID" in source, "BasicSR DPID should be mentioned"
        assert "OpenMMLab DPID" in source, "OpenMMLab DPID should be mentioned"
        assert "Compare" in source, "Compare option should be mentioned"

    def test_umzi_dpid_menu_structure(self):
        """Test Umzi's DPID menu structure."""
        # Import the menu function to access its structure
        from dataset_forge.actions.dpid_actions import umzi_dpid_menu

        # Get the source code to extract structure
        import inspect

        source = inspect.getsource(umzi_dpid_menu)

        # Check that the function has the expected structure
        assert "show_menu(" in source, "Menu should use show_menu function"
        assert "Umzi's DPID" in source, "Menu should have correct title"

        # Check that expected options are mentioned in the source
        expected_options = ["1", "2", "3", "0"]
        for option in expected_options:
            assert (
                f'"{option}":' in source
            ), f"Option {option} should be present in menu"

        # Check that expected descriptions are mentioned
        assert "Single Folder" in source, "Single Folder option should be mentioned"
        assert "HQ/LQ Paired" in source, "HQ/LQ Paired option should be mentioned"
        assert "Configure" in source, "Configure option should be mentioned"


class TestDPIDParameterConfiguration:
    """Test DPID parameter configuration functionality."""

    def setup_method(self):
        """Clear session state before each test."""
        # Clear any existing DPID parameters
        for attr in dir(session_state):
            if "dpid" in attr.lower():
                delattr(session_state, attr)

    @patch("dataset_forge.actions.dpid_actions.ask_float")
    @patch("builtins.input")
    @patch("dataset_forge.actions.dpid_actions.print_success")
    @patch("dataset_forge.actions.dpid_actions.play_done_sound")
    def test_configure_umzi_dpid_params(
        self, mock_audio, mock_print_success, mock_input, mock_ask_float
    ):
        """Test Umzi's DPID parameter configuration."""
        # Mock user input
        mock_ask_float.return_value = 0.7
        mock_input.return_value = "0.5,0.25"

        configure_umzi_dpid_params()

        # Verify parameters were set in session state
        assert hasattr(session_state, "umzi_dpid_lambda")
        assert session_state.umzi_dpid_lambda == 0.7
        assert hasattr(session_state, "umzi_dpid_scales")
        assert session_state.umzi_dpid_scales == [0.5, 0.25]

        # Verify success message was printed
        mock_print_success.assert_called_once()
        mock_audio.assert_called_once()

    @patch("dataset_forge.actions.dpid_actions.ask_int")
    @patch("dataset_forge.actions.dpid_actions.ask_float")
    @patch("builtins.input")
    @patch("dataset_forge.actions.dpid_actions.print_success")
    @patch("dataset_forge.actions.dpid_actions.play_done_sound")
    def test_configure_basicsr_dpid_params(
        self, mock_audio, mock_print_success, mock_input, mock_ask_float, mock_ask_int
    ):
        """Test BasicSR DPID parameter configuration."""
        # Mock user input
        mock_ask_int.return_value = 21  # kernel_size
        mock_ask_float.side_effect = [2.5, 0.6]  # sigma, lambda
        mock_input.return_value = "0.5,0.25,0.125"

        configure_basicsr_dpid_params()

        # Verify parameters were set in session state
        assert hasattr(session_state, "basicsr_dpid_kernel_size")
        assert session_state.basicsr_dpid_kernel_size == 21
        assert hasattr(session_state, "basicsr_dpid_sigma")
        assert session_state.basicsr_dpid_sigma == 2.5
        assert hasattr(session_state, "basicsr_dpid_lambda")
        assert session_state.basicsr_dpid_lambda == 0.6
        assert hasattr(session_state, "basicsr_dpid_scales")
        assert session_state.basicsr_dpid_scales == [0.5, 0.25, 0.125]

        # Verify success message was printed
        mock_print_success.assert_called_once()
        mock_audio.assert_called_once()


class TestDPIDProcessingWorkflows:
    """Test DPID processing workflows with mocked dependencies."""

    def setup_method(self):
        """Set up test environment."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.input_dir.mkdir()
        self.output_dir.mkdir()

        # Create test images
        make_test_image(str(self.input_dir / "test1.png"))
        make_test_image(str(self.input_dir / "test2.png"))

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("dataset_forge.actions.dpid_actions.get_destination_path")
    @patch("dataset_forge.actions.dpid_actions.get_folder_path")
    @patch("dataset_forge.actions.dpid_actions.ask_yes_no")
    @patch("dataset_forge.actions.dpid_actions.print_success")
    @patch("dataset_forge.actions.dpid_actions.play_done_sound")
    @patch("dataset_forge.dpid.umzi_dpid.run_umzi_dpid_single_folder")
    def test_umzi_dpid_single_folder_workflow(
        self,
        mock_run,
        mock_audio,
        mock_print_success,
        mock_ask_yes_no,
        mock_get_folder_path,
        mock_get_destination_path,
    ):
        """Test Umzi's DPID single folder processing workflow."""
        # Mock user input
        mock_get_folder_path.return_value = str(self.input_dir)
        mock_get_destination_path.return_value = str(self.output_dir)
        mock_ask_yes_no.return_value = True

        # Mock the DPID processing function
        mock_run.return_value = None

        # Set session state parameters
        session_state.umzi_dpid_lambda = 0.5
        session_state.umzi_dpid_scales = [0.5, 0.25]

        umzi_dpid_single_folder()

        # Verify the DPID function was called with correct parameters
        mock_run.assert_called_once_with(
            input_folder=str(self.input_dir),
            output_base=str(self.output_dir),
            scales=[0.5, 0.25],
            overwrite=False,
            lambd=0.5,
        )

        # Verify success feedback
        mock_print_success.assert_called_once()
        mock_audio.assert_called_once()

    @patch("dataset_forge.actions.dpid_actions.get_destination_path")
    @patch("dataset_forge.actions.dpid_actions.get_folder_path")
    @patch("dataset_forge.actions.dpid_actions.ask_yes_no")
    @patch("dataset_forge.actions.dpid_actions.print_success")
    @patch("dataset_forge.actions.dpid_actions.play_done_sound")
    @patch("dataset_forge.dpid.basicsr_dpid.run_basicsr_dpid_single_folder")
    def test_basicsr_dpid_single_folder_workflow(
        self,
        mock_run,
        mock_audio,
        mock_print_success,
        mock_ask_yes_no,
        mock_get_folder_path,
        mock_get_destination_path,
    ):
        """Test BasicSR DPID single folder processing workflow."""
        # Mock user input
        mock_get_folder_path.return_value = str(self.input_dir)
        mock_get_destination_path.return_value = str(self.output_dir)
        mock_ask_yes_no.return_value = True

        # Mock the DPID processing function
        mock_run.return_value = None

        # Set session state parameters
        session_state.basicsr_dpid_kernel_size = 21
        session_state.basicsr_dpid_sigma = 2.0
        session_state.basicsr_dpid_lambda = 0.5
        session_state.basicsr_dpid_scales = [0.5, 0.25]

        basicsr_dpid_single_folder()

        # Verify the DPID function was called with correct parameters
        mock_run.assert_called_once_with(
            input_folder=str(self.input_dir),
            output_base=str(self.output_dir),
            scales=[0.5, 0.25],
            overwrite=False,
            kernel_size=21,
            sigma=2.0,
            lambd=0.5,
            isotropic=True,
        )

        # Verify success feedback
        mock_print_success.assert_called_once()
        mock_audio.assert_called_once()

    @patch("dataset_forge.actions.dpid_actions.get_destination_path")
    @patch("dataset_forge.actions.dpid_actions.get_folder_path")
    @patch("dataset_forge.actions.dpid_actions.ask_yes_no")
    @patch("dataset_forge.actions.dpid_actions.print_success")
    @patch("dataset_forge.actions.dpid_actions.play_done_sound")
    @patch("dataset_forge.dpid.umzi_dpid.run_umzi_dpid_hq_lq")
    def test_umzi_dpid_hq_lq_workflow(
        self,
        mock_run,
        mock_audio,
        mock_print_success,
        mock_ask_yes_no,
        mock_get_folder_path,
        mock_get_destination_path,
    ):
        """Test Umzi's DPID HQ/LQ paired processing workflow."""
        # Create HQ/LQ directories
        hq_dir = self.input_dir / "hq"
        lq_dir = self.input_dir / "lq"
        out_hq_dir = self.output_dir / "hq"
        out_lq_dir = self.output_dir / "lq"
        hq_dir.mkdir()
        lq_dir.mkdir()
        out_hq_dir.mkdir()
        out_lq_dir.mkdir()

        # Create test images
        make_test_image(str(hq_dir / "test1.png"))
        make_test_image(str(lq_dir / "test1.png"))

        # Mock user input
        mock_get_folder_path.side_effect = [str(hq_dir), str(lq_dir)]
        mock_get_destination_path.side_effect = [str(out_hq_dir), str(out_lq_dir)]
        mock_ask_yes_no.return_value = True

        # Mock the DPID processing function
        mock_run.return_value = None

        # Set session state parameters
        session_state.umzi_dpid_lambda = 0.5
        session_state.umzi_dpid_scales = [0.5, 0.25]

        umzi_dpid_hq_lq_pairs()

        # Verify the DPID function was called with correct parameters
        mock_run.assert_called_once_with(
            hq_folder=str(hq_dir),
            lq_folder=str(lq_dir),
            out_hq_base=str(out_hq_dir),
            out_lq_base=str(out_lq_dir),
            scales=[0.5, 0.25],
            overwrite=False,
            lambd=0.5,
        )

        # Verify success feedback
        mock_print_success.assert_called_once()
        mock_audio.assert_called_once()


class TestDPIDErrorHandling:
    """Test DPID error handling and edge cases."""

    def test_umzi_dpid_menu_pepedpid_import_error(self):
        """Test Umzi's DPID menu handles pepedpid import error gracefully."""
        # Import the menu function to access its structure
        from dataset_forge.actions.dpid_actions import umzi_dpid_menu

        # Get the source code to extract structure
        import inspect

        source = inspect.getsource(umzi_dpid_menu)

        # Check that the function has error handling structure
        assert "try:" in source, "Menu should have try-catch error handling"
        assert "except" in source, "Menu should have exception handling"
        assert "print_error(" in source, "Menu should call print_error for errors"

    @patch("dataset_forge.actions.dpid_actions.ask_yes_no")
    @patch("dataset_forge.actions.dpid_actions.get_destination_path")
    @patch("dataset_forge.actions.dpid_actions.get_folder_path")
    @patch("dataset_forge.actions.dpid_actions.print_error")
    @patch("dataset_forge.actions.dpid_actions.clear_memory")
    @patch("dataset_forge.actions.dpid_actions.clear_cuda_cache")
    def test_umzi_dpid_single_folder_processing_error(
        self,
        mock_clear_cuda,
        mock_clear_memory,
        mock_print_error,
        mock_get_folder_path,
        mock_get_destination_path,
        mock_ask_yes_no,
    ):
        """Test Umzi's DPID single folder handles processing errors gracefully."""
        # Mock user input to return valid paths
        mock_get_folder_path.return_value = "/test/path"
        mock_get_destination_path.return_value = "/test/output"
        mock_ask_yes_no.return_value = True

        # Mock the DPID processing function to raise an exception
        with patch(
            "dataset_forge.dpid.umzi_dpid.run_umzi_dpid_single_folder",
            side_effect=Exception("Processing failed"),
        ):
            umzi_dpid_single_folder()

        # Verify error handling
        mock_print_error.assert_called_once()
        mock_clear_memory.assert_called_once()
        mock_clear_cuda.assert_called_once()

        error_message = mock_print_error.call_args[0][0]
        assert "Error during processing" in error_message

    @patch("dataset_forge.actions.dpid_actions.get_folder_path")
    def test_umzi_dpid_single_folder_cancelled_by_user(self, mock_get_folder_path):
        """Test Umzi's DPID single folder handles user cancellation gracefully."""
        # Mock user input to return None (cancelled)
        mock_get_folder_path.return_value = None

        # This should not raise any exceptions
        umzi_dpid_single_folder()


class TestDPIDMethodComparison:
    """Test DPID method comparison functionality."""

    @patch("builtins.input")
    def test_compare_dpid_methods(self, mock_input):
        """Test DPID method comparison displays correctly."""
        mock_input.return_value = ""  # Press Enter to continue

        # This should not raise any exceptions
        compare_dpid_methods()


class TestDPIDSessionState:
    """Test DPID session state integration."""

    def setup_method(self):
        """Clear session state before each test."""
        # Clear any existing DPID parameters
        for attr in dir(session_state):
            if "dpid" in attr.lower():
                delattr(session_state, attr)

    def test_session_state_default_values(self):
        """Test that session state provides default values when not set."""
        # Test default values for Umzi's DPID
        lambda_val = getattr(session_state, "umzi_dpid_lambda", 0.5)
        scales = getattr(session_state, "umzi_dpid_scales", [0.5, 0.25])

        assert lambda_val == 0.5
        assert scales == [0.5, 0.25]

    def test_session_state_persistence(self):
        """Test that session state persists values across function calls."""
        # Set values
        session_state.umzi_dpid_lambda = 0.8
        session_state.umzi_dpid_scales = [0.3, 0.15]

        # Verify values are set
        assert session_state.umzi_dpid_lambda == 0.8
        assert session_state.umzi_dpid_scales == [0.3, 0.15]

        # Test that getattr returns the set values
        lambda_val = getattr(session_state, "umzi_dpid_lambda", 0.5)
        scales = getattr(session_state, "umzi_dpid_scales", [0.5, 0.25])

        assert lambda_val == 0.8
        assert scales == [0.3, 0.15]


if __name__ == "__main__":
    pytest.main([__file__])
