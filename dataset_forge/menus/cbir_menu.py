from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_warning,
    print_prompt,
    print_info,
    print_section,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.input_utils import get_path_with_history


def cbir_menu():
    """
    Content-Based Image Retrieval (CBIR) for Duplicates - Semantic Duplicate Detection
    Uses deep learning embeddings (CLIP, ResNet, VGG) to find conceptually similar images.
    """
    while True:
        print_header(
            "🧠 CBIR (Semantic Duplicate Detection) - Input/Output Selection",
            color=Mocha.yellow,
        )
        print_info("1. HQ/LQ parent_path workflow")
        print_info("2. Single-folder workflow")
        print_info("0. Return to previous menu")
        choice = input("Select workflow: ").strip()
        if choice == "0" or choice == "":
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
            "🧠 CBIR (Semantic Duplicate Detection) - Model Selection",
            color=Mocha.yellow,
        )
        print_info("")
        print_info("Select embedding model:")
        print_info("1. CLIP (semantic, recommended)")
        print_info("2. ResNet (classic CNN)")
        print_info("3. VGG (classic CNN)")
        model_choice = input("Model [1]: ").strip() or "1"
        if model_choice == "2":
            model = "resnet"
        elif model_choice == "3":
            model = "vgg"
        else:
            model = "clip"
        try:
            max_images = int(input("Max images to check? [100]: ") or "100")
        except ValueError:
            max_images = 100
        try:
            threshold = float(input("Similarity threshold? [0.98]: ") or "0.98")
        except ValueError:
            threshold = 0.98
        print_info("")
        print_info("Operations:")
        print_info("1. Find duplicates (show only)")
        print_info("2. Remove duplicates")
        print_info("3. Move duplicates to separate folder")
        print_info("4. Copy duplicates to separate folder")
        op_choice = input("Select operation [1]: ").strip() or "1"
        # Determine metric
        if model == "clip":
            metric = "cosine"
        else:
            metric = "cosine"  # ResNet/VGG: cosine is default, can add option later
        print_section("CBIR Progress", color=Mocha.yellow)
        # Call CBIR workflow
        from dataset_forge.actions.cbir_actions import cbir_workflow

        if op_choice == "1":
            results = cbir_workflow(
                folder=folder,
                hq_folder=hq,
                lq_folder=lq,
                model_name=model,
                threshold=threshold,
                max_images=max_images,
                metric=metric,
                operation="find",
            )
            # Display results
            for path, groups in results.items():
                print_header(f"Results for {path}", color=Mocha.green)
                if not groups:
                    print_info("No duplicate groups found.")
                for i, group in enumerate(groups, 1):
                    print_info(f"Group {i} ({len(group)} images):")
                    for img in group:
                        print_info(f"  {img}")
        elif op_choice == "2":
            confirm = (
                input(
                    "Are you sure you want to remove all but one image in each group? (y/N): "
                )
                .strip()
                .lower()
            )
            if confirm == "y":
                results = cbir_workflow(
                    folder=folder,
                    hq_folder=hq,
                    lq_folder=lq,
                    model_name=model,
                    threshold=threshold,
                    max_images=max_images,
                    metric=metric,
                    operation="remove",
                    dry_run=False,
                )
                for path, removed in results.items():
                    print_header(f"Removed from {path}", color=Mocha.red)
                    if not removed:
                        print_info("No files removed.")
                    for img in removed:
                        print_info(f"  Removed: {img}")
            else:
                print_info("Remove operation cancelled.")
        elif op_choice == "3":
            dest_dir = get_path_with_history(
                "Enter destination folder for moved duplicates:"
            )
            results = cbir_workflow(
                folder=folder,
                hq_folder=hq,
                lq_folder=lq,
                model_name=model,
                threshold=threshold,
                max_images=max_images,
                metric=metric,
                operation="move",
                dest_dir=dest_dir,
                dry_run=False,
            )
            for path, moved in results.items():
                print_header(f"Moved from {path}", color=Mocha.yellow)
                if not moved:
                    print_info("No files moved.")
                for msg in moved:
                    print_info(f"  {msg}")
        elif op_choice == "4":
            dest_dir = get_path_with_history(
                "Enter destination folder for copied duplicates:"
            )
            results = cbir_workflow(
                folder=folder,
                hq_folder=hq,
                lq_folder=lq,
                model_name=model,
                threshold=threshold,
                max_images=max_images,
                metric=metric,
                operation="copy",
                dest_dir=dest_dir,
                dry_run=False,
            )
            for path, copied in results.items():
                print_header(f"Copied from {path}", color=Mocha.blue)
                if not copied:
                    print_info("No files copied.")
                for msg in copied:
                    print_info(f"  {msg}")
        else:
            print_warning("Invalid operation selected.")
        # At the end of the workflow, after all processing:
        print_prompt("\n⏸️ Press Enter to return to the CBIR menu...")
        input()
