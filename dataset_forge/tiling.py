import os
from dataset_forge.io_utils import is_image_file
import cv2
from dataset_forge.common import get_file_operation_choice, get_destination_path
import numpy as np
import imageio
from PIL import Image, ImageEnhance, UnidentifiedImageError, ImageFont, ImageDraw
from tqdm import tqdm
import random

def tile_single_folder(folder_path):
    """Handle tiling for a single folder."""
    operation = get_file_operation_choice()
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path()
        if not dest_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(dest_dir, exist_ok=True)

    # Get tiling parameters
    tile_params = get_tiling_parameters()
    if not tile_params:
        return

    tile_images(folder_path, "", operation, dest_dir, **tile_params)


def get_tiling_parameters():
    """Get and validate tiling parameters from user."""
    try:
        while True:
            try:
                tile_size = int(input("Enter tile size (e.g., 512): ").strip())
                if tile_size > 0:
                    break
                print("Tile size must be positive.")
            except ValueError:
                print("Please enter a valid number.")

        while True:
            try:
                overlap = float(
                    input("Enter overlap fraction (0.0 to 0.5, default 0.0): ").strip()
                    or 0.0
                )
                if 0.0 <= overlap <= 0.5:
                    break
                print("Overlap must be between 0.0 and 0.5")
            except ValueError:
                print("Please enter a valid number.")

        while True:
            method = (
                input("Select tiling method (random/sequential/best): ").strip().lower()
            )
            if method in ["random", "sequential", "best"]:
                break
            print("Please enter 'random', 'sequential', or 'best'")

        tiles_per_image = None
        if method == "random":
            while True:
                try:
                    tiles_per_image = int(
                        input("Enter number of tiles per image (default 1): ").strip()
                        or 1
                    )
                    if tiles_per_image > 0:
                        break
                    print("Number of tiles must be positive.")
                except ValueError:
                    print("Please enter a valid number.")

        return {
            "tile_size": tile_size,
            "overlap": overlap,
            "method": method,
            "tiles_per_image": tiles_per_image,
        }
    except Exception as e:
        print(f"Error getting tiling parameters: {e}")
        return None


def tile_dataset_menu(default_hq_folder="", default_lq_folder=""):
    """Menu system for dataset tiling functionality."""
    print("\n" + "=" * 30)
    print("  Dataset Image Tiling")
    print("=" * 30)

    print("\nSelect Tiling Mode:")
    print("  1. Single Folder Tiling (Source/HQ dataset)")
    print("  2. HQ/LQ Dataset Pair Tiling")

    while True:
        mode = input("Enter mode (1 or 2): ").strip()
        if mode in ["1", "2"]:
            break
        print("Invalid choice. Please enter 1 or 2.")

    if mode == "1":
        # Single folder tiling
        folder_path = input("Enter path to folder containing images to tile: ").strip()
        if not os.path.isdir(folder_path):
            print("Invalid folder path.")
            return
        tile_single_folder(folder_path)

    else:  # mode == "2"
        print("\nHQ/LQ Dataset Tiling Options:")
        print("  1. Use current HQ/LQ folders")
        print("  2. Specify new HQ/LQ folder paths")

        while True:
            source = input("Enter choice (1 or 2): ").strip()
            if source in ["1", "2"]:
                break
            print("Invalid choice. Please enter 1 or 2.")

        hq_path = ""
        lq_path = ""

        if source == "1":
            if not default_hq_folder or not default_lq_folder:
                print("No HQ/LQ folders are currently set. Please use option 2.")
                return
            hq_path = default_hq_folder
            lq_path = default_lq_folder
        else:
            print("\nEnter paths for HQ/LQ folders:")
            hq_path = input("HQ folder path: ").strip()
            lq_path = input("LQ folder path: ").strip()
            if not (os.path.isdir(hq_path) and os.path.isdir(lq_path)):
                print("Invalid folder path(s).")
                return

        tile_hq_lq_dataset(hq_path, lq_path)


def tile_hq_lq_dataset(hq_folder, lq_folder):
    """Handle tiling for HQ/LQ dataset pairs with alignment preservation."""
    print("\n" + "=" * 30)
    print("  HQ/LQ Dataset Pair Tiling")
    print("=" * 30)

    operation = get_file_operation_choice()
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path()
        if not dest_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(os.path.join(dest_dir, "hq_tiles"), exist_ok=True)
        os.makedirs(os.path.join(dest_dir, "lq_tiles"), exist_ok=True)

    # Get tiling parameters (same parameters will be used for both HQ and LQ)
    tile_params = get_tiling_parameters()
    if not tile_params:
        return

    # Process the paired dataset
    processed_count, errors = tile_aligned_pairs(
        hq_folder, lq_folder, operation, dest_dir, **tile_params
    )

    print("\n" + "-" * 30)
    print("  HQ/LQ Dataset Tiling Summary")
    print("-" * 30)
    print(f"Total tile pairs created: {processed_count}")
    if errors:
        print("\nErrors encountered:")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)


