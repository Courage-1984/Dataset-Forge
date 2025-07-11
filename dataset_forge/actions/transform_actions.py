import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from dataset_forge.utils.progress_utils import tqdm, image_map, smart_map
from dataset_forge.utils.parallel_utils import (
    parallel_image_processing,
    ProcessingType,
    ParallelConfig,
    setup_parallel_environment,
)
from dataset_forge.menus.session_state import parallel_config, user_preferences
from dataset_forge.utils.io_utils import is_image_file
from dataset_forge.utils.input_utils import (
    get_file_operation_choice,
    get_destination_path,
)
from dataset_forge.utils.file_utils import get_unique_filename
from dataset_forge.utils.history_log import log_operation


def apply_transformation_to_image(
    input_path: str,
    transform_type: str,
    value: float,
    operation: str,
    output_path: str,
) -> bool:
    """
    Apply a transformation to a single image.

    Args:
        input_path: Path to input image
        transform_type: Type of transformation to apply
        value: Transformation value/parameter
        operation: Operation type (copy, move, inplace)
        output_path: Path for output image

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load image
        with Image.open(input_path) as img:
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Apply transformation
            if transform_type == "brightness":
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(value)
            elif transform_type == "contrast":
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(value)
            elif transform_type == "saturation":
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(value)
            elif transform_type == "sharpness":
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(value)
            elif transform_type == "blur":
                img = img.filter(ImageFilter.GaussianBlur(radius=value))
            elif transform_type == "hue":
                # Convert to HSV, adjust hue, convert back
                img_array = np.array(img)
                hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
                hsv[:, :, 0] = (hsv[:, :, 0] + value) % 180
                img_array = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                img = Image.fromarray(img_array)
            else:
                print(f"Unknown transformation type: {transform_type}")
                return False

            # Save image
            if operation == "inplace":
                img.save(input_path)
            else:
                # Create output directory if needed
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path)

            return True

    except Exception as e:
        print(f"Error applying {transform_type} to {input_path}: {e}")
        return False


def transform_single_pair(
    pair_info: tuple,
    transform_type: str,
    value: float,
    operation: str,
    dest_hq_dir: str,
    dest_lq_dir: str,
) -> bool:
    """
    Transform a single HQ/LQ pair.

    Args:
        pair_info: Tuple of (hq_path, lq_path, filename)
        transform_type: Type of transformation
        value: Transformation value
        operation: Operation type
        dest_hq_dir: Destination HQ directory
        dest_lq_dir: Destination LQ directory

    Returns:
        bool: True if both images successful, False otherwise
    """
    hq_path, lq_path, filename = pair_info

    # Determine output paths
    if operation == "inplace":
        hq_output = hq_path
        lq_output = lq_path
    else:
        hq_output = os.path.join(
            dest_hq_dir, get_unique_filename(dest_hq_dir, filename)
        )
        lq_output = os.path.join(
            dest_lq_dir, get_unique_filename(dest_lq_dir, filename)
        )

    # Apply transformations
    hq_success = apply_transformation_to_image(
        hq_path, transform_type, value, operation, hq_output
    )
    lq_success = apply_transformation_to_image(
        lq_path, transform_type, value, operation, lq_output
    )

    return hq_success and lq_success


def transform_dataset(hq_folder, lq_folder):
    """Transform dataset with parallel processing."""
    print("\n" + "=" * 30)
    print("  TRANSFORM DATASET")
    print("=" * 30)

    # Get transformation type
    print("\nAvailable transformations:")
    print("1. brightness - Adjust image brightness")
    print("2. contrast - Adjust image contrast")
    print("3. saturation - Adjust color saturation")
    print("4. sharpness - Adjust image sharpness")
    print("5. blur - Apply Gaussian blur")
    print("6. hue - Adjust hue (color shift)")

    transform_choice = input("\nSelect transformation (1-6): ").strip()

    transform_map = {
        "1": "brightness",
        "2": "contrast",
        "3": "saturation",
        "4": "sharpness",
        "5": "blur",
        "6": "hue",
    }

    if transform_choice not in transform_map:
        print("Invalid choice.")
        return

    selected_transform = transform_map[transform_choice]

    # Get transformation value
    value = float(input(f"Enter {selected_transform} value: "))

    # Get operation type
    operation = get_file_operation_choice()

    # Get destination directories if needed
    dest_hq_dir = ""
    dest_lq_dir = ""
    if operation != "inplace":
        dest_hq_dir = get_destination_path("Enter destination HQ folder: ")
        dest_lq_dir = get_destination_path("Enter destination LQ folder: ")
        if not dest_hq_dir or not dest_lq_dir:
            print("Operation aborted as destination paths were not provided.")
            return
        os.makedirs(dest_hq_dir, exist_ok=True)
        os.makedirs(dest_lq_dir, exist_ok=True)

    # Get matching files
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    matching_files = sorted(hq_files & lq_files)

    if not matching_files:
        print("No matching HQ/LQ pairs found.")
        return

    print(f"\nFound {len(matching_files)} matching pairs to transform.")

    # Prepare pair information
    pairs = []
    for filename in matching_files:
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)
        pairs.append((hq_path, lq_path, filename))

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # I/O bound task
        use_gpu=False,  # No GPU needed for basic transformations
        chunk_size=parallel_config.get("chunk_size", 1),
    )

    # Process pairs in parallel
    results = smart_map(
        lambda pair: transform_single_pair(
            pair, selected_transform, value, operation, dest_hq_dir, dest_lq_dir
        ),
        pairs,
        desc=f"Transforming pairs ({selected_transform})",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print(f"\nTransformation complete:")
    print(f"  Successful pairs: {successful}")
    print(f"  Failed pairs: {failed}")

    # Log operation
    log_operation(
        "transform_dataset",
        f"{selected_transform}={value}, {operation}, {successful}/{len(pairs)} pairs",
    )


def transform_single_folder(folder_path: str):
    """Transform images in a single folder with parallel processing."""
    print("\n" + "=" * 30)
    print("  TRANSFORM SINGLE FOLDER")
    print("=" * 30)

    # Get transformation type
    print("\nAvailable transformations:")
    print("1. brightness - Adjust image brightness")
    print("2. contrast - Adjust image contrast")
    print("3. saturation - Adjust color saturation")
    print("4. sharpness - Adjust image sharpness")
    print("5. blur - Apply Gaussian blur")
    print("6. hue - Adjust hue (color shift)")

    transform_choice = input("\nSelect transformation (1-6): ").strip()

    transform_map = {
        "1": "brightness",
        "2": "contrast",
        "3": "saturation",
        "4": "sharpness",
        "5": "blur",
        "6": "hue",
    }

    if transform_choice not in transform_map:
        print("Invalid choice.")
        return

    selected_transform = transform_map[transform_choice]

    # Get transformation value
    value = float(input(f"Enter {selected_transform} value: "))

    # Get operation type
    operation = get_file_operation_choice()

    # Get destination directory if needed
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path("Enter destination folder: ")
        if not dest_dir:
            print("Operation aborted as destination path was not provided.")
            return
        os.makedirs(dest_dir, exist_ok=True)

    # Get image files
    image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]

    if not image_files:
        print("No image files found in folder.")
        return

    print(f"\nFound {len(image_files)} images to transform.")

    # Prepare image paths
    image_paths = [os.path.join(folder_path, f) for f in image_files]

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    # Process images in parallel
    results = image_map(
        lambda path: apply_transformation_to_image(
            path, selected_transform, value, operation, dest_dir
        ),
        image_paths,
        desc=f"Transforming images ({selected_transform})",
        max_workers=config.max_workers,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print(f"\nTransformation complete:")
    print(f"  Successful images: {successful}")
    print(f"  Failed images: {failed}")

    # Log operation
    log_operation(
        "transform_single_folder",
        f"{selected_transform}={value}, {operation}, {successful}/{len(image_files)} images",
    )


def batch_transform_with_parameters(
    folder_path: str,
    transform_type: str,
    parameters: list,
    operation: str = "copy",
    dest_dir: str = None,
):
    """
    Apply transformations with multiple parameters to create variations.

    Args:
        folder_path: Path to folder containing images
        transform_type: Type of transformation
        parameters: List of parameter values to try
        operation: Operation type (copy, move, inplace)
        dest_dir: Destination directory
    """
    # Get image files
    image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]

    if not image_files:
        print("No image files found in folder.")
        return

    print(
        f"Found {len(image_files)} images to transform with {len(parameters)} parameters."
    )

    # Create destination directory if needed
    if operation != "inplace" and dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def transform_with_parameter(image_param_tuple):
        """Transform a single image with a specific parameter."""
        image_path, param = image_param_tuple
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)

        if operation == "inplace":
            output_path = image_path
        else:
            output_path = os.path.join(
                dest_dir, f"{name}_{transform_type}_{param}{ext}"
            )

        return apply_transformation_to_image(
            image_path, transform_type, param, operation, output_path
        )

    # Create all image-parameter combinations
    combinations = []
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        for param in parameters:
            combinations.append((image_path, param))

    # Process combinations in parallel
    results = smart_map(
        transform_with_parameter,
        combinations,
        desc=f"Batch transforming ({transform_type})",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print(f"\nBatch transformation complete:")
    print(f"  Total operations: {len(combinations)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

    # Log operation
    log_operation(
        "batch_transform",
        f"{transform_type}, {len(parameters)} params, {operation}, {successful}/{len(combinations)} operations",
    )


def apply_custom_transformation(
    folder_path: str,
    transform_func,
    operation: str = "copy",
    dest_dir: str = None,
    **kwargs,
):
    """
    Apply a custom transformation function to all images in a folder.

    Args:
        folder_path: Path to folder containing images
        transform_func: Custom transformation function
        operation: Operation type (copy, move, inplace)
        dest_dir: Destination directory
        **kwargs: Additional arguments for transform_func
    """
    # Get image files
    image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]

    if not image_files:
        print("No image files found in folder.")
        return

    print(f"Found {len(image_files)} images to transform.")

    # Create destination directory if needed
    if operation != "inplace" and dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def apply_custom_transform(image_path):
        """Apply custom transformation to a single image."""
        try:
            filename = os.path.basename(image_path)

            if operation == "inplace":
                output_path = image_path
            else:
                output_path = os.path.join(dest_dir, filename)

            # Load image
            with Image.open(image_path) as img:
                # Apply custom transformation
                transformed_img = transform_func(img, **kwargs)

                # Save image
                if operation == "inplace":
                    transformed_img.save(image_path)
                else:
                    transformed_img.save(output_path)

            return True

        except Exception as e:
            print(f"Error applying custom transformation to {image_path}: {e}")
            return False

    # Process images in parallel
    results = image_map(
        apply_custom_transform,
        [os.path.join(folder_path, f) for f in image_files],
        desc="Applying custom transformation",
        max_workers=config.max_workers,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print(f"\nCustom transformation complete:")
    print(f"  Successful images: {successful}")
    print(f"  Failed images: {failed}")

    # Log operation
    log_operation(
        "custom_transform",
        f"custom function, {operation}, {successful}/{len(image_files)} images",
    )
