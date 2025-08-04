#!/usr/bin/env python3
"""
Lazy import system for Dataset Forge.

This module provides lazy loading capabilities for heavy libraries to improve
CLI startup times and memory usage.
"""

import importlib
import sys
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

from dataset_forge.utils.printing import print_info


class LazyImport:
    """Lazy import wrapper for modules."""

    def __init__(self, module_name: str, import_name: Optional[str] = None):
        self.module_name = module_name
        self.import_name = import_name or module_name
        self._module = None
        self._imported = False

    def __getattr__(self, name: str) -> Any:
        """Get attribute from the lazily imported module."""
        if not self._imported:
            self._import_module()
        return getattr(self._module, name)

    def __getattribute__(self, name: str) -> Any:
        """Get attribute, handling special cases."""
        if name in ["module_name", "import_name", "_module", "_imported", "_import_module"]:
            return super().__getattribute__(name)
        if not self._imported:
            self._import_module()
        return getattr(self._module, name)

    def _import_module(self) -> None:
        """Import the module and record timing."""
        start_time = time.time()
        try:
            self._module = importlib.import_module(self.module_name)
            self._imported = True
            
            # Record import time
            import_time = time.time() - start_time
            _import_times[self.import_name] = import_time
            
        except ImportError as e:
            raise ImportError(f"Failed to import {self.module_name}: {e}")

    def __call__(self, *args, **kwargs) -> Any:
        """Call the module as a function or get a class from the module."""
        if not self._imported:
            self._import_module()
        
        # If import_name is different from module_name, we're importing a specific class/function
        if self.import_name != self.module_name:
            # Get the specific class/function from the module
            if hasattr(self._module, self.import_name):
                return getattr(self._module, self.import_name)(*args, **kwargs)
            else:
                raise AttributeError(f"Module {self.module_name} has no attribute {self.import_name}")
        
        # Otherwise, call the module itself
        return self._module(*args, **kwargs)


# Global import timing tracking
_import_times: Dict[str, float] = {}


def lazy_import(module_name: str, import_name: Optional[str] = None) -> LazyImport:
    """Create a lazy import wrapper for a module."""
    return LazyImport(module_name, import_name)


