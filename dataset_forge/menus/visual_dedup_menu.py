from dataset_forge.actions.visual_dedup_actions import visual_dedup_workflow
from dataset_forge.utils.input_utils import get_path_with_history
from dataset_forge.utils.printing import print_info


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
    print_info("\nRunning visual deduplication... (this may take a while)")
    results = visual_dedup_workflow(
        hq_path=hq,
        lq_path=lq,
        single_folder_path=folder,
        method=method,
        threshold=threshold,
        max_images=max_images,
    )
    for key, groups in results.items():
        print(f"\nResults for {key}:")
        if not groups:
            print("No near-duplicates found.")
        for i, group in enumerate(groups, 1):
            print(f"Group {i} ({len(group)} images):")
            for path in group:
                print(f"  {path}")
    input("\nPress Enter to return to the main menu...")
