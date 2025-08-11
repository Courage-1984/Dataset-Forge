import os
from typing import Optional
from PIL import Image, ImageFilter
from dataset_forge.utils.memory_utils import auto_cleanup, memory_context, clear_memory
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.printing import print_success, print_error
from dataset_forge.utils.file_utils import is_image_file
from dataset_forge.utils.history_log import log_operation
import numpy as np


@auto_cleanup
def apply_blur_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    blur_type: str = "gauss",
    kernel_size: int = 3,
    probability: float = 0.5,
) -> None:
    """
    Apply blur degradation to all images in a folder.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (Optional[str]): Path to the output folder. If None and in_place is False, raises error.
        in_place (bool): If True, overwrite images in input_folder. If False, write to output_folder.
        blur_type (str): Type of blur to apply ('gauss', 'box', 'median').
        kernel_size (int): Kernel size for the blur.
        probability (float): Probability of applying blur to each image (0.0-1.0).

    Raises:
        FileNotFoundError: If input_folder does not exist.
        ValueError: If output_folder is not specified when in_place is False.

    Example:
        apply_blur_degradation('input/', 'output/', False, 'gauss', 3, 0.5)
    """
    import random

    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)

    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return

    processed = 0
    with memory_context("Blur Degradation"):
        for img_name in tqdm(images, desc="Applying Blur"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    # Copy original if not applying blur
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    if blur_type == "gauss":
                        blurred = img.filter(
                            ImageFilter.GaussianBlur(radius=kernel_size)
                        )
                    elif blur_type == "box":
                        blurred = img.filter(ImageFilter.BoxBlur(radius=kernel_size))
                    elif blur_type == "median":
                        blurred = img.filter(ImageFilter.MedianFilter(size=kernel_size))
                    else:
                        print_error(
                            f"Unknown blur type: {blur_type}. Skipping {img_name}."
                        )
                        continue
                    out_path = (
                        img_path if in_place else os.path.join(output_folder, img_name)
                    )
                    blurred.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("blur_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Blur degradation applied to {processed} images.")
    log_operation("blur_degradation", f"Processed {processed} images in {input_folder}")
    clear_memory()


@auto_cleanup
def apply_noise_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    noise_type: str = "gauss",
    alpha: float = 0.2,
    probability: float = 0.5,
) -> None:
    """
    Apply noise degradation to all images in a folder.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (Optional[str]): Path to the output folder. If None and in_place is False, raises error.
        in_place (bool): If True, overwrite images in input_folder. If False, write to output_folder.
        noise_type (str): Type of noise to apply ('gauss', 'uniform', 'salt', 'pepper').
        alpha (float): Noise intensity (0.0-1.0).
        probability (float): Probability of applying noise to each image (0.0-1.0).
    """
    import numpy as np

    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Noise Degradation"):
        for img_name in tqdm(images, desc="Applying Noise"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    arr = np.array(img)
                    if noise_type == "gauss":
                        noise = np.random.normal(0, alpha * 255, arr.shape).astype(
                            np.int16
                        )
                        noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
                    elif noise_type == "uniform":
                        noise = np.random.uniform(
                            -alpha * 255, alpha * 255, arr.shape
                        ).astype(np.int16)
                        noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
                    elif noise_type == "salt":
                        noisy = arr.copy()
                        num_salt = np.ceil(alpha * arr.size)
                        coords = [
                            np.random.randint(0, i - 1, int(num_salt))
                            for i in arr.shape
                        ]
                        noisy[tuple(coords)] = 255
                    elif noise_type == "pepper":
                        noisy = arr.copy()
                        num_pepper = np.ceil(alpha * arr.size)
                        coords = [
                            np.random.randint(0, i - 1, int(num_pepper))
                            for i in arr.shape
                        ]
                        noisy[tuple(coords)] = 0
                    else:
                        print_error(
                            f"Unknown noise type: {noise_type}. Skipping {img_name}."
                        )
                        continue
                    out_img = Image.fromarray(noisy)
                    out_path = (
                        img_path if in_place else os.path.join(output_folder, img_name)
                    )
                    out_img.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("noise_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Noise degradation applied to {processed} images.")
    log_operation(
        "noise_degradation", f"Processed {processed} images in {input_folder}"
    )
    clear_memory()


@auto_cleanup
def apply_compress_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    algorithm: str = "jpeg",
    quality: int = 50,
    probability: float = 0.5,
) -> None:
    """
    Apply compression degradation to all images in a folder.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (Optional[str]): Path to the output folder. If None and in_place is False, raises error.
        in_place (bool): If True, overwrite images in input_folder. If False, write to output_folder.
        algorithm (str): Compression algorithm ('jpeg', 'webp').
        quality (int): Compression quality (lower = more compression, 1-100).
        probability (float): Probability of applying compression to each image (0.0-1.0).
    """
    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Compress Degradation"):
        for img_name in tqdm(images, desc="Applying Compression"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    out_path = (
                        img_path if in_place else os.path.join(output_folder, img_name)
                    )
                    if algorithm == "jpeg":
                        img = img.convert("RGB")
                        img.save(out_path, format="JPEG", quality=quality)
                    elif algorithm == "webp":
                        img.save(out_path, format="WEBP", quality=quality)
                    else:
                        print_error(
                            f"Unknown compression algorithm: {algorithm}. Skipping {img_name}."
                        )
                        continue
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("compress_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Compression degradation applied to {processed} images.")
    log_operation(
        "compress_degradation", f"Processed {processed} images in {input_folder}"
    )
    clear_memory()


@auto_cleanup
def apply_pixelate_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    size: int = 8,
    probability: float = 0.5,
) -> None:
    """
    Apply pixelate degradation to all images in a folder.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (Optional[str]): Path to the output folder. If None and in_place is False, raises error.
        in_place (bool): If True, overwrite images in input_folder. If False, write to output_folder.
        size (int): Pixel block size (2-32 recommended).
        probability (float): Probability of applying pixelate to each image (0.0-1.0).
    """
    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Pixelate Degradation"):
        for img_name in tqdm(images, desc="Applying Pixelate"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    w, h = img.size
                    img_small = img.resize(
                        (max(1, w // size), max(1, h // size)), resample=Image.NEAREST
                    )
                    pixelated = img_small.resize((w, h), Image.NEAREST)
                    out_path = (
                        img_path if in_place else os.path.join(output_folder, img_name)
                    )
                    pixelated.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("pixelate_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Pixelate degradation applied to {processed} images.")
    log_operation(
        "pixelate_degradation", f"Processed {processed} images in {input_folder}"
    )
    clear_memory()


@auto_cleanup
def apply_color_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    high: int = 255,
    low: int = 0,
    gamma: float = 1.0,
    probability: float = 0.5,
) -> None:
    """
    Apply color degradation (contrast/brightness/gamma) to all images in a folder.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (Optional[str]): Path to the output folder. If None and in_place is False, raises error.
        in_place (bool): If True, overwrite images in input_folder. If False, write to output_folder.
        high (int): Max brightness (200-255 typical).
        low (int): Min darkness (0-50 typical).
        gamma (float): Gamma correction (0.8-1.2 typical).
        probability (float): Probability of applying color degradation to each image (0.0-1.0).
    """
    import numpy as np

    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Color Degradation"):
        for img_name in tqdm(images, desc="Applying Color"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    arr = np.array(img).astype(np.float32)
                    arr = (arr - arr.min()) / (
                        arr.max() - arr.min() + 1e-8
                    )  # normalize
                    arr = arr * (high - low) + low
                    arr = np.clip(arr, 0, 255)
                    arr = arr**gamma
                    arr = np.clip(arr, 0, 255).astype(np.uint8)
                    out_img = Image.fromarray(arr)
                    out_path = (
                        img_path if in_place else os.path.join(output_folder, img_name)
                    )
                    out_img.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("color_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Color degradation applied to {processed} images.")
    log_operation(
        "color_degradation", f"Processed {processed} images in {input_folder}"
    )
    clear_memory()


@auto_cleanup
def apply_saturation_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    rand: float = 0.7,
    probability: float = 0.5,
) -> None:
    """
    Apply saturation degradation to all images in a folder.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (Optional[str]): Path to the output folder. If None and in_place is False, raises error.
        in_place (bool): If True, overwrite images in input_folder. If False, write to output_folder.
        rand (float): Random saturation factor (0.0-1.0).
        probability (float): Probability of applying saturation to each image (0.0-1.0).
    """
    from PIL import ImageEnhance

    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Saturation Degradation"):
        for img_name in tqdm(images, desc="Applying Saturation"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    enhancer = ImageEnhance.Color(img)
                    factor = np.random.uniform(0.0, rand)
                    saturated = enhancer.enhance(factor)
                    out_path = (
                        img_path if in_place else os.path.join(output_folder, img_name)
                    )
                    saturated.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("saturation_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Saturation degradation applied to {processed} images.")
    log_operation(
        "saturation_degradation", f"Processed {processed} images in {input_folder}"
    )
    clear_memory()


@auto_cleanup
def apply_dithering_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    dithering_type: str = "quantize",
    color_ch: int = 8,
    probability: float = 0.5,
) -> None:
    """
    Apply dithering degradation to all images in a folder.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (Optional[str]): Path to the output folder. If None and in_place is False, raises error.
        in_place (bool): If True, overwrite images in input_folder. If False, write to output_folder.
        dithering_type (str): Dithering algorithm ('quantize', 'floydsteinberg', 'atkinson', 'sierra', 'burkes').
        color_ch (int): Number of color channels (2-16 typical).
        probability (float): Probability of applying dithering to each image (0.0-1.0).
    """
    from PIL import Image

    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Dithering Degradation"):
        for img_name in tqdm(images, desc="Applying Dithering"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    if dithering_type == "quantize":
                        dithered = img.convert(
                            "P", palette=Image.ADAPTIVE, colors=color_ch
                        ).convert("RGB")
                    elif dithering_type == "floydsteinberg":
                        dithered = img.convert(
                            "1", dither=Image.FLOYDSTEINBERG
                        ).convert("RGB")
                    elif dithering_type == "atkinson":
                        # PIL does not support Atkinson, fallback to quantize
                        dithered = img.convert(
                            "P", palette=Image.ADAPTIVE, colors=color_ch
                        ).convert("RGB")
                    elif dithering_type == "sierra":
                        # PIL does not support Sierra, fallback to quantize
                        dithered = img.convert(
                            "P", palette=Image.ADAPTIVE, colors=color_ch
                        ).convert("RGB")
                    elif dithering_type == "burkes":
                        # PIL does not support Burkes, fallback to quantize
                        dithered = img.convert(
                            "P", palette=Image.ADAPTIVE, colors=color_ch
                        ).convert("RGB")
                    else:
                        print_error(
                            f"Unknown dithering type: {dithering_type}. Skipping {img_name}."
                        )
                        continue
                    out_path = (
                        img_path if in_place else os.path.join(output_folder, img_name)
                    )
                    dithered.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("dithering_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Dithering degradation applied to {processed} images.")
    log_operation(
        "dithering_degradation", f"Processed {processed} images in {input_folder}"
    )
    clear_memory()


@auto_cleanup
def apply_subsampling_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    sampling: str = "4:2:0",
    blur: float = 0.0,
    probability: float = 0.5,
) -> None:
    """
    Apply chroma subsampling degradation to all images in a folder.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (Optional[str]): Path to the output folder. If None and in_place is False, raises error.
        in_place (bool): If True, overwrite images in input_folder. If False, write to output_folder.
        sampling (str): Chroma subsampling format ('4:4:4', '4:2:2', '4:2:0').
        blur (float): Optional blur kernel size (0.0-4.0).
        probability (float): Probability of applying subsampling to each image (0.0-1.0).
    """
    import cv2

    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Subsampling Degradation"):
        for img_name in tqdm(images, desc="Applying Subsampling"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                img = cv2.imread(img_path)
                if img is None:
                    print_error(f"Failed to read {img_name} with OpenCV.")
                    continue
                if sampling == "4:4:4":
                    out_img = img
                elif sampling == "4:2:2":
                    out_img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
                    out_img[:, :, 1] = cv2.resize(
                        out_img[:, :, 1],
                        (img.shape[1] // 2, img.shape[0]),
                        interpolation=cv2.INTER_LINEAR,
                    )
                    out_img[:, :, 2] = cv2.resize(
                        out_img[:, :, 2],
                        (img.shape[1] // 2, img.shape[0]),
                        interpolation=cv2.INTER_LINEAR,
                    )
                    out_img = cv2.cvtColor(out_img, cv2.COLOR_YUV2BGR)
                elif sampling == "4:2:0":
                    out_img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
                    out_img[:, :, 1] = cv2.resize(
                        out_img[:, :, 1],
                        (img.shape[1] // 2, img.shape[0] // 2),
                        interpolation=cv2.INTER_LINEAR,
                    )
                    out_img[:, :, 2] = cv2.resize(
                        out_img[:, :, 2],
                        (img.shape[1] // 2, img.shape[0] // 2),
                        interpolation=cv2.INTER_LINEAR,
                    )
                    out_img = cv2.cvtColor(out_img, cv2.COLOR_YUV2BGR)
                else:
                    print_error(f"Unknown sampling: {sampling}. Skipping {img_name}.")
                    continue
                if blur > 0.0:
                    k = int(blur)
                    if k % 2 == 0:
                        k += 1
                    out_img = cv2.GaussianBlur(out_img, (k, k), 0)
                out_path = (
                    img_path if in_place else os.path.join(output_folder, img_name)
                )
                cv2.imwrite(out_path, out_img)
                processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("subsampling_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Subsampling degradation applied to {processed} images.")
    log_operation(
        "subsampling_degradation", f"Processed {processed} images in {input_folder}"
    )
    clear_memory()


@auto_cleanup
def apply_screentone_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    dot_size: int = 7,
    dot_type: str = "circle",
    angle: int = 0,
    probability: float = 0.5,
) -> None:
    """
    Apply screentone degradation to all images in a folder.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (Optional[str]): Path to the output folder. If None and in_place is False, raises error.
        in_place (bool): If True, overwrite images in input_folder. If False, write to output_folder.
        dot_size (int): Size of screentone pattern (4-16 typical).
        dot_type (str): Pattern type ('circle', 'diamond', 'line').
        angle (int): Pattern angle (-45 to 45).
        probability (float): Probability of applying screentone to each image (0.0-1.0).
    """
    # Simple screentone simulation: overlay dots/lines
    from PIL import ImageDraw

    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Screentone Degradation"):
        for img_name in tqdm(images, desc="Applying Screentone"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    img = img.convert("L")
                    overlay = Image.new("L", img.size, 255)
                    draw = ImageDraw.Draw(overlay)
                    w, h = img.size
                    for y in range(0, h, dot_size):
                        for x in range(0, w, dot_size):
                            if dot_type == "circle":
                                draw.ellipse(
                                    [x, y, x + dot_size // 2, y + dot_size // 2], fill=0
                                )
                            elif dot_type == "diamond":
                                draw.polygon(
                                    [
                                        (x + dot_size // 2, y),
                                        (x + dot_size, y + dot_size // 2),
                                        (x + dot_size // 2, y + dot_size),
                                        (x, y + dot_size // 2),
                                    ],
                                    fill=0,
                                )
                            elif dot_type == "line":
                                draw.line([(x, y), (x + dot_size, y)], fill=0, width=1)
                    # Simple angle: rotate overlay
                    if angle != 0:
                        overlay = overlay.rotate(angle, expand=0)
                    screentoned = Image.composite(overlay, img, overlay)
                    out_path = (
                        img_path if in_place else os.path.join(output_folder, img_name)
                    )
                    screentoned.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("screentone_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Screentone degradation applied to {processed} images.")
    log_operation(
        "screentone_degradation", f"Processed {processed} images in {input_folder}"
    )
    clear_memory()

@auto_cleanup
def apply_halo_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    type_halo: str = "unsharp_mask",
    kernel: int = 2,
    amount: float = 1.0,
    threshold: float = 0.0,
    probability: float = 0.5,
) -> None:
    """
    Apply halo (unsharp mask) degradation to all images in a folder.
    """
    from PIL import ImageFilter, ImageEnhance
    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Halo Degradation"):
        for img_name in tqdm(images, desc="Applying Halo"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    if type_halo == "unsharp_mask":
                        haloed = img.filter(ImageFilter.UnsharpMask(radius=kernel, percent=int(amount*150), threshold=int(threshold*255)))
                    elif type_halo == "unsharp_halo":
                        # Simulate by boosting contrast after unsharp mask
                        haloed = img.filter(ImageFilter.UnsharpMask(radius=kernel, percent=int(amount*150), threshold=int(threshold*255)))
                        enhancer = ImageEnhance.Contrast(haloed)
                        haloed = enhancer.enhance(1.5)
                    elif type_halo == "unsharp_gray":
                        haloed = img.convert("L").filter(ImageFilter.UnsharpMask(radius=kernel, percent=int(amount*150), threshold=int(threshold*255)))
                    else:
                        print_error(f"Unknown halo type: {type_halo}. Skipping {img_name}.")
                        continue
                    out_path = img_path if in_place else os.path.join(output_folder, img_name)
                    haloed.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("halo_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Halo degradation applied to {processed} images.")
    log_operation("halo_degradation", f"Processed {processed} images in {input_folder}")
    clear_memory()

@auto_cleanup
def apply_sin_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    shape: int = 200,
    alpha: float = 0.3,
    bias: float = 0.0,
    vertical: float = 0.5,
    probability: float = 0.5,
) -> None:
    """
    Apply sinusoidal pattern degradation to all images in a folder.
    """
    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Sin Degradation"):
        for img_name in tqdm(images, desc="Applying Sin"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    arr = np.array(img).astype(np.float32)
                    h, w = arr.shape[:2]
                    if random.random() < vertical:
                        x = np.arange(h).reshape(-1, 1)
                        pattern = np.sin(2 * np.pi * x / shape)
                        pattern = np.tile(pattern, (1, w))
                    else:
                        x = np.arange(w)
                        pattern = np.sin(2 * np.pi * x / shape)
                        pattern = np.tile(pattern, (h, 1))
                    pattern = (pattern * alpha * 255 + bias * 255).astype(np.float32)
                    if arr.ndim == 3:
                        for c in range(arr.shape[2]):
                            arr[..., c] = np.clip(arr[..., c] + pattern, 0, 255)
                    else:
                        arr = np.clip(arr + pattern, 0, 255)
                    out_img = Image.fromarray(arr.astype(np.uint8))
                    out_path = img_path if in_place else os.path.join(output_folder, img_name)
                    out_img.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("sin_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Sin degradation applied to {processed} images.")
    log_operation("sin_degradation", f"Processed {processed} images in {input_folder}")
    clear_memory()

@auto_cleanup
def apply_shift_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    shift_type: str = "rgb",
    percent: bool = False,
    amount: int = 2,
    probability: float = 0.5,
) -> None:
    """
    Apply color channel shift degradation to all images in a folder.
    """
    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Shift Degradation"):
        for img_name in tqdm(images, desc="Applying Shift"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    arr = np.array(img)
                    if shift_type == "rgb" and arr.ndim == 3:
                        for c in range(3):
                            shift = int(amount if not percent else arr.shape[1] * amount / 100)
                            arr[..., c] = np.roll(arr[..., c], shift, axis=1)
                    # For simplicity, only implement RGB shift here
                    out_img = Image.fromarray(arr)
                    out_path = img_path if in_place else os.path.join(output_folder, img_name)
                    out_img.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("shift_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Shift degradation applied to {processed} images.")
    log_operation("shift_degradation", f"Processed {processed} images in {input_folder}")
    clear_memory()

@auto_cleanup
def apply_canny_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    thread1: int = 100,
    thread2: int = 50,
    aperture_size: int = 3,
    scale: float = 0.5,
    white: float = 0.0,
    probability: float = 0.5,
) -> None:
    """
    Apply Canny edge detection degradation to all images in a folder.
    """
    import cv2
    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Canny Degradation"):
        for img_name in tqdm(images, desc="Applying Canny"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    print_error(f"Failed to read {img_name} with OpenCV.")
                    continue
                edges = cv2.Canny(img, thread1, thread2, apertureSize=aperture_size)
                if scale > 0:
                    k = int(scale * 5)
                    if k > 1:
                        edges = cv2.dilate(edges, np.ones((k, k), np.uint8), iterations=1)
                if white >= 0.5:
                    edges = 255 - edges
                out_path = img_path if in_place else os.path.join(output_folder, img_name)
                cv2.imwrite(out_path, edges)
                processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("canny_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Canny degradation applied to {processed} images.")
    log_operation("canny_degradation", f"Processed {processed} images in {input_folder}")
    clear_memory()

@auto_cleanup
def apply_resize_degradation(
    input_folder: str,
    output_folder: Optional[str] = None,
    in_place: bool = False,
    alg_lq: str = "box",
    scale: float = 0.5,
    probability: float = 0.5,
) -> None:
    """
    Apply resize degradation to all images in a folder.
    """
    if not os.path.isdir(input_folder):
        print_error(f"Input folder does not exist: {input_folder}")
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    if not in_place and not output_folder:
        print_error("Output folder must be specified if not running in-place.")
        raise ValueError("Output folder must be specified if not running in-place.")
    if not in_place:
        os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if is_image_file(f)]
    if not images:
        print_error("No image files found in input folder.")
        return
    processed = 0
    with memory_context("Resize Degradation"):
        for img_name in tqdm(images, desc="Applying Resize"):
            img_path = os.path.join(input_folder, img_name)
            try:
                if random.random() > probability:
                    if not in_place:
                        Image.open(img_path).save(os.path.join(output_folder, img_name))
                    continue
                with Image.open(img_path) as img:
                    w, h = img.size
                    new_w, new_h = int(w * scale), int(h * scale)
                    if alg_lq == "box":
                        resized = img.resize((new_w, new_h), Image.BOX)
                    elif alg_lq == "hermite":
                        resized = img.resize((new_w, new_h), Image.HAMMING)
                    elif alg_lq == "linear":
                        resized = img.resize((new_w, new_h), Image.BILINEAR)
                    elif alg_lq == "lagrange":
                        resized = img.resize((new_w, new_h), Image.BICUBIC)
                    elif alg_lq == "cubic_catrom":
                        resized = img.resize((new_w, new_h), Image.BICUBIC)
                    elif alg_lq == "cubic_mitchell":
                        resized = img.resize((new_w, new_h), Image.BICUBIC)
                    elif alg_lq == "cubic_bspline":
                        resized = img.resize((new_w, new_h), Image.BICUBIC)
                    elif alg_lq == "lanczos":
                        resized = img.resize((new_w, new_h), Image.LANCZOS)
                    elif alg_lq == "gauss":
                        resized = img.resize((new_w, new_h), Image.BILINEAR)
                    else:
                        print_error(f"Unknown resize algorithm: {alg_lq}. Skipping {img_name}.")
                        continue
                    # Optionally resize back to original size to simulate LQ/HQ pair
                    resized = resized.resize((w, h), Image.BILINEAR)
                    out_path = img_path if in_place else os.path.join(output_folder, img_name)
                    resized.save(out_path)
                    processed += 1
            except Exception as e:
                print_error(f"Failed to process {img_name}: {e}")
                log_operation("resize_degradation", f"Failed: {img_name}: {e}")
    print_success(f"Resize degradation applied to {processed} images.")
    log_operation("resize_degradation", f"Processed {processed} images in {input_folder}")
    clear_memory()

# Menu functions for degradations menu
def blur_degradation_menu():
    """Menu for blur degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🌀 Blur Degradation Menu")
    print_info("Apply blur effects to images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    options = {
        "1": ("Gaussian Blur", "gauss"),
        "2": ("Box Blur", "box"),
        "3": ("Median Blur", "median"),
        "0": ("⬅️ Back", None)
    }
    
    menu_context = {
        "Purpose": "Configure blur degradation settings",
        "Options": "3 blur types available",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
        "Key Features": ["Gaussian blur for natural blur", "Box blur for uniform blur", "Median blur for noise reduction"]
    }
    
    while True:
        key = show_menu("Blur Type Selection", options, Mocha.lavender, current_menu="Blur Degradation", menu_context=menu_context)
        if key is None or key == "0":
            return
        blur_type = options[key][1]
        if blur_type:
            try:
                kernel_size = int(input("Enter kernel size (1-10, default 3): ") or "3")
                probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
                
                apply_blur_degradation(
                    input_folder=input_folder,
                    output_folder=output_folder,
                    in_place=in_place,
                    blur_type=blur_type,
                    kernel_size=kernel_size,
                    probability=probability
                )
                print_success("Blur degradation completed!")
                break
            except ValueError as e:
                print_error(f"Invalid input: {e}")
            except Exception as e:
                print_error(f"Error applying blur degradation: {e}")

def noise_degradation_menu():
    """Menu for noise degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🎲 Noise Degradation Menu")
    print_info("Add noise to images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    options = {
        "1": ("Gaussian Noise", "gauss"),
        "2": ("Salt & Pepper Noise", "salt"),
        "0": ("⬅️ Back", None)
    }
    
    menu_context = {
        "Purpose": "Configure noise degradation settings",
        "Options": "2 noise types available",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
        "Key Features": ["Gaussian noise for realistic noise", "Salt & pepper for impulse noise"]
    }
    
    while True:
        key = show_menu("Noise Type Selection", options, Mocha.lavender, current_menu="Noise Degradation", menu_context=menu_context)
        if key is None or key == "0":
            return
        noise_type = options[key][1]
        if noise_type:
            try:
                alpha = float(input("Enter noise intensity (0.0-1.0, default 0.2): ") or "0.2")
                probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
                
                apply_noise_degradation(
                    input_folder=input_folder,
                    output_folder=output_folder,
                    in_place=in_place,
                    noise_type=noise_type,
                    alpha=alpha,
                    probability=probability
                )
                print_success("Noise degradation completed!")
                break
            except ValueError as e:
                print_error(f"Invalid input: {e}")
            except Exception as e:
                print_error(f"Error applying noise degradation: {e}")

def compress_degradation_menu():
    """Menu for compression degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🗜️ Compression Degradation Menu")
    print_info("Apply compression artifacts to images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    options = {
        "1": ("JPEG Compression", "jpeg"),
        "2": ("WebP Compression", "webp"),
        "0": ("⬅️ Back", None)
    }
    
    menu_context = {
        "Purpose": "Configure compression degradation settings",
        "Options": "2 compression types available",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
        "Key Features": ["JPEG compression artifacts", "WebP compression artifacts"]
    }
    
    while True:
        key = show_menu("Compression Type Selection", options, Mocha.lavender, current_menu="Compression Degradation", menu_context=menu_context)
        if key is None or key == "0":
            return
        algorithm = options[key][1]
        if algorithm:
            try:
                quality = int(input("Enter quality (1-100, default 50): ") or "50")
                probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
                
                apply_compress_degradation(
                    input_folder=input_folder,
                    output_folder=output_folder,
                    in_place=in_place,
                    algorithm=algorithm,
                    quality=quality,
                    probability=probability
                )
                print_success("Compression degradation completed!")
                break
            except ValueError as e:
                print_error(f"Invalid input: {e}")
            except Exception as e:
                print_error(f"Error applying compression degradation: {e}")

def pixelate_degradation_menu():
    """Menu for pixelate degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🟫 Pixelate Degradation Menu")
    print_info("Apply pixelation to images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        size = int(input("Enter pixel size (2-32, default 8): ") or "8")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        apply_pixelate_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            size=size,
            probability=probability
        )
        print_success("Pixelate degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying pixelate degradation: {e}")

def color_degradation_menu():
    """Menu for color degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🎨 Color Degradation Menu")
    print_info("Apply color modifications to images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        high = int(input("Enter high value (0-255, default 255): ") or "255")
        low = int(input("Enter low value (0-255, default 0): ") or "0")
        gamma = float(input("Enter gamma value (0.1-3.0, default 1.0): ") or "1.0")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        apply_color_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            high=high,
            low=low,
            gamma=gamma,
            probability=probability
        )
        print_success("Color degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying color degradation: {e}")

def saturation_degradation_menu():
    """Menu for saturation degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🌈 Saturation Degradation Menu")
    print_info("Modify image saturation")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        rand = float(input("Enter saturation factor (0.0-2.0, default 0.7): ") or "0.7")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        apply_saturation_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            rand=rand,
            probability=probability
        )
        print_success("Saturation degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying saturation degradation: {e}")

def dithering_degradation_menu():
    """Menu for dithering degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🖼️ Dithering Degradation Menu")
    print_info("Apply dithering effects to images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    options = {
        "1": ("Quantize", "quantize"),
        "2": ("Floyd-Steinberg", "floyd"),
        "0": ("⬅️ Back", None)
    }
    
    menu_context = {
        "Purpose": "Configure dithering degradation settings",
        "Options": "2 dithering types available",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
        "Key Features": ["Quantize for color reduction", "Floyd-Steinberg for error diffusion"]
    }
    
    while True:
        key = show_menu("Dithering Type Selection", options, Mocha.lavender, current_menu="Dithering Degradation", menu_context=menu_context)
        if key is None or key == "0":
            return
        dithering_type = options[key][1]
        if dithering_type:
            try:
                color_ch = int(input("Enter color channels (2-256, default 8): ") or "8")
                probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
                
                apply_dithering_degradation(
                    input_folder=input_folder,
                    output_folder=output_folder,
                    in_place=in_place,
                    dithering_type=dithering_type,
                    color_ch=color_ch,
                    probability=probability
                )
                print_success("Dithering degradation completed!")
                break
            except ValueError as e:
                print_error(f"Invalid input: {e}")
            except Exception as e:
                print_error(f"Error applying dithering degradation: {e}")

def subsampling_degradation_menu():
    """Menu for subsampling degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🧩 Subsampling Degradation Menu")
    print_info("Apply chroma subsampling to images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    options = {
        "1": ("4:2:0 Subsampling", "4:2:0"),
        "2": ("4:2:2 Subsampling", "4:2:2"),
        "3": ("4:1:1 Subsampling", "4:1:1"),
        "0": ("⬅️ Back", None)
    }
    
    menu_context = {
        "Purpose": "Configure subsampling degradation settings",
        "Options": "3 subsampling types available",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
        "Key Features": ["4:2:0 for maximum compression", "4:2:2 for moderate compression", "4:1:1 for aggressive compression"]
    }
    
    while True:
        key = show_menu("Subsampling Type Selection", options, Mocha.lavender, current_menu="Subsampling Degradation", menu_context=menu_context)
        if key is None or key == "0":
            return
        sampling = options[key][1]
        if sampling:
            try:
                blur = float(input("Enter blur amount (0.0-1.0, default 0.0): ") or "0.0")
                probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
                
                apply_subsampling_degradation(
                    input_folder=input_folder,
                    output_folder=output_folder,
                    in_place=in_place,
                    sampling=sampling,
                    blur=blur,
                    probability=probability
                )
                print_success("Subsampling degradation completed!")
                break
            except ValueError as e:
                print_error(f"Invalid input: {e}")
            except Exception as e:
                print_error(f"Error applying subsampling degradation: {e}")

def sharpen_degradation_menu():
    """Menu for sharpen degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("✨ Sharpen Degradation Menu")
    print_info("Apply sharpening effects to images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        kernel_size = int(input("Enter kernel size (1-10, default 3): ") or "3")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use the halo degradation with unsharp mask for sharpening
        apply_halo_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            type_halo="unsharp_mask",
            kernel=kernel_size,
            amount=1.0,
            threshold=0.0,
            probability=probability
        )
        print_success("Sharpen degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying sharpen degradation: {e}")

def downscale_degradation_menu():
    """Menu for downscale degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("⬇️ Downscale Degradation Menu")
    print_info("Downscale images and upscale back")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        scale = float(input("Enter scale factor (0.1-0.9, default 0.5): ") or "0.5")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        apply_resize_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            alg_lq="box",
            scale=scale,
            probability=probability
        )
        print_success("Downscale degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying downscale degradation: {e}")

def posterize_degradation_menu():
    """Menu for posterize degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🖍️ Posterize Degradation Menu")
    print_info("Reduce color levels in images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        levels = int(input("Enter color levels (2-256, default 8): ") or "8")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use dithering with quantize for posterize effect
        apply_dithering_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            dithering_type="quantize",
            color_ch=levels,
            probability=probability
        )
        print_success("Posterize degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying posterize degradation: {e}")

def bitdepth_degradation_menu():
    """Menu for bit depth degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🕳️ Bit Depth Degradation Menu")
    print_info("Reduce bit depth of images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        bits = int(input("Enter bit depth (1-8, default 4): ") or "4")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use dithering with quantize for bit depth reduction
        levels = 2 ** bits
        apply_dithering_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            dithering_type="quantize",
            color_ch=levels,
            probability=probability
        )
        print_success("Bit depth degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying bit depth degradation: {e}")

def banding_degradation_menu():
    """Menu for banding degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🟪 Banding Degradation Menu")
    print_info("Apply color banding effects")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        levels = int(input("Enter color levels (2-64, default 16): ") or "16")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use dithering without error diffusion for banding
        apply_dithering_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            dithering_type="quantize",
            color_ch=levels,
            probability=probability
        )
        print_success("Banding degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying banding degradation: {e}")

def jpeg2000_degradation_menu():
    """Menu for JPEG2000 degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🏞️ JPEG2000 Degradation Menu")
    print_info("Apply JPEG2000 compression artifacts")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        quality = int(input("Enter quality (1-100, default 30): ") or "30")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use compression with JPEG2000-like settings
        apply_compress_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            algorithm="jpeg",
            quality=quality,
            probability=probability
        )
        print_success("JPEG2000 degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying JPEG2000 degradation: {e}")

def moire_degradation_menu():
    """Menu for moiré pattern degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("📶 Moiré Pattern Degradation Menu")
    print_info("Apply moiré pattern effects")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        frequency = int(input("Enter frequency (10-200, default 50): ") or "50")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use sine wave degradation for moiré effect
        apply_sin_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            shape=frequency,
            alpha=0.3,
            bias=0.0,
            vertical=0.5,
            probability=probability
        )
        print_success("Moiré pattern degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying moiré pattern degradation: {e}")

def vignetting_degradation_menu():
    """Menu for vignetting degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🌑 Vignetting Degradation Menu")
    print_info("Apply vignetting effects to images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        intensity = float(input("Enter vignetting intensity (0.0-1.0, default 0.5): ") or "0.5")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use color degradation with gamma for vignetting effect
        apply_color_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            high=255,
            low=0,
            gamma=1.0 + intensity,
            probability=probability
        )
        print_success("Vignetting degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying vignetting degradation: {e}")

def lens_distortion_degradation_menu():
    """Menu for lens distortion degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🔄 Lens Distortion Degradation Menu")
    print_info("Apply lens distortion effects")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        distortion = float(input("Enter distortion amount (-1.0 to 1.0, default 0.1): ") or "0.1")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use shift degradation for lens distortion simulation
        apply_shift_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            shift_type="rgb",
            percent=True,
            amount=int(distortion * 10),
            probability=probability
        )
        print_success("Lens distortion degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying lens distortion degradation: {e}")

def color_shift_degradation_menu():
    """Menu for color shift degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🎭 Color Shift Degradation Menu")
    print_info("Apply color channel shifts")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        shift_amount = int(input("Enter shift amount (1-10, default 2): ") or "2")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        apply_shift_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            shift_type="rgb",
            percent=False,
            amount=shift_amount,
            probability=probability
        )
        print_success("Color shift degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying color shift degradation: {e}")

def channel_swap_degradation_menu():
    """Menu for channel swap degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🔀 Channel Swap Degradation Menu")
    print_info("Swap color channels in images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use shift degradation with RGB shift for channel swap effect
        apply_shift_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            shift_type="rgb",
            percent=False,
            amount=5,
            probability=probability
        )
        print_success("Channel swap degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying channel swap degradation: {e}")

def block_shuffle_degradation_menu():
    """Menu for block shuffle degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🧊 Block Shuffle Degradation Menu")
    print_info("Shuffle image blocks")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        block_size = int(input("Enter block size (8-64, default 16): ") or "16")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use pixelate degradation for block shuffle effect
        apply_pixelate_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            size=block_size,
            probability=probability
        )
        print_success("Block shuffle degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying block shuffle degradation: {e}")

def random_erasing_degradation_menu():
    """Menu for random erasing degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("❌ Random Erasing Degradation Menu")
    print_info("Randomly erase parts of images")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        erasure_ratio = float(input("Enter erasure ratio (0.1-0.5, default 0.2): ") or "0.2")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use noise degradation with salt & pepper for random erasing effect
        apply_noise_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            noise_type="salt",
            alpha=erasure_ratio,
            probability=probability
        )
        print_success("Random erasing degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying random erasing degradation: {e}")

def color_jitter_degradation_menu():
    """Menu for color jitter degradation settings."""
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.input_utils import get_folder_path
    from dataset_forge.utils.printing import print_info, print_success, print_error
    
    print_info("🎚️ Color Jitter Degradation Menu")
    print_info("Apply random color variations")
    
    input_folder = get_folder_path("Enter input folder path: ")
    if not input_folder:
        return
    
    output_folder = get_folder_path("Enter output folder path (or press Enter for in-place): ")
    in_place = not output_folder
    
    try:
        jitter_amount = float(input("Enter jitter amount (0.1-0.5, default 0.2): ") or "0.2")
        probability = float(input("Enter probability (0.0-1.0, default 0.5): ") or "0.5")
        
        # Use color degradation with random parameters for jitter effect
        apply_color_degradation(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            high=255,
            low=0,
            gamma=1.0 + jitter_amount,
            probability=probability
        )
        print_success("Color jitter degradation completed!")
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        print_error(f"Error applying color jitter degradation: {e}")
