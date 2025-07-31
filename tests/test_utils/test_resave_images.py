"""
Tests for resave images functionality.

This module tests the resave images actions with proper mocking and error handling,
following the Dataset Forge testing patterns.
"""

import os
import tempfile
from typing import TYPE_CHECKING
from unittest.mock import patch, MagicMock, Mock
import pytest
import cv2
import numpy as np

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

from dataset_forge.actions.resave_images_actions import (
    process_single_image,
    resave_images,
    resave_images_workflow,
)


@pytest.fixture
def sample_image_path(tmp_path):
    """Create a sample image for testing."""
    image_path = tmp_path / "test.jpg"

    # Create a simple test image
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(image_path), test_image)

    return str(image_path)


@pytest.fixture
def sample_image_dir(tmp_path):
    """Create a directory with sample images for testing."""
    # Create test images
    for i in range(3):
        image_path = tmp_path / f"test_{i}.jpg"
        test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        cv2.imwrite(str(image_path), test_image)

    return str(tmp_path)


def test_process_single_image_success(sample_image_path, tmp_path):
    """Test successful processing of a single image."""
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir, exist_ok=True)

    result = process_single_image(sample_image_path, output_dir, "png", False)

    assert result is True

    # Check that output file was created
    expected_output = os.path.join(output_dir, "test.png")
    assert os.path.exists(expected_output)


def test_process_single_image_grayscale(sample_image_path, tmp_path):
    """Test processing image with grayscale conversion."""
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir, exist_ok=True)

    result = process_single_image(sample_image_path, output_dir, "png", True)

    assert result is True

    # Check that output file was created
    expected_output = os.path.join(output_dir, "test.png")
    assert os.path.exists(expected_output)

    # Verify it's grayscale
    output_image = cv2.imread(expected_output, cv2.IMREAD_GRAYSCALE)
    assert output_image is not None
    assert len(output_image.shape) == 2  # Grayscale should be 2D


def test_process_single_image_different_formats(sample_image_path, tmp_path):
    """Test processing image to different output formats."""
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir, exist_ok=True)

    formats = ["png", "jpg", "webp"]

    for fmt in formats:
        result = process_single_image(sample_image_path, output_dir, fmt, False)
        assert result is True

        expected_output = os.path.join(output_dir, f"test.{fmt}")
        assert os.path.exists(expected_output)


def test_process_single_image_nonexistent_file(tmp_path):
    """Test processing with nonexistent input file."""
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir, exist_ok=True)

    result = process_single_image("nonexistent.jpg", output_dir, "png", False)

    assert result is False


def test_process_single_image_corrupted_file(tmp_path):
    """Test processing with corrupted image file."""
    # Create a corrupted image file
    corrupted_path = tmp_path / "corrupted.jpg"
    with open(corrupted_path, "w") as f:
        f.write("This is not an image file")

    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir, exist_ok=True)

    result = process_single_image(str(corrupted_path), output_dir, "png", False)

    assert result is False


@patch("dataset_forge.actions.resave_images_actions.ThreadPoolExecutor")
def test_resave_images_success(mock_executor):
    """Test successful resave images operation."""
    # Create mock executor
    mock_executor_instance = MagicMock()
    mock_executor.return_value.__enter__.return_value = mock_executor_instance

    # Mock futures
    mock_futures = [MagicMock() for _ in range(3)]
    for future in mock_futures:
        future.result.return_value = True

    mock_executor_instance.submit.side_effect = mock_futures

    # Create test data
    input_dir = "/test/input"
    dest_dir = "/test/output"

    # Mock os.scandir to return test files
    with patch("os.scandir") as mock_scandir:
        mock_entries = [
            MagicMock(
                is_file=lambda: True, name="test1.png", path="/test/input/test1.png"
            ),
            MagicMock(
                is_file=lambda: True, name="test2.jpg", path="/test/input/test2.jpg"
            ),
            MagicMock(
                is_file=lambda: True, name="test3.png", path="/test/input/test3.png"
            ),
        ]
        mock_scandir.return_value.__enter__.return_value = mock_entries

        # Mock os.path.exists and os.makedirs
        with patch("os.path.exists", return_value=True):
            with patch("os.path.isdir", return_value=True):
                with patch("os.makedirs"):
                    # Test the function
                    processed, skipped, failed = resave_images(input_dir, dest_dir)

                    # Verify results
                    assert processed == 3
                    assert skipped == 0
                    assert failed == 0

                    # Verify executor was called correctly
                    mock_executor.assert_called_once_with(max_workers=2)
                    assert mock_executor_instance.submit.call_count == 3


@patch("dataset_forge.actions.resave_images_actions.ThreadPoolExecutor")
def test_resave_images_with_failures(mock_executor):
    """Test resaving with some failures."""
    # Create mock executor
    mock_executor_instance = MagicMock()
    mock_executor.return_value.__enter__.return_value = mock_executor_instance

    # Mock futures - return the actual results directly
    mock_futures = [True, False, True]  # 2 success, 1 failure

    mock_executor_instance.submit.side_effect = mock_futures

    # Create test data
    input_dir = "/test/input"
    dest_dir = "/test/output"

    # Mock os.scandir to return test files
    with patch("os.scandir") as mock_scandir:
        mock_entries = [
            MagicMock(
                is_file=lambda: True, name="test1.png", path="/test/input/test1.png"
            ),
            MagicMock(
                is_file=lambda: True, name="test2.jpg", path="/test/input/test2.jpg"
            ),
            MagicMock(
                is_file=lambda: True, name="test3.png", path="/test/input/test3.png"
            ),
        ]
        mock_scandir.return_value.__enter__.return_value = mock_entries

        # Mock os.path.exists and os.makedirs
        with patch("os.path.exists", return_value=True):
            with patch("os.path.isdir", return_value=True):
                with patch("os.makedirs"):
                    # Test the function
                    processed, skipped, failed = resave_images(input_dir, dest_dir)

                    # Verify results
                    assert processed == 2
                    assert failed == 1
                    assert skipped == 0

                    # Verify executor was called correctly
                    mock_executor.assert_called_once_with(max_workers=2)
                    assert mock_executor_instance.submit.call_count == 3


