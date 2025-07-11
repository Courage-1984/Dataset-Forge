import os
import shutil
from typing import List, Optional, Tuple, Dict
from PIL import Image
import torch
import numpy as np
from dataset_forge.utils.progress_utils import tqdm, image_map, smart_map
from dataset_forge.utils.parallel_utils import (
    parallel_image_processing,
    ProcessingType,
    ParallelConfig,
    setup_parallel_environment,
)
from dataset_forge.menus.session_state import parallel_config
from functools import partial

from dataset_forge.utils.printing import (
    print_info,
    print_error,
    print_success,
    print_warning,
)


def load_images_from_folder(
    folder: str, max_images: Optional[int] = None
) -> List[Tuple[str, Image.Image]]:
    """Load images from folder with parallel processing support."""
    images = []
    supported_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}

    # Collect image paths first
    image_paths = []
    for root, _, files in os.walk(folder):
        for fname in files:
            if os.path.splitext(fname)[1].lower() in supported_exts:
                path = os.path.join(root, fname)
                image_paths.append(path)
                if max_images and len(image_paths) >= max_images:
                    break
        if max_images and len(image_paths) >= max_images:
            break

    # Load images in parallel
    def load_single_image(path: str) -> Optional[Tuple[str, Image.Image]]:
        try:
            img = Image.open(path).convert("RGB")
            return (path, img)
        except Exception:
            return None

    # Use parallel processing for loading images
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # I/O bound task
        use_gpu=parallel_config.get("use_gpu", True),
    )

    loaded_images = parallel_image_processing(
        load_single_image,
        image_paths,
        desc="Loading Images",
        max_workers=config.max_workers,
    )

    # Filter out None results
    images = [img for img in loaded_images if img is not None]

    return images


def get_lpips_model(device: str = "cuda" if torch.cuda.is_available() else "cpu"):
    if lpips is None:
        raise ImportError("lpips is not installed. Please install it via pip.")
    from dataset_forge.utils.memory_utils import to_device_safe

    return to_device_safe(lpips.LPIPS(net="vgg"), device)


