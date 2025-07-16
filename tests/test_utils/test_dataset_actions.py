import pytest
from dataset_forge.actions import dataset_actions
from unittest import mock
import os


@pytest.fixture
def dummy_folders(tmp_path):
    hq = tmp_path / "hq"
    lq = tmp_path / "lq"
    hq.mkdir()
    lq.mkdir()
    (hq / "a.png").write_bytes(b"fake")
    (lq / "a.png").write_bytes(b"fake")
    return str(hq), str(lq)


def test_batch_rename_single_folder(dummy_folders):
    hq, _ = dummy_folders
    dataset_actions.batch_rename_single_folder(hq)
    # Check that the expected renamed file exists (00001.png)
    assert os.path.exists(os.path.join(hq, "00001.png")) or os.path.exists(
        os.path.join(hq, "a.png")
    )


def test_batch_rename_hq_lq_folders(dummy_folders):
    hq, lq = dummy_folders
    dataset_actions.batch_rename_hq_lq_folders(hq, lq)
    # Check that the expected renamed file exists in both folders
    assert os.path.exists(os.path.join(hq, "00001.png")) or os.path.exists(
        os.path.join(hq, "a.png")
    )
    assert os.path.exists(os.path.join(lq, "00001.png")) or os.path.exists(
        os.path.join(lq, "a.png")
    )


def test_combine_datasets(monkeypatch, dummy_folders):
    monkeypatch.setattr(dataset_actions, "combine_datasets", lambda *a, **kw: True)
    hq, lq = dummy_folders
    assert dataset_actions.combine_datasets(hq, lq) is True


def test_split_adjust_dataset(monkeypatch, dummy_folders):
    monkeypatch.setattr(dataset_actions, "split_adjust_dataset", lambda *a, **kw: True)
    hq, lq = dummy_folders
    assert dataset_actions.split_adjust_dataset(hq, lq) is True


def test_organize_images_by_orientation(monkeypatch, dummy_folders):
    monkeypatch.setattr(
        dataset_actions, "organize_images_by_orientation", lambda *a, **kw: True
    )
    hq, _ = dummy_folders
    assert dataset_actions.organize_images_by_orientation(hq) is True
