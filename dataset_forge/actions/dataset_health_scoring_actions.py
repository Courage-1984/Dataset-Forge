"""
Business logic for Dataset Health Scoring workflow.
"""

from typing import Dict, Any, Optional, Tuple, List
import os
from dataset_forge.utils.file_utils import is_image_file
from dataset_forge.utils.printing import print_info, print_warning, print_error
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.memory_utils import clear_memory

# --- Step Functions ---


def basic_validation(
    dataset_path: str, lq_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Perform basic validation on the dataset (file existence, supported formats, min count).
    Args:
        dataset_path: Path to the dataset folder (HQ or single folder)
        lq_path: Optional LQ folder for HQ/LQ mode
    Returns:
        Dictionary with validation results and issues found.
    """
    issues = []
    passed = True
    min_images = 10
    folders = [dataset_path] if lq_path is None else [dataset_path, lq_path]
    for folder in folders:
        if not os.path.exists(folder):
            issues.append(f"Folder does not exist: {folder}")
            passed = False
        elif not os.path.isdir(folder):
            issues.append(f"Not a directory: {folder}")
            passed = False
        else:
            files = [f for f in os.listdir(folder) if is_image_file(f)]
            if len(files) < min_images:
                issues.append(
                    f"Too few images in {folder} (found {len(files)}, need {min_images})"
                )
                passed = False
    return {
        "passed": passed,
        "issues": issues,
        "suggestion": "Add more images or check folder paths." if not passed else "",
    }


def unreadable_files_check(
    dataset_path: str, lq_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check for unreadable/corrupt image files.
    """
    from PIL import Image

    folders = [dataset_path] if lq_path is None else [dataset_path, lq_path]
    unreadable = []
    for folder in folders:
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if is_image_file(fname):
                try:
                    with Image.open(fpath) as img:
                        img.verify()
                except Exception:
                    unreadable.append(fpath)
    passed = len(unreadable) == 0
    return {
        "passed": passed,
        "unreadable": unreadable,
        "suggestion": "Remove or replace corrupt files." if not passed else "",
    }


def image_format_consistency(
    dataset_path: str, lq_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check for image format consistency.
    """
    folders = [dataset_path] if lq_path is None else [dataset_path, lq_path]
    formats = set()
    for folder in folders:
        for fname in os.listdir(folder):
            if is_image_file(fname):
                ext = os.path.splitext(fname)[1].lower()
                formats.add(ext)
    passed = len(formats) <= 2  # Allow up to 2 formats
    return {
        "passed": passed,
        "formats": list(formats),
        "suggestion": (
            "Consider converting images to a consistent format (e.g., all .png or .jpg)."
            if not passed
            else ""
        ),
    }


def quality_metrics(dataset_path: str, lq_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Compute quality metrics (resolution, blur, color stats, etc.).
    """
    from PIL import Image

    folders = [dataset_path] if lq_path is None else [dataset_path, lq_path]
    resolutions = []
    for folder in folders:
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if is_image_file(fname):
                try:
                    with Image.open(fpath) as img:
                        resolutions.append(img.size)
                except Exception:
                    continue
    if not resolutions:
        return {
            "passed": False,
            "avg_resolution": (0, 0),
            "suggestion": "No readable images found.",
        }
    avg_w = sum(w for w, h in resolutions) // len(resolutions)
    avg_h = sum(h for w, h in resolutions) // len(resolutions)
    passed = avg_w >= 256 and avg_h >= 256
    return {
        "passed": passed,
        "avg_resolution": (avg_w, avg_h),
        "suggestion": (
            "Average resolution is low. Consider upscaling or filtering low-res images."
            if not passed
            else ""
        ),
    }


def aspect_ratio_consistency(
    dataset_path: str, lq_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check for aspect ratio consistency.
    """
    from PIL import Image

    folders = [dataset_path] if lq_path is None else [dataset_path, lq_path]
    ratios = set()
    for folder in folders:
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if is_image_file(fname):
                try:
                    with Image.open(fpath) as img:
                        w, h = img.size
                        ratio = round(w / h, 2) if h else 0
                        ratios.add(ratio)
                except Exception:
                    continue
    passed = len(ratios) <= 3  # Allow up to 3 aspect ratios
    return {
        "passed": passed,
        "ratios": list(ratios),
        "suggestion": (
            "Consider standardizing aspect ratios for model training."
            if not passed
            else ""
        ),
    }


def file_size_outliers(
    dataset_path: str, lq_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check for file size outliers.
    """
    import numpy as np

    folders = [dataset_path] if lq_path is None else [dataset_path, lq_path]
    sizes = []
    for folder in folders:
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if is_image_file(fname):
                try:
                    sizes.append(os.path.getsize(fpath))
                except Exception:
                    continue
    if not sizes:
        return {"passed": True, "outliers": [], "suggestion": ""}
    arr = np.array(sizes)
    q1, q3 = np.percentile(arr, 25), np.percentile(arr, 75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = [s for s in sizes if s < lower or s > upper]
    passed = len(outliers) < max(3, len(sizes) // 20)
    return {
        "passed": passed,
        "outliers": outliers,
        "suggestion": "Remove or investigate file size outliers." if not passed else "",
    }


def consistency_checks(
    dataset_path: str, lq_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check for duplicates, naming consistency, HQ/LQ alignment, etc.
    """
    # Stub: Replace with real logic
    # For now, always pass
    return {
        "passed": True,
        "duplicates": 0,
        "naming_issues": 0,
        "alignment_issues": 0,
        "suggestion": "",
    }


def compliance_scan(dataset_path: str, lq_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Scan for metadata, forbidden content, privacy issues, etc.
    """
    # Stub: Replace with real logic
    # For now, always pass
    return {
        "passed": True,
        "metadata_issues": 0,
        "forbidden_content": 0,
        "suggestion": "",
    }


# --- Scoring and Aggregation ---

STEP_WEIGHTS = [
    ("basic_validation", 0.18),
    ("unreadable_files_check", 0.12),
    ("image_format_consistency", 0.10),
    ("quality_metrics", 0.18),
    ("aspect_ratio_consistency", 0.10),
    ("file_size_outliers", 0.07),
    ("consistency_checks", 0.15),
    ("compliance_scan", 0.10),
]

ALL_STEPS = [
    ("basic_validation", basic_validation),
    ("unreadable_files_check", unreadable_files_check),
    ("image_format_consistency", image_format_consistency),
    ("quality_metrics", quality_metrics),
    ("aspect_ratio_consistency", aspect_ratio_consistency),
    ("file_size_outliers", file_size_outliers),
    ("consistency_checks", consistency_checks),
    ("compliance_scan", compliance_scan),
]


def compute_health_score(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute the overall health score from all step results.
    Args:
        results: Dictionary with all step results.
    Returns:
        Dictionary with score (0-100), status string, and suggestions.
    """
    score = 0.0
    suggestions = []
    breakdown = {}
    for step, weight in STEP_WEIGHTS:
        step_result = results.get(step, {})
        passed = step_result.get("passed", False)
        if passed:
            score += 100 * weight
            breakdown[step] = ("✅", int(100 * weight))
        else:
            breakdown[step] = ("❌", 0)
            if step_result.get("suggestion"):
                suggestions.append(
                    f"{step.replace('_', ' ').title()}: {step_result['suggestion']}"
                )
    score = int(round(score))
    if score >= 90:
        status = "✅ Production Ready"
    elif score >= 70:
        status = "⚠️ Needs Improvement"
    else:
        status = "❌ Unusable"
    return {
        "score": score,
        "status": status,
        "breakdown": breakdown,
        "suggestions": suggestions,
    }


def score_dataset(dataset_path: str, lq_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the full Dataset Health Scoring workflow.
    Args:
        dataset_path: Path to the dataset folder (HQ or single folder)
        lq_path: Optional LQ folder for HQ/LQ mode
    Returns:
        Dictionary with all step results, final score/status, and suggestions.
    """
    results = {}
    for step_name, step_func in ALL_STEPS:
        try:
            results[step_name] = step_func(dataset_path, lq_path)
        except Exception as e:
            results[step_name] = {
                "passed": False,
                "error": str(e),
                "suggestion": f"Error in {step_name}: {e}",
            }
    results["health_score"] = compute_health_score(results)
    return results
