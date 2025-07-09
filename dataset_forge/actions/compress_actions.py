# compress_actions.py - Business logic for image compression
import os
import subprocess
from PIL import Image
from tqdm import tqdm
from dataset_forge.utils.file_utils import (
    is_image_file,
    perform_file_operation,
    run_oxipng,
)


def compress_images(
    src_hq=None,
    src_lq=None,
    single_folder=None,
    output_format="png",
    quality=85,
    oxipng_level=4,
    action="copy",
    dest_dir=None,
    use_oxipng=False,
    keep_pairs=False,
    oxipng_strip=None,
    oxipng_alpha=False,
):
    """
    Compress images in HQ/LQ or single-folder mode.
    - src_hq, src_lq: HQ/LQ parent paths (if both provided, align pairs)
    - single_folder: single folder path (if provided, process all images)
    - output_format: output format (e.g., 'png', 'jpeg', 'webp')
    - quality: JPEG/WebP quality (1-100)
    - oxipng_level: Oxipng optimization level (0-6 or 'max')
    - action: 'copy', 'move', or 'inplace'
    - dest_dir: destination directory (if copy/move)
    - use_oxipng: whether to run Oxipng on PNG outputs
    - keep_pairs: if True, keep HQ/LQ alignment
    - oxipng_strip: metadata to strip (safe, all, comma-list, or None)
    - oxipng_alpha: use --alpha for transparent pixel optimization
    """
    if single_folder:
        image_files = [f for f in os.listdir(single_folder) if is_image_file(f)]
        image_paths = [os.path.join(single_folder, f) for f in image_files]
    elif src_hq and src_lq:
        # For now, align by filename intersection
        hq_files = set(f for f in os.listdir(src_hq) if is_image_file(f))
        lq_files = set(f for f in os.listdir(src_lq) if is_image_file(f))
        common_files = sorted(hq_files & lq_files)
        image_paths = [
            (os.path.join(src_hq, f), os.path.join(src_lq, f)) for f in common_files
        ]
    else:
        print("No valid input folder(s) provided.")
        return

    if not image_paths:
        print("No images found to compress.")
        return

    print(
        f"Compressing {len(image_paths)} image{' pairs' if src_hq and src_lq else 's'}..."
    )
    for idx, item in enumerate(tqdm(image_paths, desc="Compressing", ncols=80)):
        if src_hq and src_lq:
            hq_path, lq_path = item
            for path in [hq_path, lq_path]:
                _compress_single_image(
                    path,
                    output_format,
                    quality,
                    oxipng_level,
                    action,
                    dest_dir,
                    use_oxipng,
                    oxipng_strip,
                    oxipng_alpha,
                )
        else:
            _compress_single_image(
                item,
                output_format,
                quality,
                oxipng_level,
                action,
                dest_dir,
                use_oxipng,
                oxipng_strip,
                oxipng_alpha,
            )


def _compress_single_image(
    src_path,
    output_format,
    quality,
    oxipng_level,
    action,
    dest_dir,
    use_oxipng,
    oxipng_strip,
    oxipng_alpha,
):
    try:
        img = Image.open(src_path)
        img = img.convert("RGBA" if output_format.lower() == "png" else "RGB")
        base = os.path.basename(src_path)
        name, _ = os.path.splitext(base)
        out_ext = (
            ".png" if output_format.lower() == "png" else f".{output_format.lower()}"
        )
        out_name = name + out_ext
        out_dir = (
            dest_dir
            if action in ["copy", "move"] and dest_dir
            else os.path.dirname(src_path)
        )
        out_path = os.path.join(out_dir, out_name)
        save_kwargs = {}
        if output_format.lower() in ["jpeg", "jpg", "webp"]:
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        img.save(out_path, output_format.upper(), **save_kwargs)
        if use_oxipng and output_format.lower() == "png":
            run_oxipng(
                out_path, level=oxipng_level, strip=oxipng_strip, alpha=oxipng_alpha
            )
        if action == "move":
            if out_path != src_path:
                os.remove(src_path)
    except Exception as e:
        print(f"Error compressing {src_path}: {e}")
