import os
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
    print_prompt,
    print_section,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.progress_utils import tqdm


def correct_hq_lq_pairing_menu():
    from dataset_forge.actions.comparison_actions import compare_folders_menu
    from dataset_forge.actions.analysis_actions import (
        find_misaligned_images,
        test_hq_lq_scale,
    )
    from dataset_forge.actions.transform_actions import downsample_images_menu
    from dataset_forge.actions.correct_hq_lq_pairing_actions import (
        fuzzy_hq_lq_pairing_logic,
    )

    print_header(
        "🔗 Correct/Create HQ LQ Pairing - Input/Output Selection", color=Mocha.lavender
    )
    print_info(
        "This tool helps you pair HQ and LQ folders, check alignment, test scale, and correct scale if needed.\n"
    )

    # Step 1: Get HQ and LQ folder paths
    hq_folder = input("Enter path to HQ folder: ").strip()
    lq_folder = input("Enter path to LQ folder: ").strip()
    if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
        print_error("Both HQ and LQ paths must be valid directories.")
        return

    # Step 2: Get desired scale
    while True:
        try:
            desired_scale = float(
                input("Enter desired HQ/LQ scale (e.g., 2.0 for 2x): ").strip()
            )
            if desired_scale > 0:
                break
            else:
                print_error("Scale must be positive.")
        except ValueError:
            print_error("Invalid input. Please enter a number.")

    print_section("HQ/LQ Pairing Progress", color=Mocha.lavender)
    print_info("\nStep 1: Comparing folders for missing files...")
    compare_folders_menu()

    print_info("\nStep 2: Finding misaligned images (phase correlation)...")
    find_misaligned_images(hq_folder, lq_folder)

    print_info("\nStep 3: Testing current HQ/LQ scale...")
    test_hq_lq_scale(hq_folder, lq_folder)

    print_info("\nStep 4: Correcting scale if needed...")
    # Add scale correction logic here if needed
    print_info("Scale correction not yet implemented.")

    print_info("\nStep 5: Fuzzy pairing (if needed)...")
    fuzzy_hq_lq_pairing_logic(hq_folder, lq_folder)

    print_success("HQ/LQ pairing process completed!")
    input("\nPress Enter to return to the menu...")


# Register a static menu for favorites
correct_hq_lq_pairing_menu.__menu_options__ = {
    "1": ("Run HQ/LQ Pairing Correction Workflow", correct_hq_lq_pairing_menu),
    "0": ("Back to Main Menu", None),
}


def fuzzy_hq_lq_pairing_menu():
    from dataset_forge.utils.printing import print_header, print_section
    from dataset_forge.utils.color import Mocha

    print_header(
        "🔗 Automatic HQ/LQ Pairing (Fuzzy Matching) - Input/Output Selection",
        color=Mocha.lavender,
    )
    print_info(
        "This tool uses perceptual hashes or embeddings to pair HQ and LQ images even if filenames differ.\n"
    )
    hq_folder = input("Enter path to HQ folder: ").strip()
    lq_folder = input("Enter path to LQ folder: ").strip()
    if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
        print_error("Both HQ and LQ paths must be valid directories.")
        return
    print_section("Fuzzy HQ/LQ Pairing Progress", color=Mocha.lavender)
    print_info("\nRunning fuzzy HQ/LQ pairing... (progress bar will be shown)")
    pairs = fuzzy_hq_lq_pairing_logic(hq_folder, lq_folder)
    print_info(f"\nFound {len(pairs)} HQ/LQ pairs using fuzzy matching.")
    # TODO: Display results, allow user to review/save pairs
    input("\nPress Enter to return to the main menu...")


# Register a static menu for favorites
fuzzy_hq_lq_pairing_menu.__menu_options__ = {
    "1": ("Run Fuzzy HQ/LQ Pairing Workflow", fuzzy_hq_lq_pairing_menu),
    "0": ("Back to Main Menu", None),
}
