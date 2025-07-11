# compress_actions.py - Business logic for image compression
import os
import subprocess
from PIL import Image
from dataset_forge.utils.progress_utils import tqdm, image_map, smart_map
from dataset_forge.utils.parallel_utils import (
    parallel_image_processing,
    ProcessingType,
    ParallelConfig,
    setup_parallel_environment,
)
from dataset_forge.menus.session_state import parallel_config, user_preferences
from dataset_forge.utils.file_utils import (
    is_image_file,
    perform_file_operation,
    run_oxipng,
)


def compress_single_image(
    image_path: str,
    output_format: str = "png",
    quality: int = 85,
    oxipng_level: int = 4,
    action: str = "copy",
    dest_dir: str = None,
    use_oxipng: bool = False,
    oxipng_strip: str = None,
    oxipng_alpha: bool = False,
) -> bool:
    """
    Compress a single image with the specified settings.

    Args:
        image_path: Path to the input image
        output_format: Output format (png, jpeg, webp)
        quality: JPEG/WebP quality (1-100)
        oxipng_level: Oxipng optimization level (0-6)
        action: Action to perform (copy, move, inplace)
        dest_dir: Destination directory
        use_oxipng: Whether to use oxipng for PNG optimization
        oxipng_strip: Metadata to strip
        oxipng_alpha: Use alpha optimization

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Determine output path
        if action == "inplace":
            output_path = image_path
        else:
            if not dest_dir:
                raise ValueError(
                    "Destination directory required for copy/move operations"
                )

            filename = os.path.basename(image_path)
            name, _ = os.path.splitext(filename)
            output_path = os.path.join(dest_dir, f"{name}.{output_format}")

            # Create destination directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Load and compress image
        with Image.open(image_path) as img:
            # Convert to RGB if saving as JPEG
            if output_format.lower() == "jpeg" and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # Save with appropriate settings
            if output_format.lower() == "jpeg":
                img.save(output_path, "JPEG", quality=quality, optimize=True)
            elif output_format.lower() == "webp":
                img.save(output_path, "WebP", quality=quality, method=6)
            else:  # PNG
                img.save(output_path, "PNG", optimize=True)

        # Apply oxipng optimization if requested
        if use_oxipng and output_format.lower() == "png":
            run_oxipng(
                output_path, level=oxipng_level, strip=oxipng_strip, alpha=oxipng_alpha
            )

        # Move original if requested
        if action == "move" and output_path != image_path:
            os.remove(image_path)

        return True

    except Exception as e:
        print(f"Error compressing {image_path}: {e}")
        return False


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
    Compress images in HQ/LQ or single-folder mode with parallel processing.
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
    # Prepare image paths
    if single_folder:
        image_files = [f for f in os.listdir(single_folder) if is_image_file(f)]
        image_paths = [os.path.join(single_folder, f) for f in image_files]
        paired_mode = False
    elif src_hq and src_lq:
        # For now, align by filename intersection
        hq_files = set(f for f in os.listdir(src_hq) if is_image_file(f))
        lq_files = set(f for f in os.listdir(src_lq) if is_image_file(f))
        common_files = sorted(hq_files & lq_files)
        image_paths = [
            (os.path.join(src_hq, f), os.path.join(src_lq, f)) for f in common_files
        ]
        paired_mode = True
    else:
        print("No valid input folder(s) provided.")
        return

    if not image_paths:
        print("No images found to compress.")
        return

    print(f"Compressing {len(image_paths)} image{' pairs' if paired_mode else 's'}...")

    # Setup parallel processing configuration
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # I/O bound task
        use_gpu=False,  # No GPU needed for compression
        chunk_size=parallel_config.get("chunk_size", 1),
    )

    if paired_mode:
        # Process HQ/LQ pairs
        def compress_pair(pair):
            hq_path, lq_path = pair
            hq_success = compress_single_image(
                hq_path,
                output_format,
                quality,
                oxipng_level,
                action,
                dest_dir,
                use_oxipng,
                oxipng_strip,
                oxipng_alpha,
            )
            lq_success = compress_single_image(
                lq_path,
                output_format,
                quality,
                oxipng_level,
                action,
                dest_dir,
                use_oxipng,
                oxipng_strip,
                oxipng_alpha,
            )
            return hq_success and lq_success

        results = smart_map(
            compress_pair,
            image_paths,
            desc="Compressing image pairs",
            max_workers=config.max_workers,
            processing_type=ProcessingType.THREAD,
        )
    else:
        # Process single images
        results = image_map(
            lambda path: compress_single_image(
                path,
                output_format,
                quality,
                oxipng_level,
                action,
                dest_dir,
                use_oxipng,
                oxipng_strip,
                oxipng_alpha,
            ),
            image_paths,
            desc="Compressing images",
            max_workers=config.max_workers,
        )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print(f"Compression complete: {successful} successful, {failed} failed")


def compress_directory(
    input_dir: str,
    output_dir: str,
    output_format: str = "png",
    quality: int = 85,
    oxipng_level: int = 4,
    use_oxipng: bool = False,
    oxipng_strip: str = None,
    oxipng_alpha: bool = False,
    recursive: bool = True,
):
    """
    Compress all images in a directory with parallel processing.

    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        output_format: Output format (png, jpeg, webp)
        quality: JPEG/WebP quality (1-100)
        oxipng_level: Oxipng optimization level (0-6)
        use_oxipng: Whether to use oxipng for PNG optimization
        oxipng_strip: Metadata to strip
        oxipng_alpha: Use alpha optimization
        recursive: Whether to process subdirectories recursively
    """
    # Collect all image paths
    image_paths = []

    if recursive:
        for root, _, files in os.walk(input_dir):
            for file in files:
                if is_image_file(file):
                    input_path = os.path.join(root, file)
                    # Calculate relative path for output
                    rel_path = os.path.relpath(input_path, input_dir)
                    name, _ = os.path.splitext(rel_path)
                    output_path = os.path.join(output_dir, f"{name}.{output_format}")
                    image_paths.append((input_path, output_path))
    else:
        for file in os.listdir(input_dir):
            if is_image_file(file):
                input_path = os.path.join(input_dir, file)
                name, _ = os.path.splitext(file)
                output_path = os.path.join(output_dir, f"{name}.{output_format}")
                image_paths.append((input_path, output_path))

    if not image_paths:
        print("No images found to compress.")
        return

    print(f"Found {len(image_paths)} images to compress.")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def compress_with_paths(path_tuple):
        input_path, output_path = path_tuple
        return compress_single_image(
            input_path,
            output_format,
            quality,
            oxipng_level,
            "copy",
            os.path.dirname(output_path),
            use_oxipng,
            oxipng_strip,
            oxipng_alpha,
        )

    results = smart_map(
        compress_with_paths,
        image_paths,
        desc="Compressing directory",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print(f"Directory compression complete: {successful} successful, {failed} failed")


def batch_compress_with_quality_analysis(
    input_dir: str,
    output_dir: str,
    target_size_mb: float = 1.0,
    output_format: str = "jpeg",
    max_quality: int = 95,
    min_quality: int = 10,
    quality_step: int = 5,
    use_oxipng: bool = False,
):
    """
    Batch compress images with automatic quality adjustment to meet target size.

    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        target_size_mb: Target file size in MB
        output_format: Output format (jpeg, webp)
        max_quality: Maximum quality to try
        min_quality: Minimum quality to try
        quality_step: Quality adjustment step
        use_oxipng: Whether to use oxipng (only for PNG)
    """
    # Collect image paths
    image_paths = []
    for file in os.listdir(input_dir):
        if is_image_file(file):
            image_paths.append(os.path.join(input_dir, file))

    if not image_paths:
        print("No images found to compress.")
        return

    print(f"Found {len(image_paths)} images for quality-based compression.")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def find_optimal_quality(image_path):
        """Find optimal quality for a single image to meet target size."""
        filename = os.path.basename(image_path)
        name, _ = os.path.splitext(filename)

        target_size_bytes = target_size_mb * 1024 * 1024

        for quality in range(max_quality, min_quality - 1, -quality_step):
            output_path = os.path.join(output_dir, f"{name}.{output_format}")

            try:
                with Image.open(image_path) as img:
                    if output_format.lower() == "jpeg" and img.mode in (
                        "RGBA",
                        "LA",
                        "P",
                    ):
                        img = img.convert("RGB")

                    if output_format.lower() == "jpeg":
                        img.save(output_path, "JPEG", quality=quality, optimize=True)
                    elif output_format.lower() == "webp":
                        img.save(output_path, "WebP", quality=quality, method=6)
                    else:
                        img.save(output_path, "PNG", optimize=True)

                # Check file size
                file_size = os.path.getsize(output_path)
                if file_size <= target_size_bytes:
                    return True, quality

                # Remove temporary file
                os.remove(output_path)

            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                return False, 0

        return False, 0

    results = smart_map(
        find_optimal_quality,
        image_paths,
        desc="Finding optimal quality",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    successful = sum(1 for success, _ in results if success)
    failed = len(results) - successful

    print(
        f"Quality-based compression complete: {successful} successful, {failed} failed"
    )

    # Show quality statistics
    qualities = [quality for success, quality in results if success]
    if qualities:
        avg_quality = sum(qualities) / len(qualities)
        print(f"Average quality used: {avg_quality:.1f}")
        print(f"Quality range: {min(qualities)} - {max(qualities)}")
