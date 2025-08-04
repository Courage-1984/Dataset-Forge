#!/usr/bin/env python3
"""
Image operations utilities for Dataset Forge.

This module provides various image processing operations including
alpha channel removal, corruption fixing, and color adjustments.
"""

import os
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Tuple, Union

from PIL import Image, ImageEnhance, ImageCms
from tqdm import tqdm

from dataset_forge.utils.printing import print_error
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.cache_utils import in_memory_cache


class ImageOperation(ABC):
    """Abstract base class for image operations."""

    @abstractmethod
    def process(self, image_path, **kwargs):
        """Process an image and return success status and result."""
        pass


class AlphaRemover(ImageOperation):
    """Remove alpha channel from images."""

    def process(self, image_path, output_path=None, operation="inplace"):
        """Remove alpha channel from an image."""
        try:
            with Image.open(image_path) as img:
                if img.mode in ("RGBA", "LA", "PA"):
                    # Convert to RGB or L depending on original mode
                    if img.mode == "RGBA":
                        rgb_img = img.convert("RGB")
                    elif img.mode == "LA":
                        rgb_img = img.convert("L")
                    elif img.mode == "PA":
                        rgb_img = img.convert("P")
                    else:
                        return False, f"Unsupported mode with alpha: {img.mode}"
                    
                    save_path = output_path if output_path else image_path
                    rgb_img.save(save_path, quality=95)
                    return True, save_path
                else:
                    # Image doesn't have alpha channel - this is not an error, just informational
                    return True, f"No alpha channel to remove in {img.mode} mode (already processed)"
        except Exception as e:
            return False, str(e)


class CorruptionFixer(ImageOperation):
    """Fix corrupted images by re-saving them."""

    def __init__(self, grayscale=False):
        self.grayscale = grayscale

    def process(self, image_path, output_path=None, operation="inplace"):
        """Fix corrupted image by re-saving it."""
        try:
            with Image.open(image_path) as img:
                if self.grayscale:
                    img = img.convert("L")
                else:
                    img = img.convert("RGB")
                
                save_path = output_path if output_path else image_path
                img.save(save_path, quality=95)
                return True, save_path
        except Exception as e:
            return False, str(e)


class ColorAdjuster(ImageOperation):
    """Adjust color properties of images."""

    def __init__(self, adjustment_type, factor):
        self.adjustment_type = adjustment_type
        self.factor = factor

    def process(self, image_path, output_path=None, operation="inplace"):
        """Apply color adjustment to an image."""
        try:
            with Image.open(image_path) as img:
                if self.adjustment_type == "brightness":
                    enhancer = ImageEnhance.Brightness(img)
                elif self.adjustment_type == "contrast":
                    enhancer = ImageEnhance.Contrast(img)
                elif self.adjustment_type == "color":
                    enhancer = ImageEnhance.Color(img)
                elif self.adjustment_type == "sharpness":
                    enhancer = ImageEnhance.Sharpness(img)
                else:
                    return False, f"Unknown adjustment type: {self.adjustment_type}"
                img_enhanced = enhancer.enhance(self.factor)
                save_path = output_path if output_path else image_path
                img_enhanced.save(save_path, quality=95)
                return True, save_path
        except Exception as e:
            return False, str(e)


class ICCToSRGBConverter:
    @staticmethod
    def process_image(input_path, output_path):
        """Process a single image by applying its ICC profile and converting to sRGB while preserving alpha."""
        try:
            img = Image.open(input_path)
            has_alpha = "A" in img.getbands()
            if has_alpha:
                alpha = img.split()[-1]
                rgb_img = img.convert("RGB")
            else:
                rgb_img = img
            if "icc_profile" in img.info:
                input_profile = ImageCms.ImageCmsProfile(
                    BytesIO(img.info["icc_profile"])
                )
                srgb_profile = ImageCms.createProfile("sRGB")
                rgb_converted = ImageCms.profileToProfile(
                    rgb_img, input_profile, srgb_profile, outputMode="RGB"
                )
            else:
                rgb_converted = rgb_img
            if has_alpha:
                channels = list(rgb_converted.split())
                channels.append(alpha)
                final_image = Image.merge("RGBA", channels)
            else:
                final_image = rgb_converted
            final_image.save(output_path, "PNG", icc_profile=None)
            log_operation("icc_to_srgb", f"Converted ICC to sRGB for {input_path}")
        except Exception as e:
            print_error(f"Error processing {input_path}: {str(e)}")

    @staticmethod
    def process_folder(input_folder, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        files_to_process = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp")
                ):
                    input_path = os.path.join(root, file)
                    relative_path = os.path.relpath(input_path, input_folder)
                    # In-place: overwrite original file, keep extension
                    if os.path.abspath(input_folder) == os.path.abspath(output_folder):
                        output_path = input_path
                    else:
                        output_path = os.path.join(
                            output_folder, os.path.splitext(relative_path)[0] + ".png"
                        )
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    files_to_process.append((input_path, output_path))
        for input_path, output_path in tqdm(files_to_process, desc="Converting images"):
            ICCToSRGBConverter.process_image(input_path, output_path)

    @staticmethod
    def process_input(input_path, output_path):
        if os.path.isfile(input_path):
            ICCToSRGBConverter.process_image(input_path, output_path)
        elif os.path.isdir(input_path):
            ICCToSRGBConverter.process_folder(input_path, output_path)
        else:
            print_error(f"Invalid input: {input_path} is neither a file nor a directory.")


@in_memory_cache(maxsize=256, ttl_seconds=3600)  # Cache for 1 hour
def get_image_size(image_path):
    """
    Returns (width, height) of the image at image_path.

    Note:
        This function is cached in-memory for fast repeated access to the same image.
        Cache expires after 1 hour to handle potential file modifications.
    """
    with Image.open(image_path) as img:
        return img.width, img.height
