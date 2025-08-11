import os
from PIL import Image
from collections import defaultdict
import imagehash
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success, print_error, print_info
from dataset_forge.utils.audio_utils import play_done_sound


def compute_hashes(folder, hash_func="phash"):
    """
    Compute perceptual hashes for all images in a folder.
    hash_func: 'phash', 'dhash', 'ahash', or 'whash'.
    Returns a dict: {filename: hash}
    """
    hash_funcs = {
        "phash": imagehash.phash,
        "dhash": imagehash.dhash,
        "ahash": imagehash.average_hash,
        "whash": imagehash.whash,
    }
    func = hash_funcs.get(hash_func, imagehash.phash)
    hashes = {}
    files = [
        fname
        for fname in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, fname))
        and fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))
    ]
    for fname in tqdm(files, desc="Hashing images"):
        fpath = os.path.join(folder, fname)
        try:
            with Image.open(fpath) as img:
                hashes[fname] = func(img)
        except Exception as e:
            print_error(f"Error hashing {fname}: {e}")
    return hashes


def find_duplicates(hashes):
    """
    Find exact duplicates (identical hashes).
    Returns: list of lists of filenames (duplicate groups)
    """
    hash_to_files = defaultdict(list)
    for fname, h in hashes.items():
        hash_to_files[str(h)].append(fname)
    return [files for files in hash_to_files.values() if len(files) > 1]


def find_near_duplicates(hashes, max_distance=5):
    """
    Find near-duplicates (hashes within max_distance Hamming distance).
    Returns: list of sets of filenames (near-duplicate groups)
    """
    files = list(hashes.keys())
    groups = []
    used = set()
    for i, f1 in enumerate(files):
        if f1 in used:
            continue
        group = {f1}
        for j in range(i + 1, len(files)):
            f2 = files[j]
            if f2 in used:
                continue
            dist = hashes[f1] - hashes[f2]
            if dist <= max_distance:
                group.add(f2)
                used.add(f2)
        if len(group) > 1:
            groups.append(group)
            used.update(group)
    return groups


def align_and_operate_on_pairs(
    dupe_groups, hq_folder, lq_folder, op="move", dest_dir=None
):
    """
    For each group of duplicates, perform the operation (move/copy/delete) on both HQ and LQ images.
    If op is 'move' or 'copy', dest_dir must be provided (dict with 'hq' and 'lq' keys).
    """
    for group in dupe_groups:
        # Always keep the first image, operate on the rest
        to_operate = list(group)[1:]
        for fname in to_operate:
            hq_path = os.path.join(hq_folder, fname)
            lq_path = os.path.join(lq_folder, fname)
            if op == "delete":
                for p in [hq_path, lq_path]:
                    if os.path.exists(p):
                        os.remove(p)
                        print_info(f"Deleted {p}")
            elif op in ("move", "copy"):
                for src, dkey in zip([hq_path, lq_path], ["hq", "lq"]):
                    if os.path.exists(src):
                        dest = os.path.join(dest_dir[dkey], fname)
                        if op == "move":
                            os.makedirs(dest_dir[dkey], exist_ok=True)
                            os.rename(src, dest)
                            print_info(f"Moved {src} -> {dest}")
                        elif op == "copy":
                            os.makedirs(dest_dir[dkey], exist_ok=True)
                            import shutil

                            shutil.copy2(src, dest)
                            print_info(f"Copied {src} -> {dest}")
