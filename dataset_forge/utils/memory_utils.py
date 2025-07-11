"""
Memory management utilities for Dataset Forge.

This module provides comprehensive memory and CUDA memory management functions
to ensure proper cleanup and prevent memory leaks throughout the project.
"""

import gc
import os
import psutil
import torch
import logging
from typing import Optional, Dict, Any, Callable, Union
from contextlib import contextmanager
from functools import wraps
import time
import warnings

from dataset_forge.utils.printing import print_info, print_warning, print_error


class MemoryManager:
    """
    Centralized memory management for Dataset Forge.

    This class provides comprehensive memory management including:
    - CUDA memory cleanup
    - Python garbage collection
    - Memory monitoring
    - Automatic cleanup decorators
    - Context managers for memory-intensive operations
    """

    def __init__(self, enable_monitoring: bool = True):
        """
        Initialize the memory manager.

        Args:
            enable_monitoring: Whether to enable memory monitoring
        """
        self.enable_monitoring = enable_monitoring
        self.logger = logging.getLogger(__name__)
        self._memory_stats = {}
        self._cuda_available = torch.cuda.is_available()

        # Set CUDA environment variables for better memory management
        if self._cuda_available:
            os.environ.setdefault("CUDA_LAUNCH_BLOCKING", "1")
            os.environ.setdefault("CUDA_LAUNCH_TIMEOUT", "300")

    def clear_cuda_cache(self, force: bool = False) -> None:
        """
        Clear CUDA cache and perform garbage collection.

        Args:
            force: Force cleanup even if monitoring is disabled
        """
        if not self._cuda_available:
            return

        try:
            # Clear CUDA cache
            torch.cuda.empty_cache()

            # Clear IPC cache (inter-process communication)
            torch.cuda.ipc_collect()

            # Synchronize CUDA operations
            torch.cuda.synchronize()

            if self.enable_monitoring or force:
                self.logger.debug("CUDA cache cleared successfully")

        except Exception as e:
            self.logger.warning(f"Failed to clear CUDA cache: {e}")

    def clear_memory(self, force: bool = False) -> None:
        """
        Perform comprehensive memory cleanup.

        Args:
            force: Force cleanup even if monitoring is disabled
        """
        try:
            # Clear CUDA cache first
            self.clear_cuda_cache(force)

            # Perform garbage collection
            collected = gc.collect()

            if self.enable_monitoring or force:
                self.logger.debug(
                    f"Garbage collection completed, collected {collected} objects"
                )

        except Exception as e:
            self.logger.warning(f"Failed to clear memory: {e}")

    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get comprehensive memory information.

        Returns:
            Dictionary containing memory statistics
        """
        info = {"system": {}, "cuda": {}, "python": {}}

        # System memory
        try:
            memory = psutil.virtual_memory()
            info["system"] = {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent_used": memory.percent,
            }
        except Exception as e:
            self.logger.warning(f"Failed to get system memory info: {e}")

        # CUDA memory
        if self._cuda_available:
            try:
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    allocated = torch.cuda.memory_allocated(i) / (1024**3)
                    cached = torch.cuda.memory_reserved(i) / (1024**3)
                    total = props.total_memory / (1024**3)

                    info["cuda"][f"gpu_{i}"] = {
                        "name": props.name,
                        "total_gb": total,
                        "allocated_gb": allocated,
                        "cached_gb": cached,
                        "free_gb": total - cached,
                        "utilization_percent": (allocated / total) * 100,
                    }
            except Exception as e:
                self.logger.warning(f"Failed to get CUDA memory info: {e}")

        # Python memory
        try:
            info["python"] = {
                "gc_objects": len(gc.get_objects()),
                "gc_garbage": len(gc.garbage),
            }
        except Exception as e:
            self.logger.warning(f"Failed to get Python memory info: {e}")

        return info

    def print_memory_info(self, detailed: bool = False) -> None:
        """
        Print memory information to console.

        Args:
            detailed: Whether to print detailed information
        """
        info = self.get_memory_info()

        print_info("Memory Information:")

        # System memory
        if info["system"]:
            sys = info["system"]
            print_info(
                f"  System RAM: {sys['used_gb']:.1f}GB / {sys['total_gb']:.1f}GB ({sys['percent_used']:.1f}%)"
            )

        # CUDA memory
        if info["cuda"]:
            print_info("  CUDA Memory:")
            for gpu_name, gpu_info in info["cuda"].items():
                print_info(
                    f"    {gpu_name}: {gpu_info['allocated_gb']:.1f}GB / {gpu_info['total_gb']:.1f}GB ({gpu_info['utilization_percent']:.1f}%)"
                )

        if detailed:
            # Python memory
            if info["python"]:
                py = info["python"]
                print_info(f"  Python Objects: {py['gc_objects']:,}")
                if py["gc_garbage"] > 0:
                    print_warning(f"  Garbage Objects: {py['gc_garbage']:,}")

    def monitor_memory_usage(self, operation_name: str = "Operation") -> Callable:
        """
        Decorator to monitor memory usage during function execution.

        Args:
            operation_name: Name of the operation for logging

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enable_monitoring:
                    return func(*args, **kwargs)

                # Get memory before
                memory_before = self.get_memory_info()

                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    # Get memory after
                    memory_after = self.get_memory_info()

                    # Calculate memory difference
                    self._log_memory_diff(operation_name, memory_before, memory_after)

                    # Perform cleanup
                    self.clear_memory()

            return wrapper

        return decorator

    def _log_memory_diff(self, operation_name: str, before: Dict, after: Dict) -> None:
        """Log memory difference between before and after operations."""
        try:
            # System memory difference
            if before["system"] and after["system"]:
                sys_diff = after["system"]["used_gb"] - before["system"]["used_gb"]
                if abs(sys_diff) > 0.1:  # Only log if difference is significant
                    self.logger.info(
                        f"{operation_name}: System memory change: {sys_diff:+.1f}GB"
                    )

            # CUDA memory difference
            if before["cuda"] and after["cuda"]:
                for gpu_name in before["cuda"]:
                    if gpu_name in after["cuda"]:
                        cuda_diff = (
                            after["cuda"][gpu_name]["allocated_gb"]
                            - before["cuda"][gpu_name]["allocated_gb"]
                        )
                        if (
                            abs(cuda_diff) > 0.01
                        ):  # Only log if difference is significant
                            self.logger.info(
                                f"{operation_name}: {gpu_name} memory change: {cuda_diff:+.2f}GB"
                            )

        except Exception as e:
            self.logger.warning(f"Failed to log memory difference: {e}")

    @contextmanager
    def memory_context(
        self, operation_name: str = "Operation", cleanup_on_exit: bool = True
    ):
        """
        Context manager for memory-intensive operations.

        Args:
            operation_name: Name of the operation for logging
            cleanup_on_exit: Whether to perform cleanup when exiting

        Yields:
            Memory manager instance
        """
        if self.enable_monitoring:
            memory_before = self.get_memory_info()
            self.logger.debug(f"Starting {operation_name}")

        try:
            yield self
        finally:
            if cleanup_on_exit:
                self.clear_memory()

            if self.enable_monitoring:
                memory_after = self.get_memory_info()
                self._log_memory_diff(operation_name, memory_before, memory_after)
                self.logger.debug(f"Completed {operation_name}")

    def safe_cuda_operation(
        self,
        operation: Callable,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute CUDA operation with retry logic and memory management.

        Args:
            operation: Function to execute
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries (exponential backoff)
            *args: Arguments to pass to operation
            **kwargs: Keyword arguments to pass to operation

        Returns:
            Result of the operation

        Raises:
            RuntimeError: If operation fails after all retries
        """
        for attempt in range(max_retries):
            try:
                # Clear cache before operation
                self.clear_cuda_cache()

                # Execute operation
                result = operation(*args, **kwargs)

                # Clear cache after successful operation
                self.clear_cuda_cache()

                return result

            except torch.cuda.CudaError as e:
                if "timeout" in str(e).lower() or "launch timed out" in str(e):
                    self.logger.warning(
                        f"CUDA timeout on attempt {attempt + 1}/{max_retries}"
                    )

                    if attempt < max_retries - 1:
                        # Exponential backoff
                        delay = retry_delay * (2**attempt)
                        time.sleep(delay)
                        self.clear_cuda_cache()
                        continue
                    else:
                        raise RuntimeError(
                            f"CUDA operation failed after {max_retries} attempts: {e}"
                        )
                else:
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error in CUDA operation: {e}")
                raise

    def optimize_for_large_operations(
        self, available_memory_gb: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Optimize memory settings for large operations.

        Args:
            available_memory_gb: Available memory in GB (auto-detect if None)

        Returns:
            Dictionary with optimization recommendations
        """
        recommendations = {}

        # Get current memory info
        memory_info = self.get_memory_info()

        # Determine available memory
        if available_memory_gb is None:
            if memory_info["system"]:
                available_memory_gb = memory_info["system"]["available_gb"]
            else:
                available_memory_gb = 8.0  # Default assumption

        # System memory recommendations
        if available_memory_gb < 4.0:
            recommendations["batch_size"] = 1
            recommendations["max_workers"] = 1
            recommendations["use_gpu"] = False
            recommendations["warning"] = (
                "Low memory detected. Consider using CPU-only mode."
            )
        elif available_memory_gb < 8.0:
            recommendations["batch_size"] = 2
            recommendations["max_workers"] = 2
            recommendations["use_gpu"] = True
        elif available_memory_gb < 16.0:
            recommendations["batch_size"] = 4
            recommendations["max_workers"] = 4
            recommendations["use_gpu"] = True
        else:
            recommendations["batch_size"] = 8
            recommendations["max_workers"] = 8
            recommendations["use_gpu"] = True

        # CUDA memory recommendations
        if memory_info["cuda"]:
            for gpu_name, gpu_info in memory_info["cuda"].items():
                if gpu_info["total_gb"] < 4.0:
                    recommendations[f"{gpu_name}_batch_size"] = 1
                    recommendations[f"{gpu_name}_use_mixed_precision"] = True
                elif gpu_info["total_gb"] < 8.0:
                    recommendations[f"{gpu_name}_batch_size"] = 2
                    recommendations[f"{gpu_name}_use_mixed_precision"] = True
                else:
                    recommendations[f"{gpu_name}_batch_size"] = 4
                    recommendations[f"{gpu_name}_use_mixed_precision"] = False

        return recommendations


# Global memory manager instance
_memory_manager = None


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


# Convenience functions for easy access
def clear_cuda_cache() -> None:
    """Clear CUDA cache."""
    get_memory_manager().clear_cuda_cache()


def clear_memory() -> None:
    """Perform comprehensive memory cleanup."""
    get_memory_manager().clear_memory()


def get_memory_info() -> Dict[str, Any]:
    """Get comprehensive memory information."""
    return get_memory_manager().get_memory_info()


def print_memory_info(detailed: bool = False) -> None:
    """Print memory information to console."""
    get_memory_manager().print_memory_info(detailed)


def monitor_memory_usage(operation_name: str = "Operation") -> Callable:
    """Decorator to monitor memory usage during function execution."""
    return get_memory_manager().monitor_memory_usage(operation_name)


@contextmanager
def memory_context(operation_name: str = "Operation", cleanup_on_exit: bool = True):
    """Context manager for memory-intensive operations."""
    with get_memory_manager().memory_context(
        operation_name, cleanup_on_exit
    ) as manager:
        yield manager


def safe_cuda_operation(
    operation: Callable, max_retries: int = 3, retry_delay: float = 1.0, *args, **kwargs
) -> Any:
    """Execute CUDA operation with retry logic and memory management."""
    return get_memory_manager().safe_cuda_operation(
        operation, max_retries, retry_delay, *args, **kwargs
    )


def optimize_for_large_operations(
    available_memory_gb: Optional[float] = None,
) -> Dict[str, Any]:
    """Optimize memory settings for large operations."""
    return get_memory_manager().optimize_for_large_operations(available_memory_gb)


# Legacy compatibility functions
def release_memory() -> None:
    """Legacy function for backward compatibility."""
    clear_memory()


# Automatic cleanup decorator for functions that use CUDA
def auto_cleanup(func: Callable) -> Callable:
    """
    Decorator that automatically cleans up memory after function execution.

    This is particularly useful for functions that use CUDA operations.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            clear_memory()

    return wrapper


# Context manager for tensor operations
@contextmanager
def tensor_context(device: Optional[str] = None, cleanup_on_exit: bool = True):
    """
    Context manager for tensor operations with automatic cleanup.

    Args:
        device: Device to use for tensors
        cleanup_on_exit: Whether to perform cleanup when exiting

    Yields:
        Device string
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        yield device
    finally:
        if cleanup_on_exit:
            clear_memory()


# Memory-efficient tensor operations
def to_device_safe(
    tensor: torch.Tensor, device: str, non_blocking: bool = True
) -> torch.Tensor:
    """
    Safely move tensor to device with memory management.

    Args:
        tensor: Tensor to move
        device: Target device
        non_blocking: Whether to use non-blocking transfer

    Returns:
        Tensor on target device
    """
    if tensor.device == device:
        return tensor

    try:
        result = tensor.to(device, non_blocking=non_blocking)

        # Clear cache after transfer if using CUDA
        if device.startswith("cuda"):
            clear_cuda_cache()

        return result
    except Exception as e:
        print_error(f"Failed to move tensor to {device}: {e}")
        raise


def detach_and_clear(tensor: torch.Tensor) -> torch.Tensor:
    """
    Detach tensor and clear gradients to free memory.

    Args:
        tensor: Tensor to detach

    Returns:
        Detached tensor
    """
    if tensor.requires_grad:
        tensor = tensor.detach()

    if tensor.grad is not None:
        tensor.grad = None

    return tensor
