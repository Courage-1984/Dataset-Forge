import os
from tqdm import tqdm
from PIL import Image
import imagehash


def fuzzy_hq_lq_pairing_logic(
    hq_folder, lq_folder, hash_func=imagehash.phash, threshold=8
):
    """
    Pair HQ and LQ images using perceptual hashes (fuzzy matching).
    Returns a list of (hq_path, lq_path) pairs.
    TODO: Add support for deep embeddings for even more robust matching.
    """
    hq_files = [
        f for f in os.listdir(hq_folder) if os.path.isfile(os.path.join(hq_folder, f))
    ]
    lq_files = [
        f for f in os.listdir(lq_folder) if os.path.isfile(os.path.join(lq_folder, f))
    ]
    hq_hashes = {}
    lq_hashes = {}
    # Compute hashes for HQ images
    for fname in tqdm(hq_files, desc="Hashing HQ images"):
        try:
            with Image.open(os.path.join(hq_folder, fname)) as img:
                hq_hashes[fname] = hash_func(img)
        except Exception:
            continue
    # Compute hashes for LQ images
    for fname in tqdm(lq_files, desc="Hashing LQ images"):
        try:
            with Image.open(os.path.join(lq_folder, fname)) as img:
                lq_hashes[fname] = hash_func(img)
        except Exception:
            continue
    # Fuzzy match: for each HQ, find closest LQ within threshold
    pairs = []
    used_lq = set()
    for hq_fname, hq_hash in tqdm(hq_hashes.items(), desc="Pairing images"):
        best_lq = None
        best_dist = None
        for lq_fname, lq_hash in lq_hashes.items():
            if lq_fname in used_lq:
                continue
            dist = hq_hash - lq_hash
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_lq = lq_fname
        if best_lq is not None and best_dist is not None and best_dist <= threshold:
            pairs.append(
                (os.path.join(hq_folder, hq_fname), os.path.join(lq_folder, best_lq))
            )
            used_lq.add(best_lq)
    return pairs
