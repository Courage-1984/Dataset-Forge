from dataset_forge.dataset_ops import DatasetCombiner
from dataset_forge.de_dupe import (
    compute_hashes,
    find_duplicates,
    find_near_duplicates,
    align_and_operate_on_pairs,
)
from dataset_forge.batch_rename import (
    batch_rename_single_folder,
    batch_rename_hq_lq_folders,
)
from dataset_forge.frames import extract_frames_menu
from dataset_forge.orientation_organizer import (
    organize_images_by_orientation,
    organize_hq_lq_by_orientation,
)
from dataset_forge.operations import (
    extract_random_pairs as _extract_random_pairs,
    shuffle_image_pairs as _shuffle_image_pairs,
    split_adjust_dataset as _split_adjust_dataset,
    remove_small_image_pairs as _remove_small_image_pairs,
    split_single_folder_in_sets as _split_single_folder_in_sets,
)
import os
from tqdm import tqdm
from dataset_forge.ic9600_tiling import run_ic9600_tiling
from dataset_forge.utils.printing import print_header, print_success, print_error


def create_multiscale_dataset(*args, **kwargs):
    """Create a multiscale dataset from input images/folders. (Stub: see multiscale.py)"""
    pass


def image_tiling():
    """Perform image tiling on a folder or HQ/LQ pair using IC9600."""
    print_header("Image Tiling (IC9600)")
    mode = input("Select mode: [1] HQ/LQ paired folders, [2] Single folder: ").strip()
    try:
        if mode == "1":
            hq_folder = input("Enter HQ folder path: ").strip()
            lq_folder = input("Enter LQ folder path: ").strip()
            out_hq_folder = input("Enter output HQ tiles folder: ").strip()
            out_lq_folder = input("Enter output LQ tiles folder: ").strip()
            tile_size = int(input("Tile size (default 1024): ").strip() or "1024")
            scale = int(input("Scale factor (default 1): ").strip() or "1")
            dynamic_n_tiles = (
                input("Dynamic number of tiles per image? [Y/n]: ").strip().lower()
                != "n"
            )
            laplacian_thread = float(
                input("Laplacian threshold (default 0.01): ").strip() or "0.01"
            )
            image_gray = (
                input("Process images as grayscale? [y/N]: ").strip().lower() == "y"
            )
            device = input("Device [cuda/cpu] (default cuda): ").strip() or "cuda"
            run_ic9600_tiling(
                hq_folder=hq_folder,
                lq_folder=lq_folder,
                out_hq_folder=out_hq_folder,
                out_lq_folder=out_lq_folder,
                tile_size=tile_size,
                scale=scale,
                dynamic_n_tiles=dynamic_n_tiles,
                laplacian_thread=laplacian_thread,
                image_gray=image_gray,
                device=device,
            )
            print_success("HQ/LQ tiling complete.")
        elif mode == "2":
            single_folder = input("Enter folder path: ").strip()
            out_folder = input("Enter output tiles folder: ").strip()
            tile_size = int(input("Tile size (default 1024): ").strip() or "1024")
            scale = int(input("Scale factor (default 1): ").strip() or "1")
            dynamic_n_tiles = (
                input("Dynamic number of tiles per image? [Y/n]: ").strip().lower()
                != "n"
            )
            laplacian_thread = float(
                input("Laplacian threshold (default 0.01): ").strip() or "0.01"
            )
            image_gray = (
                input("Process images as grayscale? [y/N]: ").strip().lower() == "y"
            )
            device = input("Device [cuda/cpu] (default cuda): ").strip() or "cuda"
            run_ic9600_tiling(
                single_folder=single_folder,
                out_folder=out_folder,
                tile_size=tile_size,
                scale=scale,
                dynamic_n_tiles=dynamic_n_tiles,
                laplacian_thread=laplacian_thread,
                image_gray=image_gray,
                device=device,
            )
            print_success("Single-folder tiling complete.")
        else:
            print_error("Invalid mode selected.")
    except Exception as e:
        print_error(f"Error during tiling: {e}")


def combine_datasets():
    """Combine multiple HQ/LQ datasets into one."""
    combiner = DatasetCombiner()
    combiner.run()


