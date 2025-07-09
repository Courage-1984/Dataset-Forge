import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pepeline import read, save, ImgFormat
from pepedpid import dpid_resize
from dataset_forge.io_utils import is_image_file

SUPPORTED_INPUT_EXTS = {
    ".webp",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".bmp",
    ".tif",
    ".jfif",
}
SUPPORTED_OUTPUT_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def process_image(input_path, output_path, scale, verbose=False):
    try:
        img = read(input_path, format=ImgFormat.F32)
        h, w = img.shape[:2]
        factor = (scale - 1) / scale
        target_h = max(1, int(round(h / scale)))
        target_w = max(1, int(round(w / scale)))
        resized = dpid_resize(img, target_h, target_w, factor)
        save(resized, output_path)
        if verbose:
            print(
                f"Processed: {os.path.basename(input_path)} -> {os.path.basename(output_path)} [Size: {target_w}x{target_h}]"
            )
        return True
    except Exception as e:
        print(f"Error processing {os.path.basename(input_path)}: {str(e)}")
        return False


def downscale_folder(
    input_folder,
    output_folder,
    scale,
    output_ext=".png",
    threads=4,
    recursive=False,
    skip_existing=False,
    verbose=False,
):
    os.makedirs(output_folder, exist_ok=True)
    image_paths = []
    if recursive:
        for root, _, files in os.walk(input_folder):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in SUPPORTED_INPUT_EXTS:
                    input_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(input_path, input_folder)
                    output_path = os.path.join(
                        output_folder,
                        os.path.splitext(rel_path)[0] + output_ext,
                    )
                    image_paths.append((input_path, output_path))
    else:
        for filename in os.listdir(input_folder):
            filepath = os.path.join(input_folder, filename)
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1].lower()
                if ext in SUPPORTED_INPUT_EXTS:
                    output_path = os.path.join(
                        output_folder,
                        os.path.splitext(filename)[0] + output_ext,
                    )
                    image_paths.append((filepath, output_path))
    if not image_paths:
        print("No valid images found in input directory")
        return 0, 0, 0
    processed_count = 0
    skipped_count = 0

    def process_task(input_path, output_path):
        nonlocal skipped_count
        if skip_existing and os.path.exists(output_path):
            skipped_count += 1
            if verbose:
                print(f"Skipping existing: {os.path.basename(output_path)}")
            return False
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        return process_image(input_path, output_path, scale, verbose)

    if threads > 0:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(process_task, ip, op) for ip, op in image_paths]
            for future in as_completed(futures):
                if future.result():
                    processed_count += 1
    else:
        for input_path, output_path in image_paths:
            if process_task(input_path, output_path):
                processed_count += 1
    failed_count = len(image_paths) - processed_count - skipped_count
    return processed_count, skipped_count, failed_count


def downscale_hq_lq_pair(
    hq_folder,
    lq_folder,
    out_hq_folder,
    out_lq_folder,
    scale,
    output_ext=".png",
    threads=4,
    skip_existing=False,
    verbose=False,
    recursive=False,
):
    os.makedirs(out_hq_folder, exist_ok=True)
    os.makedirs(out_lq_folder, exist_ok=True)
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    matching_files = sorted(hq_files & lq_files)
    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        return 0, 0, 0
    processed_count = 0
    skipped_count = 0

    def process_task(filename):
        nonlocal skipped_count
        hq_input = os.path.join(hq_folder, filename)
        lq_input = os.path.join(lq_folder, filename)
        hq_output = os.path.join(
            out_hq_folder, os.path.splitext(filename)[0] + output_ext
        )
        lq_output = os.path.join(
            out_lq_folder, os.path.splitext(filename)[0] + output_ext
        )
        if skip_existing and os.path.exists(hq_output) and os.path.exists(lq_output):
            skipped_count += 1
            if verbose:
                print(f"Skipping existing pair: {filename}")
            return False
        ok1 = process_image(hq_input, hq_output, scale, verbose)
        ok2 = process_image(lq_input, lq_output, scale, verbose)
        return ok1 and ok2

    if threads > 0:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(process_task, fname) for fname in matching_files]
            for future in as_completed(futures):
                if future.result():
                    processed_count += 1
    else:
        for fname in matching_files:
            if process_task(fname):
                processed_count += 1
    failed_count = len(matching_files) - processed_count - skipped_count
    return processed_count, skipped_count, failed_count
