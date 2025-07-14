from dataset_forge.utils.input_utils import get_path_with_history, get_folder_path
from dataset_forge.utils.printing import print_info, print_warning, print_prompt


def visual_dedup_menu():
    from dataset_forge.actions.visual_dedup_actions import (
        visual_dedup_workflow,
        move_duplicate_groups,
        copy_duplicate_groups,
        remove_duplicate_groups,
    )

    while True:
        print("\n=== Visual Duplicate & Near-Duplicate Detection ===")
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
        if method == "lpips":
            try:
                threshold = float(input("LPIPS threshold? [0.2]: ") or "0.2")
            except ValueError:
                threshold = 0.2
        else:
            try:
                threshold = float(
                    input("CLIP similarity threshold? [0.98]: ") or "0.98"
                )
            except ValueError:
                threshold = 0.98

        # Get operation
        print("\nOperations:")
        print("1. Find duplicates (show only)")
        print("2. Remove duplicates")
        print("3. Move duplicates to separate folder")
        print("4. Copy duplicates to separate folder")
        op_choice = input("Select operation [1]: ").strip() or "1"
        if op_choice == "1":
            visual_dedup_workflow(
                hq_folder=hq,
                lq_folder=lq,
                single_folder=folder,
                method=method,
                max_images=max_images,
                threshold=threshold,
                operation="find",
            )
        elif op_choice == "2":
            visual_dedup_workflow(
                hq_folder=hq,
                lq_folder=lq,
                single_folder=folder,
                method=method,
                max_images=max_images,
                threshold=threshold,
                operation="remove",
            )
        elif op_choice == "3":
            dest_hq = get_path_with_history("Enter destination HQ folder: ")
            dest_lq = (
                get_path_with_history("Enter destination LQ folder: ") if lq else None
            )
            visual_dedup_workflow(
                hq_folder=hq,
                lq_folder=lq,
                single_folder=folder,
                method=method,
                max_images=max_images,
                threshold=threshold,
                operation="move",
                dest_hq=dest_hq,
                dest_lq=dest_lq,
            )
        elif op_choice == "4":
            dest_hq = get_path_with_history("Enter destination HQ folder: ")
            dest_lq = (
                get_path_with_history("Enter destination LQ folder: ") if lq else None
            )
            visual_dedup_workflow(
                hq_folder=hq,
                lq_folder=lq,
                single_folder=folder,
                method=method,
                max_images=max_images,
                threshold=threshold,
                operation="copy",
                dest_hq=dest_hq,
                dest_lq=dest_lq,
            )
        else:
            print_warning("Invalid operation selected.")
            continue
        print_prompt("\n⏸️ Press Enter to return to the Visual Deduplication menu...")
        input()


# Register a static menu for favorites
visual_dedup_menu.__menu_options__ = {
    "1": ("Run Visual Deduplication Workflow", visual_dedup_menu),
    "0": ("Back to Main Menu", None),
}
