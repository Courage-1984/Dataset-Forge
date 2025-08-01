"""
Advanced caching system for Dataset Forge.

This module provides a comprehensive caching solution with multiple strategies:
- In-memory LRU caching for fast, session-only results
- Disk caching for persistent, cross-session results
- Model caching for expensive model loading operations
- Cache statistics and monitoring
- Cache management utilities
"""

import os
import functools
import hashlib
import json
import time
import threading
import weakref
from typing import Callable, Any, Optional, Dict, List, Union, Tuple
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
import pickle
import gzip
import shutil

# Local imports
from dataset_forge.utils.printing import (
    print_info,
    print_warning,
    print_error,
    print_success,
)
from dataset_forge.utils.monitoring import monitor_all

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    joblib,
    numpy_as_np as np,
)


# ============================================================================
# CACHE CONFIGURATION
# ============================================================================

# Set up cache directories
CACHE_BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../store/cache")
)
DISK_CACHE_DIR = os.path.join(CACHE_BASE_DIR, "disk")
MODEL_CACHE_DIR = os.path.join(CACHE_BASE_DIR, "models")
STATS_CACHE_DIR = os.path.join(CACHE_BASE_DIR, "stats")

# Create cache directories
for cache_dir in [CACHE_BASE_DIR, DISK_CACHE_DIR, MODEL_CACHE_DIR, STATS_CACHE_DIR]:
    os.makedirs(cache_dir, exist_ok=True)

# Initialize joblib memory for disk caching
disk_memory = joblib.Memory(DISK_CACHE_DIR, verbose=0)

# Global cache statistics
_cache_stats = {
    "in_memory": {"hits": 0, "misses": 0, "evictions": 0},
    "disk": {"hits": 0, "misses": 0, "evictions": 0},
    "model": {"hits": 0, "misses": 0, "evictions": 0},
}

# Thread-safe cache statistics
_stats_lock = threading.Lock()


# ============================================================================
# CACHE DATA STRUCTURES
# ============================================================================


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""

    key: str
    value: Any
    timestamp: float
    size_bytes: int
    access_count: int = 0
    last_access: float = field(default_factory=time.time)

    def update_access(self):
        """Update access statistics."""
        self.access_count += 1
        self.last_access = time.time()


@dataclass
class CacheConfig:
    """Configuration for cache behavior."""

    max_size: int = 128
    ttl_seconds: Optional[int] = None  # Time to live
    compression: bool = False
    key_prefix: str = ""
    cache_type: str = "in_memory"  # "in_memory", "disk", "model"


