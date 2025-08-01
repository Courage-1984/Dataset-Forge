"""
Parallel processing utilities for Dataset Forge.

This module provides comprehensive multiprocessing and multithreading capabilities
for accelerating image processing operations across the Dataset Forge project.
"""

import os
import multiprocessing as mp
import threading
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed,
    Executor,
)
from typing import Callable, List, Any, Optional, Dict, Tuple, Union, Iterator
import functools
import time
import logging
from dataclasses import dataclass
from enum import Enum

from dataset_forge.utils.printing import print_info, print_warning

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    numpy_as_np as np,
    torch,
)


class ProcessingType(Enum):
    """Types of parallel processing available."""

    THREAD = "thread"
    PROCESS = "process"
    AUTO = "auto"


@dataclass
class ParallelConfig:
    """Configuration for parallel processing."""

    max_workers: Optional[int] = None
    processing_type: ProcessingType = ProcessingType.AUTO
    chunk_size: int = 1
    timeout: Optional[float] = None
    use_gpu: bool = True
    gpu_memory_fraction: float = 0.8
    cpu_only: bool = False

    def __post_init__(self):
        if self.max_workers is None:
            if self.processing_type == ProcessingType.THREAD:
                # For I/O bound tasks, use more threads
                self.max_workers = min(32, (os.cpu_count() or 1) * 4)
            elif self.processing_type == ProcessingType.PROCESS:
                # For CPU bound tasks, use CPU count
                self.max_workers = os.cpu_count() or 1
            else:  # AUTO
                self.max_workers = os.cpu_count() or 1


