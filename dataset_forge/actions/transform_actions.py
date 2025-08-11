import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
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
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
    print_section,
)
from dataset_forge.utils.color import Mocha


@monitor_all("apply_transformation_to_image")
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
                print_error(f"Unknown transformation type: {transform_type}")
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
        print_error(f"Error applying {transform_type} to {input_path}: {e}")
        return False


@monitor_all("transform_single_pair", critical_on_error=True)
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


@monitor_all("transform_dataset", critical_on_error=True)
def transform_dataset(hq_folder, lq_folder):
    """Transform dataset with parallel processing."""
    print_header("TRANSFORM DATASET", char="=", color=Mocha.lavender)

    # Get transformation type
    print_section("Available transformations", char="-", color=Mocha.lavender)
    print_info("1. brightness - Adjust image brightness")
    print_info("2. contrast - Adjust image contrast")
    print_info("3. saturation - Adjust color saturation")
    print_info("4. sharpness - Adjust image sharpness")
    print_info("5. blur - Apply Gaussian blur")
    print_info("6. hue - Adjust hue (color shift)")

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
        print_error("Invalid choice.")
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
            print_error("Operation aborted as destination paths were not provided.")
            return
        os.makedirs(dest_hq_dir, exist_ok=True)
        os.makedirs(dest_lq_dir, exist_ok=True)

    # Get matching files
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    matching_files = sorted(hq_files & lq_files)

    if not matching_files:
        print_warning("No matching HQ/LQ pairs found.")
        return

    print_info(f"\nFound {len(matching_files)} matching pairs to transform.")

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

    print_section("Transformation complete", char="-", color=Mocha.lavender)
    print_info(f"  Successful pairs: {successful}")
    print_info(f"  Failed pairs: {failed}")

    # Log operation
    log_operation(
        "transform_dataset",
        f"{selected_transform}={value}, {operation}, {successful}/{len(pairs)} pairs",
    )

    print_success("Dataset transformation complete!")
    play_done_sound()


@monitor_all("transform_single_folder", critical_on_error=True)
def transform_single_folder(folder_path: str):
    """Transform images in a single folder with parallel processing."""
    print_header("TRANSFORM SINGLE FOLDER", char="=", color=Mocha.lavender)

    # Get transformation type
    print_section("Available transformations", char="-", color=Mocha.lavender)
    print_info("1. brightness - Adjust image brightness")
    print_info("2. contrast - Adjust image contrast")
    print_info("3. saturation - Adjust color saturation")
    print_info("4. sharpness - Adjust image sharpness")
    print_info("5. blur - Apply Gaussian blur")
    print_info("6. hue - Adjust hue (color shift)")

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
        print_error("Invalid choice.")
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
            print_error("Operation aborted as destination path was not provided.")
            return
        os.makedirs(dest_dir, exist_ok=True)

    # Get image files
    image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]

    if not image_files:
        print_warning("No image files found in folder.")
        return

    print_info(f"\nFound {len(image_files)} images to transform.")

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

    print_section("Transformation complete", char="-", color=Mocha.lavender)
    print_info(f"  Successful images: {successful}")
    print_info(f"  Failed images: {failed}")

    # Log operation
    log_operation(
        "transform_single_folder",
        f"{selected_transform}={value}, {operation}, {successful}/{len(image_files)} images",
    )

    print_success("Single folder transformation complete!")
    play_done_sound()


