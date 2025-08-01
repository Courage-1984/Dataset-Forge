"""
Distributed processing utilities for Dataset Forge.

This module provides distributed processing capabilities for both single-machine
multi-GPU and multi-machine cluster setups using Dask and Ray.
"""

import os
import time
import logging
from typing import Callable, List, Any, Optional, Dict, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import queue

# Optional imports for distributed processing
try:
    import dask
    import dask.array as da
    from dask.distributed import Client, LocalCluster, progress
    from dask.distributed import get_client, as_completed

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False

try:
    import ray
    from ray import tune
    from ray.util.dask import ray_dask_get

    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False

from dataset_forge.utils.memory_utils import (
    clear_cuda_cache,
    to_device_safe,
    get_memory_manager,
)
from dataset_forge.utils.cache_utils import smart_cache
from dataset_forge.utils.printing import (
    print_info,
    print_warning,
    print_error,
    print_success,
)
from dataset_forge.utils.monitoring import monitor_all

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    torch,
    numpy_as_np as np,
)


class ProcessingMode(Enum):
    """Distributed processing modes."""

    LOCAL = "local"
    SINGLE_MACHINE_MULTI_GPU = "single_machine_multi_gpu"
    MULTI_MACHINE = "multi_machine"
    AUTO = "auto"


@dataclass
class DistributedConfig:
    """Configuration for distributed processing."""

    mode: ProcessingMode = ProcessingMode.AUTO
    num_workers: Optional[int] = None
    gpu_devices: Optional[List[int]] = None
    memory_limit: Optional[str] = None
    threads_per_worker: int = 1
    processes: bool = True
    dashboard_address: Optional[str] = None
    scheduler_address: Optional[str] = None
    cluster_addresses: Optional[List[str]] = None
    batch_size: int = 32
    timeout: Optional[float] = None
    retry_failed: bool = True
    max_retries: int = 3


