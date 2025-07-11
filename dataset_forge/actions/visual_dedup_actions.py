import os
import shutil
from typing import List, Optional, Tuple, Dict
from PIL import Image
import torch
import numpy as np
from tqdm import tqdm

from dataset_forge.utils.printing import (
    print_info,
    print_error,
    print_success,
    print_warning,
)

try:
    import lpips
except ImportError:
    lpips = None
try:
    import open_clip
except ImportError:
    open_clip = None


def load_images_from_folder(
    folder: str, max_images: Optional[int] = None
) -> List[Tuple[str, Image.Image]]:
    images = []
    supported_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    for root, _, files in os.walk(folder):
        for fname in files:
            if os.path.splitext(fname)[1].lower() in supported_exts:
                path = os.path.join(root, fname)
                try:
                    img = Image.open(path).convert("RGB")
                    images.append((path, img))
                    if max_images and len(images) >= max_images:
                        return images
                except Exception:
                    continue
    return images


def get_lpips_model(device: str = "cuda" if torch.cuda.is_available() else "cpu"):
    if lpips is None:
        raise ImportError("lpips is not installed. Please install it via pip.")
    return lpips.LPIPS(net="vgg").to(device)


def compute_lpips_matrix(
    images: List[Tuple[str, Image.Image]],
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> np.ndarray:
    model = get_lpips_model(device)
    n = len(images)
    matrix = np.zeros((n, n), dtype=np.float32)
    imgs_tensor = [
        torch.from_numpy(np.array(img[1]).transpose(2, 0, 1)).float() / 127.5 - 1
        for img in images
    ]
    imgs_tensor = [img.unsqueeze(0).to(device) for img in imgs_tensor]
    for i in tqdm(range(n), desc="LPIPS (perceptual) similarity"):
        for j in range(i + 1, n):
            dist = model(imgs_tensor[i], imgs_tensor[j]).item()
            matrix[i, j] = matrix[j, i] = dist
    return matrix


def get_clip_model(device: str = "cuda" if torch.cuda.is_available() else "cpu"):
    if open_clip is None:
        raise ImportError(
            "open-clip-torch is not installed. Please install it via pip."
        )
    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="laion2b_s34b_b79k"
    )
    model = model.to(device)
    return model, preprocess


