"""
Intelligent sample prioritization for Dataset Forge.

This module provides quality-based sample prioritization to optimize processing
order and improve overall dataset quality.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

from dataset_forge.utils.memory_utils import (
    clear_cuda_cache,
    to_device_safe,
    tensor_context,
)
from dataset_forge.utils.cache_utils import smart_cache
from dataset_forge.utils.gpu_acceleration import gpu_image_analysis
from dataset_forge.utils.printing import (
    print_info,
    print_warning,
    print_error,
    print_success,
)
from dataset_forge.utils.monitoring import monitor_all

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    numpy_as_np as np,
    PIL_Image as Image,
    torch,
    cv2,
)


class PrioritizationStrategy(Enum):
    """Sample prioritization strategies."""

    QUALITY_SCORE = "quality_score"
    COMPLEXITY_SCORE = "complexity_score"
    HYBRID_SCORE = "hybrid_score"
    USER_DEFINED = "user_defined"
    RANDOM = "random"


@dataclass
class SampleInfo:
    """Information about a sample for prioritization."""

    path: str
    quality_score: float = 0.0
    complexity_score: float = 0.0
    hybrid_score: float = 0.0
    user_priority: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_time: float = 0.0

    def __post_init__(self):
        """Compute hybrid score after initialization."""
        self.hybrid_score = (self.quality_score + self.complexity_score) / 2.0


@dataclass
class PrioritizationConfig:
    """Configuration for sample prioritization."""

    strategy: PrioritizationStrategy = PrioritizationStrategy.HYBRID_SCORE
    quality_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "sharpness": 0.3,
            "contrast": 0.2,
            "brightness": 0.15,
            "noise": 0.15,
            "artifacts": 0.2,
        }
    )
    complexity_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "edge_density": 0.4,
            "texture_complexity": 0.3,
            "color_variety": 0.2,
            "structural_complexity": 0.1,
        }
    )
    use_gpu: bool = True
    batch_size: int = 32
    cache_results: bool = True
    min_quality_threshold: float = 0.1
    max_quality_threshold: float = 0.9
    adaptive_thresholds: bool = True


class QualityAnalyzer:
    """
    Analyzes image quality for prioritization.

    Provides various quality metrics including sharpness, contrast,
    brightness, noise, and artifact detection.
    """

    def __init__(self, device: Optional[str] = None):
        """
        Initialize quality analyzer.

        Args:
            device: Device to use for analysis (auto-detect if None)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.logger = logging.getLogger(__name__)

    @smart_cache(ttl_seconds=7200, maxsize=1000)
    def analyze_quality(self, image_path: str) -> Dict[str, float]:
        """
        Analyze image quality metrics.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary of quality metrics
        """
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            image_array = np.array(image)

            # Analyze various quality aspects
            metrics = {}

            # Sharpness analysis
            metrics["sharpness"] = self._analyze_sharpness(image_array)

            # Contrast analysis
            metrics["contrast"] = self._analyze_contrast(image_array)

            # Brightness analysis
            metrics["brightness"] = self._analyze_brightness(image_array)

            # Noise analysis
            metrics["noise"] = self._analyze_noise(image_array)

            # Artifact detection
            metrics["artifacts"] = self._analyze_artifacts(image_array)

            return metrics

        except Exception as e:
            self.logger.error(f"Error analyzing quality for {image_path}: {e}")
            return {
                "sharpness": 0.0,
                "contrast": 0.0,
                "brightness": 0.0,
                "noise": 0.0,
                "artifacts": 0.0,
            }

    def _analyze_sharpness(self, image: np.ndarray) -> float:
        """Analyze image sharpness using Laplacian variance."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()

            # Normalize to 0-1 range (empirical values)
            normalized = min(1.0, variance / 1000.0)
            return normalized

        except Exception as e:
            self.logger.warning(f"Sharpness analysis failed: {e}")
            return 0.5

    def _analyze_contrast(self, image: np.ndarray) -> float:
        """Analyze image contrast."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Calculate contrast using standard deviation
            mean = np.mean(gray)
            std = np.std(gray)

            # Normalize to 0-1 range
            normalized = min(1.0, std / 128.0)
            return normalized

        except Exception as e:
            self.logger.warning(f"Contrast analysis failed: {e}")
            return 0.5

    def _analyze_brightness(self, image: np.ndarray) -> float:
        """Analyze image brightness."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            mean_brightness = np.mean(gray)

            # Normalize to 0-1 range (0=black, 1=white)
            normalized = mean_brightness / 255.0

            # Prefer mid-range brightness (avoid too dark or too bright)
            if normalized < 0.2 or normalized > 0.8:
                normalized *= 0.5

            return normalized

        except Exception as e:
            self.logger.warning(f"Brightness analysis failed: {e}")
            return 0.5

    def _analyze_noise(self, image: np.ndarray) -> float:
        """Analyze image noise level."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Apply Gaussian blur to get noise-free version
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Calculate noise as difference between original and blurred
            noise = np.abs(gray.astype(float) - blurred.astype(float))
            noise_level = np.mean(noise)

            # Invert so lower noise = higher quality
            normalized = max(0.0, 1.0 - (noise_level / 50.0))
            return normalized

        except Exception as e:
            self.logger.warning(f"Noise analysis failed: {e}")
            return 0.5

    def _analyze_artifacts(self, image: np.ndarray) -> float:
        """Analyze image artifacts (compression, etc.)."""
        try:
            # Simple artifact detection using edge analysis
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Count edge pixels
            edge_density = np.sum(edges > 0) / edges.size

            # High edge density might indicate compression artifacts
            # But we want some edges for good quality
            if edge_density < 0.01:  # Too few edges
                return 0.3
            elif edge_density > 0.1:  # Too many edges (possible artifacts)
                return 0.7
            else:
                return 1.0

        except Exception as e:
            self.logger.warning(f"Artifact analysis failed: {e}")
            return 0.5


