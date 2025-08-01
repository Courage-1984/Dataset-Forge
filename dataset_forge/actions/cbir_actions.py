import os
import shutil
from typing import List, Optional, Tuple, Dict
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.audio_utils import play_done_sound
from functools import partial

# Import embedding extraction logic from frames_actions
from dataset_forge.actions.frames_actions import ImgToEmbedding
from dataset_forge.utils.cache_utils import in_memory_cache, disk_cache

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    numpy_as_np as np,
    PIL_Image as Image,
    torch,
)


@in_memory_cache(maxsize=32)
def load_images_from_folder(
    folder: str, max_images: Optional[int] = None
) -> List[Tuple[str, Image.Image]]:
    """
    Load images from a folder (with in-memory caching).
    Args:
        folder: Path to folder
        max_images: Max number of images to load
    Returns:
        List of (path, PIL.Image) tuples
    Note:
        This function is cached in-memory for fast repeated access in the same session.
    """
    images = []
    supported_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
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

    def load_single_image(path: str) -> Optional[Tuple[str, Image.Image]]:
        try:
            img = Image.open(path).convert("RGB")
            return (path, img)
        except Exception:
            return None

    # Sequential processing to avoid pickling issues
    loaded_images = []
    for path in tqdm(image_paths, desc="Loading Images"):
        try:
            img = load_single_image(path)
            if img is not None:
                loaded_images.append(img)
        except Exception as e:
            print_warning(f"Error loading image {path}: {e}")
    return loaded_images


def get_model_enum(model_name: str):
    from dataset_forge.actions.frames_actions import EmbeddedModel

    if model_name.lower() == "clip":
        return "clip"
    elif model_name.lower() == "resnet":
        # Use timm's resnet50
        return "resnet"
    elif model_name.lower() == "vgg":
        # Use timm's vgg16
        return "vgg"
    else:
        raise ValueError(f"Unknown model: {model_name}")