def tile_aligned_pairs(hq_folder, lq_folder, operation, dest_dir, **params):
    """Process HQ and LQ pairs maintaining alignment and scale."""
    hq_files = sorted([f for f in os.listdir(hq_folder) if is_image_file(f)])
    lq_files = sorted([f for f in os.listdir(lq_folder) if is_image_file(f)])
    matching_pairs = [(f, f) for f in hq_files if f in lq_files]

    if not matching_pairs:
        print("No matching HQ/LQ pairs found.")
        return 0, []

    print(f"\nProcessing {len(matching_pairs)} HQ/LQ pairs...")
    processed_pairs = 0
    errors = []

    for hq_file, lq_file in tqdm(matching_pairs, desc="Processing Pairs"):
        try:
            # Load images using PIL for better format support
            hq_img = Image.open(os.path.join(hq_folder, hq_file))
            lq_img = Image.open(os.path.join(lq_folder, lq_file))

            # Convert to numpy arrays for processing
            hq_array = np.array(hq_img)
            lq_array = np.array(lq_img)

            # Get dimensions and calculate scale
            h_hq, w_hq = hq_array.shape[:2]
            h_lq, w_lq = lq_array.shape[:2]
            scale_x = w_hq / w_lq
            scale_y = h_hq / h_lq

            # Verify scale is consistent
            if abs(scale_x - scale_y) > 0.01:  # Allow small difference
                errors.append(
                    f"Inconsistent scale in {hq_file}: x={scale_x:.2f}, y={scale_y:.2f}"
                )
                continue

            scale = (scale_x + scale_y) / 2  # Use average scale
            print(f"Processing pair with scale factor: {scale:.2f}x")

            # Calculate tile sizes
            lq_tile_size = params["tile_size"]
            hq_tile_size = int(lq_tile_size * scale)

            # Ensure tile sizes don't exceed image dimensions
            if lq_tile_size > min(h_lq, w_lq) or hq_tile_size > min(h_hq, w_hq):
                max_lq_size = min(h_lq, w_lq)
                lq_tile_size = max_lq_size
                hq_tile_size = int(max_lq_size * scale)
                print(
                    f"Warning: Adjusting tile size to {lq_tile_size} (LQ) and {hq_tile_size} (HQ) for pair {hq_file}"
                )

            # Calculate stride with overlap
            lq_stride = int(lq_tile_size * (1 - params["overlap"]))
            hq_stride = int(hq_tile_size * (1 - params["overlap"]))

            # Generate valid positions
            valid_positions = []
            for y in range(0, h_lq - lq_tile_size + 1, lq_stride):
                for x in range(0, w_lq - lq_tile_size + 1, lq_stride):
                    # Calculate corresponding HQ coordinates
                    hq_x = int(x * scale)
                    hq_y = int(y * scale)

                    # Verify HQ coordinates are within bounds
                    if hq_x + hq_tile_size <= w_hq and hq_y + hq_tile_size <= h_hq:
                        lq_tile = lq_array[y : y + lq_tile_size, x : x + lq_tile_size]
                        hq_tile = hq_array[
                            hq_y : hq_y + hq_tile_size, hq_x : hq_x + hq_tile_size
                        ]

                        score = None
                        if params["method"] == "best":
                            # Calculate score based on both tiles
                            lq_gray = (
                                cv2.cvtColor(lq_tile, cv2.COLOR_RGB2GRAY)
                                if len(lq_tile.shape) > 2
                                else lq_tile
                            )
                            hq_gray = (
                                cv2.cvtColor(hq_tile, cv2.COLOR_RGB2GRAY)
                                if len(hq_tile.shape) > 2
                                else hq_tile
                            )
                            score = (
                                cv2.Laplacian(lq_gray, cv2.CV_64F).var()
                                + cv2.Laplacian(hq_gray, cv2.CV_64F).var()
                            ) / 2

                        valid_positions.append((x, y, hq_x, hq_y, score))

            # Select positions based on method
            selected_positions = []
            if params["method"] == "best":
                valid_positions.sort(key=lambda x: x[4], reverse=True)
                selected_positions = (
                    valid_positions[: params["tiles_per_image"]]
                    if params["tiles_per_image"]
                    else valid_positions
                )
            elif params["method"] == "random" and params["tiles_per_image"]:
                selected_positions = random.sample(
                    valid_positions,
                    min(params["tiles_per_image"], len(valid_positions)),
                )
            else:  # sequential
                selected_positions = valid_positions

            # Extract and save tiles
            base_name = os.path.splitext(hq_file)[0]
            for i, (lq_x, lq_y, hq_x, hq_y, _) in enumerate(selected_positions):
                # Extract tiles maintaining original scales
                lq_tile = lq_array[
                    lq_y : lq_y + lq_tile_size, lq_x : lq_x + lq_tile_size
                ]
                hq_tile = hq_array[
                    hq_y : hq_y + hq_tile_size, hq_x : hq_x + hq_tile_size
                ]

                # Create filenames that indicate the scale relationship
                tile_suffix = f"_tile_{i}_x{lq_x}_y{lq_y}_scale{scale:.1f}.png"

                if operation == "inplace":
                    hq_path = os.path.join(hq_folder, base_name + tile_suffix)
                    lq_path = os.path.join(lq_folder, base_name + tile_suffix)
                else:
                    hq_path = os.path.join(
                        dest_dir, "hq_tiles", base_name + tile_suffix
                    )
                    lq_path = os.path.join(
                        dest_dir, "lq_tiles", base_name + tile_suffix
                    )

                # Save tiles maintaining their original scales
                Image.fromarray(hq_tile).save(hq_path, "PNG")
                Image.fromarray(lq_tile).save(lq_path, "PNG")
                processed_pairs += 1

            hq_img.close()
            lq_img.close()

        except Exception as e:
            errors.append(f"Error processing pair {hq_file}: {str(e)}")

    return processed_pairs, errors


