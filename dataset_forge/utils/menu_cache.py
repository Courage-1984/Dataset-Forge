#!/usr/bin/env python3
"""
Menu Caching System for Dataset Forge.

This module provides intelligent caching for menu functions and contexts
to improve menu loading performance and reduce memory usage.
"""

import time
import functools
from typing import Any, Callable, Dict, Optional, Tuple
from collections import OrderedDict
import threading

from dataset_forge.utils.printing import print_info, print_warning, print_error
from dataset_forge.utils.color import Mocha


class MenuCache:
    """Intelligent cache for menu functions and contexts."""

    def __init__(self, max_size: int = 100, ttl: int = 300):
        """
        Initialize the menu cache.

        Args:
            max_size: Maximum number of cached items
            ttl: Time to live for cached items in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "total_requests": 0}

    def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            self._stats["total_requests"] += 1

            if key not in self._cache:
                self._stats["misses"] += 1
                return None

            value, timestamp = self._cache[key]
            current_time = time.time()

            # Check if item has expired
            if current_time - timestamp > self.ttl:
                del self._cache[key]
                self._stats["misses"] += 1
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._stats["hits"] += 1
            return value

    def set(self, key: str, value: Any) -> None:
        """
        Set an item in the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            current_time = time.time()

            # Remove if already exists
            if key in self._cache:
                del self._cache[key]

            # Evict oldest item if cache is full
            if len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats["evictions"] += 1

            self._cache[key] = (value, current_time)

    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            hit_rate = (
                self._stats["hits"] / max(self._stats["total_requests"], 1)
            ) * 100
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "total_requests": self._stats["total_requests"],
                "hit_rate": hit_rate,
                "current_size": len(self._cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
            }

    def cleanup_expired(self) -> int:
        """
        Remove expired items from cache.

        Returns:
            Number of items removed
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, (_, timestamp) in self._cache.items()
                if current_time - timestamp > self.ttl
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)


# Global menu cache instance
_menu_cache = MenuCache(max_size=50, ttl=600)  # 10 minutes TTL


def menu_function_cache(func: Callable) -> Callable:
    """
    Decorator to cache menu function results.

    Args:
        func: Function to cache

    Returns:
        Cached function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

        # Try to get from cache
        cached_result = _menu_cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Execute function and cache result
        result = func(*args, **kwargs)
        _menu_cache.set(cache_key, result)

        return result

    return wrapper


