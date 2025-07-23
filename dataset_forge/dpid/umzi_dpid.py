# Umzi DPID implementation for Dataset Forge
# Wraps pepedpid.dpid_resize as described in store/umzi_dpid.md

import os
from tqdm import tqdm
from dataset_forge.actions.tiling_actions import read, save

try:
    from pepedpid import dpid_resize
except ImportError:
    dpid_resize = None


def run_umzi_dpid_single_folder(
    input_folder: str,
    output_base: str,
    scales,
    overwrite: bool = False,
    lambd: float = 0.5,
):
    """
    Downscale all images in a folder using Umzi's DPID (pepedpid) implementation.

    Args:
        input_folder: Path to input images folder.
        output_base: Path to output base folder (subfolders for each scale).
        scales: List of scale factors (e.g., [0.75, 0.5, 0.25]).
        overwrite: If True, overwrite existing files.
        lambd: DPID lambda (0=smooth, 1=detail, recommended 0.5).

    Raises:
        ImportError: If pepedpid is not installed.
        FileNotFoundError: If input_folder does not exist.
    """
    if dpid_resize is None:
        raise ImportError(
            "pepedpid is required for Umzi DPID. Please install it: pip install pepedpid"
        )
    if not os.path.isdir(input_folder):
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if isinstance(scales, float):
        scales = [scales]
    files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")
        )
    ]
    for scale in scales:
        scale_pct = f"{int(scale*100)}pct"
        output_folder = os.path.join(output_base, scale_pct)
        os.makedirs(output_folder, exist_ok=True)
        for fname in tqdm(files, desc=f"Umzi DPID {scale_pct} (single folder)"):
            in_path = os.path.join(input_folder, fname)
            out_path = os.path.join(output_folder, fname)
            if not overwrite and os.path.exists(out_path):
                continue
            img = read(in_path)
            h, w = img.shape[:2]
            target_h = max(1, int(round(h * scale)))
            target_w = max(1, int(round(w * scale)))
            img_ds = dpid_resize(img, target_h, target_w, lambd)
            save(img_ds, out_path)


def run_umzi_dpid_hq_lq(
    hq_folder: str,
    lq_folder: str,
    out_hq_base: str,
    out_lq_base: str,
    scales,
    overwrite: bool = False,
    lambd: float = 0.5,
):
    """
    Downscale HQ/LQ paired images using Umzi's DPID (pepedpid) implementation.

    Args:
        hq_folder: Path to HQ images folder.
        lq_folder: Path to LQ images folder.
        out_hq_base: Output base folder for HQ images.
        out_lq_base: Output base folder for LQ images.
        scales: List of scale factors (e.g., [0.75, 0.5, 0.25]).
        overwrite: If True, overwrite existing files.
        lambd: DPID lambda (0=smooth, 1=detail, recommended 0.5).

    Raises:
        ImportError: If pepedpid is not installed.
        FileNotFoundError: If input folders do not exist.
    """
    if dpid_resize is None:
        raise ImportError(
            "pepedpid is required for Umzi DPID. Please install it: pip install pepedpid"
        )
    if not os.path.isdir(hq_folder):
        raise FileNotFoundError(f"HQ folder does not exist: {hq_folder}")
    if not os.path.isdir(lq_folder):
        raise FileNotFoundError(f"LQ folder does not exist: {lq_folder}")
    if isinstance(scales, float):
        scales = [scales]
    hq_files = {
        f
        for f in os.listdir(hq_folder)
        if f.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")
        )
    }
    lq_files = {
        f
        for f in os.listdir(lq_folder)
        if f.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")
        )
    }
    matching_files = sorted(hq_files & lq_files)
    for scale in scales:
        scale_pct = f"{int(scale*100)}pct"
        out_hq_folder = os.path.join(out_hq_base, scale_pct)
        out_lq_folder = os.path.join(out_lq_base, scale_pct)
        os.makedirs(out_hq_folder, exist_ok=True)
        os.makedirs(out_lq_folder, exist_ok=True)
        for fname in tqdm(matching_files, desc=f"Umzi DPID {scale_pct} (HQ/LQ pair)"):
            in_hq = os.path.join(hq_folder, fname)
            in_lq = os.path.join(lq_folder, fname)
            out_hq = os.path.join(out_hq_folder, fname)
            out_lq = os.path.join(out_lq_folder, fname)
            if not overwrite and os.path.exists(out_hq) and os.path.exists(out_lq):
                continue
            img_hq = read(in_hq)
            img_lq = read(in_lq)
            h, w = img_hq.shape[:2]
            target_h = max(1, int(round(h * scale)))
            target_w = max(1, int(round(w * scale)))
            img_hq_ds = dpid_resize(img_hq, target_h, target_w, lambd)
            img_lq_ds = dpid_resize(img_lq, target_h, target_w, lambd)
            save(img_hq_ds, out_hq)
            save(img_lq_ds, out_lq)
