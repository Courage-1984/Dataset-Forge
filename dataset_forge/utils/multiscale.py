import os
from dataset_forge.utils.file_utils import is_image_file
from PIL import Image
import numpy as np
import shutil

# Import new DPID modules
from dataset_forge.dpid.basicsr_dpid import (
    run_basicsr_dpid_single_folder,
    run_basicsr_dpid_hq_lq,
)
from dataset_forge.dpid.openmmlab_dpid import (
    run_openmmlab_dpid_single_folder,
    run_openmmlab_dpid_hq_lq,
)
from dataset_forge.dpid.phhofm_dpid import (
    run_phhofm_dpid_single_folder,
    run_phhofm_dpid_hq_lq,
)
from dataset_forge.dpid.umzi_dpid import (
    run_umzi_dpid_single_folder,
    run_umzi_dpid_hq_lq,
)

DPID_METHODS = {
    "basicsr": "DPID (BasicSR)",
    "openmmlab": "DPID (OpenMMLab)",
    "phhofm": "DPID (Phhofm's pepedpid)",
    "umzi": "DPID (Umzi's pepedpid)",
}

SCALE_MAP = {"75%": 0.75, "50%": 0.5, "25%": 0.25}


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
    **kwargs,
):
    results = {}
    if paired:
        hq_folder = input_path
        for scale in scales:
            scale_name = f"{int(scale*100)}pct"
            out_hq = os.path.join(output_base, f"hq_{scale_name}_{dpid_method}")
            out_lq = os.path.join(output_base, f"lq_{scale_name}_{dpid_method}")
            if dpid_method == "phhofm":
                run_phhofm_dpid_hq_lq(
                    hq_folder,
                    lq_folder,
                    out_hq,
                    out_lq,
                    [scale],
                    overwrite=False,
                    lambd=l,
                )
                processed = len([f for f in os.listdir(out_hq) if is_image_file(f)])
                skipped = failed = 0
            elif dpid_method == "basicsr":
                run_basicsr_dpid_hq_lq(
                    hq_folder,
                    lq_folder,
                    out_hq,
                    out_lq,
                    [scale],
                    overwrite=False,
                    lambd=l,
                )
                processed = len([f for f in os.listdir(out_hq) if is_image_file(f)])
                skipped = failed = 0
            elif dpid_method == "openmmlab":
                run_openmmlab_dpid_hq_lq(
                    hq_folder,
                    lq_folder,
                    out_hq,
                    out_lq,
                    [scale],
                    overwrite=False,
                    lambd=l,
                )
                processed = len([f for f in os.listdir(out_hq) if is_image_file(f)])
                skipped = failed = 0
            elif dpid_method == "umzi":
                run_umzi_dpid_hq_lq(
                    hq_folder,
                    lq_folder,
                    out_hq,
                    out_lq,
                    [scale],
                    overwrite=False,
                    lambd=l,
                )
                processed = len([f for f in os.listdir(out_hq) if is_image_file(f)])
                skipped = failed = 0
            else:
                raise ValueError(f"Unknown DPID method: {dpid_method}")
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
                run_phhofm_dpid_single_folder(
                    input_path, output_base, [scale], overwrite=False, lambd=l
                )
                processed = len([f for f in os.listdir(out_folder) if is_image_file(f)])
                skipped = failed = 0
            elif dpid_method == "basicsr":
                run_basicsr_dpid_single_folder(
                    input_path, output_base, [scale], overwrite=False, lambd=l
                )
                processed = len([f for f in os.listdir(out_folder) if is_image_file(f)])
                skipped = failed = 0
            elif dpid_method == "openmmlab":
                run_openmmlab_dpid_single_folder(
                    input_path, output_base, [scale], overwrite=False, lambd=l
                )
                processed = len([f for f in os.listdir(out_folder) if is_image_file(f)])
                skipped = failed = 0
            elif dpid_method == "umzi":
                run_umzi_dpid_single_folder(
                    input_path, output_base, [scale], overwrite=False, lambd=l
                )
                processed = len([f for f in os.listdir(out_folder) if is_image_file(f)])
                skipped = failed = 0
            else:
                raise ValueError(f"Unknown DPID method: {dpid_method}")
            results[(scale, dpid_method)] = {
                "folder": out_folder,
                "processed": processed,
                "skipped": skipped,
                "failed": failed,
            }
    return results
