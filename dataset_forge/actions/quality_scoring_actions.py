import os
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.file_utils import is_image_file
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    numpy_as_np as np,
    matplotlib_pyplot as plt,
    pyiqa,
)


def score_images_with_pyiqa(folder, model_name="niqe", device="cpu"):
    if pyiqa is None:
        raise ImportError(
            "pyiqa is not installed. Please install it to use quality scoring."
        )
    model = pyiqa.create_metric(model_name, device=device)
    image_files = [
        os.path.join(folder, f) for f in os.listdir(folder) if is_image_file(f)
    ]
    scores = []
    for img_path in tqdm(image_files, desc=f"Scoring ({model_name})", unit="img"):
        try:
            score = float(model(img_path))
            scores.append((img_path, score))
        except Exception as e:
            print(f"[WARN] Failed to score {img_path}: {e}")
    return scores


def plot_quality_histogram(scores, model_name="niqe", show=True, save_path=None):
    values = [s[1] for s in scores]
    plt.figure(figsize=(8, 4))
    plt.hist(values, bins=30, color="#8aadf4", edgecolor="#24273a")
    plt.title(f"Image Quality Score Histogram ({model_name.upper()})")
    plt.xlabel("Score")
    plt.ylabel("Count")
    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()
    plt.close()


def filter_images_by_quality(scores, threshold, mode="above"):
    if mode == "above":
        return [s for s in scores if s[1] >= threshold]
    else:
        return [s for s in scores if s[1] <= threshold]


def score_hq_lq_folders(hq_folder, lq_folder, model_name="niqe", device="cpu"):
    print(f"Scoring HQ folder: {hq_folder}")
    hq_scores = score_images_with_pyiqa(hq_folder, model_name, device)
    print(f"Scoring LQ folder: {lq_folder}")
    lq_scores = score_images_with_pyiqa(lq_folder, model_name, device)
    return hq_scores, lq_scores


def score_image_with_pyiqa(
    image_path: str, model_name: str = "niqe", device: str = "cpu"
) -> float:
    """
    Score a single image using pyiqa.

    Args:
        image_path: Path to the image file
        model_name: Name of the IQA model (default: "niqe")
        device: Device to use ("cpu" or "cuda")

    Returns:
        The quality score as a float

    Raises:
        ImportError: If pyiqa is not installed
        Exception: If scoring fails
    """
    if pyiqa is None:
        raise ImportError(
            "pyiqa is not installed. Please install it to use quality scoring."
        )
    model = pyiqa.create_metric(model_name, device=device)
    try:
        score = float(model(image_path))
        return score
    except Exception as e:
        raise Exception(f"Failed to score {image_path}: {e}")
