import os
import shutil
import random
from tqdm import tqdm
from dataset_forge.utils.file_utils import is_image_file
from dataset_forge.utils.history_log import log_operation


def move_or_copy_files(
    source_folder,
    destination_folder,
    move_percentage: int = 100,
    file_extension=None,
    operation="move",
    seed=None,
):
    """
    Move or copy files from source_folder to destination_folder.
    Supports filtering by extension and percentage (as integer 0-100).
    """
    if seed is not None:
        random.seed(seed)

    files_to_process = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file_extension and not file.lower().endswith(file_extension.lower()):
                continue
            files_to_process.append(os.path.join(root, file))

    if not files_to_process:
        print(
            f"No files found in {source_folder} matching extension '{file_extension}'."
        )
        return

    random.shuffle(files_to_process)
    num_files = int(len(files_to_process) * (move_percentage / 100))
    files_to_process = files_to_process[:num_files]

    for source_path in tqdm(
        files_to_process, desc=f"{operation.capitalize()}ing files", unit="file"
    ):
        relative_path = os.path.relpath(source_path, source_folder)
        destination_path = os.path.join(destination_folder, relative_path)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        try:
            if operation == "move":
                shutil.move(source_path, destination_path)
                log_operation("move", f"{source_path} -> {destination_path}")
            elif operation == "copy":
                shutil.copy2(source_path, destination_path)
                log_operation("copy", f"{source_path} -> {destination_path}")
        except Exception as e:
            print(f"Error {operation}ing {source_path} to {destination_path}: {e}")


def move_or_copy_hq_lq_pairs(
    input_folder,
    output_folder,
    move_percentage: int = 100,
    file_extension=None,
    operation="move",
    seed=None,
):
    """
    Move or copy aligned HQ/LQ pairs from input_folder/hq and input_folder/lq to output_folder/hq and output_folder/lq.
    Only processes pairs where both HQ and LQ images exist (by filename).
    Supports filtering by extension and percentage (as integer 0-100).
    """
    hq_folder = os.path.join(input_folder, "hq")
    lq_folder = os.path.join(input_folder, "lq")
    out_hq_folder = os.path.join(output_folder, "hq")
    out_lq_folder = os.path.join(output_folder, "lq")

    if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
        print(f"Both HQ and LQ folders must exist in {input_folder}.")
        return

    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    if file_extension:
        hq_files = {f for f in hq_files if f.lower().endswith(file_extension.lower())}
        lq_files = {f for f in lq_files if f.lower().endswith(file_extension.lower())}
    common_files = sorted(list(hq_files & lq_files))
    if not common_files:
        print(f"No aligned HQ/LQ pairs found in {hq_folder} and {lq_folder}.")
        return

    random.shuffle(common_files)
    num_pairs = int(len(common_files) * (move_percentage / 100))
    selected_files = common_files[:num_pairs]

    for fname in tqdm(
        selected_files, desc=f"{operation.capitalize()}ing HQ/LQ pairs", unit="pair"
    ):
        hq_src = os.path.join(hq_folder, fname)
        lq_src = os.path.join(lq_folder, fname)
        hq_dest = os.path.join(out_hq_folder, fname)
        lq_dest = os.path.join(out_lq_folder, fname)
        os.makedirs(os.path.dirname(hq_dest), exist_ok=True)
        os.makedirs(os.path.dirname(lq_dest), exist_ok=True)
        try:
            if operation == "move":
                shutil.move(hq_src, hq_dest)
                shutil.move(lq_src, lq_dest)
                log_operation("move_hq", f"{hq_src} -> {hq_dest}")
                log_operation("move_lq", f"{lq_src} -> {lq_dest}")
            elif operation == "copy":
                shutil.copy2(hq_src, hq_dest)
                shutil.copy2(lq_src, lq_dest)
                log_operation("copy_hq", f"{hq_src} -> {hq_dest}")
                log_operation("copy_lq", f"{lq_src} -> {lq_dest}")
        except Exception as e:
            print(f"Error {operation}ing pair {fname}: {e}")
