import os
from dataset_forge.io_utils import is_image_file
from dataset_forge.utils.input_utils import get_destination_path
from PIL import Image, ImageFont, ImageDraw
import random
import numpy as np
from tqdm import tqdm
import gc
import torch
from dataset_forge import folder_compare


def release_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def create_comparison_images(hq_folder, lq_folder):
    """Create side-by-side comparison images of HQ/LQ pairs."""
    print("\n" + "=" * 30)
    print("  Creating HQ/LQ Comparison Images")
    print("=" * 30)
    output_dir = get_destination_path()
    if not output_dir:
        print("Operation aborted as no destination path was provided.")
        return
    os.makedirs(output_dir, exist_ok=True)
    lq_label = "LQ"
    hq_label = "HQ"
    label_color = (255, 255, 255)
    stroke_color = (0, 0, 0)
    stroke_width = 1
    font_size = 15
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
        except IOError:
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size
                )
            except IOError:
                print("Warning: Could not load TrueType fonts. Using default PIL font.")
                font = ImageFont.load_default()
    hq_files = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    available_pairs = [
        f for f in hq_files if os.path.isfile(os.path.join(lq_folder, f))
    ]
    if not available_pairs:
        print("No matching HQ/LQ pairs found.")
        return
    while True:
        try:
            num_pairs_str = input("Enter the number of pairs to compare: ").strip()
            num_pairs = int(num_pairs_str)
            if num_pairs <= 0:
                print("Please enter a positive number.")
            elif num_pairs > len(available_pairs):
                print(
                    f"Only {len(available_pairs)} pairs available. Will use all of them."
                )
                num_pairs = len(available_pairs)
                break
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")
    selected_pairs = random.sample(available_pairs, num_pairs)
    processed_count = 0
    errors = []

    def draw_text_with_stroke(
        draw, position, text, font, fill, stroke_fill, stroke_width
    ):
        x, y = position
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill)
        draw.text((x, y), text, font=font, fill=fill)

    for filename in tqdm(selected_pairs, desc="Creating Comparisons"):
        try:
            lq_path = os.path.join(lq_folder, filename)
            hq_path = os.path.join(hq_folder, filename)
            output_path = os.path.join(output_dir, filename)
            lq_img = Image.open(lq_path).convert("RGB")
            hq_img = Image.open(hq_path).convert("RGB")
            target_size = (
                min(lq_img.size[0], hq_img.size[0]),
                min(lq_img.size[1], hq_img.size[1]),
            )
            lq_img = lq_img.resize(target_size, Image.Resampling.LANCZOS)
            hq_img = hq_img.resize(target_size, Image.Resampling.LANCZOS)
            composite_img = Image.new(
                "RGB", (target_size[0], target_size[1]), (255, 255, 255)
            )
            composite_img.paste(lq_img, (0, 0))
            composite_img.paste(
                hq_img,
                (0, 0),
                mask=hq_img.split()[3] if hq_img.mode == "RGBA" else None,
            )
            draw = ImageDraw.Draw(composite_img)
            text_padding = 5
            draw_text_with_stroke(
                draw,
                (text_padding, text_padding),
                lq_label,
                font,
                label_color,
                stroke_color,
                stroke_width,
            )
            draw_text_with_stroke(
                draw,
                (
                    target_size[0] - text_padding - font.getsize(hq_label)[0],
                    text_padding,
                ),
                hq_label,
                font,
                label_color,
                stroke_color,
                stroke_width,
            )
            composite_img.save(output_path, quality=100, subsampling=0)
            processed_count += 1
        except Exception as e:
            errors.append(f"Error processing {filename}: {e}")
    print("\n" + "-" * 30)
    print(" Create Comparisons Summary")
    print("-" * 30)
    print(f"Total pairs to process: {num_pairs}")
    print(f"Successfully created: {processed_count} comparisons")
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)
    release_memory()


def create_gif_comparison(hq_folder, lq_folder):
    """Create animated GIF/WebP comparisons of HQ/LQ pairs with transition effects."""
    print("\n" + "=" * 30)
    print("  Creating HQ/LQ Animated Comparisons")
    print("=" * 30)

    def get_folder_with_default(prompt, default):
        val = input(f"{prompt} [default: {default}]: ").strip()
        return val if val else default

    hq_folder = get_folder_with_default("Enter HQ folder path", hq_folder)
    lq_folder = get_folder_with_default("Enter LQ folder path", lq_folder)
    # TODO: Paste the rest of the logic from comparison.py for GIF/WebP creation
    print("[TODO] Full GIF/WebP comparison logic not yet migrated.")
    pass


def compare_folders_menu():
    """Compare two folders and report missing files in each."""
    print("\n=== Compare Folders ===")
    folder1 = input("Enter path to first folder: ").strip()
    folder2 = input("Enter path to second folder: ").strip()
    if not os.path.isdir(folder1) or not os.path.isdir(folder2):
        print("Both paths must be valid directories.")
        return
    ext_input = input(
        "Filter by file extensions (comma-separated, blank for all): "
    ).strip()
    extensions = (
        [
            (
                e.strip().lower()
                if e.strip().startswith(".")
                else "." + e.strip().lower()
            )
            for e in ext_input.split(",")
            if e.strip()
        ]
        if ext_input
        else None
    )
    missing1, missing2 = folder_compare.compare_folders(folder1, folder2, extensions)
    if not missing1 and not missing2:
        print(
            "Both folders contain the same files"
            + (f" (filtered by {', '.join(extensions)})" if extensions else "")
            + "."
        )
    else:
        if missing1:
            print(f"Files missing in {folder1}:")
            for f in missing1:
                print(f"  {f}")
        if missing2:
            print(f"Files missing in {folder2}:")
            for f in missing2:
                print(f"  {f}")
