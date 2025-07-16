import os
import functools
from joblib import Memory
from typing import Callable, Any, Optional

# Set up a persistent cache directory (relative to project root)
CACHE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../store/cache")
)
os.makedirs(CACHE_DIR, exist_ok=True)
memory = Memory(CACHE_DIR, verbose=0)


def in_memory_cache(maxsize: int = 128):
    """
    Decorator for in-memory LRU caching of function results.

    Args:
        maxsize: Maximum number of items to cache in memory.

    Returns:
        Decorated function with in-memory caching.
    """

    def decorator(func: Callable) -> Callable:
        return functools.lru_cache(maxsize=maxsize)(func)

    return decorator


def disk_cache(func: Callable) -> Callable:
    """
    Decorator for persistent disk caching of function results using joblib.

    Args:
        func: Function to cache.

    Returns:
        Decorated function with disk caching.
    """
    return memory.cache(func)


def clear_disk_cache():
    """
    Clear the persistent disk cache.
    """
    memory.clear(warn=False)


def clear_in_memory_cache(func: Optional[Callable] = None):
    """
    Clear the in-memory cache for a specific function or all lru_cache-decorated functions.

    Args:
        func: The function whose cache to clear. If None, does nothing.
    """
    if func and hasattr(func, "cache_clear"):
        func.cache_clear()


def cache_info(func: Callable) -> Any:
    """
    Get cache info for an in-memory cached function.

    Args:
        func: The function decorated with lru_cache.

    Returns:
        Cache info object, or None if not available.
    """
    if hasattr(func, "cache_info"):
        return func.cache_info()
    return None