@disk_cache(compression=True, ttl_seconds=3600)
def extract_embeddings(
    images: List[Tuple[str, Image.Image]], model_name: str, device: str = "cuda"
) -> np.ndarray:
    """
    Extract deep embeddings for a list of images (with persistent disk caching).
    Args:
        images: List of (path, PIL.Image) tuples
        model_name: 'clip', 'resnet', or 'vgg'
        device: Device string
    Returns:
        np.ndarray of embeddings
    Note:
        This function is disk-cached for fast repeated access across sessions.
    """
    if model_name == "clip":
        # Use existing CLIP logic from visual_dedup_actions
        try:
            from dataset_forge.actions.visual_dedup_actions import (
                compute_clip_embeddings,
            )

            return compute_clip_embeddings(images, device)
        except ImportError:
            print_error(
                "open-clip-torch not installed. Please install it for CLIP support."
            )
            raise
    elif model_name == "resnet":
        import timm
        import torchvision.transforms as T

        model = timm.create_model("resnet50", pretrained=True)
        model.eval()
        model = model.to(device)
        preprocess = T.Compose(
            [
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

        def get_embedding(img_tuple):
            _, img = img_tuple
            with torch.no_grad():
                img_tensor = preprocess(img).unsqueeze(0).to(device)
                emb = model.forward_features(img_tensor)
                if hasattr(emb, "detach"):
                    emb = emb.detach().cpu().numpy().flatten()
                else:
                    emb = np.array(emb).flatten()
                return emb

        # Sequential processing to avoid pickling issues
        embs = []
        for i, img_tuple in enumerate(tqdm(images, desc="ResNet embedding")):
            try:
                emb = get_embedding(img_tuple)
                embs.append(emb)
            except Exception as e:
                print_warning(f"Error processing image {i}: {e}")
                # Add zero embedding for failed images
                if embs:
                    embs.append(np.zeros_like(embs[0]))
                else:
                    # If no successful embeddings yet, create a dummy one
                    embs.append(np.zeros(2048))  # ResNet50 feature size
        return np.stack(embs)
    elif model_name == "vgg":
        import timm
        import torchvision.transforms as T

        model = timm.create_model("vgg16", pretrained=True)
        model.eval()
        model = model.to(device)
        preprocess = T.Compose(
            [
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

        def get_embedding(img_tuple):
            _, img = img_tuple
            with torch.no_grad():
                img_tensor = preprocess(img).unsqueeze(0).to(device)
                emb = model.forward_features(img_tensor)
                if hasattr(emb, "detach"):
                    emb = emb.detach().cpu().numpy().flatten()
                else:
                    emb = np.array(emb).flatten()
                return emb

        # Sequential processing to avoid pickling issues
        embs = []
        for i, img_tuple in enumerate(tqdm(images, desc="VGG embedding")):
            try:
                emb = get_embedding(img_tuple)
                embs.append(emb)
            except Exception as e:
                print_warning(f"Error processing image {i}: {e}")
                # Add zero embedding for failed images
                if embs:
                    embs.append(np.zeros_like(embs[0]))
                else:
                    # If no successful embeddings yet, create a dummy one
                    embs.append(np.zeros(512))  # VGG16 feature size
        return np.stack(embs)
    else:
        raise ValueError(f"Unknown model: {model_name}")


def compute_similarity_matrix(embs: np.ndarray, metric: str = "cosine") -> np.ndarray:
    if metric == "cosine":
        # Handle zero vectors to avoid division by zero
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        # Replace zero norms with 1 to avoid division by zero
        norms = np.where(norms == 0, 1, norms)
        norm_embs = embs / norms
        sim_matrix = np.dot(norm_embs, norm_embs.T)
        # Ensure diagonal is 1.0 for self-similarity
        np.fill_diagonal(sim_matrix, 1.0)
        return sim_matrix
    elif metric == "euclidean":
        from scipy.spatial.distance import cdist

        dist_matrix = cdist(embs, embs, metric="euclidean")
        return dist_matrix
    else:
        raise ValueError(f"Unknown metric: {metric}")


def group_duplicates(
    images: List[Tuple[str, Image.Image]],
    sim_matrix: np.ndarray,
    threshold: float,
    metric: str = "cosine",
) -> List[List[str]]:
    n = len(images)
    groups = []
    visited = set()
    for i in range(n):
        if i in visited:
            continue
        group = [images[i][0]]
        for j in range(n):
            if i == j:
                continue
            if metric == "cosine":
                if sim_matrix[i, j] > threshold:
                    group.append(images[j][0])
                    visited.add(j)
            elif metric == "euclidean":
                if sim_matrix[i, j] < threshold:
                    group.append(images[j][0])
                    visited.add(j)
        if len(group) > 1:
            groups.append(group)
        visited.add(i)
    return groups


def remove_duplicate_groups(
    groups: List[List[str]], dry_run: bool = False
) -> List[str]:
    """Remove all but the first image in each group."""
    removed = []
    for group in tqdm(groups, desc="Removing duplicates"):
        for img in group[1:]:
            if dry_run:
                removed.append(img)
            else:
                try:
                    os.remove(img)
                    removed.append(img)
                except Exception as e:
                    print_warning(f"Failed to remove {img}: {e}")
    return removed


def move_duplicate_groups(
    groups: List[List[str]], destination_dir: str, dry_run: bool = False
) -> List[str]:
    """Move all but the first image in each group to destination_dir."""
    os.makedirs(destination_dir, exist_ok=True)
    moved = []
    from dataset_forge.utils.file_utils import get_unique_filename

    for group in tqdm(groups, desc="Moving duplicates"):
        for img in group[1:]:
            dest = os.path.join(
                destination_dir,
                get_unique_filename(destination_dir, os.path.basename(img)),
            )
            if dry_run:
                moved.append(f"{img} -> {dest}")
            else:
                try:
                    shutil.move(img, dest)
                    moved.append(dest)
                except Exception as e:
                    print_warning(f"Failed to move {img}: {e}")
    return moved


def copy_duplicate_groups(
    groups: List[List[str]], destination_dir: str, dry_run: bool = False
) -> List[str]:
    """Copy all but the first image in each group to destination_dir."""
    os.makedirs(destination_dir, exist_ok=True)
    copied = []
    from dataset_forge.utils.file_utils import get_unique_filename

    for group in tqdm(groups, desc="Copying duplicates"):
        for img in group[1:]:
            dest = os.path.join(
                destination_dir,
                get_unique_filename(destination_dir, os.path.basename(img)),
            )
            if dry_run:
                copied.append(f"{img} -> {dest}")
            else:
                try:
                    shutil.copy2(img, dest)
                    copied.append(dest)
                except Exception as e:
                    print_warning(f"Failed to copy {img}: {e}")
    return copied


# Update cbir_workflow to support these actions


def cbir_workflow(
    folder: Optional[str] = None,
    hq_folder: Optional[str] = None,
    lq_folder: Optional[str] = None,
    model_name: str = "clip",
    threshold: float = 0.98,
    max_images: Optional[int] = 100,
    metric: str = "cosine",
    operation: str = "find",
    device: str = "cuda",
    dest_dir: Optional[str] = None,
    dry_run: bool = False,
    **kwargs,
) -> Dict[str, List[List[str]]]:
    """
    Main CBIR workflow for semantic duplicate detection.
    Returns a dict with folder as key and groups as value, or a summary for remove/move/copy.
    """
    results = {}
    if folder:
        print_info(f"Loading images from {folder}...")
        images = load_images_from_folder(folder, max_images)
        print_info(f"Extracting embeddings with {model_name}...")
        embs = extract_embeddings(images, model_name, device)
        print_info(f"Computing similarity matrix ({metric})...")
        sim_matrix = compute_similarity_matrix(embs, metric)
        print_info(f"Grouping duplicates (threshold={threshold})...")
        groups = group_duplicates(images, sim_matrix, threshold, metric)
        if operation == "find":
            results[folder] = groups
        elif operation == "remove":
            removed = remove_duplicate_groups(groups, dry_run=dry_run)
            results[folder] = removed
        elif operation == "move":
            if not dest_dir:
                print_error("Destination directory required for move operation.")
                return {}
            moved = move_duplicate_groups(groups, dest_dir, dry_run=dry_run)
            results[folder] = moved
        elif operation == "copy":
            if not dest_dir:
                print_error("Destination directory required for copy operation.")
                return {}
            copied = copy_duplicate_groups(groups, dest_dir, dry_run=dry_run)
            results[folder] = copied
        else:
            print_warning(f"Unknown operation: {operation}")
            results[folder] = []
    elif hq_folder and lq_folder:
        for path in [hq_folder, lq_folder]:
            print_info(f"Loading images from {path}...")
            images = load_images_from_folder(path, max_images)
            print_info(f"Extracting embeddings with {model_name}...")
            embs = extract_embeddings(images, model_name, device)
            print_info(f"Computing similarity matrix ({metric})...")
            sim_matrix = compute_similarity_matrix(embs, metric)
            print_info(f"Grouping duplicates (threshold={threshold})...")
            groups = group_duplicates(images, sim_matrix, threshold, metric)
            if operation == "find":
                results[path] = groups
            elif operation == "remove":
                removed = remove_duplicate_groups(groups, dry_run=dry_run)
                results[path] = removed
            elif operation == "move":
                if not dest_dir:
                    print_error("Destination directory required for move operation.")
                    return {}
                moved = move_duplicate_groups(groups, dest_dir, dry_run=dry_run)
                results[path] = moved
            elif operation == "copy":
                if not dest_dir:
                    print_error("Destination directory required for copy operation.")
                    return {}
                copied = copy_duplicate_groups(groups, dest_dir, dry_run=dry_run)
                results[path] = copied
            else:
                print_warning(f"Unknown operation: {operation}")
                results[path] = []
    else:
        print_warning("No valid folder(s) provided for CBIR workflow.")
        return {}
    print_success(f"CBIR operation '{operation}' complete.")
    play_done_sound()
    clear_memory()
    clear_cuda_cache()
    return results