def extract_random_pairs(hq_folder, lq_folder):
    """Extract random HQ/LQ image pairs from the dataset."""
    return _extract_random_pairs(hq_folder, lq_folder)


def shuffle_image_pairs(hq_folder, lq_folder):
    """Shuffle HQ/LQ image pairs while maintaining alignment."""
    return _shuffle_image_pairs(hq_folder, lq_folder)


def split_single_folder_in_sets(folder):
    """Split a single folder of images into N sets with progress bar and operation choice."""
    return _split_single_folder_in_sets(folder)


def split_adjust_dataset(hq_folder, lq_folder):
    """Split and adjust the dataset according to user parameters."""
    if not lq_folder:
        return split_single_folder_in_sets(hq_folder)
    return _split_adjust_dataset(hq_folder, lq_folder)


def remove_small_image_pairs(hq_folder, lq_folder):
    """Remove HQ/LQ image pairs that are below a minimum size."""
    return _remove_small_image_pairs(hq_folder, lq_folder)


def de_dupe(
    hq_folder,
    lq_folder=None,
    hash_type="phash",
    mode="exact",
    max_dist=5,
    op="move",
    dest_dir=None,
):
    """Detect and handle duplicate or near-duplicate images. If lq_folder is None or blank, only dedupe in hq_folder."""
    hq_hashes = compute_hashes(hq_folder, hash_func=hash_type)
    if not hq_hashes:
        print("No images found in HQ folder.")
        return
    if mode == "near":
        groups = find_near_duplicates(hq_hashes, max_distance=max_dist) or []
    else:
        groups = find_duplicates(hq_hashes) or []
    if not groups:
        print("No duplicates or near-duplicates found.")
        return
    if lq_folder:
        # Progress bar for paired deduplication
        for group in tqdm(groups, desc="Processing duplicate groups"):
            align_and_operate_on_pairs(
                [group], hq_folder, lq_folder, op=op, dest_dir=dest_dir
            )
    else:
        # Only operate on HQ folder, with progress bar
        for group in tqdm(groups, desc="Processing duplicate groups"):
            to_operate = list(group)[1:]
            for fname in to_operate:
                hq_path = os.path.join(hq_folder, fname)
                if op == "delete":
                    if os.path.exists(hq_path):
                        os.remove(hq_path)
                        print(f"Deleted {hq_path}")
                elif op in ("move", "copy"):
                    if dest_dir and "hq" in dest_dir:
                        dest = os.path.join(dest_dir["hq"], fname)
                        os.makedirs(dest_dir["hq"], exist_ok=True)
                        if op == "move":
                            os.rename(hq_path, dest)
                            print(f"Moved {hq_path} -> {dest}")
                        elif op == "copy":
                            import shutil

                            shutil.copy2(hq_path, dest)
                            print(f"Copied {hq_path} -> {dest}")
    print("Done!")


def batch_rename(
    input_path, hq_path=None, lq_path=None, prefix="", padding=5, dry_run=True
):
    """Batch rename images in a folder or HQ/LQ pair."""
    if hq_path and lq_path:
        batch_rename_hq_lq_folders(
            hq_path, lq_path, prefix=prefix, padding=padding, dry_run=dry_run
        )
    else:
        batch_rename_single_folder(
            input_path, prefix=prefix, padding=padding, dry_run=dry_run
        )


def extract_frames_from_video():
    """Extract frames from a video file for dataset creation."""
    extract_frames_menu()


def images_orientation_organization(*args, **kwargs):
    """Organize images by orientation (landscape, portrait, square)."""
    # This function can call organize_images_by_orientation or organize_hq_lq_by_orientation based on args
    if "hq_folder" in kwargs and "lq_folder" in kwargs:
        return organize_hq_lq_by_orientation(
            kwargs["hq_folder"],
            kwargs["lq_folder"],
            kwargs["output_hq_folder"],
            kwargs["output_lq_folder"],
            kwargs["orientations"],
            kwargs.get("operation", "copy"),
        )
    else:
        return organize_images_by_orientation(
            kwargs["input_folder"],
            kwargs["output_folder"],
            kwargs["orientations"],
            kwargs.get("operation", "copy"),
        )
