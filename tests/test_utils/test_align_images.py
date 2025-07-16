import os
import shutil
import tempfile
import numpy as np
import cv2
import pytest
from dataset_forge.actions.align_images_actions import align_images_workflow


def create_feature_rich_image(path, color=(0, 0, 255), size=(64, 64), text=None):
    arr = np.full((size[1], size[0], 3), color, dtype=np.uint8)
    # Draw a white rectangle
    cv2.rectangle(arr, (5, 5), (size[0] - 5, size[1] - 5), (255, 255, 255), 2)
    # Draw a black circle
    cv2.circle(arr, (size[0] // 2, size[1] // 2), 15, (0, 0, 0), 2)
    # Draw a diagonal line
    cv2.line(arr, (0, 0), (size[0] - 1, size[1] - 1), (0, 255, 0), 2)
    # Add text if provided
    if text:
        cv2.putText(
            arr, text, (8, size[1] // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1
        )
    cv2.imwrite(path, arr)


def make_flat_test_dirs(tmpdir):
    folder1 = os.path.join(tmpdir, "folder1")
    folder2 = os.path.join(tmpdir, "folder2")
    out = os.path.join(tmpdir, "output")
    os.makedirs(folder1)
    os.makedirs(folder2)
    os.makedirs(out)
    # Create matching and non-matching images with features
    create_feature_rich_image(
        os.path.join(folder1, "a.png"), color=(255, 0, 0), text="A1"
    )
    create_feature_rich_image(
        os.path.join(folder2, "a.png"), color=(0, 255, 0), text="A2"
    )
    create_feature_rich_image(
        os.path.join(folder1, "b.png"), color=(0, 0, 255), text="B1"
    )
    create_feature_rich_image(
        os.path.join(folder2, "b.png"), color=(0, 255, 255), text="B2"
    )
    create_feature_rich_image(
        os.path.join(folder1, "c.png"), color=(255, 255, 0), text="C1"
    )
    # Only in folder1
    create_feature_rich_image(
        os.path.join(folder1, "only1.png"), color=(128, 128, 128), text="O1"
    )
    # Only in folder2
    create_feature_rich_image(
        os.path.join(folder2, "only2.png"), color=(128, 0, 128), text="O2"
    )
    return folder1, folder2, out


def make_recursive_test_dirs(tmpdir):
    folder1 = os.path.join(tmpdir, "folder1")
    folder2 = os.path.join(tmpdir, "folder2")
    out = os.path.join(tmpdir, "output")
    os.makedirs(os.path.join(folder1, "sub"))
    os.makedirs(os.path.join(folder2, "sub"))
    os.makedirs(out)
    # Create matching images in subfolders with features
    create_feature_rich_image(
        os.path.join(folder1, "sub", "d.png"), color=(10, 20, 30), text="D1"
    )
    create_feature_rich_image(
        os.path.join(folder2, "sub", "d.png"), color=(30, 20, 10), text="D2"
    )
    # Create non-matching in subfolders
    create_feature_rich_image(
        os.path.join(folder1, "sub", "only1.png"), color=(1, 2, 3), text="S1"
    )
    create_feature_rich_image(
        os.path.join(folder2, "sub", "only2.png"), color=(4, 5, 6), text="S2"
    )
    return folder1, folder2, out


@pytest.mark.slow
@pytest.mark.parametrize("recursive", [False, True])
def test_align_images_workflow(tmp_path, recursive):
    if recursive:
        folder1, folder2, out = make_recursive_test_dirs(tmp_path)
    else:
        folder1, folder2, out = make_flat_test_dirs(tmp_path)
    # Monkeypatch get_folder_path to avoid user input
    import dataset_forge.actions.align_images_actions as aia

    aia.get_folder_path = lambda prompt: {
        "Select the first folder (images to align)": folder1,
        "Select the second folder (reference images)": folder2,
        "Select the output folder for aligned images": out,
    }[prompt]
    # Run workflow
    align_images_workflow(folder1, folder2, out, recursive=recursive, dry_run=False)
    # Check that output images exist for matching files
    if recursive:
        expected = [os.path.join(out, "sub", "d.png")]
    else:
        expected = [os.path.join(out, f) for f in ["a.png", "b.png"]]
    for path in expected:
        assert os.path.isfile(path), f"Output image missing: {path}"
    # Clean up
    shutil.rmtree(out, ignore_errors=True)