def test_resave_images_nonexistent_input_dir(tmp_path):
    """Test resaving with nonexistent input directory."""
    output_dir = str(tmp_path / "output")

    with pytest.raises(FileNotFoundError):
        resave_images(
            input_dir="nonexistent_dir",
            dest_dir=output_dir,
            output_format="png",
        )


def test_resave_images_invalid_output_format(sample_image_dir, tmp_path):
    """Test resaving with invalid output format."""
    output_dir = str(tmp_path / "output")

    with pytest.raises(ValueError):
        resave_images(
            input_dir=sample_image_dir,
            dest_dir=output_dir,
            output_format="invalid_format",
        )


def test_resave_images_empty_directory(tmp_path):
    """Test resaving with empty directory."""
    empty_dir = str(tmp_path / "empty")
    os.makedirs(empty_dir, exist_ok=True)

    output_dir = str(tmp_path / "output")

    processed, skipped, failed = resave_images(
        input_dir=empty_dir,
        dest_dir=output_dir,
        output_format="png",
    )

    assert processed == 0
    assert skipped == 0
    assert failed == 0


@patch("dataset_forge.actions.resave_images_actions.input")
def test_resave_images_workflow_cancelled(mock_input):
    """Test resave images workflow when cancelled."""
    with patch(
        "dataset_forge.utils.input_utils.get_folder_path"
    ) as mock_get_folder_path:
        mock_get_folder_path.return_value = None
        mock_input.return_value = "n"  # Cancel confirmation

        # Should not raise any exceptions
        resave_images_workflow()


@patch("dataset_forge.actions.resave_images_actions.resave_images")
@patch("dataset_forge.actions.resave_images_actions.input")
def test_resave_images_workflow_success(mock_input, mock_resave_images):
    """Test successful resave images workflow."""
    with patch(
        "dataset_forge.utils.input_utils.get_folder_path"
    ) as mock_get_folder_path:
        # Mock folder selection
        mock_get_folder_path.side_effect = ["/input/dir", "/output/dir"]

        # Mock format selection and options
        mock_input.side_effect = [
            "png",  # Format selection
            "n",  # No grayscale
            "n",  # No recursive
            "y",  # Confirm processing
            "y",  # Final confirmation
        ]

        # Mock resave_images
        mock_resave_images.return_value = (10, 0, 0)

        # Should complete successfully
        resave_images_workflow()

        # Verify resave_images was called
        mock_resave_images.assert_called_once_with(
            input_dir="/input/dir",
            dest_dir="/output/dir",
            output_format="png",
            grayscale=False,
            recursive=True,
            quality=95,
            lossless=False,
        )


def test_resave_images_workflow_with_predefined_parameters():
    """Test resave images workflow with predefined parameters."""
    with patch(
        "dataset_forge.actions.resave_images_actions.resave_images"
    ) as mock_resave:
        mock_resave.return_value = (5, 0, 0)

        with patch("dataset_forge.actions.resave_images_actions.input") as mock_input:
            mock_input.return_value = "1"  # Just need one input for format selection

            # Test with predefined parameters
            resave_images_workflow(
                input_dir="/test/input",
                dest_dir="/test/output",
                output_format="jpg",
                grayscale=True,
                recursive=True,
            )

            # Verify resave_images was called with correct parameters
            mock_resave.assert_called_once_with(
                input_dir="/test/input",
                dest_dir="/test/output",
                output_format="jpg",
                grayscale=True,
                recursive=True,
                quality=95,
                lossless=True,
            )


@patch("dataset_forge.actions.resave_images_actions.resave_images")
def test_resave_images_workflow_exception_handling(mock_resave_images):
    """Test resave images workflow exception handling."""
    # Mock resave_images to raise an exception
    mock_resave_images.side_effect = Exception("Test error")

    with patch("dataset_forge.actions.resave_images_actions.input") as mock_input:
        mock_input.side_effect = ["1", "n", "n", "y"]  # Standard options

        with patch(
            "dataset_forge.utils.input_utils.get_folder_path"
        ) as mock_get_folder:
            mock_get_folder.side_effect = ["/input/dir", "/output/dir"]

            # Should handle exception gracefully
            resave_images_workflow()


def test_process_single_image_unique_filename(tmp_path):
    """Test that process_single_image creates unique filenames."""
    # Create a test image
    image_path = tmp_path / "test.jpg"
    test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    cv2.imwrite(str(image_path), test_image)

    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir, exist_ok=True)

    # Create an existing file with the same name
    existing_file = os.path.join(output_dir, "test.png")
    with open(existing_file, "w") as f:
        f.write("existing file")

    # Process the image - should create a unique filename
    result = process_single_image(str(image_path), output_dir, "png", False)

    assert result is True

    # Check that a unique filename was created
    files = os.listdir(output_dir)
    png_files = [f for f in files if f.startswith("test") and f.endswith(".png")]
    assert len(png_files) == 2  # Original + new unique file
