# OpenMMLab DPID implementation for Dataset-Forge
# Adapted from dpid_implementation_examples/OpenMMLab's_blur_kernels.py

import os
from tqdm import tqdm
import numpy as np
from PIL import Image
import cv2
import math

# Import alpha handling functions from umzi_dpid
from dataset_forge.dpid.umzi_dpid import read_with_alpha, save_with_alpha


def dpid_kernel_openmmlab(
    kernel_size, sigma, lambd, isotropic=True, sig_x=None, sig_y=None, theta=None
):
    # Generate a DPID Gaussian kernel (isotropic or anisotropic) using OpenMMLab logic
    range_ = np.arange(-kernel_size // 2 + 1.0, kernel_size // 2 + 1.0)
    x_grid, y_grid = np.meshgrid(range_, range_)
    grid = np.stack([x_grid, y_grid], axis=-1)
    if isotropic:
        sig_x = sig_y = sigma
        theta = 0.0
    else:
        sig_x = sig_x if sig_x is not None else sigma
        sig_y = sig_y if sig_y is not None else sigma
        theta = theta if theta is not None else 0.0
    diag = np.array([[sig_x**2, 0], [0, sig_y**2]], dtype=np.float32)
    rot = np.array(
        [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]],
        dtype=np.float32,
    )
    sigma_matrix = np.matmul(rot, np.matmul(diag, rot.T))
    inv_sigma = np.linalg.inv(sigma_matrix)
    kernel = np.exp(-0.5 * np.sum(np.matmul(grid, inv_sigma) * grid, 2))
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


def process_image_with_alpha_openmmlab(img, scale, kernel, has_alpha=False):
    """
    Process image with OpenMMLab DPID, handling alpha channels properly.
    
    Args:
        img: Input image (float32, range [0,1])
        scale: Scale factor
        kernel: DPID kernel
        has_alpha: Whether the image has alpha channel
        
    Returns:
        Processed image with same format as input
    """
    if has_alpha:
        # Separate RGB and alpha channels
        rgb = img[:, :, :3]
        alpha = img[:, :, 3]  # Convert to 2D array (H, W)
        
        # Process RGB channels with OpenMMLab DPID
        rgb_processed = dpid_downscale_img(rgb, scale, kernel)
        
        # Process alpha channel with OpenCV resize (more reliable for single channel)
        # Convert to uint8 for OpenCV, resize, then convert back to float32
        alpha_uint8 = (alpha * 255).astype(np.uint8)
        h, w = alpha_uint8.shape[:2]
        new_h = int(h * scale)
        new_w = int(w * scale)
        alpha_resized = cv2.resize(alpha_uint8, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        alpha_processed = alpha_resized.astype(np.float32) / 255.0
        
        # Add channel dimension back for concatenation
        alpha_processed_3d = alpha_processed[:, :, np.newaxis]
        
        # Combine RGB and alpha
        result = np.concatenate([rgb_processed, alpha_processed_3d], axis=2)
        return result
    else:
        # Process RGB image directly
        return dpid_downscale_img(img, scale, kernel)


def run_openmmlab_dpid_single_folder(
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
    """
    Downscale all images in a folder using OpenMMLab's DPID implementation.
    Now supports alpha channels properly.
    """
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
        kernel = dpid_kernel_openmmlab(
            kernel_size, sigma, lambd, isotropic, sig_x, sig_y, theta
        )
        for fname in tqdm(files, desc=f"OpenMMLab DPID {scale_pct} (single folder)"):
            in_path = os.path.join(input_folder, fname)
            out_path = os.path.join(output_folder, fname)
            if not overwrite and os.path.exists(out_path):
                continue
            
            # Read image with alpha support
            img, has_alpha = read_with_alpha(in_path)
            
            # Process image with alpha handling
            img_ds = process_image_with_alpha_openmmlab(img, scale, kernel, has_alpha)
            
            # Save with alpha support
            save_with_alpha(img_ds, out_path, has_alpha)


def run_openmmlab_dpid_hq_lq(
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
    """
    Downscale HQ/LQ paired images using OpenMMLab's DPID implementation.
    Now supports alpha channels properly.
    """
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
        kernel = dpid_kernel_openmmlab(
            kernel_size, sigma, lambd, isotropic, sig_x, sig_y, theta
        )
        for fname in tqdm(
            matching_files, desc=f"OpenMMLab DPID {scale_pct} (HQ/LQ pair)"
        ):
            in_hq = os.path.join(hq_folder, fname)
            in_lq = os.path.join(lq_folder, fname)
            out_hq = os.path.join(out_hq_folder, fname)
            out_lq = os.path.join(out_lq_folder, fname)
            if not overwrite and os.path.exists(out_hq) and os.path.exists(out_lq):
                continue
            
            # Read images with alpha support
            img_hq, has_alpha_hq = read_with_alpha(in_hq)
            img_lq, has_alpha_lq = read_with_alpha(in_lq)
            
            # Use the alpha status from HQ image (they should match)
            has_alpha = has_alpha_hq
            
            # Process images with alpha handling
            img_hq_ds = process_image_with_alpha_openmmlab(img_hq, scale, kernel, has_alpha)
            img_lq_ds = process_image_with_alpha_openmmlab(img_lq, scale, kernel, has_alpha)
            
            # Save with alpha support
            save_with_alpha(img_hq_ds, out_hq, has_alpha)
            save_with_alpha(img_lq_ds, out_lq, has_alpha)
