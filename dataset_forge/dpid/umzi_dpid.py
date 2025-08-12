# Umzi DPID implementation for Dataset Forge
# Wraps pepedpid.dpid_resize as described in store/umzi_dpid.md

import os
import cv2
import numpy as np
from tqdm import tqdm
from dataset_forge.actions.tiling_actions import read, save

try:
    from pepedpid import dpid_resize
except ImportError:
    dpid_resize = None


def read_with_alpha(path):
    """
    Read image with alpha channel support.
    
    Args:
        path: Path to the image file
        
    Returns:
        tuple: (image_array, has_alpha) where image_array is RGB or RGBA
    """
    # Read with alpha channel if present
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    
    # Check if image has alpha channel
    has_alpha = img.shape[-1] == 4 if len(img.shape) == 3 else False
    
    if has_alpha:
        # Convert BGR to RGB and preserve alpha
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    else:
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Convert to float32 and normalize
    if img.dtype == np.uint8:
        img = img.astype(np.float32) / 255.0
    
    return img, has_alpha


def save_with_alpha(img, path, has_alpha=False):
    """
    Save image with alpha channel support.
    
    Args:
        img: Image array (float32, range [0,1])
        path: Output path
        has_alpha: Whether the image has alpha channel
    """
    # Convert to uint8
    if img.dtype == np.float32:
        img = (img * 255).astype(np.uint8)
    
    if has_alpha:
        # Convert RGBA to BGRA for OpenCV
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
    else:
        # Convert RGB to BGR for OpenCV
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    cv2.imwrite(path, img)


def process_image_with_alpha(img, target_h, target_w, lambd, has_alpha=False):
    """
    Process image with DPID, handling alpha channels properly.
    
    Args:
        img: Input image (float32, range [0,1])
        target_h: Target height
        target_w: Target width
        lambd: DPID lambda parameter
        has_alpha: Whether the image has alpha channel
        
    Returns:
        Processed image with same format as input
    """
    if has_alpha:
        # Separate RGB and alpha channels
        rgb = img[:, :, :3]
        alpha = img[:, :, 3]  # Convert to 2D array (H, W)
        
        # Process RGB channels with DPID
        rgb_processed = dpid_resize(rgb, target_h, target_w, lambd)
        
        # Process alpha channel with OpenCV resize (more reliable than dpid_resize for single channel)
        # Convert to uint8 for OpenCV, resize, then convert back to float32
        alpha_uint8 = (alpha * 255).astype(np.uint8)
        alpha_resized = cv2.resize(alpha_uint8, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
        alpha_processed = alpha_resized.astype(np.float32) / 255.0
        
        # Add channel dimension back for concatenation
        alpha_processed_3d = alpha_processed[:, :, np.newaxis]
        
        # Combine RGB and alpha
        result = np.concatenate([rgb_processed, alpha_processed_3d], axis=2)
        return result
    else:
        # Process RGB image directly
        return dpid_resize(img, target_h, target_w, lambd)


def run_umzi_dpid_single_folder(
    input_folder: str,
    output_base: str,
    scales,
    overwrite: bool = False,
    lambd: float = 0.5,
):
    """
    Downscale all images in a folder using Umzi's DPID (pepedpid) implementation.
    Now supports alpha channels properly.

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
            
            # Read image with alpha support
            img, has_alpha = read_with_alpha(in_path)
            h, w = img.shape[:2]
            target_h = max(1, int(round(h * scale)))
            target_w = max(1, int(round(w * scale)))
            
            # Process image with alpha handling
            img_ds = process_image_with_alpha(img, target_h, target_w, lambd, has_alpha)
            
            # Save with alpha support
            save_with_alpha(img_ds, out_path, has_alpha)


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
    Now supports alpha channels properly.

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
            
            # Read images with alpha support
            img_hq, has_alpha_hq = read_with_alpha(in_hq)
            img_lq, has_alpha_lq = read_with_alpha(in_lq)
            
            # Use the alpha status from HQ image (they should match)
            has_alpha = has_alpha_hq
            
            h, w = img_hq.shape[:2]
            target_h = max(1, int(round(h * scale)))
            target_w = max(1, int(round(w * scale)))
            
            # Process images with alpha handling
            img_hq_ds = process_image_with_alpha(img_hq, target_h, target_w, lambd, has_alpha)
            img_lq_ds = process_image_with_alpha(img_lq, target_h, target_w, lambd, has_alpha)
            
            # Save with alpha support
            save_with_alpha(img_hq_ds, out_hq, has_alpha)
            save_with_alpha(img_lq_ds, out_lq, has_alpha)