class DistributedProcessor:
    """
    Distributed processing manager for Dataset Forge.

    Supports both single-machine multi-GPU and multi-machine distributed processing
    using Dask and Ray.
    """

    def __init__(self, config: Optional[DistributedConfig] = None):
        """
        Initialize distributed processor.

        Args:
            config: Configuration for distributed processing
        """
        self.config = config or DistributedConfig()
        self.logger = logging.getLogger(__name__)
        self._client = None
        self._cluster = None
        self._ray_initialized = False

        # Auto-detect configuration if not specified
        if self.config.mode == ProcessingMode.AUTO:
            self.config.mode = self._auto_detect_mode()

        if self.config.num_workers is None:
            self.config.num_workers = self._auto_detect_workers()

        if self.config.gpu_devices is None:
            self.config.gpu_devices = self._auto_detect_gpus()

    def _auto_detect_mode(self) -> ProcessingMode:
        """Auto-detect the best processing mode."""
        if not DASK_AVAILABLE and not RAY_AVAILABLE:
            return ProcessingMode.LOCAL

        # Check for multiple GPUs
        if torch.cuda.is_available() and torch.cuda.device_count() > 1:
            return ProcessingMode.SINGLE_MACHINE_MULTI_GPU

        # Check for cluster environment variables
        if os.environ.get("DASK_SCHEDULER_ADDRESS") or os.environ.get("RAY_ADDRESS"):
            return ProcessingMode.MULTI_MACHINE

        return ProcessingMode.LOCAL

    def _auto_detect_workers(self) -> int:
        """Auto-detect optimal number of workers."""
        cpu_count = os.cpu_count() or 1

        if self.config.mode == ProcessingMode.SINGLE_MACHINE_MULTI_GPU:
            # For multi-GPU, use GPU count as base
            gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 1
            return min(cpu_count, gpu_count * 2)
        elif self.config.mode == ProcessingMode.MULTI_MACHINE:
            # For distributed, use more workers
            return min(cpu_count * 2, 16)
        else:
            return cpu_count

    def _auto_detect_gpus(self) -> List[int]:
        """Auto-detect available GPU devices."""
        if torch.cuda.is_available():
            return list(range(torch.cuda.device_count()))
        return []

    def start(self) -> bool:
        """
        Start the distributed processing cluster.

        Returns:
            True if started successfully
        """
        try:
            if self.config.mode == ProcessingMode.LOCAL:
                return True

            elif self.config.mode == ProcessingMode.SINGLE_MACHINE_MULTI_GPU:
                return self._start_single_machine_cluster()

            elif self.config.mode == ProcessingMode.MULTI_MACHINE:
                return self._start_multi_machine_cluster()

            return False

        except Exception as e:
            self.logger.error(f"Failed to start distributed processing: {e}")
            return False

    def _start_single_machine_cluster(self) -> bool:
        """Start single-machine multi-GPU cluster."""
        if not DASK_AVAILABLE:
            print_warning("Dask not available, falling back to local processing")
            return False

        try:
            # Create local cluster
            self._cluster = LocalCluster(
                n_workers=self.config.num_workers,
                threads_per_worker=self.config.threads_per_worker,
                processes=self.config.processes,
                memory_limit=self.config.memory_limit,
                dashboard_address=self.config.dashboard_address or ":8787",
            )

            # Create client
            self._client = Client(self._cluster)

            # Setup GPU workers if available
            if self.config.gpu_devices:
                self._setup_gpu_workers()

            print_success(
                f"Started single-machine cluster with {self.config.num_workers} workers"
            )
            if self.config.dashboard_address:
                print_info(
                    f"Dask dashboard available at: http://localhost{self.config.dashboard_address}"
                )

            return True

        except Exception as e:
            self.logger.error(f"Failed to start single-machine cluster: {e}")
            return False

    def _start_multi_machine_cluster(self) -> bool:
        """Start multi-machine distributed cluster."""
        if not DASK_AVAILABLE:
            print_warning("Dask not available, falling back to local processing")
            return False

        try:
            if self.config.scheduler_address:
                # Connect to existing cluster
                self._client = Client(self.config.scheduler_address)
                print_success(
                    f"Connected to existing cluster at {self.config.scheduler_address}"
                )
            else:
                # Start new cluster
                self._cluster = LocalCluster(
                    n_workers=self.config.num_workers,
                    threads_per_worker=self.config.threads_per_worker,
                    processes=self.config.processes,
                    memory_limit=self.config.memory_limit,
                    dashboard_address=self.config.dashboard_address or ":8787",
                )
                self._client = Client(self._cluster)
                print_success("Started new distributed cluster")

            return True

        except Exception as e:
            self.logger.error(f"Failed to start multi-machine cluster: {e}")
            return False

    def _setup_gpu_workers(self):
        """Setup GPU workers for distributed processing."""
        if not self.config.gpu_devices:
            return

        # Distribute GPUs across workers
        gpu_per_worker = len(self.config.gpu_devices) // self.config.num_workers
        if gpu_per_worker == 0:
            gpu_per_worker = 1

        # Submit GPU setup task to each worker
        for i, worker in enumerate(self._client.scheduler_info()["workers"]):
            gpu_id = self.config.gpu_devices[i % len(self.config.gpu_devices)]

            def setup_gpu_worker(gpu_id):
                import torch

                if torch.cuda.is_available():
                    torch.cuda.set_device(gpu_id)
                    return f"GPU {gpu_id} setup on worker"
                return "No GPU available"

            self._client.submit(setup_gpu_worker, gpu_id, key=f"gpu_setup_{i}")

    def stop(self):
        """Stop the distributed processing cluster."""
        try:
            if self._client:
                self._client.close()
                self._client = None

            if self._cluster:
                self._cluster.close()
                self._cluster = None

            if self._ray_initialized and RAY_AVAILABLE:
                ray.shutdown()
                self._ray_initialized = False

            print_success("Distributed processing cluster stopped")

        except Exception as e:
            self.logger.error(f"Error stopping cluster: {e}")

    @monitor_all("distributed_map")
    def map(
        self,
        func: Callable,
        items: List[Any],
        desc: str = "Distributed Processing",
        **kwargs,
    ) -> List[Any]:
        """
        Process items using distributed processing.

        Args:
            func: Function to apply to each item
            items: List of items to process
            desc: Description for progress tracking
            **kwargs: Additional arguments to pass to func

        Returns:
            List of results. In local mode, if any errors occur, returns (results, errors),
            where errors is a list of (idx, item, exception) for failed items.
        """
        if not self._client:
            print_warning("No distributed client available, using local processing")
            results = []
            errors = []
            for idx, item in enumerate(items):
                try:
                    results.append(func(item, **kwargs))
                except Exception as e:
                    self.logger.error(f"Local task failed for item {idx}: {e}")
                    errors.append((idx, item, e))
                    results.append(None)
            if errors:
                return results, errors
            return results

        try:
            # Submit all tasks
            futures = []
            for item in items:
                future = self._client.submit(func, item, **kwargs)
                futures.append(future)

            # Collect results with progress tracking
            results = []
            completed = 0

            print_info(
                f"Processing {len(items)} items with {self.config.num_workers} workers"
            )

            for future in as_completed(futures, timeout=self.config.timeout):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1

                    if completed % 10 == 0:
                        progress_pct = (completed / len(items)) * 100
                        print_info(
                            f"{desc}: {completed}/{len(items)} ({progress_pct:.1f}%)"
                        )

                except Exception as e:
                    self.logger.error(f"Task failed: {e}")
                    if self.config.retry_failed:
                        # Retry logic could be implemented here
                        results.append(None)
                    else:
                        raise

            print_success(f"Completed {desc}: {completed}/{len(items)} items")
            return results

        except Exception as e:
            self.logger.error(f"Distributed processing failed: {e}")
            raise

    def map_batches(
        self,
        func: Callable,
        items: List[Any],
        batch_size: Optional[int] = None,
        desc: str = "Distributed Batch Processing",
        **kwargs,
    ) -> List[Any]:
        """
        Process items in batches using distributed processing.

        Args:
            func: Function to apply to each batch
            items: List of items to process
            batch_size: Size of each batch (uses config default if None)
            desc: Description for progress tracking
            **kwargs: Additional arguments to pass to func

        Returns:
            List of results
        """
        if batch_size is None:
            batch_size = self.config.batch_size

        # Create batches
        batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]

        # Process batches
        batch_results = self.map(func, batches, desc, **kwargs)

        # Flatten results
        results = []
        for batch_result in batch_results:
            if isinstance(batch_result, list):
                results.extend(batch_result)
            else:
                results.append(batch_result)

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get status of distributed processing cluster."""
        status = {
            "mode": self.config.mode.value,
            "num_workers": self.config.num_workers,
            "gpu_devices": self.config.gpu_devices,
            "client_active": self._client is not None,
            "cluster_active": self._cluster is not None,
        }

        if self._client:
            try:
                info = self._client.scheduler_info()
                status.update(
                    {
                        "total_workers": len(info["workers"]),
                        "memory_usage": info.get("memory", {}),
                        "cpu_usage": info.get("cpu", {}),
                    }
                )
            except Exception as e:
                status["error"] = str(e)

        return status


class MultiGPUProcessor:
    """
    Multi-GPU processor for single-machine setups.

    This class provides efficient multi-GPU processing without requiring
    distributed computing frameworks.
    """

    def __init__(self, gpu_devices: Optional[List[int]] = None):
        """
        Initialize multi-GPU processor.

        Args:
            gpu_devices: List of GPU device IDs to use
        """
        self.gpu_devices = gpu_devices or list(range(torch.cuda.device_count()))
        self.logger = logging.getLogger(__name__)

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA not available for multi-GPU processing")

        if not self.gpu_devices:
            raise RuntimeError("No GPU devices specified")

        print_info(f"Multi-GPU processor initialized with {len(self.gpu_devices)} GPUs")

    def map(
        self,
        func: Callable,
        items: List[Any],
        desc: str = "Multi-GPU Processing",
        **kwargs,
    ) -> List[Any]:
        """
        Process items using multiple GPUs.

        Args:
            func: Function to apply to each item
            items: List of items to process
            desc: Description for progress tracking
            **kwargs: Additional arguments to pass to func

        Returns:
            List of results
        """
        import threading
        from concurrent.futures import ThreadPoolExecutor

        results = [None] * len(items)
        lock = threading.Lock()

        def process_with_gpu(gpu_id: int, item_indices: List[int]):
            """Process items on a specific GPU."""
            torch.cuda.set_device(gpu_id)

            for idx in item_indices:
                try:
                    result = func(items[idx], gpu_id=gpu_id, **kwargs)
                    with lock:
                        results[idx] = result
                except Exception as e:
                    self.logger.error(
                        f"Error processing item {idx} on GPU {gpu_id}: {e}"
                    )
                    with lock:
                        results[idx] = None

        # Distribute items across GPUs
        items_per_gpu = len(items) // len(self.gpu_devices)
        remainder = len(items) % len(self.gpu_devices)

        start_idx = 0
        threads = []

        with ThreadPoolExecutor(max_workers=len(self.gpu_devices)) as executor:
            for i, gpu_id in enumerate(self.gpu_devices):
                # Calculate items for this GPU
                num_items = items_per_gpu + (1 if i < remainder else 0)
                end_idx = start_idx + num_items

                if num_items > 0:
                    item_indices = list(range(start_idx, end_idx))
                    thread = executor.submit(process_with_gpu, gpu_id, item_indices)
                    threads.append(thread)

                start_idx = end_idx

            # Wait for completion
            for thread in threads:
                thread.result()

        return results


# Global instances
distributed_processor = DistributedProcessor()
multi_gpu_processor = None

if torch.cuda.is_available() and torch.cuda.device_count() > 1:
    multi_gpu_processor = MultiGPUProcessor()


# Convenience functions
def start_distributed_processing(config: Optional[DistributedConfig] = None) -> bool:
    """Start distributed processing with given configuration."""
    global distributed_processor
    if config:
        distributed_processor = DistributedProcessor(config)
    return distributed_processor.start()


def stop_distributed_processing():
    """Stop distributed processing."""
    global distributed_processor
    distributed_processor.stop()


def distributed_map(
    func: Callable, items: List[Any], desc: str = "Processing", **kwargs
) -> List[Any]:
    """Convenience function for distributed mapping."""
    result = distributed_processor.map(func, items, desc, **kwargs)
    if isinstance(result, tuple) and len(result) == 2:
        results, errors = result
        if errors:
            # Raise an aggregated exception for test purposes
            error_msgs = [f"Item {idx}: {exc}" for idx, _, exc in errors]
            raise RuntimeError(
                f"Distributed map encountered errors:\n" + "\n".join(error_msgs)
            )
        return results
    return result


def multi_gpu_map(
    func: Callable, items: List[Any], desc: str = "Processing", **kwargs
) -> List[Any]:
    """Convenience function for multi-GPU mapping."""
    global multi_gpu_processor
    if multi_gpu_processor is None:
        raise RuntimeError("Multi-GPU processing not available")
    return multi_gpu_processor.map(func, items, desc, **kwargs)