class ComplexityAnalyzer:
    """
    Analyzes image complexity for prioritization.

    Provides various complexity metrics including edge density,
    texture complexity, color variety, and structural complexity.
    """

    def __init__(self, device: Optional[str] = None):
        """
        Initialize complexity analyzer.

        Args:
            device: Device to use for analysis (auto-detect if None)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.logger = logging.getLogger(__name__)

    @smart_cache(ttl_seconds=7200, maxsize=1000)
    def analyze_complexity(self, image_path: str) -> Dict[str, float]:
        """
        Analyze image complexity metrics.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary of complexity metrics
        """
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            image_array = np.array(image)

            # Analyze various complexity aspects
            metrics = {}

            # Edge density analysis
            metrics["edge_density"] = self._analyze_edge_density(image_array)

            # Texture complexity analysis
            metrics["texture_complexity"] = self._analyze_texture_complexity(
                image_array
            )

            # Color variety analysis
            metrics["color_variety"] = self._analyze_color_variety(image_array)

            # Structural complexity analysis
            metrics["structural_complexity"] = self._analyze_structural_complexity(
                image_array
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Error analyzing complexity for {image_path}: {e}")
            return {
                "edge_density": 0.5,
                "texture_complexity": 0.5,
                "color_variety": 0.5,
                "structural_complexity": 0.5,
            }

    def _analyze_edge_density(self, image: np.ndarray) -> float:
        """Analyze edge density in the image."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Apply Sobel edge detection
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

            # Calculate edge magnitude
            edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)

            # Calculate edge density
            edge_density = np.sum(edge_magnitude > 50) / edge_magnitude.size

            return min(1.0, edge_density * 10)  # Scale to 0-1

        except Exception as e:
            self.logger.warning(f"Edge density analysis failed: {e}")
            return 0.5

    def _analyze_texture_complexity(self, image: np.ndarray) -> float:
        """Analyze texture complexity using GLCM-like features."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Calculate local variance as texture measure
            kernel = np.ones((5, 5), np.float32) / 25
            mean_img = cv2.filter2D(gray.astype(float), -1, kernel)
            variance_img = cv2.filter2D(
                (gray.astype(float) - mean_img) ** 2, -1, kernel
            )

            # Average variance as texture complexity
            texture_complexity = np.mean(variance_img)

            # Normalize to 0-1 range
            normalized = min(1.0, texture_complexity / 1000.0)
            return normalized

        except Exception as e:
            self.logger.warning(f"Texture complexity analysis failed: {e}")
            return 0.5

    def _analyze_color_variety(self, image: np.ndarray) -> float:
        """Analyze color variety in the image."""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

            # Calculate color variety using hue and saturation
            hue_std = np.std(hsv[:, :, 0])
            sat_std = np.std(hsv[:, :, 1])

            # Combine hue and saturation variety
            color_variety = (hue_std + sat_std) / 2.0

            # Normalize to 0-1 range
            normalized = min(1.0, color_variety / 100.0)
            return normalized

        except Exception as e:
            self.logger.warning(f"Color variety analysis failed: {e}")
            return 0.5

    def _analyze_structural_complexity(self, image: np.ndarray) -> float:
        """Analyze structural complexity using contour analysis."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Find contours
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if not contours:
                return 0.0

            # Calculate structural complexity based on contour properties
            total_area = sum(cv2.contourArea(c) for c in contours)
            total_perimeter = sum(cv2.arcLength(c, True) for c in contours)

            if total_area == 0:
                return 0.0

            # Complexity based on perimeter-to-area ratio
            complexity = total_perimeter / total_area

            # Normalize to 0-1 range
            normalized = min(1.0, complexity / 0.1)
            return normalized

        except Exception as e:
            self.logger.warning(f"Structural complexity analysis failed: {e}")
            return 0.5


