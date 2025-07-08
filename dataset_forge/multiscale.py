import os
from dataset_forge.io_utils import is_image_file
from dataset_forge.dpid_phhofm import (
    downscale_folder as dpid_phhofm_downscale_folder,
    downscale_hq_lq_pair as dpid_phhofm_downscale_hq_lq_pair,
)
from dataset_forge.operations import dpid_basicsr, dpid_openmmlab
from PIL import Image
import numpy as np
import shutil

DPID_METHODS = {
    "basicsr": "DPID (BasicSR)",
    "openmmlab": "DPID (OpenMMLab)",
    "phhofm": "DPID (Phhofm's pepedpid)",
}

SCALE_MAP = {"75%": 0.75, "50%": 0.5, "25%": 0.25}


# --- DPID Downscale for a single image using numpy (for basicsr/openmmlab) ---
def dpid_downscale_image(img_path, out_path, scale, method="basicsr", l=0.5):
    img = Image.open(img_path).convert("RGB")
    arr = np.asarray(img).astype(np.float32) / 255.0
    h, w = arr.shape[:2]
    new_h = int(h * scale)
    new_w = int(w * scale)
    if method == "basicsr":
        arr_lr = dpid_basicsr(arr, new_h, new_w, l)
    elif method == "openmmlab":
        arr_lr = dpid_openmmlab(arr, new_h, new_w, l)
    else:
        raise ValueError(f"Unknown DPID method: {method}")
    arr_lr = (arr_lr * 255.0).clip(0, 255).astype(np.uint8)
    img_lr = Image.fromarray(arr_lr)
    img_lr.save(out_path)


# --- DPID Downscale for a folder (single folder, basicsr/openmmlab) ---
def dpid_downscale_folder(input_folder, output_folder, scale, method="basicsr", l=0.5):
    os.makedirs(output_folder, exist_ok=True)
    for fname in os.listdir(input_folder):
        if not is_image_file(fname):
            continue
        in_path = os.path.join(input_folder, fname)
        out_path = os.path.join(output_folder, fname)
        dpid_downscale_image(in_path, out_path, scale, method, l)


# --- DPID Downscale for HQ/LQ paired folders (basicsr/openmmlab) ---
def dpid_downscale_hq_lq_pair(
    hq_folder, lq_folder, out_hq_folder, out_lq_folder, scale, method="basicsr", l=0.5
):
    os.makedirs(out_hq_folder, exist_ok=True)
    os.makedirs(out_lq_folder, exist_ok=True)
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    matching_files = sorted(hq_files & lq_files)
    for fname in matching_files:
        in_hq = os.path.join(hq_folder, fname)
        in_lq = os.path.join(lq_folder, fname)
        out_hq = os.path.join(out_hq_folder, fname)
        out_lq = os.path.join(out_lq_folder, fname)
        dpid_downscale_image(in_hq, out_hq, scale, method, l)
        dpid_downscale_image(in_lq, out_lq, scale, method, l)


# --- Main Multiscale Dataset API ---
def multiscale_downscale(
    input_path,
    output_base,
    scales=(0.75, 0.5, 0.25),
    dpid_method="basicsr",
    l=0.5,
    paired=False,
    lq_folder=None,
    verbose=True,
):
    results = {}
    if paired:
        hq_folder = input_path
        for scale in scales:
            scale_name = f"{int(scale*100)}pct"
            out_hq = os.path.join(output_base, f"hq_{scale_name}_{dpid_method}")
            out_lq = os.path.join(output_base, f"lq_{scale_name}_{dpid_method}")
            if dpid_method == "phhofm":
                processed, skipped, failed = dpid_phhofm_downscale_hq_lq_pair(
                    hq_folder,
                    lq_folder,
                    out_hq,
                    out_lq,
                    1 / scale,
                    output_ext=".png",
                    threads=4,
                    skip_existing=False,
                    verbose=verbose,
                )
            else:
                dpid_downscale_hq_lq_pair(
                    hq_folder, lq_folder, out_hq, out_lq, scale, method=dpid_method, l=l
                )
                processed = len([f for f in os.listdir(out_hq) if is_image_file(f)])
                skipped = failed = 0
            results[(scale, dpid_method)] = {
                "hq": out_hq,
                "lq": out_lq,
                "processed": processed,
                "skipped": skipped,
                "failed": failed,
            }
    else:
        for scale in scales:
            scale_name = f"{int(scale*100)}pct"
            out_folder = os.path.join(output_base, f"{scale_name}_{dpid_method}")
            if dpid_method == "phhofm":
                processed, skipped, failed = dpid_phhofm_downscale_folder(
                    input_path,
                    out_folder,
                    1 / scale,
                    output_ext=".png",
                    threads=4,
                    recursive=False,
                    skip_existing=False,
                    verbose=verbose,
                )
            else:
                dpid_downscale_folder(
                    input_path, out_folder, scale, method=dpid_method, l=l
                )
                processed = len([f for f in os.listdir(out_folder) if is_image_file(f)])
                skipped = failed = 0
            results[(scale, dpid_method)] = {
                "folder": out_folder,
                "processed": processed,
                "skipped": skipped,
                "failed": failed,
            }
    return results