class AdvancedLRUCache:
    """Advanced LRU cache with TTL, compression, and statistics."""

    def __init__(self, max_size: int = 128, ttl_seconds: Optional[int] = None):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.Lock()
        self._sentinel = object()  # Sentinel for distinguishing None values

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        # Create a hashable representation of arguments
        key_data = (args, tuple(sorted(kwargs.items())))
        return hashlib.md5(pickle.dumps(key_data)).hexdigest()

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry has expired."""
        if self.ttl_seconds is None:
            return False
        return time.time() - entry.timestamp > self.ttl_seconds

    def _estimate_size(self, obj: Any) -> int:
        """Estimate the size of an object in bytes."""
        try:
            return len(pickle.dumps(obj))
        except (pickle.PickleError, TypeError):
            return 1024  # Default estimate

    def get(self, key: str) -> Any:
        """Get a value from cache. Returns sentinel if not found."""
        with self.lock:
            if key not in self.cache:
                self._update_stats("misses")
                return self._sentinel

            entry = self.cache[key]

            # Check if expired
            if self._is_expired(entry):
                del self.cache[key]
                self._update_stats("misses")
                return self._sentinel

            # Update access statistics
            entry.update_access()
            self.cache.move_to_end(key)
            self._update_stats("hits")
            return entry.value

    def set(self, key: str, value: Any) -> None:
        """Set a value in cache."""
        with self.lock:
            # Remove if already exists
            if key in self.cache:
                del self.cache[key]

            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                size_bytes=self._estimate_size(value),
            )

            # Evict if necessary
            while len(self.cache) >= self.max_size:
                _, evicted_entry = self.cache.popitem(last=False)
                self._update_stats("evictions")

            # Add new entry
            self.cache[key] = entry

    def clear(self) -> None:
        """Clear all entries from cache."""
        with self.lock:
            self.cache.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "total_size_bytes": sum(
                    entry.size_bytes for entry in self.cache.values()
                ),
                "oldest_entry": min(
                    (entry.timestamp for entry in self.cache.values()), default=0
                ),
                "newest_entry": max(
                    (entry.timestamp for entry in self.cache.values()), default=0
                ),
            }

    def _update_stats(self, stat_type: str) -> None:
        """Update global cache statistics."""
        with _stats_lock:
            _cache_stats["in_memory"][stat_type] += 1


# ============================================================================
# CACHE DECORATORS
# ============================================================================


def in_memory_cache(
    maxsize: int = 128,
    ttl_seconds: Optional[int] = None,
    key_prefix: str = "",
    compression: bool = False,
):
    """
    Advanced in-memory LRU cache decorator with TTL and compression.

    Args:
        maxsize: Maximum number of items to cache
        ttl_seconds: Time to live in seconds (None for no expiration)
        key_prefix: Prefix for cache keys
        compression: Whether to compress cached values

    Returns:
        Decorated function with in-memory caching
    """
    cache = AdvancedLRUCache(maxsize, ttl_seconds)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{cache._generate_key(*args, **kwargs)}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not cache._sentinel:
                return cached_result

            # Compute result
            result = func(*args, **kwargs)

            # Compress if requested
            if compression:
                try:
                    result = gzip.compress(pickle.dumps(result))
                except (pickle.PickleError, TypeError):
                    pass  # Fall back to uncompressed

            # Store in cache
            cache.set(cache_key, result)

            return result

        # Add cache methods to wrapper
        wrapper.cache = cache
        wrapper.cache_clear = cache.clear
        wrapper.cache_info = cache.get_stats

        return wrapper

    return decorator


def disk_cache(
    ttl_seconds: Optional[int] = None,
    compression: bool = True,
    key_prefix: str = "",
    cache_dir: Optional[str] = None,
):
    """
    Advanced disk cache decorator with TTL and compression.

    Args:
        ttl_seconds: Time to live in seconds (None for no expiration)
        compression: Whether to compress cached values
        key_prefix: Prefix for cache keys
        cache_dir: Custom cache directory

    Returns:
        Decorated function with disk caching
    """
    # Use custom memory instance if cache_dir specified
    memory_instance = joblib.Memory(cache_dir or DISK_CACHE_DIR, verbose=0)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = (args, tuple(sorted(kwargs.items())))
            cache_key = (
                f"{key_prefix}_{hashlib.md5(pickle.dumps(key_data)).hexdigest()}"
            )

            # Check if cached result exists and is not expired
            cache_file = os.path.join(memory_instance.location, f"{cache_key}.pkl")
            if os.path.exists(cache_file):
                if (
                    ttl_seconds is None
                    or (time.time() - os.path.getmtime(cache_file)) < ttl_seconds
                ):
                    try:
                        with open(cache_file, "rb") as f:
                            if compression:
                                result = pickle.loads(gzip.decompress(f.read()))
                            else:
                                result = pickle.load(f)
                        with _stats_lock:
                            _cache_stats["disk"]["hits"] += 1
                        return result
                    except Exception:
                        pass  # Fall through to recompute

            with _stats_lock:
                _cache_stats["disk"]["misses"] += 1

            # Compute result
            result = func(*args, **kwargs)

            # Store result
            try:
                serialized = pickle.dumps(result)
                if compression:
                    serialized = gzip.compress(serialized)

                with open(cache_file, "wb") as f:
                    f.write(serialized)
            except Exception as e:
                print_warning(f"Failed to cache result: {e}")

            return result

        return wrapper

    return decorator


def model_cache(
    maxsize: int = 10, ttl_seconds: Optional[int] = None, key_prefix: str = "model"
):
    """
    Specialized cache for model loading operations.

    Args:
        maxsize: Maximum number of models to cache
        ttl_seconds: Time to live in seconds
        key_prefix: Prefix for cache keys

    Returns:
        Decorated function with model caching
    """
    cache = AdvancedLRUCache(maxsize, ttl_seconds)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key based on model path/name
            cache_key = f"{key_prefix}:{cache._generate_key(*args, **kwargs)}"

            # Try to get from cache
            cached_model = cache.get(cache_key)
            if cached_model is not cache._sentinel:
                with _stats_lock:
                    _cache_stats["model"]["hits"] += 1
                return cached_model

            with _stats_lock:
                _cache_stats["model"]["misses"] += 1

            # Load model
            model = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, model)

            return model

        # Add cache methods to wrapper
        wrapper.cache = cache
        wrapper.cache_clear = cache.clear
        wrapper.cache_info = cache.get_stats

        return wrapper

    return decorator


def smart_cache(
    maxsize: int = 128,
    ttl_seconds: Optional[int] = None,
    cache_type: str = "auto",
    compression: bool = False,
    key_prefix: str = "",
    cache_dir: Optional[str] = None,
):
    """
    Smart cache decorator that automatically chooses the best caching strategy.

    Args:
        maxsize: Maximum number of items to cache
        ttl_seconds: Time to live in seconds
        cache_type: "auto", "in_memory", "disk", or "model"
        compression: Whether to compress cached values
        key_prefix: Prefix for cache keys
        cache_dir: Custom cache directory (for disk cache)

    Returns:
        Decorated function with smart caching
    """

    def decorator(func: Callable) -> Callable:
        # Auto-detect cache type based on function name and signature
        detected_cache_type = cache_type
        if detected_cache_type == "auto":
            func_name = func.__name__.lower()
            if any(keyword in func_name for keyword in ["model", "load", "embedding"]):
                detected_cache_type = "model"
            elif any(
                keyword in func_name for keyword in ["extract", "compute", "process"]
            ):
                detected_cache_type = "disk"
            else:
                detected_cache_type = "in_memory"

        # Apply the appropriate cache decorator
        if detected_cache_type == "model":
            decorated_func = model_cache(maxsize, ttl_seconds, key_prefix)(func)
        elif detected_cache_type == "disk":
            decorated_func = disk_cache(
                ttl_seconds, compression, key_prefix, cache_dir=cache_dir
            )(func)
        else:
            decorated_func = in_memory_cache(
                maxsize, ttl_seconds, key_prefix, compression
            )(func)

        return decorated_func

    return decorator


# ============================================================================
# CACHE MANAGEMENT UTILITIES
# ============================================================================


def clear_disk_cache():
    """Clear the persistent disk cache."""
    try:
        disk_memory.clear(warn=False)
        # Also clear any custom cache files
        for cache_dir in [DISK_CACHE_DIR, MODEL_CACHE_DIR]:
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
        print_success("Disk cache cleared successfully.")
    except Exception as e:
        print_error(f"Failed to clear disk cache: {e}")


def clear_in_memory_cache(func: Optional[Callable] = None):
    """
    Clear in-memory cache for a specific function or all cached functions.

    Args:
        func: The function whose cache to clear. If None, clears all.
    """
    if func and hasattr(func, "cache_clear"):
        func.cache_clear()
        print_success(f"Cleared cache for {func.__name__}")
    else:
        # Clear all in-memory caches (this is a simplified approach)
        print_warning("Clearing all in-memory caches not fully implemented")


def clear_model_cache():
    """Clear the model cache."""
    try:
        if os.path.exists(MODEL_CACHE_DIR):
            shutil.rmtree(MODEL_CACHE_DIR)
            os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
        print_success("Model cache cleared successfully.")
    except Exception as e:
        print_error(f"Failed to clear model cache: {e}")


def clear_all_caches():
    """Clear all caches (in-memory, disk, and model)."""
    clear_disk_cache()
    clear_model_cache()
    clear_in_memory_cache()
    print_success("All caches cleared successfully.")


def get_cache_info(func: Callable) -> Optional[Dict[str, Any]]:
    """
    Get cache information for a cached function.

    Args:
        func: The function decorated with cache

    Returns:
        Cache info dictionary or None if not available
    """
    if hasattr(func, "cache_info"):
        return func.cache_info()
    elif hasattr(func, "cache"):
        return func.cache.get_stats()
    return None


def get_cache_statistics() -> Dict[str, Dict[str, int]]:
    """
    Get comprehensive cache statistics.

    Returns:
        Dictionary with cache statistics for all cache types
    """
    with _stats_lock:
        stats = _cache_stats.copy()

        # Add disk cache size information
        try:
            disk_size = sum(
                os.path.getsize(os.path.join(DISK_CACHE_DIR, f))
                for f in os.listdir(DISK_CACHE_DIR)
                if os.path.isfile(os.path.join(DISK_CACHE_DIR, f))
            )
            stats["disk"]["size_bytes"] = disk_size
        except Exception:
            stats["disk"]["size_bytes"] = 0

        return stats


def cache_size_info() -> Dict[str, Union[int, str]]:
    """
    Get information about cache sizes and disk usage.

    Returns:
        Dictionary with cache size information
    """
    info = {}

    # In-memory cache info
    info["in_memory"] = {
        "active_caches": 0,  # Would need to track this
        "total_entries": 0,
    }

    # Disk cache info
    try:
        disk_files = [f for f in os.listdir(DISK_CACHE_DIR) if f.endswith(".pkl")]
        disk_size = sum(
            os.path.getsize(os.path.join(DISK_CACHE_DIR, f)) for f in disk_files
        )
        info["disk"] = {
            "files": len(disk_files),
            "size_bytes": disk_size,
            "size_mb": disk_size / (1024 * 1024),
        }
    except Exception:
        info["disk"] = {"files": 0, "size_bytes": 0, "size_mb": 0}

    # Model cache info
    try:
        model_files = [f for f in os.listdir(MODEL_CACHE_DIR) if f.endswith(".pkl")]
        model_size = sum(
            os.path.getsize(os.path.join(MODEL_CACHE_DIR, f)) for f in model_files
        )
        info["model"] = {
            "files": len(model_files),
            "size_bytes": model_size,
            "size_mb": model_size / (1024 * 1024),
        }
    except Exception:
        info["model"] = {"files": 0, "size_bytes": 0, "size_mb": 0}

    return info


# ============================================================================
# CACHE MONITORING AND ANALYTICS
# ============================================================================


@monitor_all("cache_analytics")
def analyze_cache_performance() -> Dict[str, Any]:
    """
    Analyze cache performance and provide recommendations.

    Returns:
        Dictionary with cache analysis and recommendations
    """
    stats = get_cache_statistics()
    size_info = cache_size_info()

    analysis = {
        "statistics": stats,
        "size_info": size_info,
        "recommendations": [],
        "performance_score": 0.0,
    }

    # Calculate hit rates
    total_hits = sum(stats[cache_type]["hits"] for cache_type in stats)
    total_misses = sum(stats[cache_type]["misses"] for cache_type in stats)
    total_requests = total_hits + total_misses

    if total_requests > 0:
        hit_rate = total_hits / total_requests
        analysis["performance_score"] = hit_rate

        # Generate recommendations
        if hit_rate < 0.5:
            analysis["recommendations"].append(
                "Low cache hit rate. Consider increasing cache sizes or adjusting TTL."
            )

        if size_info["disk"]["size_mb"] > 1000:  # 1GB
            analysis["recommendations"].append(
                "Large disk cache detected. Consider clearing old entries or reducing cache size."
            )

    return analysis


def export_cache_statistics(output_path: str) -> None:
    """
    Export cache statistics to a JSON file.

    Args:
        output_path: Path to save the statistics
    """
    try:
        stats = get_cache_statistics()
        size_info = cache_size_info()
        analysis = analyze_cache_performance()

        export_data = {
            "timestamp": time.time(),
            "statistics": stats,
            "size_info": size_info,
            "analysis": analysis,
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        print_success(f"Cache statistics exported to {output_path}")
    except Exception as e:
        print_error(f"Failed to export cache statistics: {e}")


# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================


# Keep the old function names for backward compatibility
def cache_info(func: Callable) -> Any:
    """
    Get cache info for a cached function (legacy compatibility).

    Args:
        func: The function decorated with cache

    Returns:
        Cache info object, or None if not available
    """
    return get_cache_info(func)


# ============================================================================
# CACHE PRELOADING AND WARMUP
# ============================================================================


def preload_cache(func: Callable, *args, **kwargs) -> None:
    """
    Preload cache with specific function calls.

    Args:
        func: Function to preload
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function
    """
    try:
        print_info(f"Preloading cache for {func.__name__}...")
        func(*args, **kwargs)
        print_success(f"Cache preloaded for {func.__name__}")
    except Exception as e:
        print_warning(f"Failed to preload cache for {func.__name__}: {e}")


def warmup_cache(functions: List[Tuple[Callable, tuple, dict]]) -> None:
    """
    Warm up cache with multiple function calls.

    Args:
        functions: List of (function, args, kwargs) tuples
    """
    print_info("Warming up cache...")
    for func, args, kwargs in functions:
        preload_cache(func, *args, **kwargs)
    print_success("Cache warmup complete.")


# ============================================================================
# CACHE VALIDATION AND INTEGRITY
# ============================================================================


def validate_cache_integrity() -> Dict[str, bool]:
    """
    Validate cache integrity and report issues.

    Returns:
        Dictionary with validation results
    """
    results = {"disk_cache": True, "model_cache": True, "in_memory_cache": True}

    # Validate disk cache
    try:
        for cache_dir in [DISK_CACHE_DIR, MODEL_CACHE_DIR]:
            if os.path.exists(cache_dir):
                for filename in os.listdir(cache_dir):
                    filepath = os.path.join(cache_dir, filename)
                    if filename.endswith(".pkl"):
                        try:
                            with open(filepath, "rb") as f:
                                pickle.load(f)
                        except Exception:
                            results["disk_cache"] = False
                            print_warning(f"Corrupted cache file: {filepath}")
    except Exception:
        results["disk_cache"] = False

    return results


def repair_cache() -> None:
    """Attempt to repair corrupted cache files."""
    print_info("Repairing cache...")

    for cache_dir in [DISK_CACHE_DIR, MODEL_CACHE_DIR]:
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                filepath = os.path.join(cache_dir, filename)
                if filename.endswith(".pkl"):
                    try:
                        with open(filepath, "rb") as f:
                            pickle.load(f)
                    except Exception:
                        try:
                            os.remove(filepath)
                            print_info(f"Removed corrupted cache file: {filepath}")
                        except Exception as e:
                            print_warning(
                                f"Failed to remove corrupted file {filepath}: {e}"
                            )

    print_success("Cache repair complete.")
