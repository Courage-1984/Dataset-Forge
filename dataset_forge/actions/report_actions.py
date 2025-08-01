# Rich report generation actions for Dataset Forge
"""
This module provides functions to generate rich HTML/Markdown reports with plots and sample images.
Supports both HQ/LQ parent_path and single-folder workflows.
"""
import os
import shutil
from dataset_forge.utils.progress_utils import tqdm
import random
from collections import Counter
from dataset_forge.utils.file_utils import is_image_file
from dataset_forge.actions.bhi_filtering_actions import (
    BlockinessThread,
    HyperThread,
    IC9600Thread,
)
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    PIL_Image as Image,
    matplotlib_pyplot as plt,
    numpy_as_np as np,
    jinja2,
)


def collect_image_stats(files):
    stats = {
        "widths": [],
        "heights": [],
        "filepaths": [],
    }
    for f in tqdm(files, desc="Collecting image stats"):
        try:
            with Image.open(f) as img:
                w, h = img.size
                stats["widths"].append(w)
                stats["heights"].append(h)
                stats["filepaths"].append(f)
        except Exception as e:
            continue
    return stats


def plot_dimension_histogram(widths, heights, output_dir):
    plt.figure(figsize=(10, 5))
    plt.hist(widths, bins=30, alpha=0.5, label="Widths")
    plt.hist(heights, bins=30, alpha=0.5, label="Heights")
    plt.xlabel("Pixels")
    plt.ylabel("Count")
    plt.title("Image Dimension Histogram")
    plt.legend()
    plot_path = os.path.join(output_dir, "dimension_histogram.png")
    plt.savefig(plot_path)
    plt.close()
    return plot_path


def save_sample_images(filepaths, output_dir, sample_count=5):
    sample_dir = os.path.join(output_dir, "samples")
    os.makedirs(sample_dir, exist_ok=True)
    sample_paths = []
    for i, f in enumerate(filepaths[:sample_count]):
        ext = os.path.splitext(f)[1]
        dest = os.path.join(sample_dir, f"sample_{i+1}{ext}")
        shutil.copy(f, dest)
        sample_paths.append(dest)
    return sample_paths


def render_report(
    stats,
    plot_path,
    sample_paths,
    output_path,
    format="html",
    quality_hist_paths=None,
    lq_quality_hist_paths=None,
    class_balance_path=None,
    lq_class_balance_path=None,
):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "../../reports/templates")
        )
    )
    template = env.get_template(f"report_template.{format}.jinja")
    report = template.render(
        num_images=len(stats["filepaths"]),
        avg_width=np.mean(stats["widths"]) if stats["widths"] else 0,
        avg_height=np.mean(stats["heights"]) if stats["heights"] else 0,
        plot_path=os.path.relpath(plot_path, os.path.dirname(output_path)),
        sample_paths=[
            os.path.relpath(p, os.path.dirname(output_path)) for p in sample_paths
        ],
        quality_hist_paths=quality_hist_paths,
        lq_quality_hist_paths=lq_quality_hist_paths,
        class_balance_path=class_balance_path,
        lq_class_balance_path=lq_class_balance_path,
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)


def compute_quality_scores(folder, max_images=100):
    """Compute Blockiness, HyperIQA, and IC9600 scores for up to max_images in the folder."""
    files = [f for f in os.listdir(folder) if is_image_file(f)]
    if len(files) > max_images:
        files = random.sample(files, max_images)
    filepaths = [os.path.join(folder, f) for f in files]
    # Use threads from bhi_filtering
    blockiness_thread = BlockinessThread(folder, batch_size=8)
    hyper_thread = HyperThread(folder, batch_size=8)
    ic9600_thread = IC9600Thread(folder, batch_size=8)
    # Collect scores
    blockiness_scores, hyper_scores, ic9600_scores = [], [], []
    for images, filenames in tqdm(blockiness_thread.data_loader, desc="Blockiness IQA"):
        iqa = blockiness_thread.forward(images)
        blockiness_scores.extend([float(i) for i in iqa])
    for images, filenames in tqdm(hyper_thread.data_loader, desc="HyperIQA"):
        iqa = hyper_thread.forward(images)
        hyper_scores.extend([float(i) for i in iqa])
    for images, filenames in tqdm(ic9600_thread.data_loader, desc="IC9600"):
        iqa = ic9600_thread.forward(images)
        ic9600_scores.extend([float(i) for i in iqa])
    return {
        "blockiness": blockiness_scores[:max_images],
        "hyperiqa": hyper_scores[:max_images],
        "ic9600": ic9600_scores[:max_images],
    }


