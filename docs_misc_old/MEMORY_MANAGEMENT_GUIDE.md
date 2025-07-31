# Memory Management Guide for Dataset Forge

## Overview

Dataset Forge now includes comprehensive memory and CUDA memory management to prevent memory leaks, optimize performance, and provide better user control over system resources. This guide explains the memory management system and how to use it effectively.

## 🧠 Memory Management System

### Centralized Memory Management

The project now uses a centralized `MemoryManager` class located in `dataset_forge/utils/memory_utils.py` that provides:

- **Automatic CUDA cache clearing**
- **Python garbage collection**
- **Memory monitoring and reporting**
- **Safe tensor operations**
- **Context managers for memory-intensive operations**
- **Automatic cleanup decorators**

### Key Features

#### 1. Automatic Memory Cleanup

- CUDA cache is automatically cleared after operations
- Python garbage collection is performed regularly
- Memory is cleaned up when using context managers

#### 2. Safe Tensor Operations

- `to_device_safe()` function for safe tensor device transfers
- Automatic memory cleanup after tensor operations
- Error handling for memory-related operations

#### 3. Memory Monitoring

- Real-time memory usage tracking
- GPU memory utilization monitoring
- Memory optimization recommendations

#### 4. Context Managers

- `memory_context()` for memory-intensive operations
- `tensor_context()` for tensor operations
- Automatic cleanup on exit

## 🛠️ Usage Examples

### Basic Memory Management

```python
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache

# Clear all memory (CUDA + Python)
clear_memory()

# Clear only CUDA cache
clear_cuda_cache()
```

### Memory Monitoring

```python
from dataset_forge.utils.memory_utils import print_memory_info, get_memory_info

# Print memory information to console
print_memory_info(detailed=True)

# Get memory information as dictionary
memory_info = get_memory_info()
print(f"System RAM: {memory_info['system']['used_gb']:.1f}GB")
```

### Safe Tensor Operations

```python
from dataset_forge.utils.memory_utils import to_device_safe

# Safely move tensor to GPU
tensor = torch.randn(1000, 1000)
gpu_tensor = to_device_safe(tensor, "cuda")
```

### Context Managers

```python
from dataset_forge.utils.memory_utils import memory_context, tensor_context

# Memory-intensive operation with automatic cleanup
with memory_context("Image Processing", cleanup_on_exit=True):
    # Your memory-intensive code here
    result = process_large_dataset()
    return result

# Tensor operations with automatic cleanup
with tensor_context(device="cuda", cleanup_on_exit=True):
    # Your tensor operations here
    tensor = torch.randn(1000, 1000).cuda()
    result = model(tensor)
    return result
```

### Automatic Cleanup Decorators

```python
from dataset_forge.utils.memory_utils import auto_cleanup, monitor_memory_usage

@auto_cleanup
def process_images(images):
    """Function with automatic memory cleanup after execution."""
    # Your image processing code here
    return results

@monitor_memory_usage("Large Dataset Processing")
def process_large_dataset(dataset):
    """Function with memory usage monitoring."""
    # Your dataset processing code here
    return results
```

### Safe CUDA Operations

```python
from dataset_forge.utils.memory_utils import safe_cuda_operation

def my_cuda_operation(tensor):
    return model(tensor)

# Execute with retry logic and memory management
result = safe_cuda_operation(
    my_cuda_operation,
    max_retries=3,
    retry_delay=1.0,
    tensor
)
```

## 🎛️ Memory Management Menu

Access memory management features through the main menu:

```
System & Settings → Memory Management
```

### Available Options

1. **View Memory Information**

   - Shows detailed system and GPU memory usage
   - Displays Python object counts
   - Real-time memory statistics

2. **Clear Memory & CUDA Cache**

   - Performs comprehensive memory cleanup
   - Clears CUDA cache and garbage collection
   - Frees up system resources

3. **Memory Optimization Recommendations**
   - Analyzes current system state
   - Provides optimal settings for your hardware
   - Suggests batch sizes and worker counts

## 🔧 Configuration

### Memory Manager Settings

The memory manager can be configured through the global instance:

