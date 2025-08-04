"""
GPU-accelerated preprocessing operations for Dataset Forge.

This module provides GPU-accelerated versions of common image processing operations
that are identified as bottlenecks in the current implementation.
"""

# Use lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    torch,
    torch_nn_functional as F,
    torchvision_transforms as transforms,
    torchvision_transforms_functional as TF,
    numpy_as_np as np,
    cv2,
    PIL_Image as Image,
)
from typing import Union, Tuple, List, Optional, Dict, Any
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
        self, image: Union[np.ndarray, Image.Image, "torch.Tensor"]
    ) -> "torch.Tensor":
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

    def _to_pil(self, tensor: "torch.Tensor") -> Image.Image:
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
            # Convert to tensor
            tensor = self._to_tensor(image)
            
            # Apply brightness and contrast
            if brightness != 1.0:
                tensor = TF.adjust_brightness(tensor, brightness)
            if contrast != 1.0:
                tensor = TF.adjust_contrast(tensor, contrast)
            
            # Convert back to PIL
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
            # Convert to tensor
            tensor = self._to_tensor(image)
            
            # Apply saturation and hue
            if saturation != 1.0:
                tensor = TF.adjust_saturation(tensor, saturation)
            if hue != 0.0:
                tensor = TF.adjust_hue(tensor, hue)
            
            # Convert back to PIL
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
            # Convert to tensor
            tensor = self._to_tensor(image)
            
            # Apply sharpness
            if sharpness != 1.0:
                tensor = TF.adjust_sharpness(tensor, sharpness)
            
            # Apply blur if needed
            if blur_radius > 0.0:
                # Convert blur radius to kernel size
                kernel_size = max(3, int(blur_radius * 2) * 2 + 1)
                tensor = TF.gaussian_blur(tensor, [kernel_size, kernel_size], [blur_radius])
            
            # Convert back to PIL
            return self._to_pil(tensor)

    def gpu_batch_transform(
        self,
        images: List[Union[np.ndarray, Image.Image]],
        transform_config: Dict[str, Any],
    ) -> List[Image.Image]:
        """
        GPU-accelerated batch transformation.

        Args:
            images: List of input images
            transform_config: Configuration dictionary for transformations

        Returns:
            List of transformed images
        """
        with tensor_context(self.device):
            # Convert all images to tensors
            tensors = [self._to_tensor(img) for img in images]
            
            # Stack tensors for batch processing
            batch_tensor = torch.cat(tensors, dim=0)
            
            # Apply transformations
            for transform_name, transform_params in transform_config.items():
                if transform_name == "brightness":
                    batch_tensor = TF.adjust_brightness(batch_tensor, transform_params)
                elif transform_name == "contrast":
                    batch_tensor = TF.adjust_contrast(batch_tensor, transform_params)
                elif transform_name == "saturation":
                    batch_tensor = TF.adjust_saturation(batch_tensor, transform_params)
                elif transform_name == "hue":
                    batch_tensor = TF.adjust_hue(batch_tensor, transform_params)
                elif transform_name == "sharpness":
                    batch_tensor = TF.adjust_sharpness(batch_tensor, transform_params)
                elif transform_name == "gaussian_blur":
                    kernel_size = transform_params.get("kernel_size", 3)
                    sigma = transform_params.get("sigma", 1.0)
                    batch_tensor = TF.gaussian_blur(batch_tensor, [kernel_size, kernel_size], [sigma])
            
            # Convert back to PIL images
            return [self._to_pil(tensor) for tensor in batch_tensor]

    @smart_cache(ttl_seconds=1800, maxsize=50)
    def gpu_image_analysis(
        self, image: Union[np.ndarray, Image.Image]
    ) -> Dict[str, Any]:
        """
        GPU-accelerated image analysis.

        Args:
            image: Input image

        Returns:
            Dictionary containing analysis results
        """
        with tensor_context(self.device):
            # Convert to tensor
            tensor = self._to_tensor(image)
            
            # Calculate basic statistics
            mean = torch.mean(tensor)
            std = torch.std(tensor)
            min_val = torch.min(tensor)
            max_val = torch.max(tensor)
            
            # Calculate histogram (simplified)
            hist = torch.histc(tensor, bins=256, min=0, max=1)
            
            # Calculate edge detection using Sobel
            # Convert to grayscale for edge detection
            if tensor.shape[1] == 3:  # RGB image
                # Convert to grayscale using luminance weights
                gray_tensor = 0.299 * tensor[:, 0:1, :, :] + 0.587 * tensor[:, 1:2, :, :] + 0.114 * tensor[:, 2:3, :, :]
            else:
                gray_tensor = tensor
            
            # Apply Sobel filters
            sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            
            edges_x = F.conv2d(gray_tensor, sobel_x, padding=1)
            edges_y = F.conv2d(gray_tensor, sobel_y, padding=1)
            edges = torch.sqrt(edges_x**2 + edges_y**2)
            edge_strength = torch.mean(edges)
            
            return {
                "mean": mean.item(),
                "std": std.item(),
                "min": min_val.item(),
                "max": max_val.item(),
                "edge_strength": edge_strength.item(),
                "histogram": hist.cpu().numpy().tolist(),
                "size": (tensor.shape[2], tensor.shape[3]),  # (height, width)
            }

    def gpu_sift_keypoints(
        self, image: Union[np.ndarray, Image.Image]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        GPU-accelerated SIFT keypoint detection.

        Args:
            image: Input image

        Returns:
            Tuple of (keypoints, descriptors)
        """
        # Convert to numpy array for OpenCV
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Ensure image is in correct format
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Initialize SIFT detector
        sift = cv2.SIFT_create()
        
        # Detect keypoints and compute descriptors
        keypoints, descriptors = sift.detectAndCompute(image, None)
        
        # Convert keypoints to numpy array
        keypoints_array = np.array([kp.pt for kp in keypoints])
        
        return keypoints_array, descriptors

    def cleanup(self):
        """Clean up GPU resources."""
        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.logger.info("GPU cache cleared")


# Convenience functions for direct use
def gpu_brightness_contrast(image, brightness=1.0, contrast=1.0):
    """Convenience function for GPU brightness/contrast adjustment."""
    processor = GPUImageProcessor()
    return processor.gpu_brightness_contrast(image, brightness, contrast)


def gpu_saturation_hue(image, saturation=1.0, hue=0.0):
    """Convenience function for GPU saturation/hue adjustment."""
    processor = GPUImageProcessor()
    return processor.gpu_saturation_hue(image, saturation, hue)


def gpu_sharpness_blur(image, sharpness=1.0, blur_radius=0.0):
    """Convenience function for GPU sharpness/blur adjustment."""
    processor = GPUImageProcessor()
    return processor.gpu_sharpness_blur(image, sharpness, blur_radius)


def gpu_batch_transform(images, transform_config):
    """Convenience function for GPU batch transformation."""
    processor = GPUImageProcessor()
    return processor.gpu_batch_transform(images, transform_config)


def gpu_image_analysis(image):
    """Convenience function for GPU image analysis."""
    processor = GPUImageProcessor()
    return processor.gpu_image_analysis(image)
