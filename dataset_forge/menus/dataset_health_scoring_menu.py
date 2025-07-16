"""
UI workflow for Dataset Health Scoring.
"""

from dataset_forge.utils.input_utils import get_path_with_history, get_folder_path
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.memory_utils import clear_memory
from dataset_forge.utils.progress_utils import tqdm
import os

# Lazy import pattern for actions
score_dataset = None


def dataset_health_scoring_menu():
    """
    Interactive workflow for Dataset Health Scoring.
    Prompts for single folder or HQ/LQ parent, runs scoring, and displays results.
    """
    global score_dataset
    if score_dataset is None:
        from dataset_forge.actions.dataset_health_scoring_actions import score_dataset
    print_header("🩺 Dataset Health Scoring", color=Mocha.sapphire)
    try:
        print_info("Choose dataset type:")
        print_info("  [1] Single folder (all images in one folder)")
        print_info("  [2] HQ/LQ parent folder (contains HQ and LQ subfolders)")
        mode = input("Enter 1 for single folder, 2 for HQ/LQ parent: ").strip()
        if mode == "2":
            parent_path = get_folder_path("Enter HQ/LQ parent folder path:")
            # Try to auto-detect HQ/LQ subfolders
            subfolders = [
                f
                for f in os.listdir(parent_path)
                if os.path.isdir(os.path.join(parent_path, f))
            ]
            hq_path, lq_path = None, None
            for sub in subfolders:
                if sub.lower() in ("hq", "high", "high_quality", "highquality"):
                    hq_path = os.path.join(parent_path, sub)
                if sub.lower() in ("lq", "low", "low_quality", "lowquality"):
                    lq_path = os.path.join(parent_path, sub)
            if not hq_path:
                hq_path = get_folder_path("Enter HQ folder path:")
            if not lq_path:
                lq_path = get_folder_path("Enter LQ folder path:")
            print_info(f"Selected HQ: {hq_path}")
            print_info(f"Selected LQ: {lq_path}")
            print_info("Running health scoring for HQ/LQ pair...\n")
            results = score_dataset(hq_path, lq_path)
            dataset_path_display = f"HQ: {hq_path}\nLQ: {lq_path}"
        else:
            dataset_path = get_path_with_history("Enter path to dataset folder:")
            print_info(f"Selected dataset: {dataset_path}")
            print_info("Running health scoring...\n")
            results = score_dataset(dataset_path)
            dataset_path_display = dataset_path
        # Show step results (detailed breakdown)
        health = results["health_score"]
        print_info("\nStep Results:")
        for step, (icon, pts) in health["breakdown"].items():
            label = step.replace("_", " ").title()
            print_info(f"  {icon} {label} ({pts} pts)")
        print_info("\n─────────────────────────────")
        print_info(f"Dataset Health Score: {health['score']}/100")
        print_info(f"Status: {health['status']}")
        print_info("─────────────────────────────\n")
        if health["suggestions"]:
            print_warning("Next Steps / Suggestions:")
            for suggestion in health["suggestions"]:
                print_info(f"  - {suggestion}")
            print_info("")
    except Exception as e:
        print_error(f"Error during health scoring: {e}")
    finally:
        clear_memory()
