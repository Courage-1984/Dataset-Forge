"""
Tests for the enhanced caching system in Dataset Forge.

This module tests all caching functionality including:
- In-memory caching with TTL and compression
- Disk caching with persistence
- Model caching for expensive operations
- Cache management utilities
- Cache statistics and monitoring
"""

import os
import tempfile
import time
import pickle
import gzip
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the caching system
from dataset_forge.utils.cache_utils import (
    in_memory_cache,
    disk_cache,
    model_cache,
    smart_cache,
    clear_all_caches,
    clear_disk_cache,
    clear_model_cache,
    clear_in_memory_cache,
    get_cache_statistics,
    cache_size_info,
    analyze_cache_performance,
    export_cache_statistics,
    validate_cache_integrity,
    repair_cache,
    preload_cache,
    warmup_cache,
    AdvancedLRUCache,
    CacheEntry,
    CacheConfig,
)


class TestCacheDecorators:
    """Test the cache decorators."""

    def test_in_memory_cache_basic(self):
        """Test basic in-memory caching functionality."""
        call_count = 0

        @in_memory_cache(maxsize=10)
        def test_func(x, y=1):
            nonlocal call_count
            call_count += 1
            return x + y

        # First call should increment counter
        result1 = test_func(5, 2)
        assert result1 == 7
        assert call_count == 1

        # Second call with same args should use cache
        result2 = test_func(5, 2)
        assert result2 == 7
        assert call_count == 1  # Should not increment

        # Different args should increment counter
        result3 = test_func(5, 3)
        assert result3 == 8
        assert call_count == 2

    def test_in_memory_cache_ttl(self):
        """Test in-memory caching with TTL."""
        call_count = 0

        @in_memory_cache(maxsize=10, ttl_seconds=0.1)  # Very short TTL
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1

        # Immediate second call should use cache
        result2 = test_func(5)
        assert result2 == 10
        assert call_count == 1

        # Wait for TTL to expire
        time.sleep(0.2)

        # Call after TTL should recompute
        result3 = test_func(5)
        assert result3 == 10
        assert call_count == 2

    def test_disk_cache_basic(self, tmp_path):
        """Test basic disk caching functionality."""
        call_count = 0

        @disk_cache(cache_dir=str(tmp_path))
        def test_func(x, y=1):
            nonlocal call_count
            call_count += 1
            return {"result": x + y, "timestamp": time.time()}

        # First call should increment counter
        result1 = test_func(5, 2)
        assert result1["result"] == 7
        assert call_count == 1

        # Second call with same args should use cache
        result2 = test_func(5, 2)
        assert result2["result"] == 7
        assert call_count == 1  # Should not increment

        # Check that cache file was created
        cache_files = list(tmp_path.glob("*.pkl"))
        assert len(cache_files) > 0

    def test_model_cache_basic(self):
        """Test model caching functionality."""
        call_count = 0

        @model_cache(maxsize=5)
        def test_model_loader(model_name):
            nonlocal call_count
            call_count += 1
            return {"model": model_name, "loaded": True}

        # First call should increment counter
        result1 = test_model_loader("test_model")
        assert result1["model"] == "test_model"
        assert call_count == 1

        # Second call with same args should use cache
        result2 = test_model_loader("test_model")
        assert result2["model"] == "test_model"
        assert call_count == 1  # Should not increment

    def test_smart_cache_auto_detection(self, tmp_path):
        """Test smart cache auto-detection."""
        call_count = 0

        @smart_cache(cache_type="auto", cache_dir=str(tmp_path))
        def extract_features(data):
            nonlocal call_count
            call_count += 1
            return np.random.rand(100)  # Simulate feature extraction

        # First call
        result1 = extract_features("test_data")
        assert call_count == 1

        # Second call should use cache
        result2 = extract_features("test_data")
        assert call_count == 1  # Should not increment

        # Should detect this as disk cache due to "extract" in name
        assert hasattr(extract_features, "__wrapped__")