@monitor_all("batch_transform_with_parameters", critical_on_error=True)
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
        print_warning("No image files found in folder.")
        return

    print_info(
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

    print_section("Batch transformation complete", char="-", color=Mocha.lavender)
    print_info(f"  Total operations: {len(combinations)}")
    print_info(f"  Successful: {successful}")
    print_info(f"  Failed: {failed}")

    # Log operation
    log_operation(
        "batch_transform",
        f"{transform_type}, {len(parameters)} params, {operation}, {successful}/{len(combinations)} operations",
    )

    print_success("Batch transformation complete!")
    play_done_sound()


@monitor_all("apply_custom_transformation", critical_on_error=True)
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
        print_warning("No image files found in folder.")
        return

    print_info(f"Found {len(image_files)} images to transform.")

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
            print_error(f"Error applying custom transformation to {image_path}: {e}")
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

    print_section("Custom transformation complete", char="-", color=Mocha.lavender)
    print_info(f"  Successful images: {successful}")
    print_info(f"  Failed images: {failed}")

    # Log operation
    log_operation(
        "custom_transform",
        f"custom function, {operation}, {successful}/{len(image_files)} images",
    )


def downsample_images_menu():
    """
    Menu for downsampling images with various options.

    This function provides a user interface for downsampling images with
    different scaling methods and aspect ratio handling options.
    """
    from dataset_forge.utils.input_utils import (
        get_file_operation_choice,
        get_destination_path,
    )
    from dataset_forge.utils.image_ops import get_image_size
    from dataset_forge.utils.printing import (
        print_header,
        print_info,
        print_error,
        print_success,
    )
    from dataset_forge.utils.color import Mocha

    print_header("Downsample Images", color=Mocha.lavender)
    print_info(
        "This tool allows you to downsample images with various scaling options.\n"
    )

    # Get input folder
    input_folder = input("Enter path to input folder: ").strip()
    if not os.path.isdir(input_folder):
        print_error("Input path must be a valid directory.")
        return

    # Get scale factor
    while True:
        try:
            scale_factor = float(
                input("Enter scale factor (e.g., 2.0 for 50% size): ").strip()
            )
            if scale_factor > 1:
                break
            else:
                print_error("Scale factor must be greater than 1 for downsampling.")
        except ValueError:
            print_error("Invalid input. Please enter a number.")

    # Get operation type
    operation = get_file_operation_choice()

    # Get destination directory if needed
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path("Enter destination folder: ")
        if not dest_dir:
            print_error("Operation aborted as destination path was not provided.")
            return
        os.makedirs(dest_dir, exist_ok=True)

    # Get aspect ratio handling method
    print_info("\nHow should aspect ratio differences be handled when resizing?")
    print_info("1. Just resize (may distort aspect ratio) [default]")
    print_info("2. Crop to fit (center crop to target size)")
    print_info("3. Pad to fit (add black bars to target size)")
    aspect_mode = input("Enter 1, 2, or 3: ").strip()
    if aspect_mode not in {"2", "3"}:
        aspect_mode = "1"

    # Get image files
    image_files = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not image_files:
        print_error("No image files found in the input folder.")
        return

    print_info(f"\nFound {len(image_files)} images to downsample.")

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def downsample_single_image(image_file):
        """Downsample a single image."""
        try:
            input_path = os.path.join(input_folder, image_file)
            name, ext = os.path.splitext(image_file)

            if operation == "inplace":
                output_path = input_path
            else:
                output_path = os.path.join(dest_dir, image_file)

            # Get original dimensions
            orig_w, orig_h = get_image_size(input_path)
            target_w = int(round(orig_w / scale_factor))
            target_h = int(round(orig_h / scale_factor))

            with Image.open(input_path) as img:
                if aspect_mode == "1":
                    # Just resize (may distort)
                    resized = img.resize((target_w, target_h), Image.LANCZOS)
                elif aspect_mode == "2":
                    # Crop to fit (center crop, then resize)
                    src_w, src_h = img.size
                    src_aspect = src_w / src_h
                    tgt_aspect = target_w / target_h
                    if src_aspect > tgt_aspect:
                        # Crop width
                        new_w = int(src_h * tgt_aspect)
                        left = (src_w - new_w) // 2
                        img_cropped = img.crop((left, 0, left + new_w, src_h))
                    else:
                        # Crop height
                        new_h = int(src_w / tgt_aspect)
                        top = (src_h - new_h) // 2
                        img_cropped = img.crop((0, top, src_w, top + new_h))
                    resized = img_cropped.resize((target_w, target_h), Image.LANCZOS)
                elif aspect_mode == "3":
                    # Pad to fit (letterbox/pillarbox)
                    src_w, src_h = img.size
                    src_aspect = src_w / src_h
                    tgt_aspect = target_w / target_h
                    if src_aspect > tgt_aspect:
                        # Pad height
                        new_h = int(src_w / tgt_aspect)
                        pad_top = (new_h - src_h) // 2
                        pad_bottom = new_h - src_h - pad_top
                        padding = (0, pad_top, 0, pad_bottom)
                    else:
                        # Pad width
                        new_w = int(src_h * tgt_aspect)
                        pad_left = (new_w - src_w) // 2
                        pad_right = new_w - src_w - pad_left
                        padding = (pad_left, 0, pad_right, 0)
                    img_padded = ImageOps.expand(img, padding, fill=(0, 0, 0))
                    resized = img_padded.resize((target_w, target_h), Image.LANCZOS)
                else:
                    resized = img.resize((target_w, target_h), Image.LANCZOS)

                # Save with appropriate format and quality
                save_kwargs = {}
                if ext.lower() in [".jpg", ".jpeg"]:
                    save_kwargs["quality"] = 95
                    save_format = "JPEG"
                elif ext.lower() == ".png":
                    save_format = "PNG"
                elif ext.lower() == ".webp":
                    save_format = "WEBP"
                else:
                    save_format = None

                if save_format:
                    resized.save(output_path, save_format, **save_kwargs)
                else:
                    resized.save(output_path)

            return True

        except Exception as e:
            print_error(f"Failed to downsample {image_file}: {e}")
            return False

    # Process images in parallel
    results = image_map(
        downsample_single_image,
        image_files,
        desc=f"Downsampling images (1/{scale_factor:.2f}x)",
        max_workers=config.max_workers,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print_success(f"\nDownsampling complete:")
    print_info(f"  Successful images: {successful}")
    print_info(f"  Failed images: {failed}")
    print_info(f"  Scale factor: 1/{scale_factor:.2f}x")

    # Log operation
    log_operation(
        "downsample_images",
        f"scale=1/{scale_factor:.2f}, {operation}, aspect_mode={aspect_mode}, {successful}/{len(image_files)} images",
    )
    input("Press Enter to return to the menu...")


def hdr_to_sdr_menu():
    """
    Menu for converting HDR images to SDR with various tone mapping options.

    This function provides a user interface for converting HDR images to SDR
    using different tone mapping algorithms and parameters.
    """
    from dataset_forge.utils.input_utils import (
        get_file_operation_choice,
        get_destination_path,
    )
    from dataset_forge.utils.printing import (
        print_header,
        print_info,
        print_error,
        print_success,
        print_warning,
    )
    from dataset_forge.utils.color import Mocha

    print_header("Convert HDR to SDR", color=Mocha.lavender)
    print_info("This tool converts HDR images to SDR using tone mapping.\n")

    # Get input folder
    input_folder = input("Enter path to input folder: ").strip()
    if not os.path.isdir(input_folder):
        print_error("Input path must be a valid directory.")
        return

    # Get operation type
    operation = get_file_operation_choice()

    # Get destination directory if needed
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path("Enter destination folder: ")
        if not dest_dir:
            print_error("Operation aborted as destination path was not provided.")
            return
        os.makedirs(dest_dir, exist_ok=True)

    # Get tone mapping method
    print_info("\nSelect tone mapping method:")
    print_info("1. Reinhard (photographic) [default]")
    print_info("2. Drago (adaptive logarithmic)")
    print_info("3. Durand (fast bilateral filtering)")
    print_info("4. Mantiuk (contrast preserving)")
    print_info("5. Simple gamma correction")

    method_choice = input("Enter choice (1-5): ").strip()
    if method_choice not in ["1", "2", "3", "4", "5"]:
        method_choice = "1"

    # Get additional parameters based on method
    gamma = 2.2
    saturation = 1.0
    if method_choice in ["1", "2", "3", "4"]:
        try:
            gamma = float(input("Enter gamma value (default 2.2): ").strip() or "2.2")
            saturation = float(
                input("Enter saturation value (default 1.0): ").strip() or "1.0"
            )
        except ValueError:
            print_warning("Using default values for gamma and saturation.")

    # Get image files
    image_files = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not image_files:
        print_error("No image files found in the input folder.")
        return

    print_info(f"\nFound {len(image_files)} images to convert.")

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def convert_hdr_to_sdr(image_file):
        """Convert a single HDR image to SDR."""
        try:
            input_path = os.path.join(input_folder, image_file)

            if operation == "inplace":
                output_path = input_path
            else:
                output_path = os.path.join(dest_dir, image_file)

            # Read image with OpenCV
            img = cv2.imread(input_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
            if img is None:
                print_error(f"Could not read image: {image_file}")
                return False

            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Apply tone mapping based on method
            if method_choice == "1":
                # Reinhard tone mapping
                tonemap = cv2.createTonemapReinhard(
                    gamma=gamma, intensity=0.0, light_adapt=1.0, color_adapt=0.0
                )
            elif method_choice == "2":
                # Drago tone mapping
                tonemap = cv2.createTonemapDrago(
                    gamma=gamma, saturation=saturation, bias=0.85
                )
            elif method_choice == "3":
                # Durand tone mapping
                tonemap = cv2.createTonemapDurand(
                    gamma=gamma,
                    contrast=4.0,
                    saturation=saturation,
                    sigma_space=2.0,
                    sigma_color=2.0,
                )
            elif method_choice == "4":
                # Mantiuk tone mapping
                tonemap = cv2.createTonemapMantiuk(
                    gamma=gamma, scale=0.6, saturation=saturation
                )
            else:
                # Simple gamma correction
                tonemap = None
                # Normalize to 0-1 range and apply gamma
                img_normalized = img_rgb.astype(np.float32) / 65535.0  # Assuming 16-bit
                img_gamma = np.power(img_normalized, 1.0 / gamma)
                img_8bit = np.clip(img_gamma * 255, 0, 255).astype(np.uint8)

            if tonemap is not None:
                # Apply tone mapping
                img_tonemapped = tonemap.process(img_rgb.astype(np.float32))
                img_8bit = np.clip(img_tonemapped * 255, 0, 255).astype(np.uint8)

            # Convert back to BGR for saving
            img_bgr = cv2.cvtColor(img_8bit, cv2.COLOR_RGB2BGR)

            # Save image
            cv2.imwrite(output_path, img_bgr)

            return True

        except Exception as e:
            print_error(f"Failed to convert {image_file}: {e}")
            return False

    # Process images in parallel
    results = image_map(
        convert_hdr_to_sdr,
        image_files,
        desc=f"Converting HDR to SDR ({method_choice})",
        max_workers=config.max_workers,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print_success(f"\nHDR to SDR conversion complete:")
    print_info(f"  Successful images: {successful}")
    print_info(f"  Failed images: {failed}")
    print_info(f"  Method: {method_choice}")
    print_info(f"  Gamma: {gamma}")
    print_info(f"  Saturation: {saturation}")

    # Log operation
    log_operation(
        "hdr_to_sdr",
        f"method={method_choice}, gamma={gamma}, saturation={saturation}, {operation}, {successful}/{len(image_files)} images",
    )
    input("Press Enter to return to the menu...")


def dataset_colour_adjustment(hq_folder, lq_folder):
    """
    Apply color adjustments to both HQ and LQ folders in a dataset.

    This function provides color adjustment options for image datasets
    including brightness, contrast, saturation, and hue adjustments.
    """
    from dataset_forge.utils.input_utils import (
        get_file_operation_choice,
        get_destination_path,
    )
    from dataset_forge.utils.printing import (
        print_header,
        print_info,
        print_error,
        print_success,
    )
    from dataset_forge.utils.color import Mocha

    print_header("Dataset Color Adjustment", color=Mocha.lavender)
    print_info("This tool applies color adjustments to both HQ and LQ folders.\n")

    # Get adjustment type
    print_info("Available adjustments:")
    print_info("1. brightness - Adjust image brightness")
    print_info("2. contrast - Adjust image contrast")
    print_info("3. saturation - Adjust color saturation")
    print_info("4. sharpness - Adjust image sharpness")
    print_info("5. blur - Apply Gaussian blur")
    print_info("6. hue - Adjust hue (color shift)")

    adjustment_choice = input("\nSelect adjustment (1-6): ").strip()

    adjustment_map = {
        "1": "brightness",
        "2": "contrast",
        "3": "saturation",
        "4": "sharpness",
        "5": "blur",
        "6": "hue",
    }

    if adjustment_choice not in adjustment_map:
        print_error("Invalid choice.")
        return

    selected_adjustment = adjustment_map[adjustment_choice]

    # Get adjustment value
    try:
        value = float(input(f"Enter {selected_adjustment} value: "))
    except ValueError:
        print_error("Invalid value. Please enter a number.")
        return

    # Get operation type
    operation = get_file_operation_choice()

    # Get destination directories if needed
    dest_hq_dir = ""
    dest_lq_dir = ""
    if operation != "inplace":
        dest_hq_dir = get_destination_path("Enter destination HQ folder: ")
        dest_lq_dir = get_destination_path("Enter destination LQ folder: ")
        if not dest_hq_dir or not dest_lq_dir:
            print_error("Operation aborted as destination paths were not provided.")
            return
        os.makedirs(dest_hq_dir, exist_ok=True)
        os.makedirs(dest_lq_dir, exist_ok=True)

    # Get matching files
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    matching_files = sorted(hq_files & lq_files)

    if not matching_files:
        print_error("No matching HQ/LQ pairs found.")
        return

    print_info(f"\nFound {len(matching_files)} matching pairs to adjust.")

    # Prepare pair information
    pairs = []
    for filename in matching_files:
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)
        pairs.append((hq_path, lq_path, filename))

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    # Process pairs in parallel
    results = image_map(
        lambda pair: transform_single_pair(
            pair, selected_adjustment, value, operation, dest_hq_dir, dest_lq_dir
        ),
        pairs,
        desc=f"Adjusting {selected_adjustment}",
        max_workers=config.max_workers,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print_success(f"\nColor adjustment complete:")
    print_info(f"  Successful pairs: {successful}")
    print_info(f"  Failed pairs: {failed}")
    print_info(f"  Adjustment: {selected_adjustment} = {value}")

    # Log operation
    log_operation(
        "dataset_colour_adjustment",
        f"{selected_adjustment}={value}, {operation}, {successful}/{len(matching_files)} pairs",
    )
    input("Press Enter to return to the menu...")


def grayscale_conversion(hq_folder, lq_folder):
    """
    Convert both HQ and LQ folders to grayscale.

    This function converts all images in both HQ and LQ folders to grayscale
    while maintaining the folder structure and file relationships.
    """
    from dataset_forge.utils.input_utils import (
        get_file_operation_choice,
        get_destination_path,
    )
    from dataset_forge.utils.printing import (
        print_header,
        print_info,
        print_error,
        print_success,
    )
    from dataset_forge.utils.color import Mocha

    print_header("Convert to Grayscale", color=Mocha.lavender)
    print_info(
        "This tool converts all images in both HQ and LQ folders to grayscale.\n"
    )

    # Get operation type
    operation = get_file_operation_choice()

    # Get destination directories if needed
    dest_hq_dir = ""
    dest_lq_dir = ""
    if operation != "inplace":
        dest_hq_dir = get_destination_path("Enter destination HQ folder: ")
        dest_lq_dir = get_destination_path("Enter destination LQ folder: ")
        if not dest_hq_dir or not dest_lq_dir:
            print_error("Operation aborted as destination paths were not provided.")
            return
        os.makedirs(dest_hq_dir, exist_ok=True)
        os.makedirs(dest_lq_dir, exist_ok=True)

    # Get matching files
    hq_files = {f for f in os.listdir(hq_folder) if is_image_file(f)}
    lq_files = {f for f in os.listdir(lq_folder) if is_image_file(f)}
    matching_files = sorted(hq_files & lq_files)

    if not matching_files:
        print_error("No matching HQ/LQ pairs found.")
        return

    print_info(f"\nFound {len(matching_files)} matching pairs to convert to grayscale.")

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def convert_to_grayscale(pair_info):
        """Convert a single HQ/LQ pair to grayscale."""
        hq_path, lq_path, filename = pair_info

        # Determine output paths
        if operation == "inplace":
            hq_output = hq_path
            lq_output = lq_path
        else:
            hq_output = os.path.join(dest_hq_dir, filename)
            lq_output = os.path.join(dest_lq_dir, filename)

        try:
            # Convert HQ image
            with Image.open(hq_path) as img:
                if img.mode != "L":
                    img_gray = img.convert("L")
                else:
                    img_gray = img

                if operation == "inplace":
                    img_gray.save(hq_path)
                else:
                    img_gray.save(hq_output)

            # Convert LQ image
            with Image.open(lq_path) as img:
                if img.mode != "L":
                    img_gray = img.convert("L")
                else:
                    img_gray = img

                if operation == "inplace":
                    img_gray.save(lq_path)
                else:
                    img_gray.save(lq_output)

            return True

        except Exception as e:
            print_error(f"Failed to convert {filename} to grayscale: {e}")
            return False

    # Prepare pair information
    pairs = []
    for filename in matching_files:
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)
        pairs.append((hq_path, lq_path, filename))

    # Process pairs in parallel
    results = image_map(
        convert_to_grayscale,
        pairs,
        desc="Converting to grayscale",
        max_workers=config.max_workers,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print_success(f"\nGrayscale conversion complete:")
    print_info(f"  Successful pairs: {successful}")
    print_info(f"  Failed pairs: {failed}")

    # Log operation
    log_operation(
        "grayscale_conversion",
        f"{operation}, {successful}/{len(matching_files)} pairs",
    )
    input("Press Enter to return to the menu...")


def remove_alpha_channels_menu():
    """
    Menu for removing alpha channels from images.

    This function provides a user interface for removing alpha channels
    from images in a folder, converting RGBA to RGB.
    """
    from dataset_forge.utils.input_utils import (
        get_file_operation_choice,
        get_destination_path,
    )
    from dataset_forge.utils.printing import (
        print_header,
        print_info,
        print_error,
        print_success,
    )
    from dataset_forge.utils.color import Mocha

    print_header("Remove Alpha Channels", color=Mocha.lavender)
    print_info(
        "This tool removes alpha channels from images, converting RGBA to RGB.\n"
    )

    # Get input folder
    input_folder = input("Enter path to input folder: ").strip()
    if not os.path.isdir(input_folder):
        print_error("Input path must be a valid directory.")
        return

    # Get operation type
    operation = get_file_operation_choice()

    # Get destination directory if needed
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path("Enter destination folder: ")
        if not dest_dir:
            print_error("Operation aborted as destination path was not provided.")
            return
        os.makedirs(dest_dir, exist_ok=True)

    # Get image files
    image_files = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not image_files:
        print_error("No image files found in the input folder.")
        return

    print_info(f"\nFound {len(image_files)} images to process.")

    # Setup parallel processing
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def remove_alpha_channel(image_file):
        """Remove alpha channel from a single image."""
        try:
            input_path = os.path.join(input_folder, image_file)

            if operation == "inplace":
                output_path = input_path
            else:
                output_path = os.path.join(dest_dir, image_file)

            with Image.open(input_path) as img:
                # Check if image has alpha channel
                if img.mode in ("RGBA", "LA", "PA"):
                    # Convert to RGB or L (grayscale)
                    if img.mode == "RGBA":
                        # Create white background
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(
                            img, mask=img.split()[-1]
                        )  # Use alpha channel as mask
                        img_rgb = background
                    elif img.mode == "LA":
                        # Convert to grayscale
                        img_rgb = img.convert("L")
                    else:  # PA
                        img_rgb = img.convert("RGB")
                else:
                    # No alpha channel, just copy
                    img_rgb = img

                # Save image
                if operation == "inplace":
                    img_rgb.save(input_path)
                else:
                    img_rgb.save(output_path)

            return True

        except Exception as e:
            print_error(f"Failed to remove alpha channel from {image_file}: {e}")
            return False

    # Process images in parallel
    results = image_map(
        remove_alpha_channel,
        image_files,
        desc="Removing alpha channels",
        max_workers=config.max_workers,
    )

    # Count results
    successful = sum(1 for result in results if result)
    failed = len(results) - successful

    print_success(f"\nAlpha channel removal complete:")
    print_info(f"  Successful images: {successful}")
    print_info(f"  Failed images: {failed}")

    # Log operation
    log_operation(
        "remove_alpha_channels",
        f"{operation}, {successful}/{len(image_files)} images",
    )
    input("Press Enter to return to the menu...")


def crop_image_menu():
    """
    Menu for cropping images in a folder.
    Prompts user for crop box and processes all images in the folder.
    """
    from dataset_forge.utils.input_utils import (
        get_path_with_history,
        get_file_operation_choice,
        get_destination_path,
    )
    from dataset_forge.utils.printing import (
        print_header,
        print_info,
        print_error,
        print_success,
    )
    from dataset_forge.utils.color import Mocha

    print_header("Crop Images", color=Mocha.lavender)
    input_folder = get_path_with_history("Enter path to input folder:")
    if not input_folder or not os.path.isdir(input_folder):
        print_error("Input path must be a valid directory.")
        input("Press Enter to return to the menu...")
        return
    try:
        left = int(input("Enter left coordinate (pixels): ").strip())
        upper = int(input("Enter upper coordinate (pixels): ").strip())
        right = int(input("Enter right coordinate (pixels): ").strip())
        lower = int(input("Enter lower coordinate (pixels): ").strip())
    except Exception:
        print_error("Invalid crop coordinates.")
        input("Press Enter to return to the menu...")
        return
    crop_box = (left, upper, right, lower)
    operation = get_file_operation_choice()
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path("Enter destination folder: ")
        if not dest_dir:
            print_error("Operation aborted as destination path was not provided.")
            input("Press Enter to return to the menu...")
            return
        os.makedirs(dest_dir, exist_ok=True)
    image_files = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not image_files:
        print_error("No image files found in the input folder.")
        input("Press Enter to return to the menu...")
        return
    print_info(f"\nFound {len(image_files)} images to crop.")
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def crop_single_image(image_file):
        try:
            input_path = os.path.join(input_folder, image_file)
            if operation == "inplace":
                output_path = input_path
            else:
                output_path = os.path.join(dest_dir, image_file)
            with Image.open(input_path) as img:
                cropped = img.crop(crop_box)
                cropped.save(output_path)
            return True
        except Exception as e:
            print_error(f"Failed to crop {image_file}: {e}")
            return False

    results = image_map(
        crop_single_image,
        image_files,
        desc="Cropping images",
        max_workers=config.max_workers,
    )
    successful = sum(1 for result in results if result)
    failed = len(results) - successful
    print_success(f"\nCropping complete:")
    print_info(f"  Successful images: {successful}")
    print_info(f"  Failed images: {failed}")
    log_operation(
        "crop_images",
        f"crop_box={crop_box}, {operation}, {successful}/{len(image_files)} images",
    )
    input("Press Enter to return to the menu...")


def flip_image_menu():
    """
    Menu for flipping images in a folder.
    Prompts user for flip direction and processes all images in the folder.
    """
    from dataset_forge.utils.input_utils import (
        get_path_with_history,
        get_file_operation_choice,
        get_destination_path,
    )
    from dataset_forge.utils.printing import (
        print_header,
        print_info,
        print_error,
        print_success,
    )
    from dataset_forge.utils.color import Mocha

    print_header("Flip Images", color=Mocha.lavender)
    input_folder = get_path_with_history("Enter path to input folder:")
    if not input_folder or not os.path.isdir(input_folder):
        print_error("Input path must be a valid directory.")
        input("Press Enter to return to the menu...")
        return
    print_info("Select flip direction:")
    print_info("1. Horizontal (left-right)")
    print_info("2. Vertical (top-bottom)")
    direction = input("Enter 1 or 2: ").strip()
    if direction == "1":
        flip_type = "horizontal"
    elif direction == "2":
        flip_type = "vertical"
    else:
        print_error("Invalid flip direction.")
        input("Press Enter to return to the menu...")
        return
    operation = get_file_operation_choice()
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path("Enter destination folder: ")
        if not dest_dir:
            print_error("Operation aborted as destination path was not provided.")
            input("Press Enter to return to the menu...")
            return
        os.makedirs(dest_dir, exist_ok=True)
    image_files = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not image_files:
        print_error("No image files found in the input folder.")
        input("Press Enter to return to the menu...")
        return
    print_info(f"\nFound {len(image_files)} images to flip.")
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def flip_single_image(image_file):
        try:
            input_path = os.path.join(input_folder, image_file)
            if operation == "inplace":
                output_path = input_path
            else:
                output_path = os.path.join(dest_dir, image_file)
            with Image.open(input_path) as img:
                if flip_type == "horizontal":
                    flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
                else:
                    flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
                flipped.save(output_path)
            return True
        except Exception as e:
            print_error(f"Failed to flip {image_file}: {e}")
            return False

    results = image_map(
        flip_single_image,
        image_files,
        desc="Flipping images",
        max_workers=config.max_workers,
    )
    successful = sum(1 for result in results if result)
    failed = len(results) - successful
    print_success(f"\nFlipping complete:")
    print_info(f"  Successful images: {successful}")
    print_info(f"  Failed images: {failed}")
    log_operation(
        "flip_images",
        f"flip_type={flip_type}, {operation}, {successful}/{len(image_files)} images",
    )
    input("Press Enter to return to the menu...")


def rotate_image_menu():
    """
    Menu for rotating images in a folder.
    Prompts user for rotation angle and processes all images in the folder.
    """
    from dataset_forge.utils.input_utils import (
        get_path_with_history,
        get_file_operation_choice,
        get_destination_path,
    )
    from dataset_forge.utils.printing import (
        print_header,
        print_info,
        print_error,
        print_success,
    )
    from dataset_forge.utils.color import Mocha

    print_header("Rotate Images", color=Mocha.lavender)
    input_folder = get_path_with_history("Enter path to input folder:")
    if not input_folder or not os.path.isdir(input_folder):
        print_error("Input path must be a valid directory.")
        input("Press Enter to return to the menu...")
        return
    try:
        angle = float(input("Enter rotation angle (degrees, positive=CCW): ").strip())
    except Exception:
        print_error("Invalid angle.")
        input("Press Enter to return to the menu...")
        return
    operation = get_file_operation_choice()
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path("Enter destination folder: ")
        if not dest_dir:
            print_error("Operation aborted as destination path was not provided.")
            input("Press Enter to return to the menu...")
            return
        os.makedirs(dest_dir, exist_ok=True)
    image_files = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not image_files:
        print_error("No image files found in the input folder.")
        input("Press Enter to return to the menu...")
        return
    print_info(f"\nFound {len(image_files)} images to rotate.")
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,
        use_gpu=False,
    )

    def rotate_single_image(image_file):
        try:
            input_path = os.path.join(input_folder, image_file)
            if operation == "inplace":
                output_path = input_path
            else:
                output_path = os.path.join(dest_dir, image_file)
            with Image.open(input_path) as img:
                rotated = img.rotate(angle, expand=True)
                rotated.save(output_path)
            return True
        except Exception as e:
            print_error(f"Failed to rotate {image_file}: {e}")
            return False

    results = image_map(
        rotate_single_image,
        image_files,
        desc="Rotating images",
        max_workers=config.max_workers,
    )
    successful = sum(1 for result in results if result)
    failed = len(results) - successful
    print_success(f"\nRotation complete:")
    print_info(f"  Successful images: {successful}")
    print_info(f"  Failed images: {failed}")
    log_operation(
        "rotate_images",
        f"angle={angle}, {operation}, {successful}/{len(image_files)} images",
    )
    input("Press Enter to return to the menu...")


def shuffle_images_menu():
    print_info("DEBUG: Entered shuffle_images_menu")
    try:
        from dataset_forge.utils.input_utils import (
            get_path_with_history,
            get_file_operation_choice,
            get_destination_path,
        )
        from dataset_forge.utils.printing import (
            print_header,
            print_info,
            print_error,
            print_success,
        )
        from dataset_forge.utils.color import Mocha
        from dataset_forge.actions import dataset_actions
        import os
        import random
        import shutil

        print_header("Shuffle Images", color=Mocha.lavender)
        print_info("Choose input mode:")
        print_info("  1. \U0001f4c2 HQ/LQ paired folders")
        print_info("  2. \U0001f5c1 Single folder")
        print_info("  0. \u274c Cancel")
        mode = input("\U0001f3af Select mode: ").strip()
        print_info(f"DEBUG: mode={{mode!r}}")
        if mode == "0":
            input("Press Enter to return to the menu...")
            return
        elif mode == "1":
            hq_folder = get_path_with_history("Enter HQ folder path:")
            lq_folder = get_path_with_history("Enter LQ folder path:")
            print_info(f"DEBUG: hq_folder={{hq_folder!r}}, lq_folder={{lq_folder!r}}")
            if not hq_folder or not lq_folder:
                print_error("Both HQ and LQ folder paths are required.")
                input("Press Enter to return to the menu...")
                return
            dataset_actions.shuffle_image_pairs(hq_folder, lq_folder)
            input("Press Enter to return to the menu...")
        elif mode == "2":
            folder = get_path_with_history("Enter folder path:")
            print_info(f"DEBUG: folder={{folder!r}}")
            if not folder or not os.path.isdir(folder):
                print_error("Input path must be a valid directory.")
                input("Press Enter to return to the menu...")
                return
            shuffle_images_single_folder(folder)
            input("Press Enter to return to the menu...")
        else:
            print_error("Invalid selection.")
            input("Press Enter to return to the menu...")
            return
    except Exception as e:
        from dataset_forge.utils.printing import print_error

        print_error(f"Exception in shuffle_images_menu: {e}")
        import traceback

        traceback.print_exc()
        input("Press Enter to return to the menu...")


def shuffle_images_single_folder(folder_path):
    print_info(
        f"DEBUG: Entered shuffle_images_single_folder with folder_path={{folder_path!r}}"
    )
    try:
        from dataset_forge.utils.input_utils import (
            get_file_operation_choice,
            get_destination_path,
        )
        from dataset_forge.utils.printing import print_info, print_success, print_error
        from dataset_forge.utils.file_utils import get_unique_filename, is_image_file
        from dataset_forge.utils.progress_utils import tqdm
        import os
        import random
        import shutil

        image_files = [f for f in os.listdir(folder_path) if is_image_file(f)]
        print_info(f"DEBUG: image_files={{image_files}}")
        if not image_files:
            print_error("No image files found in the folder.")
            return
        print_info(f"Found {len(image_files)} images to shuffle and rename.")
        operation = get_file_operation_choice()
        print_info(f"DEBUG: operation={{operation!r}}")
        output_dir = folder_path
        if operation != "inplace":
            output_dir = get_destination_path(
                "Enter destination folder for shuffled images:"
            )
            print_info(f"DEBUG: output_dir={{output_dir!r}}")
            if not output_dir:
                print_error(
                    f"Operation aborted as no destination path was provided for {operation}."
                )
                return
            os.makedirs(output_dir, exist_ok=True)
            print_info(
                f"Shuffled images will be {operation}d and renamed in: {output_dir}"
            )
        else:
            print_info("Shuffling and renaming files in-place within original folder.")

        # Shuffle file order
        shuffled_files = list(image_files)
        random.shuffle(shuffled_files)
        print_info(f"DEBUG: shuffled_files={{shuffled_files}}")

        # Temporary renaming for inplace shuffle to avoid collisions
        temp_suffix = "_shuffletemp_" + str(random.randint(10000, 99999))
        files_in_final_location = []

        print_info("\nStage 1: Preparing files for shuffling...")
        if operation == "inplace":
            for idx, orig_name in enumerate(
                tqdm(shuffled_files, desc="Renaming to Temp (Inplace)")
            ):
                ext = os.path.splitext(orig_name)[1]
                src_path = os.path.join(folder_path, orig_name)
                temp_name = f"{idx:05d}{temp_suffix}{ext}"
                temp_path = os.path.join(folder_path, temp_name)
                try:
                    if os.path.exists(src_path):
                        os.rename(src_path, temp_path)
                        files_in_final_location.append((temp_path, ext))
                    else:
                        print_error(f"Source {src_path} not found.")
                except Exception as e:
                    print_error(f"Error renaming {orig_name} to temporary: {e}")
        else:
            for orig_name in tqdm(
                shuffled_files, desc=f"{operation.capitalize()}ing to Destination"
            ):
                ext = os.path.splitext(orig_name)[1]
                src_path = os.path.join(folder_path, orig_name)
                dest_path = os.path.join(
                    output_dir, get_unique_filename(output_dir, orig_name)
                )
                try:
                    if operation == "copy":
                        shutil.copy2(src_path, dest_path)
                    elif operation == "move":
                        shutil.move(src_path, dest_path)
                    files_in_final_location.append((dest_path, ext))
                except Exception as e:
                    print_error(
                        f"Error {operation}ing file {orig_name} to destination: {e}"
                    )

        print_info(f"DEBUG: files_in_final_location={{files_in_final_location}}")
        print_info("\nStage 2: Renaming files to final shuffled order...")
        for idx, (current_path, ext) in enumerate(
            tqdm(files_in_final_location, desc="Final Renaming")
        ):
            new_name = f"{idx+1:05d}{ext}"
            final_path = os.path.join(os.path.dirname(current_path), new_name)
            try:
                if current_path != final_path:
                    if os.path.exists(final_path):
                        print_error(
                            f"Final Renaming: Target path {final_path} unexpectedly exists before rename."
                        )
                        continue
                    os.rename(current_path, final_path)
            except Exception as e:
                print_error(
                    f"Error during final rename of '{os.path.basename(current_path)}' to '{new_name}': {e}"
                )

        print_success("\nShuffle Images Summary")
        print_info(f"Total images considered: {len(image_files)}")
        print_info(
            f"Successfully processed (shuffled & renamed): {len(files_in_final_location)} images."
        )
        if operation == "inplace":
            print_info(f"  Files were renamed in-place in {folder_path}.")
        else:
            print_info(f"  Files were {operation}d and renamed in {output_dir}.")
        input("Press Enter to return to the menu...")
    except Exception as e:
        from dataset_forge.utils.printing import print_error

        print_error(f"Exception in shuffle_images_single_folder: {e}")
        import traceback

        traceback.print_exc()
        input("Press Enter to return to the menu...")


def resize_images_menu():
    """Menu for resizing images."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("📏 Resize Images Menu")
    print_info("Resize images to specified dimensions")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        width = int(input("Enter target width (pixels): "))
        height = int(input("Enter target height (pixels): "))
        probability = float(input("Enter probability (0.0-1.0, default 1.0): ") or "1.0")
        
        # Use the existing downsample function with custom parameters
        downsample_images_menu()
        print_success("Resize images completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error resizing images: {e}")

# Create aliases for functions with different names
flip_images_menu = flip_image_menu
crop_images_menu = crop_image_menu
rotate_images_menu = rotate_image_menu
