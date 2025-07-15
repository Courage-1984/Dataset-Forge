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