class TestAdvancedLRUCache:
    """Test the AdvancedLRUCache class."""

    def test_cache_basic_operations(self):
        """Test basic cache operations."""
        cache = AdvancedLRUCache(max_size=3)

        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Test cache miss
        assert cache.get("nonexistent") is cache._sentinel

    def test_cache_eviction(self):
        """Test LRU eviction behavior."""
        cache = AdvancedLRUCache(max_size=2)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.get("key1") is cache._sentinel  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_ttl(self):
        """Test TTL functionality."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=0.1)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for TTL to expire
        time.sleep(0.2)
        assert cache.get("key1") is cache._sentinel  # Expired

    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        cache = AdvancedLRUCache(max_size=3)

        # Add some entries
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Access entries
        cache.get("key1")  # Hit
        cache.get("key2")  # Hit
        cache.get("nonexistent")  # Miss

        stats = cache.get_stats()
        assert stats["size"] == 2
        assert stats["max_size"] == 3

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = AdvancedLRUCache(max_size=10)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"

        cache.clear()

        assert cache.get("key1") is cache._sentinel
        assert cache.get("key2") is cache._sentinel


class TestCacheManagement:
    """Test cache management utilities."""

    def test_clear_all_caches(self, tmp_path):
        """Test clearing all caches."""
        # Create some test cache files
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        with patch("dataset_forge.utils.cache_utils.DISK_CACHE_DIR", str(cache_dir)):
            # Create some dummy cache files
            (cache_dir / "test1.pkl").write_bytes(b"dummy")
            (cache_dir / "test2.pkl").write_bytes(b"dummy")

            # Clear all caches
            clear_all_caches()

            # Check that cache directory still exists but files are gone
            assert cache_dir.exists()
            assert len(list(cache_dir.glob("*.pkl"))) == 0

    def test_get_cache_statistics(self):
        """Test getting cache statistics."""
        stats = get_cache_statistics()

        # Should return a dictionary with expected keys
        assert isinstance(stats, dict)
        assert "in_memory" in stats
        assert "disk" in stats
        assert "model" in stats

        # Each cache type should have expected statistics
        for cache_type in ["in_memory", "disk", "model"]:
            cache_stats = stats[cache_type]
            assert "hits" in cache_stats
            assert "misses" in cache_stats
            assert "evictions" in cache_stats

    def test_cache_size_info(self, tmp_path):
        """Test getting cache size information."""
        # Create some test cache files
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        with patch("dataset_forge.utils.cache_utils.DISK_CACHE_DIR", str(cache_dir)):
            # Create some dummy cache files
            (cache_dir / "test1.pkl").write_bytes(b"dummy" * 1000)
            (cache_dir / "test2.pkl").write_bytes(b"dummy" * 2000)

            size_info = cache_size_info()

            assert "disk" in size_info
            assert size_info["disk"]["files"] == 2
            assert size_info["disk"]["size_bytes"] > 0

    def test_analyze_cache_performance(self):
        """Test cache performance analysis."""
        analysis = analyze_cache_performance()

        assert isinstance(analysis, dict)
        assert "statistics" in analysis
        assert "size_info" in analysis
        assert "recommendations" in analysis
        assert "performance_score" in analysis

        # Performance score should be between 0 and 1
        assert 0 <= analysis["performance_score"] <= 1

    def test_export_cache_statistics(self, tmp_path):
        """Test exporting cache statistics."""
        export_path = tmp_path / "cache_stats.json"

        export_cache_statistics(str(export_path))

        # Check that file was created
        assert export_path.exists()

        # Check that it contains valid JSON
        with open(export_path) as f:
            import json

            data = json.load(f)
            assert "timestamp" in data
            assert "statistics" in data
            assert "size_info" in data
            assert "analysis" in data

    def test_validate_cache_integrity(self, tmp_path):
        """Test cache integrity validation."""
        # Create some test cache files
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        with patch("dataset_forge.utils.cache_utils.DISK_CACHE_DIR", str(cache_dir)):
            # Create a valid cache file
            valid_data = pickle.dumps({"test": "data"})
            (cache_dir / "valid.pkl").write_bytes(valid_data)

            # Create an invalid cache file
            (cache_dir / "invalid.pkl").write_bytes(b"invalid data")

            results = validate_cache_integrity()

            assert isinstance(results, dict)
            assert "disk_cache" in results
            assert "model_cache" in results
            assert "in_memory_cache" in results

    def test_repair_cache(self, tmp_path):
        """Test cache repair functionality."""
        # Create some test cache files
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        with patch("dataset_forge.utils.cache_utils.DISK_CACHE_DIR", str(cache_dir)):
            # Create a valid cache file
            valid_data = pickle.dumps({"test": "data"})
            (cache_dir / "valid.pkl").write_bytes(valid_data)

            # Create an invalid cache file
            (cache_dir / "invalid.pkl").write_bytes(b"invalid data")

            # Repair cache
            repair_cache()

            # Check that invalid file was removed
            assert not (cache_dir / "invalid.pkl").exists()
            assert (cache_dir / "valid.pkl").exists()


class TestCacheWarmup:
    """Test cache warmup functionality."""

    def test_preload_cache(self):
        """Test preloading cache for a specific function."""
        call_count = 0

        @in_memory_cache(maxsize=10)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Preload cache
        preload_cache(test_func, 5)

        # Check that function was called
        assert call_count == 1

        # Call again should use cache
        result = test_func(5)
        assert result == 10
        assert call_count == 1  # Should not increment

    def test_warmup_cache(self):
        """Test warming up cache with multiple functions."""
        call_counts = {"func1": 0, "func2": 0}

        @in_memory_cache(maxsize=10)
        def func1(x):
            call_counts["func1"] += 1
            return x * 2

        @in_memory_cache(maxsize=10)
        def func2(x):
            call_counts["func2"] += 1
            return x + 1

        # Warmup cache
        warmup_functions = [
            (func1, (5,), {}),
            (func2, (10,), {}),
        ]

        warmup_cache(warmup_functions)

        # Check that both functions were called
        assert call_counts["func1"] == 1
        assert call_counts["func2"] == 1


class TestCacheCompression:
    """Test cache compression functionality."""

    def test_compression_in_memory(self):
        """Test in-memory cache with compression."""
        call_count = 0

        @in_memory_cache(maxsize=10, compression=True)
        def test_func(data):
            nonlocal call_count
            call_count += 1
            return data * 1000  # Large result

        # First call
        result1 = test_func("test")
        assert call_count == 1

        # Second call should use compressed cache
        result2 = test_func("test")
        assert result2 == result1
        assert call_count == 1

    def test_compression_disk(self, tmp_path):
        """Test disk cache with compression."""
        call_count = 0

        @disk_cache(cache_dir=str(tmp_path), compression=True)
        def test_func(data):
            nonlocal call_count
            call_count += 1
            return {"large_data": "x" * 1000}

        # First call
        result1 = test_func("test")
        assert call_count == 1

        # Second call should use compressed cache
        result2 = test_func("test")
        assert result2 == result1
        assert call_count == 1


class TestCacheEdgeCases:
    """Test edge cases and error handling."""

    def test_cache_with_none_values(self):
        """Test caching with None values."""
        call_count = 0

        @in_memory_cache(maxsize=10)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return None if x == 0 else x

        # Test with None result
        result1 = test_func(0)
        assert result1 is None
        assert call_count == 1

        result2 = test_func(0)
        assert result2 is None
        assert call_count == 1  # Should use cache

    def test_cache_with_exceptions(self):
        """Test caching behavior with exceptions."""
        call_count = 0

        @in_memory_cache(maxsize=10)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            if x < 0:
                raise ValueError("Negative number")
            return x * 2

        # Test normal case
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1

        # Test exception case
        with pytest.raises(ValueError):
            test_func(-1)
        assert call_count == 2  # Should increment for exception

        # Normal case should still use cache
        result2 = test_func(5)
        assert result2 == 10
        assert call_count == 2  # Should not increment

    def test_cache_with_large_objects(self):
        """Test caching with large objects."""
        call_count = 0

        @in_memory_cache(maxsize=10)
        def test_func(size):
            nonlocal call_count
            call_count += 1
            return np.random.rand(size, size)  # Large numpy array

        # Create large object
        result1 = test_func(100)
        assert call_count == 1

        # Should still cache
        result2 = test_func(100)
        assert np.array_equal(result1, result2)
        assert call_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
