import os
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from tqdm import tqdm
import random
from typing import Callable, List, Dict, Any, Optional, Tuple
from dataset_forge.utils.history_log import log_operation


# --- Augmentation Operations ---
def random_horizontal_flip(img: Image.Image, p: float = 0.5) -> Image.Image:
    if random.random() < p:
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def random_vertical_flip(img: Image.Image, p: float = 0.5) -> Image.Image:
    if random.random() < p:
        return img.transpose(Image.FLIP_TOP_BOTTOM)
    return img


def random_rotation(img: Image.Image, degrees: float = 30) -> Image.Image:
    angle = random.uniform(-degrees, degrees)
    return img.rotate(angle)


def random_crop(img: Image.Image, crop_size: Tuple[int, int]) -> Image.Image:
    w, h = img.size
    th, tw = crop_size
    if w == tw and h == th:
        return img
    x1 = random.randint(0, max(0, w - tw))
    y1 = random.randint(0, max(0, h - th))
    return img.crop((x1, y1, x1 + tw, y1 + th))


def color_jitter(
    img: Image.Image, brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1
) -> Image.Image:
    if brightness > 0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1 + random.uniform(-brightness, brightness))
    if contrast > 0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1 + random.uniform(-contrast, contrast))
    if saturation > 0:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1 + random.uniform(-saturation, saturation))
    if hue > 0:
        img = np.array(img.convert("HSV"))
        img[..., 0] = (
            img[..., 0].astype(np.int16) + int(255 * random.uniform(-hue, hue))
        ) % 255
        img = Image.fromarray(img, "HSV").convert("RGB")
    return img


def random_erasing(
    img: Image.Image,
    p: float = 0.5,
    scale: Tuple[float, float] = (0.02, 0.33),
    ratio: Tuple[float, float] = (0.3, 3.3),
) -> Image.Image:
    if random.random() > p:
        return img
    w, h = img.size
    area = w * h
    for _ in range(10):
        target_area = random.uniform(*scale) * area
        aspect_ratio = random.uniform(*ratio)
        erase_w = int(round((target_area * aspect_ratio) ** 0.5))
        erase_h = int(round((target_area / aspect_ratio) ** 0.5))
        if erase_w < w and erase_h < h:
            x1 = random.randint(0, w - erase_w)
            y1 = random.randint(0, h - erase_h)
            img_np = np.array(img)
            img_np[y1 : y1 + erase_h, x1 : x1 + erase_w, :] = np.random.randint(
                0, 256, (erase_h, erase_w, 3), dtype=np.uint8
            )
            return Image.fromarray(img_np)
    return img


def mixup(img1: Image.Image, img2: Image.Image, alpha: float = 0.4) -> Image.Image:
    """Mixup two images with a given alpha."""
    arr1 = np.array(img1).astype(np.float32)
    arr2 = np.array(img2).astype(np.float32)
    lam = np.random.beta(alpha, alpha)
    mixed = lam * arr1 + (1 - lam) * arr2
    mixed = np.clip(mixed, 0, 255).astype(np.uint8)
    return Image.fromarray(mixed)


def cutout(img: Image.Image, size: int = 32, p: float = 0.5) -> Image.Image:
    if random.random() > p:
        return img
    w, h = img.size
    x = random.randint(0, w - size)
    y = random.randint(0, h - size)
    img_np = np.array(img)
    img_np[y : y + size, x : x + size, :] = 0
    return Image.fromarray(img_np)


# --- Augmentation Recipes ---
AUGMENTATION_RECIPES: Dict[str, List[Tuple[Callable, Dict[str, Any]]]] = {
    "basic": [
        (random_horizontal_flip, {"p": 0.5}),
        (random_vertical_flip, {"p": 0.5}),
        (random_crop, {"crop_size": (128, 128)}),
    ],
    "color_jitter": [
        (
            color_jitter,
            {"brightness": 0.3, "contrast": 0.3, "saturation": 0.3, "hue": 0.1},
        ),
    ],
    "geometric": [
        (random_rotation, {"degrees": 30}),
        (random_crop, {"crop_size": (128, 128)}),
    ],
    "advanced": [
        (random_horizontal_flip, {"p": 0.5}),
        (random_rotation, {"degrees": 45}),
        (random_erasing, {"p": 0.5}),
    ],
    "mixup": [
        # Mixup requires two images, so this is a special case. We'll handle it in the pipeline application.
        # For now, we provide a placeholder for UI and documentation.
        (mixup, {"alpha": 0.4}),
    ],
    "cutout": [
        (cutout, {"size": 32, "p": 0.5}),
    ],
    "full_advanced": [
        (random_horizontal_flip, {"p": 0.5}),
        (random_vertical_flip, {"p": 0.5}),
        (random_rotation, {"degrees": 30}),
        (
            color_jitter,
            {"brightness": 0.3, "contrast": 0.3, "saturation": 0.3, "hue": 0.1},
        ),
        (cutout, {"size": 32, "p": 0.5}),
        (random_erasing, {"p": 0.5}),
    ],
}


# --- Pipeline Application ---
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
    Apply an augmentation pipeline to all images in input_dir (and optionally lq_input_dir for HQ/LQ mode).
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
    files = [
        f
        for f in os.listdir(input_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))
    ]
    if recipe_name == "mixup":
        # Mixup: randomly pair images
        random.shuffle(files)
        for i in range(0, len(files) - 1, 2):
            img1 = Image.open(os.path.join(input_dir, files[i])).convert("RGB")
            img2 = Image.open(os.path.join(input_dir, files[i + 1])).convert("RGB")
            mixed = mixup(img1, img2)
            out_path = os.path.join(output_dir, f"mixup_{files[i]}_{files[i+1]}")
            mixed.save(out_path)
            log_operation("augment_mixup", f"{files[i]}, {files[i+1]} -> {out_path}")
        return
    if hq_lq_mode and lq_input_dir and lq_output_dir:
        os.makedirs(lq_output_dir, exist_ok=True)
        hq_files = sorted(files)
        lq_files = sorted(
            [
                f
                for f in os.listdir(lq_input_dir)
                if f.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")
                )
            ]
        )
        for hq_file, lq_file in zip(hq_files, lq_files):
            hq_img = Image.open(os.path.join(input_dir, hq_file)).convert("RGB")
            lq_img = Image.open(os.path.join(lq_input_dir, lq_file)).convert("RGB")
            for fn, params in recipe:
                hq_img = fn(hq_img, **params)
                lq_img = fn(lq_img, **params)
            hq_out = os.path.join(output_dir, hq_file)
            lq_out = os.path.join(lq_output_dir, lq_file)
            hq_img.save(hq_out)
            lq_img.save(lq_out)
            log_operation(
                "augment_hq_lq", f"{hq_file}, {lq_file} -> {hq_out}, {lq_out}"
            )
        return
    for f in files:
        img = Image.open(os.path.join(input_dir, f)).convert("RGB")
        for fn, params in recipe:
            img = fn(img, **params)
        out_path = os.path.join(output_dir, f)
        img.save(out_path)
        log_operation("augment", f"{f} -> {out_path}")


# --- Utilities ---
def list_recipes() -> List[str]:
    return list(AUGMENTATION_RECIPES.keys())


def get_recipe(name: str) -> List[Tuple[Callable, Dict[str, Any]]]:
    return AUGMENTATION_RECIPES[name]


def compose_recipe(
    steps: List[Tuple[Callable, Dict[str, Any]]],
) -> List[Tuple[Callable, Dict[str, Any]]]:
    return steps
