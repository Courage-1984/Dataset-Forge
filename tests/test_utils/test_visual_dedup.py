import pytest
from dataset_forge.actions import visual_dedup_actions
import os


@pytest.fixture
def dummy_images(tmp_path):
    img1 = tmp_path / "a.png"
    img2 = tmp_path / "b.png"
    img1.write_bytes(b"fake")
    img2.write_bytes(b"fake")
    return [str(img1), str(img2)]


def test_find_duplicate_groups(monkeypatch, tmp_path):
    # Patch load_images_from_folder to return two identical dummy images
    dummy_img_path = tmp_path / "a.png"
    dummy_img_path.write_bytes(b"fake")
    from PIL import Image

    dummy_img = Image.new("RGB", (10, 10))
    monkeypatch.setattr(
        visual_dedup_actions,
        "load_images_from_folder",
        lambda folder, max_images=None: [
            (str(dummy_img_path), dummy_img),
            (str(dummy_img_path), dummy_img),
        ],
    )
    # Patch find_near_duplicates_clip to always return a single group
    monkeypatch.setattr(
        visual_dedup_actions,
        "find_near_duplicates_clip",
        lambda images, threshold, device: [[str(dummy_img_path), str(dummy_img_path)]],
    )
    groups = visual_dedup_actions.find_duplicate_groups(str(tmp_path), method="clip")
    assert isinstance(groups, list)
    assert len(groups) == 1
    assert all(isinstance(g, list) for g in groups)


def test_move_duplicate_groups(monkeypatch, dummy_images, tmp_path):
    # Patch shutil.move to avoid real file operations
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr("shutil.move", lambda src, dst: None)
    groups = [dummy_images]
    moved = visual_dedup_actions.move_duplicate_groups(
        groups, str(tmp_path), dry_run=False
    )
    assert isinstance(moved, list)
    assert set(moved) == set(dummy_images[1:])


def test_copy_duplicate_groups(monkeypatch, dummy_images, tmp_path):
    # Patch shutil.copy2 to avoid real file operations
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr("shutil.copy2", lambda src, dst: None)
    groups = [dummy_images]
    copied = visual_dedup_actions.copy_duplicate_groups(
        groups, str(tmp_path), dry_run=False
    )
    assert isinstance(copied, list)
    assert set(copied) == set(dummy_images[1:])


def test_remove_duplicate_groups(monkeypatch, dummy_images):
    # Patch os.remove to avoid real file operations
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr(os, "remove", lambda path: None)
    groups = [dummy_images]
    removed = visual_dedup_actions.remove_duplicate_groups(groups, dry_run=False)
    assert isinstance(removed, list)
    assert set(removed) == set(dummy_images[1:])
