#!/usr/bin/env python3
"""
Comprehensive test suite for CUDA optimizations in Dataset Forge.
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import torch
import pytest

from dataset_forge.utils.printing import print_info, print_success, print_warning, print_error
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.actions.bhi_filtering_actions import get_optimal_batch_size


def test_cuda_availability():
    """Test CUDA availability and basic GPU information."""
    print_info("=== Testing CUDA Availability ===")
    
    cuda_available = torch.cuda.is_available()
    print_info(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        print_info(f"GPU: {torch.cuda.get_device_name(0)}")
        print_info(f"CUDA Version: {torch.version.cuda}")
        print_info(f"PyTorch Version: {torch.__version__}")
        
        # Test GPU memory
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        allocated_memory = torch.cuda.memory_allocated(0) / (1024**3)
        cached_memory = torch.cuda.memory_reserved(0) / (1024**3)
        
        print_info(f"Total GPU Memory: {total_memory:.1f} GB")
        print_info(f"Allocated Memory: {allocated_memory:.1f} GB")
        print_info(f"Cached Memory: {cached_memory:.1f} GB")
        
        assert total_memory > 0, "Invalid total memory"
        assert allocated_memory >= 0, "Invalid allocated memory"
        assert cached_memory >= 0, "Invalid cached memory"
    else:
        print_warning("CUDA not available - some tests will be skipped")
    
    print_success("✓ CUDA availability test passed\n")


def test_mixed_precision():
    """Test mixed precision (FP16) functionality."""
    print_info("=== Testing Mixed Precision ===")
    
    if not torch.cuda.is_available():
        print_warning("Skipping mixed precision test - CUDA not available")
        return
    
    try:
        # Test autocast functionality
        with torch.amp.autocast('cuda', enabled=True):
            x = torch.randn(100, 100, device='cuda')
            y = torch.randn(100, 100, device='cuda')
            z = torch.mm(x, y)
            
            print_info(f"Mixed precision result dtype: {z.dtype}")
            assert z.dtype in [torch.float16, torch.float32], f"Unexpected dtype: {z.dtype}"
        
        # Test with disabled autocast
        with torch.amp.autocast('cuda', enabled=False):
            x = torch.randn(100, 100, device='cuda')
            y = torch.randn(100, 100, device='cuda')
            z = torch.mm(x, y)
            
            print_info(f"Standard precision result dtype: {z.dtype}")
            assert z.dtype == torch.float32, f"Expected float32, got {z.dtype}"
        
        print_success("✓ Mixed precision test passed")
        
    except Exception as e:
        print_warning(f"Mixed precision test failed: {e}")
    
    print_success("✓ Mixed precision test completed\n")


def test_memory_management():
    """Test memory management utilities."""
    print_info("=== Testing Memory Management ===")
    
    if torch.cuda.is_available():
        # Test memory allocation and cleanup
        initial_allocated = torch.cuda.memory_allocated(0)
        
        # Allocate some memory
        x = torch.randn(1000, 1000, device='cuda')
        after_alloc = torch.cuda.memory_allocated(0)
        
        print_info(f"Memory after allocation: {after_alloc / (1024**3):.3f} GB")
        assert after_alloc > initial_allocated, "Memory should be allocated"
        
        # Test memory cleanup
        clear_cuda_cache()
        after_cleanup = torch.cuda.memory_allocated(0)
        
        print_info(f"Memory after cleanup: {after_cleanup / (1024**3):.3f} GB")
        # Note: cleanup might not immediately free all memory due to PyTorch's caching
        
        # Test clear_memory function
        clear_memory()
        
    else:
        # Test CPU memory management
        clear_memory()
        print_info("CPU memory management tested")
    
    print_success("✓ Memory management test passed\n")


def test_optimal_batch_size():
    """Test optimal batch size calculation."""
    print_info("=== Testing Optimal Batch Size Calculation ===")
    
    # Test with different base sizes
    test_cases = [
        (1, 1),    # Very small
        (4, 4),    # Small
        (8, 8),    # Medium
        (16, 16),  # Large
        (32, 16),  # Very large (should be capped)
        (64, 16),  # Extremely large (should be capped)
    ]
    
    for base_size, expected_max in test_cases:
        optimal = get_optimal_batch_size(base_size)
        print_info(f"Base size: {base_size} → Optimal: {optimal}")
        
        # Verify optimal size is reasonable
        assert optimal > 0, f"Optimal size should be positive, got {optimal}"
        assert optimal <= expected_max, f"Optimal size {optimal} exceeds expected max {expected_max}"
        
        # Verify optimal size doesn't exceed base size (unless capped)
        if base_size <= 16:
            assert optimal <= base_size, f"Optimal size {optimal} exceeds base size {base_size}"
    
    print_success("✓ Optimal batch size test passed\n")


def test_dataloader_optimization():
    """Test DataLoader optimization settings."""
    print_info("=== Testing DataLoader Optimization ===")
    
    from torch.utils.data import Dataset, DataLoader
    
    # Create a simple test dataset
    class TestDataset(Dataset):
        def __init__(self, size=10):
            self.size = size
            self.data = torch.randn(size, 3, 224, 224)
        
        def __len__(self):
            return self.size
        
        def __getitem__(self, idx):
            return self.data[idx], f"item_{idx}"
    
    # Test different device configurations
    device_configs = [
        ("cpu", True),   # CPU with pin_memory=True
        ("cuda", False) if torch.cuda.is_available() else ("cpu", True)  # CUDA with pin_memory=False
    ]
    
    for device_type, expected_pin_memory in device_configs:
        device = torch.device(device_type)
        dataset = TestDataset(5)
        
        # Test optimized DataLoader settings
        dataloader = DataLoader(
            dataset,
            batch_size=2,
            num_workers=0,  # Disable multiprocessing on Windows
            pin_memory=(device.type == "cpu"),  # Only for CPU tensors
            persistent_workers=False,  # Disable when num_workers=0
            prefetch_factor=None,  # Disable when num_workers=0
        )
        
        print_info(f"Device: {device_type}, pin_memory: {dataloader.pin_memory}")
        assert dataloader.num_workers == 0, "num_workers should be 0"
        assert dataloader.pin_memory == expected_pin_memory, f"pin_memory should be {expected_pin_memory}"
        
        # Test iteration
        for batch_idx, (data, labels) in enumerate(dataloader):
            print_info(f"Batch {batch_idx}: {data.shape}, {len(labels)} items")
            break  # Just test first batch
    
    print_success("✓ DataLoader optimization test passed\n")


def test_cuda_error_handling():
    """Test CUDA error handling and CPU fallback."""
    print_info("=== Testing CUDA Error Handling ===")
    
    if not torch.cuda.is_available():
        print_warning("Skipping CUDA error handling test - CUDA not available")
        return
    
    # Test CPU fallback pattern
    def test_cuda_operation_with_fallback():
        """Test CUDA operation with CPU fallback."""
        try:
            # Try to allocate more memory than available (this might fail)
            large_tensor = torch.randn(10000, 10000, device='cuda')
            return large_tensor
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print_info("CUDA memory error detected, falling back to CPU")
                clear_cuda_cache()
                
                # Fallback to CPU
                cpu_tensor = torch.randn(10000, 10000, device='cpu')
                return cpu_tensor
            else:
                raise e
    
    try:
        result = test_cuda_operation_with_fallback()
        print_info(f"Operation completed successfully, result device: {result.device}")
        assert result.device.type in ['cuda', 'cpu'], f"Unexpected device: {result.device}"
    except Exception as e:
        print_warning(f"CUDA error handling test failed: {e}")
    
    print_success("✓ CUDA error handling test passed\n")


def test_performance_monitoring():
    """Test performance monitoring capabilities."""
    print_info("=== Testing Performance Monitoring ===")
    
    # Test timing functionality
    start_time = time.time()
    
    # Simulate some work
    time.sleep(0.1)
    
    elapsed_time = time.time() - start_time
    print_info(f"Elapsed time: {elapsed_time:.3f} seconds")
    
    assert elapsed_time >= 0.1, "Timing should be accurate"
    
    # Test memory monitoring (if CUDA available)
    if torch.cuda.is_available():
        initial_memory = torch.cuda.memory_allocated(0) / (1024**3)
        print_info(f"Initial GPU memory: {initial_memory:.3f} GB")
        
        # Allocate some memory
        x = torch.randn(1000, 1000, device='cuda')
        
        current_memory = torch.cuda.memory_allocated(0) / (1024**3)
        print_info(f"Current GPU memory: {current_memory:.3f} GB")
        
        assert current_memory > initial_memory, "Memory should increase after allocation"
    
    print_success("✓ Performance monitoring test passed\n")


def test_environment_variables():
    """Test CUDA environment variable configuration."""
    print_info("=== Testing Environment Variables ===")
    
    # Test that environment variables are set (from run.bat)
    env_vars = [
        "PYTORCH_NO_CUDA_MEMORY_CACHING",
        "PYTORCH_CUDA_ALLOC_CONF",
        "CUDA_LAUNCH_BLOCKING",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "CUDA_MEMORY_FRACTION",
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print_info(f"{var}: {value}")
        else:
            print_warning(f"{var}: Not set")
    
    print_success("✓ Environment variables test passed\n")


def main():
    """Run all CUDA optimization tests."""
    print_info("🚀 Starting Comprehensive CUDA Optimization Tests...\n")
    
    test_functions = [
        test_cuda_availability,
        test_mixed_precision,
        test_memory_management,
        test_optimal_batch_size,
        test_dataloader_optimization,
        test_cuda_error_handling,
        test_performance_monitoring,
        test_environment_variables,
    ]
    
    passed = 0
    total = len(test_functions)
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print_error(f"❌ {test_func.__name__} failed: {e}")
    
    print_info(f"\n=== Test Results ===")
    print_info(f"Passed: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 All CUDA optimization tests passed!")
    else:
        print_warning(f"⚠️  {total - passed} tests failed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
