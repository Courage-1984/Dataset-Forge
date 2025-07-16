# BasicSR DPID implementation for Dataset-Forge
# Adapted from dpid_implementation_examples/BasicSR's_degradations.py

import os
from tqdm import tqdm
import numpy as np
from PIL import Image
import cv2
import math


def dpid_kernel_basicsr(
    kernel_size, sigma, lambd, isotropic=True, sig_x=None, sig_y=None, theta=None
):
    # Generate a DPID Gaussian kernel (isotropic or anisotropic)
    ax = np.arange(-kernel_size // 2 + 1.0, kernel_size // 2 + 1.0)
    xx, yy = np.meshgrid(ax, ax)
    if isotropic:
        sig_x = sig_y = sigma
        theta = 0.0
    else:
        sig_x = sig_x if sig_x is not None else sigma
        sig_y = sig_y if sig_y is not None else sigma
        theta = theta if theta is not None else 0.0
    d_matrix = np.array([[sig_x**2, 0], [0, sig_y**2]])
    u_matrix = np.array(
        [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
    )
    sigma_matrix = np.dot(u_matrix, np.dot(d_matrix, u_matrix.T))
    inv_sigma = np.linalg.inv(sigma_matrix)
    grid = np.stack([xx, yy], axis=-1)
    kernel = np.exp(-0.5 * np.sum(np.dot(grid, inv_sigma) * grid, axis=2))
    kernel = kernel / np.sum(kernel)
    # DPID: blend with identity kernel using lambda
    identity = np.zeros_like(kernel)
    identity[kernel_size // 2, kernel_size // 2] = 1.0
    kernel = (1 - lambd) * kernel + lambd * identity
    kernel = kernel / np.sum(kernel)
    return kernel.astype(np.float32)


def dpid_downscale_img(img, scale, kernel, border_type=cv2.BORDER_REFLECT):
    # img: float32, [0,1], shape HxWxC
    # kernel: float32, shape kxk
    # 1. Convolve
    if img.ndim == 2:
        img_filt = cv2.filter2D(img, -1, kernel, borderType=border_type)
    else:
        img_filt = np.stack(
            [
                cv2.filter2D(img[..., c], -1, kernel, borderType=border_type)
                for c in range(img.shape[2])
            ],
            axis=2,
        )
    # 2. Downsample
    h, w = img_filt.shape[:2]
    new_h = int(h * scale)
    new_w = int(w * scale)
    img_ds = cv2.resize(img_filt, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    return img_ds


def run_basicsr_dpid_single_folder(
    input_folder,
    output_base,
    scales,
    overwrite=False,
    kernel_size=21,
    sigma=2.0,
    lambd=0.5,
    isotropic=True,
    sig_x=None,
    sig_y=None,
    theta=None,
):
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
        kernel = dpid_kernel_basicsr(
            kernel_size, sigma, lambd, isotropic, sig_x, sig_y, theta
        )
        for fname in tqdm(files, desc=f"BasicSR DPID {scale_pct} (single folder)"):
            in_path = os.path.join(input_folder, fname)
            out_path = os.path.join(output_folder, fname)
            if not overwrite and os.path.exists(out_path):
                continue
            img = np.array(Image.open(in_path).convert("RGB"), dtype=np.float32) / 255.0
            img_ds = dpid_downscale_img(img, scale, kernel)
            img_ds = (img_ds * 255.0).clip(0, 255).astype(np.uint8)
            Image.fromarray(img_ds).save(out_path)


def run_basicsr_dpid_hq_lq(
    hq_folder,
    lq_folder,
    out_hq_base,
    out_lq_base,
    scales,
    overwrite=False,
    kernel_size=21,
    sigma=2.0,
    lambd=0.5,
    isotropic=True,
    sig_x=None,
    sig_y=None,
    theta=None,
):
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
        kernel = dpid_kernel_basicsr(
            kernel_size, sigma, lambd, isotropic, sig_x, sig_y, theta
        )
        for fname in tqdm(
            matching_files, desc=f"BasicSR DPID {scale_pct} (HQ/LQ pair)"
        ):
            in_hq = os.path.join(hq_folder, fname)
            in_lq = os.path.join(lq_folder, fname)
            out_hq = os.path.join(out_hq_folder, fname)
            out_lq = os.path.join(out_lq_folder, fname)
            if not overwrite and os.path.exists(out_hq) and os.path.exists(out_lq):
                continue
            img_hq = (
                np.array(Image.open(in_hq).convert("RGB"), dtype=np.float32) / 255.0
            )
            img_lq = (
                np.array(Image.open(in_lq).convert("RGB"), dtype=np.float32) / 255.0
            )
            img_hq_ds = dpid_downscale_img(img_hq, scale, kernel)
            img_lq_ds = dpid_downscale_img(img_lq, scale, kernel)
            img_hq_ds = (img_hq_ds * 255.0).clip(0, 255).astype(np.uint8)
            img_lq_ds = (img_lq_ds * 255.0).clip(0, 255).astype(np.uint8)
            Image.fromarray(img_hq_ds).save(out_hq)
            Image.fromarray(img_lq_ds).save(out_lq)
