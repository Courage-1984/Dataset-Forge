import pytest
from dataset_forge.utils.memory_utils import clear_memory, memory_context


def test_clear_memory_runs():
    # Should not raise
    clear_memory()


def test_memory_context():
    with memory_context("Test"):
        # Should enter and exit without error
        pass