def lazy_import_decorator(module_name: str, import_name: Optional[str] = None):
    """Decorator for lazy importing modules when functions are called."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Import the module when function is called
            module = importlib.import_module(module_name)
            
            # Record import time
            start_time = time.time()
            import_time = time.time() - start_time
            _import_times[import_name or module_name] = import_time
            
            # Call the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_import_times() -> Dict[str, float]:
    """Get a copy of the import timing data."""
    return _import_times.copy()


def print_import_times() -> None:
    """Print timing information for lazy imports."""
    if not _import_times:
        print_info("No lazy imports have been performed yet.")
        return

    print_info("\nLazy Import Times:")
    print_info("-" * 40)
    for module, time_taken in sorted(
        _import_times.items(), key=lambda x: x[1], reverse=True
    ):
        print_info(f"{module:<30} {time_taken:.3f}s")
    print_info("-" * 40)
    total_time = sum(_import_times.values())
    print_info(f"Total lazy import time: {total_time:.3f}s")


def clear_import_cache() -> None:
    """Clear the import timing cache."""
    _import_times.clear()


# Pre-defined lazy imports for common heavy libraries
torch = lazy_import("torch")
torchvision = lazy_import("torchvision")
torchvision_transforms = lazy_import("torchvision.transforms")
torchvision_transforms_functional = lazy_import("torchvision.transforms.functional")
torch_nn = lazy_import("torch.nn")
torch_nn_functional = lazy_import("torch.nn.functional")
torch_cuda_amp = lazy_import("torch.cuda.amp")
# Fix: torch.no_grad is a function, not a module - use torch and access no_grad as attribute
# torch_no_grad = lazy_import("torch.no_grad")

cv2 = lazy_import("cv2")
numpy = lazy_import("numpy")
numpy_as_np = lazy_import("numpy", "np")
pandas = lazy_import("pandas")
pandas_as_pd = lazy_import("pandas", "pd")

PIL = lazy_import("PIL")
PIL_Image = lazy_import("PIL.Image")
PIL_ImageEnhance = lazy_import("PIL.ImageEnhance")
PIL_ImageFont = lazy_import("PIL.ImageFont")
PIL_ImageDraw = lazy_import("PIL.ImageDraw")
PIL_ImageCms = lazy_import("PIL.ImageCms")

matplotlib = lazy_import("matplotlib")
matplotlib_pyplot = lazy_import("matplotlib.pyplot")
matplotlib_patches = lazy_import("matplotlib.patches")

seaborn = lazy_import("seaborn")
imageio = lazy_import("imageio")
imagehash = lazy_import("imagehash")

transformers = lazy_import("transformers")
timm = lazy_import("timm")
lpips = lazy_import("lpips")
spandrel = lazy_import("spandrel")
kornia = lazy_import("kornia")
albumentations = lazy_import("albumentations")

dask = lazy_import("dask")
ray = lazy_import("ray")
numba = lazy_import("numba")
cython = lazy_import("Cython")

# GPU acceleration libraries
pyiqa = lazy_import("pyiqa")
open_clip_torch = lazy_import("open_clip_torch")
onnxruntime = lazy_import("onnxruntime")

# Audio libraries
pygame = lazy_import("pygame")

# Parallel processing
joblib = lazy_import("joblib")
psutil = lazy_import("psutil")
GPUtil = lazy_import("GPUtil")

# Data processing
jinja2 = lazy_import("jinja2")
yaml = lazy_import("yaml")
gdown = lazy_import("gdown")

# umzi libraries
pepeline = lazy_import("pepeline")
pepedpid = lazy_import("pepedpid")
pepedp = lazy_import("pepedp")

# PepeDP specific imports
pepedp_enum = lazy_import("pepedp.enum")
pepedp_best_tile = lazy_import("pepedp.scripts.utils.best_tile", "BestTile")
pepedp_laplacian_complexity = lazy_import(
    "pepedp.scripts.utils.complexity.laplacian", "LaplacianComplexity"
)
pepedp_ic9600_complexity = lazy_import(
    "pepedp.scripts.utils.complexity.ic9600", "IC9600Complexity"
)
pepedp_img_to_embedding = lazy_import(
    "pepedp.embedding.embedding_class", "ImgToEmbedding"
)
# Fix: Import the actual enum modules based on PepeDP source structure
pepedp_embedded_model = lazy_import("pepedp.embedding.enum")
pepedp_euclid_dist = lazy_import("pepedp.scripts.utils.distance", "euclid_dist")
pepedp_cosine_dist = lazy_import("pepedp.scripts.utils.distance", "cosine_dist")
pepedp_video_to_frame = lazy_import("pepedp.scripts.utils.video_to_frames", "VideoToFrame")
pepedp_create_embedd = lazy_import("pepedp.scripts.utils.deduplicate", "create_embedd")
pepedp_filtered_pairs = lazy_import("pepedp.scripts.utils.deduplicate", "filtered_pairs")
pepedp_move_duplicate_files = lazy_import("pepedp.scripts.utils.deduplicate", "move_duplicate_files")
pepedp_threshold_alg = lazy_import("pepedp.torch_enum")

# Deduplication
imagededup = lazy_import("imagededup")


# Convenience functions for common import patterns
def get_torch() -> Any:
    """Get torch module with lazy import."""
    if not torch._imported:
        torch._import_module()
    return torch._module


def get_cv2() -> Any:
    """Get cv2 module with lazy import."""
    if not cv2._imported:
        cv2._import_module()
    return cv2._module


def get_numpy() -> Any:
    """Get numpy module with lazy import."""
    if not numpy._imported:
        numpy._import_module()
    return numpy._module


def get_pil() -> Any:
    """Get PIL module with lazy import."""
    if not PIL._imported:
        PIL._import_module()
    return PIL._module


def get_matplotlib() -> Any:
    """Get matplotlib module with lazy import."""
    if not matplotlib._imported:
        matplotlib._import_module()
    return matplotlib._module


# Context manager for temporary imports
class TemporaryImport:
    """Context manager for temporary imports that are cleaned up after use."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module = None

    def __enter__(self):
        self.module = importlib.import_module(self.module_name)
        return self.module

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up by removing from sys.modules if it was added
        if self.module_name in sys.modules:
            del sys.modules[self.module_name]
        self.module = None


# Performance monitoring
def monitor_import_performance(func: Callable) -> Callable:
    """Decorator to monitor import performance of functions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        import time

        start_time = time.time()

        # Get initial import times
        initial_imports = _import_times.copy()

        try:
            result = func(*args, **kwargs)

            # Calculate new imports
            new_imports = {
                k: v for k, v in _import_times.items() if k not in initial_imports
            }
            total_new_time = sum(new_imports.values())

            if new_imports:
                print_info(
                    f"Function {func.__name__} triggered imports: {new_imports}"
                )
                print_info(f"Total new import time: {total_new_time:.3f}s")

            return result

        except Exception as e:
            print_info(f"Function {func.__name__} failed: {e}")
            raise
        finally:
            function_time = time.time() - start_time
            print_info(f"Function {func.__name__} took {function_time:.3f}s")

    return wrapper
