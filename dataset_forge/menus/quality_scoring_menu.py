from dataset_forge.actions.quality_scoring_actions import (
    score_images_with_pyiqa,
    plot_quality_histogram,
    filter_images_by_quality,
    score_hq_lq_folders,
)
from dataset_forge.utils.input_utils import get_path_with_history
from dataset_forge.utils.printing import print_info, print_success, print_error


def quality_scoring_menu():
    print("\n=== Automated Dataset Quality Scoring ===")
    print("1. HQ/LQ parent_path workflow")
    print("2. Single-folder workflow")
    print("0. Return to main menu")
    choice = input("Select workflow: ")
    if choice == "1":
        hq = get_path_with_history("Enter HQ folder path:")
        lq = get_path_with_history("Enter LQ folder path:")
        workflow = "hqlq"
    elif choice == "2":
        folder = get_path_with_history("Enter folder path:")
        workflow = "single"
    else:
        return
    print("\nSelect quality model:")
    print("1. NIQE (no-reference, fast, default)")
    print("2. BRISQUE (no-reference, fast)")
    print("3. DeepIQA (deep model, slower)")
    model_choice = input("Model [1/2/3, default 1]: ").strip() or "1"
    model_map = {"1": "niqe", "2": "brisque", "3": "deepiqa"}
    model_name = model_map.get(model_choice, "niqe")
    device = "cuda" if model_name == "deepiqa" else "cpu"
    if workflow == "hqlq":
        hq_scores, lq_scores = score_hq_lq_folders(hq, lq, model_name, device)
        print("\n[HQ] Quality Histogram:")
        plot_quality_histogram(hq_scores, model_name)
        print("\n[LQ] Quality Histogram:")
        plot_quality_histogram(lq_scores, model_name)
        scores = hq_scores + lq_scores
    else:
        scores = score_images_with_pyiqa(folder, model_name, device)
        print("\nQuality Histogram:")
        plot_quality_histogram(scores, model_name)
    try:
        threshold = float(
            input("Enter quality threshold for filtering (or blank to skip): ") or ""
        )
        mode = (
            input("Filter images (above/below threshold)? [below]: ").strip().lower()
            or "below"
        )
        filtered = filter_images_by_quality(scores, threshold, mode)
        print_success(
            f"Filtered {len(filtered)} images (mode: {mode}, threshold: {threshold})"
        )
        for img_path, score in filtered[:10]:
            print(f"  {img_path} (score: {score:.3f})")
        if len(filtered) > 10:
            print(f"  ... and {len(filtered) - 10} more.")
    except ValueError:
        print_info("No filtering applied.")
    input("\nPress Enter to return to the main menu...")