class SamplePrioritizer:
    """
    Main sample prioritization system.

    Combines quality and complexity analysis to provide intelligent
    sample prioritization for dataset processing.
    """

    def __init__(self, config: Optional[PrioritizationConfig] = None):
        """
        Initialize sample prioritizer.

        Args:
            config: Configuration for prioritization
        """
        self.config = config or PrioritizationConfig()
        self.quality_analyzer = QualityAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.logger = logging.getLogger(__name__)

    @monitor_all("prioritize_samples")
    def prioritize_samples(
        self,
        sample_paths: List[str],
        strategy: Optional[PrioritizationStrategy] = None,
        **kwargs,
    ) -> List[SampleInfo]:
        """
        Prioritize samples based on the specified strategy.

        Args:
            sample_paths: List of sample file paths
            strategy: Prioritization strategy (uses config default if None)
            **kwargs: Additional arguments

        Returns:
            List of SampleInfo objects sorted by priority
        """
        if strategy is None:
            strategy = self.config.strategy

        print_info(
            f"Prioritizing {len(sample_paths)} samples using {strategy.value} strategy"
        )

        # Analyze all samples
        sample_infos = []

        for i, path in enumerate(sample_paths):
            if i % 100 == 0:
                print_info(f"Analyzing sample {i+1}/{len(sample_paths)}")

            sample_info = self._analyze_sample(path)
            sample_infos.append(sample_info)

        # Sort based on strategy
        sorted_samples = self._sort_samples(sample_infos, strategy)

        print_success(f"Prioritization complete. Top sample: {sorted_samples[0].path}")

        return sorted_samples

    def _analyze_sample(self, path: str) -> SampleInfo:
        """Analyze a single sample for prioritization."""
        start_time = time.time()

        try:
            # Analyze quality
            quality_metrics = self.quality_analyzer.analyze_quality(path)
            quality_score = self._compute_weighted_score(
                quality_metrics, self.config.quality_weights
            )

            # Analyze complexity
            complexity_metrics = self.complexity_analyzer.analyze_complexity(path)
            complexity_score = self._compute_weighted_score(
                complexity_metrics, self.config.complexity_weights
            )

            # Create sample info
            sample_info = SampleInfo(
                path=path,
                quality_score=quality_score,
                complexity_score=complexity_score,
                metadata={
                    "quality_metrics": quality_metrics,
                    "complexity_metrics": complexity_metrics,
                },
            )

            sample_info.analysis_time = time.time() - start_time
            return sample_info

        except Exception as e:
            self.logger.error(f"Error analyzing sample {path}: {e}")
            return SampleInfo(
                path=path,
                quality_score=0.5,
                complexity_score=0.5,
                analysis_time=time.time() - start_time,
            )

    def _compute_weighted_score(
        self, metrics: Dict[str, float], weights: Dict[str, float]
    ) -> float:
        """Compute weighted score from metrics and weights."""
        total_score = 0.0
        total_weight = 0.0

        for metric, weight in weights.items():
            if metric in metrics:
                total_score += metrics[metric] * weight
                total_weight += weight

        if total_weight == 0:
            return 0.5

        return total_score / total_weight

    def _sort_samples(
        self, samples: List[SampleInfo], strategy: PrioritizationStrategy
    ) -> List[SampleInfo]:
        """Sort samples based on prioritization strategy."""
        if strategy == PrioritizationStrategy.QUALITY_SCORE:
            return sorted(samples, key=lambda x: x.quality_score, reverse=True)

        elif strategy == PrioritizationStrategy.COMPLEXITY_SCORE:
            return sorted(samples, key=lambda x: x.complexity_score, reverse=True)

        elif strategy == PrioritizationStrategy.HYBRID_SCORE:
            return sorted(samples, key=lambda x: x.hybrid_score, reverse=True)

        elif strategy == PrioritizationStrategy.USER_DEFINED:
            return sorted(samples, key=lambda x: x.user_priority, reverse=True)

        elif strategy == PrioritizationStrategy.RANDOM:
            import random

            random.shuffle(samples)
            return samples

        else:
            raise ValueError(f"Unknown prioritization strategy: {strategy}")

    def get_priority_batches(
        self, samples: List[SampleInfo], batch_size: int, adaptive: bool = True
    ) -> List[List[SampleInfo]]:
        """
        Create priority-based batches for processing.

        Args:
            samples: List of prioritized samples
            batch_size: Size of each batch
            adaptive: Whether to use adaptive batch sizes

        Returns:
            List of sample batches
        """
        if not adaptive:
            # Simple batching
            return [
                samples[i : i + batch_size] for i in range(0, len(samples), batch_size)
            ]

        # Adaptive batching based on priority
        batches = []
        current_batch = []
        current_priority_sum = 0.0

        for sample in samples:
            current_batch.append(sample)
            current_priority_sum += sample.hybrid_score

            # Create batch if size reached or priority threshold met
            if (
                len(current_batch) >= batch_size
                or current_priority_sum >= batch_size * 0.7
            ):
                batches.append(current_batch)
                current_batch = []
                current_priority_sum = 0.0

        # Add remaining samples
        if current_batch:
            batches.append(current_batch)

        return batches


# Global instances
sample_prioritizer = SamplePrioritizer()


# Convenience functions
def prioritize_samples(
    sample_paths: List[str],
    strategy: PrioritizationStrategy = PrioritizationStrategy.HYBRID_SCORE,
    **kwargs,
) -> List[SampleInfo]:
    """Convenience function for sample prioritization."""
    return sample_prioritizer.prioritize_samples(sample_paths, strategy, **kwargs)


def get_priority_batches(
    samples: List[SampleInfo], batch_size: int, adaptive: bool = True
) -> List[List[SampleInfo]]:
    """Convenience function for creating priority batches."""
    return sample_prioritizer.get_priority_batches(samples, batch_size, adaptive)
