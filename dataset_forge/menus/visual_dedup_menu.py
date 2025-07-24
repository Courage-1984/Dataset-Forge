from dataset_forge.utils.input_utils import get_path_with_history, get_folder_path
from dataset_forge.utils.printing import print_info, print_warning, print_prompt


def visual_dedup_menu():
    from dataset_forge.actions.visual_dedup_actions import (
        visual_dedup_workflow,
        move_duplicate_groups,
        copy_duplicate_groups,
        remove_duplicate_groups,
    )
    from dataset_forge.utils.printing import print_header, print_section
    from dataset_forge.utils.color import Mocha

    while True:
        print_header(
            "🖼️ Visual Duplicate & Near-Duplicate Detection - Input/Output Selection",
            color=Mocha.yellow,
        )
        print("1. HQ/LQ parent_path workflow")
        print("2. Single-folder workflow")
        print("0. Return to main menu")
        choice = input("Select workflow: ")
        if choice == "0" or choice.strip() == "":
            return
        if choice == "1":
            hq = get_path_with_history(
                "Enter HQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            lq = get_path_with_history(
                "Enter LQ folder path:", allow_hq_lq=True, allow_single_folder=True
            )
            folder = None
        elif choice == "2":
            hq = lq = None
            folder = get_path_with_history(
                "Enter folder path:", allow_hq_lq=True, allow_single_folder=True
            )
        else:
            print_warning("Invalid selection. Please try again.")
            continue
        print_header(
            "🖼️ Visual Duplicate & Near-Duplicate Detection - Method Selection",
            color=Mocha.yellow,
        )
        print("\nSelect method:")
        print("1. CLIP Embedding (fast, semantic)")
        print("2. LPIPS (slow, perceptual)")
        method_choice = input("Method [1]: ").strip() or "1"
        if method_choice == "2":
            method = "lpips"
        else:
            method = "clip"
        try:
            max_images = int(input("Max images to check? [100]: ") or "100")
        except ValueError:
            max_images = 100
        threshold = None
        print_section("Visual Deduplication Progress", color=Mocha.yellow)
        try:
            visual_dedup_workflow(
                hq_path=hq,
                lq_path=lq,
                single_folder_path=folder,
                method=method,
                threshold=threshold,
                max_images=max_images,
            )
        except Exception as e:
            print_warning(f"Error during visual deduplication: {e}")
        # At the end of the workflow, after all processing:
        print_prompt("\n⏸️ Press Enter to return to the Visual Deduplication menu...")
        input()


# Register a static menu for favorites
visual_dedup_menu.__menu_options__ = {
    "1": ("Run Visual Deduplication Workflow", visual_dedup_menu),
    "0": ("Back to Main Menu", None),
}