def tile_images(
    folder_path,
    folder_type="",
    operation="inplace",
    dest_dir="",
    tile_size=None,
    overlap=None,
    method=None,
    tiles_per_image=None,
):
    """Create tiles from images with various options."""
    print("\n" + "=" * 30)
    print(f"  Image Tiling {folder_type}")  # Add folder type to header
    print("=" * 30)

    # Only prompt for missing parameters
    if not operation:
        operation = get_file_operation_choice()
    if not dest_dir and operation != "inplace":
        dest_dir = get_destination_path()
        if not dest_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(dest_dir, exist_ok=True)
    if tile_size is None:
        while True:
            try:
                tile_size = int(input("Enter tile size (e.g., 512): ").strip())
                if tile_size > 0:
                    break
                print("Tile size must be positive.")
            except ValueError:
                print("Please enter a valid number.")
    if overlap is None:
        while True:
            try:
                overlap = float(
                    input("Enter overlap fraction (0.0 to 0.5, default 0.0): ").strip()
                    or 0.0
                )
                if 0.0 <= overlap <= 0.5:
                    break
                print("Overlap must be between 0.0 and 0.5")
            except ValueError:
                print("Please enter a valid number.")
    if method is None:
        while True:
            method = (
                input("Select tiling method (random/sequential/best): ").strip().lower()
            )
            if method in ["random", "sequential", "best"]:
                break
            print("Please enter 'random', 'sequential', or 'best'")
    if method == "random" and tiles_per_image is None:
        while True:
            try:
                tiles_per_image = int(
                    input("Enter number of tiles per image (default 1): ").strip() or 1
                )
                if tiles_per_image > 0:
                    break
                print("Number of tiles must be positive.")
            except ValueError:
                print("Please enter a valid number.")

    def extract_tiles(img, size, overlap_frac):
        h, w = img.shape[:2]
        stride = int(size * (1 - overlap_frac))
        tiles = []
        for y in range(0, h - size + 1, stride):
            for x in range(0, w - size + 1, stride):
                tile = img[y : y + size, x : x + size]
                if method == "best":
                    gray = (
                        cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
                        if len(tile.shape) > 2
                        else tile
                    )
                    score = cv2.Laplacian(gray, cv2.CV_64F).var()
                    tiles.append((tile, score, (x, y)))
                else:
                    tiles.append((tile, None, (x, y)))
        return tiles

    image_files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
    ]

    processed_count = 0
    errors = []

    for filename in tqdm(image_files, desc="Processing Images"):
        try:
            img_path = os.path.join(folder_path, filename)
            img = cv2.imread(img_path)
            if img is None:
                errors.append(f"Could not read {filename}")
                continue

            tiles = extract_tiles(img, tile_size, overlap)

            if method == "best":
                tiles.sort(key=lambda x: x[1], reverse=True)
                selected_tiles = tiles[:tiles_per_image] if tiles_per_image else tiles
            elif method == "random" and tiles_per_image:
                if len(tiles) > tiles_per_image:
                    selected_tiles = random.sample(tiles, tiles_per_image)
                else:
                    selected_tiles = tiles
            else:  # sequential
                selected_tiles = tiles

            base_name = os.path.splitext(filename)[0]
            for i, (tile, _, pos) in enumerate(selected_tiles):
                if operation == "inplace":
                    tile_filename = f"{base_name}_tile_{i}_x{pos[0]}_y{pos[1]}.png"
                    tile_path = os.path.join(folder_path, tile_filename)
                else:
                    tile_filename = f"{base_name}_tile_{i}_x{pos[0]}_y{pos[1]}.png"
                    tile_path = os.path.join(dest_dir, tile_filename)

                cv2.imwrite(tile_path, tile)
                processed_count += 1

        except Exception as e:
            errors.append(f"Error processing {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Image Tiling Summary")
    print("-" * 30)
    print(f"Total tiles created: {processed_count}")
    if errors:
        print("\nErrors encountered:")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(
                f"  ... and {len(errors) - 5} more issues (check log if detailed logging was added)."
            )
    print("-" * 30)
    print("=" * 30)
