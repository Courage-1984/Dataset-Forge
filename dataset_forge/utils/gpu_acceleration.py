"""
GPU-accelerated preprocessing operations for Dataset Forge.

This module provides GPU-accelerated versions of common image processing operations
that are identified as bottlenecks in the current implementation.
"""

import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF
import numpy as np
import cv2
from typing import Union, Tuple, List, Optional, Dict, Any
from PIL import Image
import logging

from dataset_forge.utils.memory_utils import (
    clear_cuda_cache,
    to_device_safe,
    safe_cuda_operation,
    tensor_context,
)
from dataset_forge.utils.cache_utils import smart_cache
from dataset_forge.utils.printing import print_info, print_warning, print_error


class GPUImageProcessor:
    """
    GPU-accelerated image processing operations.

    This class provides GPU-accelerated versions of common image processing
    operations that are bottlenecks in the current implementation.
    """

    def __init__(self, device: Optional[str] = None, batch_size: int = 32):
        """
        Initialize GPU image processor.

        Args:
            device: CUDA device to use (auto-detect if None)
            batch_size: Default batch size for operations
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = batch_size
        self.logger = logging.getLogger(__name__)

        # Initialize GPU if available
        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.logger.info(
                f"GPU acceleration initialized on {torch.cuda.get_device_name(0)}"
            )
        else:
            self.logger.warning("GPU not available, falling back to CPU")

    def _to_tensor(
        self, image: Union[np.ndarray, Image.Image, torch.Tensor]
    ) -> torch.Tensor:
        """Convert image to tensor format."""
        if isinstance(image, torch.Tensor):
            return image
        elif isinstance(image, np.ndarray):
            if image.dtype != np.float32:
                image = image.astype(np.float32)
            if image.max() > 1.0:
                image = image / 255.0
            if image.ndim == 2:
                image = np.stack([image] * 3, axis=-1)
            return torch.from_numpy(image.transpose(2, 0, 1)).unsqueeze(0)
        elif isinstance(image, Image.Image):
            return TF.to_tensor(image).unsqueeze(0)
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")

    def _to_pil(self, tensor: torch.Tensor) -> Image.Image:
        """Convert tensor back to PIL Image."""
        if tensor.dim() == 4:
            tensor = tensor.squeeze(0)
        return TF.to_pil_image(tensor)

    @smart_cache(ttl_seconds=3600, maxsize=100)
    def gpu_brightness_contrast(
        self,
        image: Union[np.ndarray, Image.Image],
        brightness: float = 1.0,
        contrast: float = 1.0,
    ) -> Image.Image:
        """
        GPU-accelerated brightness and contrast adjustment.

        Args:
            image: Input image
            brightness: Brightness factor (0.0-2.0)
            contrast: Contrast factor (0.0-2.0)

        Returns:
            Adjusted image
        """
        with tensor_context(self.device):
            tensor = self._to_tensor(image)
            tensor = to_device_safe(tensor, self.device)

            # Apply brightness and contrast
            tensor = TF.adjust_brightness(tensor, brightness)
            tensor = TF.adjust_contrast(tensor, contrast)

            return self._to_pil(tensor)

    @smart_cache(ttl_seconds=3600, maxsize=100)
    def gpu_saturation_hue(
        self,
        image: Union[np.ndarray, Image.Image],
        saturation: float = 1.0,
        hue: float = 0.0,
    ) -> Image.Image:
        """
        GPU-accelerated saturation and hue adjustment.

        Args:
            image: Input image
            saturation: Saturation factor (0.0-2.0)
            hue: Hue shift (-0.5 to 0.5)

        Returns:
            Adjusted image
        """
        with tensor_context(self.device):
            tensor = self._to_tensor(image)
            tensor = to_device_safe(tensor, self.device)

            # Apply saturation and hue
            tensor = TF.adjust_saturation(tensor, saturation)
            tensor = TF.adjust_hue(tensor, hue)

            return self._to_pil(tensor)

    @smart_cache(ttl_seconds=3600, maxsize=100)
    def gpu_sharpness_blur(
        self,
        image: Union[np.ndarray, Image.Image],
        sharpness: float = 1.0,
        blur_radius: float = 0.0,
    ) -> Image.Image:
        """
        GPU-accelerated sharpness and blur adjustment.

        Args:
            image: Input image
            sharpness: Sharpness factor (0.0-2.0)
            blur_radius: Blur radius (0.0-5.0)

        Returns:
            Adjusted image
        """
        with tensor_context(self.device):
            tensor = self._to_tensor(image)
            tensor = to_device_safe(tensor, self.device)

            # Apply sharpness
            if sharpness != 1.0:
                tensor = TF.adjust_sharpness(tensor, sharpness)

            # Apply blur
            if blur_radius > 0.0:
                kernel_size = max(3, int(blur_radius * 2) * 2 + 1)
                sigma = blur_radius / 3.0
                tensor = TF.gaussian_blur(tensor, kernel_size, sigma)

            return self._to_pil(tensor)

    def gpu_batch_transform(
        self,
        images: List[Union[np.ndarray, Image.Image]],
        transform_config: Dict[str, Any],
    ) -> List[Image.Image]:
        """
        GPU-accelerated batch image transformation.

        Args:
            images: List of input images
            transform_config: Dictionary with transformation parameters

        Returns:
            List of transformed images
        """
        results = []

        # Process in batches
        for i in range(0, len(images), self.batch_size):
            batch = images[i : i + self.batch_size]
            batch_tensors = []

            # Convert batch to tensors
            with tensor_context(self.device):
                for img in batch:
                    tensor = self._to_tensor(img)
                    tensor = to_device_safe(tensor, self.device)
                    batch_tensors.append(tensor)

                # Stack batch
                batch_tensor = torch.cat(batch_tensors, dim=0)

                # Apply transformations
                if "brightness" in transform_config or "contrast" in transform_config:
                    brightness = transform_config.get("brightness", 1.0)
                    contrast = transform_config.get("contrast", 1.0)
                    batch_tensor = TF.adjust_brightness(batch_tensor, brightness)
                    batch_tensor = TF.adjust_contrast(batch_tensor, contrast)

                if "saturation" in transform_config or "hue" in transform_config:
                    saturation = transform_config.get("saturation", 1.0)
                    hue = transform_config.get("hue", 0.0)
                    batch_tensor = TF.adjust_saturation(batch_tensor, saturation)
                    batch_tensor = TF.adjust_hue(batch_tensor, hue)

                if "sharpness" in transform_config or "blur" in transform_config:
                    sharpness = transform_config.get("sharpness", 1.0)
                    blur_radius = transform_config.get("blur", 0.0)
                    if sharpness != 1.0:
                        batch_tensor = TF.adjust_sharpness(batch_tensor, sharpness)
                    if blur_radius > 0.0:
                        kernel_size = max(3, int(blur_radius * 2) * 2 + 1)
                        sigma = blur_radius / 3.0
                        batch_tensor = TF.gaussian_blur(
                            batch_tensor, kernel_size, sigma
                        )

                # Convert back to PIL images
                for j in range(batch_tensor.size(0)):
                    results.append(self._to_pil(batch_tensor[j]))

        return results

    @smart_cache(ttl_seconds=1800, maxsize=50)
    def gpu_image_analysis(
        self, image: Union[np.ndarray, Image.Image]
    ) -> Dict[str, Any]:
        """
        GPU-accelerated image analysis.

        Args:
            image: Input image

        Returns:
            Dictionary with analysis results
        """
        with tensor_context(self.device):
            tensor = self._to_tensor(image)
            tensor = to_device_safe(tensor, self.device)

            # Compute statistics
            mean = torch.mean(tensor)
            std = torch.std(tensor)
            min_val = torch.min(tensor)
            max_val = torch.max(tensor)

            # Compute histogram (simplified)
            hist = torch.histc(tensor, bins=256, min=0, max=1)

            # Compute edge strength (simplified)
            if tensor.size(1) > 1 and tensor.size(2) > 1:
                # Sobel edge detection
                sobel_x = torch.tensor(
                    [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                    dtype=torch.float32,
                    device=self.device,
                ).view(1, 1, 3, 3)
                sobel_y = torch.tensor(
                    [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                    dtype=torch.float32,
                    device=self.device,
                ).view(1, 1, 3, 3)

                gray = TF.rgb_to_grayscale(tensor)
                edge_x = F.conv2d(gray, sobel_x, padding=1)
                edge_y = F.conv2d(gray, sobel_y, padding=1)
                edge_magnitude = torch.sqrt(edge_x**2 + edge_y**2)
                edge_strength = torch.mean(edge_magnitude).item()
            else:
                edge_strength = 0.0

            return {
                "mean": mean.item(),
                "std": std.item(),
                "min": min_val.item(),
                "max": max_val.item(),
                "edge_strength": edge_strength,
                "size": (tensor.size(2), tensor.size(3)),
                "channels": tensor.size(1),
            }

    def gpu_sift_keypoints(
        self, image: Union[np.ndarray, Image.Image]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        GPU-accelerated SIFT keypoint detection (using PyTorch-based implementation).

        Args:
            image: Input image

        Returns:
            Tuple of (keypoints, descriptors)
        """
        # Note: This is a simplified GPU-accelerated SIFT implementation
        # For production use, consider using kornia or similar libraries

        with tensor_context(self.device):
            tensor = self._to_tensor(image)
            tensor = to_device_safe(tensor, self.device)

            # Convert to grayscale for keypoint detection
            if tensor.size(1) == 3:
                gray = TF.rgb_to_grayscale(tensor)
            else:
                gray = tensor

            # Simplified keypoint detection using gradient magnitude
            # In practice, you'd use a proper SIFT implementation
            grad_x = F.conv2d(
                gray,
                torch.tensor(
                    [[-1, 0, 1]], dtype=torch.float32, device=self.device
                ).view(1, 1, 1, 3),
                padding=(0, 1),
            )
            grad_y = F.conv2d(
                gray,
                torch.tensor(
                    [[-1], [0], [1]], dtype=torch.float32, device=self.device
                ).view(1, 1, 3, 1),
                padding=(1, 0),
            )

            magnitude = torch.sqrt(grad_x**2 + grad_y**2)

            # Find local maxima as keypoints (simplified)
            # This is a basic implementation - real SIFT is more complex
            keypoints = []
            descriptors = []

            # For now, return empty arrays - implement proper SIFT later
            return np.array([]), np.array([])

    def cleanup(self):
        """Clean up GPU memory."""
        if self.device == "cuda":
            clear_cuda_cache()


# Global instance for easy access
gpu_processor = GPUImageProcessor()


# Convenience functions
def gpu_brightness_contrast(image, brightness=1.0, contrast=1.0):
    """Convenience function for GPU brightness/contrast adjustment."""
    return gpu_processor.gpu_brightness_contrast(image, brightness, contrast)


def gpu_saturation_hue(image, saturation=1.0, hue=0.0):
    """Convenience function for GPU saturation/hue adjustment."""
    return gpu_processor.gpu_saturation_hue(image, saturation, hue)


def gpu_sharpness_blur(image, sharpness=1.0, blur_radius=0.0):
    """Convenience function for GPU sharpness/blur adjustment."""
    return gpu_processor.gpu_sharpness_blur(image, sharpness, blur_radius)


def gpu_batch_transform(images, transform_config):
    """Convenience function for GPU batch transformation."""
    return gpu_processor.gpu_batch_transform(images, transform_config)


def gpu_image_analysis(image):
    """Convenience function for GPU image analysis."""
    return gpu_processor.gpu_image_analysis(image)
