import os
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_error,
    print_prompt,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.actions.comparison_actions import compare_folders_menu
from dataset_forge.actions.analysis_actions import (
    find_misaligned_images,
    test_hq_lq_scale,
)
from dataset_forge.actions.transform_actions import downsample_images_menu
from tqdm import tqdm
from dataset_forge.actions.correct_hq_lq_pairing_actions import (
    fuzzy_hq_lq_pairing_logic,
)


def correct_hq_lq_pairing_menu():
    print_header("Correct/Create HQ LQ Pairing", color=Mocha.lavender)
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

    print_info("\nStep 1: Comparing folders for missing files...")
    compare_folders_menu()

    print_info("\nStep 2: Finding misaligned images (phase correlation)...")
    find_misaligned_images(hq_folder, lq_folder)

    print_info("\nStep 3: Testing current HQ/LQ scale...")
    test_hq_lq_scale(hq_folder, lq_folder)

    print_info("\nStep 4: Correcting scale if needed...")
    print_info("Suggesting downscaling LQ folder to match desired scale. (Recommended)")
    print_info("If you want to downscale HQ instead, use a separate tool.")
    choice = (
        input("Proceed to downscale LQ folder to match desired scale? (y/n): ")
        .strip()
        .lower()
    )
    if choice != "y":
        print_info("Scale correction skipped.")
        return

    # Analyze and report aspect ratios before asking how to handle differences
    print_info("\nAnalyzing aspect ratios of HQ and LQ pairs...")
    aspect_tolerance = 0.01
    matching_aspect = 0
    nonmatching_aspect = 0
    aspect_details = []
    from PIL import Image, ImageOps
    from dataset_forge.image_ops import get_image_size

    lq_files = {
        f for f in os.listdir(lq_folder) if os.path.isfile(os.path.join(lq_folder, f))
    }
    hq_files = {
        f for f in os.listdir(hq_folder) if os.path.isfile(os.path.join(hq_folder, f))
    }
    matching_files = sorted(hq_files & lq_files)
    for fname in matching_files:
        hq_path = os.path.join(hq_folder, fname)
        lq_path = os.path.join(lq_folder, fname)
        try:
            hq_w, hq_h = get_image_size(hq_path)
            lq_w, lq_h = get_image_size(lq_path)
            hq_aspect = hq_w / hq_h if hq_h != 0 else 0
            lq_aspect = lq_w / lq_h if lq_h != 0 else 0
            if abs(hq_aspect - lq_aspect) < aspect_tolerance:
                matching_aspect += 1
            else:
                nonmatching_aspect += 1
            aspect_details.append((fname, hq_aspect, lq_aspect))
        except Exception as e:
            print_error(f"Failed to get aspect ratio for {fname}: {e}")
    print_info(f"\nAspect ratio analysis for {len(matching_files)} pairs:")
    print_info(f"  Matching aspect ratio pairs: {matching_aspect}")
    print_info(f"  Non-matching aspect ratio pairs: {nonmatching_aspect}")
    if nonmatching_aspect > 0:
        print_info("  Example non-matching pairs (up to 5):")
        shown = 0
        for fname, hq_aspect, lq_aspect in aspect_details:
            if abs(hq_aspect - lq_aspect) >= aspect_tolerance:
                print_info(
                    f"    {fname}: HQ aspect {hq_aspect:.4f}, LQ aspect {lq_aspect:.4f}"
                )
                shown += 1
                if shown >= 5:
                    break

    # Ask user how to handle aspect ratio differences
    print_info(
        "\nHow should aspect ratio differences be handled when resizing LQ images?"
    )
    print_info("1. Just resize (may distort aspect ratio) [default]")
    print_info("2. Crop to fit (center crop to target size)")
    print_info("3. Pad to fit (add black bars to target size)")
    aspect_mode = input("Enter 1, 2, or 3: ").strip()
    if aspect_mode not in {"2", "3"}:
        aspect_mode = "1"

    # Downscaling using per-image HQ/scale as target
    print_info("\nResizing LQ images to match HQ/scale dimensions for each pair...")
    out_lq_folder = os.path.join(lq_folder, "downscaled")
    os.makedirs(out_lq_folder, exist_ok=True)

    lq_files = {
        f for f in os.listdir(lq_folder) if os.path.isfile(os.path.join(lq_folder, f))
    }
    hq_files = {
        f for f in os.listdir(hq_folder) if os.path.isfile(os.path.join(hq_folder, f))
    }
    matching_files = sorted(hq_files & lq_files)
    processed = 0
    failed = 0
    for fname in tqdm(matching_files, desc="Resizing LQ images"):
        hq_path = os.path.join(hq_folder, fname)
        lq_path = os.path.join(lq_folder, fname)
        hq_ext = os.path.splitext(fname)[1]
        out_path = os.path.join(out_lq_folder, os.path.splitext(fname)[0] + hq_ext)
        try:
            hq_w, hq_h = get_image_size(hq_path)
            target_w = int(round(hq_w / desired_scale))
            target_h = int(round(hq_h / desired_scale))
            with Image.open(lq_path) as img:
                if aspect_mode == "1":
                    # Just resize (may distort)
                    resized = img.resize((target_w, target_h), Image.LANCZOS)
                elif aspect_mode == "2":
                    # Crop to fit (center crop, then resize)
                    src_w, src_h = img.size
                    src_aspect = src_w / src_h
                    tgt_aspect = target_w / target_h
                    if src_aspect > tgt_aspect:
                        # Crop width
                        new_w = int(src_h * tgt_aspect)
                        left = (src_w - new_w) // 2
                        img_cropped = img.crop((left, 0, left + new_w, src_h))
                    else:
                        # Crop height
                        new_h = int(src_w / tgt_aspect)
                        top = (src_h - new_h) // 2
                        img_cropped = img.crop((0, top, src_w, top + new_h))
                    resized = img_cropped.resize((target_w, target_h), Image.LANCZOS)
                elif aspect_mode == "3":
                    # Pad to fit (letterbox/pillarbox)
                    src_w, src_h = img.size
                    src_aspect = src_w / src_h
                    tgt_aspect = target_w / target_h
                    if src_aspect > tgt_aspect:
                        # Pad height
                        new_h = int(src_w / tgt_aspect)
                        pad_top = (new_h - src_h) // 2
                        pad_bottom = new_h - src_h - pad_top
                        padding = (0, pad_top, 0, pad_bottom)
                    else:
                        # Pad width
                        new_w = int(src_h * tgt_aspect)
                        pad_left = (new_w - src_w) // 2
                        pad_right = new_w - src_w - pad_left
                        padding = (pad_left, 0, pad_right, 0)
                    img_padded = ImageOps.expand(img, padding, fill=(0, 0, 0))
                    resized = img_padded.resize((target_w, target_h), Image.LANCZOS)
                else:
                    resized = img.resize((target_w, target_h), Image.LANCZOS)
                # Save with the same extension as HQ
                save_kwargs = {}
                if hq_ext.lower() in [".jpg", ".jpeg"]:
                    save_kwargs["quality"] = 95
                    save_format = "JPEG"
                elif hq_ext.lower() == ".png":
                    save_format = "PNG"
                elif hq_ext.lower() == ".webp":
                    save_format = "WEBP"
                else:
                    save_format = None
                if save_format:
                    resized.save(out_path, save_format, **save_kwargs)
                else:
                    resized.save(out_path)
            processed += 1
        except Exception as e:
            print_error(f"Failed to resize {fname}: {e}")
            failed += 1
    print_success(f"LQ resizing complete. Processed: {processed}, Failed: {failed}")

    print_info("\nStep 5: Testing HQ/LQ scale again after correction...")
    test_hq_lq_scale(hq_folder, out_lq_folder)

    print_success("\nHQ/LQ pairing correction workflow complete!")


def fuzzy_hq_lq_pairing_menu():
    print_header("Automatic HQ/LQ Pairing (Fuzzy Matching)", color=Mocha.lavender)
    print_info(
        "This tool uses perceptual hashes or embeddings to pair HQ and LQ images even if filenames differ.\n"
    )
    hq_folder = input("Enter path to HQ folder: ").strip()
    lq_folder = input("Enter path to LQ folder: ").strip()
    if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
        print_error("Both HQ and LQ paths must be valid directories.")
        return
    print_info("\nRunning fuzzy HQ/LQ pairing... (progress bar will be shown)")
    pairs = fuzzy_hq_lq_pairing_logic(hq_folder, lq_folder)
    print_info(f"\nFound {len(pairs)} HQ/LQ pairs using fuzzy matching.")
    # TODO: Display results, allow user to review/save pairs
    input("\nPress Enter to return to the main menu...")
