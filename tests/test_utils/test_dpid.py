import pytest
import numpy as np
from PIL import Image
import os
from dataset_forge.dpid import basicsr_dpid, openmmlab_dpid, phhofm_dpid, umzi_dpid
from dataset_forge.actions.dpid_actions import dpid_menu


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


def test_run_umzi_dpid_single_folder(tmp_path, monkeypatch):
    """Test Umzi DPID single folder downscale creates output files (mock dpid_resize)."""
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()
    img = in_dir / "a.png"
    make_dummy_image(img)
    # Patch dpid_resize to just return the input image
    monkeypatch.setattr(umzi_dpid, "dpid_resize", lambda img, h, w, f: img)
    monkeypatch.setattr(umzi_dpid, "read", lambda path: np.array(Image.open(path)))
    monkeypatch.setattr(
        umzi_dpid, "save", lambda arr, path: Image.fromarray(arr).save(path)
    )
    umzi_dpid.run_umzi_dpid_single_folder(
        str(in_dir), str(out_dir), scales=[0.5], overwrite=True
    )
    out_subdir = out_dir / "50pct"
    assert (out_subdir / "a.png").exists()


def test_run_umzi_dpid_hq_lq(tmp_path, monkeypatch):
    """Test Umzi DPID HQ/LQ downscale creates output files (mock dpid_resize)."""
    hq_dir = tmp_path / "hq"
    lq_dir = tmp_path / "lq"
    out_hq = tmp_path / "out_hq"
    out_lq = tmp_path / "out_lq"
    hq_dir.mkdir()
    lq_dir.mkdir()
    out_hq.mkdir()
    out_lq.mkdir()
    img = hq_dir / "a.png"
    make_dummy_image(img)
    (lq_dir / "a.png").write_bytes(img.read_bytes())
    # Patch dpid_resize to just return the input image
    monkeypatch.setattr(umzi_dpid, "dpid_resize", lambda img, h, w, f: img)
    monkeypatch.setattr(umzi_dpid, "read", lambda path: np.array(Image.open(path)))
    monkeypatch.setattr(
        umzi_dpid, "save", lambda arr, path: Image.fromarray(arr).save(path)
    )
    umzi_dpid.run_umzi_dpid_hq_lq(
        str(hq_dir), str(lq_dir), str(out_hq), str(out_lq), scales=[0.5], overwrite=True
    )
    out_subdir_hq = out_hq / "50pct"
    out_subdir_lq = out_lq / "50pct"
    assert (out_subdir_hq / "a.png").exists()
    assert (out_subdir_lq / "a.png").exists()


def test_dpid_menu_integration():
    """Test that DPID menu can be imported and called."""
    assert dpid_menu is not None
    assert callable(dpid_menu)


def test_dpid_menu_imports():
    """Test that all DPID menu components can be imported."""
    from dataset_forge.actions.dpid_actions import (
        umzi_dpid_menu,
        phhofm_dpid_menu,
        basicsr_dpid_menu,
        openmmlab_dpid_menu,
        compare_dpid_methods,
    )
    
    # Test that all menus are callable
    assert callable(umzi_dpid_menu)
    assert callable(phhofm_dpid_menu)
    assert callable(basicsr_dpid_menu)
    assert callable(openmmlab_dpid_menu)
    assert callable(compare_dpid_methods)