def compute_clip_embeddings(
    images: List[Tuple[str, Image.Image]],
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> np.ndarray:
    model, preprocess = get_clip_model(device)
    model.eval()
    with torch.no_grad():
        embs = []
        for _, img in tqdm(images, desc="CLIP embedding"):
            emb = model.encode_image(preprocess(img).unsqueeze(0).to(device))
            emb = emb.cpu().numpy().flatten()
            embs.append(emb)
    return np.stack(embs)


def compute_clip_similarity_matrix(embs: np.ndarray) -> np.ndarray:
    # Cosine similarity
    norm_embs = embs / np.linalg.norm(embs, axis=1, keepdims=True)
    sim_matrix = np.dot(norm_embs, norm_embs.T)
    return sim_matrix


def find_near_duplicates_lpips(
    images: List[Tuple[str, Image.Image]],
    threshold: float = 0.2,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> List[List[str]]:
    matrix = compute_lpips_matrix(images, device)
    n = len(images)
    groups = []
    visited = set()
    for i in range(n):
        if i in visited:
            continue
        group = [images[i][0]]
        for j in range(n):
            if i != j and matrix[i, j] < threshold:
                group.append(images[j][0])
                visited.add(j)
        if len(group) > 1:
            groups.append(group)
        visited.add(i)
    return groups


def find_near_duplicates_clip(
    images: List[Tuple[str, Image.Image]],
    threshold: float = 0.98,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> List[List[str]]:
    embs = compute_clip_embeddings(images, device)
    sim_matrix = compute_clip_similarity_matrix(embs)
    n = len(images)
    groups = []
    visited = set()
    for i in range(n):
        if i in visited:
            continue
        group = [images[i][0]]
        for j in range(n):
            if i != j and sim_matrix[i, j] > threshold:
                group.append(images[j][0])
                visited.add(j)
        if len(group) > 1:
            groups.append(group)
        visited.add(i)
    return groups


def visual_dedup_workflow(
    hq_path: Optional[str] = None,
    lq_path: Optional[str] = None,
    single_folder_path: Optional[str] = None,
    method: str = "clip",
    threshold: Optional[float] = None,
    max_images: Optional[int] = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> Dict[str, List[List[str]]]:
    """
    Main entry point for visual deduplication. Returns a dict with method as key and groups as value.
    """
    if method == "lpips":
        threshold = threshold or 0.2
    else:
        threshold = threshold or 0.98
    results = {}
    if single_folder_path:
        images = load_images_from_folder(single_folder_path, max_images)
        if method == "lpips":
            groups = find_near_duplicates_lpips(images, threshold, device)
        else:
            groups = find_near_duplicates_clip(images, threshold, device)
        results[single_folder_path] = groups
    elif hq_path and lq_path:
        for path in [hq_path, lq_path]:
            images = load_images_from_folder(path, max_images)
            if method == "lpips":
                groups = find_near_duplicates_lpips(images, threshold, device)
            else:
                groups = find_near_duplicates_clip(images, threshold, device)
            results[path] = groups
    return results


def move_duplicate_groups(
    groups: List[List[str]], 
    destination_dir: str, 
    dry_run: bool = True
) -> List[str]:
    """
    Move duplicate files from groups to destination directory.
    
    Args:
        groups: List of duplicate groups (each group is a list of file paths)
        destination_dir: Directory to move duplicates to
        dry_run: If True, only show what would be moved
        
    Returns:
        List of moved file paths
    """
    if not groups:
        print_info("No duplicate groups to process.")
        return []
    
    # Flatten all duplicate files (keep first file in each group as original)
    files_to_move = []
    for group in groups:
        # Skip the first file (original), move the rest (duplicates)
        duplicates = group[1:]
        files_to_move.extend(duplicates)
    
    if not files_to_move:
        print_info("No duplicate files to move.")
        return []
    
    print_info(f"Found {len(files_to_move)} duplicate files to move.")
    
    if dry_run:
        print_warning("DRY RUN - No files will be moved. Set dry_run=False to actually move files.")
        for file_path in files_to_move:
            print_info(f"Would move: {file_path} -> {destination_dir}")
        return files_to_move
    
    # Create destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)
    
    moved_files = []
    for file_path in tqdm(files_to_move, desc="Moving duplicates"):
        try:
            # Check if file exists before trying to move it
            if not os.path.exists(file_path):
                print_warning(f"File not found (may have been moved already): {file_path}")
                continue
                
            filename = os.path.basename(file_path)
            dest_path = os.path.join(destination_dir, filename)
            
            # Handle filename conflicts
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(destination_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            shutil.move(file_path, dest_path)
            moved_files.append(file_path)
        except Exception as e:
            print_error(f"Error moving {file_path}: {e}")
    
    print_success(f"Moved {len(moved_files)} duplicate files to {destination_dir}.")
    if len(moved_files) < len(files_to_move):
        print_info(f"Note: {len(files_to_move) - len(moved_files)} files were not moved (may have been moved already or don't exist)")
    
    return moved_files


def copy_duplicate_groups(
    groups: List[List[str]], 
    destination_dir: str, 
    dry_run: bool = True
) -> List[str]:
    """
    Copy duplicate files from groups to destination directory.
    
    Args:
        groups: List of duplicate groups (each group is a list of file paths)
        destination_dir: Directory to copy duplicates to
        dry_run: If True, only show what would be copied
        
    Returns:
        List of copied file paths
    """
    if not groups:
        print_info("No duplicate groups to process.")
        return []
    
    # Flatten all duplicate files (keep first file in each group as original)
    files_to_copy = []
    for group in groups:
        # Skip the first file (original), copy the rest (duplicates)
        duplicates = group[1:]
        files_to_copy.extend(duplicates)
    
    if not files_to_copy:
        print_info("No duplicate files to copy.")
        return []
    
    print_info(f"Found {len(files_to_copy)} duplicate files to copy.")
    
    if dry_run:
        print_warning("DRY RUN - No files will be copied. Set dry_run=False to actually copy files.")
        for file_path in files_to_copy:
            print_info(f"Would copy: {file_path} -> {destination_dir}")
        return files_to_copy
    
    # Create destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)
    
    copied_files = []
    for file_path in tqdm(files_to_copy, desc="Copying duplicates"):
        try:
            # Check if file exists before trying to copy it
            if not os.path.exists(file_path):
                print_warning(f"File not found: {file_path}")
                continue
                
            filename = os.path.basename(file_path)
            dest_path = os.path.join(destination_dir, filename)
            
            # Handle filename conflicts
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(destination_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            shutil.copy2(file_path, dest_path)
            copied_files.append(file_path)
        except Exception as e:
            print_error(f"Error copying {file_path}: {e}")
    
    print_success(f"Copied {len(copied_files)} duplicate files to {destination_dir}.")
    if len(copied_files) < len(files_to_copy):
        print_info(f"Note: {len(files_to_copy) - len(copied_files)} files were not copied (may not exist)")
    
    return copied_files


def remove_duplicate_groups(
    groups: List[List[str]], 
    dry_run: bool = True
) -> List[str]:
    """
    Remove duplicate files from groups.
    
    Args:
        groups: List of duplicate groups (each group is a list of file paths)
        dry_run: If True, only show what would be removed
        
    Returns:
        List of removed file paths
    """
    if not groups:
        print_info("No duplicate groups to process.")
        return []
    
    # Flatten all duplicate files (keep first file in each group as original)
    files_to_remove = []
    for group in groups:
        # Skip the first file (original), remove the rest (duplicates)
        duplicates = group[1:]
        files_to_remove.extend(duplicates)
    
    if not files_to_remove:
        print_info("No duplicate files to remove.")
        return []
    
    print_info(f"Found {len(files_to_remove)} duplicate files to remove.")
    
    if dry_run:
        print_warning("DRY RUN - No files will be removed. Set dry_run=False to actually remove files.")
        for file_path in files_to_remove:
            print_info(f"Would remove: {file_path}")
        return files_to_remove
    
    removed_files = []
    for file_path in tqdm(files_to_remove, desc="Removing duplicates"):
        try:
            # Check if file exists before trying to remove it
            if not os.path.exists(file_path):
                print_warning(f"File not found (may have been removed already): {file_path}")
                continue
                
            os.remove(file_path)
            removed_files.append(file_path)
        except Exception as e:
            print_error(f"Error removing {file_path}: {e}")
    
    print_success(f"Removed {len(removed_files)} duplicate files.")
    if len(removed_files) < len(files_to_remove):
        print_info(f"Note: {len(files_to_remove) - len(removed_files)} files were not removed (may have been removed already or don't exist)")
    
    return removed_files
