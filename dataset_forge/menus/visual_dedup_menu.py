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
        print_info("1. HQ/LQ parent_path workflow")
        print_info("2. Single-folder workflow")
        print_info("0. Return to main menu")
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
        print_info("\nSelect method:")
        print_info("1. CLIP Embedding (fast, semantic)")
        print_info("2. LPIPS (slow, perceptual)")
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
            results = visual_dedup_workflow(
                hq_path=hq,
                lq_path=lq,
                single_folder_path=folder,
                method=method,
                threshold=threshold,
                max_images=max_images,
            )
        except Exception as e:
            print_warning(f"Error during visual deduplication: {e}")
            results = None
        # Post-processing: Offer move/copy/delete if duplicates found
        if results:
            # Flatten all groups from all folders
            all_groups = []
            for group_list in results.values():
                all_groups.extend(group_list)
            if all_groups:
                print_section("Duplicate Groups Found", color=Mocha.peach)
                print_info(f"Found {len(all_groups)} duplicate groups.")
                print_info("What would you like to do with the duplicates?")
                print_info("[1] Move to folder")
                print_info("[2] Copy to folder")
                print_info("[3] Delete in-place")
                print_info("[0] Do nothing")
                action = input("Select action: ").strip()
                if action == "1":
                    dest = get_path_with_history(
                        "Enter destination folder for moved duplicates",
                        is_destination=True,
                    )
                    moved = move_duplicate_groups(all_groups, dest, dry_run=False)
                    print_info(f"Moved {len(moved)} files to {dest}")
                elif action == "2":
                    dest = get_path_with_history(
                        "Enter destination folder for copied duplicates",
                        is_destination=True,
                    )
                    copied = copy_duplicate_groups(all_groups, dest, dry_run=False)
                    print_info(f"Copied {len(copied)} files to {dest}")
                elif action == "3":
                    removed = remove_duplicate_groups(all_groups, dry_run=False)
                    print_info(f"Deleted {len(removed)} duplicate files in-place.")
                else:
                    print_info("No action taken. Duplicates remain in place.")
            else:
                print_info("No duplicate groups found.")
        else:
            print_warning("No results returned from deduplication workflow.")
        print_prompt("\n⏸️ Press Enter to return to the Visual Deduplication menu...")
        input()


# Register a static menu for favorites
visual_dedup_menu.__menu_options__ = {
    "1": ("Run Visual Deduplication Workflow", visual_dedup_menu),
    "0": ("Back to Main Menu", None),
}
