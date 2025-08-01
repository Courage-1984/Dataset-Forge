# Phhofm DPID implementation for Dataset-Forge
# Adapted from dpid_implementation_examples/Phhofm's_dpid_downscaler.py

import os
from tqdm import tqdm
from PIL import Image
import numpy as np
import cv2

# Use local read/save from tiling.py
from dataset_forge.actions.tiling_actions import read, save

try:
    from pepedpid import dpid_resize
except ImportError:
    dpid_resize = None


def run_phhofm_dpid_single_folder(
    input_folder, output_base, scales, overwrite=False, lambd=1.0
):
    if dpid_resize is None:
        raise ImportError(
            "pepedpid is required for Phhofm DPID. Please install it: pip install pepedpid"
        )
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
        for fname in tqdm(files, desc=f"Phhofm DPID {scale_pct} (single folder)"):
            in_path = os.path.join(input_folder, fname)
            out_path = os.path.join(output_folder, fname)
            if not overwrite and os.path.exists(out_path):
                continue
            img = read(in_path)
            h, w = img.shape[:2]
            # Phhofm DPID expects scale as an integer factor (e.g., 4 for 0.25)
            scale_factor = 1.0 / scale
            target_h = max(1, int(round(h * scale)))
            target_w = max(1, int(round(w * scale)))
            # DPID factor: (scale_factor - 1) / scale_factor, but allow user override
            factor = lambd if lambd is not None else (scale_factor - 1) / scale_factor
            img_ds = dpid_resize(img, target_h, target_w, factor)
            save(img_ds, out_path)


def run_phhofm_dpid_hq_lq(
    hq_folder, lq_folder, out_hq_base, out_lq_base, scales, overwrite=False, lambd=1.0
):
    if dpid_resize is None:
        raise ImportError(
            "pepedpid is required for Phhofm DPID. Please install it: pip install pepedpid"
        )
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
        for fname in tqdm(matching_files, desc=f"Phhofm DPID {scale_pct} (HQ/LQ pair)"):
            in_hq = os.path.join(hq_folder, fname)
            in_lq = os.path.join(lq_folder, fname)
            out_hq = os.path.join(out_hq_folder, fname)
            out_lq = os.path.join(out_lq_folder, fname)
            if not overwrite and os.path.exists(out_hq) and os.path.exists(out_lq):
                continue
            img_hq = read(in_hq)
            img_lq = read(in_lq)
            h, w = img_hq.shape[:2]
            scale_factor = 1.0 / scale
            target_h = max(1, int(round(h * scale)))
            target_w = max(1, int(round(w * scale)))
            factor = lambd if lambd is not None else (scale_factor - 1) / scale_factor
            img_hq_ds = dpid_resize(img_hq, target_h, target_w, factor)
            img_lq_ds = dpid_resize(img_lq, target_h, target_w, factor)
            save(img_hq_ds, out_hq)
            save(img_lq_ds, out_lq)