class ParallelProcessor:
    """
    Main parallel processing class that handles both multiprocessing and multithreading.

    This class provides a unified interface for parallel processing with automatic
    optimization based on the task type and system resources.
    """

    def __init__(self, config: Optional[ParallelConfig] = None):
        """
        Initialize the parallel processor.

        Args:
            config: Configuration for parallel processing
        """
        self.config = config or ParallelConfig()
        self._executor: Optional[Executor] = None
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for parallel operations."""
        self.logger = logging.getLogger(__name__)

    def _determine_processing_type(
        self, func: Callable, *args, **kwargs
    ) -> ProcessingType:
        """
        Automatically determine the best processing type based on function characteristics.

        Args:
            func: Function to be processed
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            ProcessingType: Recommended processing type
        """
        if self.config.processing_type != ProcessingType.AUTO:
            return self.config.processing_type

        # Check if function uses GPU
        func_name = get_func_name(func).lower()
        gpu_keywords = ["cuda", "gpu", "torch", "model", "neural", "ai", "ml"]
        if any(keyword in func_name for keyword in gpu_keywords):
            return ProcessingType.THREAD  # GPU operations should use threads

        # Check if function is I/O bound
        io_keywords = ["read", "write", "save", "load", "file", "image", "cv2", "pil"]
        if any(keyword in func_name for keyword in io_keywords):
            return ProcessingType.THREAD  # I/O bound tasks use threads

        # Default to process for CPU-bound tasks
        return ProcessingType.PROCESS

    def _create_executor(self, processing_type: ProcessingType) -> Executor:
        """
        Create the appropriate executor based on processing type.

        Args:
            processing_type: Type of processing to use

        Returns:
            Executor: ThreadPoolExecutor or ProcessPoolExecutor
        """
        if processing_type == ProcessingType.THREAD:
            return ThreadPoolExecutor(max_workers=self.config.max_workers)
        else:
            return ProcessPoolExecutor(max_workers=self.config.max_workers)

    def _setup_gpu_environment(self):
        """Setup GPU environment for parallel processing."""
        if not self.config.use_gpu or self.config.cpu_only:
            return

        if torch.cuda.is_available():
            # Import centralized memory management
            from dataset_forge.utils.memory_utils import get_memory_manager

            # Set GPU memory fraction to prevent OOM
            torch.cuda.set_per_process_memory_fraction(self.config.gpu_memory_fraction)
            # Set device for current process
            torch.cuda.set_device(0)

            # Clear cache after setup
            get_memory_manager().clear_cuda_cache()

    def process_map(
        self,
        func: Callable,
        items: List[Any],
        desc: str = "Processing",
        processing_type: Optional[ProcessingType] = None,
        **kwargs,
    ) -> List[Any]:
        """
        Process items in parallel using map-style interface.

        Args:
            func: Function to apply to each item
            items: List of items to process
            desc: Description for progress bar
            processing_type: Override processing type
            **kwargs: Additional arguments to pass to func

        Returns:
            List of results
        """
        if not items:
            return []

        # Determine processing type
        if processing_type is None:
            processing_type = self._determine_processing_type(func, items[0], **kwargs)

        # Create partial function with kwargs
        partial_func = functools.partial(func, **kwargs)

        # Setup GPU environment
        self._setup_gpu_environment()

        # Process items
        with self._create_executor(processing_type) as executor:
            from dataset_forge.utils.progress_utils import tqdm

            if processing_type == ProcessingType.THREAD:
                results = list(
                    tqdm(executor.map(partial_func, items), total=len(items), desc=desc)
                )
            else:
                # For process pool, we need to handle chunks
                results = list(
                    tqdm(
                        executor.map(
                            partial_func, items, chunksize=self.config.chunk_size
                        ),
                        total=len(items),
                        desc=desc,
                    )
                )

        return results

    def process_submit(
        self,
        func: Callable,
        items: List[Any],
        desc: str = "Processing",
        processing_type: Optional[ProcessingType] = None,
        **kwargs,
    ) -> List[Any]:
        """
        Process items in parallel using submit-style interface.

        Args:
            func: Function to apply to each item
            items: List of items to process
            desc: Description for progress bar
            processing_type: Override processing type
            **kwargs: Additional arguments to pass to func

        Returns:
            List of results
        """
        if not items:
            return []

        # Determine processing type
        if processing_type is None:
            processing_type = self._determine_processing_type(func, items[0], **kwargs)

        # Create partial function with kwargs
        partial_func = functools.partial(func, **kwargs)

        # Setup GPU environment
        self._setup_gpu_environment()

        results = []
        with self._create_executor(processing_type) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(partial_func, item): item for item in items
            }

            # Collect results with progress bar
            from dataset_forge.utils.progress_utils import tqdm

            with tqdm(total=len(items), desc=desc) as pbar:
                for future in as_completed(future_to_item, timeout=self.config.timeout):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        item = future_to_item[future]
                        self.logger.error(f"Error processing item {item}: {e}")
                        results.append(None)
                    finally:
                        pbar.update(1)

        return results

    def process_batches(
        self,
        func: Callable,
        items: List[Any],
        batch_size: int,
        desc: str = "Processing",
        processing_type: Optional[ProcessingType] = None,
        **kwargs,
    ) -> List[Any]:
        """
        Process items in batches for memory efficiency.

        Args:
            func: Function to apply to each batch
            items: List of items to process
            batch_size: Size of each batch
            desc: Description for progress bar
            processing_type: Override processing type
            **kwargs: Additional arguments to pass to func

        Returns:
            List of results
        """
        if not items:
            return []

        # Determine processing type
        if processing_type is None:
            processing_type = self._determine_processing_type(
                func, items[:batch_size], **kwargs
            )

        # Create partial function with kwargs
        partial_func = functools.partial(func, **kwargs)

        # Setup GPU environment
        self._setup_gpu_environment()

        results = []
        batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]

        with self._create_executor(processing_type) as executor:
            from dataset_forge.utils.progress_utils import tqdm

            with tqdm(total=len(items), desc=desc) as pbar:
                for batch in batches:
                    try:
                        result = partial_func(batch)
                        if isinstance(result, list):
                            results.extend(result)
                        else:
                            results.append(result)
                        pbar.update(len(batch))
                    except Exception as e:
                        self.logger.error(f"Error processing batch: {e}")
                        # Add None for each item in the batch
                        results.extend([None] * len(batch))
                        pbar.update(len(batch))

        return results


class ImageProcessor:
    """
    Specialized processor for image operations with GPU support.
    """

    def __init__(self, config: Optional[ParallelConfig] = None):
        """
        Initialize the image processor.

        Args:
            config: Configuration for parallel processing
        """
        self.config = config or ParallelConfig()
        self.processor = ParallelProcessor(config)

    def process_images(
        self,
        func: Callable,
        image_paths: List[str],
        desc: str = "Processing Images",
        **kwargs,
    ) -> List[Any]:
        """
        Process images in parallel with automatic GPU handling.

        Args:
            func: Function to apply to each image
            image_paths: List of image file paths
            desc: Description for progress bar
            **kwargs: Additional arguments to pass to func

        Returns:
            List of results
        """
        # For image processing, prefer threads to avoid GPU memory issues
        config = ParallelConfig(
            max_workers=self.config.max_workers,
            processing_type=ProcessingType.THREAD,
            use_gpu=self.config.use_gpu,
            gpu_memory_fraction=self.config.gpu_memory_fraction,
        )

        processor = ParallelProcessor(config)
        return processor.process_map(func, image_paths, desc, **kwargs)

    def process_image_pairs(
        self,
        func: Callable,
        hq_paths: List[str],
        lq_paths: List[str],
        desc: str = "Processing Image Pairs",
        **kwargs,
    ) -> List[Any]:
        """
        Process HQ/LQ image pairs in parallel.

        Args:
            func: Function to apply to each image pair
            hq_paths: List of HQ image file paths
            lq_paths: List of LQ image file paths
            desc: Description for progress bar
            **kwargs: Additional arguments to pass to func

        Returns:
            List of results
        """
        if len(hq_paths) != len(lq_paths):
            raise ValueError("HQ and LQ path lists must have the same length")

        # Create pairs
        pairs = list(zip(hq_paths, lq_paths))

        # For image pair processing, prefer threads
        config = ParallelConfig(
            max_workers=self.config.max_workers,
            processing_type=ProcessingType.THREAD,
            use_gpu=self.config.use_gpu,
            gpu_memory_fraction=self.config.gpu_memory_fraction,
        )

        processor = ParallelProcessor(config)
        return processor.process_map(func, pairs, desc, **kwargs)


class BatchProcessor:
    """
    Processor for batch operations with memory management.
    """

    def __init__(self, config: Optional[ParallelConfig] = None):
        """
        Initialize the batch processor.

        Args:
            config: Configuration for parallel processing
        """
        self.config = config or ParallelConfig()
        self.processor = ParallelProcessor(config)

    def process_in_batches(
        self,
        func: Callable,
        items: List[Any],
        batch_size: int,
        desc: str = "Processing Batches",
        **kwargs,
    ) -> List[Any]:
        """
        Process items in batches to manage memory usage.

        Args:
            func: Function to apply to each batch
            items: List of items to process
            batch_size: Size of each batch
            desc: Description for progress bar
            **kwargs: Additional arguments to pass to func

        Returns:
            List of results
        """
        return self.processor.process_batches(func, items, batch_size, desc, **kwargs)


# Global instances for easy access
default_processor = ParallelProcessor()
image_processor = ImageProcessor()
batch_processor = BatchProcessor()


# Convenience functions for common operations
def parallel_map(
    func: Callable,
    items: List[Any],
    desc: str = "Processing",
    max_workers: Optional[int] = None,
    processing_type: ProcessingType = ProcessingType.AUTO,
    **kwargs,
) -> List[Any]:
    """
    Convenience function for parallel processing with map interface.

    Args:
        func: Function to apply to each item
        items: List of items to process
        desc: Description for progress bar
        max_workers: Maximum number of workers
        processing_type: Type of processing to use
        **kwargs: Additional arguments to pass to func

    Returns:
        List of results
    """
    config = ParallelConfig(max_workers=max_workers, processing_type=processing_type)
    processor = ParallelProcessor(config)
    return processor.process_map(func, items, desc)


def parallel_submit(
    func: Callable,
    items: List[Any],
    desc: str = "Processing",
    max_workers: Optional[int] = None,
    processing_type: ProcessingType = ProcessingType.AUTO,
    **kwargs,
) -> List[Any]:
    """
    Convenience function for parallel processing with submit interface.

    Args:
        func: Function to apply to each item
        items: List of items to process
        desc: Description for progress bar
        max_workers: Maximum number of workers
        processing_type: Type of processing to use
        **kwargs: Additional arguments to pass to func

    Returns:
        List of results
    """
    config = ParallelConfig(max_workers=max_workers, processing_type=processing_type)
    processor = ParallelProcessor(config)
    return processor.process_submit(func, items, desc)


def parallel_image_processing(
    func: Callable,
    image_paths: List[str],
    desc: str = "Processing Images",
    max_workers: Optional[int] = None,
    **kwargs,
) -> List[Any]:
    """
    Convenience function for parallel image processing.

    Args:
        func: Function to apply to each image
        image_paths: List of image file paths
        desc: Description for progress bar
        max_workers: Maximum number of workers
        **kwargs: Additional arguments to pass to func

    Returns:
        List of results
    """
    config = ParallelConfig(
        max_workers=max_workers, processing_type=ProcessingType.THREAD
    )
    processor = ImageProcessor(config)
    return processor.process_images(func, image_paths, desc)


def get_optimal_worker_count(task_type: str = "auto") -> int:
    """
    Get optimal number of workers based on task type and system resources.

    Args:
        task_type: Type of task ('cpu', 'io', 'gpu', 'auto')

    Returns:
        Optimal number of workers
    """
    cpu_count = os.cpu_count() or 1

    if task_type == "cpu":
        return cpu_count
    elif task_type == "io":
        return min(32, cpu_count * 4)
    elif task_type == "gpu":
        return min(8, cpu_count)  # GPU tasks are usually memory-bound
    else:  # auto
        return cpu_count


def setup_parallel_environment(
    max_workers: Optional[int] = None,
    use_gpu: bool = True,
    gpu_memory_fraction: float = 0.8,
) -> ParallelConfig:
    """
    Setup parallel processing environment with optimal settings.

    Args:
        max_workers: Maximum number of workers
        use_gpu: Whether to use GPU
        gpu_memory_fraction: GPU memory fraction to use

    Returns:
        ParallelConfig: Configuration for parallel processing
    """
    if max_workers is None:
        max_workers = get_optimal_worker_count()

    return ParallelConfig(
        max_workers=max_workers,
        use_gpu=use_gpu,
        gpu_memory_fraction=gpu_memory_fraction,
    )


def get_func_name(func):
    if isinstance(func, functools.partial):
        return func.func.__name__
    return func.__name__