def compute_lpips_matrix(
    images: List[Tuple[str, Image.Image]],
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> np.ndarray:
    """Compute LPIPS similarity matrix with parallel processing."""
    model = get_lpips_model(device)
    n = len(images)
    matrix = np.zeros((n, n), dtype=np.float32)

    # Import centralized memory management
    from dataset_forge.utils.memory_utils import to_device_safe

    # Prepare image tensors
    imgs_tensor = [
        torch.from_numpy(np.array(img[1]).transpose(2, 0, 1)).float() / 127.5 - 1
        for img in images
    ]
    imgs_tensor = [to_device_safe(img.unsqueeze(0), device) for img in imgs_tensor]

    # Compute similarities in parallel batches
    def compute_similarity_batch(
        batch_indices: List[int],
    ) -> List[Tuple[int, int, float]]:
        results = []
        for i in batch_indices:
            for j in range(i + 1, n):
                dist = model(imgs_tensor[i], imgs_tensor[j]).item()
                results.append((i, j, dist))
        return results

    # Create batches of indices
    batch_size = max(1, n // (parallel_config.get("max_workers", 4) or 4))
    batches = [list(range(i, min(i + batch_size, n))) for i in range(0, n, batch_size)]

    # Process batches in parallel
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # GPU operations use threads
        use_gpu=parallel_config.get("use_gpu", True),
    )

    all_results = smart_map(
        compute_similarity_batch,
        batches,
        desc="LPIPS (perceptual) similarity",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    # Fill matrix with results
    for batch_results in all_results:
        for i, j, dist in batch_results:
            matrix[i, j] = matrix[j, i] = dist

    return matrix


def get_clip_model(device: str = "cuda" if torch.cuda.is_available() else "cpu"):
    if open_clip is None:
        raise ImportError(
            "open-clip-torch is not installed. Please install it via pip."
        )
    from dataset_forge.utils.memory_utils import to_device_safe

    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="laion2b_s34b_b79k"
    )
    model = to_device_safe(model, device)
    return model, preprocess


def compute_single_embedding(
    img_tuple: Tuple[str, Image.Image], model, preprocess, device: str
) -> np.ndarray:
    try:
        from dataset_forge.utils.memory_utils import to_device_safe

        _, img = img_tuple
        with torch.no_grad():
            img_tensor = to_device_safe(preprocess(img).unsqueeze(0), device)
            emb = model.encode_image(img_tensor)
            return emb.cpu().numpy().flatten()
    except Exception as e:
        print_warning(f"Error computing embedding: {e}")
        return np.zeros(512)  # Default CLIP embedding size


def compute_clip_embeddings(
    images: List[Tuple[str, Image.Image]],
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> np.ndarray:
    """Compute CLIP embeddings with parallel processing."""
    model, preprocess = get_clip_model(device)
    model.eval()

    # Use parallel processing for embeddings
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # GPU operations use threads
        use_gpu=parallel_config.get("use_gpu", True),
    )

    # Use functools.partial to bind model, preprocess, and device
    embedding_func = partial(
        compute_single_embedding, model=model, preprocess=preprocess, device=device
    )

    embs = smart_map(
        embedding_func,
        images,
        desc="CLIP embedding",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

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
    """Find near duplicates using LPIPS with parallel processing."""
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
    """Find near duplicates using CLIP with parallel processing."""
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
    Main entry point for visual deduplication with parallel processing.
    Returns a dict with method as key and groups as value.
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
        # Process HQ and LQ folders in parallel
        def process_folder(path: str) -> Tuple[str, List[List[str]]]:
            images = load_images_from_folder(path, max_images)
            if method == "lpips":
                groups = find_near_duplicates_lpips(images, threshold, device)
            else:
                groups = find_near_duplicates_clip(images, threshold, device)
            return path, groups

        # Process both folders in parallel
        config = ParallelConfig(
            max_workers=parallel_config.get("max_workers"),
            processing_type=ProcessingType.THREAD,
            use_gpu=parallel_config.get("use_gpu", True),
        )

        folder_results = smart_map(
            process_folder,
            [hq_path, lq_path],
            desc="Processing folders",
            max_workers=2,  # Only 2 folders
            processing_type=ProcessingType.THREAD,
        )

        for path, groups in folder_results:
            results[path] = groups

    return results


def move_duplicate_groups(
    groups: List[List[str]], destination_dir: str, dry_run: bool = True
) -> List[str]:
    """
    Move duplicate files from groups to destination directory with parallel processing.

    Args:
        groups: List of duplicate groups (each group is a list of file paths)
        destination_dir: Directory to move duplicates to
        dry_run: If True, only show what would be moved

    Returns:
        List of moved file paths
    """
    if not dry_run:
        os.makedirs(destination_dir, exist_ok=True)

    moved_files = []

    def process_group(group: List[str]) -> List[str]:
        group_moved = []
        # Keep the first file, move the rest
        for i, file_path in enumerate(group[1:], 1):
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                dest_path = os.path.join(destination_dir, f"dup_{i}_{filename}")

                if not dry_run:
                    try:
                        shutil.move(file_path, dest_path)
                        group_moved.append(file_path)
                    except Exception as e:
                        print_error(f"Error moving {file_path}: {e}")
                else:
                    print_info(f"Would move: {file_path} -> {dest_path}")
                    group_moved.append(file_path)

        return group_moved

    # Process groups in parallel
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # File I/O bound
        use_gpu=False,  # No GPU needed for file operations
    )

    all_moved = smart_map(
        process_group,
        groups,
        desc="Moving duplicates",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    for group_moved in all_moved:
        moved_files.extend(group_moved)

    return moved_files


def copy_duplicate_groups(
    groups: List[List[str]], destination_dir: str, dry_run: bool = True
) -> List[str]:
    """
    Copy duplicate files from groups to destination directory with parallel processing.

    Args:
        groups: List of duplicate groups (each group is a list of file paths)
        destination_dir: Directory to copy duplicates to
        dry_run: If True, only show what would be copied

    Returns:
        List of copied file paths
    """
    if not dry_run:
        os.makedirs(destination_dir, exist_ok=True)

    copied_files = []

    def process_group(group: List[str]) -> List[str]:
        group_copied = []
        # Keep the first file, copy the rest
        for i, file_path in enumerate(group[1:], 1):
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                dest_path = os.path.join(destination_dir, f"dup_{i}_{filename}")

                if not dry_run:
                    try:
                        shutil.copy2(file_path, dest_path)
                        group_copied.append(file_path)
                    except Exception as e:
                        print_error(f"Error copying {file_path}: {e}")
                else:
                    print_info(f"Would copy: {file_path} -> {dest_path}")
                    group_copied.append(file_path)

        return group_copied

    # Process groups in parallel
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # File I/O bound
        use_gpu=False,  # No GPU needed for file operations
    )

    all_copied = smart_map(
        process_group,
        groups,
        desc="Copying duplicates",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    for group_copied in all_copied:
        copied_files.extend(group_copied)

    return copied_files


def remove_duplicate_groups(groups: List[List[str]], dry_run: bool = True) -> List[str]:
    """
    Remove duplicate files from groups with parallel processing.

    Args:
        groups: List of duplicate groups (each group is a list of file paths)
        dry_run: If True, only show what would be removed

    Returns:
        List of removed file paths
    """
    removed_files = []

    def process_group(group: List[str]) -> List[str]:
        group_removed = []
        # Keep the first file, remove the rest
        for file_path in group[1:]:
            if os.path.exists(file_path):
                if not dry_run:
                    try:
                        os.remove(file_path)
                        group_removed.append(file_path)
                    except Exception as e:
                        print_error(f"Error removing {file_path}: {e}")
                else:
                    print_info(f"Would remove: {file_path}")
                    group_removed.append(file_path)

        return group_removed

    # Process groups in parallel
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # File I/O bound
        use_gpu=False,  # No GPU needed for file operations
    )

    all_removed = smart_map(
        process_group,
        groups,
        desc="Removing duplicates",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    for group_removed in all_removed:
        removed_files.extend(group_removed)

    return removed_files


# Import statements at the end to avoid circular imports
try:
    import lpips
except ImportError:
    lpips = None

try:
    import open_clip
except ImportError:
    open_clip = None
