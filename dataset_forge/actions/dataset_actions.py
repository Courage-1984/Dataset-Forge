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
)


def create_multiscale_dataset(*args, **kwargs):
    """Create a multiscale dataset from input images/folders. (Stub: see multiscale.py)"""
    pass


def image_tiling(*args, **kwargs):
    """Perform image tiling on a folder or HQ/LQ pair. (Stub: see tiling.py/tiling_grid.py)"""
    pass


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


def split_adjust_dataset(hq_folder, lq_folder):
    """Split and adjust the dataset according to user parameters."""
    return _split_adjust_dataset(hq_folder, lq_folder)


def remove_small_image_pairs(hq_folder, lq_folder):
    """Remove HQ/LQ image pairs that are below a minimum size."""
    return _remove_small_image_pairs(hq_folder, lq_folder)


def de_dupe(
    hq_folder,
    lq_folder,
    hash_type="phash",
    mode="exact",
    max_dist=5,
    op="move",
    dest_dir=None,
):
    """Detect and handle duplicate or near-duplicate images."""
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
    align_and_operate_on_pairs(groups, hq_folder, lq_folder, op=op, dest_dir=dest_dir)
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