```python
from dataset_forge.utils.memory_utils import get_memory_manager

# Get the global memory manager
manager = get_memory_manager()

# Enable/disable monitoring
manager.enable_monitoring = True

# Configure memory settings
manager._cuda_available = torch.cuda.is_available()
```

### Environment Variables

The system automatically sets these CUDA environment variables for better memory management:

```bash
CUDA_LAUNCH_BLOCKING=1      # Better error reporting
CUDA_LAUNCH_TIMEOUT=300     # 5 minutes timeout
```

## 📊 Memory Optimization

### Automatic Optimization

The system provides automatic optimization recommendations based on your hardware:

```python
from dataset_forge.utils.memory_utils import optimize_for_large_operations

recommendations = optimize_for_large_operations()
print(recommendations)
```

### Manual Optimization Tips

1. **Batch Size Adjustment**

   - Reduce batch size for low memory systems
   - Increase batch size for high memory systems
   - Monitor memory usage during processing

2. **Worker Count Optimization**

   - Use fewer workers for GPU operations
   - Use more workers for I/O operations
   - Balance between CPU and GPU workers

3. **Memory Cleanup Frequency**
   - Clear memory after large operations
   - Use context managers for automatic cleanup
   - Monitor memory usage regularly

## 🚨 Troubleshooting

### Common Memory Issues

1. **CUDA Out of Memory**

   - Reduce batch size
   - Clear CUDA cache more frequently
   - Use CPU-only mode for large datasets

2. **System Memory Issues**

   - Close other applications
   - Process smaller batches
   - Use memory monitoring to identify leaks

3. **Slow Performance**
   - Check memory utilization
   - Optimize worker counts
   - Use appropriate processing types

### Debugging Memory Issues

```python
from dataset_forge.utils.memory_utils import get_memory_info, print_memory_info

# Before operation
print_memory_info(detailed=True)

# Your operation here
process_data()

# After operation
print_memory_info(detailed=True)
```

## 🔄 Legacy Compatibility

The new memory management system maintains backward compatibility:

```python
# Old way (still works)
import gc
import torch
gc.collect()
torch.cuda.empty_cache()

# New way (recommended)
from dataset_forge.utils.memory_utils import clear_memory
clear_memory()
```

## 📈 Performance Benefits

### Memory Efficiency

- Reduced memory leaks
- Better CUDA memory management
- Automatic cleanup reduces manual intervention

### Performance Improvements

- Faster tensor operations
- Better parallel processing
- Optimized resource utilization

### User Experience

- Real-time memory monitoring
- Automatic optimization recommendations
- Easy-to-use memory management tools

## 🔮 Future Enhancements

Planned improvements to the memory management system:

1. **Advanced Memory Profiling**

   - Detailed memory usage tracking
   - Memory leak detection
   - Performance bottleneck identification

2. **Dynamic Memory Optimization**

   - Automatic batch size adjustment
   - Real-time worker count optimization
   - Adaptive memory cleanup

3. **Multi-GPU Support**
   - Better multi-GPU memory management
   - GPU load balancing
   - Cross-GPU memory optimization

## 📚 API Reference

### Core Functions

- `clear_memory()` - Comprehensive memory cleanup
- `clear_cuda_cache()` - Clear CUDA cache only
- `get_memory_info()` - Get memory statistics
- `print_memory_info()` - Print memory information
- `to_device_safe()` - Safe tensor device transfer
- `safe_cuda_operation()` - Safe CUDA operations

### Decorators

- `@auto_cleanup` - Automatic cleanup after function
- `@monitor_memory_usage()` - Memory usage monitoring

### Context Managers

- `memory_context()` - Memory-intensive operations
- `tensor_context()` - Tensor operations

### Classes

- `MemoryManager` - Centralized memory management
- `ParallelConfig` - Parallel processing configuration

---

## 🤝 Contributing

When contributing to Dataset Forge, please follow these memory management guidelines:

1. **Use the centralized memory management system**
2. **Add memory cleanup to new operations**
3. **Use context managers for memory-intensive code**
4. **Monitor memory usage in new features**
5. **Test memory management with large datasets**

For questions or issues with memory management, please refer to the troubleshooting section or create an issue in the repository.