def menu_context_cache(func: Callable) -> Callable:
    """
    Decorator to cache menu context generation.

    Args:
        func: Function that generates menu context

    Returns:
        Cached function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from function name
        cache_key = f"context:{func.__name__}"

        # Try to get from cache
        cached_context = _menu_cache.get(cache_key)
        if cached_context is not None:
            return cached_context

        # Generate context and cache result
        context = func(*args, **kwargs)
        _menu_cache.set(cache_key, context)

        return context

    return wrapper


def get_menu_cache_stats() -> Dict[str, Any]:
    """
    Get menu cache statistics.

    Returns:
        Dictionary with cache statistics
    """
    return _menu_cache.get_stats()


def clear_menu_cache() -> None:
    """Clear the menu cache."""
    _menu_cache.clear()


def cleanup_menu_cache() -> int:
    """
    Clean up expired items from menu cache.

    Returns:
        Number of items removed
    """
    return _menu_cache.cleanup_expired()


def menu_preload_cache(menu_paths: list) -> None:
    """
    Preload cache with frequently accessed menus.

    Args:
        menu_paths: List of menu module paths to preload
    """
    for menu_path in menu_paths:
        try:
            # Import the menu module
            import importlib

            module = importlib.import_module(menu_path)

            # Cache the main menu function if it exists
            if hasattr(module, "main_menu"):
                cache_key = f"preload:{menu_path}:main_menu"
                _menu_cache.set(cache_key, module.main_menu)

        except ImportError as e:
            print_warning(f"Failed to preload menu {menu_path}: {e}")


def optimize_menu_cache() -> Dict[str, Any]:
    """
    Optimize menu cache based on usage patterns.

    Returns:
        Dictionary with optimization results
    """
    stats = get_menu_cache_stats()

    # Clean up expired items
    removed = cleanup_menu_cache()

    # Adjust cache size based on hit rate
    if stats["hit_rate"] < 50 and stats["current_size"] > 20:
        # Reduce cache size if hit rate is low
        _menu_cache.max_size = max(20, _menu_cache.max_size - 10)
        print_info(f"Reduced cache size to {_menu_cache.max_size} due to low hit rate")

    elif stats["hit_rate"] > 80 and stats["current_size"] < _menu_cache.max_size:
        # Increase cache size if hit rate is high
        _menu_cache.max_size = min(100, _menu_cache.max_size + 10)
        print_info(
            f"Increased cache size to {_menu_cache.max_size} due to high hit rate"
        )

    return {
        "items_removed": removed,
        "new_cache_size": _menu_cache.max_size,
        "hit_rate": stats["hit_rate"],
    }


def print_menu_cache_stats() -> None:
    """Print menu cache statistics."""
    stats = get_menu_cache_stats()

    print_info("📊 Menu Cache Statistics:")
    print_info(f"  Hit Rate: {stats['hit_rate']:.1f}%")
    print_info(f"  Hits: {stats['hits']}")
    print_info(f"  Misses: {stats['misses']}")
    print_info(f"  Evictions: {stats['evictions']}")
    print_info(f"  Current Size: {stats['current_size']}/{stats['max_size']}")
    print_info(f"  TTL: {stats['ttl']}s")


# Performance monitoring for menu operations
_menu_performance_stats = {"load_times": {}, "total_loads": 0, "average_load_time": 0.0}


def record_menu_load_time(menu_name: str, load_time: float) -> None:
    """
    Record menu load time for performance analysis.

    Args:
        menu_name: Name of the menu
        load_time: Time taken to load the menu
    """
    if menu_name not in _menu_performance_stats["load_times"]:
        _menu_performance_stats["load_times"][menu_name] = []

    _menu_performance_stats["load_times"][menu_name].append(load_time)
    _menu_performance_stats["total_loads"] += 1

    # Update average load time
    total_time = sum(_menu_performance_stats["load_times"][menu_name])
    _menu_performance_stats["average_load_time"] = total_time / len(
        _menu_performance_stats["load_times"][menu_name]
    )


def get_menu_performance_stats() -> Dict[str, Any]:
    """
    Get menu performance statistics.

    Returns:
        Dictionary with performance statistics
    """
    stats = _menu_performance_stats.copy()

    # Calculate performance metrics
    if stats["load_times"]:
        all_times = [time for times in stats["load_times"].values() for time in times]
        stats["overall_average"] = sum(all_times) / len(all_times)
        stats["fastest_menu"] = min(
            stats["load_times"].items(), key=lambda x: sum(x[1]) / len(x[1])
        )[0]
        stats["slowest_menu"] = max(
            stats["load_times"].items(), key=lambda x: sum(x[1]) / len(x[1])
        )[0]

    return stats


def print_menu_performance_stats() -> None:
    """Print menu performance statistics."""
    stats = get_menu_performance_stats()

    print_info("📈 Menu Performance Statistics:")
    print_info(f"  Total Menu Loads: {stats['total_loads']}")
    if "overall_average" in stats:
        print_info(f"  Overall Average Load Time: {stats['overall_average']:.3f}s")
        print_info(f"  Fastest Menu: {stats['fastest_menu']}")
        print_info(f"  Slowest Menu: {stats['slowest_menu']}")

    print_info("  Individual Menu Load Times:")
    for menu_name, times in stats["load_times"].items():
        avg_time = sum(times) / len(times)
        print_info(f"    {menu_name}: {avg_time:.3f}s (loaded {len(times)} times)")