def plot_quality_histograms(quality_scores, output_dir, prefix=""):
    paths = {}
    for metric, scores in quality_scores.items():
        plt.figure(figsize=(8, 4))
        plt.hist(scores, bins=30, alpha=0.7)
        plt.xlabel("Score")
        plt.ylabel("Count")
        plt.title(f"{prefix} {metric.capitalize()} Histogram")
        plot_path = os.path.join(output_dir, f"{prefix}{metric}_hist.png")
        plt.savefig(plot_path)
        plt.close()
        paths[metric] = plot_path
    return paths


def compute_class_balance(folder):
    """If subfolders exist, treat them as classes and count images per class."""
    subdirs = [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
    if not subdirs:
        return None
    class_counts = {}
    for sub in subdirs:
        sub_path = os.path.join(folder, sub)
        count = len([f for f in os.listdir(sub_path) if is_image_file(f)])
        class_counts[sub] = count
    return class_counts


def plot_class_balance(class_counts, output_dir, prefix=""):
    plt.figure(figsize=(10, 5))
    classes = list(class_counts.keys())
    counts = list(class_counts.values())
    plt.bar(classes, counts)
    plt.xlabel("Class")
    plt.ylabel("Count")
    plt.title(f"{prefix} Class Balance")
    plt.xticks(rotation=45)
    plot_path = os.path.join(output_dir, f"{prefix}class_balance.png")
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    return plot_path


def generate_rich_report(
    hq_path=None,
    lq_path=None,
    single_folder_path=None,
    output_path=None,
    format="html",
    sample_count=5,
    max_quality_images=100,
):
    """
    Generate a rich HTML or Markdown report with plots and sample images.
    Supports both HQ/LQ parent_path and single-folder path workflows.
    sample_count: number of sample images to include in the report
    max_quality_images: max images to process for quality scores
    """
    # Gather files
    if single_folder_path:
        files = [
            os.path.join(single_folder_path, f)
            for f in os.listdir(single_folder_path)
            if is_image_file(f)
        ]
        report_name = os.path.basename(single_folder_path.rstrip("/\\"))
    elif hq_path and lq_path:
        base = os.path.basename(hq_path.rstrip("/\\"))
        report_name = f"{base}_HQ"
    else:
        print("No valid path(s) provided.")
        return
    # Output directory
    output_dir = os.path.join(os.getcwd(), "reports", report_name)
    os.makedirs(output_dir, exist_ok=True)
    if not output_path:
        output_path = os.path.join(output_dir, f"report.{format}")
    # Stats
    stats = collect_image_stats(files)
    # Plot
    plot_path = plot_dimension_histogram(stats["widths"], stats["heights"], output_dir)
    # Samples
    sample_paths = save_sample_images(
        stats["filepaths"], output_dir, sample_count=sample_count
    )
    # Quality scores and plots
    quality_scores = compute_quality_scores(
        single_folder_path or hq_path, max_images=max_quality_images
    )
    quality_hist_paths = plot_quality_histograms(
        quality_scores, output_dir, prefix="HQ_" if hq_path else ""
    )
    if hq_path and lq_path:
        lq_quality_scores = compute_quality_scores(
            lq_path, max_images=max_quality_images
        )
        lq_quality_hist_paths = plot_quality_histograms(
            lq_quality_scores, output_dir, prefix="LQ_"
        )
    else:
        lq_quality_scores = None
        lq_quality_hist_paths = None
    # Class balance
    class_counts = compute_class_balance(single_folder_path or hq_path)
    if class_counts:
        class_balance_path = plot_class_balance(
            class_counts, output_dir, prefix="HQ_" if hq_path else ""
        )
    else:
        class_balance_path = None
    if hq_path and lq_path:
        lq_class_counts = compute_class_balance(lq_path)
        if lq_class_counts:
            lq_class_balance_path = plot_class_balance(
                lq_class_counts, output_dir, prefix="LQ_"
            )
        else:
            lq_class_balance_path = None
    else:
        lq_class_counts = None
        lq_class_balance_path = None
    # Render
    render_report(
        stats,
        plot_path,
        sample_paths,
        output_path,
        format=format,
        quality_hist_paths=quality_hist_paths,
        lq_quality_hist_paths=lq_quality_hist_paths,
        class_balance_path=class_balance_path,
        lq_class_balance_path=lq_class_balance_path,
    )
    print(f"Report generated: {output_path}")
