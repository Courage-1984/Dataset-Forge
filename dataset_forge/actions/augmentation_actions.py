import os
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import List, Tuple, Callable, Dict, Any, Optional
from dataset_forge.utils.progress_utils import tqdm, image_map, smart_map
from dataset_forge.utils.parallel_utils import (
    parallel_image_processing,
    ProcessingType,
    ParallelConfig,
    setup_parallel_environment,
)
from dataset_forge.menus.session_state import parallel_config, user_preferences
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.monitoring import monitor_all


# Augmentation functions
def random_crop(
    img: Image.Image, crop_size: Tuple[int, int] = (256, 256)
) -> Image.Image:
    """Random crop augmentation."""
    width, height = img.size
    crop_w, crop_h = crop_size

    if width < crop_w or height < crop_h:
        # If image is smaller than crop size, resize it
        scale = max(crop_w / width, crop_h / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        width, height = new_width, new_height

    # Random crop
    left = random.randint(0, width - crop_w)
    top = random.randint(0, height - crop_h)
    right = left + crop_w
    bottom = top + crop_h

    return img.crop((left, top, right, bottom))


def random_flip(img: Image.Image, p: float = 0.5) -> Image.Image:
    """Random horizontal flip augmentation."""
    if random.random() < p:
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def random_rotation(img: Image.Image, max_angle: int = 30) -> Image.Image:
    """Random rotation augmentation."""
    angle = random.uniform(-max_angle, max_angle)
    return img.rotate(angle, expand=True, fillcolor=(128, 128, 128))


def random_brightness(
    img: Image.Image, factor_range: Tuple[float, float] = (0.8, 1.2)
) -> Image.Image:
    """Random brightness adjustment."""
    factor = random.uniform(*factor_range)
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)


def random_contrast(
    img: Image.Image, factor_range: Tuple[float, float] = (0.8, 1.2)
) -> Image.Image:
    """Random contrast adjustment."""
    factor = random.uniform(*factor_range)
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)


def random_saturation(
    img: Image.Image, factor_range: Tuple[float, float] = (0.8, 1.2)
) -> Image.Image:
    """Random saturation adjustment."""
    factor = random.uniform(*factor_range)
    enhancer = ImageEnhance.Color(img)
    return enhancer.enhance(factor)


def random_noise(img: Image.Image, noise_factor: float = 0.05) -> Image.Image:
    """Add random noise to image."""
    img_array = np.array(img).astype(np.float32)
    noise = np.random.normal(0, noise_factor * 255, img_array.shape)
    img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array)


def random_blur(img: Image.Image, max_radius: float = 2.0) -> Image.Image:
    """Random Gaussian blur."""
    radius = random.uniform(0, max_radius)
    if radius > 0:
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    return img


def mixup(img1: Image.Image, img2: Image.Image, alpha: float = 0.5) -> Image.Image:
    """Mixup augmentation between two images."""
    # Resize images to same size
    size = img1.size
    img2_resized = img2.resize(size, Image.LANCZOS)

    # Convert to numpy arrays
    arr1 = np.array(img1).astype(np.float32)
    arr2 = np.array(img2_resized).astype(np.float32)

    # Mixup
    mixed = alpha * arr1 + (1 - alpha) * arr2
    mixed = np.clip(mixed, 0, 255).astype(np.uint8)

    return Image.fromarray(mixed)


# Predefined augmentation recipes
AUGMENTATION_RECIPES = {
    "basic": [
        (random_flip, {"p": 0.5}),
        (random_rotation, {"max_angle": 15}),
        (random_brightness, {"factor_range": (0.9, 1.1)}),
        (random_contrast, {"factor_range": (0.9, 1.1)}),
    ],
    "moderate": [
        (random_flip, {"p": 0.5}),
        (random_rotation, {"max_angle": 30}),
        (random_brightness, {"factor_range": (0.8, 1.2)}),
        (random_contrast, {"factor_range": (0.8, 1.2)}),
        (random_saturation, {"factor_range": (0.8, 1.2)}),
        (random_noise, {"noise_factor": 0.03}),
    ],
    "aggressive": [
        (random_flip, {"p": 0.5}),
        (random_rotation, {"max_angle": 45}),
        (random_brightness, {"factor_range": (0.7, 1.3)}),
        (random_contrast, {"factor_range": (0.7, 1.3)}),
        (random_saturation, {"factor_range": (0.7, 1.3)}),
        (random_noise, {"noise_factor": 0.05}),
        (random_blur, {"max_radius": 1.5}),
    ],
    "mixup": [
        # Mixup is handled specially in the pipeline
    ],
}


