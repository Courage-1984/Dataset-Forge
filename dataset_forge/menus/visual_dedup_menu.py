from dataset_forge.actions.visual_dedup_actions import (
    visual_dedup_workflow,
    move_duplicate_groups,
    copy_duplicate_groups,
    remove_duplicate_groups,
)
from dataset_forge.utils.input_utils import get_path_with_history, get_folder_path
from dataset_forge.utils.printing import print_info, print_warning


def visual_dedup_menu():
    print("\n=== Visual Duplicate & Near-Duplicate Detection ===")
    print("1. HQ/LQ parent_path workflow")
    print("2. Single-folder workflow")
    print("0. Return to main menu")
    choice = input("Select workflow: ")
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
        return
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
            threshold = float(input("CLIP similarity threshold? [0.98]: ") or "0.98")
        except ValueError:
            threshold = 0.98

    # Get operation
    print("\nOperations:")
    print("1. Find duplicates (show only)")
    print("2. Remove duplicates")
    print("3. Move duplicates to separate folder")
    print("4. Copy duplicates to separate folder")

    op_choice = input("Select operation [1]: ").strip() or "1"
    operations = {"1": "find", "2": "remove", "3": "move", "4": "copy"}
    operation = operations.get(op_choice, "find")

    # Get additional parameters based on operation
    destination_dir = None
    dry_run = True

    if operation in ["remove", "move", "copy"]:
        confirm = (
            input("This will permanently modify files. Continue? (y/n) [n]: ")
            .strip()
            .lower()
            or "n"
        )
        if confirm == "y":
            dry_run = False
        else:
            print_warning("Operation cancelled.")
            return

    if operation in ["move", "copy"]:
        destination_dir = get_folder_path("Enter destination folder for duplicates: ")

    print_info("\nRunning visual deduplication... (this may take a while)")
    results = visual_dedup_workflow(
        hq_path=hq,
        lq_path=lq,
        single_folder_path=folder,
        method=method,
        threshold=threshold,
        max_images=max_images,
    )

    # Process results based on operation
    for key, groups in results.items():
        print(f"\nResults for {key}:")
        if not groups:
            print("No near-duplicates found.")
            continue

        total_duplicates = sum(
            len(group) - 1 for group in groups
        )  # -1 to exclude original
        print(
            f"Found {len(groups)} duplicate groups with {total_duplicates} total duplicate files."
        )

        if operation == "find":
            # Show duplicate groups
            for i, group in enumerate(groups, 1):
                print(f"\nGroup {i} ({len(group)} images):")
                print(f"  Original: {group[0]}")
                print(f"  Duplicates ({len(group) - 1}):")
                for path in group[1:]:
                    print(f"    - {path}")

        elif operation == "remove":
            removed_files = remove_duplicate_groups(groups, dry_run=dry_run)

        elif operation == "move":
            moved_files = move_duplicate_groups(
                groups, destination_dir, dry_run=dry_run
            )

        elif operation == "copy":
            copied_files = copy_duplicate_groups(
                groups, destination_dir, dry_run=dry_run
            )

    input("\nPress Enter to return to the main menu...")


# Register a static menu for favorites
visual_dedup_menu.__menu_options__ = {
    "1": ("Run Visual Deduplication Workflow", visual_dedup_menu),
    "0": ("Back to Main Menu", None),
}
