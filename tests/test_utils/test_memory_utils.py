import pytest
from dataset_forge.utils.memory_utils import (
    clear_memory,
    memory_context,
    get_memory_manager,
    auto_cleanup,
)


def test_clear_memory_runs():
    """Test that clear_memory runs without error."""
    clear_memory()


def test_memory_context():
    """Test that memory_context enters and exits without error."""
    with memory_context("Test"):
        pass


def test_get_memory_manager():
    """Test that get_memory_manager returns a MemoryManager instance."""
    mgr = get_memory_manager()
    assert hasattr(mgr, "clear_cuda_cache")


def test_memory_context_error():
    """Test that memory_context propagates exceptions."""
    with pytest.raises(ValueError):
        with memory_context("TestError"):
            raise ValueError("fail")


def test_auto_cleanup_decorator():
    """Test that @auto_cleanup decorator works and does not interfere with function output."""

    @auto_cleanup
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
