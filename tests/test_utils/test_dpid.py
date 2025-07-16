import pytest
import numpy as np
from PIL import Image
import os
from dataset_forge.dpid import basicsr_dpid, openmmlab_dpid, phhofm_dpid


def make_dummy_image(path, size=(8, 8)):
    arr = np.random.randint(0, 255, size + (3,), dtype=np.uint8)
    Image.fromarray(arr).save(path)


def test_run_basicsr_dpid_single_folder(tmp_path):
    """Test basicsr DPID single folder downscale creates output files."""
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()
    img = in_dir / "a.png"
    make_dummy_image(img)
    basicsr_dpid.run_basicsr_dpid_single_folder(
        str(in_dir), str(out_dir), scales=[0.5], overwrite=True
    )
    out_subdir = out_dir / "50pct"
    assert (out_subdir / "a.png").exists()


def test_run_openmmlab_dpid_single_folder(tmp_path):
    """Test openmmlab DPID single folder downscale creates output files."""
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()
    img = in_dir / "a.png"
    make_dummy_image(img)
    openmmlab_dpid.run_openmmlab_dpid_single_folder(
        str(in_dir), str(out_dir), scales=[0.5], overwrite=True
    )
    out_subdir = out_dir / "50pct"
    assert (out_subdir / "a.png").exists()


def test_run_phhofm_dpid_single_folder(tmp_path, monkeypatch):
    """Test phhofm DPID single folder downscale creates output files (mock dpid_resize)."""
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()
    img = in_dir / "a.png"
    make_dummy_image(img)
    # Patch dpid_resize to just return the input image
    monkeypatch.setattr(phhofm_dpid, "dpid_resize", lambda img, h, w, f: img)
    monkeypatch.setattr(phhofm_dpid, "read", lambda path: np.array(Image.open(path)))
    monkeypatch.setattr(
        phhofm_dpid, "save", lambda arr, path: Image.fromarray(arr).save(path)
    )
    phhofm_dpid.run_phhofm_dpid_single_folder(
        str(in_dir), str(out_dir), scales=[0.5], overwrite=True
    )
    out_subdir = out_dir / "50pct"
    assert (out_subdir / "a.png").exists()
