import os
from dataset_forge.utils.progress_utils import tqdm
import numpy as np
from dataset_forge.actions.frames_actions import ImgToEmbedding, EmbeddedModel
from dataset_forge.utils.file_utils import is_image_file
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
    print_section,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.audio_utils import play_done_sound


def detect_outliers(
    hq_folder=None,
    lq_folder=None,
    single_path=None,
    model_name="ConvNextS",
    device="cuda",
):
    """
    Detect outlier images using embeddings and clustering or distance-based scoring.
    Supports HQ/LQ or single-folder workflows.
    """
    if hq_folder and lq_folder:
        print_info(f"\n[Outlier Detection] HQ/LQ mode: {hq_folder} / {lq_folder}")
        _detect_outliers_for_folder(hq_folder, model_name, device, label="HQ")
        _detect_outliers_for_folder(lq_folder, model_name, device, label="LQ")
    elif single_path:
        print_info(f"\n[Outlier Detection] Single folder mode: {single_path}")
        _detect_outliers_for_folder(single_path, model_name, device)
    else:
        print_error("[Outlier Detection] No valid path(s) provided.")


def _detect_outliers_for_folder(folder, model_name, device, label=None):
    image_files = [
        os.path.join(folder, f) for f in os.listdir(folder) if is_image_file(f)
    ]
    if not image_files:
        print_warning(f"No images found in {folder}.")
        return
    print_info(
        f"Extracting embeddings for {len(image_files)} images{' in ' + label if label else ''}..."
    )
    model_enum = getattr(EmbeddedModel, model_name, EmbeddedModel.ConvNextS)
    embedder = ImgToEmbedding(model=model_enum, device=device)
    embeddings = []
    for img_path in tqdm(image_files, desc="Embedding", unit="img"):
        try:
            import cv2

            img = (
                cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB).astype(np.float32)
                / 255.0
            )
            emb = embedder(img)
            if hasattr(emb, "detach"):
                emb = emb.detach().cpu().numpy().flatten()
            else:
                emb = np.array(emb).flatten()
            embeddings.append(emb)
        except Exception as e:
            print_warning(f"Failed to embed {img_path}: {e}")
            embeddings.append(None)
    # Remove failed embeddings
    valid = [(f, e) for f, e in zip(image_files, embeddings) if e is not None]
    if not valid:
        print_error("No valid embeddings computed.")
        return
    files, emb_array = zip(*valid)
    emb_array = np.stack(emb_array)
    # Outlier scoring: use distance to mean (simple stub, replace with clustering if needed)
    mean_emb = np.mean(emb_array, axis=0)
    dists = np.linalg.norm(emb_array - mean_emb, axis=1)
    threshold = np.mean(dists) + 2 * np.std(dists)
    outliers = [f for f, d in zip(files, dists) if d > threshold]
    print_info(f"\nPotential outliers ({len(outliers)}):")
    for f in outliers:
        print_info(f"  {f}")
    if not outliers:
        print_info("No strong outliers detected.")