@monitor_all("augment_single_image")
def augment_single_image(
    image_path: str,
    recipe: List[Tuple[Callable, Dict[str, Any]]],
    output_path: str,
    crop_size: Optional[Tuple[int, int]] = None,
) -> bool:
    """
    Apply augmentation pipeline to a single image.

    Args:
        image_path: Path to input image
        recipe: List of (function, parameters) tuples
        output_path: Path for output image
        crop_size: Optional crop size for random_crop

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load image
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Apply augmentation pipeline
            for func, params in recipe:
                if func == random_crop and crop_size:
                    img = func(img, crop_size)
                else:
                    img = func(img, **params)

            # Save augmented image
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path)

            return True

    except Exception as e:
        print(f"Error augmenting {image_path}: {e}")
        return False


@monitor_all("augment_image_pair")
def augment_image_pair(
    pair_info: tuple,
    recipe: List[Tuple[Callable, Dict[str, Any]]],
    output_hq_dir: str,
    output_lq_dir: str,
    crop_size: Optional[Tuple[int, int]] = None,
) -> bool:
    """
    Apply augmentation pipeline to an HQ/LQ pair.

    Args:
        pair_info: Tuple of (hq_path, lq_path, filename)
        recipe: List of (function, parameters) tuples
        output_hq_dir: Output HQ directory
        output_lq_dir: Output LQ directory
        crop_size: Optional crop size for random_crop

    Returns:
        bool: True if both images successful, False otherwise
    """
    hq_path, lq_path, filename = pair_info

    # Determine output paths
    name, ext = os.path.splitext(filename)
    hq_output = os.path.join(output_hq_dir, f"{name}_aug{ext}")
    lq_output = os.path.join(output_lq_dir, f"{name}_aug{ext}")

    # Apply augmentations
    hq_success = augment_single_image(hq_path, recipe, hq_output, crop_size)
    lq_success = augment_single_image(lq_path, recipe, lq_output, crop_size)

    return hq_success and lq_success


# --- Pipeline Application ---
@monitor_all("apply_augmentation_pipeline", critical_on_error=True)
def apply_augmentation_pipeline(
    input_dir: str,
    output_dir: str,
    recipe_name: str,
    hq_lq_mode: bool = False,
    lq_input_dir: Optional[str] = None,
    lq_output_dir: Optional[str] = None,
    custom_recipe: Optional[List[Tuple[Callable, Dict[str, Any]]]] = None,
    crop_size: Optional[Tuple[int, int]] = None,
    progress_desc: str = "Augmenting images",
):
    """
    Apply an augmentation pipeline to all images in input_dir with parallel processing.
    Special handling for mixup: pairs images randomly for mixup.
    """
    recipe = (
        custom_recipe
        if custom_recipe is not None
        else AUGMENTATION_RECIPES[recipe_name]
    )

    if crop_size:
        recipe = [
            (fn, {**params, **({"crop_size": crop_size} if fn == random_crop else {})})
            for fn, params in recipe
        ]

    os.makedirs(output_dir, exist_ok=True)

    if recipe_name == "mixup":
        # Mixup: randomly pair images
        files = [
            f
            for f in os.listdir(input_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))
        ]

        if len(files) < 2:
            print("Need at least 2 images for mixup augmentation.")
            return

        # Shuffle files for random pairing
        random.shuffle(files)

        def process_mixup_pair(pair_info):
            """Process a single mixup pair."""
            idx, (file1, file2) = pair_info
            try:
                img1 = Image.open(os.path.join(input_dir, file1)).convert("RGB")
                img2 = Image.open(os.path.join(input_dir, file2)).convert("RGB")
                mixed = mixup(img1, img2)
                out_path = os.path.join(output_dir, f"mixup_{idx}_{file1}_{file2}")
                mixed.save(out_path)
                return True
            except Exception as e:
                print(f"Error processing mixup pair {file1}, {file2}: {e}")
                return False

        # Create pairs
        pairs = []
        for i in range(0, len(files) - 1, 2):
            pairs.append((i // 2, (files[i], files[i + 1])))

        # Setup parallel processing
        config = ParallelConfig(
            max_workers=parallel_config.get("max_workers"),
            processing_type=ProcessingType.THREAD,
            use_gpu=False,
        )

        # Process pairs in parallel
        results = smart_map(
            process_mixup_pair,
            pairs,
            desc="Processing mixup pairs",
            max_workers=config.max_workers,
            processing_type=ProcessingType.THREAD,
        )

        successful = sum(1 for result in results if result)
        print(
            f"Mixup augmentation complete: {successful}/{len(pairs)} pairs successful"
        )
        return

    if hq_lq_mode and lq_input_dir and lq_output_dir:
        # HQ/LQ mode
        os.makedirs(lq_output_dir, exist_ok=True)

        hq_files = sorted(
            [
                f
                for f in os.listdir(input_dir)
                if f.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")
                )
            ]
        )
        lq_files = sorted(
            [
                f
                for f in os.listdir(lq_input_dir)
                if f.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")
                )
            ]
        )

        # Match HQ/LQ pairs
        matching_files = sorted(set(hq_files) & set(lq_files))

        if not matching_files:
            print("No matching HQ/LQ pairs found.")
            return

        # Prepare pair information
        pairs = []
        for filename in matching_files:
            hq_path = os.path.join(input_dir, filename)
            lq_path = os.path.join(lq_input_dir, filename)
            pairs.append((hq_path, lq_path, filename))

        # Setup parallel processing
        config = ParallelConfig(
            max_workers=parallel_config.get("max_workers"),
            processing_type=ProcessingType.THREAD,
            use_gpu=False,
        )

        # Process pairs in parallel
        results = smart_map(
            lambda pair: augment_image_pair(
                pair, recipe, output_dir, lq_output_dir, crop_size
            ),
            pairs,
            desc="Augmenting HQ/LQ pairs",
            max_workers=config.max_workers,
            processing_type=ProcessingType.THREAD,
        )

        successful = sum(1 for result in results if result)
        print(
            f"HQ/LQ augmentation complete: {successful}/{len(pairs)} pairs successful"
        )

    else:
        # Single folder mode
        files = [
            f
            for f in os.listdir(input_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))
        ]

        if not files:
            print("No image files found in input directory.")
            return

        # Prepare file paths
        file_paths = [os.path.join(input_dir, f) for f in files]

        # Setup parallel processing
        config = ParallelConfig(
            max_workers=parallel_config.get("max_workers"),
            processing_type=ProcessingType.THREAD,
            use_gpu=False,
        )

        # Process images in parallel
        results = image_map(
            lambda path: augment_single_image(path, recipe, output_dir, crop_size),
            file_paths,
            desc="Augmenting images",
            max_workers=config.max_workers,
        )

        successful = sum(1 for result in results if result)
        print(f"Augmentation complete: {successful}/{len(files)} images successful")

    # Log operation
    log_operation(
        "augmentation_pipeline", f"{recipe_name}, {successful} images processed"
    )


@monitor_all("create_augmentation_variations", critical_on_error=True)
def create_augmentation_variations(
    input_dir: str,
    output_dir: str,
    recipe_name: str,
    num_variations: int = 3,
    hq_lq_mode: bool = False,
    lq_input_dir: Optional[str] = None,
    lq_output_dir: Optional[str] = None,
    crop_size: Optional[Tuple[int, int]] = None,
):
    """
    Create multiple variations of each image using augmentation.

    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        recipe_name: Name of augmentation recipe
        num_variations: Number of variations to create per image
        hq_lq_mode: Whether to process HQ/LQ pairs
        lq_input_dir: LQ input directory (for HQ/LQ mode)
        lq_output_dir: LQ output directory (for HQ/LQ mode)
        crop_size: Optional crop size
    """
    recipe = AUGMENTATION_RECIPES[recipe_name]

    if crop_size:
        recipe = [
            (fn, {**params, **({"crop_size": crop_size} if fn == random_crop else {})})
            for fn, params in recipe
        ]

    os.makedirs(output_dir, exist_ok=True)

    if hq_lq_mode and lq_input_dir and lq_output_dir:
        # HQ/LQ mode
        os.makedirs(lq_output_dir, exist_ok=True)

        hq_files = sorted(
            [
                f
                for f in os.listdir(input_dir)
                if f.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")
                )
            ]
        )
        lq_files = sorted(
            [
                f
                for f in os.listdir(lq_input_dir)
                if f.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")
                )
            ]
        )

        matching_files = sorted(set(hq_files) & set(lq_files))

        if not matching_files:
            print("No matching HQ/LQ pairs found.")
            return

        def create_variations_for_pair(pair_info):
            """Create variations for a single HQ/LQ pair."""
            filename, variation_idx = pair_info
            hq_path = os.path.join(input_dir, filename)
            lq_path = os.path.join(lq_input_dir, filename)

            name, ext = os.path.splitext(filename)
            hq_output = os.path.join(output_dir, f"{name}_var{variation_idx}{ext}")
            lq_output = os.path.join(lq_output_dir, f"{name}_var{variation_idx}{ext}")

            hq_success = augment_single_image(hq_path, recipe, hq_output, crop_size)
            lq_success = augment_single_image(lq_path, recipe, lq_output, crop_size)

            return hq_success and lq_success

        # Create variation tasks
        variation_tasks = []
        for filename in matching_files:
            for i in range(num_variations):
                variation_tasks.append((filename, i + 1))

        # Setup parallel processing
        config = ParallelConfig(
            max_workers=parallel_config.get("max_workers"),
            processing_type=ProcessingType.THREAD,
            use_gpu=False,
        )

        # Process variations in parallel
        results = smart_map(
            create_variations_for_pair,
            variation_tasks,
            desc=f"Creating {num_variations} variations per pair",
            max_workers=config.max_workers,
            processing_type=ProcessingType.THREAD,
        )

        successful = sum(1 for result in results if result)
        total_expected = len(matching_files) * num_variations
        print(
            f"Variation creation complete: {successful}/{total_expected} variations successful"
        )

    else:
        # Single folder mode
        files = [
            f
            for f in os.listdir(input_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))
        ]

        if not files:
            print("No image files found in input directory.")
            return

        def create_variations_for_image(image_info):
            """Create variations for a single image."""
            filepath, variation_idx = image_info
            filename = os.path.basename(filepath)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(output_dir, f"{name}_var{variation_idx}{ext}")

            return augment_single_image(filepath, recipe, output_path, crop_size)

        # Create variation tasks
        variation_tasks = []
        for filename in files:
            filepath = os.path.join(input_dir, filename)
            for i in range(num_variations):
                variation_tasks.append((filepath, i + 1))

        # Setup parallel processing
        config = ParallelConfig(
            max_workers=parallel_config.get("max_workers"),
            processing_type=ProcessingType.THREAD,
            use_gpu=False,
        )

        # Process variations in parallel
        results = smart_map(
            create_variations_for_image,
            variation_tasks,
            desc=f"Creating {num_variations} variations per image",
            max_workers=config.max_workers,
            processing_type=ProcessingType.THREAD,
        )

        successful = sum(1 for result in results if result)
        total_expected = len(files) * num_variations
        print(
            f"Variation creation complete: {successful}/{total_expected} variations successful"
        )

    # Log operation
    log_operation(
        "augmentation_variations",
        f"{recipe_name}, {num_variations} variations, {successful} successful",
    )
